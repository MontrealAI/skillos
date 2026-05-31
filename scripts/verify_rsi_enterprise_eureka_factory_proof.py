#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "data" / "rsi_enterprise_eureka_factory_proof.json"

REQUIRED_TOP_LEVEL = [
    "proved",
    "status",
    "workflow",
    "agent_system",
    "benchmark_public",
    "pre_registered_gates",
    "single_agent_baseline",
    "uncoordinated_multi_agent_pool",
    "static_multi_agent_coordination",
    "negative_controls",
    "final",
    "comparisons",
    "bootstrap_confidence_intervals",
    "rsi_releases",
    "holdout_samples",
    "protocol_fingerprint_sha256",
]

REQUIRED_FINAL = [
    "benchmark_value_capture_rate_percent",
    "value_capture_rate_percent",
    "fully_correct_percent",
    "top3_percent",
    "risk_breach_rate_percent",
    "invalid_action_rate_percent",
    "total_benchmark_value_at_stake_usd",
    "total_benchmark_value_captured_usd",
    "benchmark_implied_value_captured_over_single_agent_usd",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)


def main() -> None:
    if not PROOF.exists():
        fail(f"Missing proof receipt: {PROOF}")

    proof = json.loads(PROOF.read_text(encoding="utf-8"))

    for key in REQUIRED_TOP_LEVEL:
        if key not in proof:
            fail(f"Missing top-level proof key: {key}")

    for key in REQUIRED_FINAL:
        if key not in proof["final"]:
            fail(f"Missing final metric: {key}")

    if not proof["proved"]:
        fail("Proof receipt says proved=false")

    if not all(proof["pre_registered_gates"].values()):
        failures = [key for key, value in proof["pre_registered_gates"].items() if not value]
        fail(f"Pre-registered gates failed: {failures}")

    agent_system = proof["agent_system"]
    benchmark = proof["benchmark_public"]
    final = proof["final"]
    comparisons = proof["comparisons"]
    bootstrap = proof["bootstrap_confidence_intervals"]

    checks = [
        (agent_system["agent_count"] >= 2048, "agent_count must be at least 2048"),
        (agent_system["role_count"] >= 128, "role_count must be at least 128"),
        (agent_system["governance_board_count"] >= 16, "must include at least 16 governance boards"),
        (benchmark["holdout_count"] >= 1536, "holdout_count must be at least 1536"),
        (proof["rsi_release_count"] >= 8, "must release at least 8 validation-gated RSI protocol updates"),
        (final["benchmark_value_capture_rate_percent"] >= 99.5, "benchmark value capture must be at least 99.5%"),
        (final["fully_correct_percent"] >= 90.0, "fully correct decision rate must be at least 90%"),
        (final["risk_breach_rate_percent"] <= proof["static_multi_agent_coordination"]["risk_breach_rate_percent"] + 0.10, "risk breach must not exceed static coordination by more than 0.10 points"),
        (comparisons["vs_single_agent"]["benchmark_value_capture_gain_points"] >= 15.0, "must beat single-agent value capture by at least 15 points"),
        (comparisons["vs_uncoordinated_multi_agent_pool"]["benchmark_value_capture_gain_points"] >= 4.0, "must beat uncoordinated pool value capture by at least 4 points"),
        (comparisons["vs_static_multi_agent_coordination"]["benchmark_value_capture_gain_points"] >= 0.4, "must beat static multi-agent coordination value capture by at least 0.4 points"),
        (comparisons["vs_single_agent"]["fully_correct_gain_points"] >= 60.0, "must beat single-agent fully-correct rate by at least 60 points"),
        (comparisons["vs_single_agent"]["benchmark_value_captured_gain_usd"] >= 50_000_000_000, "must capture at least $50B benchmark value over single-agent baseline"),
        (bootstrap["vs_static_multi_agent_coordination"]["p05_gain_points"] > 0.0, "bootstrap p05 gain over static coordination must be positive"),
        (proof["negative_controls"]["shuffled_reward_rsi"]["benchmark_value_capture_rate_percent"] + 2.0 < final["benchmark_value_capture_rate_percent"], "shuffled-reward RSI control must not match final proof"),
    ]

    failures = [message for ok, message in checks if not ok]
    if failures:
        print("Autonomous RSI Enterprise Eureka Factory verification failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(json.dumps({
        "status": "PASSED",
        "proof": str(PROOF.relative_to(ROOT)),
        "agents": agent_system["agent_count"],
        "roles": agent_system["role_count"],
        "governance_boards": agent_system["governance_board_count"],
        "holdout_cases": benchmark["holdout_count"],
        "rsi_releases": proof["rsi_release_count"],
        "benchmark_value_capture_percent": final["benchmark_value_capture_rate_percent"],
        "benchmark_value_captured_usd": final["total_benchmark_value_captured_usd"],
        "value_captured_over_single_agent_usd": comparisons["vs_single_agent"]["benchmark_value_captured_gain_usd"],
        "protocol_fingerprint_sha256": proof["protocol_fingerprint_sha256"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
