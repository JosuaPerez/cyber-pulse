import logging
import time
from enum import Enum

import requests
from google import genai

from app import config
from app.almacenamiento_r2 import subir_imagen_publica
from app.analizador import ErrorAnalisis, NoticiaDescartada, analizar_noticia
from app.historial_db import (
    actualizar_estado,
    inicializar_db,
    marcar_revision_manual,
    registrar_fallo,
    registrar_publicacion_ambigua,
)
from app.lector_rss import obtener_noticia_nueva
from app.generador import generar_imagenes_carrusel
from app.publicador_x import publicar_hilo_x

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


class ResultadoPublicacion(Enum):
    PUBLICADA = "publicada"
    FALLIDA = "fallida"
    AMBIGUA = "ambigua"

class CyberPulseBot:
    def __init__(self):
        config.validar_config_publicacion()
        self.access_token = config.META_ACCESS_TOKEN
        self.ig_user_id = config.IG_USER_ID
        self.meta_base_url = (
            f"https://graph.facebook.com/{config.META_GRAPH_VERSION}"
        )
        self.gemini_client = genai.Client(api_key=config.GEMINI_API_KEY)
        self.session = requests.Session()
        if self.access_token:
            self.session.headers.update(
                {"Authorization": f"Bearer {self.access_token}"}
            )
        self.ultimo_meta_post_id = None

    def analizar_noticia_con_ia(self, noticia_rss):
        """Procesa la noticia y estructura los datos para las 5 diapositivas."""
        logger.info("Procesando noticia con Gemini: %s", noticia_rss["title"])
        try:
            return analizar_noticia(
                self.gemini_client,
                noticia_rss,
                modelo=config.GEMINI_MODEL,
            )
        except NoticiaDescartada as exc:
            clave = noticia_rss.get("clave_historial", noticia_rss["title"])
            actualizar_estado(clave, "descartada", ultimo_error=str(exc))
            logger.info("Noticia descartada: %s", exc)
            return None
        except ErrorAnalisis as exc:
            clave = noticia_rss.get("clave_historial", noticia_rss["title"])
            requiere_revision = registrar_fallo(clave, str(exc))
            logger.error("No se pudo analizar la noticia: %s", exc)
            if requiere_revision:
                logger.error(
                    "La noticia alcanzo el maximo de intentos y requiere revision manual"
                )
            return None

    def _respuesta_json(self, response, operacion):
        try:
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.error("Error en respuesta de Meta durante %s: %s", operacion, exc)
            return None

    def crear_item_carrusel(self, image_url):
        """Inyecta la URL pública en Meta para crear un contenedor individual."""
        url = f"{self.meta_base_url}/{self.ig_user_id}/media"
        payload = {
            'image_url': image_url, 
            'is_carousel_item': 'true',
        }
        try:
            response = self.session.post(url, data=payload, timeout=config.HTTP_TIMEOUT)
        except requests.RequestException as exc:
            logger.error("Error de red al crear item de carrusel: %s", exc)
            return None

        res = self._respuesta_json(response, "crear item de carrusel")
        if res is None:
            return None
        
        if 'id' not in res:
            logger.error("Meta rechazo la imagen %s: %s", image_url, res)
            return None
            
        return res.get('id')

    def esperar_contenedor_finalizado(self, container_id):
        """Espera hasta que Meta termine de procesar un contenedor.

        FIX 3: registra progreso periódicamente para que quede claro que el
        proceso sigue vivo durante el sondeo (antes se quedaba en silencio
        hasta 90s, lo que hacía parecer que el bot estaba trabado).
        """
        url = f"{self.meta_base_url}/{container_id}"
        inicio = time.monotonic()

        while True:
            transcurrido = time.monotonic() - inicio
            if transcurrido >= config.META_POLL_TIMEOUT:
                break

            try:
                response = self.session.get(
                    url,
                    params={
                        "fields": "status_code",
                    },
                    timeout=config.HTTP_TIMEOUT,
                )
            except requests.RequestException as exc:
                logger.error("Error consultando estado del contenedor Meta: %s", exc)
                return False

            estado = self._respuesta_json(response, "consultar estado del contenedor")
            if estado is None:
                return False

            status_code = estado.get("status_code")
            if status_code == "FINISHED":
                return True
            if status_code == "ERROR":
                logger.error("Meta marco el contenedor %s como ERROR", container_id)
                return False

            logger.info(
                "Esperando a que Meta procese el contenedor %s... "
                "(%.0fs transcurridos de %s maximo, estado actual: %s) "
                "NO cancelar, esto es normal.",
                container_id,
                transcurrido,
                config.META_POLL_TIMEOUT,
                status_code,
            )
            time.sleep(config.META_POLL_INTERVAL)

        logger.error(
            "Timeout esperando el contenedor Meta %s tras %s segundos",
            container_id,
            config.META_POLL_TIMEOUT,
        )
        return False

    def publicar_carrusel_local(self, rutas_imagenes, caption, clave_historial=None):
        """Orquesta la subida, ensamblaje y publicación del carrusel completo.

        FIX 1: en cuanto Meta confirma la publicación, se escribe
        inmediatamente el estado "publicada_meta" en SQLite, en la misma
        función y sin ninguna otra operación de por medio. Así, si el
        proceso se interrumpe justo después, el post ya queda registrado
        como publicado y no se vuelve a publicar en el siguiente ciclo.
        """
        # Se reinicia en cada llamada: si esta publicación no llega a
        # confirmarse, ultimo_meta_post_id debe quedar en None, no arrastrar
        # el id de una noticia anterior.
        self.ultimo_meta_post_id = None

        if not clave_historial:
            raise ValueError(
                "clave_historial es obligatoria para publicar de forma reconciliable"
            )

        if len(rutas_imagenes) != 5:
            logger.error(
                "Se requieren exactamente 5 imagenes para publicar; se recibieron %d",
                len(rutas_imagenes),
            )
            return ResultadoPublicacion.FALLIDA

        item_ids = []
        for indice, ruta in enumerate(rutas_imagenes):
            url_publica = subir_imagen_publica(ruta)
            if url_publica:
                item_id = self.crear_item_carrusel(url_publica)
                if item_id:
                    item_ids.append(item_id)
            if indice < len(rutas_imagenes) - 1:
                time.sleep(config.META_POLL_INTERVAL)

        if len(item_ids) != len(rutas_imagenes):
            logger.error(
                "No se publicara un carrusel incompleto: %d/%d items validos",
                len(item_ids),
                len(rutas_imagenes),
            )
            return ResultadoPublicacion.FALLIDA

        logger.info("Ensamblando estructura del carrusel en Meta")
        url_carousel = f"{self.meta_base_url}/{self.ig_user_id}/media"
        payload_carousel = {
            'media_type': 'CAROUSEL',
            'children': ','.join(item_ids),
            'caption': caption,
        }
        try:
            response_carousel = self.session.post(
                url_carousel,
                data=payload_carousel,
                timeout=config.HTTP_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.error("Error de red al ensamblar el carrusel: %s", exc)
            return ResultadoPublicacion.FALLIDA

        res_carousel = self._respuesta_json(response_carousel, "ensamblar carrusel")
        if res_carousel is None:
            return ResultadoPublicacion.FALLIDA
        
        if 'id' not in res_carousel:
            logger.error("Error al ensamblar el carrusel en Meta: %s", res_carousel)
            return ResultadoPublicacion.FALLIDA
            
        creation_id = res_carousel['id']
        
        if not self.esperar_contenedor_finalizado(creation_id):
            return ResultadoPublicacion.FALLIDA

        actualizar_estado(
            clave_historial,
            "renderizada",
            meta_creation_id=creation_id,
            meta_publicacion_pendiente=1,
        )
        
        logger.info("Enviando orden de publicacion final a Meta")
        url_publish = f"{self.meta_base_url}/{self.ig_user_id}/media_publish"
        try:
            response_final = self.session.post(
                url_publish,
                data={
                    'creation_id': creation_id,
                },
                timeout=config.HTTP_TIMEOUT,
            )
        except requests.RequestException as exc:
            logger.critical(
                "Resultado ambiguo al publicar el carrusel %s: %s",
                creation_id,
                exc,
            )
            registrar_publicacion_ambigua(
                clave_historial,
                creation_id,
                f"Respuesta de media_publish no confirmada: {exc}",
            )
            return ResultadoPublicacion.AMBIGUA

        res_final = self._respuesta_json(response_final, "publicar carrusel")
        if res_final is None:
            registrar_publicacion_ambigua(
                clave_historial,
                creation_id,
                "Meta devolvio una respuesta HTTP o JSON no verificable",
            )
            return ResultadoPublicacion.AMBIGUA

        if 'id' not in res_final:
            logger.error("Error en la publicacion final del carrusel: %s", res_final)
            actualizar_estado(
                clave_historial,
                "renderizada",
                meta_publicacion_pendiente=0,
                ultimo_error=f"Meta rechazo media_publish: {res_final}",
            )
            return ResultadoPublicacion.FALLIDA

        # === A partir de aquí, Meta YA confirmó el post. ===
        # Ninguna línea de aquí en adelante debe ser una llamada de red
        # bloqueante ni nada que pueda demorar: escribir en SQLite es
        # prácticamente instantáneo, minimizando al máximo la ventana en la
        # que un Ctrl+C podría dejar el post publicado sin registrar.
        self.ultimo_meta_post_id = res_final['id']
        logger.info("Carrusel publicado. ID de post: %s", res_final['id'])

        try:
            actualizar_estado(
                clave_historial,
                "publicada_meta",
                meta_post_id=res_final['id'],
            )
        except Exception:
            # No relanzamos: el post YA está en Instagram. Si esta escritura
            # falla, procesar_una_noticia tiene un intento de respaldo usando
            # el mismo ultimo_meta_post_id.
            logger.exception(
                "El post se publico en Meta (id=%s) pero no se pudo "
                "registrar de inmediato en SQLite; se reintentara.",
                res_final['id'],
            )

        return ResultadoPublicacion.PUBLICADA

def ejecutar_modo_centinela():
    inicializar_db()
    bot = CyberPulseBot()
    logger.info("CyberPulse Centinela iniciado")
    
    while True:
        try:
            procesar_una_noticia(bot)
        except KeyboardInterrupt:
            logger.critical("Interrupcion manual (Ctrl+C) recibida. Deteniendo el centinela.")
            raise
        except Exception:
            logger.exception("Fallo no controlado al procesar una noticia")

        logger.info(
            "Proximo escaneo en %s segundos",
            config.INTERVALO_CICLO_SEGUNDOS,
        )
        time.sleep(config.INTERVALO_CICLO_SEGUNDOS)


def procesar_una_noticia(bot):
    """Procesa como maximo una noticia y deja el estado en el historial si publica."""
    noticia = None
    # Nunca se debe heredar el ID confirmado de una noticia anterior. Si la
    # siguiente falla antes de llegar a Meta, conservarlo marcaría la noticia
    # equivocada como publicada.
    bot.ultimo_meta_post_id = None
    try:
        noticia = obtener_noticia_nueva()
        if not noticia:
            logger.info("Sin amenazas nuevas")
            return

        datos_procesados = bot.analizar_noticia_con_ia(noticia)
        if not datos_procesados:
            return

        clave = noticia["clave_historial"]
        meta = datos_procesados.get("meta", {})
        actualizar_estado(
            clave,
            "analizada",
            cves=meta.get("cves", []),
            severidad=meta.get("severidad"),
        )

        logger.info("Generando carrusel")
        rutas_carrusel = generar_imagenes_carrusel(datos_procesados)
        if not rutas_carrusel:
            raise RuntimeError("No se generaron imagenes para el carrusel")
        actualizar_estado(clave, "renderizada")

        caption = datos_procesados.get("caption", "")
        hilo_x = datos_procesados.get("hilo_x")

        if config.DRY_RUN:
            logger.info("DRY_RUN activo. Meta del analisis: %s", meta)
            logger.info("DRY_RUN activo. Caption completo: %s", caption)
            if hilo_x:
                logger.info("DRY_RUN activo. Hilo de X: %s", hilo_x)

            archivo_pendiente = config.IMAGENES_DIR.parent / "post_pendiente.txt"
            with archivo_pendiente.open("w", encoding="utf-8") as archivo:
                archivo.write("CAPTION\n")
                archivo.write(caption)
                archivo.write("\n\n--------------------\n\n")
                for indice, tweet in enumerate(hilo_x or [], 1):
                    archivo.write(f"Tweet {indice}\n{tweet}\n\n")
                archivo.write(
                    f"Severidad: {meta.get('severidad', '')}\n"
                    f"CVEs: {', '.join(meta.get('cves', []))}\n"
                )
            logger.info("Post pendiente guardado en: %s", archivo_pendiente)
            marcar_revision_manual(clave)
            return

        # FIX 1: se pasa clave_historial para que el estado quede escrito
        # inmediatamente dentro de publicar_carrusel_local, apenas Meta
        # confirme el post.
        resultado = bot.publicar_carrusel_local(
            rutas_carrusel,
            caption,
            clave_historial=clave,
        )
        if resultado is ResultadoPublicacion.AMBIGUA:
            logger.critical(
                "La publicacion tiene resultado ambiguo y requiere verificacion manual"
            )
            return
        if resultado is not ResultadoPublicacion.PUBLICADA:
            registrar_fallo(clave, "La publicacion en Meta fallo")
            logger.error("La publicacion en Meta fallo")
            return

        # FIX 1b: respaldo idempotente. Si por algún motivo la escritura
        # inmediata dentro de publicar_carrusel_local no se hizo o falló,
        # esto la deja igualmente en publicada_meta. Si ya estaba escrita,
        # este UPDATE simplemente repite el mismo valor sin efecto negativo.
        if bot.ultimo_meta_post_id:
            actualizar_estado(
                clave,
                "publicada_meta",
                meta_post_id=bot.ultimo_meta_post_id,
            )

        if config.PUBLICAR_EN_X and hilo_x:
            try:
                publicar_hilo_x(rutas_carrusel, datos_procesados)
            except Exception:
                logger.exception("Fallo al publicar el hilo en X")

        logger.info("Ciclo de publicacion completado")

    except KeyboardInterrupt:
        # FIX 4: si Meta ya habia confirmado el post antes de la
        # interrupcion, lo dejamos registrado como publicada_meta en vez de
        # dejarlo en un estado no terminal que provoque una republicacion.
        if noticia and bot.ultimo_meta_post_id:
            try:
                actualizar_estado(
                    noticia["clave_historial"],
                    "publicada_meta",
                    meta_post_id=bot.ultimo_meta_post_id,
                )
            except Exception:
                logger.exception("No se pudo persistir el estado tras la interrupcion")
            logger.critical(
                "Interrumpido con Ctrl+C, pero Meta ya habia confirmado el "
                "post %s: quedo registrado como publicada_meta. NO se "
                "volvera a publicar.",
                bot.ultimo_meta_post_id,
            )
        elif noticia:
            logger.critical(
                "Interrumpido con Ctrl+C durante el procesamiento de '%s'. "
                "Verifica manualmente en Instagram si el post llego a "
                "publicarse antes de dejar correr el bot de nuevo.",
                noticia.get("title"),
            )
        raise

    except Exception as exc:
        if noticia:
            # FIX 2: si Meta ya habia confirmado el post, nunca lo marcamos
            # como "fallida" (eso causaria una republicacion). Lo dejamos
            # como publicada_meta, aunque algo posterior (por ejemplo,
            # publicar en X) haya fallado.
            if bot.ultimo_meta_post_id:
                try:
                    actualizar_estado(
                        noticia["clave_historial"],
                        "publicada_meta",
                        meta_post_id=bot.ultimo_meta_post_id,
                    )
                except Exception:
                    logger.exception("No se pudo persistir publicada_meta tras el error")
            else:
                registrar_fallo(noticia["clave_historial"], str(exc))
        raise

if __name__ == "__main__":
    ejecutar_modo_centinela()
