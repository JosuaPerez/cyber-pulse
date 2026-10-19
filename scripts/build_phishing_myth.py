"""Build the phone-based educational reel; voice is explicit and publication absent."""

import argparse
import asyncio
import base64
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script():
    return json.loads((ROOT / "cyberpulse-bot/content/reels/phishing-myth.json")
                      .read_text(encoding="utf-8"))


def make_voice(script, output):
    from dotenv import load_dotenv
    from moviepy import AudioClip, AudioFileClip, concatenate_audioclips

    sys.path.insert(0, str(ROOT / "cyberpulse-bot"))
    from app.reel_educativo import muestras_silencio
    from app.voz_educativa import generar_escenas

    load_dotenv(ROOT / "cyberpulse-bot/.env")
    print("Generating original synthetic narration with configured Gemini TTS...", flush=True)
    paths = asyncio.run(generar_escenas(
        [s["narration"] for s in script["scenes"]], output / "voice-cache",
        provider="gemini", voice="Charon",
    ))
    resources = []
    try:
        pause = AudioClip(muestras_silencio, duration=.18, fps=44100)
        resources.append(pause)
        segments = []
        for scene, path in zip(script["scenes"], paths, strict=True):
            audio = AudioFileClip(str(path))
            resources.append(audio)
            segment = concatenate_audioclips([audio, pause])
            resources.append(segment)
            scene["duration"] = segment.duration
            segments.append(segment)
        narration = concatenate_audioclips(segments)
        resources.append(narration)
        audio_path = output / "narration.wav"
        narration.write_audiofile(str(audio_path), codec="pcm_s16le", logger=None)
        return audio_path
    finally:
        for resource in reversed(resources):
            resource.close()


