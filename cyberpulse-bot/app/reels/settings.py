"""Configuración compartida por plantilla, audio y exportador."""

import json
import logging
import math
import os
from dataclasses import dataclass
from pathlib import Path

LOGGER = logging.getLogger(__name__)
ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "content/reels/phishing-myth.json"
WIDTH, HEIGHT = 1080, 1920
SAFE_TOP, SAFE_BOTTOM = .14, .25


@dataclass(frozen=True)
class Settings:
    fps: int = 24
    bitrate_mbps: float = 5
    safe_top: float = SAFE_TOP
    safe_bottom: float = SAFE_BOTTOM
    draft_label: bool = False
    audio: str = "none"
    music_path: Path | None = None
    music_volume: float = .12
    voice: str = "es-DO-EmilioNeural"

    def __post_init__(self):
        if self.fps not in (24, 30):
            raise ValueError("REEL_FPS debe ser 24 o 30")
        if not math.isfinite(self.bitrate_mbps) or self.bitrate_mbps < 4:
            raise ValueError("REEL_VIDEO_MBPS debe ser al menos 4")
        if not (SAFE_TOP <= self.safe_top <= .25 and SAFE_BOTTOM <= self.safe_bottom <= .35):
            raise ValueError("Zonas seguras: superior 14–25 %, inferior 25–35 %")
        if self.audio not in ("none", "voice", "music"):
            raise ValueError("REEL_AUDIO debe ser none, voice o music")
        if not 0 <= self.music_volume <= .3:
            raise ValueError("REEL_MUSIC_VOLUME debe estar entre 0 y 0.3")
        if self.audio == "music" and not (self.music_path and self.music_path.is_file()):
            raise ValueError("REEL_MUSIC_PATH debe señalar un archivo local existente")

    @classmethod
    def from_env(cls):
        try:
            draft = os.getenv("REEL_DRAFT_LABEL", "false").lower()
            if draft not in ("true", "false"):
                raise ValueError("REEL_DRAFT_LABEL debe ser true o false")
            music = os.getenv("REEL_MUSIC_PATH")
            return cls(
                fps=int(os.getenv("REEL_FPS", "24")),
                bitrate_mbps=float(os.getenv("REEL_VIDEO_MBPS", "5")),
                safe_top=float(os.getenv("REEL_SAFE_TOP", str(SAFE_TOP))),
                safe_bottom=float(os.getenv("REEL_SAFE_BOTTOM", str(SAFE_BOTTOM))),
                draft_label=draft == "true", audio=os.getenv("REEL_AUDIO", "none"),
                music_path=Path(music).expanduser() if music else None,
                music_volume=float(os.getenv("REEL_MUSIC_VOLUME", ".12")),
                voice=os.getenv("REEL_VOICE", "es-DO-EmilioNeural"),
            )
        except (ValueError, OSError):
            LOGGER.error("Configuración del reel inválida; no se generará una salida parcial")
            raise

    def layout(self):
        return {"width": WIDTH, "height": HEIGHT,
                "top": math.ceil(HEIGHT * self.safe_top),
                "bottom": math.floor(HEIGHT * (1 - self.safe_bottom)),
                "draft": self.draft_label}


def load_script(path=SCRIPT):
    try:
        script = json.loads(Path(path).read_text(encoding="utf-8"))
        scenes = script["scenes"]
        if len(scenes) < 2:
            raise ValueError("El reel requiere al menos dos escenas")
        for scene in scenes:
            if scene["view"] not in {"hook", "attachment", "call", "qr", "verify", "cta"}:
                raise ValueError("Escena visual no admitida")
            if not isinstance(scene["duration"], (float, int)) or not math.isfinite(
                scene["duration"]
            ) or scene["duration"] <= 0:
                raise ValueError("Cada escena requiere duración positiva y finita")
            for key in ("headline", "narration", "detail"):
                if not isinstance(scene[key], str) or not scene[key].strip():
                    raise ValueError(f"Falta texto de escena: {key}")
            visual_keys = ("visual_title", "visual_detail") if scene["view"] in {
                "attachment", "call", "qr"
            } else ("options",) if scene["view"] == "cta" else ("phone_title", "message", "link")
            if any(not isinstance(scene.get(k), str) or not scene[k].strip()
                   for k in visual_keys):
                raise ValueError("Faltan textos visuales de la escena en la configuración")
        if not 17 <= sum(s["duration"] for s in scenes) <= 21:
            raise ValueError("El guion debe durar entre 17 y 21 segundos")
        return script
    except (OSError, ValueError, KeyError, TypeError):
        LOGGER.error("No se pudo cargar un guion válido desde %s", path)
        raise
