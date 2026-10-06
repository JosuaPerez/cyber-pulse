import feedparser
import logging

import requests

from app import config
from app.historial_db import registrar_deteccion, ya_procesada

# Agregamos los sitios web más relevantes del sector
FUENTES_RSS = [
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/",
    "https://www.darkreading.com/rss.xml",
    "https://www.securityweek.com/feed/"
]

def obtener_noticia_nueva():
    """Escanea todos los sitios y devuelve la primera noticia que no esté en el historial."""
    for url in FUENTES_RSS:
        logging.info("Escaneando fuente RSS: %s", url)

        try:
            respuesta = requests.get(
                url,
                timeout=config.HTTP_TIMEOUT,
                headers={"User-Agent": "CyberPulseBot/1.0"},
            )
            respuesta.raise_for_status()
            feed = feedparser.parse(respuesta.content)
        except requests.RequestException as exc:
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
            
            clave_legacy_migrada = titulo if titulo != clave_historial else None
            if not ya_procesada(clave_historial) and (
                not clave_legacy_migrada or not ya_procesada(clave_legacy_migrada)
            ):
                registrar_deteccion(clave_historial, titulo)
                logging.info("Noticia inédita encontrada: %s", titulo)
                return {
                    "title": titulo,
                    "summary": entrada.get("summary", ""),
                    "link": entrada.get("link", ""),
                    "clave_historial": clave_historial,
                }
                
    return None