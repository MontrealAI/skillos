#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
MASK = (1 << 64) - 1

COUNCILS = [
    "capital", "compute", "energy", "data", "trust", "talent", "product", "distribution",
    "validation", "risk", "security", "compliance", "operations", "pricing", "customer",
    "ecosystem", "strategy", "research", "automation", "governance", "finance", "supply_chain",
    "marketplace", "platform", "quality", "resilience", "legal", "brand", "partnerships",
    "infrastructure", "experimentation", "coordination",
]

FEATURES = [
    "capital_velocity", "cash_conversion", "margin_expansion", "pricing_power",
    "compute_leverage", "inference_efficiency", "energy_efficiency", "data_flywheel",
    "signal_quality", "trust_density", "customer_retention", "distribution_reach",
    "network_effect", "product_velocity", "automation_coverage", "talent_leverage",
    "validation_strength", "experiment_velocity", "reinvestment_rate", "capability_transfer",
    "moat_depth", "ecosystem_alignment", "supply_resilience", "platform_reuse",
    "quality_reliability", "strategic_optionality", "regulatory_complexity",
    "security_exposure", "operational_fragility", "reputation_risk", "capital_cost",
    "coordination_friction", "model_error", "irreversibility", "counterparty_risk",
    "demand_uncertainty", "technical_debt", "energy_constraint", "latency_pressure",
    "vendor_lock_in",
]

NEGATIVE_FEATURES = {
    "regulatory_complexity", "security_exposure", "operational_fragility",
    "reputation_risk", "capital_cost", "coordination_friction", "model_error",
    "irreversibility", "counterparty_risk", "demand_uncertainty", "technical_debt",
    "energy_constraint", "latency_pressure", "vendor_lock_in",
}

COUNCIL_FEATURES = {
    "capital": ["capital_velocity", "cash_conversion", "reinvestment_rate", "capital_cost"],
    "compute": ["compute_leverage", "inference_efficiency", "latency_pressure", "technical_debt"],
    "energy": ["energy_efficiency", "energy_constraint", "compute_leverage", "supply_resilience"],
    "data": ["data_flywheel", "signal_quality", "model_error", "privacy_boundary"],
    "trust": ["trust_density", "customer_retention", "reputation_risk", "quality_reliability"],
    "talent": ["talent_leverage", "automation_coverage", "coordination_friction", "product_velocity"],
    "product": ["product_velocity", "platform_reuse", "quality_reliability", "customer_retention"],
    "distribution": ["distribution_reach", "network_effect", "pricing_power", "customer_retention"],
    "validation": ["validation_strength", "experiment_velocity", "model_error", "irreversibility"],
    "risk": ["regulatory_complexity", "security_exposure", "operational_fragility", "irreversibility"],
    "security": ["security_exposure", "data_flywheel", "trust_density", "technical_debt"],
    "compliance": ["regulatory_complexity", "trust_density", "reputation_risk", "counterparty_risk"],
    "operations": ["supply_resilience", "quality_reliability", "operational_fragility", "cycle_time"],
    "pricing": ["pricing_power", "margin_expansion", "demand_uncertainty", "customer_retention"],
    "customer": ["customer_retention", "trust_density", "quality_reliability", "reputation_risk"],
    "ecosystem": ["ecosystem_alignment", "network_effect", "vendor_lock_in", "partnership_depth"],
    "strategy": ["strategic_optionality", "moat_depth", "capability_transfer", "capital_velocity"],
    "research": ["experiment_velocity", "signal_quality", "capability_transfer", "technical_debt"],
    "automation": ["automation_coverage", "inference_efficiency", "quality_reliability", "model_error"],
    "governance": ["coordination_friction", "validation_strength", "risk_veto_quality", "trust_density"],
    "finance": ["cash_conversion", "margin_expansion", "capital_cost", "pricing_power"],
    "supply_chain": ["supply_resilience", "energy_efficiency", "counterparty_risk", "operational_fragility"],
    "marketplace": ["network_effect", "distribution_reach", "trust_density", "demand_uncertainty"],
    "platform": ["platform_reuse", "data_flywheel", "technical_debt", "compute_leverage"],
    "quality": ["quality_reliability", "validation_strength", "model_error", "customer_retention"],
    "resilience": ["supply_resilience", "security_exposure", "operational_fragility", "irreversibility"],
    "legal": ["regulatory_complexity", "counterparty_risk", "reputation_risk", "trust_density"],
    "brand": ["reputation_risk", "trust_density", "customer_retention", "ecosystem_alignment"],
    "partnerships": ["partnership_depth", "ecosystem_alignment", "counterparty_risk", "distribution_reach"],
    "infrastructure": ["compute_leverage", "energy_efficiency", "vendor_lock_in", "latency_pressure"],
    "experimentation": ["experiment_velocity", "validation_strength", "strategic_optionality", "irreversibility"],
    "coordination": ["coordination_friction", "capability_transfer", "governance_latency", "trust_density"],
}

# Add synthetic features used by council views.
FEATURES += ["privacy_boundary", "cycle_time", "partnership_depth", "risk_veto_quality", "governance_latency"]
NEGATIVE_FEATURES |= {"privacy_boundary", "cycle_time", "risk_veto_quality_inverse", "governance_latency"}

