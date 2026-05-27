from __future__ import annotations

from .storage import SkillOSStorage


class LearningEngine:
    def __init__(self, storage: SkillOSStorage):
        self.storage = storage

    def discover_lessons(self, min_support: int = 3) -> list[dict]:
        lessons: list[dict] = []
        lessons.extend(self._discover_sales_followup_next_step(min_support=min_support))
        return lessons

    def _discover_sales_followup_next_step(self, min_support: int) -> list[dict]:
        skill_id = "sales_followup_email"
        current = self.storage.get_skill_version(skill_id)
        if not current:
            return []
        if "first three lines" in current["markdown"].lower():
            return []
        existing = [l for l in self.storage.list_lessons() if l["skill_id"] == skill_id and "first three lines" in l["suggested_change"].lower() and l["status"] != "rejected"]
        if existing:
            return existing
        traces = self.storage.list_traces(limit=500)
        relevant = [t for t in traces if any(s.startswith(f"{skill_id}:") for s in t["skills_used"])]
        support = []
        for trace in relevant:
            feedback = (trace.get("human_edits") or "").lower()
            output = (trace.get("output") or "").lower().splitlines()[:4]
            output_first_lines = " ".join(output)
            if "next step" in feedback or "move" in feedback and "next" in feedback:
                support.append(trace)
            elif "next step" not in output_first_lines and trace.get("score", 0) < 0.8:
                support.append(trace)
        if len(support) < min_support:
            return []
        evidence = {
            "jobs_analyzed": len(relevant),
            "supporting_traces": len(support),
            "average_score_before": round(sum(float(t["score"]) for t in relevant) / max(1, len(relevant)), 3),
            "example_trace_ids": [t["trace_id"] for t in support[:5]],
        }
        lesson_id = self.storage.create_lesson(
            skill_id=skill_id,
            pattern="Users repeatedly improve follow-up emails by making the agreed next step more prominent.",
            suggested_change="Put the agreed next step in the first three lines of the email.",
            evidence=evidence,
            confidence=min(0.95, 0.55 + len(support) / max(10, len(relevant) * 2)),
            status="ready_to_train",
        )
        return [self.storage.get_lesson(lesson_id)]
