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

TEMA_CHECKLIST = {
    "id": "codigos-http-que-indican-ataque",
    "tipo": "checklist",
    "brief": "Pasos defensivos para revisar logs HTTP.",
}

TEMA_TIP = {
    "id": "senales-de-phishing",
    "tipo": "tip",
    "brief": "Señales breves para reconocer phishing.",
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


def test_esquema_checklist_exige_de_4_a_6_pasos_y_limita_longitud():
    base = json.loads(analisis_educativo_valido())
    base["riesgos"] = []
    base["mitigacion"] = []
    base["items_checklist"] = [{"paso": f"Paso defensivo {i}"} for i in range(4)]
    analisis = AnalisisIA.model_validate(base)
    assert [item.paso for item in analisis.items_checklist] == [
        "Paso defensivo 0",
        "Paso defensivo 1",
        "Paso defensivo 2",
        "Paso defensivo 3",
    ]

    with pytest.raises(ValueError, match="entre 4 y 6 pasos"):
        AnalisisIA.model_validate({**base, "items_checklist": [{"paso": "Uno"}]})

    with pytest.raises(ValueError, match="máximo 100"):
        AnalisisIA.model_validate(
            {**base, "items_checklist": [{"paso": "x" * 101} for _ in range(4)]}
        )


def test_checklist_usa_campo_y_prompt_semanticos():
    respuesta = analisis_educativo_valido(
        riesgos=[],
        mitigacion=[],
        items_checklist=[
            {"paso": "Revisa los códigos 401 y 403 repetidos"},
            {"paso": "Busca errores 500 en el mismo endpoint"},
            {"paso": "Inspecciona solicitudes a rutas administrativas"},
            {"paso": "Confirma que las rutas sensibles exijan autenticación"},
        ],
    )

    prompt = analizador_educativo.construir_system_prompt(TEMA_CHECKLIST)
    assert "items_checklist: exactamente 4 a 6 objetos" in prompt
    assert "sin sintaxis de comandos" in prompt
    assert "items: null" in prompt

    datos = analizar_tema_educativo(ClienteFalso([respuesta]), TEMA_CHECKLIST)

    assert datos["meta"]["tipo"] == "checklist"
    assert datos["items_checklist"] == [
        {"paso": "Revisa los códigos 401 y 403 repetidos"},
        {"paso": "Busca errores 500 en el mismo endpoint"},
        {"paso": "Inspecciona solicitudes a rutas administrativas"},
        {"paso": "Confirma que las rutas sensibles exijan autenticación"},
    ]
    assert "items" not in datos


def test_esquema_tip_valida_cardinalidades_y_longitudes():
    base = json.loads(analisis_educativo_valido())
    base["riesgos"] = []
    base["mitigacion"] = []
    base["tip_slides"] = [
        {
            "texto": "La urgencia busca que actúes sin revisar.",
            "chips": [{"texto": "Urgencia"}, {"texto": "Presión"}],
            "stats": [
                {"valor": "ALTO", "etiqueta": "Riesgo"},
                {"valor": "DUDOSO", "etiqueta": "Remitente"},
            ],
        },
        {
            "texto": "Un enlace puede ocultar un destino distinto.",
            "chips": [{"texto": "Enlace"}, {"texto": "Destino"}],
            "stats": [
                {"valor": "ANTES", "etiqueta": "Revisa"},
                {"valor": "SIEMPRE", "etiqueta": "Confirma"},
            ],
        },
    ]
    base["tip_bullets"] = ["Pausa antes de hacer clic", "Revisa el remitente", "Confirma por otro canal"]

    analisis = AnalisisIA.model_validate(base)
    assert len(analisis.tip_slides) == 2
    assert len(analisis.tip_bullets) == 3

    with pytest.raises(ValueError, match="exactamente 2"):
        AnalisisIA.model_validate({**base, "tip_slides": base["tip_slides"][:1]})

    with pytest.raises(ValueError, match="entre 2 y 4"):
        invalid = {**base, "tip_slides": [{**base["tip_slides"][0], "chips": [{"texto": "Uno"}]}, base["tip_slides"][1]]}
        AnalisisIA.model_validate(invalid)

    with pytest.raises(ValueError, match="máximo 15"):
        invalid = {
            **base,
            "tip_slides": [
                {**base["tip_slides"][0], "chips": [{"texto": "x" * 16}, {"texto": "Ok"}]},
                base["tip_slides"][1],
            ],
        }
        AnalisisIA.model_validate(invalid)

    with pytest.raises(ValueError, match="máximo 60"):
        AnalisisIA.model_validate({**base, "tip_bullets": ["x" * 61] * 3})


def test_tip_usa_contrato_y_prompt_breve_sin_estadisticas_inventadas():
    respuesta = analisis_educativo_valido(
        riesgos=[],
        mitigacion=[],
        tip_slides=[
            {
                "texto": "La urgencia busca que actúes sin revisar.",
                "chips": [{"texto": "Urgencia"}, {"texto": "Presión"}],
                "stats": [
                    {"valor": "ALTO", "etiqueta": "Riesgo"},
                    {"valor": "DUDOSO", "etiqueta": "Remitente"},
                ],
            },
            {
                "texto": "Un enlace puede ocultar un destino distinto.",
                "chips": [{"texto": "Enlace"}, {"texto": "Destino"}],
                "stats": [
                    {"valor": "ANTES", "etiqueta": "Revisa"},
                    {"valor": "SIEMPRE", "etiqueta": "Confirma"},
                ],
            },
        ],
        tip_bullets=["Pausa antes de hacer clic", "Revisa el remitente", "Confirma por otro canal"],
    )

    prompt = analizador_educativo.construir_system_prompt(TEMA_TIP)
    assert "tip_slides: exactamente 2 objetos" in prompt
    assert "No inventes porcentajes" in prompt
    assert "sin comandos, checklist ni desarrollo narrativo largo" in prompt

    datos = analizar_tema_educativo(ClienteFalso([respuesta]), TEMA_TIP)

    assert datos["meta"]["tipo"] == "tip"
    assert len(datos["tip_slides"]) == 2
    assert datos["tip_bullets"] == [
        "Pausa antes de hacer clic",
        "Revisa el remitente",
        "Confirma por otro canal",
    ]
    assert "items" not in datos
    assert "items_checklist" not in datos
