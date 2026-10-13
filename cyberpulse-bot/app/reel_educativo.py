"""Vista previa y exportación de reels educativos a partir de un guion revisable."""

import argparse
import asyncio
import base64
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "content" / "reels" / "template.html"
PILOT = ROOT / "content" / "reels" / "password-reuse.json"


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


def construir_preview(guion: Guion, durations: list[float], audio: bytes | None = None) -> str:
    if len(durations) != len(guion.scenes) or any(d <= 0 for d in durations):
        raise ValueError("Cada escena debe tener una duración positiva")
    data = guion.model_dump()
    for scene, duration in zip(data["scenes"], durations, strict=True):
        scene["duration"] = duration
    if audio is not None:
        data["audio"] = "data:audio/mpeg;base64," + base64.b64encode(audio).decode("ascii")
    # Impide cerrar el elemento script desde texto del guion.
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return TEMPLATE.read_text(encoding="utf-8").replace("__REEL_DATA__", payload)


async def generar_narracion(guion: Guion, folder: Path, voice: str) -> list[Path]:
    import edge_tts

    paths = []
    for i, scene in enumerate(guion.scenes):
        path = folder / f"voice-{i:02}.mp3"
        try:
            await edge_tts.Communicate(scene.narration, voice, rate="+0%").save(str(path))
        except Exception:
            raise RuntimeError(
                "El servicio de voz no respondió. Puedes revisar el formato con "
                "--export --silent; esa opción genera un borrador sin narración."
            ) from None
        paths.append(path)
    return paths


def exportar(guion: Guion, output: Path, voice: str, width: int, silent: bool = False) -> Path:
    from moviepy import (
        AudioClip, AudioFileClip, CompositeVideoClip, ImageClip,
        concatenate_audioclips, concatenate_videoclips, vfx,
    )
    from playwright.sync_api import sync_playwright

    with TemporaryDirectory(prefix="cyberpulse-reel-") as temporary:
        folder = Path(temporary)
        paths = [] if silent else asyncio.run(generar_narracion(guion, folder, voice))
        resources = []
        try:
            audios = [AudioFileClip(str(path)) for path in paths]
            resources.extend(audios)
            narration = None
            audio_bytes = None
            if silent:
                durations = [max(5, len(s.narration.split()) / 2.5) for s in guion.scenes]
            else:
                pause = AudioClip(lambda t: 0 * t, duration=0.35, fps=44100)
                resources.append(pause)
                segments = [concatenate_audioclips([a, pause]) for a in audios]
                resources.extend(segments)
                narration = concatenate_audioclips(segments)
                resources.append(narration)
                durations = [segment.duration for segment in segments]
                audio_path = folder / "narration.mp3"
                narration.write_audiofile(str(audio_path), logger=None)
                audio_bytes = audio_path.read_bytes()
            html = construir_preview(guion, durations, audio_bytes)
            preview = output / "preview.html"
            preview.write_text(html, encoding="utf-8")
            frames = []
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                try:
                    page = browser.new_page(viewport={"width": 1080, "height": 1920})
                    page.set_content(html, wait_until="load")
                    page.add_style_tag(content=(
                        ".stage {transform:none!important;margin:0!important;}"
                        ".controls,.note {display:none!important;}"
                    ))
                    for i in range(len(guion.scenes)):
                        page.evaluate("index => window.renderScene(index)", i)
                        frame = folder / f"scene-{i:02}.png"
                        page.screenshot(path=str(frame))
                        frames.append(frame)
                finally:
                    browser.close()
            height = width * 16 // 9
            clips = []
            for frame, duration in zip(frames, durations, strict=True):
                image = ImageClip(str(frame)).resized(width=width).with_duration(duration)
                resources.append(image)
                # Movimiento ligero; todas las escenas conservan el área segura de lectura.
                moving = image.resized(lambda t: 1 + 0.006 * min(t / duration, 1))
                clip = CompositeVideoClip(
                    [moving.with_position("center")], size=(width, height)
                ).with_duration(duration).with_effects([vfx.FadeIn(0.15)])
                clips.append(clip)
                resources.extend([moving, clip])
            video = concatenate_videoclips(clips, method="compose")
            if narration is not None:
                video = video.with_audio(narration)
            resources.append(video)
            video.write_videofile(
                str(output / "reel.mp4"), fps=24, codec="libx264", audio_codec="aac",
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
    parser.add_argument("--voice", default="es-CO-GonzaloNeural")
    parser.add_argument("--width", type=int, choices=[540, 1080], default=1080)
    args = parser.parse_args()
    guion = cargar_guion(args.script)
    output = args.output or ROOT / "media" / "reels" / guion.id
    output.mkdir(parents=True, exist_ok=True)
    if args.export:
        try:
            preview = exportar(guion, output, args.voice, args.width, args.silent)
        except RuntimeError as error:
            parser.exit(1, f"{error}\n")
    else:
        durations = [max(5, len(s.narration.split()) / 2.5) for s in guion.scenes]
        preview = output / "preview.html"
        preview.write_text(construir_preview(guion, durations), encoding="utf-8")
    print(f"Vista previa: {preview.resolve()}")
    if args.export:
        print(f"Video: {(output / 'reel.mp4').resolve()}")


if __name__ == "__main__":
    main()
