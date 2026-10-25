"""Manual news packages must remain outside automatic publishing."""

import json
import unittest

from build_news_review import ROOT, review_package


class NewsReviewTests(unittest.TestCase):
    def test_manual_packages_remain_pending_and_unstamped(self):
        for topic in ("php", "emudhra"):
            with self.subTest(topic=topic):
                path = ROOT / f"cyberpulse-bot/content/alerts/reviews/2026-10-21-{topic}.json"
                review = json.loads(path.read_text(encoding="utf-8"))
                package = review_package(review)
                self.assertEqual(review["publication_status"], "pending_user_review")
                self.assertNotIn("validacion", package["meta"])
                self.assertEqual(package["meta"]["revision_manual"]["estado"],
                                 "pendiente_aprobacion_usuario")
                self.assertNotIn("hilo_x", package)
                self.assertTrue(all(s["url"].startswith("https://") for s in review["sources"]))

    def test_php_identity_and_attributed_activity(self):
        path = ROOT / "cyberpulse-bot/content/alerts/reviews/2026-10-21-php.json"
        analysis = json.loads(path.read_text(encoding="utf-8"))["analysis"]
        self.assertEqual(analysis["cves"], ["CVE-2026-109618", "CVE-2026-109619"])
        self.assertEqual(analysis["severidad"], "critical")
        self.assertIn("Patchstack", analysis["nota_vigencia"])

    def test_emudhra_not_a_password_leak_or_unrelated_browser_cve(self):
        path = ROOT / "cyberpulse-bot/content/alerts/reviews/2026-10-21-emudhra.json"
        analysis = json.loads(path.read_text(encoding="utf-8"))["analysis"]
        self.assertEqual(analysis["cves"], [])
        self.assertIn("no son contraseñas personales", analysis["hecho_documentado"])
        self.assertIn("prevé", analysis["caption"])


if __name__ == "__main__":
    unittest.main()
