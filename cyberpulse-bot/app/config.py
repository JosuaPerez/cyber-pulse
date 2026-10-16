import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default

    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise RuntimeError(
        f"La variable {name} debe ser booleana (true/false), no {value!r}."
    )


def _get_positive_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        parsed = int(value)
    except ValueError as exc:
        raise RuntimeError(f"La variable {name} debe ser un entero positivo.") from exc

    if parsed <= 0:
        raise RuntimeError(f"La variable {name} debe ser un entero positivo.")
    return parsed


TEMPLATES_BASE_URL = os.getenv("TEMPLATES_BASE_URL", "http://localhost:5173").rstrip("/")
META_GRAPH_VERSION = os.getenv("META_GRAPH_VERSION", "v23.0")
META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
R2_PUBLIC_BASE_URL = os.getenv("R2_PUBLIC_BASE_URL", "").rstrip("/")
_R2_ACCOUNT_ID_HOST = (R2_ACCOUNT_ID or "").removeprefix("https://").removeprefix("http://")
_R2_ACCOUNT_ID_HOST = _R2_ACCOUNT_ID_HOST.split(".r2.", 1)[0]
R2_ENDPOINT_URL = f"https://{_R2_ACCOUNT_ID_HOST}.r2.cloudflarestorage.com"

DRY_RUN = _get_bool("DRY_RUN", True)
PUBLICAR_EN_X = _get_bool("PUBLICAR_EN_X", False)


def _get_alert_variant() -> str:
    value = os.getenv("ALERTAS_VARIANTE", "clasica").strip().lower()
    if value not in {"clasica", "clara", "editorial"}:
        raise RuntimeError("ALERTAS_VARIANTE debe ser clasica, clara (opción A) o editorial.")
    return value


ALERTAS_VARIANTE = _get_alert_variant()

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
MEDIA_DIR = Path(os.getenv("MEDIA_DIR", "media"))
IMAGENES_DIR = MEDIA_DIR / "imagenes"
HISTORIAL_DB = Path(os.getenv("HISTORIAL_DB", str(DATA_DIR / "cyberpulse.sqlite3")))
DATA_DIR.mkdir(parents=True, exist_ok=True)
IMAGENES_DIR.mkdir(parents=True, exist_ok=True)
HISTORIAL_DB.parent.mkdir(parents=True, exist_ok=True)

HTTP_TIMEOUT = _get_positive_int("HTTP_TIMEOUT", 15)
RSS_MAX_BYTES = _get_positive_int("RSS_MAX_BYTES", 2_000_000)
ARTICULO_MAX_BYTES = _get_positive_int("ARTICULO_MAX_BYTES", 5_000_000)
HTTP_MAX_REDIRECCIONES = _get_positive_int("HTTP_MAX_REDIRECCIONES", 3)
META_POLL_INTERVAL = _get_positive_int("META_POLL_INTERVAL", 3)
META_POLL_TIMEOUT = _get_positive_int("META_POLL_TIMEOUT", 90)
INTERVALO_CICLO_SEGUNDOS = _get_positive_int("INTERVALO_CICLO_SEGUNDOS", 900)
MAX_INTENTOS_PUBLICACION = _get_positive_int("MAX_INTENTOS_PUBLICACION", 3)
REINTENTO_BASE_SEGUNDOS = _get_positive_int("REINTENTO_BASE_SEGUNDOS", 300)
RESERVA_PUBLICACION_SEGUNDOS = _get_positive_int(
    "RESERVA_PUBLICACION_SEGUNDOS", 1800
)


def validar_config_publicacion() -> None:
    """Valida las credenciales necesarias para el modo de ejecucion seleccionado."""
    if not GEMINI_API_KEY:
        raise RuntimeError("Falta la variable obligatoria GEMINI_API_KEY.")

    if not DRY_RUN:
        missing = [
            name
            for name, value in {
                "META_ACCESS_TOKEN": META_ACCESS_TOKEN,
                "IG_USER_ID": IG_USER_ID,
                "R2_ACCOUNT_ID": R2_ACCOUNT_ID,
                "R2_ACCESS_KEY_ID": R2_ACCESS_KEY_ID,
                "R2_SECRET_ACCESS_KEY": R2_SECRET_ACCESS_KEY,
                "R2_BUCKET_NAME": R2_BUCKET_NAME,
                "R2_PUBLIC_BASE_URL": R2_PUBLIC_BASE_URL,
            }.items()
            if not value
        ]
        if missing:
            variables = ", ".join(missing)
            raise RuntimeError(
                f"Faltan credenciales de publicacion con DRY_RUN=false: {variables}."
            )
