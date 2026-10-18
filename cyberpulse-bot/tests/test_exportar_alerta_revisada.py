import json
from pathlib import Path

from app.exportar_alerta_revisada import aplicar_revision
from app.generador import construir_alerta_clara

ROOT = Path(__file__).resolve().parents[1]


def test_revision_candiru_conserva_original_y_exporta_contexto_historico():
    data = json.loads((ROOT / "content/alerts/editorial-demo.json").read_text(encoding="utf-8"))
    original = json.dumps(data, sort_keys=True)
    review = json.loads((ROOT / "content/alerts/reviews/candiru-v2.json").read_text(encoding="utf-8"))
    resultado = aplicar_revision(data, review)
    slides = construir_alerta_clara(resultado)
    assert len(slides) == 4
    assert "vector" not in slides[0]["title"]
    assert "2024 y 2025" in slides[0]["description"]
    assert resultado["meta"]["editorial"]["alcance"].startswith("Puede interesar")
    assert resultado["meta"]["editorial"]["temporalidad"] == "historica"
    assert "Citizen Lab" in resultado["caption"]
    assert resultado["meta"]["visual_apoyo"]["clase"] == "resumen"
    assert json.dumps(data, sort_keys=True) == original


def test_revision_legacy_no_hereda_sello_ids_ni_textos_de_otro_analisis():
    from app.alertas_v3 import AnalisisAlerta, a_datos_publicacion, validar_paquete_publicacion
    from test_esquema_alerta import valido
    import pytest
    data = a_datos_publicacion(AnalisisAlerta(**valido()), "Otra fuente", "https://example.org/otra")
    review = json.loads((ROOT / "content/alerts/reviews/candiru-v2.json").read_text(encoding="utf-8"))
    resultado = aplicar_revision(data, review)
    assert "alerta" not in resultado
    assert "hilo_x" not in resultado
    assert "validacion" not in resultado["meta"]
    assert resultado["meta"]["cves"] == []
    assert "SampleBug" not in json.dumps(resultado)
    with pytest.raises(ValueError, match="análisis nuevo"):
        validar_paquete_publicacion(resultado)
