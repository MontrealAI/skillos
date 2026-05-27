from __future__ import annotations

import json
import sqlite3
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .models import utcnow


class SkillOSStorage:
    def __init__(self, db_path: str | Path = ".skillos/skillos.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connect(self):
        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        try:
            yield con
            con.commit()
        finally:
            con.close()

    def init(self) -> None:
        with self.connect() as con:
            con.executescript("""
            create table if not exists agents (
              agent_id text primary key,
              role text not null,
              description text not null default '',
              permissions_json text not null default '[]',
              installed_skills_json text not null default '[]',
              created_at text not null
            );

            create table if not exists skills (
              skill_id text primary key,
              name text not null,
              description text not null default '',
              current_version integer,
              visibility text not null default 'team',
              status text not null default 'active',
              created_at text not null,
              updated_at text not null
            );

            create table if not exists skill_versions (
              id integer primary key autoincrement,
              skill_id text not null,
              version integer not null,
              markdown text not null,
              status text not null default 'draft',
              quality_score real not null default 0,
              allowed_tools_json text not null default '[]',
              blocked_tools_json text not null default '[]',
              tests_json text not null default '[]',
              created_at text not null,
              unique(skill_id, version),
              foreign key(skill_id) references skills(skill_id)
            );

            create table if not exists jobs (
              job_id text primary key,
              agent_id text not null,
              goal text not null,
              inputs_json text not null,
              status text not null,
              created_at text not null
            );

            create table if not exists traces (
              trace_id text primary key,
              job_id text not null,
              agent_id text not null,
              goal text not null,
              skills_used_json text not null,
              tools_used_json text not null,
              inputs_json text not null,
              output text not null,
              human_edits text not null default '',
              score real not null default 0,
              failure_tags_json text not null default '[]',
              created_at text not null
            );

            create table if not exists lessons (
              lesson_id text primary key,
              skill_id text not null,
              pattern text not null,
              suggested_change text not null,
              evidence_json text not null,
              confidence real not null,
              status text not null default 'new',
              created_at text not null
            );

            create table if not exists releases (
              release_id text primary key,
              skill_id text not null,
              from_version integer not null,
              to_version integer not null,
              scope text not null,
              rollout text not null,
              status text not null,
              rollback_version integer,
              created_at text not null
            );
            """)

    def _row_to_dict(self, row: sqlite3.Row | None) -> dict[str, Any] | None:
        if row is None:
            return None
        out = dict(row)
        for key in list(out):
            if key.endswith("_json"):
                out[key[:-5]] = json.loads(out.pop(key) or "[]")
        return out

    def upsert_agent(self, agent_id: str, role: str, description: str = "", permissions: list[str] | None = None, installed_skills: list[str] | None = None) -> None:
        permissions = permissions or []
        installed_skills = installed_skills or []
        with self.connect() as con:
            con.execute("""
            insert into agents(agent_id, role, description, permissions_json, installed_skills_json, created_at)
            values(?,?,?,?,?,?)
            on conflict(agent_id) do update set
              role=excluded.role,
              description=excluded.description,
              permissions_json=excluded.permissions_json,
              installed_skills_json=excluded.installed_skills_json
            """, (agent_id, role, description, json.dumps(permissions), json.dumps(installed_skills), utcnow()))

    def list_agents(self) -> list[dict[str, Any]]:
        with self.connect() as con:
            return [self._row_to_dict(r) for r in con.execute("select * from agents order by agent_id")]

    def create_skill(self, skill_id: str, name: str, description: str = "", visibility: str = "team") -> None:
        now = utcnow()
        with self.connect() as con:
            con.execute("""
            insert or ignore into skills(skill_id, name, description, current_version, visibility, status, created_at, updated_at)
            values(?,?,?,?,?,?,?,?)
            """, (skill_id, name, description, None, visibility, "active", now, now))

    def get_skill(self, skill_id: str) -> dict[str, Any] | None:
        with self.connect() as con:
            return self._row_to_dict(con.execute("select * from skills where skill_id=?", (skill_id,)).fetchone())

    def list_skills(self) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = [self._row_to_dict(r) for r in con.execute("select * from skills order by skill_id")]
        for row in rows:
            row["current"] = self.get_skill_version(row["skill_id"])
            row["versions"] = self.list_skill_versions(row["skill_id"])
        return rows

    def next_skill_version(self, skill_id: str) -> int:
        with self.connect() as con:
            row = con.execute("select coalesce(max(version), 0) + 1 as next_version from skill_versions where skill_id=?", (skill_id,)).fetchone()
            return int(row["next_version"])

    def add_skill_version(self, skill_id: str, markdown: str, status: str = "draft", quality_score: float = 0.0, allowed_tools: list[str] | None = None, blocked_tools: list[str] | None = None, tests: list[dict[str, Any]] | None = None, version: int | None = None, set_current: bool = False) -> int:
        allowed_tools = allowed_tools or []
        blocked_tools = blocked_tools or []
        tests = tests or []
        version = version or self.next_skill_version(skill_id)
        with self.connect() as con:
            con.execute("""
            insert into skill_versions(skill_id, version, markdown, status, quality_score, allowed_tools_json, blocked_tools_json, tests_json, created_at)
            values(?,?,?,?,?,?,?,?,?)
            """, (skill_id, version, markdown, status, quality_score, json.dumps(allowed_tools), json.dumps(blocked_tools), json.dumps(tests), utcnow()))
            if set_current:
                con.execute("update skills set current_version=?, updated_at=? where skill_id=?", (version, utcnow(), skill_id))
        return version

    def get_skill_version(self, skill_id: str, version: int | None = None) -> dict[str, Any] | None:
        with self.connect() as con:
            if version is None:
                skill = con.execute("select current_version from skills where skill_id=?", (skill_id,)).fetchone()
                if not skill or skill["current_version"] is None:
                    return None
                version = int(skill["current_version"])
            row = con.execute("select * from skill_versions where skill_id=? and version=?", (skill_id, version)).fetchone()
            return self._row_to_dict(row)

    def list_skill_versions(self, skill_id: str) -> list[dict[str, Any]]:
        with self.connect() as con:
            return [self._row_to_dict(r) for r in con.execute("select * from skill_versions where skill_id=? order by version desc", (skill_id,))]

    def set_current_version(self, skill_id: str, version: int) -> None:
        with self.connect() as con:
            con.execute("update skills set current_version=?, updated_at=? where skill_id=?", (version, utcnow(), skill_id))
            con.execute("update skill_versions set status='approved' where skill_id=? and version=?", (skill_id, version))

    def update_skill_version(self, skill_id: str, version: int, *, status: str | None = None, quality_score: float | None = None) -> None:
        updates = []
        args: list[Any] = []
        if status is not None:
            updates.append("status=?")
            args.append(status)
        if quality_score is not None:
            updates.append("quality_score=?")
            args.append(quality_score)
        if not updates:
            return
        args.extend([skill_id, version])
        with self.connect() as con:
            con.execute(f"update skill_versions set {', '.join(updates)} where skill_id=? and version=?", args)

    def create_job(self, agent_id: str, goal: str, inputs: dict[str, Any], status: str = "completed") -> str:
        job_id = f"job_{uuid.uuid4().hex[:10]}"
        with self.connect() as con:
            con.execute("insert into jobs(job_id, agent_id, goal, inputs_json, status, created_at) values(?,?,?,?,?,?)", (job_id, agent_id, goal, json.dumps(inputs), status, utcnow()))
        return job_id

    def create_trace(self, job_id: str, agent_id: str, goal: str, skills_used: list[str], tools_used: list[str], inputs: dict[str, Any], output: str, human_edits: str = "", score: float = 0.0, failure_tags: list[str] | None = None) -> str:
        trace_id = f"trace_{uuid.uuid4().hex[:10]}"
        failure_tags = failure_tags or []
        with self.connect() as con:
            con.execute("""
            insert into traces(trace_id, job_id, agent_id, goal, skills_used_json, tools_used_json, inputs_json, output, human_edits, score, failure_tags_json, created_at)
            values(?,?,?,?,?,?,?,?,?,?,?,?)
            """, (trace_id, job_id, agent_id, goal, json.dumps(skills_used), json.dumps(tools_used), json.dumps(inputs), output, human_edits, score, json.dumps(failure_tags), utcnow()))
        return trace_id

    def list_traces(self, limit: int = 200) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute("select * from traces order by created_at desc limit ?", (limit,)).fetchall()
            return [self._row_to_dict(r) for r in rows]

    def create_lesson(self, skill_id: str, pattern: str, suggested_change: str, evidence: dict[str, Any], confidence: float, status: str = "new") -> str:
        lesson_id = f"lesson_{uuid.uuid4().hex[:10]}"
        with self.connect() as con:
            con.execute("""
            insert into lessons(lesson_id, skill_id, pattern, suggested_change, evidence_json, confidence, status, created_at)
            values(?,?,?,?,?,?,?,?)
            """, (lesson_id, skill_id, pattern, suggested_change, json.dumps(evidence), confidence, status, utcnow()))
        return lesson_id

    def get_lesson(self, lesson_id: str) -> dict[str, Any] | None:
        with self.connect() as con:
            return self._row_to_dict(con.execute("select * from lessons where lesson_id=?", (lesson_id,)).fetchone())

    def list_lessons(self, status: str | None = None) -> list[dict[str, Any]]:
        with self.connect() as con:
            if status:
                rows = con.execute("select * from lessons where status=? order by created_at desc", (status,)).fetchall()
            else:
                rows = con.execute("select * from lessons order by created_at desc").fetchall()
            return [self._row_to_dict(r) for r in rows]

    def update_lesson_status(self, lesson_id: str, status: str) -> None:
        with self.connect() as con:
            con.execute("update lessons set status=? where lesson_id=?", (status, lesson_id))

    def create_release(self, skill_id: str, from_version: int, to_version: int, scope: str, rollout: str, status: str = "released", rollback_version: int | None = None) -> str:
        release_id = f"rel_{uuid.uuid4().hex[:10]}"
        with self.connect() as con:
            con.execute("""
            insert into releases(release_id, skill_id, from_version, to_version, scope, rollout, status, rollback_version, created_at)
            values(?,?,?,?,?,?,?,?,?)
            """, (release_id, skill_id, from_version, to_version, scope, rollout, status, rollback_version, utcnow()))
        return release_id

    def list_releases(self) -> list[dict[str, Any]]:
        with self.connect() as con:
            return [self._row_to_dict(r) for r in con.execute("select * from releases order by created_at desc")]

    def dashboard(self) -> dict[str, Any]:
        with self.connect() as con:
            counts = {}
            for table in ["agents", "skills", "skill_versions", "jobs", "traces", "lessons", "releases"]:
                counts[table] = con.execute(f"select count(*) as n from {table}").fetchone()["n"]
            avg_score = con.execute("select coalesce(avg(score), 0) as n from traces").fetchone()["n"]
            approved_versions = con.execute("select count(*) as n from skill_versions where status='approved'").fetchone()["n"]
        return {
            "counts": counts,
            "average_trace_score": round(float(avg_score), 3),
            "approved_skill_versions": approved_versions,
            "recent_traces": self.list_traces(limit=8),
            "recent_lessons": self.list_lessons()[:8],
            "skills": self.list_skills(),
            "releases": self.list_releases()[:8],
        }
