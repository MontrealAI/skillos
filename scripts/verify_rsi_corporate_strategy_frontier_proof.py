#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROOF = ROOT / "data" / "rsi-corporate-strategy-frontier-proof.json"
EXPECTED_SCHEMA = "skillos.rsi_corporate_strategy_frontier.proof.v6"

REQUIRED_TOP_LEVEL = [
    "schema_version", "proof_name", "slug", "proved", "summary", "final_holdout_metrics",
    "baselines", "negative_controls", "confidence", "pass_fail_gates", "rsi_releases", "mechanism", "artifacts"
]


def fail(msg: str) -> None:
    raise SystemExit(f"Corporate Strategy Frontier proof verification failed: {msg}")


def load(path: Path) -> dict:
    if not path.exists():
        fail(f"missing proof JSON: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", default=str(DEFAULT_PROOF))
    args = parser.parse_args()
    path = Path(args.proof)
    proof = load(path)

    for key in REQUIRED_TOP_LEVEL:
        if key not in proof:
            fail(f"missing top-level key: {key}")
    if proof["schema_version"] != EXPECTED_SCHEMA:
        fail(f"schema mismatch: {proof['schema_version']!r}")
    if proof["slug"] != "rsi-corporate-strategy-frontier-proof":
        fail("unexpected slug")
    if proof["proved"] is not True:
        fail("proved flag is not true")

    summary = proof["summary"]
    gates = proof["pass_fail_gates"]
    for gate, passed in gates.items():
        if passed is not True:
            fail(f"gate did not pass: {gate}")

    hard_thresholds = {
        "agents": 65536,
        "specialist_roles": 2048,
        "strategy_councils": 64,
        "locked_holdout_cases": 1536,
        "rsi_releases": 10,
    }
    for key, minimum in hard_thresholds.items():
        if summary.get(key, 0) < minimum:
            fail(f"{key} below required minimum: {summary.get(key)} < {minimum}")

    if summary["value_capture_percent"] < 98.5:
        fail("value capture below 98.5%")
    if summary["frontier_equivalent_percent"] < 90.0:
        fail("frontier-equivalent decisions below 90%")
    if summary["risk_breach_rate_percent"] > 1.0:
        fail("risk breach rate above 1%")
    for key in ["value_over_single_corporate_generalist", "value_over_uncoordinated_swarm", "value_over_static_committee", "value_over_no_rsi_organization"]:
        if summary[key] <= 0:
            fail(f"{key} is not positive")

    expected_baselines = {"single_corporate_generalist", "uncoordinated_multi_agent_swarm", "static_multi_agent_committee", "no_rsi_large_organization"}
    if set(proof["baselines"]) != expected_baselines:
        fail(f"baseline set mismatch: {set(proof['baselines'])}")
    expected_controls = {"shuffled_reward_protocol", "random_protocol", "risk_blind_coordination", "random_strategy_policy"}
    if set(proof["negative_controls"]) != expected_controls:
        fail(f"negative-control set mismatch: {set(proof['negative_controls'])}")
    final_capture = proof["final_holdout_metrics"]["value_capture_percent"]
    for name, metrics in proof["negative_controls"].items():
        if metrics["value_capture_percent"] >= final_capture:
            fail(f"negative control matched or beat final proof: {name}")

    ci = proof["confidence"]
    if ci["vs_static_multi_agent_committee"]["p05_gain_percent"] <= 0:
        fail("bootstrap p05 gain vs static committee must be positive")
    if ci["vs_uncoordinated_multi_agent_swarm"]["p05_gain_percent"] <= 0:
        fail("bootstrap p05 gain vs uncoordinated swarm must be positive")

    releases = proof["rsi_releases"]
    if len(releases) != summary["rsi_releases"] + 1:
        fail("RSI release audit trail length mismatch")
    if releases[0]["release"] != 0 or releases[-1]["release"] != summary["rsi_releases"]:
        fail("RSI release numbering mismatch")
    if not any(r["accepted"] for r in releases[1:]):
        fail("no recursive release was accepted")
    if releases[-1]["value_capture_percent"] < releases[0]["value_capture_percent"]:
        fail("final validation release regressed vs v0")

    for artifact in proof["artifacts"].values():
        rel = ROOT / artifact
        if not rel.exists() and artifact.endswith(".json"):
            fail(f"missing artifact: {artifact}")

    print(json.dumps({
        "verified": True,
        "proof": proof["proof_name"],
        "value_capture_percent": summary["value_capture_percent"],
        "frontier_equivalent_percent": summary["frontier_equivalent_percent"],
        "risk_breach_rate_percent": summary["risk_breach_rate_percent"],
        "protocol_fingerprint": summary["protocol_fingerprint"],
    }, indent=2))

if __name__ == "__main__":
    main()
