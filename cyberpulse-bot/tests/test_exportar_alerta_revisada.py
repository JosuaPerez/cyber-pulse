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
