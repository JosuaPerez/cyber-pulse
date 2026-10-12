from types import SimpleNamespace

from app import lector_rss


class RespuestaFalsa:
    content = b"feed"

    def raise_for_status(self):
        return None


def test_selector_salta_noticia_no_elegible_y_continua(monkeypatch):
    entradas = [
        {
            "id": "noticia-en-backoff",
            "title": "Noticia temporalmente bloqueada",
            "summary": "Resumen 1",
            "link": "https://example.test/1",
        },
        {
            "id": "noticia-disponible",
            "title": "Noticia disponible",
            "summary": "Resumen 2",
            "link": "https://example.test/2",
        },
    ]
    registradas = []

    monkeypatch.setattr(lector_rss, "FUENTES_RSS", ["https://feed.example.test"])
    monkeypatch.setattr(
        lector_rss.requests,
        "get",
        lambda *args, **kwargs: RespuestaFalsa(),
    )
    monkeypatch.setattr(
        lector_rss.feedparser,
        "parse",
        lambda contenido: SimpleNamespace(bozo=False, entries=entradas),
    )
    monkeypatch.setattr(lector_rss, "ya_procesada", lambda clave: False)
    monkeypatch.setattr(
        lector_rss,
        "registrar_deteccion",
        lambda clave, titulo: registradas.append((clave, titulo)),
    )
    monkeypatch.setattr(
        lector_rss,
        "reservar_publicacion",
        lambda clave: clave == "noticia-disponible",
    )

    noticia = lector_rss.obtener_noticia_nueva()

    assert noticia["clave_historial"] == "noticia-disponible"
    assert [clave for clave, _ in registradas] == [
        "noticia-en-backoff",
        "noticia-disponible",
    ]


def test_selector_ignora_entradas_sin_identidad(monkeypatch):
    monkeypatch.setattr(lector_rss, "FUENTES_RSS", ["https://feed.example.test"])
    monkeypatch.setattr(
        lector_rss.requests,
        "get",
        lambda *args, **kwargs: RespuestaFalsa(),
    )
    monkeypatch.setattr(
        lector_rss.feedparser,
        "parse",
        lambda contenido: SimpleNamespace(
            bozo=False,
            entries=[{"title": "", "summary": "sin identidad"}],
        ),
    )

    assert lector_rss.obtener_noticia_nueva() is None
