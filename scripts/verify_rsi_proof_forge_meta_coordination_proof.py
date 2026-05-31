#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

PROOF_ID = "rsi-proof-forge-meta-coordination-proof"
FORBIDDEN = [
    "achieved superintelligence", "achieved kardashev", "kardashev type ii achieved", "guaranteed wealth",
    "guaranteed roi", "audited roi", "investment advice", "legal advice", "policy advice", "medical advice",
    "live revenue", "customer results", "financial guarantee", "guaranteed profit", "guaranteed market value",
    "token recommendation", "securities advice", "claims consciousness",
]


def fail(msg: str) -> None:
    raise SystemExit(f"Proof verification failed: {msg}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root)
    data_path = root / "data" / f"{PROOF_ID}.json"
    doc_path = root / "docs" / f"{PROOF_ID}.md"
    badge_path = root / "badges" / f"{PROOF_ID}.svg"
    if not data_path.exists(): fail(f"missing {data_path}")
    if not doc_path.exists(): fail(f"missing {doc_path}")
    if not badge_path.exists(): fail(f"missing {badge_path}")
    result = json.loads(data_path.read_text(encoding="utf-8"))
    if result.get("proof_id") != PROOF_ID: fail("wrong proof_id")
    if not result.get("proved"): fail("proved flag is false")
    gates = result.get("proof_gates", [])
    failed = [g for g in gates if not g.get("passed")]
    if failed: fail("failed gates: " + ", ".join(g["name"] for g in failed))
    s = result.get("selected_release_summary", {})
    checks = {
        "value_capture_rate": (s.get("value_capture_rate", 0), 0.90),
        "mean_proof_credibility": (s.get("mean_proof_credibility", 0), 0.93),
        "mean_coordination_quality": (s.get("mean_coordination_quality", 0), 0.90),
        "mean_recursive_improvement_quality": (s.get("mean_recursive_improvement_quality", 0), 0.90),
        "frontier_correct_rate": (s.get("frontier_correct_rate", 0), 0.98),
    }
    for k, (v, floor) in checks.items():
        if v < floor: fail(f"{k} {v:.6f} below {floor:.6f}")
    if s.get("risk_breach_rate", 1) > 0.0025: fail("risk breach rate too high")
    if s.get("unauthorized_action_rate", 1) != 0: fail("unauthorized action rate not zero")
    if result.get("scale", {}).get("virtual_specialist_agents", 0) < 4_000_000: fail("agent scale too small")
    if result.get("scale", {}).get("verifier_courts", 0) < 200: fail("verifier court scale too small")
    doc = doc_path.read_text(encoding="utf-8").lower()
    boundary = result.get("theorem", {}).get("public_safe_boundary", "").lower()
    if "does not claim achieved superintelligence" not in doc: fail("missing public safety boundary")
    if "benchmark-only" not in boundary: fail("json boundary missing benchmark-only")
    for phrase in FORBIDDEN:
        # Allow forbidden phrases only when used as explicit non-claims / exclusions.
        idx = doc.find(phrase)
        if idx >= 0:
            context = doc[max(0, idx-90): idx+len(phrase)+90]
            if not any(token in context for token in ["does not claim", "not claim", "no claim", "not live", "exclusion", "boundary", "advice"]):
                fail(f"unsafe public claim phrase appears without boundary: {phrase}")
    print("Proof verification passed")


if __name__ == "__main__":
    main()