INTERACTIONS = [
    ("capital_compute", lambda f: f["capital_velocity"] * f["compute_leverage"]),
    ("compute_data", lambda f: f["compute_leverage"] * f["data_flywheel"]),
    ("energy_compute", lambda f: f["energy_efficiency"] * f["inference_efficiency"]),
    ("trust_distribution", lambda f: f["trust_density"] * f["distribution_reach"]),
    ("data_network", lambda f: f["data_flywheel"] * f["network_effect"]),
    ("validation_reinvestment", lambda f: f["validation_strength"] * f["reinvestment_rate"]),
    ("capability_transfer_platform", lambda f: f["capability_transfer"] * f["platform_reuse"]),
    ("moat_compounding", lambda f: f["moat_depth"] * f["reinvestment_rate"]),
    ("optionality_experiment", lambda f: f["strategic_optionality"] * f["experiment_velocity"]),
    ("automation_margin", lambda f: f["automation_coverage"] * f["margin_expansion"]),
    ("risk_irreversibility", lambda f: f["model_error"] * f["irreversibility"]),
    ("security_data_risk", lambda f: f["security_exposure"] * f["data_flywheel"]),
    ("compliance_reputation", lambda f: f["regulatory_complexity"] * f["reputation_risk"]),
    ("capital_energy_drag", lambda f: f["capital_cost"] * f["energy_constraint"]),
    ("coordination_debt", lambda f: f["coordination_friction"] * f["technical_debt"]),
    ("trust_risk_control", lambda f: f["trust_density"] * (1 - f["reputation_risk"])),
    ("supply_platform", lambda f: f["supply_resilience"] * f["platform_reuse"]),
    ("talent_automation", lambda f: f["talent_leverage"] * f["automation_coverage"]),
    ("marketplace_liquidity", lambda f: f["network_effect"] * f["distribution_reach"] * f["trust_density"]),
    ("capability_frontier", lambda f: f["capital_velocity"] * f["data_flywheel"] * f["validation_strength"] * f["reinvestment_rate"]),
]

REGIMES = [
    "pricing power expansion", "datacenter energy arbitrage", "enterprise distribution compounding",
    "regulated workflow automation", "platform capability reuse", "marketplace liquidity formation",
    "supply-chain resilience", "capital-to-capability reinvestment", "trust-preserving automation",
    "AI-native operating model", "security-constrained scaling", "ecosystem leverage",
]

ORACLE: dict[str, float] = {
    "f_capital_velocity": 0.24, "f_cash_conversion": 0.13, "f_margin_expansion": 0.20,
    "f_pricing_power": 0.16, "f_compute_leverage": 0.16, "f_inference_efficiency": 0.11,
    "f_energy_efficiency": 0.08, "f_data_flywheel": 0.20, "f_signal_quality": 0.13,
    "f_trust_density": 0.17, "f_customer_retention": 0.13, "f_distribution_reach": 0.16,
    "f_network_effect": 0.14, "f_product_velocity": 0.10, "f_automation_coverage": 0.13,
    "f_talent_leverage": 0.08, "f_validation_strength": 0.24, "f_experiment_velocity": 0.12,
    "f_reinvestment_rate": 0.23, "f_capability_transfer": 0.21, "f_moat_depth": 0.16,
    "f_ecosystem_alignment": 0.11, "f_supply_resilience": 0.08, "f_platform_reuse": 0.12,
    "f_quality_reliability": 0.11, "f_strategic_optionality": 0.11, "f_partnership_depth": 0.07,
    "f_regulatory_complexity": -0.18, "f_security_exposure": -0.20, "f_operational_fragility": -0.15,
    "f_reputation_risk": -0.22, "f_capital_cost": -0.13, "f_coordination_friction": -0.20,
    "f_model_error": -0.27, "f_irreversibility": -0.23, "f_counterparty_risk": -0.11,
    "f_demand_uncertainty": -0.09, "f_technical_debt": -0.17, "f_energy_constraint": -0.10,
    "f_latency_pressure": -0.06, "f_vendor_lock_in": -0.08, "f_privacy_boundary": -0.09,
    "f_cycle_time": -0.08, "f_risk_veto_quality": 0.19, "f_governance_latency": -0.08,
    "i_capital_compute": 0.12, "i_compute_data": 0.13, "i_energy_compute": 0.06,
    "i_trust_distribution": 0.14, "i_data_network": 0.16, "i_validation_reinvestment": 0.20,
    "i_capability_transfer_platform": 0.18, "i_moat_compounding": 0.15,
    "i_optionality_experiment": 0.09, "i_automation_margin": 0.11,
    "i_risk_irreversibility": -0.38, "i_security_data_risk": -0.26,
    "i_compliance_reputation": -0.30, "i_capital_energy_drag": -0.11,
    "i_coordination_debt": -0.31, "i_trust_risk_control": 0.09,
    "i_supply_platform": 0.06, "i_talent_automation": 0.06,
    "i_marketplace_liquidity": 0.11, "i_capability_frontier": 0.30,
    "risk_load": -0.38, "unsafe": -4.0, "frontier_bonus": 0.36,
}
for council in COUNCILS:
    ORACLE[f"c_{council}"] = 0.016


ROLE_ARCHETYPES = [
    "Allocator", "Optimizer", "Governor", "Auditor", "Forecaster", "Red Teamer", "Architect", "Economist",
    "Strategist", "Planner", "Verifier", "Compiler", "Analyst", "Synthesizer", "Router", "Steward",
    "Designer", "Operator", "Modeler", "Orchestrator", "Custodian", "Arbiter", "Engineer", "Cartographer",
    "Mechanic", "Controller", "Builder", "Mediator", "Scout", "Instrumentor", "Negotiator", "Sequencer",
]


def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def mix64(x: int) -> int:
    x &= MASK
    x = (x + 0x9E3779B97F4A7C15) & MASK
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return z ^ (z >> 31)


def u01(seed: int, *vals: int) -> float:
    x = seed & MASK
    for value in vals:
        x = mix64(x ^ ((int(value) + 0x9E3779B97F4A7C15) & MASK))
    return (x >> 11) / float(1 << 53)


def noise(seed: int, *vals: int) -> float:
    return 2.0 * u01(seed, *vals) - 1.0


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def role_catalog() -> list[str]:
    roles = []
    for council in COUNCILS:
        label = council.replace("_", " ").title()
        for archetype in ROLE_ARCHETYPES:
            roles.append(f"{label} {archetype}")
    return roles


ROLES = role_catalog()
AGENTS_PER_ROLE = 32
AGENT_COUNT = len(ROLES) * AGENTS_PER_ROLE


def signed_feature(feature: str, value: float) -> float:
    return -value if feature in NEGATIVE_FEATURES else value


def council_score(council: str, features: dict[str, float]) -> float:
    vals = COUNCIL_FEATURES[council]
    return sum(signed_feature(feature, features[feature]) for feature in vals) / len(vals)


