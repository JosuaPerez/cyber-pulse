from types import SimpleNamespace

import pytest

from app import bot_cyberpulse


def _datos_validos():
    return {
        "slide_1": {"title": "Titulo", "description": "Descripcion"},
        "slide_2": {"description": "Problema"},
        "slide_3": {"description": "Detalle"},
        "slide_4": {"description": "Impacto", "points": ["a", "b", "c"]},
        "slide_5": {"description": "Mitigacion", "points": ["a", "b", "c"]},
        "caption": "Caption",
        "hilo_x": [],
        "meta": {"cves": [], "severidad": "medium"},
    }


def test_nueva_noticia_no_hereda_meta_post_id_anterior(monkeypatch):
    bot = SimpleNamespace(
        ultimo_meta_post_id="post-anterior",
        analizar_noticia_con_ia=lambda noticia: _datos_validos(),
    )
    noticia = {
        "title": "Noticia nueva",
        "clave_historial": "noticia-nueva",
    }
    estados = []
    fallos = []

    monkeypatch.setattr(bot_cyberpulse, "obtener_noticia_nueva", lambda: noticia)
    monkeypatch.setattr(
        bot_cyberpulse,
        "actualizar_estado",
        lambda clave, estado, **campos: estados.append((clave, estado, campos)),
    )
    monkeypatch.setattr(
        bot_cyberpulse,
        "registrar_fallo",
        lambda clave, error: fallos.append((clave, error)),
    )
    monkeypatch.setattr(
        bot_cyberpulse,
        "generar_imagenes_carrusel",
        lambda datos: (_ for _ in ()).throw(RuntimeError("fallo de render")),
    )

    with pytest.raises(RuntimeError, match="fallo de render"):
        bot_cyberpulse.procesar_una_noticia(bot)

    assert bot.ultimo_meta_post_id is None
    assert fallos == [("noticia-nueva", "fallo de render")]
    assert all(estado != "publicada_meta" for _, estado, _ in estados)
