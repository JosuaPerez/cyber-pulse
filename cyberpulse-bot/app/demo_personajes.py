"""Render determinista de una muestra corta con personajes SVG originales."""

import argparse
import base64
import io
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def dimensiones_exportacion(width: int) -> tuple[int, int, float]:
    if width not in {540, 1080}:
        raise ValueError("El ancho debe ser 540 o 1080")
    return width, width * 16 // 9, width / 1080


def construir_portada(html: str) -> str:
    marker = '<svg class="world"'
    _, found, remainder = html.partition(marker)
    svg, closing, _ = remainder.partition("</svg>")
    if not found or not closing:
        raise ValueError("La plantilla no contiene los personajes del reel")
    template = (ROOT / "content/reels/password-reuse-cover.html").read_text(encoding="utf-8")
    return template.replace("__CHARACTERS_SVG__", marker + svg + closing)


def construir_historia(voice_cache: Path) -> dict:
    import wave
    from app.reel_educativo import PILOT, cargar_guion

    guion = cargar_guion(PILOT)
    scenes = []
    start = 0.0
    for index, scene in enumerate(guion.scenes):
        paths = list(voice_cache.glob(f"voice-{index:02}-*.wav"))
        if len(paths) != 1:
            raise ValueError(f"Se necesita un único WAV aprobado para la escena {index + 1}")
        with wave.open(str(paths[0]), "rb") as audio:
            duration = audio.getnframes() / audio.getframerate() + 0.35
        scenes.append({**scene.model_dump(), "start": start, "end": start + duration})
        start += duration
    return {"scenes": scenes, "duration": start, "caption": guion.caption}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audio", type=Path, help="Fragmento de voz ya generado")
    parser.add_argument("--output", type=Path, default=ROOT / "media/reels/characters-demo")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--width", type=int, choices=[540, 1080], default=540,
                        help="Ancho de exportación; 1080 para la versión final")
    parser.add_argument("--cover", action="store_true", help="Genera también la portada en 1080 × 1920")
    parser.add_argument("--duration", type=float, default=12, help="Duración de la muestra")
    parser.add_argument("--subtitles", type=Path, help="Marcas JSON del reel existente")
    parser.add_argument("--full", action="store_true", help="Renderiza la historia completa aprobada")
    parser.add_argument("--voice-cache", type=Path, help="WAV por escena del piloto aprobado")
    args = parser.parse_args()
    story = None
    if args.full:
        if not (args.audio and args.subtitles and args.voice_cache):
            parser.error("--full requiere --audio, --subtitles y --voice-cache")
        try:
            story = construir_historia(args.voice_cache)
        except (ValueError, OSError) as error:
            parser.error(str(error))
        args.duration = story["duration"]
        from moviepy import AudioFileClip

        with AudioFileClip(str(args.audio)) as audio:
            if abs(audio.duration - args.duration) > 0.15:
                parser.error("La narración no coincide con las duraciones de las escenas aprobadas")
    if not 1 <= args.duration <= 60:
        parser.error("La duración debe estar entre 1 y 60 segundos")
    if args.audio and args.audio.suffix.lower() not in {".wav", ".mp3"}:
        parser.error("La muestra admite audio WAV o MP3")
    args.output.mkdir(parents=True, exist_ok=True)
    audio_data = None
    if args.audio:
        mime = "audio/wav" if args.audio.suffix.lower() == ".wav" else "audio/mpeg"
        audio_data = f"data:{mime};base64," + base64.b64encode(args.audio.read_bytes()).decode()
    html = (ROOT / "content/reels/characters-demo.html").read_text(encoding="utf-8")
    html = html.replace("__AUDIO_DATA__", json.dumps(audio_data))
    cues = json.loads(args.subtitles.read_text(encoding="utf-8")) if args.subtitles else []
    html = html.replace("__DURATION__", json.dumps(args.duration))
    html = html.replace("__SUBTITLES__", json.dumps(cues, ensure_ascii=False).replace("<", "\\u003c"))
    html = html.replace("__STORY_DATA__", json.dumps(story, ensure_ascii=False).replace("<", "\\u003c"))
    if story:
        (args.output / "timeline.json").write_text(
            json.dumps(story, ensure_ascii=False, indent=2), encoding="utf-8",
        )
        (args.output / "caption.txt").write_text(story["caption"], encoding="utf-8")
    preview = args.output / "preview.html"
    preview.write_text(html, encoding="utf-8")
    if args.export or args.cover:
        import imageio_ffmpeg
        import numpy as np
        from PIL import Image
        from playwright.sync_api import sync_playwright

        width, height, scale = dimensiones_exportacion(args.width)
        fps = 24
        writer = imageio_ffmpeg.write_frames(
            str(args.output / ("reel.mp4" if story else "demo.mp4")), (width, height), fps=fps,
            codec="libx264", pix_fmt_out="yuv420p", macro_block_size=1,
            audio_path=str(args.audio.resolve()) if args.audio else None, audio_codec="aac",
            output_params=["-crf", "18", "-movflags", "+faststart", "-t", str(args.duration), *(
                ["-af", "apad"] if args.audio else []
            )],
        ) if args.export else None
        if writer:
            writer.send(None)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page(viewport={"width": width, "height": height})
                    if args.cover:
                        cover = args.output / "cover.html"
                        cover.write_text(construir_portada(html), encoding="utf-8")
                        page.set_viewport_size({"width": 1080, "height": 1920})
                        page.goto(cover.resolve().as_uri())
                        page.evaluate("document.fonts.ready")
                        page.screenshot(path=str(args.output / "cover.png"))
                        with Image.open(args.output / "cover.png") as image:
                            image.crop((135, 420, 945, 1500)).save(
                                args.output / "cover-grid-preview.png",
                            )
                        page.close()
                        page = browser.new_page(viewport={"width": width, "height": height})
                    page.set_content(html)
                    page.add_style_tag(content=(
                        f".controls{{display:none}}.stage{{transform:scale({scale})!important;"
                        "margin:0!important;transform-origin:top left!important}"
                    ))
                    page.evaluate("document.fonts.ready")
                    for frame in range(math.ceil(fps * args.duration) if writer else 0):
                        t = frame / fps
                        page.evaluate("t=>window.renderAt(t)", t)
                        raw = page.screenshot()
                        if frame in {fps * t for t in [0, 1, 2, 4, 6, 8, 10, 14, 19, 24,
                                                      29, 34, 38, 42, 45, 49, 53, 57]}:
                            (args.output / f"scene-{frame // fps}.png").write_bytes(raw)
                        with Image.open(io.BytesIO(raw)) as image:
                            writer.send(np.asarray(image.convert("RGB")))
                        if frame and frame % (fps * 10) == 0:
                            print(f"Render: {frame // fps}/{args.duration:.1f} s", flush=True)
                finally:
                    browser.close()
        finally:
            if writer:
                writer.close()
        filename = "reel.mp4" if story else "demo.mp4"
        if args.export:
            print(f"Video: {(args.output / filename).resolve()}")
        if args.cover:
            print(f"Portada: {(args.output / 'cover.png').resolve()}")
    print(f"Vista previa: {preview.resolve()}")


if __name__ == "__main__":
    main()
