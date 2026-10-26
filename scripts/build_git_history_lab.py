"""Build a local-only Git demonstration with fixed, deliberately invalid data.

Never accepts an existing repository, never configures a remote, never reads .env.
Files written by this program are generated demo fixtures and review artifacts.
"""

import argparse
import base64
import json
import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory, gettempdir

ROOT = Path(__file__).resolve().parents[1]
DUMMY = "DEMO_ONLY_NOT_VALID_001"
BEFORE = f"APP_MODE=training\nAPI_TOKEN={DUMMY}\n"
AFTER = "APP_MODE=training\n# Credencial retirada de este archivo.\n"


def demonstrate():
    """Create two commits in a fresh OS-temp repo, then verify their contents."""
    temp_root = Path(gettempdir()).resolve()
    with TemporaryDirectory(prefix="cyberpulse-lab-", dir=temp_root) as folder:
        repo = Path(folder).resolve()
        # Validate the exact temporary target before TemporaryDirectory cleans it up.
        assert repo.parent == temp_root and repo.name.startswith("cyberpulse-lab-")
        assert not repo.is_relative_to(ROOT)
        env = {key: value for key, value in os.environ.items()
               if not key.startswith("GIT_")}
        env.update({
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "CyberPulse Lab", "GIT_COMMITTER_NAME": "CyberPulse Lab",
            "GIT_AUTHOR_EMAIL": "lab@example.invalid",
            "GIT_COMMITTER_EMAIL": "lab@example.invalid",
            "GIT_AUTHOR_DATE": "2026-10-18T12:00:00+00:00",
            "GIT_COMMITTER_DATE": "2026-10-18T12:00:00+00:00",
            "GIT_TERMINAL_PROMPT": "0",
        })

        def git(*args):
            result = subprocess.run(
                ["git", "-c", "core.hooksPath=empty-hooks", *args], cwd=repo,
                env=env, capture_output=True, text=True, encoding="utf-8", check=True,
            )
            return result.stdout

        (repo / "empty-hooks").mkdir()
        (repo / "empty-template").mkdir()
        git("init", "--template=empty-template", "-b", "main")
        assert Path(git("rev-parse", "--show-toplevel").strip()).resolve() == repo
        fixture = repo / "app.ini"
        fixture.write_text(BEFORE, encoding="utf-8")
        git("add", "app.ini")
        git("commit", "-m", "lab: add deliberately invalid credential")
        fixture.write_text(AFTER, encoding="utf-8")
        git("add", "app.ini")
        git("commit", "-m", "lab: remove credential from current file")
        current = git("show", "HEAD:app.ini")
        previous = git("show", "HEAD~1:app.ini")
        assert DUMMY not in current and DUMMY in previous
        assert git("rev-list", "--count", "HEAD").strip() == "2"
        assert not git("remote").strip()
        return {
            "dummy": DUMMY, "current": current, "previous": previous,
            "head": git("rev-parse", "HEAD").strip(),
            "previous_commit": git("rev-parse", "HEAD~1").strip(),
            "remote_count": 0, "commit_count": 2,
            "scope": "Fresh temporary local repository; no real credentials or network",
        }


def build(output):
    source = ROOT / "cyberpulse-bot/content/labs"
    script = json.loads((source / "git-history.json").read_text(encoding="utf-8"))
    evidence = demonstrate()
    output.mkdir(parents=True, exist_ok=True)
    payload = json.dumps({"script": script, "evidence": evidence}, ensure_ascii=False)
    html = (source / "git-history.html").read_text(encoding="utf-8")
    html = html.replace("__LAB_DATA__", payload.replace("<", "\\u003c"))
    for token, filename in [("SPACE", "space-grotesk-latin.woff2"),
                            ("OSWALD", "oswald-latin.woff2")]:
        font = (ROOT / "cyberpulse-templates/public/fonts" / filename).read_bytes()
        html = html.replace(f"__{token}_FONT__",
                            "data:font/woff2;base64," + base64.b64encode(font).decode())
    (output / "preview.html").write_text(html, encoding="utf-8")
    (output / "evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "caption.txt").write_text(script["caption"], encoding="utf-8")
    return script


def render(output, script):
    from moviepy import ImageClip, VideoFileClip, concatenate_videoclips
    from PIL import Image, ImageOps
    from playwright.sync_api import sync_playwright

    total = sum(scene["duration"] for scene in script["scenes"])
    starts = []
    elapsed = 0
    for scene in script["scenes"]:
        starts.append(elapsed)
        elapsed += scene["duration"]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            page = browser.new_page(viewport={"width": 1080, "height": 1200},
                                    device_scale_factor=2)
            page.goto((output / "preview.html").as_uri())
            page.evaluate("document.fonts.ready")
            for index, start in enumerate(starts):
                page.evaluate("t => window.renderAt(t)", start + .01)
                stage = page.locator("#stage")
                assert stage.evaluate(
                    "e => e.scrollHeight <= e.clientHeight && e.scrollWidth <= e.clientWidth"
                ), f"Overflow in scene {index + 1}"
                # Footer must not overlap the final visible text above it.
                assert page.evaluate(
                    "document.querySelector('.disclaimer').getBoundingClientRect().bottom"
                    " < document.querySelector('.footer').getBoundingClientRect().top"
                ), f"Footer overlap in scene {index + 1}"
                stage.screenshot(path=str(output / f"scene-{index + 1}.png"))
        finally:
            browser.close()
    overview = Image.new("RGB", (1350, 480), "#1b2637")
    clips = []
    try:
        for index, scene in enumerate(script["scenes"]):
            path = output / f"scene-{index + 1}.png"
            with Image.open(path) as image:
                assert image.size == (1080, 1920)
                overview.paste(ImageOps.contain(image.convert("RGB"), (264, 470)),
                               (index * 270 + 3, 5))
            clips.append(ImageClip(str(path)).resized(width=540)
                         .with_duration(scene["duration"]))
        overview.save(output / "storyboard.png")
        video = concatenate_videoclips(clips)
        try:
            video.write_videofile(str(output / "lab-sin-voz.mp4"), fps=24,
                                 codec="libx264", audio=False, logger=None,
                                 ffmpeg_params=["-pix_fmt", "yuv420p", "-movflags", "+faststart"])
        finally:
            video.close()
        with VideoFileClip(str(output / "lab-sin-voz.mp4")) as check:
            assert abs(check.duration - total) < .1
            assert check.size == [540, 960] and check.audio is None
    finally:
        for clip in clips:
            clip.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render", action="store_true", help="Export silent review MP4")
    args = parser.parse_args()
    output = ROOT / "cyberpulse-bot/media/labs/git-history-v1"
    script = build(output)
    if args.render:
        render(output, script)
    print(output)


if __name__ == "__main__":
    main()
