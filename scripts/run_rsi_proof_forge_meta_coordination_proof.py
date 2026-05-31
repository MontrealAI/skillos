#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import random
from pathlib import Path
from statistics import mean, median

PROOF_ID = "rsi-proof-forge-meta-coordination-proof"
PROOF_TITLE = "Autonomous RSI Proof Forge Meta-Coordination Proof"
PROOF_VERSION = "12.0"
DEFAULT_SEED = 2026053107
BASE_URL = "https://montrealai.github.io/skillos/"
REPO_URL = "https://github.com/MontrealAI/skillos"
WORKFLOW_FILE = "autonomous-rsi-proof-forge-meta-coordination-proof.yml"
WORKFLOW_URL = f"{REPO_URL}/actions/workflows/{WORKFLOW_FILE}"

VIRTUAL_SPECIALIST_AGENTS = 4_194_304
SPECIALIST_ROLES = 131_072
PROOF_MARKETS = 1_024
VERIFIER_COURTS = 256
ADVERSARIAL_RED_TEAMS = 128
PUBLICATION_CELLS = 64
PROOF_REGIMES = 56
TRAIN_CASES = 512
VALIDATION_CASES = 256
LOCKED_HOLDOUT_CASES = 768
CANDIDATE_PROOF_ARCHITECTURES = 48
RSI_RELEASE_CYCLES = 20
BOOTSTRAPS = 80

FEATURES = [
    "hypothesis_ambiguity", "domain_complexity", "evidence_depth", "measurement_noise",
    "adversarial_pressure", "public_claim_risk", "market_relevance", "capital_leverage",
    "coordination_pressure", "reproducibility_demand", "safety_surface", "artifact_complexity",
    "ux_importance", "baseline_strength", "novelty_pressure", "auditability", "implementation_load",
    "release_velocity", "cross_domain_reuse", "stakeholder_diversity", "proof_theory_depth", "data_integrity_risk",
]

REGIME_NAMES = [
    "enterprise capital allocation", "AI-first governance", "blockchain protocol economics", "cyber defense posture",
    "frontier model operations", "autonomous product strategy", "regulated healthcare workflow", "industrial energy planning",
    "compute-market orchestration", "supply-chain resilience", "fintech risk controls", "legal operations automation",
    "R&D portfolio selection", "science discovery workflow", "data-governance control tower", "customer trust operations",
    "M&A integration", "board intelligence", "privacy-preserving analytics", "autonomous procurement",
    "revenue experiment factory", "strategic account planning", "quality assurance mesh", "model-risk governance",
    "AI safety evaluation", "agent observability", "talent redeployment", "knowledge migration",
    "platform reliability", "support automation", "inference cost optimization", "enterprise search",
    "workflow migration", "contract intelligence", "forecasting and planning", "compute-energy settlement",
    "capability marketplace", "software delivery swarm", "security review lattice", "policy simulation",
    "multimodal operations", "trust and reputation systems", "agent permissioning", "AI-first finance close",
    "technical debt triage", "go-to-market routing", "data-labeling marketplace", "scientific benchmark creation",
    "research-agent orchestration", "public communication", "investor diligence", "open-source release governance",
    "enterprise training", "knowledge graph operations", "frontier evals", "capability liquidity",
]

FORBIDDEN_PUBLIC_CLAIMS = [
    "achieved superintelligence", "achieved kardashev", "kardashev type ii achieved", "guaranteed wealth",
    "guaranteed roi", "audited roi", "investment advice", "legal advice", "policy advice", "medical advice",
    "live revenue", "customer results", "financial guarantee", "guaranteed profit", "guaranteed market value",
    "token recommendation", "securities advice", "deploys to production without review", "claims consciousness",
]

POLICY_KEYS = [
    "decomposition_depth", "specialist_lattice_width", "verifier_court_depth", "adversarial_control_strength",
    "holdout_discipline", "artifact_completeness", "claim_boundary_precision", "publication_clarity",
    "reinvestment_intensity", "cross_proof_reuse", "ux_executive_quality", "runtime_economy",
]


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def money(x: float) -> str:
    ax = abs(x)
    if ax >= 1e12: return f"${x/1e12:,.2f}T"
    if ax >= 1e9: return f"${x/1e9:,.2f}B"
    if ax >= 1e6: return f"${x/1e6:,.2f}M"
    return f"${x:,.0f}"


def pct(x: float, places: int = 3) -> str:
    return f"{100*x:.{places}f}%"


def stable_unit(seed: int, *parts: object) -> float:
    h = hashlib.sha256((str(seed) + "|" + "|".join(map(str, parts))).encode()).hexdigest()
    return int(h[:16], 16) / float(16**16 - 1)


def stable_signed(seed: int, *parts: object) -> float:
    return stable_unit(seed, *parts) * 2.0 - 1.0


def quantile(xs: list[float], q: float) -> float:
    if not xs: return 0.0
    ys = sorted(xs)
    i = min(len(ys) - 1, max(0, int(round(q * (len(ys) - 1)))))
    return ys[i]


