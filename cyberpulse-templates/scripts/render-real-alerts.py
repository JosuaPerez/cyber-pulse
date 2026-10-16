"""Render local de tres noticias verificadas. Sin IA ni publicación."""

import argparse
import json
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:5173")
    args = parser.parse_args()
    host = urlsplit(args.url)
    if host.scheme != "http" or host.hostname not in {"127.0.0.1", "localhost"}:
        parser.error("Se requiere un servidor HTTP local")
    output = ROOT / "cyberpulse-bot/media/real-alerts-2026-10-14"
    data = json.loads((ROOT / "cyberpulse-templates/src/content/real-alerts.json").read_text(encoding="utf-8"))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1080, "height": 1350})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("**/*", lambda route: route.continue_()
                       if urlsplit(route.request.url).hostname == host.hostname else route.abort())
            for variant, example in data.items():
                directory = output / variant
                directory.mkdir(parents=True, exist_ok=True)
                sheet = Image.new("RGB", (1620, 1410), "#252b3d")
                draw = ImageDraw.Draw(sheet)
                for i in range(5):
                    params = {"preview": "real-alerts", "variant": variant, "slide": i + 1}
                    page.goto(args.url.rstrip("/") + "/?" + urlencode(params))
                    page.locator(".daily-alert").wait_for()
                    page.evaluate("document.fonts.ready")
                    if errors:
                        raise RuntimeError("; ".join(errors))
                    overflow = page.evaluate("""() => {
                        const r = document.querySelector('.daily-alert');
                        const b = document.querySelector('.daily-content');
                        return r.scrollHeight > r.clientHeight + 1 || r.scrollWidth > r.clientWidth + 1 ||
                               b.scrollHeight > b.clientHeight + 1 || b.scrollWidth > b.clientWidth + 1;
                    }""")
                    if overflow:
                        raise RuntimeError(f"Desbordamiento en {variant}: {i + 1}")
                    if example["sourceName"] not in page.locator('.daily-source').inner_text():
                        raise RuntimeError("Falta la atribución")
                    path = directory / f"slide_{i + 1}.png"
                    page.screenshot(path=str(path))
                    with Image.open(path) as image:
                        if image.size != (1080, 1350):
                            raise RuntimeError("Dimensiones incorrectas")
                        x, y = i % 3 * 540, i // 3 * 705
                        draw.text((x + 12, y + 8), f"{i + 1} / 5", fill="white")
                        sheet.paste(image.resize((540, 675), Image.Resampling.LANCZOS), (x, y + 30))
                sheet.save(directory / "carousel.png")
                print((directory / "carousel.png").resolve())
        finally:
            browser.close()
    comparison = Image.new("RGB", (1620, 730), "#252b3d")
    draw = ImageDraw.Draw(comparison)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 22) if font_path.is_file() else ImageFont.load_default()
    for i, (variant, label) in enumerate([
        ("update", "A · Firefox · 13/10/2026"),
        ("editorial", "B · Power BI · septiembre 2026"),
        ("context", "C · Discord · HISTÓRICO 2025"),
    ]):
        x = i * 540
        draw.text((x + 15, 13), label, fill="white", font=font)
        with Image.open(output / variant / "slide_1.png") as image:
            comparison.paste(image.resize((540, 675), Image.Resampling.LANCZOS), (x, 50))
    comparison.save(output / "covers.png")


if __name__ == "__main__":
    main()
