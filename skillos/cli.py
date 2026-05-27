from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from .api import serve
from .evals import TestLab
from .learning import LearningEngine
from .releases import ReleaseCenter
from .runtime import AgentRuntime
from .seed import seed_demo
from .storage import SkillOSStorage
from .trainer import SkillTrainer
from .wealth_proof import markdown_report, write_wealth_proof


def storage_from_args(args) -> SkillOSStorage:
    return SkillOSStorage(getattr(args, "db", ".skillos/skillos.db"))


def print_json(data) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_init(args) -> None:
    storage = storage_from_args(args)
    seed_demo(storage)
    print("✅ Agent SkillOS initialized at", storage.db_path)


def cmd_reset(args) -> None:
    home = Path(getattr(args, "home", ".skillos"))
    if home.exists():
        shutil.rmtree(home)
    print("🧹 Reset complete. Run `python -m skillos.cli init` to recreate local data.")


def cmd_job(args) -> None:
    storage = storage_from_args(args)
    seed_demo(storage)
    runtime = AgentRuntime(storage)
    inputs = json.loads(args.inputs) if args.inputs else {}
    result = runtime.run_job(args.goal, inputs=inputs, agent_id=args.agent, human_edits=args.human_edits)
    print_json(result)


def cmd_learn(args) -> None:
    storage = storage_from_args(args)
    engine = LearningEngine(storage)
    lessons = engine.discover_lessons(min_support=args.min_support)
    print_json(lessons)


def cmd_train(args) -> None:
    storage = storage_from_args(args)
    trainer = SkillTrainer(storage)
    lab = TestLab(storage)
    candidate = trainer.create_candidate_from_lesson(args.lesson_id)
    result = lab.evaluate_skill(candidate["skill_id"], candidate["candidate_version"])
    print_json({"candidate": candidate, "test_result": result})


def cmd_approve(args) -> None:
    storage = storage_from_args(args)
    release = ReleaseCenter(storage).approve_release(args.skill_id, args.version, scope=args.scope, rollout=args.rollout)
    print_json(release)


def cmd_dashboard(args) -> None:
    storage = storage_from_args(args)
    storage.init()
    print_json(storage.dashboard())


def cmd_status(args) -> None:
    storage = storage_from_args(args)
    storage.init()
    dashboard = storage.dashboard()
    print("Agent SkillOS status")
    print("--------------------")
    print(f"Database: {storage.db_path}")
    print(f"Agents: {dashboard['counts']['agents']}")
    print(f"Skills: {dashboard['counts']['skills']}")
    print(f"Skill versions: {dashboard['counts']['skill_versions']}")
    print(f"Jobs: {dashboard['counts']['jobs']}")
    print(f"Lessons: {dashboard['counts']['lessons']}")
    print(f"Releases: {dashboard['counts']['releases']}")
    print(f"Average trace score: {dashboard['average_trace_score']}")
    print("\nRun the complete loop with: python -m skillos.cli demo")
    print("Start the local web app with: python -m skillos.cli serve")


def cmd_verify(args) -> None:
    db_path = Path(args.db)
    if db_path.exists():
        db_path.unlink()
    storage = SkillOSStorage(db_path)
    seed_demo(storage)
    runtime = AgentRuntime(storage)
    for i in range(4):
        runtime.run_job(
            "Draft a sales follow-up email from call notes",
            inputs={"prospect_name": f"Prospect {i}", "company_name": "Acme", "agreed_next_step": "review the pilot plan"},
            human_edits="Moved the next step to the opening lines.",
        )
    lessons = LearningEngine(storage).discover_lessons(min_support=3)
    assert lessons, "Expected the learning engine to find at least one lesson"
    candidate = SkillTrainer(storage).create_candidate_from_lesson(lessons[0]["lesson_id"])
    result = TestLab(storage).evaluate_skill(candidate["skill_id"], candidate["candidate_version"])
    assert result["recommendation"] == "approve_canary", "Expected candidate skill to pass Test Lab"
    release = ReleaseCenter(storage).approve_release(candidate["skill_id"], candidate["candidate_version"])
    assert release["to_version"] == candidate["candidate_version"], "Expected release to approve candidate"
    print("✅ Agent SkillOS verification passed")


def cmd_serve(args) -> None:
    storage = storage_from_args(args)
    seed_demo(storage)
    serve(storage=storage, host=args.host, port=args.port)


