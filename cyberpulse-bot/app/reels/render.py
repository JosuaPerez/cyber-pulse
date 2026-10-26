"""Captura nativa 1080p y codificación H.264; verificación sin servicios externos."""

import json
import logging
import os
import re
import shutil
import subprocess
from fractions import Fraction

from .preview import validate_visuals, write_cover
from .settings import HEIGHT, WIDTH

LOGGER = logging.getLogger(__name__)


def ffmpeg_exe():
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def verify_video(path, settings, *, expected_duration, has_audio):
    """ffprobe si existe; FFmpeg/MoviePy como alternativa portable ya instalada."""
    try:
        probe = os.getenv("REEL_FFPROBE") or shutil.which("ffprobe")
        if probe:
            process = subprocess.run([probe, "-v", "error", "-show_streams", "-show_format",
                                      "-of", "json", str(path)], check=True,
                                     capture_output=True, text=True, timeout=60)
            info = json.loads(process.stdout)
            video = next(s for s in info["streams"] if s["codec_type"] == "video")
            audios = [s for s in info["streams"] if s["codec_type"] == "audio"]
            result = {"width": video["width"], "height": video["height"],
                      "duration": float(info["format"]["duration"]),
                      "codec": video["codec_name"], "pix_fmt": video["pix_fmt"],
                      "fps": float(Fraction(video["avg_frame_rate"])),
                      "bitrate": int(video["bit_rate"]),
                      "audio": bool(audios), "audio_codec": audios[0]["codec_name"]
                      if audios else None, "probe": "ffprobe"}
        else:
            from moviepy.video.io.ffmpeg_reader import ffmpeg_parse_infos

            info = ffmpeg_parse_infos(str(path))
            metadata = subprocess.run([ffmpeg_exe(), "-hide_banner", "-i", str(path)],
                                      capture_output=True, text=True, timeout=30).stderr
            if not re.search(r"Video: h264[^\n]*\byuv420p(?:\b|\()", metadata):
                raise ValueError("FFmpeg no confirma H.264 yuv420p")
            audio_codecs = re.findall(r"Audio: ([a-zA-Z0-9_]+)", metadata)
            result = {"width": info["video_size"][0], "height": info["video_size"][1],
                      "duration": info["duration"], "fps": info["video_fps"],
                      "codec": info["video_codec_name"],
                      "pix_fmt": "yuv420p",
                      "bitrate": int(info["video_bitrate"] * 1000),
                      "audio": info["audio_found"],
                      "audio_codec": audio_codecs[0] if audio_codecs else None,
                      "probe": "FFmpeg/MoviePy"}
        if (result["width"], result["height"]) != (WIDTH, HEIGHT):
            raise ValueError("Resolución final incorrecta")
        if not 17 <= result["duration"] <= 21 or abs(
            result["duration"] - expected_duration
        ) > .15:
            raise ValueError("Duración final fuera del contrato")
        if result["codec"] != "h264" or result["pix_fmt"] != "yuv420p":
            raise ValueError("Se requiere H.264 yuv420p")
        if abs(result["fps"] - settings.fps) > .05 or result["bitrate"] < 4_000_000:
            raise ValueError("FPS o bitrate de video insuficiente")
        if result["audio"] != has_audio or has_audio and result["audio_codec"] != "aac":
            raise ValueError("Pista de audio incorrecta")
        # Decodifica todo: un contenedor legible no prueba que todos los frames sean válidos.
        subprocess.run([ffmpeg_exe(), "-v", "error", "-xerror", "-i", str(path),
                        "-f", "null", "-"], check=True, capture_output=True, timeout=120)
        data = path.read_bytes()
        if not (0 <= data.find(b"moov") < data.find(b"mdat")):
            raise ValueError("Falta faststart en el MP4")
        LOGGER.info("MP4 validado: %s", result)
        return result
    except Exception:
        LOGGER.error("La verificación del MP4 falló: %s", path)
        raise


def render(output, script, audio_path, settings):
    from playwright.sync_api import sync_playwright

    duration = sum(s["duration"] for s in script["scenes"])
    target = output / f"reel-{settings.audio}.mp4"
    partial = output / f"reel-{settings.audio}.partial.mp4"
    encoder = None
    browser = None
    try:
        # La media del stream puede quedar ligeramente por debajo del objetivo
        # durante el arranque del VBV. Margen mínimo para garantizar >=4 Mbps.
        encode_mbps = max(4.1, settings.bitrate_mbps)
        bitrate = f"{encode_mbps:g}M"
        command = [ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "image2pipe",
                   "-vcodec", "mjpeg", "-framerate", str(settings.fps), "-i", "pipe:0"]
        if audio_path:
            command += ["-i", str(audio_path), "-c:a", "aac", "-b:a", "192k"]
        else:
            command += ["-an"]
        command += ["-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
                    "-vf", "scale=in_range=pc:out_range=tv,format=yuv420p",
                    "-color_range", "tv", "-colorspace", "bt709",
                    "-color_primaries", "bt709", "-color_trc", "bt709",
                    "-b:v", bitrate, "-minrate", bitrate, "-maxrate", bitrate,
                    "-bufsize", f"{encode_mbps * 2:g}M",
                    "-x264-params", "nal-hrd=cbr:filler=1", "-movflags", "+faststart",
                    "-t", str(duration), str(partial)]
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT},
                                    device_scale_factor=1)
            page.goto((output / "preview.html").resolve().as_uri())
            page.evaluate("document.fonts.ready")
            page.evaluate("window.prepareLoop()")
            checks = validate_visuals(page, script, settings)
            write_cover(page, output, settings)
            stage = page.locator("#stage")
            elapsed = 0
            for index, scene in enumerate(script["scenes"]):
                page.evaluate("t => window.renderAt(t)", elapsed + scene["duration"] / 2)
                stage.screenshot(path=str(output / f"scene-{index + 1}.png"))
                elapsed += scene["duration"]
            # Archivo de stderr evita bloquear el pipe al llenarse durante un render largo.
            with (output / "encoder.log").open("wb") as errors:
                encoder = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=errors)
                frame_count = round(duration * settings.fps)
                for frame in range(frame_count):
                    t = duration if frame == frame_count - 1 else frame / settings.fps
                    page.evaluate("t => window.renderAt(t)", t)
                    encoder.stdin.write(stage.screenshot(type="jpeg", quality=97))
                    if frame % (settings.fps * 4) == 0:
                        LOGGER.info("Render nativo %dx%d: %d/%.2fs", WIDTH, HEIGHT,
                                    frame // settings.fps, duration)
                encoder.stdin.close()
                if encoder.wait(timeout=120):
                    raise RuntimeError("FFmpeg falló; consulta encoder.log")
            browser.close()
            browser = None
        report = verify_video(partial, settings, expected_duration=duration,
                              has_audio=audio_path is not None)
        partial.replace(target)
        (output / "visual-checks.json").write_text(json.dumps(checks, indent=2),
                                                   encoding="utf-8")
        (output / "verification.json").write_text(json.dumps(report, indent=2),
                                                  encoding="utf-8")
        LOGGER.info("Reel listo para revisión, no publicado: %s", target)
        return target
    except Exception:
        LOGGER.error("Exportación del reel interrumpida; no se publicará ningún archivo")
        raise
    finally:
        if encoder is not None and encoder.poll() is None:
            encoder.kill()
            encoder.wait()
        if browser is not None:
            try:
                browser.close()
            except Exception:
                LOGGER.warning("El contexto de Chromium ya se cerró durante la salida")
