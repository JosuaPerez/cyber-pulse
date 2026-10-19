"""Editorial checks for the phishing myth reel; no provider calls."""

import contextlib
import io
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory, gettempdir
from unittest.mock import patch

from build_phishing_myth import build, load_script


class PhishingMythTests(unittest.TestCase):
    def test_timing_and_scope(self):
        script = load_script()
        self.assertEqual(sum(scene["duration"] for scene in script["scenes"]), 29)
        self.assertEqual([scene["view"] for scene in script["scenes"]],
                         ["hook", "link", "attachment", "call", "qr", "verify", "cta"])
        self.assertIn("ficticios", script["caption"])

    def test_no_unsubstantiated_majority_or_qr_infection_claim(self):
        script = load_script()
        narration = " ".join(scene["narration"] for scene in script["scenes"])
        self.assertNotIn("mayoría", narration)
        self.assertIn("por sí solo", script["caption"])
        self.assertIn("otro canal", narration)
        self.assertTrue(all(url.startswith("https://") for url in script["sources"]))

    def test_voice_failure_is_labelled_silent_without_old_audio(self):
        temp_root = Path(gettempdir()).resolve()
        with TemporaryDirectory(prefix="cyberpulse-myth-test-", dir=temp_root) as folder:
            output = Path(folder).resolve()
            self.assertEqual(output.parent, temp_root)
            self.assertTrue(output.name.startswith("cyberpulse-myth-test-"))
            with (
                patch("build_phishing_myth.make_voice", side_effect=RuntimeError("HTTP 429")),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                script, audio = build(output, with_voice=True)
            self.assertIsNone(audio)
            timing = json.loads((output / "timing.json").read_text(encoding="utf-8"))
            self.assertFalse(timing["voice"])
            self.assertEqual(timing["voice_error"], "HTTP 429")
            self.assertEqual(sum(scene["duration"] for scene in script["scenes"]), 29)
            self.assertNotIn('"audio": "data:', (output / "preview.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
