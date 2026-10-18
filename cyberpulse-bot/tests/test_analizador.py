"""Tests del analizador con un cliente de Gemini simulado (no gastan cuota ni requieren red).
Ejecutar desde la raíz del proyecto:  python -m pytest tests/ -v
"""
import json
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app import analizador
from app.analizador import ErrorAnalisis, analizar_noticia
from app.esquemas import AnalisisIA

TEXTO_FUENTE = (
    "Acme VPN flaw exploited in the wild\n\n"
    "Attackers are exploiting CVE-2026-12345 in Acme VPN Gateway, allowing unauthenticated "
    "remote code execution. The vendor rated it CVSS 9.8 and released version 5.2.1 to fix it."
)
NOTICIA = {"title": "Acme VPN flaw exploited", "summary": "x", "link": "https://www.bleepingcomputer.com/news/acme"}
OBTENER_TEXTO_REAL = analizador.obtener_texto_fuente


def analisis_valido(**cambios):
    datos = {
        "es_relevante": True,
        "motivo_descarte": "",
        "severidad": "critical",
        "estado_explotacion": "explotacion_activa",
        "cves": ["CVE-2026-12345"],
        "portada_titulo": "Acme VPN: RCE explotada activamente",
        "portada_subtitulo": "Atacantes ejecutan código sin autenticación en Acme VPN Gateway",
        "problema": "Una falla en Acme VPN Gateway permite ejecutar código de forma remota sin credenciales.",
        "dato_tecnico": "CVE-2026-12345, CVSS 9.8. Corregida en la versión 5.2.1.",
        "riesgos": ["Toma de control del gateway", "Acceso a la red interna", "Robo de credenciales"],
        "mitigacion": ["Actualiza a la versión 5.2.1", "Restringe el acceso a la interfaz de administración",
                       "Monitorea logs en busca de accesos anómalos"],
        "caption": "¡Atención! 🚨 Acme VPN Gateway está siendo explotado y puede poner en riesgo tu red. ¿Ya revisaste tu exposición?",
        "hashtags": ["#Ciberseguridad", "#InfoSec", "#ZeroDay"],
        "hilo_x": ["Se explota una RCE en Acme VPN Gateway #InfoSec", "CVE-2026-12345 (CVSS 9.8) permite ejecución remota sin autenticación.",
                   "Actualiza a 5.2.1 y restringe la interfaz de administración."],
        "editorial": {
            "tipo_noticia": "vulnerabilidad",
            "gancho": "¿Usas Acme VPN? Revisa este aviso", "resumen": "El aviso describe un fallo que permite acceder al equipo sin credenciales.",
            "audiencia": "mixta", "hecho": "La fuente documenta explotación de Acme VPN Gateway.", "alcance": "Concierne a quienes usan o administran Acme VPN Gateway. Consulta el aviso para comprobar tu caso.",
            "limite": "Esta noticia no demuestra que tu equipo esté comprometido.",
            "temporalidad": "vigencia_no_confirmada", "evidencia_temporal": "",
            "detalle": "El fallo permite ejecutar código sin credenciales; el aviso explica las condiciones.",
            "acciones": [
                {"rol": "personas", "texto": "Consulta la fuente o pide ayuda al proveedor antes de asumir que estás afectado.", "orientacion_general": True, "evidencia": ""},
                {"rol": "administradores", "texto": "Revisa las medidas del aviso oficial y verifica su aplicación.", "orientacion_general": True, "evidencia": ""}],
            "caption": "Si usas Acme VPN, consulta el aviso y comprueba con tu administrador si te afecta. ¿Ya lo revisaste?",
            "evidencias": ["Acme VPN flaw exploited in the wild"], "visual": "resumen", "nodos": [], "evidencia_relacion": ""},
    }
    datos.update(cambios)
    return json.dumps(datos)


class ClienteFalso:
    """Devuelve las respuestas en orden; cada elemento puede ser un str (JSON) o una Exception."""

    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.llamadas = []
        self.models = self

    def generate_content(self, model, contents, config):
        self.llamadas.append(contents)
        r = self.respuestas.pop(0)
        if isinstance(r, Exception):
            raise r
        return SimpleNamespace(text=r)


@pytest.fixture(autouse=True)
def sin_red_ni_esperas(monkeypatch):
    monkeypatch.setattr(analizador, "obtener_texto_fuente", lambda noticia: TEXTO_FUENTE)
    monkeypatch.setattr(analizador.time, "sleep", lambda s: None)


def test_validacion_conserva_limite_real_del_caption():
    with pytest.raises(ValidationError, match="caption tiene 1001 caracteres"):
        AnalisisIA.model_validate_json(analisis_valido(caption="x" * 1001))


def test_fuente_insuficiente_no_llama_a_ia(monkeypatch):
    monkeypatch.setattr(analizador, "obtener_texto_fuente", OBTENER_TEXTO_REAL)
    cliente = ClienteFalso([])
    with pytest.raises(ErrorAnalisis, match="Fuente insuficiente"):
        analizar_noticia(cliente, {"title": "Guest-to-Host VM escape", "summary": "", "link": ""})
    assert cliente.llamadas == []


def test_resumen_suficiente_conserva_fallback():
    assert " ".join(TEXTO_FUENTE.split()) in OBTENER_TEXTO_REAL({"title": "Aviso", "summary": TEXTO_FUENTE, "link": ""})


def test_evidencia_breaking_out_es_valida(monkeypatch):
    monkeypatch.setattr(analizador.app_config, "ALERTAS_VARIANTE", "clara")
    evidencia = "The researcher reached administrator control of a host, breaking out of the virtual machine."
    a = AnalisisIA.model_validate_json(analisis_valido(visual_tipo="vm_isolation", visual_evidencia=evidencia))
    assert analizador.verificar_contra_fuente(a, TEXTO_FUENTE + evidencia) == []


def test_vm_sin_explotacion_activa_no_es_critical(monkeypatch):
    monkeypatch.setattr(analizador.app_config, "ALERTAS_VARIANTE", "clara")
    a = AnalisisIA.model_validate_json(analisis_valido(visual_tipo="vm_isolation", estado_explotacion="desconocido", editorial=None))
    assert any("acceso previo" in error for error in analizador.verificar_contra_fuente(a, TEXTO_FUENTE))


def test_no_recomienda_virtualizacion_anidada_sin_evidencia(monkeypatch):
    monkeypatch.setattr(analizador.app_config, "ALERTAS_VARIANTE", "clara")
    a = AnalisisIA.model_validate_json(analisis_valido(mitigacion=["Deshabilita la virtualización anidada", "Revisa el aviso", "Consulta al proveedor"], editorial=None))
    assert any("virtualización anidada" in error for error in analizador.verificar_contra_fuente(a, TEXTO_FUENTE))


def test_negacion_o_titulo_solo_no_activa_ficha_vm():
    assert not analizador.evidencia_aislamiento_valida("The guest cannot escape to the host.", "The guest cannot escape to the host.")