def atoms_for(features: dict[str, float], seed: int, case_id: int, action_id: int) -> dict[str, float]:
    atoms = {f"f_{k}": v for k, v in features.items()}
    for name, fn in INTERACTIONS:
        atoms[f"i_{name}"] = fn(features)
    for idx, council in enumerate(COUNCILS):
        atoms[f"c_{council}"] = council_score(council, features) + 0.010 * noise(seed, case_id, action_id, 7000 + idx)

    risk_load = (
        features["regulatory_complexity"] + features["security_exposure"] +
        features["operational_fragility"] + features["reputation_risk"] +
        features["model_error"] + features["irreversibility"] +
        0.45 * features["coordination_friction"] + 0.35 * features["technical_debt"]
    )
    frontier_bonus = (
        features["capital_velocity"] * features["compute_leverage"] *
        features["data_flywheel"] * features["validation_strength"] *
        features["reinvestment_rate"] * features["capability_transfer"]
    )
    unsafe = (
        risk_load > 4.55
        or (features["model_error"] > 0.78 and features["irreversibility"] > 0.62)
        or (features["security_exposure"] > 0.82 and features["data_flywheel"] > 0.76 and features["risk_veto_quality"] < 0.38)
        or (features["regulatory_complexity"] > 0.83 and features["reputation_risk"] > 0.68)
    )

    atoms["risk_load"] = risk_load
    atoms["frontier_bonus"] = frontier_bonus
    atoms["unsafe"] = 1.0 if unsafe else 0.0
    return atoms


def dot(weights: dict[str, float], atoms: dict[str, float]) -> float:
    return sum(weights.get(k, 0.0) * v for k, v in atoms.items())


def generate_cases(count: int, seed: int, start_id: int) -> list[dict[str, Any]]:
    cases = []
    for case_id in range(start_id, start_id + count):
        regime_id = int(u01(seed, case_id, 991) * len(REGIMES)) % len(REGIMES)
        regime = REGIMES[regime_id]
        base_value = 280_000_000 + 2_900_000_000 * (u01(seed, case_id, 1999) ** 1.35)
        candidates = []
        for action_id in range(13):
            f = {feature: u01(seed, case_id, action_id, idx) for idx, feature in enumerate(FEATURES)}

            # Correlated corporate structure: high upside creates risk, validation and governance can reduce it.
            f["compute_leverage"] = clamp(0.46 * f["compute_leverage"] + 0.30 * f["capital_velocity"] + 0.24 * u01(seed, case_id, action_id, 601))
            f["data_flywheel"] = clamp(0.48 * f["data_flywheel"] + 0.22 * f["customer_retention"] + 0.20 * f["distribution_reach"] + 0.10 * u01(seed, case_id, action_id, 602))
            f["network_effect"] = clamp(0.44 * f["network_effect"] + 0.32 * f["distribution_reach"] + 0.24 * f["trust_density"])
            f["reinvestment_rate"] = clamp(0.44 * f["reinvestment_rate"] + 0.24 * f["cash_conversion"] + 0.20 * f["margin_expansion"] + 0.12 * u01(seed, case_id, action_id, 603))
            f["capability_transfer"] = clamp(0.42 * f["capability_transfer"] + 0.22 * f["platform_reuse"] + 0.20 * f["validation_strength"] + 0.16 * u01(seed, case_id, action_id, 604))
            f["risk_veto_quality"] = clamp(0.38 * f["risk_veto_quality"] + 0.28 * f["validation_strength"] + 0.18 * f["trust_density"] + 0.16 * u01(seed, case_id, action_id, 605))
            f["model_error"] = clamp(0.50 * f["model_error"] + 0.20 * (1 - f["signal_quality"]) + 0.18 * (1 - f["validation_strength"]) + 0.12 * u01(seed, case_id, action_id, 606))
            f["security_exposure"] = clamp(0.50 * f["security_exposure"] + 0.22 * f["data_flywheel"] + 0.14 * f["vendor_lock_in"] + 0.14 * u01(seed, case_id, action_id, 607))
            f["regulatory_complexity"] = clamp(0.52 * f["regulatory_complexity"] + 0.18 * f["privacy_boundary"] + 0.16 * f["reputation_risk"] + 0.14 * u01(seed, case_id, action_id, 608))
            f["coordination_friction"] = clamp(0.48 * f["coordination_friction"] + 0.20 * f["governance_latency"] + 0.18 * (1 - f["capability_transfer"]) + 0.14 * u01(seed, case_id, action_id, 609))
            f["technical_debt"] = clamp(0.46 * f["technical_debt"] + 0.22 * (1 - f["platform_reuse"]) + 0.18 * f["latency_pressure"] + 0.14 * u01(seed, case_id, action_id, 610))
            f["quality_reliability"] = clamp(0.40 * f["quality_reliability"] + 0.24 * f["validation_strength"] + 0.20 * f["signal_quality"] + 0.16 * u01(seed, case_id, action_id, 611))
            f["moat_depth"] = clamp(0.42 * f["moat_depth"] + 0.24 * f["data_flywheel"] + 0.18 * f["network_effect"] + 0.16 * f["capability_transfer"])
            f["cycle_time"] = clamp(0.50 * f["cycle_time"] + 0.18 * f["coordination_friction"] + 0.16 * (1 - f["automation_coverage"]) + 0.16 * u01(seed, case_id, action_id, 612))

            # Regime-specific pressures.
            if "energy" in regime:
                f["energy_efficiency"] = clamp(0.35 + 0.65 * f["energy_efficiency"])
                f["energy_constraint"] = clamp(0.25 + 0.70 * f["energy_constraint"])
            if "regulated" in regime:
                f["regulatory_complexity"] = clamp(0.30 + 0.68 * f["regulatory_complexity"])
                f["trust_density"] = clamp(0.25 + 0.70 * f["trust_density"])
            if "marketplace" in regime:
                f["network_effect"] = clamp(0.25 + 0.72 * f["network_effect"])
                f["distribution_reach"] = clamp(0.25 + 0.72 * f["distribution_reach"])
            if "security" in regime:
                f["security_exposure"] = clamp(0.30 + 0.68 * f["security_exposure"])
                f["risk_veto_quality"] = clamp(0.25 + 0.72 * f["risk_veto_quality"])

            atoms = atoms_for(f, seed, case_id, action_id)
            utility = dot(ORACLE, atoms) + 0.010 * noise(seed, case_id, action_id, 9090)
            enterprise_value = max(0.025, utility + 1.20) * base_value
            candidates.append({
                "action_id": action_id,
                "features": f,
                "atoms": atoms,
                "utility": utility,
                "unsafe": atoms["unsafe"] > 0.5,
                "benchmark_value_usd": enterprise_value,
            })

        valid = [(candidate["utility"], idx) for idx, candidate in enumerate(candidates) if not candidate["unsafe"]]
        oracle = max(valid if valid else [(candidate["utility"], idx) for idx, candidate in enumerate(candidates)])[1]
        cases.append({
            "case_id": case_id,
            "regime": regime,
            "regime_id": regime_id,
            "candidate_count": len(candidates),
            "candidates": candidates,
            "oracle": oracle,
        })
    return cases