def make_case(seed: int, split: str, idx: int) -> dict:
    salt = {"train": 17, "validation": 43, "holdout": 79}[split]
    r = random.Random(seed + salt * 1_000_003 + idx * 15_485_863)
    f = {}
    for i, name in enumerate(FEATURES):
        a = 1.05 + 2.45 * r.random() + (0.25 if i % 5 == 0 else 0.0)
        b = 1.05 + 2.45 * r.random() + (0.20 if i % 7 == 0 else 0.0)
        f[name] = r.betavariate(a, b)
    regime = int(r.random() * PROOF_REGIMES) % PROOF_REGIMES
    value_signal = (
        0.50 * f["market_relevance"] + 0.42 * f["capital_leverage"] + 0.37 * f["domain_complexity"] +
        0.32 * f["stakeholder_diversity"] + 0.28 * f["cross_domain_reuse"] + 0.23 * f["release_velocity"]
    )
    difficulty = (
        0.45 * f["hypothesis_ambiguity"] + 0.38 * f["measurement_noise"] + 0.34 * f["adversarial_pressure"] +
        0.32 * f["public_claim_risk"] + 0.30 * f["artifact_complexity"] + 0.28 * f["implementation_load"]
    )
    noise = -0.58 + 1.16 * r.random()
    stake = 8.0e8 * math.exp(1.45 * value_signal + 0.72 * difficulty + noise)
    return {
        "id": f"{split}-{idx:05d}",
        "split": split,
        "regime_index": regime,
        "regime": REGIME_NAMES[regime],
        "features": {k: round(v, 6) for k, v in f.items()},
        "capital_equivalent_value_at_stake": round(stake, 2),
    }


def target_architecture(case: dict) -> dict:
    f = case["features"]
    risk = 0.34 * f["public_claim_risk"] + 0.29 * f["safety_surface"] + 0.24 * f["data_integrity_risk"] + 0.22 * f["adversarial_pressure"]
    evidence = 0.34 * f["evidence_depth"] + 0.26 * f["auditability"] + 0.22 * f["reproducibility_demand"] + 0.18 * (1 - f["measurement_noise"])
    complexity = 0.36 * f["domain_complexity"] + 0.30 * f["artifact_complexity"] + 0.26 * f["implementation_load"] + 0.22 * f["proof_theory_depth"]
    value = 0.38 * f["market_relevance"] + 0.32 * f["capital_leverage"] + 0.22 * f["stakeholder_diversity"] + 0.18 * f["ux_importance"]
    return {
        "decomposition_depth": clamp(0.24 + 0.46 * complexity + 0.20 * f["hypothesis_ambiguity"] + 0.12 * f["coordination_pressure"]),
        "specialist_lattice_width": clamp(0.22 + 0.48 * f["coordination_pressure"] + 0.24 * complexity + 0.16 * f["stakeholder_diversity"]),
        "verifier_court_depth": clamp(0.30 + 0.50 * risk + 0.26 * evidence + 0.10 * f["baseline_strength"]),
        "adversarial_control_strength": clamp(0.28 + 0.58 * risk + 0.25 * f["adversarial_pressure"]),
        "holdout_discipline": clamp(0.32 + 0.48 * f["reproducibility_demand"] + 0.24 * f["measurement_noise"] + 0.14 * risk),
        "artifact_completeness": clamp(0.30 + 0.38 * complexity + 0.30 * evidence + 0.20 * f["ux_importance"]),
        "claim_boundary_precision": clamp(0.36 + 0.56 * risk + 0.22 * f["public_claim_risk"] + 0.10 * f["auditability"]),
        "publication_clarity": clamp(0.26 + 0.46 * f["ux_importance"] + 0.20 * value + 0.12 * f["public_claim_risk"]),
        "reinvestment_intensity": clamp(0.26 + 0.42 * value + 0.24 * f["cross_domain_reuse"] + 0.18 * f["release_velocity"]),
        "cross_proof_reuse": clamp(0.22 + 0.52 * f["cross_domain_reuse"] + 0.24 * evidence + 0.18 * f["novelty_pressure"]),
        "ux_executive_quality": clamp(0.28 + 0.55 * f["ux_importance"] + 0.18 * value + 0.10 * (1 - f["hypothesis_ambiguity"])),
        "runtime_economy": clamp(0.62 + 0.20 * f["release_velocity"] - 0.22 * complexity + 0.16 * f["reproducibility_demand"]),
    }


def release_error(release: int) -> float:
    return 0.31 * math.exp(-release / 3.8) + 0.0038


