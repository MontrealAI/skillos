#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SLUG = "rsi-ai-first-blockchain-capital-machine-proof"
REQ = [
    "holdout_value_capture",
    "frontier_correct_rate",
    "risk_breach_rate",
    "unsafe_action_rate",
    "accepted_rsi_releases",
    "value_over_single_protocol_strategist",
    "value_over_uncoordinated_agent_swarm",
    "value_over_static_dao_committee",
    "value_over_no_rsi_protocol_organization",
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    path = ROOT / "data" / f"{SLUG}.json"
    if not path.exists():
        raise SystemExit(f"missing proof receipt: {path}")
    obj = json.loads(path.read_text())
    metrics = obj.get("metrics", {})
    gates = obj.get("gate_results", {})
    missing = [k for k in REQ if k not in metrics]
    if missing:
        raise SystemExit(f"missing metrics: {missing}")
    failures = [k for k, v in gates.items() if v is not True]
    if failures:
        raise SystemExit(f"proof gates failed: {failures}")
    if metrics.get("proved") is not True:
        raise SystemExit("metrics.proved is not true")
    if metrics["virtual_specialist_agents"] < 262144 or metrics["specialist_roles"] < 8192:
        raise SystemExit("multi-agent scale below proof requirement")
    if metrics["holdout_value_capture"] < 0.965:
        raise SystemExit("holdout value capture below gate")
    if metrics["risk_breach_rate"] > 0.008 or metrics["unsafe_action_rate"] > 0.001:
        raise SystemExit("risk/unsafe gate failed")
    for k in ["value_over_single_protocol_strategist", "value_over_uncoordinated_agent_swarm", "value_over_static_dao_committee", "value_over_no_rsi_protocol_organization"]:
        if metrics[k] <= 0:
            raise SystemExit(f"non-positive superiority result: {k}")
    if obj.get("autonomy_receipt", {}).get("human_review_required") is not False:
        raise SystemExit("proof is not autonomous")
    note = obj.get("public_safety_note", "").lower()
    for phrase in ["not live protocol revenue", "not", "investment advice", "kardashev"]:
        if phrase not in note:
            raise SystemExit(f"public-safety note missing phrase: {phrase}")
    print(json.dumps({"verified": True, "proof": SLUG, "fingerprint": obj.get("protocol_fingerprint")}, indent=2))

if __name__ == "__main__":
    main()
