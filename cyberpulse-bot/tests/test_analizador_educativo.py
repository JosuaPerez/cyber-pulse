"""Tests del analizador educativo con un cliente Gemini simulado."""
import json
from types import SimpleNamespace

import pytest

from app import analizador_educativo
from app.analizador_educativo import analizar_tema_educativo
from app.esquemas import AnalisisIA

TEMA = {
    "id": "que-es-zero-day",
    "tipo": "concepto",
    "brief": "Explica el concepto de forma defensiva y práctica.",
    "usado": False,
}

TEMA_CHEATSHEET = {
    "id": "nmap-reconocimiento-basico",
    "tipo": "cheatsheet",
    "brief": "Comandos seguros de nmap para auditorías autorizadas.",
    "usado": False,
}


def analisis_educativo_valido(**cambios):
    datos = {
        "es_relevante": True,
        "motivo_descarte": "",
        "severidad": "medium",
        "estado_explotacion": "desconocido",
        "cves": [],
        "portada_titulo": "¿Reconocerías un zero-day?",
        "portada_subtitulo": "La señal no siempre aparece en una alerta evidente",
        "problema": "Una vulnerabilidad desconocida puede exigir detección basada en comportamiento y contexto.",
        "dato_tecnico": "Observa cambios anómalos, procesos inesperados y accesos fuera del patrón habitual.",
        "riesgos": ["Detecciones tardías", "Exposición no identificada", "Respuesta descoordinada"],
        "mitigacion": ["Define una línea base", "Correlaciona eventos", "Documenta la respuesta"],
        "caption": "Entender el concepto ayuda a detectar señales débiles antes de que se conviertan en un incidente. ¿Qué señal revisarías primero?",
        "hashtags": ["#Ciberseguridad", "#BlueTeam", "#ThreatDetection"],
        "hilo_x": ["Un zero-day exige pensar más allá de las firmas.", "Busca cambios de comportamiento y contexto.", "¿Qué señal revisarías primero en tu entorno?"],
    }
    datos.update(cambios)
    return json.dumps(datos)


class ClienteFalso:
    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.llamadas = []
        self.models = self

    def generate_content(self, model, contents, config):
        self.llamadas.append((contents, config))
        respuesta = self.respuestas.pop(0)
        if isinstance(respuesta, Exception):
            raise respuesta
        return SimpleNamespace(text=respuesta)


@pytest.fixture(autouse=True)
def sin_esperas(monkeypatch):
    monkeypatch.setattr(analizador_educativo.time, "sleep", lambda segundos: None)


def test_tema_educativo_no_incluye_cves_ni_estadisticas():
    datos = analizar_tema_educativo(ClienteFalso([analisis_educativo_valido()]), TEMA)
    assert datos["meta"]["cves"] == []
    contenido = " ".join([
        datos["slide_1"]["title"], datos["slide_1"]["description"],
        datos["slide_2"]["description"], datos["slide_3"]["description"],
        datos["caption"], *datos["slide_4"]["points"], *datos["slide_5"]["points"],
    ])
    assert "CVE-" not in contenido
    assert "%" not in contenido


def test_caption_educativo_termina_en_pregunta():
    datos = analizar_tema_educativo(ClienteFalso([analisis_educativo_valido()]), TEMA)
    caption_sin_fuente = datos["caption"].split("\n\nFuente:", 1)[0].strip()
    assert caption_sin_fuente.endswith("?")


def test_respuesta_con_cve_se_rechaza():
    cliente = ClienteFalso([
        analisis_educativo_valido(cves=["CVE-2026-12345"]),
        analisis_educativo_valido(),
    ])
    analizar_tema_educativo(cliente, TEMA)
    assert "no puede incluir CVEs" in cliente.llamadas[1][0]


def test_cheatsheet_devuelve_items_y_no_narrativa_de_riesgos():
    respuesta = analisis_educativo_valido(
        riesgos=[],
        mitigacion=[],
        items=[
            {"sintaxis": "nmap -sV", "explicacion": "Detecta servicios y sus versiones."},
            {"sintaxis": "nmap -O", "explicacion": "Ayuda a identificar el sistema operativo."},
            {"sintaxis": "nmap -sS", "explicacion": "Realiza un escaneo TCP SYN controlado."},
        ],
    )

    datos = analizar_tema_educativo(
        ClienteFalso([respuesta]),
        TEMA_CHEATSHEET,
    )

    assert datos["meta"]["familia"] == "educativo"
    assert datos["meta"]["tipo"] == "cheatsheet"
    assert datos["items"] == [
        {"sintaxis": "nmap -sV", "explicacion": "Detecta servicios y sus versiones."},
        {"sintaxis": "nmap -O", "explicacion": "Ayuda a identificar el sistema operativo."},
        {"sintaxis": "nmap -sS", "explicacion": "Realiza un escaneo TCP SYN controlado."},
    ]


def test_prompt_cheatsheet_pide_items_y_no_riesgos():
    prompt = analizador_educativo.construir_system_prompt(TEMA_CHEATSHEET)

    assert "items: exactamente 3 a 4 objetos" in prompt
    assert "sintaxis exacta" in prompt
    assert "riesgos y mitigacion: listas vacías" in prompt
    assert "riesgos: exactamente 3 consecuencias" not in prompt
