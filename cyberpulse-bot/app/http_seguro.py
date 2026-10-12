"""Descargas HTTP restringidas para fuentes editoriales conocidas."""

import ipaddress
import socket
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests


HOSTS_CYBERPULSE = frozenset(
    {
        "feeds.feedburner.com",
        "thehackernews.com",
        "bleepingcomputer.com",
        "krebsonsecurity.com",
        "darkreading.com",
        "securityweek.com",
    }
)
CODIGOS_REDIRECCION = {301, 302, 303, 307, 308}


class DescargaRechazada(ValueError):
    """La descarga incumple una restricción de seguridad."""


class DescargaFallida(RuntimeError):
    """La descarga falló por una respuesta HTTP o un problema de red."""


@dataclass(frozen=True)
class RespuestaSegura:
    contenido: bytes
    url_final: str
    encoding: str
    content_type: str

    @property
    def texto(self) -> str:
        return self.contenido.decode(self.encoding, errors="replace")


def _host_permitido(host: str, hosts_permitidos: frozenset[str]) -> bool:
    return any(host == base or host.endswith(f".{base}") for base in hosts_permitidos)


def validar_url_publica(
    url: str,
    hosts_permitidos: frozenset[str] = HOSTS_CYBERPULSE,
) -> None:
    """Valida esquema, autoridad, puerto y resolución DNS pública."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower().rstrip(".")

    if parsed.scheme.lower() != "https":
        raise DescargaRechazada("La URL debe usar HTTPS")
    if not host or not _host_permitido(host, hosts_permitidos):
        raise DescargaRechazada(f"Host no permitido: {host or '<vacio>'}")
    if parsed.username is not None or parsed.password is not None:
        raise DescargaRechazada("La URL no puede incluir credenciales")
    try:
        puerto = parsed.port
    except ValueError as exc:
        raise DescargaRechazada("Puerto invalido") from exc
    if puerto not in (None, 443):
        raise DescargaRechazada(f"Puerto no permitido: {puerto}")

    try:
        direcciones = {
            info[4][0]
            for info in socket.getaddrinfo(
                host,
                443,
                type=socket.SOCK_STREAM,
            )
        }
    except socket.gaierror as exc:
        raise DescargaRechazada(f"No se pudo resolver el host {host}") from exc

    if not direcciones:
        raise DescargaRechazada(f"El host {host} no tiene direcciones")
    for direccion in direcciones:
        try:
            ip = ipaddress.ip_address(direccion)
        except ValueError as exc:
            raise DescargaRechazada("DNS devolvio una direccion invalida") from exc
        if not ip.is_global:
            raise DescargaRechazada(
                f"El host {host} resolvio a una red no publica"
            )


def descargar_bytes(
    url: str,
    *,
    max_bytes: int,
    timeout: int,
    headers: dict[str, str] | None = None,
    hosts_permitidos: frozenset[str] = HOSTS_CYBERPULSE,
    max_redirecciones: int = 3,
) -> RespuestaSegura:
    """Descarga contenido limitado validando manualmente cada redirección."""
    if max_bytes <= 0:
        raise ValueError("max_bytes debe ser mayor que cero")
    if max_redirecciones < 0:
        raise ValueError("max_redirecciones no puede ser negativo")

    url_actual = url

    for salto in range(max_redirecciones + 1):
        validar_url_publica(url_actual, hosts_permitidos)
        try:
            respuesta = requests.get(
                url_actual,
                timeout=timeout,
                headers=headers,
                allow_redirects=False,
                stream=True,
            )
        except requests.RequestException as exc:
            raise DescargaFallida(f"No se pudo descargar {url_actual}") from exc
        try:
            if respuesta.status_code in CODIGOS_REDIRECCION:
                if salto >= max_redirecciones:
                    raise DescargaRechazada("Demasiadas redirecciones")
                destino = respuesta.headers.get("Location")
                if not destino:
                    raise DescargaRechazada("Redireccion sin destino")
                url_actual = urljoin(url_actual, destino)
                continue

            try:
                respuesta.raise_for_status()
            except requests.RequestException as exc:
                raise DescargaFallida(
                    f"Respuesta HTTP no valida desde {url_actual}"
                ) from exc
            content_length = respuesta.headers.get("Content-Length")
            if content_length:
                try:
                    bytes_declarados = int(content_length)
                except ValueError:
                    bytes_declarados = None
                if bytes_declarados is not None and bytes_declarados > max_bytes:
                    raise DescargaRechazada(
                        f"La respuesta supera el limite de {max_bytes} bytes"
                    )

            bloques = []
            total = 0
            for bloque in respuesta.iter_content(chunk_size=64 * 1024):
                if not bloque:
                    continue
                total += len(bloque)
                if total > max_bytes:
                    raise DescargaRechazada(
                        f"La respuesta supera el limite de {max_bytes} bytes"
                    )
                bloques.append(bloque)

            content_type = respuesta.headers.get("Content-Type", "")
            encoding = requests.utils.get_encoding_from_headers(respuesta.headers)
            return RespuestaSegura(
                contenido=b"".join(bloques),
                url_final=url_actual,
                encoding=encoding or "utf-8",
                content_type=content_type,
            )
        finally:
            respuesta.close()

    raise DescargaRechazada("Demasiadas redirecciones")
