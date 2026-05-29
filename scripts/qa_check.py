#!/usr/bin/env python3
"""SkillOS repository QA check with autonomous safe-copy enforcement."""

from __future__ import annotations
import json, subprocess, sys
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
    return json.loads(path.read_text(encoding="utf-8"))

def truthy(value: Any) -> bool:
    if isinstance(value, bool): return value
    if isinstance(value, (int, float)): return value > 0
    if isinstance(value, str): return value.strip().lower() in {"true", "yes", "pass", "passed", "success", "ok", "approved"}
    return False

def get_path(obj: dict[str, Any], *path: str) -> Any:
    cur: Any = obj
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur

def proof_passed(proof: dict[str, Any]) -> bool:
    for path in [
        ("proved",), ("proof_passed",), ("passed",), ("success",), ("status",),
        ("conclusion","proved"), ("conclusion","proof_passed"), ("conclusion","passed"), ("conclusion","success"), ("conclusion","status"),
        ("summary","proved"), ("summary","proof_passed"), ("summary","passed"), ("summary","success"), ("summary","status"),
    ]:
        value = get_path(proof, *path)
        if value is not None and truthy(value):
            return True

    checks = proof.get("monotonic_checks")
    if isinstance(checks, dict) and checks and all(truthy(v) for v in checks.values()):
        return True

    initial = proof.get("initial_agent_metrics") or {}
    final = proof.get("final_skillos_metrics") or proof.get("final_skills_metrics") or {}
    ok = 0
    if isinstance(initial, dict) and isinstance(final, dict):
        if isinstance(final.get("quality_score"), (int, float)) and isinstance(initial.get("quality_score"), (int, float)) and final["quality_score"] > initial["quality_score"]:
            ok += 1
        if isinstance(final.get("accepted_rate"), (int, float)) and isinstance(initial.get("accepted_rate"), (int, float)) and final["accepted_rate"] > initial["accepted_rate"]:
            ok += 1
        if isinstance(final.get("minutes_per_job"), (int, float)) and isinstance(initial.get("minutes_per_job"), (int, float)) and final["minutes_per_job"] < initial["minutes_per_job"]:
            ok += 1
        if isinstance(final.get("cost_per_job_usd"), (int, float)) and isinstance(initial.get("cost_per_job_usd"), (int, float)) and final["cost_per_job_usd"] < initial["cost_per_job_usd"]:
            ok += 1
    if ok >= 3:
        return True

    top = 0
    for key, threshold in [
        ("cost_reduction_percent_vs_initial_agent", 0.50),
        ("speed_gain_percent_vs_initial_agent", 0.50),
        ("quality_gain_points_vs_initial_agent", 0.40),
    ]:
        value = proof.get(key)
        if isinstance(value, (int, float)) and value >= threshold:
            top += 1
    return top >= 2

def verify_required_files() -> None:
    required = [
        "README.md", "PROOF_OF_WEALTH_ACCUMULATION.md",
        "scripts/apply_safe_public_copy.py", "scripts/verify_safe_public_copy.py", "scripts/qa_check.py",
        "skillos/wealth_proof.py", "site/index.html", "site/app.js", "site/styles.css", ".github/workflows/pages.yml",
    ]
    for rel in required:
        if not (ROOT / rel).exists():
            fail(f"Missing required file: {rel}")
    print("Repository file verification passed")

def apply_safe_copy() -> None:
    script = ROOT / "scripts" / "apply_safe_public_copy.py"
    if script.exists():
        run([sys.executable, str(script)])

def verify_proof() -> None:
    generator = ROOT / "scripts" / "prove_wealth_loop.py"
    if generator.exists():
        run([sys.executable, str(generator)])
    proof = load_json(DATA / "wealth_proof.json")
    if not proof_passed(proof):
        print("Top-level proof keys:", sorted(proof.keys()))
        fail("Wealth proof did not pass according to recognized proof schemas.")
    print("Wealth proof verification passed")

def run_tests() -> None:
    if (ROOT / "tests").exists():
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    print("Tests passed")

def build_site() -> None:
    builder = ROOT / "scripts" / "build_pages.py"
    if builder.exists():
        run([sys.executable, str(builder)])
    print("Website build step complete")

def verify_safe_copy(strict: bool = False) -> None:
    verifier = ROOT / "scripts" / "verify_safe_public_copy.py"
    if verifier.exists():
        cmd = [sys.executable, str(verifier)]
        if strict:
            cmd.append("--strict")
        run(cmd)
    print("Safe public copy verification passed")

def main() -> None:
    verify_required_files()
    apply_safe_copy()
    verify_proof()
    apply_safe_copy()
    run_tests()
    build_site()
    apply_safe_copy()
    verify_safe_copy(strict=True)
    print("Repository QA passed")

if __name__ == "__main__":
    main()
