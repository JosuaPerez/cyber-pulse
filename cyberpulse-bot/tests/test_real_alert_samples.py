import json
from pathlib import Path
from urllib.parse import urlsplit

from app.esquemas import LIMITES


def test_muestras_reales_tienen_fuente_y_cinco_slides_compatibles():
    path = Path(__file__).resolve().parents[2] / "cyberpulse-templates/src/content/real-alerts.json"
    samples = json.loads(path.read_text(encoding="utf-8"))
    assert set(samples) == {"update", "editorial", "context"}
    for sample in samples.values():
        assert sample["sourceName"]
        assert sample["sourceDate"]
        assert urlsplit(sample["sourceUrl"]).scheme == "https"
        slides = sample["slides"]
        assert [s["type"] for s in slides] == ["cover", "problem", "detail", "impact", "mitigation"]
        assert len(slides[0]["title"]) <= LIMITES["portada_titulo"]
        assert len(slides[0]["description"]) <= LIMITES["portada_subtitulo"]
        assert len(slides[1]["description"]) <= LIMITES["problema"]
        assert len(slides[2]["description"]) <= LIMITES["dato_tecnico"]
        for slide, limit in [(slides[3], "riesgo"), (slides[4], "mitigacion")]:
            assert len(slide["summary"]) == 3
            assert all(len(p) <= LIMITES[limit] for p in slide["summary"])


def test_incidente_discord_no_se_presenta_como_nuevo():
    path = Path(__file__).resolve().parents[2] / "cyberpulse-templates/src/content/real-alerts.json"
    case = json.loads(path.read_text(encoding="utf-8"))["context"]
    assert "2025" in case["seriesLabel"]
    assert "no es una alerta nueva" in case["statusText"]
