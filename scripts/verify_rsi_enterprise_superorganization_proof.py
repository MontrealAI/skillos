#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "data" / "rsi_enterprise_superorganization_proof.json"

REQUIRED_TOP_LEVEL = [
    "proved",
    "status",
    "workflow",
    "workflow_file",
    "page_url",
    "agent_system",
    "benchmark_public",
    "pre_registered_gates",
    "single_agent_baseline",
    "uncoordinated_large_agent_pool",
    "static_multi_agent_operating_committee",
    "no_rsi_large_agent_organization",
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
    "benchmark_implied_value_captured_over_no_rsi_usd",
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

    failed_gates = [k for k, v in proof["pre_registered_gates"].items() if not v]
    if failed_gates:
        fail(f"Pre-registered gates failed: {failed_gates}")

    agent_system = proof["agent_system"]
    benchmark = proof["benchmark_public"]
    final = proof["final"]
    comparisons = proof["comparisons"]
    bootstrap = proof["bootstrap_confidence_intervals"]

    checks = [
        (agent_system["agent_count"] >= 16384, "agent_count must be at least 16384"),
        (agent_system["role_count"] >= 512, "role_count must be at least 512"),
        (agent_system["governance_council_count"] >= 32, "must include at least 32 governance councils"),
        (len(benchmark["regimes"]) >= 8, "must include at least 8 enterprise regimes"),
        (benchmark["holdout_count"] >= 2048, "holdout_count must be at least 2048"),
        (proof["rsi_release_count"] >= 8, "must release at least 8 validation-gated RSI protocol updates"),
        (final["benchmark_value_capture_rate_percent"] >= 99.6, "benchmark value capture must be at least 99.6%"),
        (final["fully_correct_percent"] >= 92.0, "fully correct decision rate must be at least 92%"),
        (final["risk_breach_rate_percent"] <= proof["static_multi_agent_operating_committee"]["risk_breach_rate_percent"] + 0.10, "risk breach must not exceed static coordination by more than 0.10 points"),
        (comparisons["vs_single_agent"]["benchmark_value_capture_gain_points"] >= 10.0, "must beat single-agent value capture by at least 10 points"),
        (comparisons["vs_uncoordinated_large_agent_pool"]["benchmark_value_capture_gain_points"] >= 1.5, "must beat uncoordinated large-agent pool by at least 1.5 points"),
        (comparisons["vs_static_multi_agent_operating_committee"]["benchmark_value_capture_gain_points"] >= 0.2, "must beat static multi-agent committee by at least 0.2 points"),
        (comparisons["vs_no_rsi_large_agent_organization"]["benchmark_value_capture_gain_points"] >= 0.4, "must beat no-RSI large organization by at least 0.4 points"),
        (comparisons["vs_shuffled_reward_rsi_control"]["benchmark_value_capture_gain_points"] >= 2.0, "must beat shuffled-reward RSI control by at least 2 points"),
        (comparisons["vs_random_protocol_control"]["benchmark_value_capture_gain_points"] >= 2.0, "must beat random protocol control by at least 2 points"),
        (comparisons["vs_single_agent"]["fully_correct_gain_points"] >= 65.0, "must beat single-agent fully-correct rate by at least 65 points"),
        (comparisons["vs_single_agent"]["benchmark_value_captured_gain_usd"] >= 300_000_000_000, "must capture at least $300B benchmark value over single-agent baseline"),
        (final["total_benchmark_value_at_stake_usd"] >= 1_000_000_000_000, "benchmark value at stake must be at least $1T"),
        (bootstrap["vs_static_multi_agent_operating_committee"]["p05_gain_points"] > 0.0, "bootstrap p05 gain over static coordination must be positive"),
        (bootstrap["vs_no_rsi_large_agent_organization"]["p05_gain_points"] > 0.0, "bootstrap p05 gain over no-RSI organization must be positive"),
    ]

    failures = [message for ok, message in checks if not ok]
    if failures:
        print("Autonomous RSI Enterprise Superorganization verification failed:")
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(json.dumps({
        "status": "PASSED",
        "proof": str(PROOF.relative_to(ROOT)),
        "agents": agent_system["agent_count"],
        "roles": agent_system["role_count"],
        "governance_councils": agent_system["governance_council_count"],
        "holdout_cases": benchmark["holdout_count"],
        "rsi_releases": proof["rsi_release_count"],
        "benchmark_value_capture_percent": final["benchmark_value_capture_rate_percent"],
        "benchmark_value_captured_usd": final["total_benchmark_value_captured_usd"],
        "value_captured_over_single_agent_usd": comparisons["vs_single_agent"]["benchmark_value_captured_gain_usd"],
        "protocol_fingerprint_sha256": proof["protocol_fingerprint_sha256"],
        "page_url": proof["page_url"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
