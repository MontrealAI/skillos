from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .evals import TestLab
from .learning import LearningEngine
from .releases import ReleaseCenter
from .runtime import AgentRuntime
from .seed import seed_demo
from .storage import SkillOSStorage
from .trainer import SkillTrainer


WEB_ROOT = Path(__file__).resolve().parent.parent / "web"


class SkillOSHandler(BaseHTTPRequestHandler):
    storage: SkillOSStorage

    def log_message(self, format, *args):
        return

    def _send_json(self, data, status: int = 200) -> None:
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path) -> None:
        if not path.exists() or path.is_dir():
            self.send_error(404)
            return
        body = path.read_bytes()
        content_type = "text/html; charset=utf-8"
        if path.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        if path.suffix == ".js":
            content_type = "application/javascript; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            if path == "/api/health":
                return self._send_json({"ok": True, "service": "Agent SkillOS"})
            if path == "/api/dashboard":
                return self._send_json(self.storage.dashboard())
            if path == "/api/skills":
                return self._send_json(self.storage.list_skills())
            if path == "/api/lessons":
                return self._send_json(self.storage.list_lessons())
            if path == "/api/releases":
                return self._send_json(self.storage.list_releases())
            if path in ["/", "/index.html"]:
                return self._send_file(WEB_ROOT / "index.html")
            static_path = (WEB_ROOT / path.lstrip("/")).resolve()
            if str(static_path).startswith(str(WEB_ROOT.resolve())):
                return self._send_file(static_path)
            self.send_error(404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            body = self._read_body()
            if path == "/api/init":
                seed_demo(self.storage)
                return self._send_json({"ok": True})
            if path == "/api/jobs":
                result = AgentRuntime(self.storage).run_job(
                    goal=body.get("goal", "Draft a sales follow-up email from call notes"),
                    inputs=body.get("inputs", {}),
                    agent_id=body.get("agent_id", "sales_agent"),
                    human_edits=body.get("human_edits", ""),
                )
                return self._send_json(result)
            if path == "/api/learn":
                lessons = LearningEngine(self.storage).discover_lessons(min_support=int(body.get("min_support", 3)))
                return self._send_json(lessons)
            if path == "/api/train":
                lesson_id = body["lesson_id"]
                candidate = SkillTrainer(self.storage).create_candidate_from_lesson(lesson_id)
                result = TestLab(self.storage).evaluate_skill(candidate["skill_id"], candidate["candidate_version"])
                return self._send_json({"candidate": candidate, "test_result": result})
            if path == "/api/approve":
                release = ReleaseCenter(self.storage).approve_release(
                    body["skill_id"],
                    int(body["version"]),
                    scope=body.get("scope", "team"),
                    rollout=body.get("rollout", "10_percent_canary"),
                )
                return self._send_json(release)
            if path == "/api/demo":
                from .cli import cmd_demo
                return self._send_json({"message": "Use the CLI demo for the full printed walkthrough: python -m skillos.cli demo"})
            self.send_error(404)
        except Exception as exc:
            self._send_json({"error": str(exc)}, status=500)


def make_handler(storage: SkillOSStorage):
    class BoundHandler(SkillOSHandler):
        pass
    BoundHandler.storage = storage
    return BoundHandler


def serve(storage: SkillOSStorage | None = None, host: str = "127.0.0.1", port: int = 8765) -> None:
    storage = storage or SkillOSStorage()
    storage.init()
    server = ThreadingHTTPServer((host, port), make_handler(storage))
    print(f"Agent SkillOS is running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Agent SkillOS.")
    finally:
        server.server_close()
