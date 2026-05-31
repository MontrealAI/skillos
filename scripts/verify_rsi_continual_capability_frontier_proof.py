#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / "data" / "rsi-continual-capability-frontier-proof.json"

def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)

def main() -> None:
    if not PROOF.exists():
        fail(f"Missing proof receipt: {PROOF}")

    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    required = [
        "proved", "status", "workflow", "agent_system", "benchmark_public",
        "pre_registered_gates", "baselines_and_controls", "final",
        "comparisons", "bootstrap_confidence_intervals", "rsi_releases",
        "protocol_fingerprint_sha256",
    ]
    for key in required:
        if key not in proof:
            fail(f"Missing key: {key}")

    if not proof["proved"]:
        fail("Proof receipt says proved=false")

    failed_gates = [k for k, v in proof["pre_registered_gates"].items() if not v]
    if failed_gates:
        fail(f"Pre-registered gates failed: {failed_gates}")

    final = proof["final"]
    agent_system = proof["agent_system"]
    checks = [
        (agent_system["virtual_specialist_agents"] >= 67_000_000, "virtual specialist agents must be at least 67M"),
        (agent_system["specialist_roles"] >= 2_000_000, "specialist roles must be at least 2M"),
        (proof["benchmark_public"]["locked_holdout_count"] >= 1536, "locked holdout must be at least 1536"),
        (proof["rsi_release_count"] >= 10, "must have at least 10 released RSI updates"),
        (final["value_capture_rate_percent"] >= 95.0, "value capture must be at least 95%"),
        (final["minimum_regime_value_capture_percent"] >= 86.0, "minimum regime capture must be at least 86%"),
        (final["catastrophic_forgetting_rate_percent"] == 0.0, "catastrophic forgetting must be zero"),
        (final["risk_breach_rate_percent"] == 0.0, "risk breach must be zero"),
        (final["unauthorized_action_rate_percent"] == 0.0, "unauthorized action must be zero"),
        (proof["bootstrap_confidence_intervals"]["vs_strongest_control"]["p05_gain_points"] > 0.0, "bootstrap p05 gain over strongest control must be positive"),
    ]
    failures = [msg for ok, msg in checks if not ok]
    if failures:
        for msg in failures:
            print(f"- {msg}")
        raise SystemExit(1)

    print(json.dumps({
        "status": "PASSED",
        "proof": str(PROOF.relative_to(ROOT)),
        "virtual_specialist_agents": agent_system["virtual_specialist_agents"],
        "specialist_roles": agent_system["specialist_roles"],
        "rsi_release_count": proof["rsi_release_count"],
        "value_capture_percent": final["value_capture_rate_percent"],
        "minimum_regime_value_capture_percent": final["minimum_regime_value_capture_percent"],
        "catastrophic_forgetting_percent": final["catastrophic_forgetting_rate_percent"],
        "risk_breach_percent": final["risk_breach_rate_percent"],
    }, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
