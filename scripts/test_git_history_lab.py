"""Regression checks for the isolated educational Git demonstration."""

import json
import unittest

from build_git_history_lab import DUMMY, ROOT, demonstrate


class GitHistoryLabTests(unittest.TestCase):
    def test_real_git_history_preserves_only_the_fake_old_credential(self):
        evidence = demonstrate()
        self.assertNotIn(DUMMY, evidence["current"])
        self.assertIn(DUMMY, evidence["previous"])
        self.assertEqual(evidence["remote_count"], 0)
        self.assertEqual(evidence["commit_count"], 2)
        self.assertNotEqual(evidence["head"], evidence["previous_commit"])

    def test_script_is_short_and_explicitly_a_draft(self):
        script = json.loads((ROOT / "cyberpulse-bot/content/labs/git-history.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(sum(scene["duration"] for scene in script["scenes"]), 27)
        self.assertIn("Borrador", script["status"])
        self.assertIn("ficticio", script["caption"])
        self.assertEqual(len(script["scenes"]), 5)

    def test_motion_script_keeps_provisional_timing_explicit(self):
        script = json.loads((ROOT / "cyberpulse-bot/content/labs/git-history-motion.json")
                            .read_text(encoding="utf-8"))
        self.assertEqual(sum(scene["duration"] for scene in script["scenes"]), 29)
        self.assertIn("sin voz", script["status"])
        self.assertIn("provisionales", script["status"])
        self.assertTrue(all(scene["duration"] > 0 for scene in script["scenes"]))


if __name__ == "__main__":
    unittest.main()
