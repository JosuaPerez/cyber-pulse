"""Marcas de voz verificadas y subtítulos breves para reels educativos."""

import base64
import hashlib
import json
import os
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import httpx
from pydantic import BaseModel, ConfigDict, Field, model_validator

MODEL = "gemini-3.5-transcribe"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"


class ErrorSubtitulos(RuntimeError):
    pass


class Palabra(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    text: str = Field(min_length=1, max_length=80)
    start: float = Field(ge=0)
    end: float = Field(gt=0)

    @model_validator(mode="after")
    def intervalo(self):
        if self.end <= self.start:
            raise ValueError("Intervalo de palabra inválido")
        return self


def normalizar(text: str) -> str:
    text = unicodedata.normalize("NFKD", text.casefold())
    return "".join(c for c in text if c.isalnum() and not unicodedata.combining(c))


def validar_palabras(words: list[Palabra], duration: float) -> None:
    if not words:
        raise ErrorSubtitulos("La transcripción no contiene marcas de palabra.")
    previous = 0.0
    for word in words:
        if word.start < previous - 0.02 or word.end > duration + 0.1:
            raise ErrorSubtitulos("Marcas fuera del audio o solapadas; revisa la transcripción.")
        previous = word.end


def transcribir(audio: bytes) -> list[Palabra]:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        raise ErrorSubtitulos("Falta GEMINI_API_KEY para obtener las marcas de subtítulos.")
    body = {
        "model": MODEL,
        "input": [{"type": "audio", "data": base64.b64encode(audio).decode(),
                   "mime_type": "audio/mp3"}],
        "generation_config": {"transcription_config": {
            "language_codes": ["es-419"],
            "mode": {"type": "verbatim", "timestamp_granularities": ["word"]},
        }},
        "store": False,
    }
    try:
        response = httpx.post(
            ENDPOINT, headers={"x-goog-api-key": key}, json=body,
            timeout=httpx.Timeout(180, connect=15),
        )
    except httpx.RequestError:
        raise ErrorSubtitulos("No se pudo conectar al servicio de transcripción.") from None
    if response.status_code >= 400:
        raise ErrorSubtitulos(f"Gemini rechazó la transcripción (HTTP {response.status_code}).")
    try:
        words = []
        for step in response.json().get("steps", []):
            if step.get("type") != "model_output":
                continue
            for content in step.get("content", []):
                for annotation in content.get("annotations", []):
                    if annotation.get("type") == "word_info":
                        if not normalizar(annotation["text"]):
                            continue
                        start = float(annotation["start_offset"].removesuffix("s"))
                        end = float(annotation["end_offset"].removesuffix("s"))
                        # La API puede redondear una palabra breve al mismo instante.
                        if end == start:
                            end += 0.01
                        words.append(Palabra(text=annotation["text"], start=start, end=end))
        return words
    except (ValueError, KeyError, AttributeError, TypeError):
        raise ErrorSubtitulos("Respuesta de marcas de tiempo inválida.") from None


def obtener_palabras(audio: Path, duration: float, reference: str) -> list[Palabra]:
    data = audio.read_bytes()
    digest = hashlib.sha256(data + MODEL.encode()).hexdigest()
    cache = audio.with_name(f"subtitles-{digest[:20]}.json")
    if cache.exists():
        words = [Palabra.model_validate(w) for w in json.loads(cache.read_text(encoding="utf-8"))]
    else:
        words = transcribir(data)
    validar_palabras(words, duration)
    expected = normalizar(reference)
    actual = normalizar(" ".join(w.text for w in words))
    if SequenceMatcher(None, expected, actual, autojunk=False).ratio() < 0.95:
        raise ErrorSubtitulos("La transcripción difiere del guion; revisa antes de renderizar.")
    if not cache.exists():
        cache.write_text(json.dumps([w.model_dump() for w in words], ensure_ascii=False, indent=2),
                         encoding="utf-8")
    return words


def agrupar(words: list[Palabra], scene_ends: list[float]) -> list[dict]:
    """Agrupa hasta cinco palabras sin atravesar pausas ni cambios de escena."""
    cues = []
    group = []

    def finish():
        if group:
            cues.append({"start": group[0].start, "end": group[-1].end,
                         "words": [w.model_dump() for w in group]})
            group.clear()

    def scene(t):
        return next((i for i, end in enumerate(scene_ends) if t < end), len(scene_ends) - 1)

    for word in words:
        if group and (
            len(group) >= 5
            or len(" ".join(w.text for w in [*group, word])) > 42
            or word.start - group[-1].end > 0.45
            or scene(word.start) != scene(group[0].start)
            or re.search(r"[.!?]$", group[-1].text)
        ):
            finish()
        group.append(word)
    finish()
    return cues


def formato_srt(cues: list[dict]) -> str:
    def stamp(seconds):
        ms = round(seconds * 1000)
        return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"

    return "\n\n".join(
        f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n"
        + " ".join(w["text"] for w in c["words"])
        for i, c in enumerate(cues, 1)
    ) + "\n"
