from __future__ import annotations

import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from skillos.evals import TestLab
from skillos.learning import LearningEngine
from skillos.releases import ReleaseCenter
from skillos.runtime import AgentRuntime
from skillos.seed import seed_demo
from skillos.storage import SkillOSStorage
from skillos.trainer import SkillTrainer
from skillos.wealth_proof import run_wealth_proof

SITE = ROOT / "site"
DIST = ROOT / "dist"
PAGES_URL = "https://montrealai.github.io/skillos/"
REPO_URL = "https://github.com/MontrealAI/skillos"


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def run_demo_snapshot() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        storage = SkillOSStorage(Path(tmp) / "skillos-pages.db")
        seed_demo(storage)
        runtime = AgentRuntime(storage)
        examples = [
            ("Maya", "Orion Labs", "manual CRM follow-up", "review the pilot plan on Friday"),
            ("Noah", "VectorPay", "slow sales handoffs", "send a two-page implementation outline"),
            ("Iris", "Northwind", "support backlog triage", "schedule a technical scoping call"),
            ("Sam", "HelioGrid", "energy-project reporting", "share the security questionnaire"),
            ("Jules", "AtlasOps", "spreadsheet cleanup", "confirm stakeholder availability"),
            ("Ari", "NovaWorks", "manual reporting", "schedule a workflow review"),
        ]
        traces = []
        for prospect, company, pain, next_step in examples:
            traces.append(runtime.run_job(
                "Draft a sales follow-up email from call notes",
                inputs={
                    "prospect_name": prospect,
                    "company_name": company,
                    "pain_point": pain,
                    "agreed_next_step": next_step,
                },
                agent_id="sales_agent",
                human_edits="Moved the next step to the opening lines and made the ask clearer.",
            ))
        lessons = LearningEngine(storage).discover_lessons(min_support=3)
        candidate = test_result = release = None
        if lessons:
            candidate = SkillTrainer(storage).create_candidate_from_lesson(lessons[0]["lesson_id"])
            test_result = TestLab(storage).evaluate_skill(candidate["skill_id"], candidate["candidate_version"])
            if test_result["recommendation"] == "approve_canary":
                release = ReleaseCenter(storage).approve_release(candidate["skill_id"], candidate["candidate_version"])
        wealth_proof = run_wealth_proof()
        return {
            "headline": "Work → Trace → Learn → Skill → Test → Approve → Release → Improve",
            "generated_at": iso_now(),
            "url": PAGES_URL,
            "repository": REPO_URL,
            "generated_for": "MontrealAI/skillos",
            "sample_traces": traces[:3],
            "lessons": lessons,
            "candidate": candidate,
            "test_result": test_result,
            "release": release,
            "dashboard": storage.dashboard(),
            "wealth_proof": wealth_proof,
        }


def build() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    if not SITE.exists():
        raise SystemExit(f"Missing site source folder: {SITE}")
    shutil.copytree(SITE, DIST)
    (DIST / ".nojekyll").write_text("", encoding="utf-8")
    (DIST / "data").mkdir(exist_ok=True)
    snapshot = run_demo_snapshot()
    wealth_proof = snapshot["wealth_proof"]
    for key in ["lessons", "candidate", "test_result", "release", "dashboard", "wealth_proof"]:
        if not snapshot.get(key):
            raise SystemExit(f"Demo snapshot missing {key}; refusing to deploy an unconvincing demo")
    if not wealth_proof.get("conclusion", {}).get("proved"):
        raise SystemExit("Wealth proof failed; refusing to deploy")
    (DIST / "data" / "demo.json").write_text(json.dumps(snapshot, indent=2, ensure_ascii=False), encoding="utf-8")
    (DIST / "data" / "wealth_proof.json").write_text(json.dumps(wealth_proof, indent=2, ensure_ascii=False), encoding="utf-8")
    manifest = {
        "site": "Agent SkillOS",
        "generated_by": "scripts/build_pages.py",
        "generated_at": snapshot["generated_at"],
        "entrypoint": "index.html",
        "pages_url": PAGES_URL,
        "repository": REPO_URL,
        "required_files": ["index.html", "styles.css", "app.js", "data/demo.json", "data/wealth_proof.json", ".nojekyll"],
        "wealth_proof_passed": True,
    }
    (DIST / "pages-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (DIST / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n", encoding="utf-8")
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url>\n    <loc>{PAGES_URL}</loc>\n    <lastmod>{snapshot["generated_at"]}</lastmod>\n  </url>\n</urlset>\n'''
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    c = wealth_proof["conclusion"]
    print(f"Built GitHub Pages site at {DIST}")
    print(f"Generated demo snapshot with {len(snapshot['sample_traces'])} sample traces and {len(snapshot['lessons'])} lesson(s)")
    print(f"Generated wealth proof: {wealth_proof['workflow']['name']} → v{c['final_skill_version']} with {c['cost_reduction_percent_vs_initial_agent']:.0%} cost reduction vs initial agent")


if __name__ == "__main__":
    build()