def build(output, with_voice=False):
    script = load_script()
    output.mkdir(parents=True, exist_ok=True)
    audio_path = None
    warning = None
    if with_voice:
        try:
            script_with_voice = copy.deepcopy(script)
            audio_path = make_voice(script_with_voice, output)
            script = script_with_voice
        except RuntimeError as error:
            # Existing voice adapter returns sanitized errors, never response bodies.
            warning = str(error)
            print("VOICE UNAVAILABLE: " + warning, flush=True)
    payload = copy.deepcopy(script)
    if audio_path:
        payload["audio"] = "data:audio/wav;base64," + base64.b64encode(
            audio_path.read_bytes()).decode()
    source = ROOT / "cyberpulse-bot/content/reels/phishing-myth.html"
    html = source.read_text(encoding="utf-8").replace(
        "__REEL_DATA__", json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c"))
    for token, filename in [("SPACE", "space-grotesk-latin.woff2"),
                            ("OSWALD", "oswald-latin.woff2")]:
        font = (ROOT / "cyberpulse-templates/public/fonts" / filename).read_bytes()
        html = html.replace(f"__{token}_FONT__",
                            "data:font/woff2;base64," + base64.b64encode(font).decode())
    (output / "preview.html").write_text(html, encoding="utf-8")
    (output / "caption.txt").write_text(script["caption"], encoding="utf-8")
    (output / "timing.json").write_text(json.dumps({
        "voice": bool(audio_path), "voice_error": warning,
        "duration": sum(s["duration"] for s in script["scenes"]),
        "timing": "measured per spoken scene" if audio_path else "provisional silent animatic",
        "scenes": script["scenes"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return script, audio_path


def validate_visuals(page, script):
    """Sample the complete timeline, including late-scene motion and safe text areas."""
    duration = sum(scene["duration"] for scene in script["scenes"])
    checked = 0
    for quarter in range(int(duration * 4)):
        second = quarter / 4
        page.evaluate("t => window.renderAt(t)", second)
        metrics = page.evaluate("""() => {
            const rect = selector => document.querySelector(selector).getBoundingClientRect();
            const note = rect('.note'), footer = rect('.footer');
            const cursor = document.querySelector('#cursor');
            const c = rect('#cursor'), link = rect('#link');
            const visible = !cursor.classList.contains('hidden');
            return {
                footerGap: footer.top - note.bottom,
                cursorOverlap: visible && c.left < link.right && c.right > link.left
                    && c.top < link.bottom && c.bottom > link.top,
                pauseExists: !!document.querySelector('#pause'),
                cursorColor: getComputedStyle(cursor).color
            };
        }""")
        assert not metrics["cursorOverlap"], f"Cursor covers link at {second}s"
        assert not metrics["pauseExists"], "Ambiguous PAUSA control remains"
        assert metrics["footerGap"] >= 24, f"Disclaimer too close to footer at {second}s"
        assert metrics["cursorColor"] == "rgb(80, 220, 228)", "Unexpected cursor accent"
        checked += 1
    start = 0
    motion_scenes = []
    for scene in script["scenes"]:
        if scene["view"] in {"hook", "link", "verify"}:
            ids = ["phone"]
        elif scene["view"] == "cta":
            ids = ["route", "save"]
        else:
            ids = ["icon", "floating", "scan"]

        def signature(second, ids=ids):
            page.evaluate("t => window.renderAt(t)", second)
            return page.evaluate("ids => ids.map(id => {const s=document.getElementById(id).style;"
                                 "return [s.transform,s.top,s.opacity];})", ids)

        first = start + scene["duration"] * .4
        second = start + scene["duration"] * .8
        state = signature(first)
        assert state != signature(second), f"No sustained motion in {scene['view']}"
        assert state == signature(first), "Timeline is not deterministic when seeking"
        motion_scenes.append(scene["view"])
        start += scene["duration"]
    return {"timeline_samples": checked, "cursor_link_overlap": False,
            "minimum_footer_gap_px": 24, "continuous_motion_scenes": motion_scenes,
            "deterministic_seek": True, "ambiguous_pause_removed": True}


def render(output, script, audio_path):
    import imageio_ffmpeg
    from moviepy import VideoFileClip
    from PIL import Image, ImageOps
    from playwright.sync_api import sync_playwright

    fps = 24
    duration = sum(s["duration"] for s in script["scenes"])
    target = output / ("reel-con-voz.mp4" if audio_path else "reel-sin-voz.mp4")
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
               "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", str(fps),
               "-i", "pipe:0"]
    if audio_path:
        command += ["-i", str(audio_path), "-c:a", "aac", "-shortest"]
    else:
        command += ["-an"]
    command += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(target)]
    starts = []
    elapsed = 0
    for scene in script["scenes"]:
        starts.append(elapsed)
        elapsed += scene["duration"]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        encoder = None
        try:
            page = browser.new_page(viewport={"width": 1080, "height": 1150})
            page.goto((output / "preview.html").as_uri())
            page.evaluate("document.fonts.ready")
            stage = page.locator("#stage")
            visual_checks = validate_visuals(page, script)
            for index, start in enumerate(starts):
                page.evaluate("t => window.renderAt(t)", start + script["scenes"][index]["duration"] * .65)
                stage.screenshot(path=str(output / f"scene-{index + 1}.png"))
                assert stage.evaluate("e => e.scrollHeight <= e.clientHeight"), "Stage overflow"
                assert page.evaluate(
                    "document.querySelector('.note').getBoundingClientRect().bottom < "
                    "document.querySelector('.footer').getBoundingClientRect().top"
                ), f"Footer overlap in scene {index + 1}"
            encoder = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            for frame in range(round(duration * fps)):
                page.evaluate("t => window.renderAt(t)", frame / fps)
                encoder.stdin.write(stage.screenshot(type="jpeg", quality=88))
                if frame % (fps * 5) == 0:
                    print(f"Rendered {frame // fps}/{duration:.1f}s", flush=True)
            encoder.stdin.close()
            errors = encoder.stderr.read().decode(errors="replace")
            if encoder.wait() != 0:
                raise RuntimeError("Encoder failed: " + errors[:300])
        finally:
            if encoder is not None and encoder.poll() is None:
                encoder.kill()
                encoder.wait()
            browser.close()
    with VideoFileClip(str(target)) as video:
        assert abs(video.duration - duration) < .15
        assert video.size == [540, 960]
        assert (video.audio is not None) == bool(audio_path)
        hashes = [hashlib.sha256(video.get_frame(t).tobytes()).hexdigest()
                  for t in [.1, .4, .8, 1.2]]
        assert len(set(hashes)) >= 3, "Opening motion lost"
    overview = Image.new("RGB", (1890, 480), "#202b3c")
    for index in range(len(script["scenes"])):
        with Image.open(output / f"scene-{index + 1}.png") as image:
            overview.paste(ImageOps.contain(image.convert("RGB"), (264, 470)),
                           (index * 270 + 3, 5))
    overview.save(output / "storyboard.png")
    (output / "visual-checks.json").write_text(
        json.dumps(visual_checks, indent=2), encoding="utf-8")
    print(target, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--voice", action="store_true", help="Use configured Gemini TTS; consumes quota")
    args = parser.parse_args()
    output = ROOT / "cyberpulse-bot/media/reels/phishing-myth-v2"
    script, audio_path = build(output, args.voice)
    if args.render:
        render(output, script, audio_path)
    print(output / "preview.html")


if __name__ == "__main__":
    main()
