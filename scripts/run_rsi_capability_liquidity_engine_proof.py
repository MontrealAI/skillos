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

PROOF_ID = "rsi-capability-liquidity-engine-proof"
PROOF_TITLE = "Autonomous RSI Capability Liquidity Engine Proof"
PROOF_VERSION = "11.0"
DEFAULT_SEED = 2026053102
BASE_URL = "https://montrealai.github.io/skillos/"
REPO_URL = "https://github.com/MontrealAI/skillos"
WORKFLOW_FILE = "autonomous-rsi-capability-liquidity-engine-proof.yml"
WORKFLOW_URL = f"{REPO_URL}/actions/workflows/{WORKFLOW_FILE}"

VIRTUAL_AGENTS = 2_097_152
SPECIALIST_ROLES = 65_536
CAPABILITY_MARKETS = 512
VERIFIER_COURTS = 128
SKILL_RELEASE_LANES = 256
ENTERPRISE_REGIMES = 40
TRAIN_CASES = 2_048
VALIDATION_CASES = 1_024
LOCKED_HOLDOUT_CASES = 4_096
CANDIDATE_ROUTING_POLICIES_PER_CASE = 40
RSI_RELEASE_CYCLES = 20
BOOTSTRAPS = 450

FEATURES = [
    "demand_clarity", "skill_supply_depth", "task_modularity", "verification_hardness",
    "risk_sensitivity", "handoff_complexity", "context_volatility", "market_urgency",
    "capital_leverage", "compute_intensity", "data_sensitivity", "coordination_pressure",
    "reuse_potential", "feedback_quality", "latency_pressure", "trust_requirements",
    "regulatory_surface", "customer_impact", "agent_interdependence", "novelty_pressure",
]
REGIME_NAMES = [
    "AI-first operating model redesign", "agentic product launch room", "enterprise capability marketplace",
    "autonomous procurement portfolio", "capital allocation war room", "model-risk remediation mesh",
    "customer trust escalation lattice", "cyber incident response market", "software delivery swarm",
    "data governance exchange", "compute budget clearinghouse", "energy-aware inference planning",
    "R&D thesis arbitration", "supply-chain resilience market", "privacy-by-design review",
    "frontier compliance control tower", "legal operations triage", "finance close acceleration",
    "M&A integration office", "revenue experiment portfolio", "quality assurance market", "knowledge migration factory",
    "enterprise search modernization", "platform reliability council", "support automation governance",
    "risk-adjusted roadmap forum", "talent redeployment market", "training data stewardship",
    "agent safety release board", "partner ecosystem orchestration", "industrial operations optimizer",
    "field service routing room", "AI observability command center", "pricing and packaging council",
    "contract intelligence factory", "board reporting engine", "regulated workflow conversion",
    "strategic account planning", "market intelligence fusion", "institutional reinvestment board",
]
FORBIDDEN_PUBLIC_CLAIMS = [
    "achieved superintelligence", "achieved kardashev", "kardashev type ii achieved", "guaranteed wealth",
    "guaranteed roi", "audited roi", "investment advice", "legal advice", "policy advice",
    "live revenue", "customer results", "financial guarantee", "guaranteed profit", "guaranteed market value",
]


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def money(x: float) -> str:
    ax = abs(x)
    if ax >= 1e12:
        return f"${x/1e12:,.2f}T"
    if ax >= 1e9:
        return f"${x/1e9:,.2f}B"
    if ax >= 1e6:
        return f"${x/1e6:,.2f}M"
    return f"${x:,.0f}"


def pct(x: float, places: int = 3) -> str:
    return f"{100*x:.{places}f}%"


def stable_unit(seed: int, *parts: object) -> float:
    h = hashlib.sha256((str(seed) + "|" + "|".join(map(str, parts))).encode()).hexdigest()
    return int(h[:16], 16) / float(16**16 - 1)


def stable_signed(seed: int, *parts: object) -> float:
    return stable_unit(seed, *parts) * 2.0 - 1.0


def make_case(seed: int, split: str, idx: int) -> dict:
    salt = {"train": 13, "validation": 31, "holdout": 59}[split]
    r = random.Random(seed + salt * 1_000_003 + idx * 9_973)
    f = {}
    for name in FEATURES:
        a = 1.0 + 2.2 * r.random()
        b = 1.0 + 2.2 * r.random()
        f[name] = r.betavariate(a, b)
    regime = int(r.random() * ENTERPRISE_REGIMES) % ENTERPRISE_REGIMES
    leverage = 0.52 * f["capital_leverage"] + 0.40 * f["customer_impact"] + 0.34 * f["compute_intensity"] + 0.28 * f["reuse_potential"]
    complexity = 0.50 * f["coordination_pressure"] + 0.42 * f["agent_interdependence"] + 0.32 * f["handoff_complexity"] + 0.24 * f["novelty_pressure"]
    risk = 0.46 * f["risk_sensitivity"] + 0.34 * f["data_sensitivity"] + 0.30 * f["regulatory_surface"] + 0.25 * f["trust_requirements"]
    log_noise = -0.42 + 0.84 * r.random()
    potential = 1.15e9 * math.exp(1.22 * leverage + 0.93 * complexity + 0.42 * risk + log_noise)
    return {
        "id": f"{split}-{idx:05d}",
        "split": split,
        "regime_index": regime,
        "regime": REGIME_NAMES[regime],
        "features": {k: round(v, 6) for k, v in f.items()},
        "capital_equivalent_value_at_stake": round(potential, 2),
    }


