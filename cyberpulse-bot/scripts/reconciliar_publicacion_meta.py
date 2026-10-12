"""Gestiona publicaciones cuyo resultado de media_publish quedó ambiguo."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.historial_db import (
    confirmar_publicacion_meta,
    listar_publicaciones_ambiguas,
    reanudar_publicacion,
)


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reconcilia manualmente publicaciones ambiguas de Meta."
    )
    subparsers = parser.add_subparsers(dest="comando", required=True)

    subparsers.add_parser("listar", help="Lista publicaciones pendientes")

    confirmar = subparsers.add_parser(
        "confirmar",
        help="Marca como publicada una entrada comprobada en Instagram",
    )
    confirmar.add_argument("clave_historial")
    confirmar.add_argument("meta_post_id")

    reintentar = subparsers.add_parser(
        "reintentar",
        help="Devuelve a la cola una entrada comprobada como no publicada",
    )
    reintentar.add_argument("clave_historial")
    reintentar.add_argument(
        "--confirmo-no-publicada",
        action="store_true",
        help="Confirma que se verificó Instagram antes de reintentar",
    )
    return parser


def main() -> None:
    parser = construir_parser()
    args = parser.parse_args()

    if args.comando == "listar":
        pendientes = listar_publicaciones_ambiguas()
        if not pendientes:
            print("No hay publicaciones ambiguas pendientes.")
            return
        for pendiente in pendientes:
            print(
                f"clave={pendiente['clave_historial']} | "
                f"creation_id={pendiente['meta_creation_id']} | "
                f"actualizada={pendiente['actualizado_en']} | "
                f"titulo={pendiente['titulo']}"
            )
        return

    if args.comando == "confirmar":
        confirmar_publicacion_meta(args.clave_historial, args.meta_post_id)
        print("Publicación confirmada y cerrada en el historial.")
        return

    if not args.confirmo_no_publicada:
        parser.error(
            "reintentar requiere --confirmo-no-publicada después de revisar Instagram"
        )
    reanudar_publicacion(args.clave_historial)
    print("Publicación devuelta a la cola.")


if __name__ == "__main__":
    main()
