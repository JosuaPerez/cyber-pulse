"""Entrada compatible: la implementación vive en app.reels, sin publicador."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "cyberpulse-bot"))

from app.reels.myth import build, main, render
from app.reels.settings import Settings, load_script

__all__ = ["Settings", "build", "load_script", "main", "render"]

if __name__ == "__main__":
    main()