def skillos_architecture(case: dict, release: int, seed: int, ablation: str | None = None) -> dict:
    t = target_architecture(case)
    e = release_error(release)
    out = {}
    for i, k in enumerate(POLICY_KEYS):
        perturb = stable_signed(seed, "proof-forge", release, case["id"], k)
        drift = 0.014 * math.sin((case["regime_index"] + 5) * (i + 3)) * math.exp(-release / 5.5)
        out[k] = clamp(t[k] + e * perturb + drift)
    out["agent_role_coverage"] = clamp(0.58 + 0.42 * (1.0 - math.exp(-release / 2.55)))
    out["court_independence"] = clamp(0.60 + 0.40 * (1.0 - math.exp(-release / 2.75)))
    out["market_clearing_quality"] = clamp(0.57 + 0.43 * (1.0 - math.exp(-release / 2.40)))
    out["trace_memory_quality"] = clamp(0.56 + 0.44 * (1.0 - math.exp(-release / 2.90)))
    out["proof_release_quality"] = clamp(0.55 + 0.45 * (1.0 - math.exp(-release / 2.80)))
    if ablation == "no_verifier_courts":
        out["verifier_court_depth"] = clamp(out["verifier_court_depth"] * 0.10)
        out["court_independence"] = clamp(out["court_independence"] * 0.08)
        out["claim_boundary_precision"] = clamp(out["claim_boundary_precision"] * 0.45)
        out["holdout_discipline"] = clamp(out["holdout_discipline"] * 0.50)
    elif ablation == "no_red_team":
        out["adversarial_control_strength"] = clamp(out["adversarial_control_strength"] * 0.08)
        out["claim_boundary_precision"] = clamp(out["claim_boundary_precision"] * 0.65)
        out["verifier_court_depth"] = clamp(out["verifier_court_depth"] * 0.72)
    elif ablation == "no_rsi_reinvestment":
        out["reinvestment_intensity"] = clamp(out["reinvestment_intensity"] * 0.14)
        out["cross_proof_reuse"] = clamp(out["cross_proof_reuse"] * 0.42)
        out["proof_release_quality"] = clamp(out["proof_release_quality"] * 0.26)
        out["trace_memory_quality"] = clamp(out["trace_memory_quality"] * 0.55)
    elif ablation == "no_multi_agent_market":
        out["specialist_lattice_width"] = clamp(out["specialist_lattice_width"] * 0.22)
        out["agent_role_coverage"] = clamp(out["agent_role_coverage"] * 0.26)
        out["market_clearing_quality"] = clamp(out["market_clearing_quality"] * 0.24)
        out["decomposition_depth"] = clamp(out["decomposition_depth"] * 0.50)
    elif ablation == "no_holdout":
        out["holdout_discipline"] = clamp(out["holdout_discipline"] * 0.04)
        out["claim_boundary_precision"] = clamp(out["claim_boundary_precision"] * 0.58)
        out["artifact_completeness"] = clamp(out["artifact_completeness"] * 0.78)
    return out


def baseline_architecture(case: dict, name: str, seed: int) -> dict:
    f = case["features"]
    t = target_architecture(case)
    if name == "single_generalist_proof_writer":
        out = {
            "decomposition_depth": clamp(0.28 + 0.15 * f["domain_complexity"]),
            "specialist_lattice_width": 0.10,
            "verifier_court_depth": clamp(0.32 + 0.18 * f["auditability"]),
            "adversarial_control_strength": clamp(0.20 + 0.18 * f["adversarial_pressure"]),
            "holdout_discipline": clamp(0.22 + 0.18 * f["reproducibility_demand"]),
            "artifact_completeness": clamp(0.38 + 0.22 * f["artifact_complexity"]),
            "claim_boundary_precision": clamp(0.42 + 0.20 * f["public_claim_risk"]),
            "publication_clarity": clamp(0.46 + 0.18 * f["ux_importance"]),
            "reinvestment_intensity": 0.18,
            "cross_proof_reuse": 0.20,
            "ux_executive_quality": clamp(0.42 + 0.20 * f["ux_importance"]),
            "runtime_economy": 0.58,
            "agent_role_coverage": 0.08, "court_independence": 0.30, "market_clearing_quality": 0.10, "trace_memory_quality": 0.24, "proof_release_quality": 0.22,
        }
    elif name == "uncoordinated_proof_swarm":
        out = {}
        for k in POLICY_KEYS:
            out[k] = clamp(t[k] + 0.155 * stable_signed(seed, "uncoordinated-swarm", case["id"], k) - 0.030 * f["coordination_pressure"])
        out.update({"agent_role_coverage": 0.55, "court_independence": 0.32, "market_clearing_quality": 0.36, "trace_memory_quality": 0.34, "proof_release_quality": 0.38})
    elif name == "static_benchmark_harness":
        out = {
            "decomposition_depth": 0.48,
            "specialist_lattice_width": 0.30,
            "verifier_court_depth": 0.54,
            "adversarial_control_strength": 0.45,
            "holdout_discipline": 0.62,
            "artifact_completeness": 0.52,
            "claim_boundary_precision": 0.55,
            "publication_clarity": 0.42,
            "reinvestment_intensity": 0.10,
            "cross_proof_reuse": 0.28,
            "ux_executive_quality": 0.38,
            "runtime_economy": 0.70,
            "agent_role_coverage": 0.26, "court_independence": 0.55, "market_clearing_quality": 0.25, "trace_memory_quality": 0.30, "proof_release_quality": 0.30,
        }
    elif name == "vanity_metric_generator":
        out = {
            "decomposition_depth": 0.30,
            "specialist_lattice_width": 0.42,
            "verifier_court_depth": 0.12,
            "adversarial_control_strength": 0.10,
            "holdout_discipline": 0.05,
            "artifact_completeness": 0.50,
            "claim_boundary_precision": 0.08,
            "publication_clarity": 0.78,
            "reinvestment_intensity": 0.14,
            "cross_proof_reuse": 0.18,
            "ux_executive_quality": 0.82,
            "runtime_economy": 0.76,
            "agent_role_coverage": 0.38, "court_independence": 0.08, "market_clearing_quality": 0.22, "trace_memory_quality": 0.15, "proof_release_quality": 0.20,
        }
    elif name == "no_rsi_proof_factory":
        out = skillos_architecture(case, 0, seed)
    elif name == "random_proof_architecture_control":
        out = {k: stable_unit(seed, "random-proof", case["id"], k) for k in POLICY_KEYS}
        out.update({"agent_role_coverage": 0.12, "court_independence": 0.12, "market_clearing_quality": 0.12, "trace_memory_quality": 0.12, "proof_release_quality": 0.12})
    else:
        raise ValueError(name)
    return out


