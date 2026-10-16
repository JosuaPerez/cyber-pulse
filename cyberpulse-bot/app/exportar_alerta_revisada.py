"""Exporta una edición editorial manual como paquete de publicación, sin IA ni redes sociales."""

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from zipfile import ZipFile

from PIL import Image

from app import config
from app.editorial_alertas import EditorialAlerta
from app.generador import generar_imagenes_carrusel

ROOT = Path(__file__).resolve().parents[1]


def aplicar_revision(datos, revision):
    """La revisión es una decisión humana explícita, no una validación automática de la fuente."""
    e = EditorialAlerta.model_validate(revision["editorial"])
    fuente_url = revision["fuente_url"]
    url = urlsplit(fuente_url)
    if url.scheme != "https" or not url.hostname:
        raise ValueError("La revisión requiere una fuente HTTPS")
    resultado = copy.deepcopy(datos)
    resultado["meta"].update({"editorial": e.model_dump(), "editorial_version": 2,
                              "fuente_nombre": revision["fuente_nombre"], "fuente_url": fuente_url,
                              "fecha_fuente": revision["fecha_fuente"],
                              "revision_manual": {"fecha": revision["fecha_revision"], "nota": revision["nota_revision"]}})
    # El mapa neutral no necesita convertir una edición manual en una cadena no comprobada.
    resultado["meta"]["visual_apoyo"] = {"tipo": "editorial", "clase": "resumen", "nodos": []}
    resultado["caption"] = (f"{e.caption}\n\nFuente: {revision['fuente_nombre']}\n{fuente_url}"
                            "\n\n#Ciberseguridad #SeguridadDigital #Privacidad #CyberPulse")
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    args = parser.parse_args()
    datos = json.loads(args.analysis.read_text(encoding="utf-8"))
    revision = json.loads(args.review.read_text(encoding="utf-8"))
    data = aplicar_revision(datos, revision)
    output = ROOT / "media/publicacion-revisada" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    original = config.IMAGENES_DIR
    config.IMAGENES_DIR = output
    try:
        paths = generar_imagenes_carrusel(data, variante_alerta="clara")
        if len(paths) != 4:
            raise RuntimeError("Se requieren cuatro imágenes completas")
        sheet = Image.new("RGB", (1080, 1350), "#080f20")
        for i, path in enumerate(paths):
            with Image.open(path) as rendered:
                if rendered.size != (1080, 1350):
                    raise RuntimeError("Dimensiones incorrectas")
                sheet.paste(rendered.resize((540, 675), Image.Resampling.LANCZOS), (i % 2 * 540, i // 2 * 675))
        sheet.save(output / "vista-previa.png")
        caption = output / "caption.txt"
        caption.write_text(data["caption"], encoding="utf-8")
        (output / "registro_revision.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        instrucciones = output / "LEEME.txt"
        instrucciones.write_text("Publica slide_1.png a slide_4.png en ese orden. Copia caption.txt.\n"
                                  "No publiques vista-previa.png ni el registro JSON.\n"
                                  "Exportación revisada manualmente. No se ha publicado en ninguna red.\n", encoding="utf-8")
        with ZipFile(output / "cyberpulse-alerta-v2.zip", "w") as bundle:
            for path in [*paths, caption, instrucciones]:
                bundle.write(path, arcname=path.name)
        print("Paquete revisado (sin publicar):", output)
    finally:
        config.IMAGENES_DIR = original


if __name__ == "__main__":
    main()
