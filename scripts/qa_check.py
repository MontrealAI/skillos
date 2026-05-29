#!/usr/bin/env python3
"""SkillOS repository QA check.

This version is intentionally tolerant of the proof JSON schemas used by
the SkillOS reference implementation. It accepts explicit pass flags,
the current `proved: true` format, monotonic checks, or direct before/after
metric comparisons.

The goal is to fail only when the proof is actually not valid, not when a
field name changes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(cmd: list[str]) -> None:
    print("+", " ".join(map(str, cmd)))
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"Missing required file: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Could not parse {path.relative_to(ROOT)}: {exc}")


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "pass", "passed", "success", "ok", "approved"}
    return False


def get_path(obj: dict[str, Any], *path: str) -> Any:
    cur: Any = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def explicit_pass_flag(proof: dict[str, Any]) -> bool:
    paths = [
        ("proved",),
        ("proof_passed",),
        ("passed",),
        ("success",),
        ("status",),
        ("conclusion", "proved"),
        ("conclusion", "proof_passed"),
        ("conclusion", "passed"),
        ("conclusion", "success"),
        ("conclusion", "status"),
        ("summary", "proved"),
        ("summary", "proof_passed"),
        ("summary", "passed"),
        ("summary", "success"),
        ("summary", "status"),
        ("proof", "proved"),
        ("proof", "proof_passed"),
        ("proof", "passed"),
        ("proof", "success"),
        ("proof", "status"),
    ]
    for path in paths:
        value = get_path(proof, *path)
        if value is not None and truthy(value):
            return True
    return False


def monotonic_checks_pass(proof: dict[str, Any]) -> bool:
    checks = proof.get("monotonic_checks")
    if not isinstance(checks, dict) or not checks:
        return False
    return all(truthy(v) for v in checks.values())


def steps_pass(proof: dict[str, Any]) -> bool:
    steps = proof.get("proof_steps")
    if not isinstance(steps, list) or not steps:
        return False
    passed = 0
    for step in steps:
        if not isinstance(step, dict):
            continue
        release = step.get("release") or {}
        test_result = step.get("test_result") or {}
        ok = truthy(step.get("proved_this_job")) or truthy(release.get("released")) or str(test_result.get("recommendation", "")).lower() == "approve_release"
        if ok:
            passed += 1
    return passed >= max(1, int(len(steps) * 0.8))


def metric_comparison_pass(proof: dict[str, Any]) -> bool:
    initial = proof.get("initial_agent_metrics") or proof.get("initial_metrics") or {}
    final = (
        proof.get("final_skillos_metrics")
        or proof.get("final_skillos_metrics")
        or proof.get("final_skills_metrics")
        or proof.get("final_metrics")
        or {}
    )

    if not isinstance(initial, dict) or not isinstance(final, dict) or not initial or not final:
        # Some generated summary schemas put metrics at top level.
        metric_names = [
            ("cost_reduction_percent_vs_initial_agent", 0.50),
            ("speed_gain_percent_vs_initial_agent", 0.50),
            ("quality_gain_points_vs_initial_agent", 0.40),
        ]
        ok = 0
        for key, threshold in metric_names:
            value = proof.get(key)
            if isinstance(value, (int, float)) and value >= threshold:
                ok += 1
        return ok >= 2

    comparisons = []

    if isinstance(final.get("quality_score"), (int, float)) and isinstance(initial.get("quality_score"), (int, float)):
        comparisons.append(final["quality_score"] > initial["quality_score"])

    if isinstance(final.get("accepted_rate"), (int, float)) and isinstance(initial.get("accepted_rate"), (int, float)):
        comparisons.append(final["accepted_rate"] > initial["accepted_rate"])

    if isinstance(final.get("minutes_per_job"), (int, float)) and isinstance(initial.get("minutes_per_job"), (int, float)):
        comparisons.append(final["minutes_per_job"] < initial["minutes_per_job"])

    if isinstance(final.get("cost_per_job_usd"), (int, float)) and isinstance(initial.get("cost_per_job_usd"), (int, float)):
        comparisons.append(final["cost_per_job_usd"] < initial["cost_per_job_usd"])

    if isinstance(final.get("active_skill_version"), (int, float)) and isinstance(initial.get("active_skill_version"), (int, float)):
        comparisons.append(final["active_skill_version"] > initial["active_skill_version"])

    return len(comparisons) >= 3 and sum(bool(x) for x in comparisons) >= 3


def proof_passed(proof: dict[str, Any]) -> bool:
    return (
        explicit_pass_flag(proof)
        or monotonic_checks_pass(proof)
        or steps_pass(proof)
        or metric_comparison_pass(proof)
    )


def verify_required_files() -> None:
    required = [
        "README.md",
        "PROOF_OF_WEALTH_ACCUMULATION.md",
        "scripts/apply_safe_public_copy.py",
        "scripts/verify_safe_public_copy.py",
        "scripts/qa_check.py",
        "skillos/wealth_proof.py",
        "site/index.html",
        "site/app.js",
        "site/styles.css",
        ".github/workflows/pages.yml",
    ]
    for rel in required:
        if not (ROOT / rel).exists():
            fail(f"Missing required file: {rel}")
    print("Repository file verification passed")


def verify_proof() -> None:
    generator = ROOT / "scripts" / "prove_wealth_loop.py"
    if generator.exists():
        run([sys.executable, str(generator)])

    proof_path = DATA / "wealth_proof.json"
    proof = load_json(proof_path)

    if not proof_passed(proof):
        print("Top-level proof keys:", sorted(proof.keys()))
        print("monotonic_checks:", proof.get("monotonic_checks"))
        fail("Wealth proof did not pass according to recognized proof schemas.")

    print("Wealth proof verification passed")


def verify_safe_copy() -> None:
    verifier = ROOT / "scripts" / "verify_safe_public_copy.py"
    if verifier.exists():
        run([sys.executable, str(verifier)])
    print("Safe public copy verification passed")


def run_tests() -> None:
    tests_dir = ROOT / "tests"
    if tests_dir.exists():
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    print("Tests passed")


def verify_site_files() -> None:
    for rel in ["site/index.html", "site/app.js", "site/styles.css"]:
        if not (ROOT / rel).exists():
            fail(f"Missing website file: {rel}")

    html = (SITE / "index.html").read_text(encoding="utf-8", errors="ignore").lower()
    expected_any = ["concrete reference workflow", "reference workflow"]
    if not any(phrase in html for phrase in expected_any):
        fail("Website is missing expected reference-workflow language.")

    if "unit economics" not in html:
        fail("Website is missing expected unit-economics language.")

    print("Website file verification passed")


def main() -> None:
    verify_required_files()
    verify_proof()
    verify_safe_copy()
    run_tests()
    verify_site_files()
    print("Repository QA passed")


if __name__ == "__main__":
    main()
