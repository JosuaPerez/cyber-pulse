import feedparser
import logging

from app import config
from app.historial_db import registrar_deteccion, reservar_publicacion, ya_procesada
from app.http_seguro import DescargaFallida, DescargaRechazada, descargar_bytes

# Agregamos los sitios web más relevantes del sector
FUENTES_RSS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://www.darkreading.com/rss.xml",
    "https://www.securityweek.com/feed/"
]
HEADERS_RSS = {
    "User-Agent": "Mozilla/5.0 (compatible; CyberPulseBot/1.0)",
    "Accept": "application/rss+xml, application/xml;q=0.9, */*;q=0.1",
}

def obtener_noticia_nueva():
    """Escanea todos los sitios y devuelve la primera noticia que no esté en el historial."""
    for url in FUENTES_RSS:
        logging.info("Escaneando fuente RSS: %s", url)

        try:
            respuesta = descargar_bytes(
                url,
                timeout=config.HTTP_TIMEOUT,
                headers=HEADERS_RSS,
                max_bytes=config.RSS_MAX_BYTES,
                max_redirecciones=config.HTTP_MAX_REDIRECCIONES,
            )
            feed = feedparser.parse(respuesta.contenido)
        except (DescargaFallida, DescargaRechazada) as exc:
            logging.warning("No se pudo descargar el feed %s: %s", url, exc)
            continue
        
        if feed.bozo and not feed.entries:
            logging.warning("Feed RSS invalido y sin entradas: %s", url)
            continue

        if not feed.entries:
            logging.warning("Feed RSS sin entradas: %s", url)
            continue
            
        # Revisamos las 3 últimas noticias de cada portal
        for entrada in feed.entries[:3]:
            titulo = entrada.get("title", "").strip()
            clave_historial = str(
                entrada.get("id") or entrada.get("link") or titulo
            ).strip()

            if not titulo or not clave_historial:
                logging.warning("Entrada RSS sin titulo o identificador en %s", url)
                continue
            
            clave_legacy_migrada = titulo if titulo != clave_historial else None
            if clave_legacy_migrada and ya_procesada(clave_legacy_migrada):
                continue

            registrar_deteccion(clave_historial, titulo)
            if reservar_publicacion(clave_historial):
                logging.info("Noticia inédita encontrada: %s", titulo)
                return {
                    "title": titulo,
                    "summary": entrada.get("summary", ""),
                    "link": entrada.get("link", ""),
                    "clave_historial": clave_historial,
                }
                
    return None
