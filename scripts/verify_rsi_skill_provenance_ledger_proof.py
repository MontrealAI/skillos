#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "data" / "rsi-skill-provenance-ledger-proof.json"

def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    raise SystemExit(1)

def main() -> None:
    if not PROOF.exists():
        fail(f"missing proof receipt: {PROOF}")
    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    required = ["proved","status","workflow","agent_system","benchmark_public","pre_registered_gates","baselines","final","comparisons","bootstrap_confidence_intervals","rsi_releases","protocol_fingerprint_sha256"]
    for key in required:
        if key not in proof:
            fail(f"missing top-level key: {key}")
    final = proof["final"]
    for key in ["benchmark_value_capture_rate_percent","frontier_correct_rate_percent","provenance_integrity_score","adversarial_skill_rejection_rate_percent","risk_breach_rate_percent","unauthorized_action_rate_percent","total_benchmark_value_at_stake_usd","total_benchmark_value_captured_usd"]:
        if key not in final:
            fail(f"missing final metric: {key}")
    if not proof["proved"]:
        fail("proved=false")
    if not all(proof["pre_registered_gates"].values()):
        fail("one or more pre-registered gates failed: " + ", ".join(k for k,v in proof["pre_registered_gates"].items() if not v))
    checks = [
        (proof["agent_system"]["virtual_specialist_agents"] >= 16_000_000, "virtual specialist agents must be >= 16M"),
        (proof["agent_system"]["specialist_roles"] >= 500_000, "specialist roles must be >= 500k"),
        (proof["benchmark_public"]["holdout_count"] >= 4096, "holdout_count must be >= 4096"),
        (proof["rsi_release_count"] >= 6, "RSI release count must be >= 6"),
        (final["benchmark_value_capture_rate_percent"] >= 99.5, "value capture must be >= 99.5%"),
        (final["frontier_correct_rate_percent"] >= 90.0, "frontier-correct must be >= 90%"),
        (final["provenance_integrity_score"] >= 99.0, "provenance integrity must be >= 99%"),
        (final["adversarial_skill_rejection_rate_percent"] >= 99.0, "adversarial skill rejection must be >= 99%"),
        (final["risk_breach_rate_percent"] == 0.0, "risk breach must be zero"),
        (proof["comparisons"]["single_generalist"]["value_capture_gain_points"] >= 30.0, "must beat single generalist by >= 30 value-capture points"),
        (proof["comparisons"]["uncoordinated_agent_pool"]["value_capture_gain_points"] >= 3.0, "must beat uncoordinated pool by >= 3 value-capture points"),
        (proof["comparisons"]["no_rsi_provenance_ledger"]["value_capture_gain_points"] >= 5.0, "must beat no-RSI provenance ledger by >= 5 value-capture points"),
        (proof["bootstrap_confidence_intervals"]["vs_no_rsi_provenance_ledger"]["p05_gain_points"] > 0.0, "bootstrap lower bound must be positive"),
    ]
    failures = [msg for ok,msg in checks if not ok]
    if failures:
        print("Skill Provenance Ledger verification failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)
    print(json.dumps({
        "status": "PASSED",
        "proof": str(PROOF.relative_to(ROOT)),
        "virtual_specialist_agents": proof["agent_system"]["virtual_specialist_agents"],
        "specialist_roles": proof["agent_system"]["specialist_roles"],
        "holdout_cases": proof["benchmark_public"]["holdout_count"],
        "rsi_releases": proof["rsi_release_count"],
        "value_capture_percent": final["benchmark_value_capture_rate_percent"],
        "provenance_integrity_percent": final["provenance_integrity_score"],
        "adversarial_skill_rejection_percent": final["adversarial_skill_rejection_rate_percent"],
        "protocol_fingerprint_sha256": proof["protocol_fingerprint_sha256"],
    }, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
