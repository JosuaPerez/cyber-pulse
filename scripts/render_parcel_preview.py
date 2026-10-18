"""Render the editorial review assets locally; never publishes or calls TTS."""

from pathlib import Path

from moviepy import ImageClip, concatenate_videoclips
from playwright.sync_api import sync_playwright


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "cyberpulse-bot/media/content/2026-10-paquetes"
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 1200}, device_scale_factor=2)
        page.goto((root / "docs/content/paquetes-preview.html").as_uri())
        page.evaluate("document.fonts.ready")
        for second, name in [(0, "apertura"), (3, "accion")]:
            page.evaluate("t => window.renderAt(t)", second)
            page.locator("#reel").screenshot(path=str(output / f"{name}.png"))
        page.locator("#guide").screenshot(path=str(output / "cheat-sheet.png"))
        for selector in ["#reel", "#guide"]:
            assert page.locator(selector).evaluate(
                "e => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth"
            ), f"Overflow: {selector}"
        browser.close()
    clips = [ImageClip(str(output / f"{name}.png")).with_duration(2.5)
             for name in ["apertura", "accion"]]
    video = concatenate_videoclips(clips)
    video.write_videofile(str(output / "apertura-5s-sin-voz.mp4"), fps=24,
                          codec="libx264", audio=False,
                          ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"])
    video.close()
    for clip in clips:
        clip.close()
    print(output)


if __name__ == "__main__":
    main()
