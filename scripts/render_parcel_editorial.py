"""Export the v2 guide and educational carousel without modifying the live bot."""

from pathlib import Path

from PIL import Image, ImageOps
from playwright.sync_api import sync_playwright


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "cyberpulse-bot/media/content/2026-10-paquetes/editorial-v2"
    output.mkdir(parents=True, exist_ok=True)
    selectors = ["cheat-sheet-v2", *(f"carousel-{n}" for n in range(1, 5))]
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 1500})
        page.goto((root / "docs/content/paquetes-editorial-v2.html").as_uri())
        page.evaluate("document.fonts.ready")
        assert page.evaluate("document.fonts.check('24px Space')")
        assert page.evaluate("document.fonts.check('24px Oswald')")
        for selector in selectors:
            locator = page.locator(f"#{selector}")
            assert locator.evaluate(
                "e => e.scrollWidth <= e.clientWidth && e.scrollHeight <= e.clientHeight"
            ), f"Overflow: {selector}"
            locator.screenshot(path=str(output / f"{selector}.png"))
        browser.close()
    overview = Image.new("RGB", (1440, 450), "#202938")
    for index in range(1, 5):
        with Image.open(output / f"carousel-{index}.png") as image:
            assert image.size == (1080, 1350)
            overview.paste(ImageOps.contain(image.convert("RGB"), (352, 440)),
                           ((index - 1) * 360 + 4, 5))
    overview.save(output / "carousel-overview.png")
    print(output)


if __name__ == "__main__":
    main()
