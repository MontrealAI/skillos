#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

PROOF_ID = "rsi-cross-domain-capability-transfer-atlas-proof"

def require(condition, message):
    if not condition:
        raise SystemExit(f"verification failed: {message}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root)
    path = root/"data"/f"{PROOF_ID}.json"
    require(path.exists(), f"missing {path}")
    proof = json.loads(path.read_text(encoding="utf-8"))
    m = proof["metrics"]
    b = proof["baselines"]
    require(proof["proved"] is True, "proof did not pass")
    require(proof["large_agent_coordination"]["virtual_specialist_agents"] >= 1_000_000, "agent lattice is too small")
    require(proof["large_agent_coordination"]["specialist_roles"] >= 100_000, "role lattice is too small")
    require(proof["benchmark_design"]["locked_holdout_cases"] >= 4000, "not enough locked holdout cases")
    require(proof["benchmark_design"]["no_network_calls"] is True, "must not depend on network calls")
    require(proof["benchmark_design"]["no_private_data"] is True, "must not use private data")
    require(proof["benchmark_design"]["no_human_review"] is True, "must be autonomous")
    require(m["locked_holdout_value_capture"] >= 0.85, "value capture below threshold")
    require(m["cross_domain_transfer_score"] >= 0.86, "transfer score below threshold")
    require(m["capability_liquidity_score"] >= 0.86, "liquidity score below threshold")
    require(m["frontier_correct_rate"] >= 0.95, "frontier-correct rate below threshold")
    require(m["risk_breach_rate"] == 0.0, "risk breach rate must be zero")
    require(m["unsafe_action_rate"] == 0.0, "unsafe action rate must be zero")
    require(m["locked_holdout_value_capture"] > b["static_skill_catalog"]["locked_holdout_value_capture"] + 0.25, "does not beat static skill catalog")
    require(m["locked_holdout_value_capture"] > b["uncoordinated_agent_pool"]["locked_holdout_value_capture"] + 0.30, "does not beat uncoordinated pool")
    require(m["locked_holdout_value_capture"] > b["single_generalist"]["locked_holdout_value_capture"] + 0.40, "does not beat single generalist")
    require(b["negative_shuffled_traces"]["frontier_correct_rate"] < 0.10, "shuffled-trace negative control unexpectedly passes")
    require(b["negative_release_without_verifiers"]["risk_breach_rate"] > 0.10, "verifier-free negative control unexpectedly safe")
    for rel in ["json", "markdown", "badge"]:
        out = root/proof["output_files"][rel]
        require(out.exists(), f"missing output file: {out}")
    print("Cross-domain capability transfer atlas proof verification passed.")

if __name__ == "__main__":
    main()
