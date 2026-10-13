import wave

import pytest

from app.demo_personajes import construir_historia


def guardar_wav(path, seconds):
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(8000)
        audio.writeframes(b"\0\0" * round(seconds * 8000))


def test_historia_usa_duraciones_reales_y_pausas_sin_huecos(tmp_path):
    for i in range(6):
        guardar_wav(tmp_path / f"voice-{i:02}-test.wav", i + 1)
    story = construir_historia(tmp_path)
    assert story["duration"] == pytest.approx(21 + 6 * 0.35)
    assert len(story["scenes"]) == 6
    assert story["scenes"][0]["start"] == 0
    for previous, current in zip(story["scenes"], story["scenes"][1:]):
        assert previous["end"] == current["start"]
    assert story["scenes"][-1]["end"] == story["duration"]


def test_no_elige_una_voz_arbitraria_si_la_cache_es_ambigua(tmp_path):
    guardar_wav(tmp_path / "voice-00-one.wav", 1)
    guardar_wav(tmp_path / "voice-00-two.wav", 1)
    with pytest.raises(ValueError, match="único WAV"):
        construir_historia(tmp_path)
