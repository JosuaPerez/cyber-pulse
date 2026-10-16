"""Prueba local de alertas claras/editoriales; no llama a IA ni publica."""

import argparse
import copy
import json
from pathlib import Path
from urllib.parse import urlsplit

from app import config
from app.generador import generar_imagenes_carrusel

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:5173")
    parser.add_argument("--output", type=Path, default=ROOT / "media/alert-editorial")
    parser.add_argument("--stress", action="store_true", help="Comprueba textos en los límites del esquema")
    parser.add_argument("--variant", choices=["editorial", "clara"], default="editorial")
    parser.add_argument("--example", choices=["demo", "firefox", "pwnescape"], default="demo")
    args = parser.parse_args()
    url = urlsplit(args.url)
    if url.scheme != "http" or url.hostname not in {"127.0.0.1", "localhost"}:
        parser.error("La demostración requiere un servidor HTTP local")
    data = json.loads((ROOT / "content/alerts/editorial-demo.json").read_text(encoding="utf-8"))
    if args.example == "pwnescape":
        data = json.loads((ROOT / "content/alerts/pwnescape-review.json").read_text(encoding="utf-8"))
    if args.example == "firefox":
        sample_path = ROOT.parent / "cyberpulse-templates/src/content/real-alerts.json"
        sample = json.loads(sample_path.read_text(encoding="utf-8"))["update"]
        slides = sample["slides"]
        data = {
            "slide_1": {"title": slides[0]["title"], "description": slides[0]["description"]},
            "slide_2": {"description": slides[1]["description"]},
            "slide_3": {"description": slides[2]["description"]},
            "slide_4": {"description": slides[3]["description"], "points": slides[3]["summary"]},
            "slide_5": {"description": slides[4]["description"], "points": slides[4]["summary"]},
            "meta": {"familia": "alerta", "severidad": sample["level"],
                     "fuente_nombre": sample["sourceName"] + " · PRUEBA VISUAL",
                     "fuente_url": sample["sourceUrl"], "fecha_fuente": sample["sourceDate"],
                     "cves": json.loads(sample["cves"]), "estado_explotacion": "desconocido"},
        }
        if args.variant == "clara":
            data["slide_1"]["title"] = "¿Usas Firefox? Revisa esta actualización"
            data["meta"]["visual_apoyo"] = {"tipo": "firefox_version", "version": "158"}
    if args.stress:
        from app.esquemas import LIMITES

        data = copy.deepcopy(data)
        for slide, field, limit in [("slide_1", "title", "portada_titulo"),
                                    ("slide_1", "description", "portada_subtitulo"),
                                    ("slide_2", "description", "problema"),
                                    ("slide_3", "description", "dato_tecnico")]:
            data[slide][field] = ("Texto largo de prueba " * 30)[:LIMITES[limit]]
        for slide, limit in [("slide_4", "riesgo"), ("slide_5", "mitigacion")]:
            data[slide]["points"] = [("Texto de prueba en el límite " * 8)[:LIMITES[limit]]] * 3
    previous_url, previous_dir = config.TEMPLATES_BASE_URL, config.IMAGENES_DIR
    try:
        config.TEMPLATES_BASE_URL = args.url.rstrip("/")
        config.IMAGENES_DIR = args.output
        paths = generar_imagenes_carrusel(data, variante_alerta=args.variant)
    finally:
        config.TEMPLATES_BASE_URL, config.IMAGENES_DIR = previous_url, previous_dir
    from PIL import Image, ImageDraw

    columns = 2 if len(paths) == 4 else 3
    sheet = Image.new("RGB", (columns * 540, 1410), "#252b3d")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(paths):
        with Image.open(path) as image:
            if image.size != (1080, 1350):
                raise ValueError(f"Dimensiones inesperadas en {path.name}")
            x, y = index % columns * 540, index // columns * 705
            draw.text((x + 12, y + 8), f"{index + 1} / {len(paths)}", fill="white")
            sheet.paste(image.resize((540, 675), Image.Resampling.LANCZOS), (x, y + 30))
    sheet.save(args.output / "carousel.png")
    print("Carrusel de revisión:", (args.output / "carousel.png").resolve())


if __name__ == "__main__":
    main()