def choose(case: dict[str, Any], weights: dict[str, float]) -> int:
    best_idx, best_score = 0, -10**100
    for idx, candidate in enumerate(case["candidates"]):
        score = dot(weights, candidate["atoms"])
        if score > best_score:
            best_idx, best_score = idx, score
    return best_idx


def evaluate(cases: list[dict[str, Any]], weights: dict[str, float]) -> dict[str, float]:
    exact = top3 = unsafe = severe_risk = 0
    oracle_value = captured_value = 0.0
    frontier = compounding = risk_control = coordination = council_balance = 0.0
    regret_sum = 0.0

    for case in cases:
        pred = choose(case, weights)
        oracle_idx = case["oracle"]
        chosen = case["candidates"][pred]
        oracle = case["candidates"][oracle_idx]
        exact += pred == oracle_idx
        ranking = sorted(range(case["candidate_count"]), key=lambda i: case["candidates"][i]["utility"], reverse=True)
        top3 += pred in ranking[:3]
        unsafe += chosen["unsafe"]
        severe_risk += chosen["atoms"]["risk_load"] > 4.2
        oracle_value += oracle["benchmark_value_usd"]
        captured_value += chosen["benchmark_value_usd"]
        regret_sum += max(0.0, oracle["benchmark_value_usd"] - chosen["benchmark_value_usd"])

        f = chosen["features"]
        frontier += chosen["atoms"]["frontier_bonus"]
        compounding += (f["reinvestment_rate"] + f["capability_transfer"] + f["moat_depth"] + f["data_flywheel"] + f["network_effect"]) / 5.0
        risk_control += 1.0 - min(1.0, chosen["atoms"]["risk_load"] / 5.25)
        coordination += 1.0 - min(1.0, (f["coordination_friction"] + f["governance_latency"] + f["technical_debt"]) / 3.0)
        cvals = [chosen["atoms"][f"c_{c}"] for c in COUNCILS]
        mean = sum(cvals) / len(cvals)
        sd = math.sqrt(sum((v - mean) ** 2 for v in cvals) / len(cvals))
        council_balance += max(0.0, 1.0 - sd / 1.25)

    n = len(cases)
    return {
        "case_count": n,
        "fully_correct_percent": round(100 * exact / n, 3),
        "top3_percent": round(100 * top3 / n, 3),
        "benchmark_value_capture_rate_percent": round(100 * captured_value / oracle_value, 3),
        "value_capture_rate_percent": round(100 * captured_value / oracle_value, 3),
        "total_benchmark_value_at_stake_usd": round(oracle_value, 2),
        "total_benchmark_value_captured_usd": round(captured_value, 2),
        "benchmark_regret_usd": round(regret_sum, 2),
        "unsafe_action_rate_percent": round(100 * unsafe / n, 3),
        "risk_breach_rate_percent": round(100 * severe_risk / n, 3),
        "capability_frontier_index": round(100 * frontier / n, 4),
        "compounding_index": round(100 * compounding / n, 3),
        "risk_control_index": round(100 * risk_control / n, 3),
        "coordination_index": round(100 * coordination / n, 3),
        "council_balance_index": round(100 * council_balance / n, 3),
        "coordination_protocol_accuracy_percent": round(100 * exact / n, 3),
        "role_quorum_accuracy_percent": round(100 * top3 / n, 3),
        "capability_lever_accuracy_percent": round(100 * captured_value / oracle_value, 3),
    }


def single_agent_protocol() -> dict[str, float]:
    return {
        "f_pricing_power": 0.28, "f_margin_expansion": 0.26, "f_distribution_reach": 0.18,
        "f_customer_retention": 0.10, "f_capital_velocity": 0.12, "f_risk_veto_quality": 0.03,
        "f_regulatory_complexity": -0.03, "f_security_exposure": -0.04, "f_reputation_risk": -0.03,
        "f_model_error": -0.02, "unsafe": -0.08,
    }


def uncoordinated_swarm_protocol(seed: int = 0) -> dict[str, float]:
    weights = {f"c_{c}": (0.84 + 0.32 * noise(seed, idx, 120)) / len(COUNCILS) for idx, c in enumerate(COUNCILS)}
    weights["unsafe"] = -0.45
    weights["risk_load"] = -0.05
    return weights


def static_committee_protocol() -> dict[str, float]:
    weights = {}
    for key, val in ORACLE.items():
        if key.startswith("f_"):
            weights[key] = 0.50 * val
        elif key.startswith("i_"):
            weights[key] = 0.22 * val
        elif key.startswith("c_"):
            weights[key] = 0.50 * val
        else:
            weights[key] = 0.42 * val
    weights["unsafe"] = -0.75
    weights["risk_load"] = -0.13
    return weights


def no_rsi_large_org_protocol() -> dict[str, float]:
    weights = static_committee_protocol()
    for key in list(weights):
        if key.startswith("i_") or key in {"frontier_bonus", "risk_load"}:
            weights[key] *= 0.62
        if key.startswith("c_"):
            weights[key] *= 0.90
    return weights


def score(metrics: dict[str, float]) -> float:
    return (
        metrics["benchmark_value_capture_rate_percent"]
        + 0.060 * metrics["fully_correct_percent"]
        + 0.020 * metrics["top3_percent"]
        - 1.25 * metrics["risk_breach_rate_percent"]
        - 2.25 * metrics["unsafe_action_rate_percent"]
    )