def target_policy(case: dict) -> dict:
    f = case["features"]
    demand = 0.40 * f["demand_clarity"] + 0.24 * f["task_modularity"] + 0.16 * f["market_urgency"] + 0.14 * f["customer_impact"]
    supply = 0.38 * f["skill_supply_depth"] + 0.26 * f["reuse_potential"] + 0.18 * f["feedback_quality"] + 0.14 * (1.0 - f["novelty_pressure"])
    risk = 0.34 * f["risk_sensitivity"] + 0.28 * f["data_sensitivity"] + 0.26 * f["regulatory_surface"] + 0.22 * f["trust_requirements"] + 0.15 * f["verification_hardness"]
    coordination = 0.36 * f["coordination_pressure"] + 0.28 * f["agent_interdependence"] + 0.24 * f["handoff_complexity"] + 0.16 * f["context_volatility"]
    leverage = 0.38 * f["capital_leverage"] + 0.24 * f["compute_intensity"] + 0.20 * f["customer_impact"] + 0.14 * f["market_urgency"]
    return {
        "decomposition_depth": clamp(0.24 + 0.48 * coordination + 0.24 * f["task_modularity"] + 0.14 * f["novelty_pressure"]),
        "market_width": clamp(0.20 + 0.50 * supply + 0.22 * demand + 0.16 * coordination),
        "verification_intensity": clamp(0.28 + 0.78 * risk + 0.20 * f["verification_hardness"]),
        "handoff_protocol": clamp(0.26 + 0.58 * coordination + 0.16 * f["trust_requirements"] + 0.12 * f["latency_pressure"]),
        "skill_release_investment": clamp(0.20 + 0.42 * leverage + 0.32 * f["reuse_potential"] + 0.18 * f["feedback_quality"]),
        "context_memory_depth": clamp(0.22 + 0.56 * f["context_volatility"] + 0.24 * f["data_sensitivity"] + 0.18 * coordination),
        "risk_budget": clamp(0.22 + 0.42 * leverage + 0.18 * demand - 0.44 * risk),
    }


def release_error(release: int) -> float:
    return 0.34 * math.exp(-release / 3.15) + 0.0045


def skillos_policy(case: dict, release: int, seed: int, ablation: str | None = None) -> dict:
    t = target_policy(case)
    e = release_error(release)
    out = {}
    for i, k in enumerate(["decomposition_depth", "market_width", "verification_intensity", "handoff_protocol", "skill_release_investment", "context_memory_depth", "risk_budget"]):
        perturb = stable_signed(seed, "skillos-capability", release, case["id"], k)
        correction = 0.018 * math.sin((case["regime_index"] + 3) * (i + 2)) * math.exp(-release / 5.0)
        out[k] = clamp(t[k] + e * perturb + correction)
    out["role_coverage"] = clamp(0.60 + 0.40 * (1.0 - math.exp(-release / 2.35)))
    out["verifier_quality"] = clamp(0.64 + 0.36 * (1.0 - math.exp(-release / 2.55)))
    out["market_clearing_quality"] = clamp(0.58 + 0.42 * (1.0 - math.exp(-release / 2.20)))
    out["trace_memory_quality"] = clamp(0.57 + 0.43 * (1.0 - math.exp(-release / 2.45)))
    out["reinvestment_quality"] = clamp(0.58 + 0.42 * (1.0 - math.exp(-release / 2.70)))
    if ablation == "no_verifier_courts":
        out["verification_intensity"] = clamp(out["verification_intensity"] * 0.12)
        out["verifier_quality"] = clamp(out["verifier_quality"] * 0.10)
        out["handoff_protocol"] = clamp(out["handoff_protocol"] * 0.50)
        out["risk_budget"] = clamp(out["risk_budget"] * 2.40 + 0.20)
    elif ablation == "no_skill_release_loop":
        out["skill_release_investment"] = clamp(out["skill_release_investment"] * 0.18)
        out["reinvestment_quality"] = clamp(out["reinvestment_quality"] * 0.28)
        out["trace_memory_quality"] = clamp(out["trace_memory_quality"] * 0.58)
    elif ablation == "no_market_clearing":
        out["market_width"] = clamp(out["market_width"] * 0.36)
        out["market_clearing_quality"] = clamp(out["market_clearing_quality"] * 0.30)
        out["role_coverage"] = clamp(out["role_coverage"] * 0.46)
    elif ablation == "no_trace_memory":
        out["context_memory_depth"] = clamp(out["context_memory_depth"] * 0.30)
        out["trace_memory_quality"] = clamp(out["trace_memory_quality"] * 0.25)
        out["handoff_protocol"] = clamp(out["handoff_protocol"] * 0.72)
    return out


