"""Audio explícito: silencio, Edge TTS por escena o archivo local autorizado."""

import asyncio
import logging
from importlib.metadata import version

from app.voz_educativa import generar_escenas

LOGGER = logging.getLogger(__name__)


def prepare_audio(script, output, settings):
    """Ajusta escenas a voz completa; nunca recorta palabras ni cambia de proveedor."""
    from moviepy import AudioClip, AudioFileClip, afx, concatenate_audioclips

    from app.reel_educativo import muestras_silencio

    resources = []
    try:
        if settings.audio == "none":
            LOGGER.info("REEL_AUDIO=none: exportación sin pista de audio")
            return None
        duration = sum(s["duration"] for s in script["scenes"])
        target = output / f"audio-{settings.audio}.wav"
        if settings.audio == "music":
            original = AudioFileClip(str(settings.music_path))
            resources.append(original)
            if not original.duration or original.duration <= 0:
                raise ValueError("La música local está vacía")
            mixed = original.with_effects([
                afx.AudioLoop(duration=duration),
                afx.MultiplyVolume(settings.music_volume),
                afx.AudioFadeIn(.15), afx.AudioFadeOut(.15),
            ])
            resources.append(mixed)
        else:
            LOGGER.info("Generando %d escenas con Edge TTS %s (%s)",
                        len(script["scenes"]), version("edge-tts"), settings.voice)
            async def request_voice():
                return await asyncio.wait_for(generar_escenas(
                    [s["narration"] for s in script["scenes"]], output / "voice-cache",
                    provider="edge", voice=settings.voice,
                ), timeout=120)

            paths = asyncio.run(request_voice())
            segments = []
            for index, (scene, path) in enumerate(zip(script["scenes"], paths, strict=True)):
                spoken = AudioFileClip(str(path))
                resources.append(spoken)
                if spoken.duration > scene["duration"]:
                    LOGGER.warning("Escena %d: voz %.2fs supera %.2fs; ampliando sin recortar",
                                   index + 1, spoken.duration, scene["duration"])
                    scene["duration"] = spoken.duration
                pad = max(0, scene["duration"] - spoken.duration)
                if pad:
                    silence = AudioClip(muestras_silencio, duration=pad, fps=44100)
                    resources.append(silence)
                    segment = concatenate_audioclips([spoken, silence])
                    resources.append(segment)
                else:
                    segment = spoken
                segments.append(segment)
            duration = sum(s["duration"] for s in script["scenes"])
            if not 17 <= duration <= 21:
                raise ValueError(f"Voz completa requiere {duration:.2f}s (>21s); acorta el guion, "
                                 "no se ha recortado ni acelerado la voz")
            mixed = concatenate_audioclips(segments)
            resources.append(mixed)
        mixed.write_audiofile(str(target), codec="pcm_s16le", fps=44100, logger=None)
        LOGGER.info("Audio %s preparado: %.2fs", settings.audio, mixed.duration)
        return target
    except Exception:
        LOGGER.error("No se pudo preparar REEL_AUDIO=%s; no se sustituye por silencio",
                     settings.audio)
        raise
    finally:
        for resource in reversed(resources):
            resource.close()
