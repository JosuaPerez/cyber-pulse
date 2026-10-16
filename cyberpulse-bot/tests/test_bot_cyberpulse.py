from types import SimpleNamespace

import pytest
import requests

from app import bot_cyberpulse
from app.bot_cyberpulse import CyberPulseBot, ResultadoPublicacion


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


class RespuestaMeta:
    def __init__(self, datos, status_code=200):
        self.datos = datos
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self.datos


class SesionMeta:
    def __init__(self, respuestas):
        self.respuestas = list(respuestas)
        self.posts = []
        self.headers = {}

    def post(self, url, data, timeout):
        self.posts.append({"url": url, "data": data, "timeout": timeout})
        respuesta = self.respuestas.pop(0)
        if isinstance(respuesta, Exception):
            raise respuesta
        return respuesta


def _bot_meta(sesion):
    bot = object.__new__(CyberPulseBot)
    bot.access_token = "token-secreto"
    bot.ig_user_id = "ig-user"
    bot.meta_base_url = "https://graph.facebook.com/v-test"
    bot.session = sesion
    bot.ultimo_meta_post_id = None
    return bot


def test_cliente_meta_usa_authorization_header(monkeypatch):
    sesion = SesionMeta([])
    monkeypatch.setattr(bot_cyberpulse.config, "validar_config_publicacion", lambda: None)
    monkeypatch.setattr(bot_cyberpulse.config, "META_ACCESS_TOKEN", "token-secreto")
    monkeypatch.setattr(bot_cyberpulse.config, "IG_USER_ID", "ig-user")
    monkeypatch.setattr(bot_cyberpulse.requests, "Session", lambda: sesion)
    monkeypatch.setattr(
        bot_cyberpulse.genai,
        "Client",
        lambda api_key: SimpleNamespace(api_key=api_key),
    )

    CyberPulseBot()

    assert sesion.headers == {"Authorization": "Bearer token-secreto"}


def test_item_de_carrusel_no_envia_token_en_payload():
    sesion = SesionMeta([RespuestaMeta({"id": "item-1"})])
    bot = _bot_meta(sesion)

    assert bot.crear_item_carrusel("https://cdn.test/slide.png") == "item-1"
    assert "access_token" not in sesion.posts[0]["data"]


def test_carrusel_exige_exactamente_cinco_imagenes(monkeypatch):
    bot = _bot_meta(SesionMeta([]))
    subidas = []
    monkeypatch.setattr(
        bot_cyberpulse,
        "subir_imagen_publica",
        lambda ruta: subidas.append(ruta),
    )

    resultado = bot.publicar_carrusel_local(
        ["slide-1.png", "slide-2.png"],
        "Caption",
        clave_historial="noticia-1",
    )

    assert resultado is ResultadoPublicacion.FALLIDA
    assert subidas == []


def test_timeout_de_media_publish_se_marca_como_ambiguo(monkeypatch):
    sesion = SesionMeta(
        [
            RespuestaMeta({"id": "creation-1"}),
            requests.ReadTimeout("respuesta perdida"),
        ]
    )
    bot = _bot_meta(sesion)
    ambiguas = []
    estados = []

    monkeypatch.setattr(bot_cyberpulse.time, "sleep", lambda segundos: None)
    monkeypatch.setattr(
        bot_cyberpulse,
        "subir_imagen_publica",
        lambda ruta: f"https://cdn.test/{ruta}",
    )
    monkeypatch.setattr(
        bot,
        "crear_item_carrusel",
        lambda url: f"item-{len(url)}-{url[-5:]}",
    )
    monkeypatch.setattr(bot, "esperar_contenedor_finalizado", lambda creation_id: True)
    monkeypatch.setattr(
        bot_cyberpulse,
        "actualizar_estado",
        lambda clave, estado, **campos: estados.append((clave, estado, campos)),
    )
    monkeypatch.setattr(
        bot_cyberpulse,
        "registrar_publicacion_ambigua",
        lambda clave, creation_id, error: ambiguas.append(
            (clave, creation_id, error)
        ),
    )

    resultado = bot.publicar_carrusel_local(
        [f"slide-{indice}.png" for indice in range(1, 6)],
        "Caption",
        clave_historial="noticia-ambigua",
    )

    assert resultado is ResultadoPublicacion.AMBIGUA
    assert estados == [
        (
            "noticia-ambigua",
            "renderizada",
            {
                "meta_creation_id": "creation-1",
                "meta_publicacion_pendiente": 1,
            },
        )
    ]
    assert ambiguas[0][:2] == ("noticia-ambigua", "creation-1")
    assert all("access_token" not in llamada["data"] for llamada in sesion.posts)


@pytest.mark.parametrize("cantidad", [4, 5])
def test_publicacion_confirmada_persiste_meta_post_id(monkeypatch, cantidad):
    sesion = SesionMeta(
        [
            RespuestaMeta({"id": "creation-ok"}),
            RespuestaMeta({"id": "post-ok"}),
        ]
    )
    bot = _bot_meta(sesion)
    estados = []

    monkeypatch.setattr(bot_cyberpulse.time, "sleep", lambda segundos: None)
    monkeypatch.setattr(
        bot_cyberpulse,
        "subir_imagen_publica",
        lambda ruta: f"https://cdn.test/{ruta}",
    )
    monkeypatch.setattr(
        bot,
        "crear_item_carrusel",
        lambda url: f"item-{url[-5:]}",
    )
    monkeypatch.setattr(bot, "esperar_contenedor_finalizado", lambda creation_id: True)
    monkeypatch.setattr(
        bot_cyberpulse,
        "actualizar_estado",
        lambda clave, estado, **campos: estados.append((clave, estado, campos)),
    )

    resultado = bot.publicar_carrusel_local(
        [f"slide-{indice}.png" for indice in range(1, cantidad + 1)],
        "Caption",
        clave_historial="noticia-ok",
        cantidad_esperada=cantidad,
    )

    assert resultado is ResultadoPublicacion.PUBLICADA
    assert bot.ultimo_meta_post_id == "post-ok"
    assert estados[-1] == (
        "noticia-ok",
        "publicada_meta",
        {"meta_post_id": "post-ok"},
    )
    assert all("access_token" not in llamada["data"] for llamada in sesion.posts)


@pytest.mark.parametrize("esperadas,recibidas", [(5, 4), (4, 3), (4, 5)])
def test_plan_de_imagenes_incompleto_no_sube_archivos(monkeypatch, esperadas, recibidas):
    bot = _bot_meta(SesionMeta([]))
    uploads = []
    monkeypatch.setattr(bot_cyberpulse, "subir_imagen_publica", lambda p: uploads.append(p))
    result = bot.publicar_carrusel_local([f"{i}.png" for i in range(recibidas)], "Texto",
                                       clave_historial="test", cantidad_esperada=esperadas)
    assert result is ResultadoPublicacion.FALLIDA
    assert uploads == []


def test_no_admite_una_cantidad_arbitraria_para_publicar():
    bot = _bot_meta(SesionMeta([]))
    with pytest.raises(ValueError, match="cantidad esperada"):
        bot.publicar_carrusel_local([], "Texto", clave_historial="test", cantidad_esperada=3)
