from __future__ import annotations

import unittest

from skillos.wealth_proof import run_wealth_proof


class WealthProofTest(unittest.TestCase):
    def test_one_workflow_gets_cheaper_faster_better_after_each_job(self):
        report = run_wealth_proof()
        self.assertTrue(report["conclusion"]["proved"])
        self.assertTrue(report["monotonic_checks"]["every_job_created_approved_release"])
        self.assertTrue(report["monotonic_checks"]["cost_per_job_decreased_after_each_release"])
        self.assertTrue(report["monotonic_checks"]["minutes_per_job_decreased_after_each_release"])
        self.assertTrue(report["monotonic_checks"]["quality_score_increased_after_each_release"])
        self.assertTrue(report["monotonic_checks"]["accepted_rate_increased_after_each_release"])
        for step in report["proof_steps"]:
            self.assertTrue(step["proved_this_job"])
            before = step["metrics_before_release"]
            after = step["metrics_after_release"]
            self.assertLess(after["cost_per_job_usd"], before["cost_per_job_usd"])
            self.assertLess(after["minutes_per_job"], before["minutes_per_job"])
            self.assertGreater(after["quality_score"], before["quality_score"])
            self.assertGreater(after["accepted_rate"], before["accepted_rate"])

    def test_wealth_metrics_are_material(self):
        report = run_wealth_proof()
        c = report["conclusion"]
        self.assertGreaterEqual(c["cost_reduction_percent_vs_initial_agent"], 0.4)
        self.assertGreaterEqual(c["speed_gain_percent_vs_initial_agent"], 0.45)
        self.assertGreaterEqual(c["quality_gain_points_vs_initial_agent"], 0.3)
        self.assertGreater(c["projected_annual_savings_usd_vs_human_at_10000_jobs"], 100000)


if __name__ == "__main__":
    unittest.main()
