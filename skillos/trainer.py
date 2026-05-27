from __future__ import annotations

from .storage import SkillOSStorage


class SkillTrainer:
    def __init__(self, storage: SkillOSStorage):
        self.storage = storage

    def create_candidate_from_lesson(self, lesson_id: str) -> dict:
        lesson = self.storage.get_lesson(lesson_id)
        if not lesson:
            raise ValueError(f"Lesson not found: {lesson_id}")
        current = self.storage.get_skill_version(lesson["skill_id"])
        if not current:
            raise ValueError(f"Skill has no current version: {lesson['skill_id']}")
        candidate_markdown = self._bounded_edit(current["markdown"], lesson["suggested_change"])
        version = self.storage.add_skill_version(
            skill_id=lesson["skill_id"],
            markdown=candidate_markdown,
            status="candidate",
            allowed_tools=current.get("allowed_tools", []),
            blocked_tools=current.get("blocked_tools", []),
            tests=current.get("tests", []),
            quality_score=0.0,
        )
        self.storage.update_lesson_status(lesson_id, "candidate_created")
        return {
            "skill_id": lesson["skill_id"],
            "from_version": current["version"],
            "candidate_version": version,
            "change_summary": lesson["suggested_change"],
            "candidate_markdown": candidate_markdown,
        }

    def _bounded_edit(self, markdown: str, suggested_change: str) -> str:
        if suggested_change.lower() in markdown.lower():
            return markdown
        section = "\n\n## Learned Behavior\n\n- " + suggested_change.strip().rstrip(".") + ".\n"
        return markdown.rstrip() + section