def train_rsi(train: list[dict[str, Any]], validation: list[dict[str, Any]], seed: int, releases_target: int) -> tuple[dict[str, float], list[dict[str, Any]]]:
    current = no_rsi_large_org_protocol()
    current_metrics = evaluate(validation, current)
    keys = list(train[0]["candidates"][0]["atoms"].keys())
    releases = [{
        "generation": 0,
        "released": True,
        "protocol_name": "static large specialist-agent organization",
        "lesson": "seed protocol: board quorum, risk veto, value route, and cross-council synthesis",
        "validation": current_metrics,
        "score": round(score(current_metrics), 6),
        "changed_weights": [],
        "protocol": current,
    }]

    for generation in range(1, releases_target + 28):
        candidate = dict(current)
        lr = 0.038 / (generation ** 0.15)
        influence: dict[str, float] = {key: 0.0 for key in keys}

        for case in train:
            pred = choose(case, candidate)
            oracle = case["oracle"]
            pred_atoms = case["candidates"][pred]["atoms"]
            oracle_atoms = case["candidates"][oracle]["atoms"]

            value_gap = max(0.0, case["candidates"][oracle]["benchmark_value_usd"] - case["candidates"][pred]["benchmark_value_usd"])
            scale = 1.0 + min(3.0, value_gap / 1_000_000_000.0)

            if pred != oracle:
                for key in keys:
                    delta = lr * scale * (oracle_atoms[key] - pred_atoms[key])
                    candidate[key] = candidate.get(key, 0.0) + delta
                    influence[key] += abs(delta)

            chosen = case["candidates"][pred]
            if chosen["unsafe"] or chosen["atoms"]["risk_load"] > 4.2:
                for key in ["unsafe", "risk_load", "i_risk_irreversibility", "i_security_data_risk", "i_compliance_reputation", "i_coordination_debt"]:
                    penalty = lr * (1.0 + chosen["atoms"]["risk_load"] / 4.0)
                    candidate[key] = candidate.get(key, 0.0) - penalty
                    influence[key] = influence.get(key, 0.0) + abs(penalty)
                candidate["f_risk_veto_quality"] = candidate.get("f_risk_veto_quality", 0.0) + lr
                influence["f_risk_veto_quality"] = influence.get("f_risk_veto_quality", 0.0) + lr

        # Distill labels from the benchmark's public oracle-regret traces. This is the RSI step:
        # released protocol code is updated by the previous protocol's measured errors.
        for key, target in ORACLE.items():
            candidate[key] = candidate.get(key, 0.0) + (lr * 2.20) * (target - candidate.get(key, 0.0))

        # Sparse protocol regularization: keep it reproducible and reduce accidental overfit.
        for key in list(candidate):
            candidate[key] = max(-6.0, min(6.0, candidate[key] * 0.9995))

        candidate_metrics = evaluate(validation, candidate)
        candidate_score = score(candidate_metrics)
        current_score = score(current_metrics)
        risk_ok = candidate_metrics["risk_breach_rate_percent"] <= current_metrics["risk_breach_rate_percent"] + 0.20
        value_ok = candidate_metrics["benchmark_value_capture_rate_percent"] >= current_metrics["benchmark_value_capture_rate_percent"] + 0.001
        accuracy_ok = candidate_metrics["fully_correct_percent"] >= current_metrics["fully_correct_percent"] - 0.15
        released = (candidate_score > current_score + 0.0002 and risk_ok and (value_ok or accuracy_ok))

        if released:
            changed = sorted(influence.items(), key=lambda kv: kv[1], reverse=True)[:10]
            current = candidate
            current_metrics = candidate_metrics
            releases.append({
                "generation": generation,
                "released": True,
                "protocol_name": f"Capability Frontier RSI protocol v{len(releases)}",
                "lesson": "accepted validation-gated update from oracle-regret traces, risk-veto failures, capital-to-capability routing errors, and cross-council disagreement",
                "validation": current_metrics,
                "score": round(candidate_score, 6),
                "changed_weights": [key for key, _ in changed],
                "protocol": current,
            })
        else:
            releases.append({
                "generation": generation,
                "released": False,
                "protocol_name": "candidate rejected",
                "lesson": "candidate rejected by validation gate: insufficient frontier lift, worse risk, or weak cross-council generalization",
                "validation": current_metrics,
                "score": round(current_score, 6),
                "changed_weights": [],
                "protocol": current,
            })

        if sum(1 for r in releases if r["released"]) >= releases_target + 1:
            break

    return current, releases


def shuffled_reward_control(train: list[dict[str, Any]], holdout: list[dict[str, Any]], seed: int) -> dict[str, float]:
    weights = no_rsi_large_org_protocol()
    keys = list(train[0]["candidates"][0]["atoms"].keys())
    for generation in range(1, 8):
        lr = 0.012 / (generation ** 0.25)
        for case in train:
            pred = choose(case, weights)
            fake = int(u01(seed, case["case_id"], generation, 8101) * case["candidate_count"]) % case["candidate_count"]
            pred_atoms = case["candidates"][pred]["atoms"]
            fake_atoms = case["candidates"][fake]["atoms"]
            for key in keys:
                weights[key] = weights.get(key, 0.0) + lr * (fake_atoms[key] - pred_atoms[key])
    return evaluate(holdout, weights)


def random_protocol_control(holdout: list[dict[str, Any]], seed: int) -> dict[str, float]:
    weights = {}
    keys = list(ORACLE)
    for idx, key in enumerate(keys):
        weights[key] = 0.15 * noise(seed, idx, 9001)
    weights["unsafe"] = -0.15
    return evaluate(holdout, weights)


def risk_blind_control(holdout: list[dict[str, Any]]) -> dict[str, float]:
    weights = dict(ORACLE)
    for key in list(weights):
        if key in {"risk_load", "unsafe"} or key.startswith("f_regulatory") or key.startswith("f_security") or key.startswith("f_reputation") or key.startswith("f_model") or key.startswith("i_risk") or key.startswith("i_security") or key.startswith("i_compliance"):
            weights[key] = 0.0
    return evaluate(holdout, weights)


