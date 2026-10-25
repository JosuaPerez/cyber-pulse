"""Contratos del módulo aislado; los proveedores se sustituyen en pruebas."""

import copy
import os
import json
from dataclasses import replace
from unittest.mock import AsyncMock

import numpy as np
import pytest
from moviepy import AudioClip, AudioFileClip

from app.reels.audio import prepare_audio
from app.reels.myth import build
from app.reels.settings import Settings, load_script, number_scenes


def test_safe_defaults_and_invalid_modes(monkeypatch):
    for name in ("REEL_AUDIO", "REEL_DRAFT_LABEL", "REEL_FPS", "REEL_VIDEO_MBPS",
                 "REEL_MUSIC_PATH", "REEL_SAFE_TOP", "REEL_SAFE_BOTTOM"):
        monkeypatch.delenv(name, raising=False)
    settings = Settings.from_env()
    assert settings.audio == "none" and not settings.draft_label
    assert settings.layout()["top"] >= 1920 * .14
    assert settings.layout()["bottom"] <= 1920 * .75
    for kwargs in ({"fps": 25}, {"bitrate_mbps": 3}, {"safe_top": .1},
                   {"audio": "bad"}, {"audio": "music"}):
        with pytest.raises(ValueError):
            Settings(**kwargs)


def test_numbering_follows_scene_order_not_textual_offsets():
    data = load_script()
    traps = [s for s in data["scenes"] if s["view"] in {"attachment", "call", "qr"}]
    assert [s["trap_number"] for s in traps] == [1, 2, 3]
    assert data["scenes"][0]["phone_title"] == "SMS"
    assert data["scenes"][-1]["options"] == "1 adjunto · 2 llamada · 3 QR"
    assert data["scenes"][-1]["question"].endswith("1, 2 o 3")
    data["scenes"][1], data["scenes"][2] = data["scenes"][2], data["scenes"][1]
    numbered = number_scenes(data)
    assert numbered["scenes"][1]["trap_number"] == 1
    assert numbered["scenes"][-1]["options"] == "1 llamada · 2 adjunto · 3 QR"


def test_qr_real_domains_are_rejected(tmp_path):
    import json

    data = load_script()
    data["scenes"][3]["example_url"] = "example.com/datos"
    path = tmp_path / "script.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid"):
        load_script(path)


def test_compare_generates_both_modes_and_cover(monkeypatch, tmp_path):
    """Contrato del comando único; la codificación real se prueba aparte."""
    from app.reels import myth

    calls = []

    def fake_build(output, **kwargs):
        output.mkdir(parents=True, exist_ok=True)
        return load_script(), None

    def fake_render(output, script, audio, settings):
        calls.append(settings.audio)
        (output / "cover.png").write_bytes(b"mock-cover")
        return output / f"reel-{settings.audio}.mp4"

    monkeypatch.setattr(myth, "build", fake_build)
    monkeypatch.setattr(myth, "render", fake_render)
    monkeypatch.setattr("sys.argv", ["myth", "--compare", "--output", str(tmp_path)])
    myth.main()
    result = json.loads((tmp_path / "comparison.json").read_text())
    assert calls == ["none", "voice"]
    assert set(result["outputs"]) == {"none", "voice"}
    assert result["status"] == "complete_pending_editorial_review"
    assert (tmp_path / "cover.png").read_bytes() == b"mock-cover"


def test_build_is_offline_and_caption_contains_sources(tmp_path):
    script, audio = build(tmp_path, settings=Settings())
    assert audio is None
    assert sum(s["duration"] for s in script["scenes"]) == 19
    html = (tmp_path / "preview.html").read_text(encoding="utf-8")
    assert '"draft": false' in html
    assert "__SPACE_FONT__" not in html and "__REEL_DATA__" not in html
    assert "Fuentes: FTC" not in html and "SIN VOZ" not in html
    assert "Ejemplo ficticio" in html
    caption = (tmp_path / "caption.txt").read_text(encoding="utf-8")
    assert all(url in caption for url in script["sources"])


def write_tone(path, duration):
    tone = AudioClip(lambda t: .05 * np.sin(2 * np.pi * 220 * t),
                     duration=duration, fps=44100)
    try:
        tone.write_audiofile(str(path), fps=44100, codec="pcm_s16le", logger=None)
    finally:
        tone.close()


def test_voice_is_synchronized_without_cutting_words(tmp_path, monkeypatch, caplog):
    script = load_script()
    paths = []
    for i, s in enumerate(script["scenes"]):
        path = tmp_path / f"voice-{i}.wav"
        write_tone(path, 2.4 if i == 0 else s["duration"] - .5)
        paths.append(path)
    provider = AsyncMock(return_value=paths)
    monkeypatch.setattr("app.reels.audio.generar_escenas", provider)
    audio = prepare_audio(script, tmp_path, Settings(audio="voice"))
    assert provider.call_args.kwargs["provider"] == "edge"
    assert script["scenes"][0]["duration"] >= 2.39
    assert "ampliando sin recortar" in caplog.text
    with AudioFileClip(str(audio)) as clip:
        assert clip.duration == pytest.approx(sum(s["duration"] for s in script["scenes"]),
                                              abs=.05)


def test_voice_too_long_is_not_published_or_silently_truncated(tmp_path, monkeypatch):
    path = tmp_path / "too-long.wav"
    write_tone(path, 5)
    monkeypatch.setattr("app.reels.audio.generar_escenas", AsyncMock(return_value=[path] * 6))
    with pytest.raises(ValueError, match="acorta el guion"):
        prepare_audio(copy.deepcopy(load_script()), tmp_path, Settings(audio="voice"))
    assert not (tmp_path / "audio-voice.wav").exists()


def test_music_is_local_low_volume_and_loops_to_timeline(tmp_path):
    path = tmp_path / "owned-test-tone.wav"
    write_tone(path, .8)
    settings = replace(Settings(), audio="music", music_path=path)
    audio = prepare_audio(load_script(), tmp_path, settings)
    with AudioFileClip(str(audio)) as clip:
        assert clip.duration == pytest.approx(19, abs=.05)
        assert np.max(np.abs(clip.get_frame(.5))) < .02


@pytest.mark.skipif(os.getenv("REEL_EXPORT_TEST") != "1", reason="Render completo opt-in")
def test_native_voice_export_with_simulated_provider(tmp_path, monkeypatch):
    """Prueba el montaje real; los tonos NO son una narración ni un proveedor real."""
    from app.reels.myth import render

    script = load_script()
    paths = []
    for i, scene in enumerate(script["scenes"]):
        path = tmp_path / f"mock-edge-{i}.wav"
        write_tone(path, scene["duration"] - .2)
        paths.append(path)
    monkeypatch.setattr("app.reels.audio.generar_escenas", AsyncMock(return_value=paths))
    settings = Settings(audio="voice")
    prepared, audio = build(tmp_path, settings=settings)
    target = render(tmp_path, prepared, audio, settings)
    assert target.is_file()
    import json

    report = json.loads((tmp_path / "verification.json").read_text(encoding="utf-8"))
    assert report["audio_codec"] == "aac"
    assert report["width"] == 1080 and report["height"] == 1920
    assert report["bitrate"] >= 4_000_000
