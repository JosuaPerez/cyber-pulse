import json

from app.historial_db import (
    actualizar_estado,
    inicializar_db,
    marcar_tema_usado,
    registrar_deteccion,
    tema_ya_usado,
    ya_procesada,
)


def test_insercion_nueva(tmp_path):
    db_path = tmp_path / "historial.sqlite3"

    inicializar_db(db_path)
    registrar_deteccion("https://example.test/noticia", "Noticia de prueba", db_path)

    assert not ya_procesada("https://example.test/noticia", db_path)


def test_registrar_deteccion_es_idempotente(tmp_path):
    db_path = tmp_path / "historial.sqlite3"
    clave = "https://example.test/repetida"

    registrar_deteccion(clave, "Primera version", db_path)
    registrar_deteccion(clave, "Segunda version", db_path)

    import sqlite3

    with sqlite3.connect(db_path) as conexion:
        filas = conexion.execute(
            "SELECT titulo, estado FROM publicaciones WHERE clave_historial = ?",
            (clave,),
        ).fetchall()

    assert filas == [("Primera version", "detectada")]


def test_estados_terminales_y_fallida_reintentable(tmp_path):
    db_path = tmp_path / "historial.sqlite3"
    clave = "noticia-1"

    registrar_deteccion(clave, "Noticia", db_path)
    actualizar_estado(clave, "publicada_meta", db_path)
    assert ya_procesada(clave, db_path)

    otra_clave = "noticia-2"
    registrar_deteccion(otra_clave, "Otra noticia", db_path)
    actualizar_estado(otra_clave, "descartada", db_path)
    assert ya_procesada(otra_clave, db_path)

    reintentable = "noticia-3"
    registrar_deteccion(reintentable, "Reintentable", db_path)
    actualizar_estado(
        reintentable,
        "fallida",
        db_path,
        ultimo_error="Error temporal",
        incrementar_intentos=True,
    )
    assert not ya_procesada(reintentable, db_path)


def test_actualizar_estado_incrementa_intentos_y_serializa_cves(tmp_path):
    db_path = tmp_path / "historial.sqlite3"
    clave = "noticia-4"

    registrar_deteccion(clave, "Noticia", db_path)
    actualizar_estado(
        clave,
        "analizada",
        db_path,
        cves=["CVE-2026-12345"],
        severidad="high",
    )
    actualizar_estado(
        clave,
        "fallida",
        db_path,
        ultimo_error="Fallo de render",
        incrementar_intentos=True,
    )
    actualizar_estado(
        clave,
        "fallida",
        db_path,
        ultimo_error="Fallo de red",
        incrementar_intentos=True,
    )

    import sqlite3

    with sqlite3.connect(db_path) as conexion:
        fila = conexion.execute(
            "SELECT cves, severidad, estado, intentos, ultimo_error "
            "FROM publicaciones WHERE clave_historial = ?",
            (clave,),
        ).fetchone()

    assert json.loads(fila[0]) == ["CVE-2026-12345"]
    assert fila[1:] == ("high", "fallida", 2, "Fallo de red")


def test_tracking_de_temas_educativos_es_persistente_e_idempotente(tmp_path):
    db_path = tmp_path / "historial.sqlite3"

    assert not tema_ya_usado("tema-1", db_path)
    marcar_tema_usado("tema-1", db_path)
    marcar_tema_usado("tema-1", db_path)

    assert tema_ya_usado("tema-1", db_path)
    assert not tema_ya_usado("tema-2", db_path)

    import sqlite3

    with sqlite3.connect(db_path) as conexion:
        filas = conexion.execute(
            "SELECT tema_id FROM temas_educativos_usados"
        ).fetchall()

    assert filas == [("tema-1",)]
