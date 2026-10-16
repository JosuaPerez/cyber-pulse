"""Analiza una URL real y exporta una alerta para revisión, sin publicar ni tocar el historial."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from google import genai
from PIL import Image

from app import config
from app.analizador import analizar_noticia
from app.generador import generar_imagenes_carrusel


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True, help="Artículo HTTPS; se descarga con http_seguro")
    parser.add_argument("--title", required=True, help="Título real del artículo")
    args = parser.parse_args()
    if urlsplit(args.url).scheme != "https":
        parser.error("La fuente debe usar HTTPS")
    if not config.GEMINI_API_KEY:
        parser.error("Falta GEMINI_API_KEY; no se ha llamado a la API")
    # Este módulo no importa publicadores, almacenamiento R2 ni historial_db.
    # No se inicia el centinela ni se lee/reserva una entrada RSS.
    config.DRY_RUN = True
    config.PUBLICAR_EN_X = False
    config.ALERTAS_VARIANTE = "clara"
    previous_dir = config.IMAGENES_DIR
    output = Path(__file__).resolve().parents[1] / "media/revision-alertas" / datetime.now(
        timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    config.IMAGENES_DIR = output
    try:
        with genai.Client(api_key=config.GEMINI_API_KEY) as client:
            data = analizar_noticia(client, {"title": args.title, "link": args.url, "summary": ""},
                                    modelo=config.GEMINI_MODEL)
        data["meta"]["fuente_nombre"] += " · REVISIÓN SIN PUBLICAR"
        (output / "analisis.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        paths = generar_imagenes_carrusel(data, variante_alerta="clara")
        if len(paths) != 4:
            raise RuntimeError("La revisión requiere exactamente cuatro imágenes")
        sheet = Image.new("RGB", (1080, 1350), "#080f20")
        for index, path in enumerate(paths):
            with Image.open(path) as rendered:
                if rendered.size != (1080, 1350):
                    raise RuntimeError("Dimensiones incorrectas")
                sheet.paste(rendered.resize((540, 675), Image.Resampling.LANCZOS),
                            (index % 2 * 540, index // 2 * 675))
        sheet.save(output / "carousel.png")
        print("Revisión generada (sin publicar):", output)
        print("Visual:", data["meta"].get("visual_apoyo", {}).get("tipo", "ninguno"))
    finally:
        config.IMAGENES_DIR = previous_dir


if __name__ == "__main__":
    main()