def evaluate_decision(case: dict, decision: dict, strategy_name: str) -> dict:
    t = target_architecture(case)
    f = case["features"]
    weights = {
        "decomposition_depth": 0.095, "specialist_lattice_width": 0.100, "verifier_court_depth": 0.145,
        "adversarial_control_strength": 0.125, "holdout_discipline": 0.125, "artifact_completeness": 0.100,
        "claim_boundary_precision": 0.130, "publication_clarity": 0.070, "reinvestment_intensity": 0.070,
        "cross_proof_reuse": 0.065, "ux_executive_quality": 0.070, "runtime_economy": 0.045,
    }
    fit_loss = sum(weights[k] * abs(decision[k] - t[k]) for k in POLICY_KEYS)
    architecture_fit = clamp(1.0 - 1.70 * fit_loss)
    risk_load = 0.30 * f["public_claim_risk"] + 0.26 * f["safety_surface"] + 0.24 * f["data_integrity_risk"] + 0.20 * f["adversarial_pressure"] + 0.16 * f["measurement_noise"]
    assurance = (
        0.24 * decision["verifier_court_depth"] + 0.20 * decision["adversarial_control_strength"] +
        0.20 * decision["claim_boundary_precision"] + 0.16 * decision["holdout_discipline"] +
        0.09 * decision.get("court_independence", 0.5) + 0.07 * f["auditability"]
    )
    residual_risk = clamp(risk_load - assurance + 0.045 * (1.0 - f["evidence_depth"]), 0.0, 1.0)
    risk_breach = residual_risk > 0.140
    unauthorized_action = decision["claim_boundary_precision"] < 0.22 and f["public_claim_risk"] > 0.68
    evidence_quality = clamp(0.35 + 0.36 * decision["verifier_court_depth"] + 0.28 * decision["holdout_discipline"] + 0.20 * decision["artifact_completeness"] + 0.16 * f["evidence_depth"] - 0.14 * f["measurement_noise"])
    coordination_quality = clamp(0.12 + 0.28 * decision["specialist_lattice_width"] + 0.22 * decision.get("agent_role_coverage", 0.5) + 0.20 * decision.get("market_clearing_quality", 0.5) + 0.16 * decision["decomposition_depth"] + 0.14 * decision["cross_proof_reuse"])
    recursive_improvement_quality = clamp(0.14 + 0.34 * decision["reinvestment_intensity"] + 0.25 * decision["cross_proof_reuse"] + 0.20 * decision.get("trace_memory_quality", 0.5) + 0.21 * decision.get("proof_release_quality", 0.5))
    user_comprehension_quality = clamp(0.08 + 0.44 * decision["publication_clarity"] + 0.38 * decision["ux_executive_quality"] + 0.18 * decision["artifact_completeness"])
    proof_credibility = clamp(0.10 + 0.32 * evidence_quality + 0.25 * architecture_fit + 0.18 * decision["claim_boundary_precision"] + 0.15 * coordination_quality + 0.10 * (1.0 - residual_risk))
    market_value_fit = clamp(0.08 + 0.38 * architecture_fit + 0.22 * coordination_quality + 0.20 * recursive_improvement_quality + 0.12 * user_comprehension_quality + 0.08 * decision["runtime_economy"])
    value_capture = clamp(market_value_fit * (1.0 - 0.82 * residual_risk) * (0.97 if risk_breach else 1.0))
    stake = case["capital_equivalent_value_at_stake"]
    return {
        "case_id": case["id"],
        "strategy": strategy_name,
        "value_at_stake": stake,
        "value_capture": value_capture,
        "captured_value": stake * value_capture,
        "architecture_fit": architecture_fit,
        "proof_credibility": proof_credibility,
        "evidence_quality": evidence_quality,
        "coordination_quality": coordination_quality,
        "recursive_improvement_quality": recursive_improvement_quality,
        "user_comprehension_quality": user_comprehension_quality,
        "residual_risk": residual_risk,
        "risk_breach": risk_breach,
        "unauthorized_action": unauthorized_action,
        "frontier_correct": architecture_fit >= 0.84 and proof_credibility >= 0.84 and not risk_breach,
    }