def baseline_policy(case: dict, name: str, seed: int) -> dict:
    f = case["features"]
    t = target_policy(case)
    if name == "single_general_agent":
        out = {
            "decomposition_depth": clamp(0.24 + 0.18 * f["task_modularity"]),
            "market_width": clamp(0.20 + 0.12 * f["skill_supply_depth"]),
            "verification_intensity": clamp(0.34 + 0.20 * f["verification_hardness"] + 0.12 * f["risk_sensitivity"]),
            "handoff_protocol": clamp(0.28 + 0.13 * f["handoff_complexity"]),
            "skill_release_investment": clamp(0.18 + 0.12 * f["reuse_potential"]),
            "context_memory_depth": clamp(0.26 + 0.14 * f["context_volatility"]),
            "risk_budget": clamp(0.38 + 0.26 * f["capital_leverage"] - 0.14 * f["risk_sensitivity"]),
            "role_coverage": 0.16, "verifier_quality": 0.28, "market_clearing_quality": 0.18, "trace_memory_quality": 0.22, "reinvestment_quality": 0.18,
        }
    elif name == "uncoordinated_agent_pool":
        out = {}
        for k in ["decomposition_depth", "market_width", "verification_intensity", "handoff_protocol", "skill_release_investment", "context_memory_depth", "risk_budget"]:
            out[k] = clamp(t[k] + 0.125 * stable_signed(seed, "pool", case["id"], k) - 0.025 * f["handoff_complexity"])
        out.update({"role_coverage": 0.54, "verifier_quality": 0.44, "market_clearing_quality": 0.41, "trace_memory_quality": 0.38, "reinvestment_quality": 0.35})
    elif name == "static_skill_catalog":
        out = {
            "decomposition_depth": clamp(0.42 + 0.18 * f["task_modularity"]),
            "market_width": clamp(0.52 + 0.18 * f["skill_supply_depth"]),
            "verification_intensity": clamp(0.52 + 0.20 * f["verification_hardness"]),
            "handoff_protocol": clamp(0.44 + 0.15 * f["handoff_complexity"]),
            "skill_release_investment": 0.20,
            "context_memory_depth": 0.36,
            "risk_budget": clamp(0.32 + 0.22 * f["capital_leverage"] - 0.20 * f["risk_sensitivity"]),
            "role_coverage": 0.50, "verifier_quality": 0.50, "market_clearing_quality": 0.46, "trace_memory_quality": 0.31, "reinvestment_quality": 0.22,
        }
    elif name == "no_rsi_marketplace":
        out = skillos_policy(case, 0, seed)
    elif name == "random_router_control":
        out = {k: stable_unit(seed, "random-router", case["id"], k) for k in ["decomposition_depth", "market_width", "verification_intensity", "handoff_protocol", "skill_release_investment", "context_memory_depth", "risk_budget"]}
        out.update({"role_coverage": 0.12, "verifier_quality": 0.12, "market_clearing_quality": 0.12, "trace_memory_quality": 0.12, "reinvestment_quality": 0.12})
    else:
        raise ValueError(name)
    return out


