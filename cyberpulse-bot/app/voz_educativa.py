"""Narración por escena con caché local y proveedores explícitos."""

import asyncio
import base64
import binascii
import hashlib
import io
import json
import os
import wave
from pathlib import Path

import httpx

DEFAULT_MODEL = "gemini-3.8-flash-lite-tts"
DEFAULT_STYLE = (
    "Español latinoamericano. Voz de narrador educativo cercana, clara y natural. "
    "Ritmo ágil pero comprensible, con pausas breves entre frases. "
    "Sin dramatización, música ni efectos. Lee exactamente el texto proporcionado."
)
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"


class ErrorVoz(RuntimeError):
    """Error seguro para mostrar en CLI sin cabeceras ni credenciales."""


def extraer_wav(response: dict) -> bytes:
    """Valida el audio WAV antes de persistir la respuesta del proveedor."""
    blocks = [
        content
        for step in response.get("steps", []) if step.get("type") == "model_output"
        for content in step.get("content", []) if content.get("type") == "audio"
    ]
    if not blocks:
        raise ErrorVoz("Gemini no devolvió audio para esta escena.")
    try:
        data = base64.b64decode(blocks[-1]["data"], validate=True)
        with wave.open(io.BytesIO(data), "rb") as audio:
            if audio.getnframes() == 0:
                raise ErrorVoz("Gemini devolvió un audio vacío.")
    except (KeyError, ValueError, binascii.Error, wave.Error, EOFError):
        raise ErrorVoz("Gemini devolvió un audio WAV inválido.") from None
    return data


def sintetizar_gemini(text: str, voice: str, model: str, style: str) -> bytes:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ErrorVoz("Falta GEMINI_API_KEY para generar la narración con Gemini.")
    body = {
        "model": model,
        "input": [{"type": "user_input", "content": [{
            "type": "text", "text": text,
            "annotations": [{"type": "speech_metadata", "style": style}],
        }]}],
        "response_format": {"type": "audio", "mime_type": "audio/wav", "sample_rate": 24000},
        "generation_config": {"speech_config": [{"voice": voice}]},
        "store": False,
    }
    try:
        response = httpx.post(
            ENDPOINT, headers={"x-goog-api-key": key}, json=body,
            timeout=httpx.Timeout(120, connect=15),
        )
    except httpx.RequestError:
        raise ErrorVoz("No se pudo conectar al servicio de voz de Gemini.") from None
    if response.status_code >= 400:
        if response.status_code == 429:
            # Solo extrae una indicación pública de espera, nunca el cuerpo completo.
            wait = None
            try:
                for detail in response.json().get("error", {}).get("details", []):
                    if detail.get("@type", "").endswith("RetryInfo"):
                        wait = detail.get("retryDelay")
            except ValueError:
                pass
            suffix = f" Espera indicada por el servicio: {wait}." if wait else ""
            raise ErrorVoz("Gemini limitó la generación de voz (HTTP 429)." + suffix)
        raise ErrorVoz(f"Gemini rechazó la generación de voz (HTTP {response.status_code}).")
    try:
        return extraer_wav(response.json())
    except ValueError:
        raise ErrorVoz("Gemini devolvió una respuesta inválida.") from None


async def generar_escenas(
    texts: list[str], folder: Path, *, provider: str = "edge", voice: str | None = None,
    model: str = DEFAULT_MODEL, style: str = DEFAULT_STYLE,
) -> list[Path]:
    if provider not in {"edge", "gemini"}:
        raise ValueError("Proveedor de voz desconocido")
    voice = voice or ("Charon" if provider == "gemini" else "es-CO-GonzaloNeural")
    folder.mkdir(parents=True, exist_ok=True)
    paths = []
    for index, text in enumerate(texts):
        settings = {"text": text, "provider": provider, "voice": voice}
        if provider == "gemini":
            settings.update(model=model, style=style)
        digest = hashlib.sha256(json.dumps(settings, sort_keys=True).encode()).hexdigest()[:20]
        path = folder / f"voice-{index:02}-{digest}.{'wav' if provider == 'gemini' else 'mp3'}"
        if not path.exists() or path.stat().st_size == 0:
            if provider == "gemini":
                data = await asyncio.to_thread(sintetizar_gemini, text, voice, model, style)
                path.write_bytes(data)
            else:
                import edge_tts

                try:
                    await edge_tts.Communicate(text, voice, rate="+0%").save(str(path))
                except Exception:
                    # Evita reutilizar una respuesta parcial tras un fallo de conexión.
                    if path.exists():
                        path.unlink()
                    raise ErrorVoz(
                        "Edge TTS rechazó la narración. Usa --provider gemini "
                        "con GEMINI_API_KEY, o --silent para revisar el diseño."
                    ) from None
        paths.append(path)
    return paths
