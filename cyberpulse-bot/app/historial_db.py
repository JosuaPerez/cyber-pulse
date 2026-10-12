import json
import sqlite3
from datetime import datetime, timedelta, timezone
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
    "meta_creation_id",
    "meta_post_id",
    "meta_publicacion_pendiente",
}

ESTADOS_TERMINALES = {"publicada_meta", "descartada"}


def _ruta_db(db_path=None) -> Path:
    return Path(db_path) if db_path is not None else config.HISTORIAL_DB


def _conectar(db_path=None):
    ruta = _ruta_db(db_path)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(ruta, timeout=5)
    conexion.execute("PRAGMA busy_timeout = 5000")
    return conexion


def _timestamp_sql(valor: datetime) -> str:
    """Normaliza fechas UTC al formato comparable con CURRENT_TIMESTAMP de SQLite."""
    return valor.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def inicializar_db(db_path=None) -> None:
    with _conectar(db_path) as conexion:
        conexion.execute("BEGIN IMMEDIATE")
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
        columnas = {
            fila[1] for fila in conexion.execute("PRAGMA table_info(publicaciones)")
        }
        migraciones = {
            "proximo_reintento_en": (
                "ALTER TABLE publicaciones ADD COLUMN proximo_reintento_en TIMESTAMP"
            ),
            "reserva_hasta": "ALTER TABLE publicaciones ADD COLUMN reserva_hasta TIMESTAMP",
            "requiere_revision": (
                "ALTER TABLE publicaciones ADD COLUMN "
                "requiere_revision INTEGER NOT NULL DEFAULT 0 "
                "CHECK (requiere_revision IN (0, 1))"
            ),
            "meta_creation_id": (
                "ALTER TABLE publicaciones ADD COLUMN meta_creation_id TEXT"
            ),
            "meta_publicacion_pendiente": (
                "ALTER TABLE publicaciones ADD COLUMN "
                "meta_publicacion_pendiente INTEGER NOT NULL DEFAULT 0 "
                "CHECK (meta_publicacion_pendiente IN (0, 1))"
            ),
        }
        for columna, sentencia in migraciones.items():
            if columna not in columnas:
                conexion.execute(sentencia)

        # Bases creadas por versiones anteriores pueden contener fallos que ya
        # agotaron el límite, pero todavía no tienen la marca de revisión.
        conexion.execute(
            """
            UPDATE publicaciones
            SET requiere_revision = 1
            WHERE estado = 'fallida' AND intentos >= ?
            """,
            (config.MAX_INTENTOS_PUBLICACION,),
        )

        conexion.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_publicaciones_disponibles
            ON publicaciones (
                estado, requiere_revision, intentos,
                proximo_reintento_en, reserva_hasta
            )
            """
        )
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS temas_educativos_usados (
                tema_id TEXT PRIMARY KEY,
                usado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def ya_procesada(clave_historial, db_path=None) -> bool:
    inicializar_db(db_path)
    with _conectar(db_path) as conexion:
        fila = conexion.execute(
            "SELECT 1 FROM publicaciones WHERE clave_historial = ? "
            "AND (estado IN ('publicada_meta', 'descartada') "
            "OR requiere_revision = 1) LIMIT 1",
            (clave_historial,),
        ).fetchone()
    return fila is not None


def reservar_publicacion(
    clave_historial,
    db_path=None,
    *,
    max_intentos=None,
    reserva_segundos=None,
    ahora=None,
) -> bool:
    """Reserva atómicamente una noticia elegible y evita trabajo duplicado."""
    inicializar_db(db_path)
    max_intentos = max_intentos or config.MAX_INTENTOS_PUBLICACION
    reserva_segundos = reserva_segundos or config.RESERVA_PUBLICACION_SEGUNDOS
    ahora = ahora or datetime.now(timezone.utc)
    reserva_hasta = ahora + timedelta(seconds=reserva_segundos)

    with _conectar(db_path) as conexion:
        cursor = conexion.execute(
            """
            UPDATE publicaciones
            SET reserva_hasta = ?, actualizado_en = CURRENT_TIMESTAMP
            WHERE clave_historial = ?
              AND estado IN ('detectada', 'fallida', 'analizada', 'renderizada')
              AND requiere_revision = 0
              AND intentos < ?
              AND (proximo_reintento_en IS NULL OR proximo_reintento_en <= ?)
              AND (reserva_hasta IS NULL OR reserva_hasta <= ?)
            """,
            (
                _timestamp_sql(reserva_hasta),
                clave_historial,
                max_intentos,
                _timestamp_sql(ahora),
                _timestamp_sql(ahora),
            ),
        )
    return cursor.rowcount == 1


def registrar_fallo(
    clave_historial,
    error,
    db_path=None,
    *,
    max_intentos=None,
    espera_base_segundos=None,
    ahora=None,
) -> bool:
    """Registra un fallo y devuelve True cuando requiere revisión manual."""
    inicializar_db(db_path)
    max_intentos = max_intentos or config.MAX_INTENTOS_PUBLICACION
    espera_base_segundos = espera_base_segundos or config.REINTENTO_BASE_SEGUNDOS
    ahora = ahora or datetime.now(timezone.utc)

    with _conectar(db_path) as conexion:
        conexion.execute("BEGIN IMMEDIATE")
        fila = conexion.execute(
            "SELECT intentos FROM publicaciones WHERE clave_historial = ?",
            (clave_historial,),
        ).fetchone()
        if fila is None:
            raise KeyError(f"No existe la publicacion: {clave_historial}")

        intentos = fila[0] + 1
        requiere_revision = intentos >= max_intentos
        proximo_reintento = None
        if not requiere_revision:
            demora = espera_base_segundos * (2 ** (intentos - 1))
            proximo_reintento = _timestamp_sql(
                ahora + timedelta(seconds=demora)
            )

        conexion.execute(
            """
            UPDATE publicaciones
            SET estado = 'fallida',
                intentos = ?,
                ultimo_error = ?,
                proximo_reintento_en = ?,
                reserva_hasta = NULL,
                requiere_revision = ?,
                actualizado_en = CURRENT_TIMESTAMP
            WHERE clave_historial = ?
            """,
            (
                intentos,
                str(error),
                proximo_reintento,
                int(requiere_revision),
                clave_historial,
            ),
        )
    return requiere_revision


def marcar_revision_manual(clave_historial, db_path=None) -> None:
    """Evita republicar contenido generado que espera una decisión humana."""
    inicializar_db(db_path)
    with _conectar(db_path) as conexion:
        cursor = conexion.execute(
            """
            UPDATE publicaciones
            SET requiere_revision = 1,
                reserva_hasta = NULL,
                actualizado_en = CURRENT_TIMESTAMP
            WHERE clave_historial = ?
            """,
            (clave_historial,),
        )
        if cursor.rowcount == 0:
            raise KeyError(f"No existe la publicacion: {clave_historial}")


def registrar_publicacion_ambigua(
    clave_historial,
    creation_id,
    error,
    db_path=None,
) -> None:
    """Bloquea reintentos cuando Meta pudo publicar pero no confirmó respuesta."""
    inicializar_db(db_path)
    with _conectar(db_path) as conexion:
        cursor = conexion.execute(
            """
            UPDATE publicaciones
            SET meta_creation_id = ?,
                meta_publicacion_pendiente = 1,
                ultimo_error = ?,
                requiere_revision = 1,
                reserva_hasta = NULL,
                actualizado_en = CURRENT_TIMESTAMP
            WHERE clave_historial = ?
            """,
            (creation_id, str(error), clave_historial),
        )
        if cursor.rowcount == 0:
            raise KeyError(f"No existe la publicacion: {clave_historial}")


def reanudar_publicacion(clave_historial, db_path=None) -> None:
    """Devuelve manualmente una publicación a la cola desde cero."""
    inicializar_db(db_path)
    with _conectar(db_path) as conexion:
        cursor = conexion.execute(
            """
            UPDATE publicaciones
            SET estado = 'detectada',
                intentos = 0,
                ultimo_error = NULL,
                meta_creation_id = NULL,
                meta_publicacion_pendiente = 0,
                proximo_reintento_en = NULL,
                reserva_hasta = NULL,
                requiere_revision = 0,
                actualizado_en = CURRENT_TIMESTAMP
            WHERE clave_historial = ?
            """,
            (clave_historial,),
        )
        if cursor.rowcount == 0:
            raise KeyError(f"No existe la publicacion: {clave_historial}")


def listar_publicaciones_ambiguas(db_path=None) -> list[dict]:
    """Devuelve publicaciones que necesitan reconciliación manual con Meta."""
    inicializar_db(db_path)
    with _conectar(db_path) as conexion:
        conexion.row_factory = sqlite3.Row
        filas = conexion.execute(
            """
            SELECT clave_historial, titulo, meta_creation_id,
                   ultimo_error, actualizado_en
            FROM publicaciones
            WHERE meta_publicacion_pendiente = 1
            ORDER BY actualizado_en
            """
        ).fetchall()
    return [dict(fila) for fila in filas]


def confirmar_publicacion_meta(
    clave_historial,
    meta_post_id,
    db_path=None,
) -> None:
    """Registra el post encontrado manualmente en Instagram como publicado."""
    actualizar_estado(
        clave_historial,
        "publicada_meta",
        db_path,
        meta_post_id=meta_post_id,
    )


def tema_ya_usado(tema_id, db_path=None) -> bool:
    inicializar_db(db_path)
    with _conectar(db_path) as conexion:
        fila = conexion.execute(
            "SELECT 1 FROM temas_educativos_usados WHERE tema_id = ? LIMIT 1",
            (tema_id,),
        ).fetchone()
    return fila is not None


def marcar_tema_usado(tema_id, db_path=None) -> None:
    inicializar_db(db_path)
    with _conectar(db_path) as conexion:
        conexion.execute(
            """
            INSERT INTO temas_educativos_usados (tema_id)
            VALUES (?)
            ON CONFLICT(tema_id) DO NOTHING
            """,
            (tema_id,),
        )


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
    if estado in ESTADOS_TERMINALES:
        asignaciones.extend(
            [
                "reserva_hasta = NULL",
                "proximo_reintento_en = NULL",
            ]
        )
    if estado == "publicada_meta":
        asignaciones.extend(
            [
                "meta_publicacion_pendiente = 0",
                "requiere_revision = 0",
            ]
        )

    parametros.append(clave_historial)
    with _conectar(db_path) as conexion:
        cursor = conexion.execute(
            f"UPDATE publicaciones SET {', '.join(asignaciones)} "
            "WHERE clave_historial = ?",
            parametros,
        )
        if cursor.rowcount == 0:
            raise KeyError(f"No existe la publicacion: {clave_historial}")