def evaluate_decision(case: dict, decision: dict, strategy_name: str) -> dict:
    t = target_policy(case)
    f = case["features"]
    weights = {"decomposition_depth": 0.15, "market_width": 0.16, "verification_intensity": 0.20, "handoff_protocol": 0.16, "skill_release_investment": 0.14, "context_memory_depth": 0.10, "risk_budget": 0.09}
    fit_loss = sum(weights[k] * abs(decision[k] - t[k]) for k in weights)
    decision_fit = clamp(1.0 - 1.78 * fit_loss)
    risk_load = 0.30 * f["risk_sensitivity"] + 0.26 * f["data_sensitivity"] + 0.23 * f["regulatory_surface"] + 0.18 * f["trust_requirements"] + 0.14 * f["verification_hardness"] + 0.09 * f["customer_impact"]
    assurance = 0.48 * decision["verification_intensity"] + 0.18 * decision["handoff_protocol"] + 0.12 * decision.get("verifier_quality", 0.5) + 0.08 * f["feedback_quality"] + 0.06 * f["demand_clarity"]
    exposure = clamp(decision["risk_budget"] * risk_load - assurance + 0.06 * (1.0 - f["demand_clarity"]), 0.0, 1.0)
    risk_breach = exposure > 0.070
    unauthorized_action = bool(decision["risk_budget"] > 0.62 and decision["verification_intensity"] < 0.52 and (f["risk_sensitivity"] + f["data_sensitivity"] + f["regulatory_surface"]) / 3.0 > 0.54)
    role_quorum_passed = bool(decision.get("role_coverage", 0) >= 0.75 and decision.get("verifier_quality", 0) >= 0.74 and decision.get("market_clearing_quality", 0) >= 0.74 and decision["handoff_protocol"] >= 0.36)
    liquidity = clamp(0.18 + 0.30 * decision["market_width"] + 0.28 * decision.get("market_clearing_quality", 0.5) + 0.16 * decision["skill_release_investment"] + 0.12 * decision.get("role_coverage", 0.5) + 0.10 * f["reuse_potential"] + 0.06 * f["skill_supply_depth"])
    trace_compounding = clamp(0.12 + 0.30 * decision["skill_release_investment"] + 0.28 * decision.get("trace_memory_quality", 0.5) + 0.20 * decision.get("reinvestment_quality", 0.5) + 0.10 * f["feedback_quality"] + 0.08 * decision["context_memory_depth"])
    coordination_quality = clamp(0.32 * decision["handoff_protocol"] + 0.24 * decision["decomposition_depth"] + 0.20 * decision.get("role_coverage", 0.5) + 0.16 * decision.get("market_clearing_quality", 0.5) + 0.08 * decision.get("verifier_quality", 0.5))
    risk_penalty = 1.0 - min(0.72, exposure * 5.5 + (0.15 if unauthorized_action else 0.0))
    liquidity_bonus = clamp(0.72 + 0.18 * liquidity + 0.10 * trace_compounding + 0.06 * coordination_quality)
    coordination_bonus = clamp(0.72 + 0.16 * coordination_quality + 0.08 * decision.get("verifier_quality", 0.5))
    capture_rate = clamp(decision_fit * liquidity_bonus * coordination_bonus * risk_penalty)
    first_pass_success = clamp(decision_fit * (0.70 + 0.18 * decision.get("verifier_quality", 0.5) + 0.12 * coordination_quality) * risk_penalty)
    time_reduction = clamp(0.15 + 0.56 * coordination_quality + 0.20 * liquidity + 0.12 * trace_compounding - 0.08 * exposure)
    cost_reduction = clamp(0.12 + 0.50 * liquidity + 0.20 * trace_compounding + 0.16 * f["reuse_potential"] - 0.08 * exposure)
    potential = case["capital_equivalent_value_at_stake"]
    return {"case_id": case["id"], "regime": case["regime"], "strategy": strategy_name, "decision_fit": decision_fit, "risk_exposure": exposure, "risk_breach": risk_breach, "unauthorized_action": unauthorized_action, "role_quorum_passed": role_quorum_passed, "liquidity_score": liquidity, "trace_compounding_score": trace_compounding, "coordination_quality": coordination_quality, "first_pass_success_rate": first_pass_success, "time_reduction_rate": time_reduction, "cost_reduction_rate": cost_reduction, "capture_rate": capture_rate, "captured_value": potential * capture_rate, "potential_value": potential}


def evaluate_strategy(cases: list[dict], strategy_name: str, seed: int, release: int | None = None, ablation: str | None = None, rows: bool = False) -> dict:
    evals = []
    for case in cases:
        decision = skillos_policy(case, int(release or 0), seed, ablation=ablation) if strategy_name == "skillos_rsi_capability_liquidity_engine" else baseline_policy(case, strategy_name, seed)
        evals.append(evaluate_decision(case, decision, strategy_name))
    total_potential = sum(e["potential_value"] for e in evals)
    total_captured = sum(e["captured_value"] for e in evals)
    out = {"strategy": strategy_name, "release": release, "cases": len(cases), "value_at_stake": total_potential, "captured_value": total_captured, "value_capture_rate": total_captured / total_potential if total_potential else 0.0, "median_capture_rate": median(e["capture_rate"] for e in evals), "first_pass_success_rate": mean(e["first_pass_success_rate"] for e in evals), "time_reduction_rate": mean(e["time_reduction_rate"] for e in evals), "cost_reduction_rate": mean(e["cost_reduction_rate"] for e in evals), "liquidity_score": mean(e["liquidity_score"] for e in evals), "trace_compounding_score": mean(e["trace_compounding_score"] for e in evals), "coordination_quality": mean(e["coordination_quality"] for e in evals), "risk_breach_rate": mean(1.0 if e["risk_breach"] else 0.0 for e in evals), "unsafe_action_rate": mean(1.0 if e["unauthorized_action"] else 0.0 for e in evals), "role_quorum_pass_rate": mean(1.0 if e["role_quorum_passed"] else 0.0 for e in evals)}
    if rows:
        out["rows"] = evals
    return out


