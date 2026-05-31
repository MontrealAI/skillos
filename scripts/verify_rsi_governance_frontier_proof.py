#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

REQUIRED_TOP_LEVEL = [
    "proof_id", "proof_title", "proof_version", "seed", "metrics", "baseline_metrics",
    "negative_controls", "bootstrap_confidence_intervals", "rsi_release_trace", "proof_gates",
    "holdout_evaluation_rows", "proof_sha256", "claim_boundary",
]

FORBIDDEN = [
    "achieved superintelligence", "achieved kardashev", "kardashev type ii achieved", "guaranteed wealth",
    "guaranteed roi", "audited roi", "investment advice", "legal advice", "policy advice",
    "live revenue", "customer results", "financial guarantee", "guaranteed profit",
]
ALLOWED_SAFE_CONTEXT = [
    "does not claim achieved superintelligence",
    "does not claim achieved superintelligence or kardashev",
    "does not claim achieved superintelligence, live revenue",
    "not a claim of achieved superintelligence",
    "not claim achieved superintelligence",
    "not investment advice",
    "not legal advice",
    "not policy advice",
    "not a claim of live revenue",
    "not live revenue",
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
            window = lower[max(0, idx - 60): idx + len(phrase) + 60]
            sentence_start = max(lower.rfind(".", 0, idx), lower.rfind("\n", 0, idx)) + 1
            sentence_end_candidates = [p for p in [lower.find(".", idx), lower.find("\n", idx)] if p != -1]
            sentence_end = min(sentence_end_candidates) if sentence_end_candidates else min(len(lower), idx + 160)
            sentence = lower[sentence_start:sentence_end]
            prefix = lower[max(0, idx - 160):idx]
            safe_negated = ("not" in sentence or "does not" in sentence or "no claim" in sentence or "not" in prefix[-100:] or "does not" in prefix[-160:] or "no " in prefix[-60:])
            if not safe_negated and not any(ok in window for ok in ALLOWED_SAFE_CONTEXT):
                findings.append(phrase)
            start = idx + len(phrase)
    return sorted(set(findings))


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="data/rsi-governance-frontier-proof.json")
    parser.add_argument("--markdown", default="docs/rsi-governance-frontier-proof.md")
    parser.add_argument("--html", default="site/rsi-governance-frontier-proof.html")
    args = parser.parse_args()

    proof_path = Path(args.json)
    assert_true(proof_path.exists(), f"missing proof json: {proof_path}")
    proof = json.loads(proof_path.read_text(encoding="utf-8"))

    for key in REQUIRED_TOP_LEVEL:
        assert_true(key in proof, f"missing top-level key {key}")

    expected_hash = canonical_hash(proof)
    assert_true(proof["proof_sha256"] == expected_hash, "proof SHA-256 mismatch")

    m = proof["metrics"]
    assert_true(m["proved"] is True, "metrics.proved must be true")
    assert_true(m["virtual_specialist_agents"] >= 1_000_000, "must use at least 1,000,000 virtual specialist agents")
    assert_true(m["specialist_roles"] >= 32_000, "must use at least 32,000 specialist roles")
    assert_true(m["strategy_councils"] >= 128, "must use at least 128 strategy councils")
    assert_true(m["evidence_courts"] >= 32, "must use evidence courts")
    assert_true(m["risk_courts"] >= 32, "must use risk courts")
    assert_true(m["locked_holdout_cases"] >= 4096, "must evaluate at least 4,096 locked holdout cases")
    assert_true(m["accepted_rsi_releases"] >= 8, "must accept at least 8 RSI releases")
    assert_true(m["locked_holdout_value_capture_rate"] >= 0.90, "holdout value capture must be >= 90%")
    assert_true(m["frontier_correct_rate"] >= 0.95, "frontier-correct decision rate must be >= 95%")
    assert_true(m["risk_breach_rate"] <= 0.001, "risk breach rate must be <= 0.1%")
    assert_true(m["unsafe_action_rate"] == 0, "unsafe action rate must be zero")
    assert_true(m["role_quorum_pass_rate"] >= 0.995, "role quorum pass rate must be >= 99.5%")
    assert_true(m["value_over_no_rsi_governance_org"] > 2e12, "must beat no-RSI baseline by more than $2T benchmark-capital-equivalent")
    assert_true(m["value_over_uncoordinated_agent_swarm"] > 3e12, "must beat uncoordinated swarm baseline by more than $3T benchmark-capital-equivalent")
    assert_true(m["value_over_static_dao_committee"] > 3e12, "must beat static committee baseline by more than $3T benchmark-capital-equivalent")

    gates = proof["proof_gates"]
    assert_true(gates and all(g.get("passed") for g in gates), "all proof gates must pass")

    releases = proof["rsi_release_trace"]
    accepted = [r for r in releases if r.get("accepted")]
    assert_true(len(accepted) == m["accepted_rsi_releases"], "accepted release count mismatch")
    assert_true(accepted[-1]["release"] == m["selected_release"], "selected release must be the final accepted release")
    accepted_curve = [r["validation_value_capture_rate"] for r in accepted]
    assert_true(all(accepted_curve[i] <= accepted_curve[i+1] + 1e-12 for i in range(len(accepted_curve)-1)), "accepted validation curve must be monotonic")

    controls = proof["negative_controls"]
    assert_true(controls["no_risk_courts"]["risk_breach_rate"] > m["risk_breach_rate"], "no-risk-courts negative control must increase risk")
    assert_true(controls["no_reinvestment_loop"]["value_capture_rate"] < m["locked_holdout_value_capture_rate"], "no-reinvestment negative control must reduce value capture")
    assert_true(controls["no_role_quorum"]["role_quorum_pass_rate"] < m["role_quorum_pass_rate"], "no-role-quorum negative control must reduce quorum pass rate")

    rows = proof["holdout_evaluation_rows"]
    assert_true(len(rows) == m["locked_holdout_cases"], "holdout row count mismatch")
    assert_true(all("baseline_capture_rates" in r for r in rows[:10]), "holdout rows must include baseline capture rates")

    for key, ci in proof["bootstrap_confidence_intervals"].items():
        assert_true(ci["p05_delta"] > 0, f"bootstrap lower confidence bound must be positive for {key}")

    for candidate in [Path(args.markdown), Path(args.html)]:
        if candidate.exists():
            text = candidate.read_text(encoding="utf-8", errors="ignore")
            findings = safe_claim_scan(text)
            assert_true(not findings, f"unsafe public wording in {candidate}: {findings}")

    print(json.dumps({
        "verified": True,
        "proof_id": proof["proof_id"],
        "proof_sha256": proof["proof_sha256"],
        "selected_release": m["selected_release"],
        "holdout_value_capture_rate": round(m["locked_holdout_value_capture_rate"], 6),
        "risk_breach_rate": round(m["risk_breach_rate"], 6),
        "unsafe_action_rate": round(m["unsafe_action_rate"], 6),
    }, indent=2))


if __name__ == "__main__":
    main()
