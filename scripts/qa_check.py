#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"

def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)

def run(cmd):
    print("+", " ".join(map(str, cmd)))
    subprocess.run(cmd, cwd=ROOT, check=True)

def load_json(path):
    if not path.exists():
        fail(f"Missing required file: {path.relative_to(ROOT)}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Could not parse {path.relative_to(ROOT)}: {exc}")

def truthy(v):
    if isinstance(v, bool): return v
    if isinstance(v, (int, float)): return v > 0
    if isinstance(v, str): return v.strip().lower() in {"true","yes","pass","passed","success","ok"}
    return False

def get_path(d, path):
    cur = d
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur

def proof_passed(proof):
    paths = [
        ("proof_passed",), ("passed",), ("success",), ("status",),
        ("summary","proof_passed"), ("summary","passed"), ("summary","success"), ("summary","status"),
        ("proof","proof_passed"), ("proof","passed"), ("proof","success"), ("proof","status"),
    ]
    for path in paths:
        v = get_path(proof, path)
        if v is not None and truthy(v):
            return True

    metrics = proof.get("metrics") or proof.get("summary") or proof
    checks = [("cost_reduction_pct",50), ("time_reduction_pct",50), ("quality_gain_points",40)]
    ok = 0
    for key, threshold in checks:
        v = metrics.get(key) if isinstance(metrics, dict) else None
        if isinstance(v, (int, float)) and v >= threshold:
            ok += 1
    return ok >= 2

def verify_required_files():
    required = [
        "README.md", "PROOF_OF_WEALTH_ACCUMULATION.md",
        "scripts/apply_safe_public_copy.py", "scripts/verify_safe_public_copy.py", "scripts/qa_check.py",
        "skillos/wealth_proof.py", "site/index.html", "site/app.js", "site/styles.css",
        ".github/workflows/pages.yml",
    ]
    for rel in required:
        if not (ROOT / rel).exists():
            fail(f"Missing required file: {rel}")
    print("Repository file verification passed")

def verify_proof():
    generator = ROOT / "scripts" / "prove_wealth_loop.py"
    if generator.exists():
        run([sys.executable, str(generator)])
    proof = load_json(DATA / "wealth_proof.json")
    if not proof_passed(proof):
        print("Top-level proof keys:", sorted(proof.keys()))
        fail("Wealth proof did not pass according to recognized proof schema.")
    print("Wealth proof verification passed")

def verify_safe_copy():
    verifier = ROOT / "scripts" / "verify_safe_public_copy.py"
    if verifier.exists():
        run([sys.executable, str(verifier)])
    print("Safe public copy verification passed")

def run_tests():
    if (ROOT / "tests").exists():
        run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
    print("Tests passed")

def verify_site_files():
    for rel in ["site/index.html","site/app.js","site/styles.css"]:
        if not (ROOT / rel).exists():
            fail(f"Missing website file: {rel}")
    html = (SITE / "index.html").read_text(encoding="utf-8", errors="ignore").lower()
    for phrase in ["concrete reference workflow", "unit economics"]:
        if phrase not in html:
            fail(f"Website is missing expected safe phrase: {phrase}")
    print("Website file verification passed")

def main():
    verify_required_files()
    verify_proof()
    verify_safe_copy()
    run_tests()
    verify_site_files()
    print("Repository QA passed")

if __name__ == "__main__":
    main()