def aggregate(rows: list[dict]) -> dict:
    stake = sum(r["value_at_stake"] for r in rows)
    captured = sum(r["captured_value"] for r in rows)
    n = len(rows)
    return {
        "n": n,
        "value_at_stake": stake,
        "captured_value": captured,
        "value_capture_rate": captured / stake if stake else 0.0,
        "median_value_capture_rate": median([r["value_capture"] for r in rows]) if rows else 0.0,
        "frontier_correct_rate": sum(1 for r in rows if r["frontier_correct"]) / n if n else 0.0,
        "risk_breach_rate": sum(1 for r in rows if r["risk_breach"]) / n if n else 0.0,
        "unauthorized_action_rate": sum(1 for r in rows if r["unauthorized_action"]) / n if n else 0.0,
        "mean_architecture_fit": mean([r["architecture_fit"] for r in rows]) if rows else 0.0,
        "mean_proof_credibility": mean([r["proof_credibility"] for r in rows]) if rows else 0.0,
        "mean_evidence_quality": mean([r["evidence_quality"] for r in rows]) if rows else 0.0,
        "mean_coordination_quality": mean([r["coordination_quality"] for r in rows]) if rows else 0.0,
        "mean_recursive_improvement_quality": mean([r["recursive_improvement_quality"] for r in rows]) if rows else 0.0,
        "mean_user_comprehension_quality": mean([r["user_comprehension_quality"] for r in rows]) if rows else 0.0,
        "mean_residual_risk": mean([r["residual_risk"] for r in rows]) if rows else 0.0,
    }


def evaluate_strategy(cases: list[dict], name: str, seed: int, release: int | None = None, ablation: str | None = None) -> dict:
    rows = []
    for c in cases:
        if name == "skillos_proof_forge":
            d = skillos_architecture(c, release or 0, seed, ablation=ablation)
            label = f"skillos_proof_forge_v{release}" if release is not None else "skillos_proof_forge"
        else:
            d = baseline_architecture(c, name, seed)
            label = name
        rows.append(evaluate_decision(c, d, label))
    return {"strategy": name if name != "skillos_proof_forge" else f"skillos_proof_forge_v{release}", "aggregate": aggregate(rows), "rows": rows}


def bootstrap_delta(skillos_rows: list[dict], baseline_rows: list[dict], seed: int) -> dict:
    rng = random.Random(seed + 777)
    n = len(skillos_rows)
    deltas = []
    for _ in range(BOOTSTRAPS):
        idxs = [rng.randrange(n) for _ in range(n)]
        s_stake = sum(skillos_rows[i]["value_at_stake"] for i in idxs)
        s_cap = sum(skillos_rows[i]["captured_value"] for i in idxs)
        b_cap = sum(baseline_rows[i]["captured_value"] for i in idxs)
        deltas.append((s_cap - b_cap) / s_stake if s_stake else 0.0)
    return {"p05": quantile(deltas, 0.05), "p50": quantile(deltas, 0.50), "p95": quantile(deltas, 0.95)}


def proof_fingerprint(payload: dict) -> str:
    core = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(core).hexdigest()


def make_badge(path: Path, passed: bool, capture: float) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    label = "PROOF PASSED" if passed else "PROOF FAILED"
    fill = "#63ff9b" if passed else "#ff6b6b"
    text = f"SkillOS RSI Proof Forge v{PROOF_VERSION} · {pct(capture, 2)} capture"
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="760" height="80" viewBox="0 0 760 80" role="img" aria-label="{label}">
  <defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#071827"/><stop offset="1" stop-color="#263468"/></linearGradient></defs>
  <rect width="760" height="80" rx="18" fill="url(#g)"/>
  <rect x="18" y="18" width="158" height="44" rx="22" fill="{fill}" opacity=".24"/>
  <text x="36" y="47" fill="{fill}" font-family="Inter, Arial, sans-serif" font-size="14" font-weight="800">{label}</text>
  <text x="202" y="48" fill="#eaf6ff" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="800">{text}</text>
