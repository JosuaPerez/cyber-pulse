import pytest
import httpx

from app import subtitulos as subs


def word(text, start, end):
    return subs.Palabra(text=text, start=start, end=end)


def test_parser_admite_marcas_redondeadas_y_no_incluye_puntuacion_suelta(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-only")
    response = {"steps": [{"type": "model_output", "content": [{"annotations": [
        {"type": "word_info", "text": "Hola", "start_offset": "0.200s",
         "end_offset": "0.200s"},
        {"type": "word_info", "text": ".", "start_offset": "0.300s",
         "end_offset": "0.300s"},
    ]}]}]}
    monkeypatch.setattr(subs.httpx, "post", lambda *a, **kw: httpx.Response(200, json=response))
    words = subs.transcribir(b"audio-test")
    assert len(words) == 1
    assert words[0].text == "Hola"
    assert words[0].end == pytest.approx(0.21)
    subs.validar_palabras(words, 1)


def test_rechaza_marcas_solapadas_o_fuera_del_audio():
    with pytest.raises(subs.ErrorSubtitulos, match="solapadas"):
        subs.validar_palabras([word("Hola", 0, 1), word("mundo", 0.5, 2)], 3)
    with pytest.raises(subs.ErrorSubtitulos, match="fuera"):
        subs.validar_palabras([word("Hola", 0, 2)], 1)
    with pytest.raises(subs.ErrorSubtitulos, match="no contiene"):
        subs.validar_palabras([], 1)


def test_bloques_cortos_respetan_pausas_y_cambios_de_escena():
    words = [word(str(i), i * 0.3, i * 0.3 + 0.2) for i in range(8)]
    words += [word("Otra", 4, 4.2), word("escena", 4.2, 4.4)]
    cues = subs.agrupar(words, [1.2, 5])
    assert all(len(c["words"]) <= 5 for c in cues)
    assert all(not (c["start"] < 1.2 < c["end"]) for c in cues)
    assert cues[-1]["start"] == 4
    assert [w["text"] for c in cues for w in c["words"]] == [w.text for w in words]


def test_srt_conserva_milisegundos_y_texto():
    cues = subs.agrupar([word("Hola", 1.125, 1.5), word("mundo.", 1.5, 2.25)], [3])
    assert subs.formato_srt(cues) == "1\n00:00:01,125 --> 00:00:02,250\nHola mundo.\n"


def test_cache_evitar_retranscripcion_y_rechaza_otro_guion(tmp_path, monkeypatch):
    audio = tmp_path / "audio.mp3"
    audio.write_bytes(b"audio-test")
    calls = []

    def transcribe(data):
        calls.append(data)
        return [word("Hola", 0.1, 0.5), word("mundo.", 0.5, 1)]

    monkeypatch.setattr(subs, "transcribir", transcribe)
    first = subs.obtener_palabras(audio, 1.2, "Hola mundo.")
    assert subs.obtener_palabras(audio, 1.2, "Hola mundo.") == first
    assert len(calls) == 1
    with pytest.raises(subs.ErrorSubtitulos, match="difiere"):
        subs.obtener_palabras(audio, 1.2, "Un guion totalmente distinto.")
    audio.write_bytes(b"changed")
    subs.obtener_palabras(audio, 1.2, "Hola mundo.")
    assert len(calls) == 2
