import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import config
from app.historial_db import actualizar_estado, registrar_deteccion


ARCHIVO_LEGACY = config.DATA_DIR / "historial_rss.txt"


def migrar() -> int:
    if not ARCHIVO_LEGACY.exists():
        print(f"No existe historial legacy: {ARCHIVO_LEGACY}")
        return 0

    migradas = 0
    for linea in ARCHIVO_LEGACY.read_text(encoding="utf-8").splitlines():
        clave = linea.strip()
        if not clave:
            continue
        registrar_deteccion(clave, clave)
        actualizar_estado(clave, "publicada_meta")
        migradas += 1

    print(f"Noticias migradas: {migradas}")
    return migradas


if __name__ == "__main__":
    migrar()
