import asyncio
import base64
import io
import wave

import httpx
import pytest

from app import voz_educativa as voz


def wav_valido():
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(24000)
        audio.writeframes(b"\x01\x00" * 240)
    return buffer.getvalue()


def respuesta_audio(data):
    return {"steps": [{"type": "model_output", "content": [{
        "type": "audio", "data": base64.b64encode(data).decode(),
    }]}]}


def test_valida_wav_y_rechaza_respuestas_sin_audio():
    data = wav_valido()
    assert voz.extraer_wav(respuesta_audio(data)) == data
    with pytest.raises(voz.ErrorVoz, match="no devolvió audio"):
        voz.extraer_wav({"steps": []})
    with pytest.raises(voz.ErrorVoz, match="inválido"):
        voz.extraer_wav(respuesta_audio(b"invalid"))


def test_texto_y_estilo_se_envian_por_separado(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-only")
    requests = []

    def post(url, **kwargs):
        requests.append((url, kwargs))
        return httpx.Response(200, json=respuesta_audio(wav_valido()))

    monkeypatch.setattr(voz.httpx, "post", post)
    voz.sintetizar_gemini("Texto a leer", "Charon", voz.DEFAULT_MODEL, "Estilo de lectura")
    body = requests[0][1]["json"]
    text = body["input"][0]["content"][0]
    assert text["text"] == "Texto a leer"
    assert text["annotations"][0]["style"] == "Estilo de lectura"
    assert body["store"] is False


def test_error_del_proveedor_no_expone_clave(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "secret-test-key")
    monkeypatch.setattr(
        voz.httpx, "post", lambda *a, **kw: httpx.Response(403, text="secret-test-key"),
    )
    with pytest.raises(voz.ErrorVoz, match="HTTP 403") as error:
        voz.sintetizar_gemini("Texto", "Charon", voz.DEFAULT_MODEL, "Estilo")
    assert "secret-test-key" not in str(error.value)


def test_cache_reutiliza_audio_y_se_invalida_con_guion_o_voz(tmp_path, monkeypatch):
    requests = []

    def synth(text, voice, model, style):
        requests.append((text, voice))
        return wav_valido()

    monkeypatch.setattr(voz, "sintetizar_gemini", synth)

    def run(text="Hola", voice="Charon"):
        return asyncio.run(voz.generar_escenas([text], tmp_path, provider="gemini", voice=voice))

    first = run()
    assert run() == first
    assert len(requests) == 1
    assert run("Otro texto") != first
    assert run(voice="Kore") != first
    assert len(requests) == 3


def test_fallo_no_crea_audio_en_cache(tmp_path, monkeypatch):
    def fail(*args):
        raise voz.ErrorVoz("HTTP 429")

    monkeypatch.setattr(voz, "sintetizar_gemini", fail)
    with pytest.raises(voz.ErrorVoz, match="429"):
        asyncio.run(voz.generar_escenas(["Texto"], tmp_path, provider="gemini"))
    assert list(tmp_path.iterdir()) == []
