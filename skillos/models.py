from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def as_jsonable(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return value


@dataclass
class Agent:
    agent_id: str
    role: str
    description: str = ""
    permissions: list[str] = field(default_factory=list)
    installed_skills: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utcnow)


@dataclass
class Job:
    job_id: str
    agent_id: str
    goal: str
    inputs: dict[str, Any]
    status: str = "created"
    created_at: str = field(default_factory=utcnow)


@dataclass
class Trace:
    trace_id: str
    job_id: str
    agent_id: str
    goal: str
    skills_used: list[str]
    tools_used: list[str]
    inputs: dict[str, Any]
    output: str
    human_edits: str = ""
    score: float = 0.0
    failure_tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utcnow)


@dataclass
class Lesson:
    lesson_id: str
    skill_id: str
    pattern: str
    suggested_change: str
    evidence: dict[str, Any]
    confidence: float
    status: str = "new"
    created_at: str = field(default_factory=utcnow)


@dataclass
class SkillVersion:
    skill_id: str
    version: int
    markdown: str
    status: str = "draft"
    quality_score: float = 0.0
    allowed_tools: list[str] = field(default_factory=list)
    blocked_tools: list[str] = field(default_factory=list)
    tests: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(default_factory=utcnow)


@dataclass
class Release:
    release_id: str
    skill_id: str
    from_version: int
    to_version: int
    scope: str
    rollout: str
    status: str = "released"
    rollback_version: int | None = None
    created_at: str = field(default_factory=utcnow)