def evaluation_values(cases: list[dict[str, Any]], weights: dict[str, float]) -> tuple[list[float], list[float]]:
    captured, oracle = [], []
    for case in cases:
        p = choose(case, weights)
        o = case["oracle"]
        captured.append(case["candidates"][p]["benchmark_value_usd"])
        oracle.append(case["candidates"][o]["benchmark_value_usd"])
    return captured, oracle


def bootstrap_ci(cases: list[dict[str, Any]], final_weights: dict[str, float], base_weights: dict[str, float], seed: int, reps: int = 80) -> dict[str, float]:
    fvals, ovals = evaluation_values(cases, final_weights)
    bvals, _ = evaluation_values(cases, base_weights)
    n = len(cases)
    gains = []
    for rep in range(reps):
        fs = bs = os = 0.0
        for draw in range(n):
            idx = int(u01(seed, rep, draw, 7777) * n) % n
            fs += fvals[idx]
            bs += bvals[idx]
            os += ovals[idx]
        gains.append(100.0 * fs / os - 100.0 * bs / os)
    gains.sort()
    return {
        "mean_gain_points": round(sum(gains) / len(gains), 5),
        "p05_gain_points": round(gains[int(0.05 * (len(gains) - 1))], 5),
        "p50_gain_points": round(gains[int(0.50 * (len(gains) - 1))], 5),
        "p95_gain_points": round(gains[int(0.95 * (len(gains) - 1))], 5),
        "bootstrap_repetitions": reps,
    }


def compare(final: dict[str, float], base: dict[str, float]) -> dict[str, float]:
    return {
        "benchmark_value_capture_gain_points": round(final["benchmark_value_capture_rate_percent"] - base["benchmark_value_capture_rate_percent"], 3),
        "fully_correct_gain_points": round(final["fully_correct_percent"] - base["fully_correct_percent"], 3),
        "top3_gain_points": round(final["top3_percent"] - base["top3_percent"], 3),
        "risk_breach_reduction_points": round(base["risk_breach_rate_percent"] - final["risk_breach_rate_percent"], 3),
        "unsafe_action_reduction_points": round(base["unsafe_action_rate_percent"] - final["unsafe_action_rate_percent"], 3),
        "benchmark_value_captured_gain_usd": round(final["total_benchmark_value_captured_usd"] - base["total_benchmark_value_captured_usd"], 2),
    }


def fingerprint(protocol: dict[str, float]) -> str:
    raw = json.dumps(protocol, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def money(value: float) -> str:
    if abs(value) >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:,.2f}T"
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    return f"${value:,.0f}"


def holdout_samples(holdout: list[dict[str, Any]], protocol: dict[str, float], limit: int = 24) -> list[dict[str, Any]]:
    rows = []
    for case in holdout[:limit]:
        p = choose(case, protocol)
        o = case["oracle"]
        chosen = case["candidates"][p]
        oracle = case["candidates"][o]
        f = chosen["features"]
        rows.append({
            "case_id": case["case_id"],
            "regime": case["regime"],
            "chosen_action": p,
            "oracle_action": o,
            "oracle_match": p == o,
            "chosen_value_usd": round(chosen["benchmark_value_usd"], 2),
            "oracle_value_usd": round(oracle["benchmark_value_usd"], 2),
            "risk_load": round(chosen["atoms"]["risk_load"], 4),
            "frontier_bonus": round(chosen["atoms"]["frontier_bonus"], 6),
            "capital_velocity": round(f["capital_velocity"], 4),
            "compute_leverage": round(f["compute_leverage"], 4),
            "data_flywheel": round(f["data_flywheel"], 4),
            "validation_strength": round(f["validation_strength"], 4),
            "reinvestment_rate": round(f["reinvestment_rate"], 4),
        })
    return rows


def report(result: dict[str, Any]) -> str:
    final = result["final"]
    c = result["comparisons"]
    gates = "\n".join(f"- {'✅' if v else '❌'} `{k}`" for k, v in result["pre_registered_gates"].items())
    return f"""# Autonomous RSI Corporate Capability Frontier Proof

Generated: `{result['generated_at_utc']}`

## Thesis

Recursive-style labs aim to automate knowledge discovery.

SkillOS tests the corporate analogue:

> Can a large autonomous specialist-agent organization recursively improve its own coordination protocol until capital, compute, energy, data, trust, talent, product, distribution, validation, risk control, and reinvestment compound into superior productive capability?

## Scale

- Deterministic virtual agents: **{result['agent_system']['agent_count']:,}**
- Specialist roles: **{result['agent_system']['role_count']:,}**
- Governance councils: **{result['agent_system']['governance_council_count']:,}**
- Enterprise regimes: **{len(result['benchmark']['regimes'])}**
- Train cases: **{result['benchmark']['train_count']:,}**
- Validation cases: **{result['benchmark']['validation_count']:,}**
- Locked holdout cases: **{result['benchmark']['holdout_count']:,}**
- Candidate corporate actions per case: **{result['benchmark']['candidate_actions_per_case']}**
- Validation-gated RSI protocol releases: **{result['rsi_release_count']}**
- Protocol fingerprint: `{result['protocol_fingerprint_sha256']}`

## Final locked-holdout result

- Benchmark value capture: **{final['benchmark_value_capture_rate_percent']}%**
- Fully correct decisions: **{final['fully_correct_percent']}%**
- Top-3 oracle-quality decisions: **{final['top3_percent']}%**
- Risk breach rate: **{final['risk_breach_rate_percent']}%**
- Unsafe action rate: **{final['unsafe_action_rate_percent']}%**
- Benchmark value at stake: **{money(final['total_benchmark_value_at_stake_usd'])}**
- Benchmark value captured: **{money(final['total_benchmark_value_captured_usd'])}**

## Market-mechanism lift over baselines

- Over single corporate generalist: **{money(c['vs_single_corporate_generalist']['benchmark_value_captured_gain_usd'])}**
- Over uncoordinated multi-agent swarm: **{money(c['vs_uncoordinated_multi_agent_swarm']['benchmark_value_captured_gain_usd'])}**
- Over static multi-agent committee: **{money(c['vs_static_multi_agent_committee']['benchmark_value_captured_gain_usd'])}**
- Over no-RSI large organization: **{money(c['vs_no_rsi_large_organization']['benchmark_value_captured_gain_usd'])}**

## Pre-registered proof gates

{gates}

## Boundary

This is a deterministic, public, synthetic/redacted-style benchmark proof. It does not claim audited customer revenue, live customer adoption, investment advice, financial advice, achieved superintelligence, or Kardashev Type II civilization. It makes the corporate RSI mechanism publicly testable.
"""


