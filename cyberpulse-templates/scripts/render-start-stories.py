"""Exporta historias de bienvenida locales; no publica ni conecta con Instagram."""

from pathlib import Path
from zipfile import ZipFile

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "cyberpulse-templates/content/stories-start.html"
OUTPUT = ROOT / "cyberpulse-bot/media/instagram-empieza"


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    files = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("**/*", lambda route: route.continue_()
                       if route.request.url.startswith("file:") else route.abort())
            for slide in ["1", "2", "3", "cover"]:
                size = {"width": 1080, "height": 1080 if slide == "cover" else 1920}
                page.set_viewport_size(size)
                page.goto(SOURCE.as_uri() + "?slide=" + slide)
                page.evaluate("document.fonts.ready")
                if not page.evaluate("document.fonts.check('700 40px Space')"):
                    raise RuntimeError("No se cargó la fuente local")
                overflow = page.evaluate("""() => {
                    const root = document.querySelector('.active');
                    const box = root.getBoundingClientRect();
                    return root.scrollHeight > root.clientHeight + 1 ||
                        root.scrollWidth > root.clientWidth + 1 ||
                        [...root.querySelectorAll('*')].some(el => {
                            const r = el.getBoundingClientRect();
                            return r.width && r.height && (r.bottom > box.bottom + 1 ||
                                r.right > box.right + 1 || r.left < box.left - 1);
                        });
                }""")
                if overflow or errors:
                    raise RuntimeError(f"Historia {slide}: desbordamiento o errores {errors}")
                path = OUTPUT / ("portada-empieza.png" if slide == "cover" else f"historia-{slide}.png")
                page.screenshot(path=str(path))
                with Image.open(path) as rendered:
                    if rendered.size != (size["width"], size["height"]):
                        raise RuntimeError("Dimensiones incorrectas")
                files.append(path)
                print(path)
        finally:
            browser.close()
    sheet = Image.new("RGB", (1080, 640), "#080f20")
    for index, path in enumerate(files[:3]):
        with Image.open(path) as rendered:
            sheet.paste(rendered.resize((360, 640), Image.Resampling.LANCZOS), (index * 360, 0))
    sheet.save(OUTPUT / "vista-previa.png")
    with ZipFile(OUTPUT / "cyberpulse-empieza.zip", "w") as bundle:
        for path in files:
            bundle.write(path, arcname=path.name)
    print("Verificados: 3 historias 1080x1920 y portada 1080x1080. Sin publicar.")


if __name__ == "__main__":
    main()
