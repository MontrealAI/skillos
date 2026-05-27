from __future__ import annotations

from .runtime import AgentRuntime
from .storage import SkillOSStorage


class TestLab:
    def __init__(self, storage: SkillOSStorage):
        self.storage = storage

    def evaluate_skill(self, skill_id: str, candidate_version: int, baseline_version: int | None = None) -> dict:
        candidate = self.storage.get_skill_version(skill_id, candidate_version)
        if not candidate:
            raise ValueError(f"Candidate not found: {skill_id}:v{candidate_version}")
        if baseline_version is None:
            baseline = self.storage.get_skill_version(skill_id)
        else:
            baseline = self.storage.get_skill_version(skill_id, baseline_version)
        if not baseline:
            raise ValueError(f"Baseline not found: {skill_id}")
        cases = self._cases_for(skill_id)
        candidate_scores = [self._score_markdown(skill_id, candidate["markdown"], case) for case in cases]
        baseline_scores = [self._score_markdown(skill_id, baseline["markdown"], case) for case in cases]
        wins = sum(1 for c, b in zip(candidate_scores, baseline_scores) if c > b)
        ties = sum(1 for c, b in zip(candidate_scores, baseline_scores) if c == b)
        losses = len(cases) - wins - ties
        candidate_score = round(sum(candidate_scores) / len(candidate_scores), 3)
        baseline_score = round(sum(baseline_scores) / len(baseline_scores), 3)
        safety = self._safety_checks(candidate["markdown"])
        result = {
            "skill_id": skill_id,
            "baseline_version": baseline["version"],
            "candidate_version": candidate_version,
            "cases": len(cases),
            "wins": wins,
            "ties": ties,
            "losses": losses,
            "win_rate": round(wins / len(cases), 3),
            "baseline_score": baseline_score,
            "candidate_score": candidate_score,
            "quality_delta": round(candidate_score - baseline_score, 3),
            "safety": safety,
            "recommendation": "approve_canary" if candidate_score > baseline_score and safety["passed"] else "reject_or_review",
        }
        self.storage.update_skill_version(skill_id, candidate_version, quality_score=candidate_score)
        return result

    def _cases_for(self, skill_id: str) -> list[dict]:
        if skill_id == "sales_followup_email":
            return [
                {"prospect_name": "Maya", "company_name": "Orion Labs", "pain_point": "manual CRM follow-up", "agreed_next_step": "review the pilot plan on Friday"},
                {"prospect_name": "Noah", "company_name": "VectorPay", "pain_point": "slow sales handoffs", "agreed_next_step": "send a two-page implementation outline"},
                {"prospect_name": "Iris", "company_name": "Northwind", "pain_point": "support backlog triage", "agreed_next_step": "schedule a technical scoping call"},
                {"prospect_name": "Sam", "company_name": "HelioGrid", "pain_point": "energy-project reporting", "agreed_next_step": "share the security questionnaire"},
                {"prospect_name": "Jules", "company_name": "AtlasOps", "pain_point": "spreadsheet cleanup", "agreed_next_step": "confirm stakeholder availability"},
            ]
        return [{"topic": "agent skills"}, {"topic": "network learning"}, {"topic": "release governance"}]

    def _score_markdown(self, skill_id: str, markdown: str, case: dict) -> float:
        if skill_id == "sales_followup_email":
            has_next_step_rule = "first three lines" in markdown.lower() or "opening section" in markdown.lower()
            return 0.92 if has_next_step_rule else 0.74
        return 0.84

    def _safety_checks(self, markdown: str) -> dict:
        dangerous = ["send without approval", "delete customer", "initiate payment without approval", "bypass approval"]
        lowered = markdown.lower()
        findings = [term for term in dangerous if term in lowered]
        return {
            "passed": not findings,
            "findings": findings,
            "checks": ["no unauthorized send", "no payment initiation", "no destructive action", "no approval bypass"],
        }
