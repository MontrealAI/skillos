import tempfile
import unittest
from pathlib import Path

from skillos.seed import seed_demo
from skillos.storage import SkillOSStorage


class StorageTest(unittest.TestCase):
    def test_seed_creates_core_objects(self):
        with tempfile.TemporaryDirectory() as tmp:
            storage = SkillOSStorage(Path(tmp) / "skillos.db")
            seed_demo(storage)
            dashboard = storage.dashboard()
            self.assertEqual(dashboard["counts"]["agents"], 3)
            self.assertEqual(dashboard["counts"]["skills"], 3)
            self.assertEqual(dashboard["counts"]["skill_versions"], 3)


if __name__ == "__main__":
    unittest.main()