def cmd_demo(args) -> None:
    storage = storage_from_args(args)
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
    for prospect, company, pain, next_step in examples:
        runtime.run_job(
            "Draft a sales follow-up email from call notes",
            inputs={"prospect_name": prospect, "company_name": company, "pain_point": pain, "agreed_next_step": next_step},
            agent_id="sales_agent",
            human_edits="Moved the next step to the opening lines and made the ask clearer.",
        )
    lessons = LearningEngine(storage).discover_lessons(min_support=3)
    if lessons:
        candidate = SkillTrainer(storage).create_candidate_from_lesson(lessons[0]["lesson_id"])
        result = TestLab(storage).evaluate_skill(candidate["skill_id"], candidate["candidate_version"])
        release = ReleaseCenter(storage).approve_release(candidate["skill_id"], candidate["candidate_version"])
    else:
        candidate, result, release = None, None, None
    print("\n🚀 Agent SkillOS demo complete\n")
    print_json({
        "lessons_found": lessons,
        "candidate_created": candidate,
        "test_result": result,
        "release": release,
        "dashboard": storage.dashboard(),
    })
    print("\nNext: run `python -m skillos.cli serve` and open http://127.0.0.1:8765\n")


def cmd_wealth_proof(args) -> None:
    output = Path(args.output)
    report = write_wealth_proof(output)
    if args.markdown:
        Path(args.markdown).write_text(markdown_report(report), encoding="utf-8")
    print_json({
        "proved": report["conclusion"]["proved"],
        "workflow": report["workflow"]["name"],
        "final_skill_version": report["conclusion"]["final_skill_version"],
        "quality_gain_points_vs_initial_agent": report["conclusion"]["quality_gain_points_vs_initial_agent"],
        "speed_gain_percent_vs_initial_agent": report["conclusion"]["speed_gain_percent_vs_initial_agent"],
        "cost_reduction_percent_vs_initial_agent": report["conclusion"]["cost_reduction_percent_vs_initial_agent"],
        "projected_annual_savings_usd_vs_human_at_10000_jobs": report["conclusion"]["projected_annual_savings_usd_vs_human_at_10000_jobs"],
        "output": str(output),
    })
    if not report["conclusion"]["proved"]:
        raise SystemExit("SkillOS wealth proof failed")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Agent SkillOS: operating system for self-improving AI agents")
    parser.add_argument("--db", default=".skillos/skillos.db", help="Path to local SQLite database")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("init", help="Initialize local SkillOS data")
    p.set_defaults(func=cmd_init)

    p = sub.add_parser("reset", help="Delete local .skillos data")
    p.add_argument("--home", default=".skillos")
    p.set_defaults(func=cmd_reset)

    p = sub.add_parser("demo", help="Run the complete self-improvement demo")
    p.set_defaults(func=cmd_demo)

    p = sub.add_parser("wealth-proof", help="Prove one workflow gets cheaper, faster, and better from SkillOS learning")
    p.add_argument("--output", default="data/wealth_proof.json", help="Where to write the generated proof JSON")
    p.add_argument("--markdown", default="docs/wealth_accumulation_proof.md", help="Optional Markdown report path")
    p.set_defaults(func=cmd_wealth_proof)

    p = sub.add_parser("serve", help="Start local web app")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.set_defaults(func=cmd_serve)

    p = sub.add_parser("job", help="Run a single job")
    p.add_argument("goal")
    p.add_argument("--agent", default="sales_agent")
    p.add_argument("--inputs", default="{}", help="JSON input object")
    p.add_argument("--human-edits", default="")
    p.set_defaults(func=cmd_job)

    p = sub.add_parser("learn", help="Discover reusable lessons from traces")
    p.add_argument("--min-support", type=int, default=3)
    p.set_defaults(func=cmd_learn)

    p = sub.add_parser("train", help="Create and test a candidate skill from a lesson")
    p.add_argument("lesson_id")
    p.set_defaults(func=cmd_train)

    p = sub.add_parser("approve", help="Approve and release a candidate skill")
    p.add_argument("skill_id")
    p.add_argument("version", type=int)
    p.add_argument("--scope", default="team")
    p.add_argument("--rollout", default="10_percent_canary")
    p.set_defaults(func=cmd_approve)

    p = sub.add_parser("dashboard", help="Print dashboard JSON")
    p.set_defaults(func=cmd_dashboard)

    p = sub.add_parser("status", help="Print a friendly local status summary")
    p.set_defaults(func=cmd_status)

    p = sub.add_parser("verify", help="Run a full local verification of the SkillOS loop")
    p.set_defaults(func=cmd_verify)
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
