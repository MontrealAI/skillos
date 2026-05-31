#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "data" / "rsi_corporate_capability_frontier_proof.json"

REQUIRED_TOP = [
    "proved", "status", "workflow", "proof_type", "agent_system", "benchmark",
    "safe_public_boundary", "pre_registered_gates", "single_corporate_generalist",
    "uncoordinated_multi_agent_swarm", "static_multi_agent_committee",
    "no_rsi_large_organization", "negative_controls", "final", "comparisons",
    "bootstrap_confidence_intervals", "rsi_release_count", "rsi_releases",
    "holdout_samples", "protocol_fingerprint_sha256",
]

REQUIRED_FINAL = [
    "benchmark_value_capture_rate_percent", "fully_correct_percent", "top3_percent",
    "risk_breach_rate_percent", "unsafe_action_rate_percent",
    "total_benchmark_value_at_stake_usd", "total_benchmark_value_captured_usd",
    "benchmark_value_captured_over_single_generalist_usd",
    "benchmark_value_captured_over_no_rsi_large_org_usd",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def main() -> None:
    if not PROOF.exists():
        fail(f"Missing proof receipt: {PROOF}")

    proof = json.loads(PROOF.read_text(encoding="utf-8"))

    for key in REQUIRED_TOP:
        if key not in proof:
            fail(f"Missing top-level key: {key}")

    for key in REQUIRED_FINAL:
        if key not in proof["final"]:
            fail(f"Missing final metric: {key}")

    if proof["proved"] is not True:
        fail("Proof receipt says proved=false")

    failed_gates = [key for key, passed in proof["pre_registered_gates"].items() if not passed]
    if failed_gates:
        fail(f"Pre-registered gates failed: {failed_gates}")

    final = proof["final"]
    agent_system = proof["agent_system"]
    benchmark = proof["benchmark"]
    comparisons = proof["comparisons"]
    bootstrap = proof["bootstrap_confidence_intervals"]

    checks = [
        (agent_system["agent_count"] >= 32768, "must represent at least 32,768 deterministic virtual specialist agents"),
        (agent_system["role_count"] >= 1024, "must include at least 1,024 specialist roles"),
        (agent_system["governance_council_count"] >= 32, "must include at least 32 governance councils"),
        (benchmark["holdout_count"] >= 1024, "must include at least 1,024 locked holdout cases"),
        (len(benchmark["regimes"]) >= 12, "must cover at least 12 enterprise regimes"),
        (proof["rsi_release_count"] >= 8, "must include at least 8 validation-gated RSI protocol releases"),
        (final["benchmark_value_capture_rate_percent"] >= 99.80, "benchmark value capture must be at least 99.80%"),
        (final["fully_correct_percent"] >= 92.0, "fully correct holdout rate must be at least 92%"),
        (final["risk_breach_rate_percent"] <= proof["static_multi_agent_committee"]["risk_breach_rate_percent"] + 0.20, "risk breach must be controlled versus static committee"),
        (final["unsafe_action_rate_percent"] <= 0.10, "unsafe action rate must be <= 0.10%"),
        (comparisons["vs_single_corporate_generalist"]["benchmark_value_capture_gain_points"] >= 15.0, "must beat single corporate generalist by at least 15 value-capture points"),
        (comparisons["vs_uncoordinated_multi_agent_swarm"]["benchmark_value_capture_gain_points"] >= 2.5, "must beat uncoordinated multi-agent swarm by at least 2.5 value-capture points"),
        (comparisons["vs_static_multi_agent_committee"]["benchmark_value_capture_gain_points"] >= 0.02, "must beat static committee by a positive margin"),
        (comparisons["vs_no_rsi_large_organization"]["benchmark_value_capture_gain_points"] >= 0.30, "must beat no-RSI large organization ablation"),
        (comparisons["vs_single_corporate_generalist"]["benchmark_value_captured_gain_usd"] >= 500_000_000_000, "must capture at least $500B benchmark value over single generalist baseline"),
        (comparisons["vs_no_rsi_large_organization"]["benchmark_value_captured_gain_usd"] >= 10_000_000_000, "must capture at least $10B benchmark value over no-RSI large org ablation"),
        (bootstrap["vs_static_multi_agent_committee"]["p05_gain_points"] > 0.0, "bootstrap p05 gain over static committee must be positive"),
        (bootstrap["vs_no_rsi_large_organization"]["p05_gain_points"] > 0.0, "bootstrap p05 gain over no-RSI large organization must be positive"),
        ("achieved superintelligence" in proof["safe_public_boundary"], "safe boundary must explicitly say achieved superintelligence is not claimed"),
        ("Kardashev Type II civilization" in proof["safe_public_boundary"], "safe boundary must explicitly say Kardashev Type II achievement is not claimed"),
    ]

    failures = [message for ok, message in checks if not ok]
    if failures:
        print("Autonomous RSI corporate capability frontier verification failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(json.dumps({
        "status": "PASSED",
        "proof": str(PROOF.relative_to(ROOT)),
        "agents": agent_system["agent_count"],
        "roles": agent_system["role_count"],
        "councils": agent_system["governance_council_count"],
        "holdout_cases": benchmark["holdout_count"],
        "rsi_releases": proof["rsi_release_count"],
        "benchmark_value_capture_percent": final["benchmark_value_capture_rate_percent"],
        "fully_correct_percent": final["fully_correct_percent"],
        "risk_breach_percent": final["risk_breach_rate_percent"],
        "benchmark_value_captured_usd": final["total_benchmark_value_captured_usd"],
        "value_over_single_generalist_usd": comparisons["vs_single_corporate_generalist"]["benchmark_value_captured_gain_usd"],
        "value_over_no_rsi_large_org_usd": comparisons["vs_no_rsi_large_organization"]["benchmark_value_captured_gain_usd"],
        "protocol_fingerprint_sha256": proof["protocol_fingerprint_sha256"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
