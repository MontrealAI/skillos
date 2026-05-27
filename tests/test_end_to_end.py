import tempfile
import unittest
from pathlib import Path

from skillos.evals import TestLab
from skillos.learning import LearningEngine
from skillos.releases import ReleaseCenter
from skillos.runtime import AgentRuntime
from skillos.seed import seed_demo
from skillos.storage import SkillOSStorage
from skillos.trainer import SkillTrainer


class EndToEndTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.storage = SkillOSStorage(Path(self.tmp.name) / "skillos.db")
        seed_demo(self.storage)

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_skillos_loop(self):
        runtime = AgentRuntime(self.storage)
        for i in range(4):
            runtime.run_job(
                "Draft a sales follow-up email from call notes",
                inputs={"prospect_name": f"Prospect {i}", "company_name": "Acme", "agreed_next_step": "review the pilot plan"},
                human_edits="Moved the next step to the opening lines.",
            )
        lessons = LearningEngine(self.storage).discover_lessons(min_support=3)
        self.assertGreaterEqual(len(lessons), 1)
        candidate = SkillTrainer(self.storage).create_candidate_from_lesson(lessons[0]["lesson_id"])
        result = TestLab(self.storage).evaluate_skill(candidate["skill_id"], candidate["candidate_version"])
        self.assertEqual(result["recommendation"], "approve_canary")
        release = ReleaseCenter(self.storage).approve_release(candidate["skill_id"], candidate["candidate_version"])
        current = self.storage.get_skill_version("sales_followup_email")
        self.assertEqual(current["version"], release["to_version"])
        self.assertIn("first three lines", current["markdown"].lower())


if __name__ == "__main__":
    unittest.main()
