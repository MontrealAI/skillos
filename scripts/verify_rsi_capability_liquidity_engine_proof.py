#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REQUIRED_TOP_LEVEL = [
    "proof_id", "proof_title", "proof_version", "seed", "metrics", "baseline_metrics",
    "negative_controls", "bootstrap_confidence_intervals", "rsi_release_trace", "proof_gates",
    "holdout_evaluation_rows", "proof_sha256", "claim_boundary", "mechanism",
]
FORBIDDEN = [
    "achieved superintelligence", "achieved kardashev", "kardashev type ii achieved", "guaranteed wealth",
    "guaranteed roi", "audited roi", "investment advice", "legal advice", "policy advice",
    "live revenue", "customer results", "financial guarantee", "guaranteed profit", "guaranteed market value",
]


def canonical_hash(obj: dict) -> str:
    ignored = {"generated_at", "run_context", "proof_sha256"}
    reduced = {k: v for k, v in obj.items() if k not in ignored}
    blob = json.dumps(reduced, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def safe_claim_scan(text: str) -> list[str]:
    lower = text.lower()
    findings = []
    for phrase in FORBIDDEN:
        start = 0
        while True:
            idx = lower.find(phrase, start)
            if idx == -1:
                break
            prefix = lower[max(0, idx - 160):idx]
            sentence_start = max(lower.rfind(".", 0, idx), lower.rfind("\n", 0, idx)) + 1
            end_candidates = [p for p in [lower.find(".", idx), lower.find("\n", idx)] if p != -1]
            sentence_end = min(end_candidates) if end_candidates else min(len(lower), idx + 160)
            sentence = lower[sentence_start:sentence_end]
            safe_negated = "not" in sentence or "does not" in sentence or "no claim" in sentence or "not" in prefix[-100:] or "does not" in prefix[-160:] or "no " in prefix[-80:]
            if not safe_negated:
                findings.append(phrase)
            start = idx + len(phrase)
    return sorted(set(findings))


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="data/rsi-capability-liquidity-engine-proof.json")
    parser.add_argument("--markdown", default="docs/rsi-capability-liquidity-engine-proof.md")
    parser.add_argument("--html", default="site/rsi-capability-liquidity-engine-proof.html")
    args = parser.parse_args()
    path = Path(args.json)
    assert_true(path.exists(), f"missing proof json: {path}")
    proof = json.loads(path.read_text(encoding="utf-8"))

    for key in REQUIRED_TOP_LEVEL:
        assert_true(key in proof, f"missing top-level key {key}")
    assert_true(proof["proof_sha256"] == canonical_hash(proof), "proof SHA-256 mismatch")

    m = proof["metrics"]
    assert_true(m["proved"] is True, "metrics.proved must be true")
    assert_true(m["virtual_specialist_agents"] >= 2_000_000, "must use at least 2,000,000 virtual specialist agents")
    assert_true(m["specialist_roles"] >= 65_000, "must use at least 65,000 specialist roles")
    assert_true(m["capability_markets"] >= 256, "must use many capability markets")
    assert_true(m["verifier_courts"] >= 64, "must use verifier courts")
    assert_true(m["skill_release_lanes"] >= 128, "must use skill release lanes")
    assert_true(m["locked_holdout_cases"] >= 4096, "must evaluate at least 4,096 locked holdout cases")
    assert_true(m["accepted_rsi_releases"] >= 10, "must accept at least 10 RSI releases")
    assert_true(m["locked_holdout_value_capture_rate"] >= 0.90, "holdout capture must be >= 90%")
    assert_true(m["first_pass_success_rate"] >= 0.90, "first-pass verifiable success must be >= 90%")
    assert_true(m["capability_liquidity_score"] >= 0.86, "capability liquidity score must be >= 86%")
    assert_true(m["trace_compounding_score"] >= 0.80, "trace compounding score must be >= 80%")
    assert_true(m["frontier_correct_rate"] >= 0.95, "frontier-correct rate must be >= 95%")
    assert_true(m["risk_breach_rate"] <= 0.001, "risk breach rate must be <= 0.1%")
    assert_true(m["unsafe_action_rate"] == 0, "unsafe action rate must be zero")
    assert_true(m["role_quorum_pass_rate"] >= 0.995, "role quorum pass rate must be >= 99.5%")
    assert_true(m["value_over_no_rsi_marketplace"] > 2e12, "must beat no-RSI marketplace by more than $2T benchmark-capital-equivalent")
    assert_true(m["value_over_uncoordinated_agent_pool"] > 2e12, "must beat uncoordinated agent pool by more than $2T benchmark-capital-equivalent")
    assert_true(m["value_over_static_skill_catalog"] > 2e12, "must beat static skill catalog by more than $2T benchmark-capital-equivalent")
    assert_true(m["value_over_single_general_agent"] > 2e12, "must beat single general agent by more than $2T benchmark-capital-equivalent")

    gates = proof["proof_gates"]
    assert_true(gates and all(g.get("passed") for g in gates), "all proof gates must pass")
    accepted = [r for r in proof["rsi_release_trace"] if r.get("accepted")]
    assert_true(len(accepted) == m["accepted_rsi_releases"], "accepted release count mismatch")
    assert_true(accepted[-1]["release"] == m["selected_release"], "selected release must be final accepted release")
    curve = [r["validation_value_capture_rate"] for r in accepted]
    assert_true(all(curve[i] <= curve[i+1] + 1e-12 for i in range(len(curve)-1)), "accepted validation curve must be monotonic")

    controls = proof["negative_controls"]
    assert_true(controls["no_verifier_courts"]["risk_breach_rate"] > m["risk_breach_rate"], "no-verifier-courts control must increase risk")
    assert_true(controls["no_skill_release_loop"]["value_capture_rate"] < m["locked_holdout_value_capture_rate"], "no skill release loop must reduce capture")
    assert_true(controls["no_market_clearing"]["liquidity_score"] < m["capability_liquidity_score"], "no market clearing must reduce liquidity")
    assert_true(controls["no_trace_memory"]["trace_compounding_score"] < m["trace_compounding_score"], "no trace memory must reduce compounding")

    rows = proof["holdout_evaluation_rows"]
    assert_true(len(rows) == m["locked_holdout_cases"], "holdout row count mismatch")
    assert_true(all("baseline_capture_rates" in r and "frontier_correct" in r for r in rows[:10]), "holdout rows must include baseline capture rates and frontier correctness")
    for key, ci in proof["bootstrap_confidence_intervals"].items():
        assert_true(ci["p05_delta"] > 0, f"bootstrap p05 must be positive for {key}")

    for candidate in [Path(args.markdown), Path(args.html)]:
        if candidate.exists():
            findings = safe_claim_scan(candidate.read_text(encoding="utf-8", errors="ignore"))
            assert_true(not findings, f"unsafe public wording in {candidate}: {findings}")

    print(json.dumps({
        "verified": True,
        "proof_id": proof["proof_id"],
        "proof_sha256": proof["proof_sha256"],
        "selected_release": m["selected_release"],
        "holdout_value_capture_rate": round(m["locked_holdout_value_capture_rate"], 6),
        "capability_liquidity_score": round(m["capability_liquidity_score"], 6),
        "risk_breach_rate": round(m["risk_breach_rate"], 6),
        "unsafe_action_rate": round(m["unsafe_action_rate"], 6),
    }, indent=2))


if __name__ == "__main__":
    main()
