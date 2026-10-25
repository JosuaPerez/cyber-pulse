"""Verifica un MP4 existente sin renderizar ni llamar a proveedores."""

import argparse
import json
import logging
from pathlib import Path

from .render import verify_video
from .settings import Settings


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("--duration", type=float, default=19)
    parser.add_argument("--audio", choices=["none", "voice", "music"], default="none")
    parser.add_argument("--fps", type=int, choices=[24, 30], default=24)
    args = parser.parse_args()
    try:
        report = verify_video(args.video, Settings(fps=args.fps),
                              expected_duration=args.duration, has_audio=args.audio != "none")
        print(json.dumps(report, indent=2))
    except Exception:
        logging.error("MP4 no aprobado por la verificación técnica")
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
