import socket

import pytest
import requests

from app import http_seguro


HOSTS_PRUEBA = frozenset({"noticias.example"})


class RespuestaFalsa:
    def __init__(self, *, estado=200, headers=None, bloques=None):
        self.status_code = estado
        self.headers = headers or {}
        self._bloques = bloques or []
        self.cerrada = False

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size):
        del chunk_size
        yield from self._bloques

    def close(self):
        self.cerrada = True


def _dns_publico(*args, **kwargs):
    del args, kwargs
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 443))]


@pytest.mark.parametrize(
    "url",
    [
        "http://noticias.example/feed",
        "https://usuario:clave@noticias.example/feed",
        "https://noticias.example:8443/feed",
        "https://noticias.example.atacante.test/feed",
    ],
)
def test_validar_url_rechaza_destinos_no_permitidos(monkeypatch, url):
    monkeypatch.setattr(http_seguro.socket, "getaddrinfo", _dns_publico)

    with pytest.raises(http_seguro.DescargaRechazada):
        http_seguro.validar_url_publica(url, HOSTS_PRUEBA)


@pytest.mark.parametrize("direccion", ["127.0.0.1", "169.254.169.254", "::1"])
def test_validar_url_rechaza_resoluciones_no_publicas(monkeypatch, direccion):
    monkeypatch.setattr(
        http_seguro.socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", (direccion, 443))
        ],
    )

    with pytest.raises(http_seguro.DescargaRechazada, match="red no publica"):
        http_seguro.validar_url_publica(
            "https://noticias.example/feed",
            HOSTS_PRUEBA,
        )


def test_descarga_con_limite_y_sin_redirecciones_automaticas(monkeypatch):
    respuesta = RespuestaFalsa(
        headers={"Content-Type": "application/xml; charset=utf-8"},
        bloques=[b"<rss>", b"contenido", b"</rss>"],
    )
    argumentos = {}
    monkeypatch.setattr(http_seguro.socket, "getaddrinfo", _dns_publico)

    def get_falso(url, **kwargs):
        argumentos.update(url=url, **kwargs)
        return respuesta

    monkeypatch.setattr(http_seguro.requests, "get", get_falso)

    resultado = http_seguro.descargar_bytes(
        "https://noticias.example/feed",
        max_bytes=100,
        timeout=5,
        hosts_permitidos=HOSTS_PRUEBA,
    )

    assert resultado.contenido == b"<rss>contenido</rss>"
    assert resultado.url_final == "https://noticias.example/feed"
    assert argumentos["allow_redirects"] is False
    assert argumentos["stream"] is True
    assert respuesta.cerrada is True


def test_redireccion_se_valida_antes_de_seguirla(monkeypatch):
    respuesta = RespuestaFalsa(
        estado=302,
        headers={"Location": "http://169.254.169.254/latest/meta-data/"},
    )
    llamadas = []
    monkeypatch.setattr(http_seguro.socket, "getaddrinfo", _dns_publico)
    monkeypatch.setattr(
        http_seguro.requests,
        "get",
        lambda url, **kwargs: llamadas.append(url) or respuesta,
    )

    with pytest.raises(http_seguro.DescargaRechazada):
        http_seguro.descargar_bytes(
            "https://noticias.example/feed",
            max_bytes=100,
            timeout=5,
            hosts_permitidos=HOSTS_PRUEBA,
        )

    assert llamadas == ["https://noticias.example/feed"]
    assert respuesta.cerrada is True


def test_content_length_demasiado_grande_se_rechaza(monkeypatch):
    respuesta = RespuestaFalsa(headers={"Content-Length": "101"})
    monkeypatch.setattr(http_seguro.socket, "getaddrinfo", _dns_publico)
    monkeypatch.setattr(http_seguro.requests, "get", lambda *args, **kwargs: respuesta)

    with pytest.raises(http_seguro.DescargaRechazada, match="supera el limite"):
        http_seguro.descargar_bytes(
            "https://noticias.example/feed",
            max_bytes=100,
            timeout=5,
            hosts_permitidos=HOSTS_PRUEBA,
        )

    assert respuesta.cerrada is True


def test_tamano_real_demasiado_grande_se_rechaza(monkeypatch):
    respuesta = RespuestaFalsa(bloques=[b"a" * 60, b"b" * 41])
    monkeypatch.setattr(http_seguro.socket, "getaddrinfo", _dns_publico)
    monkeypatch.setattr(http_seguro.requests, "get", lambda *args, **kwargs: respuesta)

    with pytest.raises(http_seguro.DescargaRechazada, match="supera el limite"):
        http_seguro.descargar_bytes(
            "https://noticias.example/feed",
            max_bytes=100,
            timeout=5,
            hosts_permitidos=HOSTS_PRUEBA,
        )


def test_error_de_red_se_convierte_en_error_de_descarga(monkeypatch):
    monkeypatch.setattr(http_seguro.socket, "getaddrinfo", _dns_publico)

    def get_fallido(*args, **kwargs):
        raise requests.Timeout("timeout")

    monkeypatch.setattr(http_seguro.requests, "get", get_fallido)

    with pytest.raises(http_seguro.DescargaFallida):
        http_seguro.descargar_bytes(
            "https://noticias.example/feed",
            max_bytes=100,
            timeout=5,
            hosts_permitidos=HOSTS_PRUEBA,
        )
