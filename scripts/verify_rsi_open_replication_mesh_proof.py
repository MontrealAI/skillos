#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PROOF_ID = "rsi-open-replication-mesh-proof"


def fail(message: str) -> None:
    raise SystemExit(f"verification failed: {message}")


def digest(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    root = Path.cwd()
    path = root / "data" / f"{PROOF_ID}.json"
    if not path.exists():
        fail(f"missing receipt: {path}")
    proof = json.loads(path.read_text(encoding="utf-8"))
    if proof.get("proof_id") != PROOF_ID:
        fail("proof_id mismatch")
    receipt = proof.get("receipt_sha256")
    tmp = dict(proof)
    tmp.pop("receipt_sha256", None)
    if digest(tmp) != receipt:
        fail("receipt_sha256 mismatch")
    if not proof.get("proved"):
        fail("proof did not pass")
    metrics = proof.get("metrics", {})
    gates = proof.get("gates", {})
    required_gates = [
        "locked_holdout_value_capture_at_least_90pct",
        "open_replication_score_at_least_99pct",
        "replica_consensus_rate_at_least_99pct",
        "causal_uplift_p05_positive",
        "risk_breach_zero",
        "unauthorized_action_zero",
        "receipt_tree_integrity",
        "negative_controls_small",
    ]
    for gate in required_gates:
        if gates.get(gate) is not True:
            fail(f"gate failed or missing: {gate}")
    if metrics.get("open_replication_score", 0) < 0.99:
        fail("open replication score too low")
    if metrics.get("replica_consensus_rate", 0) < 0.99:
        fail("replica consensus rate too low")
    if metrics.get("causal_uplift_vs_best_control_p05", 0) <= 0:
        fail("causal uplift p05 must be positive")
    if metrics.get("risk_breach_rate") != 0.0:
        fail("risk breach rate must be zero")
    if metrics.get("negative_control_max_abs_gain", 1) > 0.005:
        fail("negative controls are too large")
    replica = proof.get("replica_summary", {})
    tree = replica.get("receipt_tree", {})
    if tree.get("leaf_count") != replica.get("replicas_evaluated"):
        fail("receipt tree leaf count mismatch")
    if not tree.get("root") or len(tree.get("root")) != 64:
        fail("invalid receipt tree root")
    for rel in proof.get("release_curve", []):
        if rel.get("risk_breach_rate", 1) != 0.0:
            fail("release curve contains risk breach")
    for required in [
        root / "docs" / f"{PROOF_ID}.md",
        root / "docs" / "AUTONOMOUS_RSI_OPEN_REPLICATION_MESH_PROOF.md",
        root / "badges" / f"{PROOF_ID}.svg",
    ]:
        if not required.exists() or required.stat().st_size <= 20:
            fail(f"missing or small artifact: {required}")
    print(json.dumps({
        "verified": True,
        "proof_id": PROOF_ID,
        "open_replication_score": metrics["open_replication_score"],
        "replica_consensus_rate": metrics["replica_consensus_rate"],
        "causal_uplift_p05": metrics["causal_uplift_vs_best_control_p05"],
        "receipt_tree_root": tree.get("root"),
    }, indent=2))


if __name__ == "__main__":
    main()
