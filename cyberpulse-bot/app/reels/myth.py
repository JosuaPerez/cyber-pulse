"""Entrada del reel Mito vs. mecanismo, ejecutable también dentro de Docker."""

import argparse
import json
import logging
from dataclasses import replace
from pathlib import Path

from .audio import prepare_audio
from .preview import write_preview
from .render import render as export_video
from .settings import ROOT, SCRIPT, Settings, load_script

LOGGER = logging.getLogger(__name__)


def build(output, with_voice=False, *, settings=None, script_path=SCRIPT):
    try:
        settings = settings or Settings.from_env()
        if with_voice:
            settings = replace(settings, audio="voice")
        script = load_script(script_path)
        output = Path(output)
        output.mkdir(parents=True, exist_ok=True)
        audio = prepare_audio(script, output, settings)
        write_preview(script, output, settings, audio)
        (output / "timing.json").write_text(json.dumps({
            "voice": settings.audio == "voice", "audio_mode": settings.audio,
            "duration": sum(s["duration"] for s in script["scenes"]),
            "scenes": script["scenes"], "layout": settings.layout(),
            "status": "pending_review_not_published",
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        return script, audio
    except Exception:
        LOGGER.error("No se pudo preparar el reel Mito vs. mecanismo")
        raise


def render(output, script, audio_path, settings=None):
    return export_video(Path(output), script, audio_path, settings or Settings.from_env())


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--voice", action="store_true", help="Compatibilidad: REEL_AUDIO=voice")
    parser.add_argument("--script", type=Path, default=SCRIPT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        settings = Settings.from_env()
        if args.voice:
            settings = replace(settings, audio="voice")
        output = args.output or ROOT / f"media/reels/phishing-myth-v3/{settings.audio}"
        script, audio = build(output, settings=settings, script_path=args.script)
        if args.render:
            render(output, script, audio, settings)
        LOGGER.info("Vista previa: %s", output / "preview.html")
    except ValueError as error:
        LOGGER.error("Reel no generado: %s", error)
        raise SystemExit(1) from None
    except Exception as error:
        # No incluye cuerpos de respuesta del proveedor, cabeceras ni credenciales.
        LOGGER.error("Reel no generado (%s). Revisa los mensajes anteriores.",
                     type(error).__name__)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
