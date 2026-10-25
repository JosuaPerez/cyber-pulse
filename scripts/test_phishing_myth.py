"""Checks for the 19-second reel; no live provider calls."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from build_phishing_myth import Settings, build, load_script


class PhishingMythTests(unittest.TestCase):
    def test_timing_and_scope(self):
        script = load_script()
        self.assertEqual(sum(s["duration"] for s in script["scenes"]), 19)
        self.assertEqual([s["view"] for s in script["scenes"]],
                         ["hook", "attachment", "call", "qr", "verify", "cta"])
        self.assertIn("ficticios", script["caption"])

    def test_no_unsubstantiated_majority_or_qr_infection_claim(self):
        script = load_script()
        narration = " ".join(s["narration"] for s in script["scenes"])
        self.assertNotIn("mayoría", narration)
        self.assertIn("por sí solo", script["caption"])
        self.assertIn("otro canal", narration)
        self.assertTrue(all(url.startswith("https://") for url in script["sources"]))

    def test_voice_failure_fails_closed_without_silent_fallback(self):
        with TemporaryDirectory(prefix="cyberpulse-myth-test-") as folder:
            with (
                patch("app.reels.myth.prepare_audio", side_effect=RuntimeError("TTS unavailable")),
                self.assertRaises(RuntimeError),
            ):
                build(Path(folder), settings=Settings(audio="voice"))
            self.assertFalse((Path(folder) / "preview.html").exists())


if __name__ == "__main__":
    unittest.main()