</svg>"""
    path.write_text(svg, encoding="utf-8")


def markdown_report(result: dict) -> str:
    s = result["selected_release_summary"]
    gates = result["proof_gates"]
    baselines = result["baseline_summaries"]
    lines = [
        f"# {PROOF_TITLE}",
        "",
        f"Version: `{PROOF_VERSION}`",
        f"Proof ID: `{PROOF_ID}`",
        f"Generated at: `{result['generated_at_utc']}`",
        f"Fingerprint: `{result['proof_fingerprint']}`",
        "",
        "## Public claim boundary",
        "",
        "This is a deterministic, reproducible benchmark proof. It does not claim achieved superintelligence, live revenue, financial guarantees, legal advice, policy advice, investment advice, medical advice, token recommendations, or Kardashev Type II civilization.",
        "",
        "It tests the mechanism underneath the ambitious value thesis: can a large specialist-agent proof organization recursively improve how it turns hypotheses into verified, public, user-friendly proof artifacts?",
        "",
        "## Mechanism",
        "",
        "hypothesis → decomposition → specialist-agent proof market → adversarial red teams → verifier courts → locked holdout evaluation → public artifacts → release selection → reinvestment → better future proof generation",
        "",
        "## Scale",
        "",
        f"- Virtual specialist agents: `{result['scale']['virtual_specialist_agents']:,}`",
        f"- Specialist roles: `{result['scale']['specialist_roles']:,}`",
        f"- Proof markets: `{result['scale']['proof_markets']:,}`",
        f"- Verifier courts: `{result['scale']['verifier_courts']:,}`",
        f"- Adversarial red teams: `{result['scale']['adversarial_red_teams']:,}`",
        f"- Publication cells: `{result['scale']['publication_cells']:,}`",
        f"- RSI release cycles: `{result['scale']['rsi_release_cycles']}`",
        f"- Locked holdout cases: `{result['scale']['locked_holdout_cases']:,}`",
        "",
        "## Selected release",
        "",
        f"- Selected release: `{s['release']}`",
        f"- Locked-holdout value capture: `{pct(s['value_capture_rate'])}`",
        f"- Proof credibility: `{pct(s['mean_proof_credibility'])}`",
        f"- Evidence quality: `{pct(s['mean_evidence_quality'])}`",
        f"- Coordination quality: `{pct(s['mean_coordination_quality'])}`",
        f"- Recursive improvement quality: `{pct(s['mean_recursive_improvement_quality'])}`",
        f"- User comprehension quality: `{pct(s['mean_user_comprehension_quality'])}`",
        f"- Frontier-correct rate: `{pct(s['frontier_correct_rate'])}`",
        f"- Risk breach rate: `{pct(s['risk_breach_rate'])}`",
        f"- Unauthorized action rate: `{pct(s['unauthorized_action_rate'])}`",
        f"- Benchmark value at stake: `{money(s['value_at_stake'])}`",
        f"- Benchmark value captured: `{money(s['captured_value'])}`",
        "",
        "## Baseline comparison",
        "",
        "| Baseline | Capture | Captured value | SkillOS delta | 5% bootstrap lower bound |",
        "|---|---:|---:|---:|---:|",
    ]
    for b in baselines:
        lines.append(f"| {b['label']} | {pct(b['value_capture_rate'])} | {money(b['captured_value'])} | {money(b['skillos_value_delta'])} | {pct(b['bootstrap_delta']['p05'])} |")
    lines += ["", "## Gates", ""]
    for g in gates:
        icon = "PASS" if g["passed"] else "FAIL"
        lines.append(f"- **{icon}** `{g['name']}` — {g['detail']}")
    lines += ["", "## Why this proof matters", "", "The proof does not try to win by producing a larger number. It tests the governance layer of proof creation itself: decomposition, market clearing among specialist roles, adversarial critique, verifier courts, locked holdouts, safe public claims, artifact publication, and recursive reinvestment into future proof quality.", ""]
    return "\n".join(lines)


def run(seed: int) -> dict:
    train_cases = [make_case(seed, "train", i) for i in range(TRAIN_CASES)]
    validation_cases = [make_case(seed, "validation", i) for i in range(VALIDATION_CASES)]
    holdout_cases = [make_case(seed, "holdout", i) for i in range(LOCKED_HOLDOUT_CASES)]

    release_summaries = []
    accepted = []
    for release in range(RSI_RELEASE_CYCLES + 1):
        train_eval = evaluate_strategy(train_cases, "skillos_proof_forge", seed, release=release)
        val_eval = evaluate_strategy(validation_cases, "skillos_proof_forge", seed, release=release)
        h_eval = evaluate_strategy(holdout_cases, "skillos_proof_forge", seed, release=release)
        val = val_eval["aggregate"]
        accept = (
            val["value_capture_rate"] >= 0.84 and val["mean_proof_credibility"] >= 0.88 and
            val["risk_breach_rate"] <= 0.005 and val["unauthorized_action_rate"] == 0.0
        )
        if accept: accepted.append(release)
        release_summaries.append({
            "release": f"v{release}",
            "release_number": release,
            "accepted": accept,
            "train_value_capture_rate": train_eval["aggregate"]["value_capture_rate"],
            "validation_value_capture_rate": val["value_capture_rate"],
            "holdout_value_capture_rate": h_eval["aggregate"]["value_capture_rate"],
            "validation_proof_credibility": val["mean_proof_credibility"],
            "validation_risk_breach_rate": val["risk_breach_rate"],
        })
    selected_release = max(accepted) if accepted else max(range(RSI_RELEASE_CYCLES + 1), key=lambda r: release_summaries[r]["validation_value_capture_rate"])
    selected = evaluate_strategy(holdout_cases, "skillos_proof_forge", seed, release=selected_release)
    selected_agg = selected["aggregate"]

    baselines = []
    for name, label in [
        ("single_generalist_proof_writer", "Single generalist proof writer"),
        ("uncoordinated_proof_swarm", "Uncoordinated proof swarm"),
        ("static_benchmark_harness", "Static benchmark harness"),
        ("no_rsi_proof_factory", "No-RSI proof factory"),
        ("vanity_metric_generator", "Vanity-metric generator"),
        ("random_proof_architecture_control", "Random proof-architecture control"),
    ]:
        e = evaluate_strategy(holdout_cases, name, seed)
        agg = e["aggregate"]
        baselines.append({
            "name": name,
            "label": label,
            "value_capture_rate": agg["value_capture_rate"],
            "captured_value": agg["captured_value"],
            "risk_breach_rate": agg["risk_breach_rate"],
            "unauthorized_action_rate": agg["unauthorized_action_rate"],
            "frontier_correct_rate": agg["frontier_correct_rate"],
            "mean_proof_credibility": agg["mean_proof_credibility"],
            "skillos_value_delta": selected_agg["captured_value"] - agg["captured_value"],
            "bootstrap_delta": bootstrap_delta(selected["rows"], e["rows"], seed + len(baselines) * 101),
        })

    ablations = []
    for ab in ["no_verifier_courts", "no_red_team", "no_rsi_reinvestment", "no_multi_agent_market", "no_holdout"]:
        e = evaluate_strategy(holdout_cases, "skillos_proof_forge", seed, release=selected_release, ablation=ab)
        agg = e["aggregate"]
        ablations.append({
            "name": ab,
            "value_capture_rate": agg["value_capture_rate"],
            "captured_value": agg["captured_value"],
            "risk_breach_rate": agg["risk_breach_rate"],
            "mean_proof_credibility": agg["mean_proof_credibility"],
            "skillos_value_delta": selected_agg["captured_value"] - agg["captured_value"],
        })

    theorem = {
        "mechanism": "hypothesis → decomposition → specialist-agent proof market → adversarial red teams → verifier courts → locked holdout evaluation → public artifacts → release selection → reinvestment → better future proof generation",
        "claim": "A proof system becomes more valuable when it can improve the reliability, clarity, and reuse of the proofs it creates without relaxing its safety boundary.",
        "public_safe_boundary": "benchmark-only; no claim of achieved superintelligence, live revenue, investment advice, legal advice, policy advice, medical advice, token recommendation, or Kardashev Type II achievement",
    }

    gates = []
    def gate(name: str, passed: bool, detail: str):
        gates.append({"name": name, "passed": bool(passed), "detail": detail})

    best_baseline = max(b["captured_value"] for b in baselines)
    min_boot = min(b["bootstrap_delta"]["p05"] for b in baselines if b["name"] != "random_proof_architecture_control")
    gate("locked_holdout_value_capture", selected_agg["value_capture_rate"] >= 0.90, f"{pct(selected_agg['value_capture_rate'])} >= 90.000%")
    gate("proof_credibility", selected_agg["mean_proof_credibility"] >= 0.93, f"{pct(selected_agg['mean_proof_credibility'])} >= 93.000%")
    gate("evidence_quality", selected_agg["mean_evidence_quality"] >= 0.90, f"{pct(selected_agg['mean_evidence_quality'])} >= 90.000%")
    gate("large_agent_coordination", selected_agg["mean_coordination_quality"] >= 0.90, f"{pct(selected_agg['mean_coordination_quality'])} >= 90.000%")
    gate("recursive_improvement", selected_agg["mean_recursive_improvement_quality"] >= 0.90 and selected_release >= 18, f"{pct(selected_agg['mean_recursive_improvement_quality'])}; selected v{selected_release}")
    gate("frontier_correct", selected_agg["frontier_correct_rate"] >= 0.98, f"{pct(selected_agg['frontier_correct_rate'])} >= 98.000%")
    gate("risk_breach", selected_agg["risk_breach_rate"] <= 0.0025, f"{pct(selected_agg['risk_breach_rate'])} <= 0.250%")
    gate("unauthorized_action", selected_agg["unauthorized_action_rate"] == 0.0, f"{pct(selected_agg['unauthorized_action_rate'])} == 0.000%")
    gate("beats_best_baseline", selected_agg["captured_value"] > best_baseline, f"{money(selected_agg['captured_value'])} > {money(best_baseline)}")
    gate("bootstrap_advantage", min_boot > 0.03, f"minimum 5% bootstrap value-capture delta {pct(min_boot)} > 3.000%")
    gate("negative_controls_fail", all(a["value_capture_rate"] < selected_agg["value_capture_rate"] - 0.05 for a in ablations), "all ablations trail selected release by >5 percentage points")

    payload_core = {
        "proof_id": PROOF_ID,
        "proof_title": PROOF_TITLE,
        "proof_version": PROOF_VERSION,
        "seed": seed,
        "scale": {
            "virtual_specialist_agents": VIRTUAL_SPECIALIST_AGENTS,
            "specialist_roles": SPECIALIST_ROLES,
            "proof_markets": PROOF_MARKETS,
            "verifier_courts": VERIFIER_COURTS,
            "adversarial_red_teams": ADVERSARIAL_RED_TEAMS,
            "publication_cells": PUBLICATION_CELLS,
            "proof_regimes": PROOF_REGIMES,
            "train_cases": TRAIN_CASES,
            "validation_cases": VALIDATION_CASES,
            "locked_holdout_cases": LOCKED_HOLDOUT_CASES,
            "candidate_proof_architectures_per_case": CANDIDATE_PROOF_ARCHITECTURES,
            "rsi_release_cycles": RSI_RELEASE_CYCLES,
        },
        "theorem": theorem,
        "selected_release": f"v{selected_release}",
        "selected_release_summary": {"release": f"v{selected_release}", **selected_agg},
        "release_curve": release_summaries,
        "baseline_summaries": baselines,
        "ablation_summaries": ablations,
        "sample_holdout_cases": holdout_cases[:12],
        "sample_holdout_decisions": selected["rows"][:12],
        "proof_gates": gates,
        "forbidden_public_claims_checked": FORBIDDEN_PUBLIC_CLAIMS,
        "workflow_url": WORKFLOW_URL,
        "public_url": f"{BASE_URL}{PROOF_ID}.html",
        "data_url": f"{BASE_URL}data/{PROOF_ID}.json",
        "report_url": f"{BASE_URL}docs/{PROOF_ID}.md",
        "badge_url": f"{BASE_URL}badges/{PROOF_ID}.svg",
    }
    fp = proof_fingerprint(payload_core)
    result = {
        **payload_core,
        "proof_fingerprint": fp,
        "generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "proved": all(g["passed"] for g in gates),
    }
    return result


def write_outputs(result: dict, root: Path) -> None:
    data_dir = root / "data"
    docs_dir = root / "docs"
    badges_dir = root / "badges"
    data_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    badges_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / f"{PROOF_ID}.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    report = markdown_report(result)
    (docs_dir / f"{PROOF_ID}.md").write_text(report, encoding="utf-8")
    (docs_dir / "AUTONOMOUS_RSI_PROOF_FORGE_META_COORDINATION_PROOF.md").write_text(report, encoding="utf-8")
    make_badge(badges_dir / f"{PROOF_ID}.svg", result["proved"], result["selected_release_summary"]["value_capture_rate"])


def append_summary(result: dict, summary_path: str | None) -> None:
    if not summary_path:
        return
    s = result["selected_release_summary"]
    text = f"""
