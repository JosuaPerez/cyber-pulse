"""Render actual per-frame motion; no TTS calls, no publishing, no new packages."""

import argparse
import base64
import hashlib
import json
import subprocess

from build_git_history_lab import ROOT, demonstrate


def build(output):
    source = ROOT / "cyberpulse-bot/content/labs"
    script = json.loads((source / "git-history-motion.json").read_text(encoding="utf-8"))
    evidence = demonstrate()
    payload = json.dumps({"script": script, "evidence": evidence}, ensure_ascii=False)
    html = (source / "git-history-motion.html").read_text(encoding="utf-8")
    html = html.replace("__LAB_DATA__", payload.replace("<", "\\u003c"))
    for token, filename in [("SPACE", "space-grotesk-latin.woff2"),
                            ("OSWALD", "oswald-latin.woff2")]:
        font = (ROOT / "cyberpulse-templates/public/fonts" / filename).read_bytes()
        html = html.replace(f"__{token}_FONT__",
                            "data:font/woff2;base64," + base64.b64encode(font).decode())
    output.mkdir(parents=True, exist_ok=True)
    (output / "preview.html").write_text(html, encoding="utf-8")
    (output / "evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    return script


def render(output, script, opening_only=False):
    import imageio_ffmpeg
    from moviepy import VideoFileClip
    from PIL import Image, ImageOps
    from playwright.sync_api import sync_playwright

    duration = 6 if opening_only else sum(s["duration"] for s in script["scenes"])
    fps = 24
    target = output / ("apertura-6s-sin-voz.mp4" if opening_only else "lab-motion-sin-voz.mp4")
    command = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
               "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", str(fps),
               "-i", "pipe:0", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-movflags", "+faststart", str(target)]
    frame_hashes = {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        encoder = None
        try:
            page = browser.new_page(viewport={"width": 1080, "height": 1100})
            page.goto((output / "preview.html").as_uri())
            page.evaluate("document.fonts.ready")
            stage = page.locator("#stage")
            page.evaluate("window.renderAt(.5)")
            initial_opacity = float(page.locator("#key").evaluate("e => e.style.opacity"))
            page.evaluate("window.renderAt(1.5)")
            removed_opacity = float(page.locator("#key").evaluate("e => e.style.opacity"))
            assert initial_opacity > removed_opacity + .5, "Key does not disappear"
            page.evaluate("window.renderAt(5)")
            initial_cursor = page.locator("#cursor").evaluate("e => e.style.left")
            page.evaluate("window.renderAt(8)")
            assert initial_cursor != page.locator("#cursor").evaluate(
                "e => e.style.left"
            ), "History cursor does not move"
            for second in [0, 2, 5, 8, 12, 20, 27]:
                page.evaluate("t => window.renderAt(t)", second)
                assert page.evaluate(
                    "document.querySelector('.note').getBoundingClientRect().bottom < "
                    "document.querySelector('.footer').getBoundingClientRect().top"
                ), f"Footer overlap at {second}s"
                stage.screenshot(path=str(output / f"frame-{second:02}.png"))
            encoder = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            for frame in range(round(duration * fps)):
                page.evaluate("t => window.renderAt(t)", frame / fps)
                image = stage.screenshot(type="jpeg", quality=88)
                encoder.stdin.write(image)
                if frame in [0, 12, 24, 36, 48, 60, 72]:
                    frame_hashes[str(frame)] = hashlib.sha256(image).hexdigest()
                if frame % (fps * 5) == 0:
                    print(f"Rendered {frame // fps}/{duration}s", flush=True)
            encoder.stdin.close()
            errors = encoder.stderr.read().decode(errors="replace")
            if encoder.wait() != 0:
                raise RuntimeError("Video encoder failed: " + errors[:300])
        finally:
            if encoder is not None and encoder.poll() is None:
                encoder.kill()
                encoder.wait()
            browser.close()
    assert len(set(frame_hashes.values())) >= 5, "Opening is not moving"
    with VideoFileClip(str(target)) as video:
        assert abs(video.duration - duration) < .1
        assert video.size == [540, 960] and video.audio is None
        decoded = [hashlib.sha256(video.get_frame(t).tobytes()).hexdigest()
                   for t in [.5, 1, 1.5, 2, 2.5]]
        assert len(set(decoded)) >= 4, "Encoded video lost opening motion"
    overview = Image.new("RGB", (1350, 480), "#1b2637")
    for index, second in enumerate([0, 2, 8, 12, 20]):
        with Image.open(output / f"frame-{second:02}.png") as image:
            overview.paste(ImageOps.contain(image.convert("RGB"), (264, 470)),
                           (index * 270 + 3, 5))
    overview.save(output / "motion-storyboard.png")
    (output / "render-checks.json").write_text(json.dumps({
        "duration": duration, "fps": fps, "audio": False,
        "opening_frame_hashes": frame_hashes, "decoded_opening_frames_differ": True,
        "key_disappears": True, "history_cursor_moves": True,
        "timing": "provisional; not aligned to speech",
    }, indent=2), encoding="utf-8")
    print(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--opening-only", action="store_true")
    args = parser.parse_args()
    output = ROOT / "cyberpulse-bot/media/labs/git-history-motion-v2"
    script = build(output)
    if args.render:
        render(output, script, args.opening_only)
    print(output / "preview.html")


if __name__ == "__main__":
    main()
