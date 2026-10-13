"""Vista previa y exportación de reels educativos a partir de un guion revisable."""

import argparse
import asyncio
import base64
import json
from bisect import bisect_right
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.voz_educativa import DEFAULT_MODEL, generar_escenas
from app.subtitulos import agrupar, formato_srt, obtener_palabras

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "content" / "reels" / "template.html"
PILOT = ROOT / "content" / "reels" / "password-reuse.json"


def muestras_silencio(t):
    import numpy as np

    # MoviePy mezcla buffers (n, canales); un vector (n,) se difunde a (n, n).
    return np.zeros((len(t), 2)) if isinstance(t, np.ndarray) else np.zeros(2)


class Escena(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    label: str = Field(min_length=1, max_length=45)
    title: str = Field(min_length=1, max_length=90)
    emphasis: str = Field(min_length=1, max_length=120)
    narration: str = Field(min_length=1, max_length=250)
    visual: Literal["accounts", "leak", "chain", "mail", "protect", "cta"]
    cards: list[str] = Field(min_length=1, max_length=3)
    detail: str = Field(min_length=1, max_length=100)
    accent: Literal["cyan", "amber", "violet"]


class Guion(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(pattern=r"^[a-z0-9-]+$", max_length=80)
    title: str = Field(min_length=1, max_length=120)
    caption: str = Field(min_length=1, max_length=2200)
    sources: list[str] = Field(min_length=1)
    scenes: list[Escena] = Field(min_length=2, max_length=10)


def cargar_guion(path: Path) -> Guion:
    return Guion.model_validate_json(path.read_text(encoding="utf-8"))


def construir_preview(
    guion: Guion, durations: list[float], audio: bytes | None = None,
    subtitles: list[dict] | None = None,
) -> str:
    if len(durations) != len(guion.scenes) or any(d <= 0 for d in durations):
        raise ValueError("Cada escena debe tener una duración positiva")
    data = guion.model_dump()
    for scene, duration in zip(data["scenes"], durations, strict=True):
        scene["duration"] = duration
    if audio is not None:
        data["audio"] = "data:audio/mpeg;base64," + base64.b64encode(audio).decode("ascii")
    if subtitles is not None:
        data["subtitles"] = subtitles
    # Impide cerrar el elemento script desde texto del guion.
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return TEMPLATE.read_text(encoding="utf-8").replace("__REEL_DATA__", payload)


async def generar_narracion(
    guion: Guion, folder: Path, voice: str | None, provider: str = "edge",
    model: str = DEFAULT_MODEL,
) -> list[Path]:
    return await generar_escenas(
        [scene.narration for scene in guion.scenes], folder,
        provider=provider, voice=voice, model=model,
    )


def exportar(
    guion: Guion, output: Path, voice: str | None, width: int, silent: bool = False,
    provider: str = "edge", model: str = DEFAULT_MODEL,
    subtitles: bool = False,
) -> Path:
    import numpy as np
    from PIL import Image
    from moviepy import (
        AudioClip, AudioFileClip, CompositeVideoClip, ImageClip, VideoClip,
        concatenate_audioclips, concatenate_videoclips, vfx,
    )
    from playwright.sync_api import sync_playwright

    with TemporaryDirectory(prefix="cyberpulse-reel-") as temporary:
        folder = Path(temporary)
        paths = [] if silent else asyncio.run(generar_narracion(
            guion, output / "voice-cache", voice, provider, model,
        ))
        resources = []
        try:
            audios = [AudioFileClip(str(path)) for path in paths]
            resources.extend(audios)
            narration = None
            audio_bytes = None
            cues = None
            if silent:
                durations = [max(5, len(s.narration.split()) / 2.5) for s in guion.scenes]
            else:
                pause = AudioClip(muestras_silencio, duration=0.35, fps=44100)
                resources.append(pause)
                segments = [concatenate_audioclips([a, pause]) for a in audios]
                resources.extend(segments)
                narration = concatenate_audioclips(segments)
                resources.append(narration)
                durations = [segment.duration for segment in segments]
                audio_path = output / "narration.mp3"
                narration.write_audiofile(str(audio_path), logger=None)
                audio_bytes = audio_path.read_bytes()
                if subtitles:
                    words = obtener_palabras(
                        audio_path, narration.duration,
                        " ".join(s.narration for s in guion.scenes),
                    )
                    cues = agrupar(words, np.cumsum(durations).tolist())
                    (output / "subtitles.srt").write_text(formato_srt(cues), encoding="utf-8")
                    (output / "subtitles.json").write_text(
                        json.dumps(cues, ensure_ascii=False, indent=2), encoding="utf-8",
                    )
            html = construir_preview(guion, durations, audio_bytes, cues)
            preview = output / ("preview-subtitled.html" if subtitles else "preview.html")
            preview.write_text(html, encoding="utf-8")
            frames = []
            caption_times = []
            caption_frames = []
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page(viewport={"width": 1080, "height": 1920})
                    page.set_content(html, wait_until="load")
                    page.add_style_tag(content=(
                        ".stage {transform:none!important;margin:0!important;}"
                        ".controls,.note {display:none!important;}"
                    ))
                    hidden = (
                        page.add_style_tag(content=".narration {visibility:hidden!important;}")
                        if cues else None
                    )
                    scene_starts = [0, *np.cumsum(durations).tolist()[:-1]]
                    for i in range(len(guion.scenes)):
                        page.evaluate("t => window.renderAt(t)", scene_starts[i] + 0.00001)
                        frame = folder / f"scene-{i:02}.png"
                        page.screenshot(path=str(frame))
                        frames.append(frame)
                    if hidden is not None:
                        hidden.evaluate("el => el.remove()")
                    if cues:
                        caption_times = sorted({0.0, *scene_starts, *[
                            t for cue in cues for word in cue["words"]
                            for t in [word["start"], word["end"]]
                        ]})
                        for i, t in enumerate(caption_times):
                            page.evaluate("t => window.renderAt(t)", t + 0.00001)
                            frame = folder / f"caption-{i:03}.png"
                            page.locator('#narration').screenshot(path=str(frame))
                            with Image.open(frame) as image:
                                caption_frames.append(np.asarray(image.convert('RGB').resize(
                                    (round(880 * width / 1080), round(150 * width / 1080)),
                                    Image.Resampling.LANCZOS,
                                )).copy())
                finally:
                    browser.close()
            height = width * 16 // 9
            clips = []
            for frame, duration in zip(frames, durations, strict=True):
                image = ImageClip(str(frame)).resized(width=width).with_duration(duration)
                resources.append(image)
                # Movimiento ligero; todas las escenas conservan el área segura de lectura.
                moving = image.resized(lambda t, d=duration: 1 + 0.006 * min(t / d, 1))
                clip = CompositeVideoClip(
                    [moving.with_position("center")], size=(width, height)
                ).with_duration(duration).with_effects([vfx.FadeIn(0.15)])
                clips.append(clip)
                resources.extend([moving, clip])
            video = concatenate_videoclips(clips, method="compose")
            resources.append(video)
            if caption_frames:
                captions = VideoClip(
                    frame_function=lambda t: caption_frames[bisect_right(caption_times, t) - 1],
                    duration=video.duration,
                ).with_position((round(85 * width / 1080), round(1445 * width / 1080)))
                resources.append(captions)
                video = CompositeVideoClip([video, captions], size=(width, height))
                resources.append(video)
            if narration is not None:
                video = video.with_audio(narration)
            resources.append(video)
            video.write_videofile(
                str(output / ("reel-subtitled.mp4" if subtitles else "reel.mp4")),
                fps=24, codec="libx264", audio_codec="aac",
                temp_audiofile=str(folder / "mixed-audio.m4a"),
                preset="fast", ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"],
                logger=None,
            )
            (output / "caption.txt").write_text(guion.caption, encoding="utf-8")
            return preview
        finally:
            for resource in reversed(resources):
                resource.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--script", type=Path, default=PILOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--export", action="store_true", help="Genera voz y MP4; requiere red")
    parser.add_argument("--silent", action="store_true", help="Exporta un borrador visual sin voz")
    parser.add_argument("--voice", help="Voz del proveedor; Gonzalo para Edge, Charon para Gemini")
    parser.add_argument("--provider", choices=["edge", "gemini"], default="edge")
    parser.add_argument("--tts-model", default=DEFAULT_MODEL)
    parser.add_argument("--audio-only", action="store_true", help="Genera las voces sin video")
    parser.add_argument("--subtitles", action="store_true", help="Transcribe y sincroniza subtítulos")
    parser.add_argument("--width", type=int, choices=[540, 1080], default=1080)
    args = parser.parse_args()
    guion = cargar_guion(args.script)
    output = args.output or ROOT / "media" / "reels" / guion.id
    output.mkdir(parents=True, exist_ok=True)
    if args.subtitles and (args.silent or not args.export or args.audio_only):
        parser.error("--subtitles requiere --export con voz")
    if (args.export or args.audio_only) and not args.silent and (
        args.provider == "gemini" or args.subtitles
    ):
        from dotenv import load_dotenv

        load_dotenv(ROOT / ".env")
    if args.audio_only:
        if args.silent:
            parser.error("--audio-only no puede combinarse con --silent")
        try:
            paths = asyncio.run(generar_narracion(
                guion, output / "voice-cache", args.voice, args.provider, args.tts_model,
            ))
        except RuntimeError as error:
            parser.exit(1, f"{error}\n")
        for path in paths:
            print(f"Voz: {path.resolve()}")
        return
    if args.export:
        try:
            preview = exportar(
                guion, output, args.voice, args.width, args.silent,
                args.provider, args.tts_model,
                args.subtitles,
            )
        except RuntimeError as error:
            parser.exit(1, f"{error}\n")
    else:
        durations = [max(5, len(s.narration.split()) / 2.5) for s in guion.scenes]
        preview = output / "preview.html"
        preview.write_text(construir_preview(guion, durations), encoding="utf-8")
    print(f"Vista previa: {preview.resolve()}")
    if args.export:
        filename = "reel-subtitled.mp4" if args.subtitles else "reel.mp4"
        print(f"Video: {(output / filename).resolve()}")


if __name__ == "__main__":
    main()
