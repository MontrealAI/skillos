#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "rsi-ai-first-governance-capital-engine-proof"
GATES = {
    "holdout_value_capture": 0.975,
    "frontier_correct_decision_rate": 0.960,
    "risk_breach_rate": 0.006,
    "unsafe_action_rate": 0.001,
    "accepted_rsi_releases": 8,
    "bootstrap_gain_vs_no_rsi_p05": 0.035,
    "bootstrap_gain_vs_uncoordinated_swarm_p05": 0.030,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    path = ROOT / "data" / f"{SLUG}.json"
    if not path.exists():
        raise SystemExit(f"missing proof receipt: {path}")
    obj = json.loads(path.read_text())
    m = obj["metrics"]
    failures = []
    if not m.get("proved"):
        failures.append("metrics.proved is false")
    if m["holdout_value_capture"] < GATES["holdout_value_capture"]:
        failures.append("holdout value capture below gate")
    if m["frontier_correct_decision_rate"] < GATES["frontier_correct_decision_rate"]:
        failures.append("frontier-correct decision rate below gate")
    if m["risk_breach_rate"] > GATES["risk_breach_rate"]:
        failures.append("risk breach rate above gate")
    if m["unsafe_action_rate"] > GATES["unsafe_action_rate"]:
        failures.append("unsafe action rate above gate")
    if m["accepted_rsi_releases"] < GATES["accepted_rsi_releases"]:
        failures.append("too few accepted RSI releases")
    if m["bootstrap_gain_vs_no_rsi_p05"] < GATES["bootstrap_gain_vs_no_rsi_p05"]:
        failures.append("lower CI gain vs no-RSI below gate")
    if m["bootstrap_gain_vs_uncoordinated_swarm_p05"] < GATES["bootstrap_gain_vs_uncoordinated_swarm_p05"]:
        failures.append("lower CI gain vs uncoordinated swarm below gate")
    if m.get("required_human_review") is not False:
        failures.append("human review is required; proof must be autonomous")
    for gate_name, gate in obj.get("proof_gates", {}).items():
        if not gate.get("pass"):
            failures.append(f"proof gate failed: {gate_name}")
    for needed in ["single_executive", "static_committee", "uncoordinated_agent_swarm", "no_rsi_governance_org", "risk_blind_speed", "random_policy", "shuffled_evidence"]:
        if needed not in obj.get("baselines", {}):
            failures.append(f"missing baseline {needed}")
    if args.strict:
        if len(obj.get("rsi_release_curve", [])) < 17:
            failures.append("strict: RSI release curve incomplete")
        if not obj.get("sample_locked_holdout_decisions"):
            failures.append("strict: missing holdout decision examples")
        if "large specialist-agent governance lattice" not in obj.get("large_multi_agent_coordination_claim", ""):
            failures.append("strict: missing large multi-agent coordination wording")
    if failures:
        print(json.dumps({"verified": False, "failures": failures}, indent=2))
        raise SystemExit(1)
    print(json.dumps({
        "verified": True,
        "proved": m["proved"],
        "holdout_value_capture": m["holdout_value_capture"],
        "frontier_correct_decision_rate": m["frontier_correct_decision_rate"],
        "risk_breach_rate": m["risk_breach_rate"],
        "unsafe_action_rate": m["unsafe_action_rate"],
        "accepted_rsi_releases": m["accepted_rsi_releases"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
