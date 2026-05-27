import json
import shutil
import unittest

from scripts.build_pages import DIST, build, run_demo_snapshot


class PagesBuildTest(unittest.TestCase):
    def tearDown(self):
        if DIST.exists():
            shutil.rmtree(DIST)

    def test_demo_snapshot_has_release_and_dashboard_and_wealth_proof(self):
        snapshot = run_demo_snapshot()
        self.assertEqual(snapshot["headline"], "Work → Trace → Learn → Skill → Test → Approve → Release → Improve")
        self.assertTrue(snapshot["generated_at"].endswith("Z"))
        self.assertTrue(snapshot["lessons"])
        self.assertEqual(snapshot["test_result"]["recommendation"], "approve_canary")
        self.assertEqual(snapshot["release"]["skill_id"], "sales_followup_email")
        self.assertGreaterEqual(snapshot["dashboard"]["counts"]["skills"], 3)
        self.assertTrue(snapshot["wealth_proof"]["conclusion"]["proved"])

    def test_build_creates_pages_artifacts(self):
        build()
        for rel in ["index.html", "styles.css", "app.js", ".nojekyll", "data/demo.json", "data/wealth_proof.json", "pages-manifest.json", "sitemap.xml"]:
            self.assertTrue((DIST / rel).exists(), rel)
        data = json.loads((DIST / "data" / "demo.json").read_text(encoding="utf-8"))
        self.assertTrue(data["release"])
        self.assertTrue(data["wealth_proof"]["conclusion"]["proved"])
        self.assertIn("MontrealAI/skillos", data["generated_for"])
        proof = json.loads((DIST / "data" / "wealth_proof.json").read_text(encoding="utf-8"))
        self.assertTrue(proof["conclusion"]["proved"])
        self.assertLess(proof["final_skillos_metrics"]["cost_per_job_usd"], proof["initial_agent_metrics"]["cost_per_job_usd"])


if __name__ == "__main__":
    unittest.main()
