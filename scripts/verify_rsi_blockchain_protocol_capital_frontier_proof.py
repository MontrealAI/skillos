from __future__ import annotations
import argparse, json, sys
from pathlib import Path

REQUIRED_TOP_LEVEL = [
    "schema_version", "proof_name", "proof_version", "slug", "generated_at", "seed", "proved",
    "methodology", "claim_boundary", "system_scale", "capital_to_capability_chain",
    "final_metrics", "baselines", "gains", "bootstrap_confidence_intervals",
    "rsi_release_history", "candidate_protocol_strategies", "protocol", "pass_fail_gates",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", default="data/rsi-blockchain-protocol-capital-frontier-proof.json")
    args = parser.parse_args()
    path = Path(args.proof)
    if not path.exists():
        print(f"ERROR: proof file not found: {path}")
        sys.exit(1)
    proof = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    for key in REQUIRED_TOP_LEVEL:
        if key not in proof:
            errors.append(f"missing top-level key: {key}")
    gates = proof.get("pass_fail_gates", {})
    for key, value in gates.items():
        if value is not True:
            errors.append(f"gate failed: {key}={value!r}")
    scale = proof.get("system_scale", {})
    if scale.get("virtual_specialist_agents", 0) < 100000:
        errors.append("virtual specialist agent count below pre-registered threshold")
    if scale.get("specialist_roles", 0) < 4000:
        errors.append("specialist role count below pre-registered threshold")
    if scale.get("accepted_rsi_releases", 0) < 6:
        errors.append("too few accepted RSI releases")
    final = proof.get("final_metrics", {})
    if final.get("value_capture", 0) < 0.97:
        errors.append("value capture below threshold")
    if final.get("frontier_correct_rate", 0) < 0.90:
        errors.append("frontier-correct rate below threshold")
    if final.get("unsafe_rate", 1) > 0:
        errors.append("unsafe action rate is nonzero")
    if final.get("risk_breach_rate", 1) > 0.01:
        errors.append("risk breach rate above threshold")
    forbidden = ["audited revenue", "guaranteed", "guarantee", "investment advice", "token recommendation", "achieved superintelligence", "Kardashev Type II achieved"]
    text = json.dumps(proof).lower()
    boundary_text = json.dumps(proof.get("claim_boundary", {}).get("does_not_claim", [])).lower()
    methodology_text = json.dumps(proof.get("methodology", {})).lower()
    for phrase in forbidden:
        ptxt = phrase.lower()
        if ptxt in text and ptxt not in boundary_text and ptxt not in methodology_text:
            errors.append(f"unsafe public-claim phrase found outside claim boundary: {phrase}")
    if errors:
        print("Blockchain protocol capital frontier verification failed:")
        for e in errors:
            print(f"- {e}")
        sys.exit(1)
    print("Blockchain protocol capital frontier verification passed")


if __name__ == "__main__":
    main()