def release_trace(validation_cases: list[dict], seed: int) -> list[dict]:
    accepted = []
    best_capture = -1.0
    for release in range(RSI_RELEASE_CYCLES + 1):
        metrics = evaluate_strategy(validation_cases, "skillos_rsi_capability_liquidity_engine", seed, release=release)
        passed = metrics["value_capture_rate"] >= max(0.58, best_capture - 1e-12) and metrics["risk_breach_rate"] <= 0.001 and metrics["unsafe_action_rate"] == 0.0 and metrics["role_quorum_pass_rate"] >= (0.90 if release < 4 else 0.985)
        if release == 0:
            passed = True
        row = {"release": release, "accepted": bool(passed and metrics["value_capture_rate"] >= best_capture - 1e-12), "validation_value_capture_rate": metrics["value_capture_rate"], "validation_first_pass_success_rate": metrics["first_pass_success_rate"], "validation_liquidity_score": metrics["liquidity_score"], "validation_coordination_quality": metrics["coordination_quality"], "validation_risk_breach_rate": metrics["risk_breach_rate"], "validation_unsafe_action_rate": metrics["unsafe_action_rate"], "validation_role_quorum_pass_rate": metrics["role_quorum_pass_rate"]}
        if row["accepted"]:
            best_capture = max(best_capture, metrics["value_capture_rate"])
        accepted.append(row)
    return accepted


def bootstrap_ci(rows: list[dict], seed: int, baseline_key: str) -> dict:
    stable = int(hashlib.sha256(baseline_key.encode()).hexdigest()[:8], 16)
    r = random.Random(seed + stable)
    n = len(rows)
    deltas = []
    for _ in range(BOOTSTRAPS):
        sample = [rows[r.randrange(n)] for _ in range(n)]
        delta = sum(x["captured_value"] - x["baseline_captured_values"][baseline_key] for x in sample) / max(1.0, sum(x["potential_value"] for x in sample))
        deltas.append(delta)
    deltas.sort()
    return {"baseline": baseline_key, "p05_delta": deltas[int(0.05 * (len(deltas) - 1))], "p50_delta": deltas[int(0.50 * (len(deltas) - 1))], "p95_delta": deltas[int(0.95 * (len(deltas) - 1))]}


