"""Exporta las propuestas locales de alertas sin tocar el bot ni publicar."""

import argparse
from pathlib import Path
from urllib.parse import urlencode, urlsplit

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
SIZE = (1080, 1350)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:5173")
    parser.add_argument("--output", type=Path, default=ROOT / "cyberpulse-bot/media/alert-preview")
    args = parser.parse_args()
    parsed = urlsplit(args.url)
    if parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost"}:
        parser.error("Usa un servidor HTTP local")
    args.output.mkdir(parents=True, exist_ok=True)
    samples = {
        "update": {"preview": "alerts", "variant": "update"},
        "scam": {"preview": "alerts", "variant": "scam"},
        "context": {"preview": "alerts", "variant": "context"},
        "actions": {"preview": "alerts", "variant": "actions"},
        "before": {"type": "cover", "familia": "alerta", "level": "medium",
                   "category": "DEMO EDITORIAL", "title": "Una actualización. Menos riesgo.",
                   "description": "Ejemplo ficticio. No es una alerta real.", "totalSlides": "4"},
    }
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": SIZE[0], "height": SIZE[1]})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("**/*", lambda route: route.continue_()
                       if urlsplit(route.request.url).hostname == parsed.hostname else route.abort())
            for name, params in samples.items():
                page.goto(args.url.rstrip("/") + "/?" + urlencode(params))
                page.locator("h1").wait_for()
                page.evaluate("document.fonts.ready")
                page.add_style_tag(content="*{animation:none!important;transition:none!important}")
                if errors:
                    raise RuntimeError("Errores de página: " + "; ".join(errors))
                path = args.output / f"{name}.png"
                page.screenshot(path=str(path))
                if name != "before":
                    overflow = page.evaluate("""() => {
                        const root = document.querySelector('.alert-preview');
                        const body = document.querySelector('.alert-body');
                        return root.scrollHeight > root.clientHeight + 1 ||
                               body.scrollWidth > body.clientWidth + 1 ||
                               body.scrollHeight > body.clientHeight + 1;
                    }""")
                    if overflow:
                        raise RuntimeError(f"Desbordamiento en {name}")
                with Image.open(path) as image:
                    if image.size != SIZE:
                        raise RuntimeError(f"Dimensiones incorrectas en {name}")
                print(path.resolve())
        finally:
            browser.close()
    labels = [("before", "ACTUAL · MISMO EJEMPLO"), ("update", "A · ACTUALIZACIÓN"),
              ("scam", "B · SEÑALES DE ESTAFA"), ("context", "C · CONTEXTO")]
    sheet = Image.new("RGB", (1120, 1480), "#182235")
    draw = ImageDraw.Draw(sheet)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 21) if font_path.is_file() else ImageFont.load_default()
    for index, (name, label) in enumerate(labels):
        x, y = (index % 2) * 560 + 10, (index // 2) * 740 + 10
        draw.text((x + 10, y + 4), label, fill="white", font=font)
        with Image.open(args.output / f"{name}.png") as image:
            sheet.paste(image.resize((540, 675), Image.Resampling.LANCZOS), (x, y + 35))
    sheet.save(args.output / "comparison.png")
    print("Comparación:", (args.output / "comparison.png").resolve())


if __name__ == "__main__":
    main()
