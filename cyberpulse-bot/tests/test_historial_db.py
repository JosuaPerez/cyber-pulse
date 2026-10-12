import json
from datetime import datetime, timedelta, timezone

from app.historial_db import (
    actualizar_estado,
    inicializar_db,
    marcar_tema_usado,
    marcar_revision_manual,
    registrar_deteccion,
    registrar_fallo,
    reanudar_publicacion,
    reservar_publicacion,
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


def test_inicializacion_migra_base_existente_sin_perder_datos(tmp_path):
    import sqlite3

    db_path = tmp_path / "historial.sqlite3"
    with sqlite3.connect(db_path) as conexion:
        conexion.execute(
            """
            CREATE TABLE publicaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clave_historial TEXT NOT NULL UNIQUE,
                titulo TEXT NOT NULL,
                cves TEXT NOT NULL DEFAULT '[]',
                severidad TEXT,
                estado TEXT NOT NULL,
                intentos INTEGER NOT NULL DEFAULT 0,
                ultimo_error TEXT,
                meta_post_id TEXT,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conexion.execute(
            "INSERT INTO publicaciones (clave_historial, titulo, estado) "
            "VALUES ('legacy-1', 'Noticia existente', 'detectada')"
        )

    inicializar_db(db_path)

    with sqlite3.connect(db_path) as conexion:
        columnas = {
            fila[1] for fila in conexion.execute("PRAGMA table_info(publicaciones)")
        }
        fila = conexion.execute(
            "SELECT titulo, estado FROM publicaciones WHERE clave_historial = 'legacy-1'"
        ).fetchone()

    assert {"proximo_reintento_en", "reserva_hasta", "requiere_revision"} <= columnas
    assert fila == ("Noticia existente", "detectada")


def test_reserva_atomica_impide_procesamiento_duplicado(tmp_path):
    db_path = tmp_path / "historial.sqlite3"
    ahora = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)
    registrar_deteccion("noticia-reservada", "Noticia", db_path)

    assert reservar_publicacion(
        "noticia-reservada", db_path, ahora=ahora, reserva_segundos=60
    )
    assert not reservar_publicacion(
        "noticia-reservada", db_path, ahora=ahora, reserva_segundos=60
    )
    assert reservar_publicacion(
        "noticia-reservada",
        db_path,
        ahora=ahora + timedelta(seconds=61),
        reserva_segundos=60,
    )


def test_fallo_aplica_backoff_y_termina_en_revision_manual(tmp_path):
    db_path = tmp_path / "historial.sqlite3"
    ahora = datetime(2026, 10, 12, 12, 0, tzinfo=timezone.utc)
    clave = "noticia-reintentable"
    registrar_deteccion(clave, "Noticia", db_path)
    reservar_publicacion(clave, db_path, ahora=ahora, reserva_segundos=60)

    requiere_revision = registrar_fallo(
        clave,
        "Gemini no respondio",
        db_path,
        max_intentos=2,
        espera_base_segundos=60,
        ahora=ahora,
    )

    assert not requiere_revision
    assert not reservar_publicacion(
        clave,
        db_path,
        max_intentos=2,
        ahora=ahora + timedelta(seconds=59),
    )
    assert reservar_publicacion(
        clave,
        db_path,
        max_intentos=2,
        ahora=ahora + timedelta(seconds=61),
    )

    requiere_revision = registrar_fallo(
        clave,
        "Segundo fallo",
        db_path,
        max_intentos=2,
        espera_base_segundos=60,
        ahora=ahora + timedelta(seconds=61),
    )

    assert requiere_revision
    assert ya_procesada(clave, db_path)
    assert not reservar_publicacion(
        clave,
        db_path,
        max_intentos=2,
        ahora=ahora + timedelta(days=1),
    )


def test_revision_manual_es_terminal_para_el_selector(tmp_path):
    db_path = tmp_path / "historial.sqlite3"
    clave = "post-pendiente"
    registrar_deteccion(clave, "Post pendiente", db_path)
    marcar_revision_manual(clave, db_path)

    assert ya_procesada(clave, db_path)
    assert not reservar_publicacion(clave, db_path)

    reanudar_publicacion(clave, db_path)

    assert not ya_procesada(clave, db_path)
    assert reservar_publicacion(clave, db_path)
