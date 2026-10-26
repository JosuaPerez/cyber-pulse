"""Render manually researched news with the real alert template; never publish.

This command deliberately does not certify manual research as automatic v3 validation.
No Gemini, history database, R2 or Meta imports/calls are used.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def review_package(review):
    sys.path.insert(0, str(ROOT / "cyberpulse-bot"))
    from app.alertas_v3 import (
        AnalisisAlerta,
        a_datos_publicacion,
        validar_paquete_publicacion,
    )

    analysis = AnalisisAlerta.model_validate(review["analysis"])
    package = a_datos_publicacion(analysis, review["source_name"], review["source_url"])
    package["meta"].pop("validacion", None)
    package["meta"]["revision_manual"] = {
        "fecha": review["reviewed_at_utc"], "estado": "pendiente_aprobacion_usuario",
        "nota": "Redacción manual multifuente; validación de esquema, no validación automática contra fuentes.",
    }
    package["meta"]["fecha_fuente"] = review["source_date"]
    package["meta"]["visual_apoyo"] = review["visual"]
    extra_sources = [source["url"] for source in review["sources"]
                     if source["url"] != review["source_url"]]
    package["caption"] = (f"{analysis.caption}\n\nFuentes consultadas:\n"
                          + "\n".join([review["source_url"], *extra_sources])
                          + "\n\n" + " ".join(analysis.hashtags))
    package.pop("hilo_x", None)
    try:
        validar_paquete_publicacion(package)
    except ValueError:
        pass
    else:
        raise RuntimeError("Manual review must not pass the automatic publication gate")
    return package


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", choices=["php", "emudhra", "all"], default="all")
    args = parser.parse_args()
    # Set safe mode before app.config loads local environment configuration.
    os.environ["DRY_RUN"] = "true"
    os.environ["PUBLICAR_EN_X"] = "false"
    os.environ["TEMPLATES_BASE_URL"] = "http://127.0.0.1:5177"
    os.environ["MEDIA_DIR"] = str(ROOT / "cyberpulse-bot/media")
    os.environ["DATA_DIR"] = str(ROOT / "cyberpulse-bot/data")
    sys.path.insert(0, str(ROOT / "cyberpulse-bot"))
    from app import config
    from app.generador import generar_imagenes_carrusel
    from PIL import Image

    topics = ["php", "emudhra"] if args.topic == "all" else [args.topic]
    original = config.IMAGENES_DIR
    try:
        for topic in topics:
            path = ROOT / f"cyberpulse-bot/content/alerts/reviews/2026-10-21-{topic}.json"
            review = json.loads(path.read_text(encoding="utf-8"))
            package = review_package(review)
            output = ROOT / f"cyberpulse-bot/media/news-review/2026-10-21/{topic}"
            output.mkdir(parents=True, exist_ok=True)
            config.IMAGENES_DIR = output
            images = generar_imagenes_carrusel(package, variante_alerta="clara")
            assert len(images) == 4
            sheet = Image.new("RGB", (1440, 450), "#080f20")
            for index, image_path in enumerate(images):
                with Image.open(image_path) as image:
                    assert image.size == (1080, 1350)
                    sheet.paste(image.convert("RGB").resize((360, 450)), (index * 360, 0))
            sheet.save(output / "vista-previa.png")
            (output / "caption.txt").write_text(package["caption"], encoding="utf-8")
            (output / "registro_revision.json").write_text(
                json.dumps({"review": review, "package": package}, ensure_ascii=False, indent=2),
                encoding="utf-8")
            instructions = (
                "PENDIENTE DE APROBACIÓN. No publicado.\n"
                "Revisa slide_1.png a slide_4.png y caption.txt antes de subir.\n"
                "La vista previa y este registro no se publican.\n"
                "Revalidar fuentes y estado si se publica en otra fecha.\n"
                "No introducir este paquete manual en el publicador automático del bot.\n"
            )
            (output / "LEEME.txt").write_text(instructions, encoding="utf-8")
            with ZipFile(output / f"cyberpulse-{topic}-2026-10-21.zip", "w") as bundle:
                for filename in [*[p.name for p in images], "caption.txt", "LEEME.txt"]:
                    bundle.write(output / filename, arcname=filename)
            print(f"Manual review only: {output}")
    finally:
        config.IMAGENES_DIR = original


if __name__ == "__main__":
    main()