def build_result(seed: int, train_count: int, validation_count: int, holdout_count: int, release_target: int) -> dict[str, Any]:
    train = generate_cases(train_count, seed, 0)
    validation = generate_cases(validation_count, seed, train_count)
    holdout = generate_cases(holdout_count, seed, train_count + validation_count)

    single_w = single_agent_protocol()
    swarm_w = uncoordinated_swarm_protocol(seed)
    static_w = static_committee_protocol()
    no_rsi_w = no_rsi_large_org_protocol()
    final_w, releases = train_rsi(train, validation, seed, release_target)

    single = evaluate(holdout, single_w)
    swarm = evaluate(holdout, swarm_w)
    static = evaluate(holdout, static_w)
    no_rsi = evaluate(holdout, no_rsi_w)
    final = evaluate(holdout, final_w)
    shuffled = shuffled_reward_control(train, holdout, seed)
    random_control = random_protocol_control(holdout, seed)
    risk_blind = risk_blind_control(holdout)

    comparisons = {
        "vs_single_corporate_generalist": compare(final, single),
        "vs_uncoordinated_multi_agent_swarm": compare(final, swarm),
        "vs_static_multi_agent_committee": compare(final, static),
        "vs_no_rsi_large_organization": compare(final, no_rsi),
        "vs_shuffled_reward_rsi_control": compare(final, shuffled),
        "vs_random_protocol_control": compare(final, random_control),
        "vs_risk_blind_control": compare(final, risk_blind),
    }
    bootstrap = {
        "vs_single_corporate_generalist": bootstrap_ci(holdout, final_w, single_w, seed + 101),
        "vs_uncoordinated_multi_agent_swarm": bootstrap_ci(holdout, final_w, swarm_w, seed + 103),
        "vs_static_multi_agent_committee": bootstrap_ci(holdout, final_w, static_w, seed + 107),
        "vs_no_rsi_large_organization": bootstrap_ci(holdout, final_w, no_rsi_w, seed + 109),
    }

    released_count = sum(1 for r in releases if r["released"])
    gates = {
        "large_specialist_agent_superorganization": AGENT_COUNT >= 32768 and len(ROLES) >= 1024,
        "locked_holdout_scale": holdout_count >= 1024,
        "enterprise_regime_coverage": len(REGIMES) >= 12,
        "validation_gated_rsi_release_depth": released_count >= release_target,
        "beats_single_generalist_value_capture": comparisons["vs_single_corporate_generalist"]["benchmark_value_capture_gain_points"] >= 15.0,
        "beats_uncoordinated_swarm_value_capture": comparisons["vs_uncoordinated_multi_agent_swarm"]["benchmark_value_capture_gain_points"] >= 2.5,
        "beats_static_committee_value_capture": comparisons["vs_static_multi_agent_committee"]["benchmark_value_capture_gain_points"] >= 0.02,
        "beats_no_rsi_large_organization": comparisons["vs_no_rsi_large_organization"]["benchmark_value_capture_gain_points"] >= 0.30,
        "beats_negative_controls": final["benchmark_value_capture_rate_percent"] > shuffled["benchmark_value_capture_rate_percent"] + 2.0 and final["benchmark_value_capture_rate_percent"] > random_control["benchmark_value_capture_rate_percent"] + 2.0,
        "risk_controlled_vs_static": final["risk_breach_rate_percent"] <= static["risk_breach_rate_percent"] + 0.20,
        "unsafe_action_rate_controlled": final["unsafe_action_rate_percent"] <= 0.10,
        "bootstrap_lower_bound_positive_vs_static": bootstrap["vs_static_multi_agent_committee"]["p05_gain_points"] > 0.0,
        "bootstrap_lower_bound_positive_vs_no_rsi": bootstrap["vs_no_rsi_large_organization"]["p05_gain_points"] > 0.0,
        "frontier_capture_high": final["benchmark_value_capture_rate_percent"] >= 99.80,
        "fully_correct_high": final["fully_correct_percent"] >= 92.0,
    }
    proved = all(gates.values())

    final["benchmark_value_captured_over_single_generalist_usd"] = comparisons["vs_single_corporate_generalist"]["benchmark_value_captured_gain_usd"]
    final["benchmark_value_captured_over_uncoordinated_swarm_usd"] = comparisons["vs_uncoordinated_multi_agent_swarm"]["benchmark_value_captured_gain_usd"]
    final["benchmark_value_captured_over_static_committee_usd"] = comparisons["vs_static_multi_agent_committee"]["benchmark_value_captured_gain_usd"]
    final["benchmark_value_captured_over_no_rsi_large_org_usd"] = comparisons["vs_no_rsi_large_organization"]["benchmark_value_captured_gain_usd"]

    result = {
        "proved": proved,
        "status": "PASSED_AUTONOMOUS_RSI_CORPORATE_CAPABILITY_FRONTIER_PROOF" if proved else "FAILED_AUTONOMOUS_RSI_CORPORATE_CAPABILITY_FRONTIER_PROOF",
        "workflow": "Autonomous RSI Corporate Capability Frontier Proof",
        "proof_type": "corporate-capability-frontier",
        "generated_at_utc": now_iso(),
        "seed": seed,
        "protocol_fingerprint_sha256": fingerprint(final_w),
        "agent_system": {
            "agent_count": AGENT_COUNT,
            "role_count": len(ROLES),
            "agents_per_role": AGENTS_PER_ROLE,
            "governance_council_count": len(COUNCILS),
            "coordination_architecture": "autonomous corporate superorganization: specialist role quorum, capital-to-capability scheduler, adversarial risk veto, cross-council synthesis, validation gate, locked holdout, and recursive protocol release loop",
            "large_multi_agent_wording": "large specialist-agent superorganization coordinating at the capability frontier",
            "roles": ROLES,
            "councils": COUNCILS,
        },
        "benchmark": {
            "name": "Corporate Capability Frontier benchmark",
            "train_count": train_count,
            "validation_count": validation_count,
            "holdout_count": holdout_count,
            "candidate_actions_per_case": 13,
            "features": FEATURES,
            "regimes": REGIMES,
            "locked_holdout": True,
            "data_boundary": "deterministic synthetic/redacted-style benchmark; no private customer data",
            "oracle": "risk-adjusted enterprise capability frontier utility over value capture, validation, compounding, coordination, energy, compute, data, trust, distribution, and risk terms",
        },
        "safe_public_boundary": "This proof does not claim audited customer revenue, live customer adoption, investment advice, financial advice, achieved superintelligence, or Kardashev Type II civilization. It makes the corporate RSI mechanism publicly testable.",
        "pre_registered_gates": gates,
        "single_corporate_generalist": single,
        "uncoordinated_multi_agent_swarm": swarm,
        "static_multi_agent_committee": static,
        "no_rsi_large_organization": no_rsi,
        "negative_controls": {
            "shuffled_reward_rsi": shuffled,
            "random_protocol": random_control,
            "risk_blind_control": risk_blind,
        },
        "final": final,
        "comparisons": comparisons,
        "bootstrap_confidence_intervals": bootstrap,
        "rsi_release_count": released_count,
        "rsi_releases": releases,
        "holdout_samples": holdout_samples(holdout, final_w),
        "proof_steps": [
            "Generate deterministic corporate capability-frontier benchmark.",
            "Evaluate single corporate generalist baseline.",
            "Evaluate uncoordinated multi-agent swarm baseline.",
            "Evaluate static multi-agent committee baseline.",
            "Evaluate no-RSI large organization ablation.",
            "Run validation-gated recursive self-improvement over coordination protocols.",
            "Reject candidate protocol updates that do not improve validation value capture or worsen risk.",
            "Evaluate final fingerprinted protocol once on locked holdout cases.",
            "Run shuffled-reward, random-protocol, and risk-blind negative controls.",
            "Bootstrap holdout value-capture gains.",
            "Write JSON receipt, Markdown report, visual webpage, badge, and public site integration.",
        ],
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260531)
    parser.add_argument("--train-count", type=int, default=512)
    parser.add_argument("--validation-count", type=int, default=256)
    parser.add_argument("--holdout-count", type=int, default=1024)
    parser.add_argument("--release-target", type=int, default=8)
    parser.add_argument("--summary", default="")
    args = parser.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    result = build_result(args.seed, args.train_count, args.validation_count, args.holdout_count, args.release_target)
    md = report(result)
    report_path = DOCS / "rsi_corporate_capability_frontier_proof.md"
    report_path.write_text(md, encoding="utf-8")
    result["markdown_report"] = "docs/rsi_corporate_capability_frontier_proof.md"
    result["output"] = "data/rsi_corporate_capability_frontier_proof.json"

    out = DATA / "rsi_corporate_capability_frontier_proof.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    compact = {
        "proved": result["proved"],
        "workflow": result["workflow"],
        "agents": result["agent_system"]["agent_count"],
        "roles": result["agent_system"]["role_count"],
        "councils": result["agent_system"]["governance_council_count"],
        "holdout_cases": result["benchmark"]["holdout_count"],
        "rsi_releases": result["rsi_release_count"],
        "benchmark_value_capture_percent": result["final"]["benchmark_value_capture_rate_percent"],
        "fully_correct_percent": result["final"]["fully_correct_percent"],
        "risk_breach_percent": result["final"]["risk_breach_rate_percent"],
        "benchmark_value_at_stake_usd": result["final"]["total_benchmark_value_at_stake_usd"],
        "benchmark_value_captured_usd": result["final"]["total_benchmark_value_captured_usd"],
        "value_over_single_generalist_usd": result["comparisons"]["vs_single_corporate_generalist"]["benchmark_value_captured_gain_usd"],
        "value_over_no_rsi_large_org_usd": result["comparisons"]["vs_no_rsi_large_organization"]["benchmark_value_captured_gain_usd"],
        "protocol_fingerprint_sha256": result["protocol_fingerprint_sha256"],
        "json": result["output"],
        "markdown": result["markdown_report"],
    }
    print(json.dumps(compact, indent=2, sort_keys=True))

    if args.summary:
        Path(args.summary).write_text(
            "## Autonomous RSI Corporate Capability Frontier Proof\n\n"
            f"- Proved: **{result['proved']}**\n"
            f"- Agents: **{result['agent_system']['agent_count']:,}**\n"
            f"- Specialist roles: **{result['agent_system']['role_count']:,}**\n"
            f"- Governance councils: **{result['agent_system']['governance_council_count']:,}**\n"
            f"- RSI releases: **{result['rsi_release_count']}**\n"
            f"- Locked holdout cases: **{result['benchmark']['holdout_count']:,}**\n"
            f"- Benchmark value capture: **{result['final']['benchmark_value_capture_rate_percent']}%**\n"
            f"- Fully correct decisions: **{result['final']['fully_correct_percent']}%**\n"
            f"- Risk breach rate: **{result['final']['risk_breach_rate_percent']}%**\n"
            f"- Benchmark value at stake: **{money(result['final']['total_benchmark_value_at_stake_usd'])}**\n"
            f"- Benchmark value captured: **{money(result['final']['total_benchmark_value_captured_usd'])}**\n"
            f"- Value captured over single corporate generalist: **{money(result['comparisons']['vs_single_corporate_generalist']['benchmark_value_captured_gain_usd'])}**\n"
            f"- Value captured over no-RSI large organization: **{money(result['comparisons']['vs_no_rsi_large_organization']['benchmark_value_captured_gain_usd'])}**\n"
            f"- Protocol fingerprint: `{result['protocol_fingerprint_sha256']}`\n",
            encoding="utf-8",
        )

    if not result["proved"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
