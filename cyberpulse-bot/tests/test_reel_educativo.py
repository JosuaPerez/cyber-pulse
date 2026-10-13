import pytest
from pydantic import ValidationError

from app.reel_educativo import PILOT, cargar_guion, construir_preview, muestras_silencio


def test_piloto_es_valido_y_preview_no_requiere_servicios_externos():
    guion = cargar_guion(PILOT)
    preview = construir_preview(guion, [8] * len(guion.scenes))
    assert "__REEL_DATA__" not in preview
    assert "cdn.tailwindcss.com" not in preview
    assert '"duration": 8' in preview


def test_guion_no_puede_inyectar_cierre_de_script():
    guion = cargar_guion(PILOT)
    guion.scenes[0].title = "</script><script>alert(1)</script>"
    preview = construir_preview(guion, [8] * len(guion.scenes))
    assert "</script><script>alert(1)" not in preview
    assert "\\u003c/script>" in preview


def test_duraciones_incompletas_se_rechazan():
    with pytest.raises(ValueError, match="duración positiva"):
        construir_preview(cargar_guion(PILOT), [8])


def test_tipo_visual_desconocido_se_rechaza():
    data = cargar_guion(PILOT).model_dump()
    data["scenes"][0]["visual"] = "unknown"
    with pytest.raises(ValidationError):
        type(cargar_guion(PILOT)).model_validate(data)


def test_pausa_se_mezcla_sin_expandir_el_buffer_de_audio():
    import numpy as np
    from moviepy import AudioClip, concatenate_audioclips

    pause = AudioClip(muestras_silencio, duration=0.35, fps=44100)
    combined = concatenate_audioclips([pause, pause])
    try:
        frames = combined.get_frame(np.linspace(0, 0.69, 100))
        assert frames.shape == (100, 2)
        assert not frames.any()
    finally:
        combined.close()
        pause.close()
