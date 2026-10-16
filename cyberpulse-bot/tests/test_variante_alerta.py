import json
from pathlib import Path
from unittest.mock import MagicMock
from urllib.parse import parse_qs, urlsplit

import pytest

from app.generador import parametros_variante_alerta
from app import generador


def test_clasica_no_agrega_parametros():
    assert parametros_variante_alerta({}, "clasica") == {}


def test_editorial_preserva_fuente_estado_y_cves():
    meta = {"familia": "alerta", "fuente_nombre": "Fuente de prueba", "fuente_url": "https://example.invalid/aviso",
            "estado_explotacion": "sin_evidencia", "cves": ["CVE-2026-1234"]}
    result = parametros_variante_alerta(meta, "editorial")
    assert result["alertVariant"] == "editorial"
    assert result["sourceName"] == meta["fuente_nombre"]
    assert result["sourceUrl"] == meta["fuente_url"]
    assert result["exploitation"] == "sin_evidencia"
    assert json.loads(result["cves"]) == meta["cves"]
    assert "alertVariant" not in meta


@pytest.mark.parametrize("tipo", ["cheatsheet", "checklist", "tip", "concepto"])
def test_editorial_no_modifica_educativos(tipo):
    assert parametros_variante_alerta({"familia": "educativo", "tipo": tipo}, "editorial") == {}


def test_datos_ausentes_no_inventan_fuentes_ni_explotacion():
    result = parametros_variante_alerta({}, "editorial")
    assert result["sourceName"] == ""
    assert result["sourceUrl"] == ""
    assert result["exploitation"] == "desconocido"
    assert json.loads(result["cves"]) == []


def test_rechaza_variante_no_soportada():
    with pytest.raises(ValueError, match="variante"):
        parametros_variante_alerta({}, "automatico")


def test_opcion_a_preserva_metadatos_sin_forzar_noticia_de_actualizacion():
    meta = {"familia": "alerta", "fuente_nombre": "Aviso", "fuente_url": "https://example.invalid/noticia"}
    params = parametros_variante_alerta(meta, "clara")
    assert params["alertVariant"] == "clara"
    assert params["sourceName"] == "Aviso"
    assert "version" not in params


@pytest.mark.parametrize("tipo", ["cheatsheet", "checklist", "tip", "concepto"])
def test_opcion_a_no_modifica_educativos(tipo):
    assert parametros_variante_alerta({"familia": "educativo", "tipo": tipo}, "clara") == {}


@pytest.mark.parametrize("configured,explicit,expected", [
    ("clara", None, "clara"), ("clasica", None, None), ("clara", "clasica", None),
])
def test_generador_aplica_config_y_permite_respaldo(monkeypatch, tmp_path, configured, explicit, expected):
    data_path = Path(__file__).resolve().parents[1] / "content/alerts/editorial-demo.json"
    data = json.loads(data_path.read_text(encoding="utf-8"))
    before = json.dumps(data, sort_keys=True)
    playwright = MagicMock()
    page = playwright.__enter__.return_value.chromium.launch.return_value.new_context.return_value.new_page.return_value
    page.evaluate.return_value = False
    monkeypatch.setattr(generador, "sync_playwright", lambda: playwright)
    monkeypatch.setattr(generador.config, "ALERTAS_VARIANTE", configured)
    monkeypatch.setattr(generador.config, "IMAGENES_DIR", tmp_path)
    monkeypatch.setattr(generador.config, "TEMPLATES_BASE_URL", "http://localhost:5173")
    paths = generador.generar_imagenes_carrusel(data, variante_alerta=explicit)
    assert len(paths) == (4 if expected == "clara" else 5)
    for call in page.goto.call_args_list:
        params = parse_qs(urlsplit(call.args[0]).query)
        assert params.get("alertVariant") == ([expected] if expected else None)
    assert all(call.kwargs["full_page"] is (expected is None) for call in page.screenshot.call_args_list)
    assert json.dumps(data, sort_keys=True) == before


def test_clara_reordena_sin_perder_detalle_riesgos_o_medidas():
    path = Path(__file__).resolve().parents[1] / "content/alerts/editorial-demo.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    before = json.dumps(data, sort_keys=True)
    slides = generador.construir_alerta_clara(data)
    assert [s["type"] for s in slides] == ["cover", "scope", "context_risks", "mitigation"]
    assert slides[1]["description"] == data["slide_2"]["description"]
    assert json.loads(slides[3]["summary"]) == data["slide_5"]["points"]
    assert slides[2]["description"] == data["slide_3"]["description"]
    assert json.loads(slides[2]["summary"]) == data["slide_4"]["points"]
    assert json.dumps(data, sort_keys=True) == before


@pytest.mark.parametrize("familia,variante,count", [
    ("alerta", "clara", 4), ("alerta", "clasica", 5), ("alerta", "editorial", 5),
    ("educativo", "clara", 5),
])
def test_cantidad_planificada_no_se_deduce_de_un_render_incompleto(familia, variante, count):
    assert generador.cantidad_imagenes_esperada({"familia": familia}, variante) == count


def test_mockup_requiere_version_explicita_y_fuente_mozilla():
    meta = {"fuente_url": "https://www.mozilla.org/en-US/security/advisories/mfsa2026-106/",
            "visual_apoyo": {"tipo": "firefox_version", "version": "158"}}
    assert generador.visual_apoyo_validado(meta) == {"tipo": "firefox_version", "version": "158"}
    assert generador.visual_apoyo_validado({"fuente_url": meta["fuente_url"]}) == {}


@pytest.mark.parametrize("url,version", [
    ("https://mozilla.org.attacker.invalid/en-US/security/advisories/test/", "158"),
    ("http://www.mozilla.org/en-US/security/advisories/test/", "158"),
    ("https://www.mozilla.org/en-US/security/advisories/test/", "latest"),
    ("https://[bad", "158"),
])
def test_no_dibuja_version_no_verificable(url, version):
    assert generador.visual_apoyo_validado({"fuente_url": url, "visual_apoyo": {
        "tipo": "firefox_version", "version": version}}) == {}
