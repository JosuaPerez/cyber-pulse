import logging

from google import genai

from app import config
from app.analizador_educativo import analizar_tema_educativo
from app.generador import generar_imagenes_carrusel
from app.historial_db import marcar_tema_usado, tema_ya_usado
from app.temas_educativos import TEMAS_EDUCATIVOS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
log = logging.getLogger("cyberpulse.bot_educativo")


def siguiente_tema_pendiente():
    """Devuelve el primer tema no registrado como usado en SQLite."""
    return next(
        (tema for tema in TEMAS_EDUCATIVOS if not tema_ya_usado(tema["id"])),
        None,
    )


def escribir_post_pendiente(datos: dict) -> None:
    """Escribe el mismo formato de revisión que usa el flujo de alertas."""
    ruta = config.MEDIA_DIR / "post_pendiente_educativo.txt"
    meta = datos.get("meta", {})
    with ruta.open("w", encoding="utf-8") as archivo:
        archivo.write("CAPTION\n")
        archivo.write(datos.get("caption", ""))
        archivo.write("\n\n--------------------\n\n")
        for indice, tweet in enumerate(datos.get("hilo_x", []), 1):
            archivo.write(f"Tweet {indice}\n{tweet}\n\n")
        archivo.write(
            f"Severidad: {meta.get('severidad', '')}\n"
            f"CVEs: {', '.join(meta.get('cves', []))}\n"
        )
    log.info("Post educativo pendiente guardado en: %s", ruta)


def ejecutar() -> None:
    tema = siguiente_tema_pendiente()
    if tema is None:
        log.info("No quedan temas educativos pendientes")
        return
    if not config.GEMINI_API_KEY:
        raise RuntimeError("Falta GEMINI_API_KEY para generar contenido educativo")

    log.info("Generando tema educativo: %s", tema["id"])
    cliente = genai.Client(api_key=config.GEMINI_API_KEY)
    datos = analizar_tema_educativo(cliente, tema, modelo=config.GEMINI_MODEL)
    config.IMAGENES_DIR = config.IMAGENES_DIR / "educativo" / tema["id"]
    rutas = generar_imagenes_carrusel(datos)
    if len(rutas) != 5:
        raise RuntimeError(f"Se esperaban 5 imágenes, se generaron {len(rutas)}")
    escribir_post_pendiente(datos)
    marcar_tema_usado(tema["id"])
    log.info("Tema educativo marcado como usado: %s", tema["id"])


if __name__ == "__main__":
    ejecutar()
