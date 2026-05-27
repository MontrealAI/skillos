from __future__ import annotations

from .storage import SkillOSStorage


class ReleaseCenter:
    def __init__(self, storage: SkillOSStorage):
        self.storage = storage

    def approve_release(self, skill_id: str, to_version: int, scope: str = "team", rollout: str = "10_percent_canary") -> dict:
        current = self.storage.get_skill_version(skill_id)
        candidate = self.storage.get_skill_version(skill_id, to_version)
        if not current:
            raise ValueError(f"Skill has no current version: {skill_id}")
        if not candidate:
            raise ValueError(f"Candidate version not found: {skill_id}:v{to_version}")
        release_id = self.storage.create_release(
            skill_id=skill_id,
            from_version=current["version"],
            to_version=to_version,
            scope=scope,
            rollout=rollout,
            status="released",
            rollback_version=current["version"],
        )
        self.storage.set_current_version(skill_id, to_version)
        return {
            "release_id": release_id,
            "skill_id": skill_id,
            "from_version": current["version"],
            "to_version": to_version,
            "scope": scope,
            "rollout": rollout,
            "status": "released",
            "rollback_version": current["version"],
        }

    def rollback(self, skill_id: str, target_version: int) -> dict:
        current = self.storage.get_skill_version(skill_id)
        target = self.storage.get_skill_version(skill_id, target_version)
        if not current or not target:
            raise ValueError("Current or target version not found")
        release_id = self.storage.create_release(
            skill_id=skill_id,
            from_version=current["version"],
            to_version=target_version,
            scope="rollback",
            rollout="immediate",
            status="rolled_back",
            rollback_version=target_version,
        )
        self.storage.set_current_version(skill_id, target_version)
        return {"release_id": release_id, "skill_id": skill_id, "from_version": current["version"], "to_version": target_version, "status": "rolled_back"}
