import json
import sqlite3
from pathlib import Path

from app import config

ESTADOS_VALIDOS = {
    "detectada",
    "analizada",
    "descartada",
    "renderizada",
    "publicada_meta",
    "fallida",
}
CAMPOS_ACTUALIZABLES = {
    "cves",
    "severidad",
    "ultimo_error",
    "meta_post_id",
}


def _ruta_db(db_path=None) -> Path:
    return Path(db_path) if db_path is not None else config.HISTORIAL_DB


def _conectar(db_path=None):
    ruta = _ruta_db(db_path)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(ruta)


def inicializar_db(db_path=None) -> None:
    with _conectar(db_path) as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS publicaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                clave_historial TEXT NOT NULL UNIQUE,
                titulo TEXT NOT NULL,
                cves TEXT NOT NULL DEFAULT '[]',
                severidad TEXT,
                estado TEXT NOT NULL CHECK (
                    estado IN (
                        'detectada', 'analizada', 'descartada',
                        'renderizada', 'publicada_meta', 'fallida'
                    )
                ),
                intentos INTEGER NOT NULL DEFAULT 0,
                ultimo_error TEXT,
                meta_post_id TEXT,
                creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                actualizado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def ya_procesada(clave_historial, db_path=None) -> bool:
    inicializar_db(db_path)
    with _conectar(db_path) as conexion:
        fila = conexion.execute(
            "SELECT 1 FROM publicaciones WHERE clave_historial = ? "
            "AND estado IN ('publicada_meta', 'descartada') LIMIT 1",
            (clave_historial,),
        ).fetchone()
    return fila is not None


def registrar_deteccion(clave_historial, titulo, db_path=None) -> None:
    inicializar_db(db_path)
    with _conectar(db_path) as conexion:
        conexion.execute(
            """
            INSERT INTO publicaciones (
                clave_historial, titulo, estado, creado_en, actualizado_en
            )
            VALUES (?, ?, 'detectada', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(clave_historial) DO NOTHING
            """,
            (clave_historial, titulo),
        )


def actualizar_estado(
    clave_historial,
    estado,
    db_path=None,
    incrementar_intentos=False,
    **campos,
) -> None:
    if estado not in ESTADOS_VALIDOS:
        raise ValueError(f"Estado de publicacion invalido: {estado}")

    desconocidos = set(campos) - CAMPOS_ACTUALIZABLES
    if desconocidos:
        nombres = ", ".join(sorted(desconocidos))
        raise ValueError(f"Campos no actualizables: {nombres}")

    valores = dict(campos)
    if "cves" in valores and not isinstance(valores["cves"], str):
        valores["cves"] = json.dumps(valores["cves"], ensure_ascii=False)

    asignaciones = ["estado = ?", "actualizado_en = CURRENT_TIMESTAMP"]
    parametros = [estado]
    for campo, valor in valores.items():
        asignaciones.append(f"{campo} = ?")
        parametros.append(valor)
    if incrementar_intentos:
        asignaciones.append("intentos = intentos + 1")

    parametros.append(clave_historial)
    with _conectar(db_path) as conexion:
        cursor = conexion.execute(
            f"UPDATE publicaciones SET {', '.join(asignaciones)} "
            "WHERE clave_historial = ?",
            parametros,
        )
        if cursor.rowcount == 0:
            raise KeyError(f"No existe la publicacion: {clave_historial}")