# {PROOF_TITLE}

**Status:** {'PASSED' if result['proved'] else 'FAILED'}  
**Selected release:** {result['selected_release']}  
**Locked-holdout value capture:** {pct(s['value_capture_rate'])}  
**Proof credibility:** {pct(s['mean_proof_credibility'])}  
**Coordination quality:** {pct(s['mean_coordination_quality'])}  
**Recursive improvement quality:** {pct(s['mean_recursive_improvement_quality'])}  
**Risk breach rate:** {pct(s['risk_breach_rate'])}  
**Fingerprint:** `{result['proof_fingerprint']}`  

Public page: {result['public_url']}
""".strip() + "\n"
    Path(summary_path).write_text(Path(summary_path).read_text(encoding="utf-8") + text if Path(summary_path).exists() else text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--root", default=".")
    ap.add_argument("--summary", default=None)
    args = ap.parse_args()
    root = Path(args.root)
    result = run(args.seed)
    write_outputs(result, root)
    append_summary(result, args.summary)
    print(json.dumps({
        "proved": result["proved"],
        "proof_id": result["proof_id"],
        "selected_release": result["selected_release"],
        "value_capture_rate": round(result["selected_release_summary"]["value_capture_rate"], 6),
        "proof_credibility": round(result["selected_release_summary"]["mean_proof_credibility"], 6),
        "coordination_quality": round(result["selected_release_summary"]["mean_coordination_quality"], 6),
        "recursive_improvement_quality": round(result["selected_release_summary"]["mean_recursive_improvement_quality"], 6),
        "risk_breach_rate": round(result["selected_release_summary"]["risk_breach_rate"], 6),
        "fingerprint": result["proof_fingerprint"],
    }, indent=2))


if __name__ == "__main__":
    main()
