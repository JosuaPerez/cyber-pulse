"""Exporta A y C como carruseles de demostración; no publica contenido."""

import argparse
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:5173")
    parser.add_argument("--output", type=Path, default=ROOT / "cyberpulse-bot/media/alert-series")
    args = parser.parse_args()
    host = urlsplit(args.url)
    if host.scheme != "http" or host.hostname not in {"127.0.0.1", "localhost"}:
        parser.error("Usa un servidor HTTP local")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1080, "height": 1350})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("**/*", lambda route: route.continue_()
                       if urlsplit(route.request.url).hostname == host.hostname else route.abort())
            for variant in ["update", "context"]:
                output = args.output / variant
                output.mkdir(parents=True, exist_ok=True)
                sheet = Image.new("RGB", (1620, 1410), "#252b3d")
                draw = ImageDraw.Draw(sheet)
                for index in range(5):
                    params = {"preview": "alerts-series", "variant": variant, "slide": index + 1}
                    page.goto(args.url.rstrip("/") + "/?" + urlencode(params))
                    page.locator(".daily-alert").wait_for()
                    page.evaluate("document.fonts.ready")
                    if errors:
                        raise RuntimeError("; ".join(errors))
                    overflow = page.evaluate("""() => {
                        const root = document.querySelector('.daily-alert');
                        const body = document.querySelector('.daily-content');
                        return root.scrollHeight > root.clientHeight + 1 ||
                               root.scrollWidth > root.clientWidth + 1 ||
                               body.scrollHeight > body.clientHeight + 1 ||
                               body.scrollWidth > body.clientWidth + 1;
                    }""")
                    if overflow:
                        raise RuntimeError(f"Desbordamiento en {variant}, diapositiva {index + 1}")
                    path = output / f"slide_{index + 1}.png"
                    page.screenshot(path=str(path))
                    with Image.open(path) as image:
                        if image.size != (1080, 1350):
                            raise RuntimeError("Dimensiones inesperadas")
                        x, y = index % 3 * 540, index // 3 * 705
                        draw.text((x + 12, y + 8), f"{index + 1} / 5", fill="white")
                        sheet.paste(image.resize((540, 675), Image.Resampling.LANCZOS), (x, y + 30))
                sheet.save(output / "carousel.png")
                print((output / "carousel.png").resolve())
            for variant, slide in [("desconocida", "99"), ("context", "-1")]:
                params = {"preview": "alerts-series", "variant": variant, "slide": slide}
                page.goto(args.url.rstrip("/") + "/?" + urlencode(params))
                page.locator(".daily-alert").wait_for()
                if page.locator("footer").inner_text().find("1 / 5") < 0:
                    raise RuntimeError("No se aplicó el fallback de diapositiva")
                if errors:
                    raise RuntimeError("; ".join(errors))
        finally:
            browser.close()


if __name__ == "__main__":
    main()
