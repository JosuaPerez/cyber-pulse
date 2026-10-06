import logging
import mimetypes
import time
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError, ConnectionError

from app import config

logger = logging.getLogger(__name__)


def subir_imagen_publica(ruta_local, intentos=3, espera_base=2):
    """Sube una imagen a R2 y devuelve su URL pública."""
    ruta = Path(ruta_local)
    nombre_archivo = f"{uuid4().hex}{ruta.suffix}"
    cliente_s3 = boto3.client(
        "s3",
        endpoint_url=config.R2_ENDPOINT_URL,
        aws_access_key_id=config.R2_ACCESS_KEY_ID,
        aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )

    for intento in range(1, intentos + 1):
        logger.info(
            "Subiendo imagen a Cloudflare R2 (intento %d/%d): %s",
            intento,
            intentos,
            ruta_local,
        )
        try:
            contenido_tipo, _ = mimetypes.guess_type(ruta.name)
            opciones = {"Bucket": config.R2_BUCKET_NAME, "Key": nombre_archivo}
            if contenido_tipo:
                opciones["ExtraArgs"] = {"ContentType": contenido_tipo}
            cliente_s3.upload_file(str(ruta), **opciones)
        except (OSError, BotoCoreError, ClientError, ConnectionError) as exc:
            logger.warning(
                "Error subiendo imagen a Cloudflare R2 (intento %d/%d): %s",
                intento,
                intentos,
                exc,
            )
        else:
            url_publica = f"{config.R2_PUBLIC_BASE_URL}/{nombre_archivo}"
            logger.info("Imagen subida correctamente a Cloudflare R2: %s", url_publica)
            return url_publica

        if intento < intentos:
            time.sleep(espera_base * intento)

    logger.error(
        "No se pudo subir %s a Cloudflare R2 tras %d intentos",
        ruta_local,
        intentos,
    )
    return None