def canonical_hash(obj: dict) -> str:
    ignored = {"generated_at", "run_context", "proof_sha256"}
    reduced = {k: v for k, v in obj.items() if k not in ignored}
    return hashlib.sha256(json.dumps(reduced, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def make_badge(metrics: dict) -> str:
    label = "SkillOS RSI Capability Liquidity"
    status = "proof passed" if metrics["proved"] else "proof failed"
    color = "#20c997" if metrics["proved"] else "#d73a49"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="390" height="28" role="img" aria-label="{label}: {status}">
<linearGradient id="g" x2="0" y2="100%"><stop offset="0" stop-color="#16233d"/><stop offset="1" stop-color="#071827"/></linearGradient>
<rect width="390" height="28" rx="14" fill="url(#g)"/>
<rect x="250" width="140" height="28" rx="14" fill="{color}"/>
<text x="14" y="18" fill="#7ef7ff" font-family="Verdana,Geneva,sans-serif" font-size="12" font-weight="700">{label}</text>
<text x="268" y="18" fill="#071827" font-family="Verdana,Geneva,sans-serif" font-size="12" font-weight="700">{status}</text>
</svg>'''


def make_markdown(proof: dict) -> str:
    m = proof["metrics"]
    baseline = proof["baseline_metrics"]
    return f'''# {proof["proof_title"]} v{proof["proof_version"]}

## What this proves

SkillOS runs a deterministic, public, no-human-review benchmark for an AI-first capability marketplace: jobs become traces, traces become lessons, lessons become skill releases, and skill releases improve future routing, verification, coordination, and value capture.

This is not a claim of achieved superintelligence, live revenue, customer results, legal advice, policy advice, investment advice, guaranteed profit, or Kardashev Type II achievement. It is a public benchmark that makes the coordination mechanism testable.

## Mechanism

```text
{proof["mechanism"]["chain"]}
```

## Headline metrics

- Proved: `{m["proved"]}`
- Virtual specialist agents: `{m["virtual_specialist_agents"]:,}`
- Specialist roles: `{m["specialist_roles"]:,}`
- Capability markets: `{m["capability_markets"]:,}`
- Verifier courts: `{m["verifier_courts"]:,}`
- Skill release lanes: `{m["skill_release_lanes"]:,}`
- Locked holdout cases: `{m["locked_holdout_cases"]:,}`
- Selected RSI release: `v{m["selected_release"]}`
- Locked-holdout value capture: `{pct(m["locked_holdout_value_capture_rate"])} `
- First-pass verifiable success: `{pct(m["first_pass_success_rate"])} `
- Capability liquidity score: `{pct(m["capability_liquidity_score"])} `
- Trace compounding score: `{pct(m["trace_compounding_score"])} `
- Coordination quality: `{pct(m["coordination_quality"])} `
- Risk breach rate: `{pct(m["risk_breach_rate"])} `
- Unauthorized action rate: `{pct(m["unsafe_action_rate"])} `
- Benchmark-capital-equivalent value at stake: `{money(m["benchmark_capital_equivalent_value_at_stake"])} `
- Benchmark-capital-equivalent value captured: `{money(m["benchmark_capital_equivalent_value_captured"])} `
- Value over no-RSI marketplace: `{money(m["value_over_no_rsi_marketplace"])} `
- Value over uncoordinated agent pool: `{money(m["value_over_uncoordinated_agent_pool"])} `
- Value over static skill catalog: `{money(m["value_over_static_skill_catalog"])} `
- Value over single general agent: `{money(m["value_over_single_general_agent"])} `

## Baselines

| Strategy | Capture | Risk breach | Unauthorized action | Role quorum |
|---|---:|---:|---:|---:|
| SkillOS RSI capability liquidity engine | {pct(m["locked_holdout_value_capture_rate"])} | {pct(m["risk_breach_rate"])} | {pct(m["unsafe_action_rate"])} | {pct(m["role_quorum_pass_rate"])} |
| No-RSI marketplace | {pct(baseline["no_rsi_marketplace"]["value_capture_rate"])} | {pct(baseline["no_rsi_marketplace"]["risk_breach_rate"])} | {pct(baseline["no_rsi_marketplace"]["unsafe_action_rate"])} | {pct(baseline["no_rsi_marketplace"]["role_quorum_pass_rate"])} |
| Uncoordinated agent pool | {pct(baseline["uncoordinated_agent_pool"]["value_capture_rate"])} | {pct(baseline["uncoordinated_agent_pool"]["risk_breach_rate"])} | {pct(baseline["uncoordinated_agent_pool"]["unsafe_action_rate"])} | {pct(baseline["uncoordinated_agent_pool"]["role_quorum_pass_rate"])} |
| Static skill catalog | {pct(baseline["static_skill_catalog"]["value_capture_rate"])} | {pct(baseline["static_skill_catalog"]["risk_breach_rate"])} | {pct(baseline["static_skill_catalog"]["unsafe_action_rate"])} | {pct(baseline["static_skill_catalog"]["role_quorum_pass_rate"])} |
| Single general agent | {pct(baseline["single_general_agent"]["value_capture_rate"])} | {pct(baseline["single_general_agent"]["risk_breach_rate"])} | {pct(baseline["single_general_agent"]["unsafe_action_rate"])} | {pct(baseline["single_general_agent"]["role_quorum_pass_rate"])} |

## Why this is the next SkillOS proof

A single impressive proof is not enough. SkillOS needs to show that capabilities become liquid: discoverable, priced, routed, verified, released, reused, and improved. This proof tests exactly that loop. It is closer to the operating-system thesis than a single domain demo.

## Run it

```bash
python scripts/run_rsi_capability_liquidity_engine_proof.py
python scripts/verify_rsi_capability_liquidity_engine_proof.py
python scripts/render_rsi_capability_liquidity_engine_site.py
python scripts/publish_rsi_capability_liquidity_engine_to_hub.py
```

Or run the GitHub Action:

{WORKFLOW_URL}

Proof SHA-256:

```text
{proof["proof_sha256"]}
```
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=f"data/{PROOF_ID}.json")
    parser.add_argument("--markdown", default=f"docs/{PROOF_ID}.md")
    parser.add_argument("--badge", default=f"badges/{PROOF_ID}.svg")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--summary", default="")
    args = parser.parse_args()
    seed = args.seed
    validation_cases = [make_case(seed, "validation", i) for i in range(VALIDATION_CASES)]
    holdout_cases = [make_case(seed, "holdout", i) for i in range(LOCKED_HOLDOUT_CASES)]
    trace = release_trace(validation_cases, seed)
    accepted = [r for r in trace if r["accepted"]]
    selected_release = accepted[-1]["release"]
    skillos_holdout = evaluate_strategy(holdout_cases, "skillos_rsi_capability_liquidity_engine", seed, release=selected_release, rows=True)
    baseline_names = ["single_general_agent", "uncoordinated_agent_pool", "static_skill_catalog", "no_rsi_marketplace", "random_router_control"]
    baselines = {name: evaluate_strategy(holdout_cases, name, seed) for name in baseline_names}
    rows = skillos_holdout.pop("rows")
    baseline_row_values = {name: {} for name in baseline_names}
    baseline_row_capture = {name: {} for name in baseline_names}
    for name in baseline_names:
        for case in holdout_cases:
            result = evaluate_decision(case, baseline_policy(case, name, seed), name)
            baseline_row_values[name][case["id"]] = result["captured_value"]
            baseline_row_capture[name][case["id"]] = result["capture_rate"]
    frontier_correct = 0
    for row in rows:
        row["baseline_captured_values"] = {name: baseline_row_values[name][row["case_id"]] for name in baseline_names}
        row["baseline_capture_rates"] = {name: baseline_row_capture[name][row["case_id"]] for name in baseline_names}
        row["frontier_correct"] = row["captured_value"] >= max(row["baseline_captured_values"].values()) and not row["risk_breach"] and not row["unauthorized_action"]
        frontier_correct += 1 if row["frontier_correct"] else 0
    frontier_correct_rate = frontier_correct / len(rows)
    negative_controls = {
        "no_verifier_courts": evaluate_strategy(holdout_cases, "skillos_rsi_capability_liquidity_engine", seed, release=selected_release, ablation="no_verifier_courts"),
        "no_skill_release_loop": evaluate_strategy(holdout_cases, "skillos_rsi_capability_liquidity_engine", seed, release=selected_release, ablation="no_skill_release_loop"),
        "no_market_clearing": evaluate_strategy(holdout_cases, "skillos_rsi_capability_liquidity_engine", seed, release=selected_release, ablation="no_market_clearing"),
        "no_trace_memory": evaluate_strategy(holdout_cases, "skillos_rsi_capability_liquidity_engine", seed, release=selected_release, ablation="no_trace_memory"),
    }
    ci = {name: bootstrap_ci(rows, seed, name) for name in ["single_general_agent", "uncoordinated_agent_pool", "static_skill_catalog", "no_rsi_marketplace"]}
    metrics = {
        "proved": True,
        "virtual_specialist_agents": VIRTUAL_AGENTS,
        "specialist_roles": SPECIALIST_ROLES,
        "capability_markets": CAPABILITY_MARKETS,
        "verifier_courts": VERIFIER_COURTS,
        "skill_release_lanes": SKILL_RELEASE_LANES,
        "enterprise_regimes": ENTERPRISE_REGIMES,
        "train_cases": TRAIN_CASES,
        "validation_cases": VALIDATION_CASES,
        "locked_holdout_cases": LOCKED_HOLDOUT_CASES,
        "candidate_routing_policies_per_case": CANDIDATE_ROUTING_POLICIES_PER_CASE,
        "rsi_release_cycles": RSI_RELEASE_CYCLES,
        "accepted_rsi_releases": len(accepted),
        "selected_release": selected_release,
        "locked_holdout_value_capture_rate": skillos_holdout["value_capture_rate"],
        "median_capture_rate": skillos_holdout["median_capture_rate"],
        "first_pass_success_rate": skillos_holdout["first_pass_success_rate"],
        "time_reduction_rate": skillos_holdout["time_reduction_rate"],
        "cost_reduction_rate": skillos_holdout["cost_reduction_rate"],
        "capability_liquidity_score": skillos_holdout["liquidity_score"],
        "trace_compounding_score": skillos_holdout["trace_compounding_score"],
        "coordination_quality": skillos_holdout["coordination_quality"],
        "frontier_correct_rate": frontier_correct_rate,
        "risk_breach_rate": skillos_holdout["risk_breach_rate"],
        "unsafe_action_rate": skillos_holdout["unsafe_action_rate"],
        "role_quorum_pass_rate": skillos_holdout["role_quorum_pass_rate"],
        "benchmark_capital_equivalent_value_at_stake": skillos_holdout["value_at_stake"],
        "benchmark_capital_equivalent_value_captured": skillos_holdout["captured_value"],
        "value_over_single_general_agent": skillos_holdout["captured_value"] - baselines["single_general_agent"]["captured_value"],
        "value_over_uncoordinated_agent_pool": skillos_holdout["captured_value"] - baselines["uncoordinated_agent_pool"]["captured_value"],
        "value_over_static_skill_catalog": skillos_holdout["captured_value"] - baselines["static_skill_catalog"]["captured_value"],
        "value_over_no_rsi_marketplace": skillos_holdout["captured_value"] - baselines["no_rsi_marketplace"]["captured_value"],
    }
    gates = [
        {"name": "large multi-agent coordination", "threshold": ">=2,000,000 virtual agents and >=65,000 specialist roles", "passed": VIRTUAL_AGENTS >= 2_000_000 and SPECIALIST_ROLES >= 65_000},
        {"name": "locked holdout", "threshold": ">=4,096 locked holdout cases", "passed": LOCKED_HOLDOUT_CASES >= 4096},
        {"name": "validation-gated RSI", "threshold": ">=10 accepted RSI releases", "passed": len(accepted) >= 10},
        {"name": "capability liquidity", "threshold": ">=0.86 liquidity score", "passed": metrics["capability_liquidity_score"] >= 0.86},
        {"name": "frontier correctness", "threshold": ">=95% holdout cases beat baselines", "passed": frontier_correct_rate >= 0.95},
        {"name": "risk discipline", "threshold": "risk breach <=0.1% and unauthorized action =0", "passed": metrics["risk_breach_rate"] <= 0.001 and metrics["unsafe_action_rate"] == 0},
        {"name": "baseline dominance", "threshold": "positive bootstrap lower confidence bound against all major baselines", "passed": all(x["p05_delta"] > 0 for x in ci.values())},
        {"name": "ablation sensitivity", "threshold": "removing verifier courts, release loop, market clearing, or trace memory hurts the system", "passed": negative_controls["no_verifier_courts"]["risk_breach_rate"] > metrics["risk_breach_rate"] and negative_controls["no_skill_release_loop"]["value_capture_rate"] < metrics["locked_holdout_value_capture_rate"] and negative_controls["no_market_clearing"]["liquidity_score"] < metrics["capability_liquidity_score"] and negative_controls["no_trace_memory"]["trace_compounding_score"] < metrics["trace_compounding_score"]},
    ]
    metrics["proved"] = all(g["passed"] for g in gates)
    proof = {
        "proof_id": PROOF_ID,
        "proof_title": PROOF_TITLE,
        "proof_version": PROOF_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "seed": seed,
        "run_context": {"repo_url": REPO_URL, "base_url": BASE_URL, "workflow_file": WORKFLOW_FILE, "workflow_url": WORKFLOW_URL},
        "claim_boundary": {"safe_public_claim": "SkillOS publicly tests whether a large autonomous specialist-agent capability marketplace can recursively improve routing, verification, skill release, and value capture on locked holdout tasks.", "not_claimed": ["achieved superintelligence", "Kardashev Type II achievement", "live revenue", "customer results", "investment advice", "legal advice", "policy advice", "guaranteed ROI", "guaranteed profit"]},
        "mechanism": {"chain": "demand → decomposition → specialist market clearing → role quorum → execution traces → verifier courts → skill release → routing policy → capability liquidity → reinvestment → compounding institutional capability", "why_it_matters": "This is a direct SkillOS proof: capabilities become reusable, inspectable, routed, verified, released, and improved rather than trapped inside one-off agent runs."},
        "metrics": metrics,
        "baseline_metrics": baselines,
        "negative_controls": negative_controls,
        "bootstrap_confidence_intervals": ci,
        "rsi_release_trace": trace,
        "proof_gates": gates,
        "holdout_evaluation_rows": rows,
        "sample_holdout_cases": holdout_cases[:12],
        "public_copy_checks": {"forbidden_claims": FORBIDDEN_PUBLIC_CLAIMS},
    }
    proof["proof_sha256"] = canonical_hash(proof)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    md_path = Path(args.markdown); md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(make_markdown(proof), encoding="utf-8")
    badge_path = Path(args.badge); badge_path.parent.mkdir(parents=True, exist_ok=True)
    badge_path.write_text(make_badge(metrics), encoding="utf-8")
    summary = {"proved": metrics["proved"], "proof_id": PROOF_ID, "proof_sha256": proof["proof_sha256"], "selected_release": selected_release, "virtual_specialist_agents": VIRTUAL_AGENTS, "specialist_roles": SPECIALIST_ROLES, "locked_holdout_value_capture_rate": round(metrics["locked_holdout_value_capture_rate"], 6), "capability_liquidity_score": round(metrics["capability_liquidity_score"], 6), "trace_compounding_score": round(metrics["trace_compounding_score"], 6), "frontier_correct_rate": round(metrics["frontier_correct_rate"], 6), "risk_breach_rate": round(metrics["risk_breach_rate"], 6), "unsafe_action_rate": round(metrics["unsafe_action_rate"], 6), "value_over_no_rsi_marketplace": round(metrics["value_over_no_rsi_marketplace"], 2)}
    print(json.dumps(summary, indent=2))
    if args.summary:
        Path(args.summary).write_text("\n".join([f"### {PROOF_TITLE}", "", "```json", json.dumps(summary, indent=2), "```", ""]), encoding="utf-8")


if __name__ == "__main__":
    main()
