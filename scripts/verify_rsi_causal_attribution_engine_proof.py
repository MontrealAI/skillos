#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

PROOF_ID = "rsi-causal-attribution-engine-proof"
REQUIRED_METRICS = [
    "locked_holdout_value_capture",
    "causal_uplift_vs_best_control",
    "causal_uplift_vs_best_control_p05",
    "frontier_correct_rate",
    "risk_breach_rate",
    "unauthorized_action_rate",
    "negative_control_max_abs_gain",
    "benchmark_capital_equivalent_value_captured_trillions",
]


def fail(message: str) -> None:
    raise SystemExit(f"proof verification failed: {message}")


def digest(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def main() -> None:
    root = Path.cwd()
    path = root / "data" / f"{PROOF_ID}.json"
    if not path.exists():
        fail(f"missing proof receipt: {path}")
    proof = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(proof, dict):
        fail("receipt must be a JSON object")
    if proof.get("proof_id") != PROOF_ID:
        fail(f"proof_id mismatch: {proof.get('proof_id')!r}")
    if proof.get("title") != "Autonomous RSI Causal Attribution Engine Proof":
        fail("unexpected proof title")
    if proof.get("version") != "15.0":
        fail("unexpected version")
    if proof.get("receipt_sha256") != digest({k: v for k, v in proof.items() if k != "receipt_sha256"}):
        fail("receipt_sha256 does not match receipt contents")
    if not proof.get("proved"):
        fail("proved flag is not true")
    gates = proof.get("gates")
    if not isinstance(gates, dict) or not gates:
        fail("missing gates")
    failed = [name for name, ok in gates.items() if not ok]
    if failed:
        fail("failed gates: " + ", ".join(failed))
    metrics = proof.get("metrics")
    if not isinstance(metrics, dict):
        fail("missing metrics object")
    for key in REQUIRED_METRICS:
        if key not in metrics:
            fail(f"missing metric: {key}")
    thresholds = proof.get("thresholds")
    if not isinstance(thresholds, dict):
        fail("missing thresholds object")
    checks = {
        "locked_holdout_value_capture": metrics["locked_holdout_value_capture"] >= thresholds["min_locked_holdout_value_capture"],
        "causal_uplift_p05": metrics["causal_uplift_vs_best_control_p05"] >= thresholds["min_causal_uplift_p05"],
        "frontier_correct_rate": metrics["frontier_correct_rate"] >= thresholds["min_frontier_correct_rate"],
        "risk_breach_rate": metrics["risk_breach_rate"] <= thresholds["max_risk_breach_rate"],
        "unauthorized_action_rate": metrics["unauthorized_action_rate"] <= thresholds["max_unauthorized_action_rate"],
        "negative_control_max_abs_gain": metrics["negative_control_max_abs_gain"] <= thresholds["max_negative_control_abs_gain"],
        "trace_replayability": metrics["trace_replayability"] >= thresholds["min_trace_replayability"],
    }
    failed_checks = [k for k, ok in checks.items() if not ok]
    if failed_checks:
        fail("threshold checks failed: " + ", ".join(failed_checks))
    scale = proof.get("scale", {})
    if scale.get("virtual_specialist_agents", 0) < 33_000_000:
        fail("virtual specialist-agent lattice is too small")
    if scale.get("specialist_roles", 0) < 1_000_000:
        fail("specialist role graph is too small")
    if scale.get("locked_holdout_cases", 0) < 4096:
        fail("locked holdout case count is too small")
    for rel in ["docs/rsi-causal-attribution-engine-proof.md", "badges/rsi-causal-attribution-engine-proof.svg"]:
        if not (root / rel).exists():
            fail(f"missing generated artifact: {rel}")
    print(json.dumps({
        "verified": True,
        "proof_id": proof["proof_id"],
        "version": proof["version"],
        "selected_release": metrics["selected_release"],
        "value_capture": metrics["locked_holdout_value_capture"],
        "causal_uplift_p05": metrics["causal_uplift_vs_best_control_p05"],
        "negative_control_max_abs_gain": metrics["negative_control_max_abs_gain"],
        "receipt_sha256": proof["receipt_sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
