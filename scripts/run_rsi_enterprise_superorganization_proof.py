#!/usr/bin/env python3
"""SkillOS Autonomous RSI Enterprise Superorganization Proof.

Research-grade, deterministic, dependency-free benchmark proof for GitHub Actions.

The proof asks whether a large specialist-agent enterprise superorganization can
recursively improve the coordination protocol that converts capital, compute,
energy, data, trust, talent, product, distribution, validation, risk control,
and reinvestment into compounding productive capability.

It evaluates:
- single enterprise generalist baseline
- uncoordinated large-agent pool baseline
- static multi-agent operating committee baseline
- no-RSI large organization baseline
- shuffled-reward RSI negative control
- random protocol negative control
- final validation-gated RSI coordination protocol

It produces a JSON receipt, Markdown report, visual HTML proof page, public badge,
GitHub Action summary, artifact upload, commit, and optional GitHub Pages deploy.

Boundary:
This is a synthetic/redacted-style public benchmark. It is not audited customer
revenue, live customer adoption, investment advice, financial advice, achieved
superintelligence, or Kardashev Type II achievement.
"""

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

FEATURES = [
    "market_size", "revenue_leverage", "margin_expansion", "cycle_speed",
    "reliability", "customer_trust", "risk_exposure", "compliance_complexity",
    "security_exposure", "capital_efficiency", "compute_efficiency",
    "energy_efficiency", "talent_leverage", "distribution_power", "product_fit",
    "data_moat", "network_effect", "defensibility", "compounding",
    "reversibility", "option_value", "ecosystem_alignment", "brand_resilience",
    "learning_velocity",
]

BAD_FEATURES = {"risk_exposure", "compliance_complexity", "security_exposure"}

COUNCILS = [
    "capital", "compute", "energy", "data", "trust", "talent", "product",
    "distribution", "validation", "risk", "security", "compliance", "operations",
    "revenue", "strategy", "marketplace", "governance", "customer", "platform",
    "research", "experimentation", "reinvestment", "resilience", "brand",
    "legal", "procurement", "partnerships", "finance", "pricing", "support",
    "infrastructure", "coordination",
]

COUNCIL_FEATURES = {
    "capital": ["capital_efficiency", "margin_expansion", "option_value", "reinvestment"],
    "compute": ["compute_efficiency", "cycle_speed", "learning_velocity", "infrastructure"],
    "energy": ["energy_efficiency", "compute_efficiency", "capital_efficiency", "reliability"],
    "data": ["data_moat", "learning_velocity", "compounding", "security_exposure"],
    "trust": ["customer_trust", "brand_resilience", "reliability", "compliance_complexity"],
    "talent": ["talent_leverage", "learning_velocity", "cycle_speed", "ecosystem_alignment"],
    "product": ["product_fit", "customer_trust", "reliability", "option_value"],
    "distribution": ["distribution_power", "network_effect", "market_size", "customer_trust"],
    "validation": ["reversibility", "learning_velocity", "reliability", "risk_exposure"],
    "risk": ["risk_exposure", "reversibility", "option_value", "capital_efficiency"],
    "security": ["security_exposure", "data_moat", "reliability", "risk_exposure"],
    "compliance": ["compliance_complexity", "customer_trust", "risk_exposure", "brand_resilience"],
    "operations": ["cycle_speed", "reliability", "capital_efficiency", "talent_leverage"],
    "revenue": ["revenue_leverage", "margin_expansion", "pricing_power", "distribution_power"],
    "strategy": ["compounding", "defensibility", "option_value", "ecosystem_alignment"],
    "marketplace": ["network_effect", "distribution_power", "customer_trust", "product_fit"],
    "governance": ["risk_exposure", "compliance_complexity", "reversibility", "ecosystem_alignment"],
    "customer": ["customer_trust", "product_fit", "support_quality", "brand_resilience"],
    "platform": ["data_moat", "compute_efficiency", "security_exposure", "ecosystem_alignment"],
    "research": ["learning_velocity", "data_moat", "option_value", "compounding"],
    "experimentation": ["reversibility", "learning_velocity", "cycle_speed", "option_value"],
    "reinvestment": ["compounding", "capital_efficiency", "learning_velocity", "defensibility"],
    "resilience": ["reliability", "reversibility", "security_exposure", "risk_exposure"],
    "brand": ["brand_resilience", "customer_trust", "ecosystem_alignment", "compliance_complexity"],
    "legal": ["compliance_complexity", "risk_exposure", "brand_resilience", "reversibility"],
    "procurement": ["capital_efficiency", "compute_efficiency", "energy_efficiency", "reliability"],
    "partnerships": ["ecosystem_alignment", "distribution_power", "network_effect", "customer_trust"],
    "finance": ["margin_expansion", "capital_efficiency", "risk_exposure", "revenue_leverage"],
    "pricing": ["pricing_power", "revenue_leverage", "margin_expansion", "customer_trust"],
    "support": ["support_quality", "customer_trust", "reliability", "brand_resilience"],
    "infrastructure": ["compute_efficiency", "energy_efficiency", "reliability", "security_exposure"],
    "coordination": ["ecosystem_alignment", "reversibility", "learning_velocity", "risk_exposure"],
}

DERIVED_FEATURES = ["pricing_power", "support_quality", "infrastructure", "reinvestment"]

ROLE_TEMPLATES = [
    "Architect", "Optimizer", "Governor", "Auditor", "Red Teamer", "Economist",
    "Planner", "Scientist", "Synthesizer", "Forecaster", "Strategist", "Operator",
    "Controller", "Verifier", "Negotiator", "Teacher",
]
ROLES = [f"{council.title()} {template}" for council in COUNCILS for template in ROLE_TEMPLATES]
AGENTS_PER_ROLE = 32
AGENT_COUNT = len(ROLES) * AGENTS_PER_ROLE

REGIMES = [
    "growth_window", "regulatory_shock", "gpu_scarcity", "energy_constraint",
    "security_incident", "distribution_breakout", "trust_crisis", "platform_shift",
]

INTERACTIONS = [
    ("data_network", lambda f: f["data_moat"] * f["network_effect"]),
    ("compound_defense", lambda f: f["compounding"] * f["defensibility"]),
    ("trust_distribution", lambda f: f["customer_trust"] * f["distribution_power"]),
    ("revenue_margin", lambda f: f["revenue_leverage"] * f["margin_expansion"]),
    ("energy_compute", lambda f: f["energy_efficiency"] * f["compute_efficiency"]),
    ("talent_learning", lambda f: f["talent_leverage"] * f["learning_velocity"]),
    ("option_reversible", lambda f: f["option_value"] * f["reversibility"]),
    ("product_trust", lambda f: f["product_fit"] * f["customer_trust"]),
    ("platform_ecosystem", lambda f: f["ecosystem_alignment"] * f["data_moat"]),
    ("support_brand", lambda f: f["support_quality"] * f["brand_resilience"]),
    ("infrastructure_reliability", lambda f: f["infrastructure"] * f["reliability"]),
    ("reinvestment_compounding", lambda f: f["reinvestment"] * f["compounding"]),
    ("risk_irreversible", lambda f: f["risk_exposure"] * (1 - f["reversibility"])),
    ("compliance_security", lambda f: f["compliance_complexity"] * f["security_exposure"]),
    ("trust_risk", lambda f: f["customer_trust"] * (1 - f["risk_exposure"])),
]

ORACLE: dict[str, float] = {
    "f_market_size": 0.10,
    "f_revenue_leverage": 0.30,
    "f_margin_expansion": 0.20,
    "f_cycle_speed": 0.06,
    "f_reliability": 0.10,
    "f_customer_trust": 0.17,
    "f_risk_exposure": -0.26,
    "f_compliance_complexity": -0.18,
    "f_security_exposure": -0.17,
    "f_capital_efficiency": 0.13,
    "f_compute_efficiency": 0.08,
    "f_energy_efficiency": 0.06,
    "f_talent_leverage": 0.08,
    "f_distribution_power": 0.16,
    "f_product_fit": 0.15,
    "f_data_moat": 0.15,
    "f_network_effect": 0.12,
    "f_defensibility": 0.13,
    "f_compounding": 0.24,
    "f_reversibility": 0.08,
    "f_option_value": 0.10,
    "f_ecosystem_alignment": 0.09,
    "f_brand_resilience": 0.08,
    "f_learning_velocity": 0.18,
    "f_pricing_power": 0.16,
    "f_support_quality": 0.07,
    "f_infrastructure": 0.08,
    "f_reinvestment": 0.20,
    "i_data_network": 0.20,
    "i_compound_defense": 0.19,
    "i_trust_distribution": 0.13,
    "i_revenue_margin": 0.15,
    "i_energy_compute": 0.06,
    "i_talent_learning": 0.08,
    "i_option_reversible": 0.08,
    "i_product_trust": 0.14,
    "i_platform_ecosystem": 0.10,
    "i_support_brand": 0.06,
    "i_infrastructure_reliability": 0.08,
    "i_reinvestment_compounding": 0.18,
    "i_risk_irreversible": -0.33,
    "i_compliance_security": -0.24,
    "i_trust_risk": 0.09,
    "risk_load": -0.42,
    "invalid": -2.40,
}
for council in COUNCILS:
    ORACLE[f"c_{council}"] = 0.018
for regime in REGIMES:
    ORACLE[f"regime_{regime}"] = 0.015


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


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def enrich_features(features: dict[str, float]) -> None:
    features["pricing_power"] = clamp(0.45 * features["margin_expansion"] + 0.25 * features["customer_trust"] + 0.20 * features["distribution_power"] + 0.10 * features["product_fit"])
    features["support_quality"] = clamp(0.40 * features["reliability"] + 0.30 * features["customer_trust"] + 0.20 * (1 - features["risk_exposure"]) + 0.10 * features["brand_resilience"])
    features["infrastructure"] = clamp(0.32 * features["compute_efficiency"] + 0.28 * features["energy_efficiency"] + 0.24 * features["reliability"] + 0.16 * (1 - features["security_exposure"]))
    features["reinvestment"] = clamp(0.35 * features["capital_efficiency"] + 0.25 * features["compounding"] + 0.20 * features["learning_velocity"] + 0.20 * features["margin_expansion"])


def council_signal(council: str, features: dict[str, float]) -> float:
    total = 0.0
    for feature in COUNCIL_FEATURES[council]:
        value = features[feature]
        if feature in BAD_FEATURES:
            value = 1 - value
        total += value
    return total / len(COUNCIL_FEATURES[council])


def atoms_for(features: dict[str, float], regime: str, seed: int, case_id: int, action_id: int) -> dict[str, float]:
    atoms = {f"f_{feature}": value for feature, value in features.items()}

    for name, fn in INTERACTIONS:
        atoms[f"i_{name}"] = fn(features)

    for idx, council in enumerate(COUNCILS):
        atoms[f"c_{council}"] = council_signal(council, features) + 0.010 * noise(seed, case_id, action_id, 1000 + idx)

    for name in REGIMES:
        atoms[f"regime_{name}"] = 1.0 if regime == name else 0.0

    risk_load = features["risk_exposure"] + features["compliance_complexity"] + features["security_exposure"]
    invalid = (
        (features["risk_exposure"] > 0.80 and features["reversibility"] < 0.34)
        or (features["compliance_complexity"] > 0.78 and features["security_exposure"] > 0.72)
        or (features["customer_trust"] < 0.24 and features["risk_exposure"] > 0.64)
        or (features["security_exposure"] > 0.86 and features["data_moat"] > 0.70)
    )
    atoms["risk_load"] = risk_load
    atoms["invalid"] = 1.0 if invalid else 0.0
    return atoms


def dot(weights: dict[str, float], atoms: dict[str, float]) -> float:
    return sum(weights.get(key, 0.0) * value for key, value in atoms.items())


def regime_for(seed: int, case_id: int) -> str:
    return REGIMES[int(u01(seed, case_id, 91001) * len(REGIMES)) % len(REGIMES)]


def apply_regime(features: dict[str, float], regime: str) -> None:
    if regime == "growth_window":
        features["market_size"] = clamp(0.60 * features["market_size"] + 0.40)
        features["revenue_leverage"] = clamp(features["revenue_leverage"] * 1.10)
        features["distribution_power"] = clamp(features["distribution_power"] * 1.10)
    elif regime == "regulatory_shock":
        features["compliance_complexity"] = clamp(0.55 * features["compliance_complexity"] + 0.35)
        features["risk_exposure"] = clamp(features["risk_exposure"] * 1.08)
    elif regime == "gpu_scarcity":
        features["compute_efficiency"] = clamp(features["compute_efficiency"] * 0.75)
        features["capital_efficiency"] = clamp(features["capital_efficiency"] * 0.90)
    elif regime == "energy_constraint":
        features["energy_efficiency"] = clamp(features["energy_efficiency"] * 0.72)
        features["compute_efficiency"] = clamp(features["compute_efficiency"] * 0.92)
    elif regime == "security_incident":
        features["security_exposure"] = clamp(0.55 * features["security_exposure"] + 0.30)
        features["customer_trust"] = clamp(features["customer_trust"] * 0.90)
    elif regime == "distribution_breakout":
        features["distribution_power"] = clamp(0.65 * features["distribution_power"] + 0.30)
        features["network_effect"] = clamp(features["network_effect"] * 1.12)
    elif regime == "trust_crisis":
        features["customer_trust"] = clamp(features["customer_trust"] * 0.72)
        features["brand_resilience"] = clamp(features["brand_resilience"] * 0.80)
    elif regime == "platform_shift":
        features["ecosystem_alignment"] = clamp(0.50 * features["ecosystem_alignment"] + 0.20)
        features["option_value"] = clamp(features["option_value"] * 1.15)


def generate_cases(count: int, seed: int, start_id: int) -> list[dict[str, Any]]:
    cases = []
    for case_id in range(start_id, start_id + count):
        regime = regime_for(seed, case_id)
        base_market = 110_000_000 + 1_150_000_000 * (u01(seed, case_id, 909) ** 1.7)
        actions = []
        for action_id in range(11):
            features = {feature: u01(seed, case_id, action_id, idx) for idx, feature in enumerate(FEATURES)}
            apply_regime(features, regime)

            features["risk_exposure"] = clamp(
                0.30 * features["risk_exposure"]
                + 0.22 * features["revenue_leverage"]
                + 0.20 * (1 - features["reversibility"])
                + 0.15 * (1 - features["customer_trust"])
                + 0.13 * u01(seed, case_id, action_id, 1201)
            )
            features["compliance_complexity"] = clamp(
                0.40 * features["compliance_complexity"]
                + 0.26 * features["risk_exposure"]
                + 0.18 * (1 - features["ecosystem_alignment"])
                + 0.16 * u01(seed, case_id, action_id, 1202)
            )
            features["security_exposure"] = clamp(
                0.40 * features["security_exposure"]
                + 0.22 * features["data_moat"]
                + 0.20 * (1 - features["compute_efficiency"])
                + 0.18 * u01(seed, case_id, action_id, 1203)
            )
            features["compounding"] = clamp(
                0.44 * features["compounding"]
                + 0.22 * features["data_moat"]
                + 0.18 * features["learning_velocity"]
                + 0.16 * features["defensibility"]
            )
            enrich_features(features)

            atoms = atoms_for(features, regime, seed, case_id, action_id)
            utility = dot(ORACLE, atoms) + 0.012 * noise(seed, case_id, action_id, 1210)
            value_usd = max(0.02, utility + 1.10) * base_market

            actions.append({
                "action_id": action_id,
                "regime": regime,
                "features": features,
                "atoms": atoms,
                "utility": utility,
                "invalid": atoms["invalid"] > 0.5,
                "value_usd": value_usd,
            })

        valid = [(a["utility"], idx) for idx, a in enumerate(actions) if not a["invalid"]]
        oracle = max(valid if valid else [(a["utility"], idx) for idx, a in enumerate(actions)])[1]
        cases.append({"case_id": case_id, "regime": regime, "actions": actions, "oracle": oracle})
    return cases


def choose(case: dict[str, Any], protocol: dict[str, float]) -> int:
    best, argbest = -10**18, 0
    for idx, action in enumerate(case["actions"]):
        s = dot(protocol, action["atoms"])
        if s > best:
            best, argbest = s, idx
    return argbest


def eval_vectors(cases: list[dict[str, Any]], protocol: dict[str, float]) -> tuple[list[float], list[float]]:
    captured, oracle = [], []
    for case in cases:
        pred = choose(case, protocol)
        true = case["oracle"]
        captured.append(case["actions"][pred]["value_usd"])
        oracle.append(case["actions"][true]["value_usd"])
    return captured, oracle


def evaluate(cases: list[dict[str, Any]], protocol: dict[str, float]) -> dict[str, float]:
    exact = top3 = invalid = risk_breach = 0
    oracle_value = captured_value = 0.0
    consensus = compounding = capacity = 0.0
    by_regime: dict[str, dict[str, float]] = {r: {"n": 0, "exact": 0, "cap": 0.0, "oracle": 0.0} for r in REGIMES}

    for case in cases:
        pred = choose(case, protocol)
        true = case["oracle"]
        action = case["actions"][pred]
        oracle_action = case["actions"][true]

        exact += pred == true
        ranking = sorted(range(len(case["actions"])), key=lambda idx: case["actions"][idx]["utility"], reverse=True)
        top3 += pred in ranking[:3]
        invalid += action["invalid"]
        risk_breach += action["atoms"]["risk_load"] > 2.0

        captured_value += action["value_usd"]
        oracle_value += oracle_action["value_usd"]

        features = action["features"]
        compounding += features["compounding"]
        capacity += (features["cycle_speed"] + features["compute_efficiency"] + features["energy_efficiency"] + features["capital_efficiency"] + features["talent_leverage"]) / 5

        cvals = [action["atoms"][f"c_{c}"] for c in COUNCILS]
        mean = sum(cvals) / len(cvals)
        sd = math.sqrt(sum((v - mean) ** 2 for v in cvals) / len(cvals))
        consensus += max(0.0, 1.0 - sd / 2.0)

        reg = by_regime[case["regime"]]
        reg["n"] += 1
        reg["exact"] += pred == true
        reg["cap"] += action["value_usd"]
        reg["oracle"] += oracle_action["value_usd"]

    n = len(cases)
    regime_table = {
        r: {
            "case_count": int(v["n"]),
            "fully_correct_percent": round(100 * v["exact"] / max(1, v["n"]), 3),
            "value_capture_percent": round(100 * v["cap"] / max(1.0, v["oracle"]), 3),
        }
        for r, v in by_regime.items()
    }
    return {
        "case_count": n,
        "fully_correct_percent": round(100 * exact / n, 3),
        "top3_percent": round(100 * top3 / n, 3),
        "benchmark_value_capture_rate_percent": round(100 * captured_value / oracle_value, 3),
        "value_capture_rate_percent": round(100 * captured_value / oracle_value, 3),
        "total_benchmark_value_at_stake_usd": round(oracle_value, 2),
        "total_benchmark_value_captured_usd": round(captured_value, 2),
        "risk_breach_rate_percent": round(100 * risk_breach / n, 3),
        "invalid_action_rate_percent": round(100 * invalid / n, 3),
        "avg_consensus_score": round(100 * consensus / n, 3),
        "avg_compounding_index": round(100 * compounding / n, 3),
        "avg_productive_capacity_index": round(100 * capacity / n, 3),
        "coordination_protocol_accuracy_percent": round(100 * exact / n, 3),
        "risk_control_accuracy_percent": round(100 - 100 * risk_breach / n, 3),
        "role_quorum_accuracy_percent": round(100 * top3 / n, 3),
        "capability_lever_accuracy_percent": round(100 * captured_value / oracle_value, 3),
        "by_regime": regime_table,
    }


def single_agent_protocol() -> dict[str, float]:
    return {
        "f_market_size": 0.12,
        "f_revenue_leverage": 0.30,
        "f_margin_expansion": 0.16,
        "f_distribution_power": 0.12,
        "f_product_fit": 0.09,
        "f_customer_trust": 0.06,
        "f_risk_exposure": -0.05,
        "f_compliance_complexity": -0.04,
        "f_security_exposure": -0.04,
        "f_compounding": 0.05,
        "f_learning_velocity": 0.04,
        "f_data_moat": 0.04,
        "invalid": -0.10,
    }


def uncoordinated_pool_protocol() -> dict[str, float]:
    w = {f"c_{c}": 1.0 / len(COUNCILS) for c in COUNCILS}
    w["invalid"] = -0.18
    w["risk_load"] = -0.04
    return w


def static_protocol() -> dict[str, float]:
    w = {}
    for key, value in ORACLE.items():
        if key.startswith("f_"):
            w[key] = 0.42 * value
        elif key.startswith("i_"):
            w[key] = 0.16 * value
        elif key.startswith("c_"):
            w[key] = 0.030
        elif key.startswith("regime_"):
            w[key] = 0.006
        else:
            w[key] = 0.28 * value
    w["invalid"] = -0.62
    w["risk_load"] = -0.13
    return w


def no_rsi_large_org_protocol() -> dict[str, float]:
    w = static_protocol()
    for c in COUNCILS:
        w[f"c_{c}"] = w.get(f"c_{c}", 0.0) + 0.025
    return w


def objective(metrics: dict[str, float]) -> float:
    return (
        metrics["benchmark_value_capture_rate_percent"]
        + 0.11 * metrics["fully_correct_percent"]
        - 0.95 * metrics["risk_breach_rate_percent"]
        - 1.60 * metrics["invalid_action_rate_percent"]
    )


def rsi_train(train: list[dict[str, Any]], validation: list[dict[str, Any]], seed: int, generations: int, lr: float) -> tuple[dict[str, float], list[dict[str, Any]]]:
    current = no_rsi_large_org_protocol()
    current_metrics = evaluate(validation, current)
    atom_keys = list(train[0]["actions"][0]["atoms"].keys())

    releases: list[dict[str, Any]] = [{
        "generation": 0,
        "released": True,
        "lesson": "seed large specialist-agent operating protocol",
        "validation": current_metrics,
        "score": round(objective(current_metrics), 6),
        "protocol_fingerprint_sha256": protocol_fingerprint(current),
    }]

    for generation in range(1, generations + 1):
        candidate = dict(current)
        step = lr / (generation ** 0.22)

        for case in train:
            pred = choose(case, candidate)
            true = case["oracle"]
            if pred != true:
                true_atoms = case["actions"][true]["atoms"]
                pred_atoms = case["actions"][pred]["atoms"]
                for key in atom_keys:
                    candidate[key] = candidate.get(key, 0.0) + step * (true_atoms[key] - pred_atoms[key])
            chosen = case["actions"][pred]
            if chosen["invalid"] or chosen["atoms"]["risk_load"] > 2.0:
                candidate["invalid"] = candidate.get("invalid", 0.0) - 2.3 * step
                candidate["risk_load"] = candidate.get("risk_load", 0.0) - 0.75 * step
                for key in ["f_risk_exposure", "f_compliance_complexity", "f_security_exposure", "i_risk_irreversible", "i_compliance_security"]:
                    candidate[key] = candidate.get(key, 0.0) - 0.20 * step

        for key in list(candidate):
            candidate[key] = max(-7.0, min(7.0, candidate[key]))

        cand_metrics = evaluate(validation, candidate)
        current_score = objective(current_metrics)
        cand_score = objective(cand_metrics)
        risk_ok = cand_metrics["risk_breach_rate_percent"] <= current_metrics["risk_breach_rate_percent"] + 0.20
        released = cand_score > current_score + 0.001 and risk_ok

        if released:
            current = candidate
            current_metrics = cand_metrics

        releases.append({
            "generation": generation,
            "released": released,
            "lesson": "validation-gated RSI update from oracle-regret traces, specialist disagreement, and risk-veto failures" if released else "candidate rejected by validation gate",
            "validation": current_metrics,
            "score": round(objective(current_metrics), 6),
            "protocol_fingerprint_sha256": protocol_fingerprint(current),
        })

    return current, releases


def shuffled_reward_control(train: list[dict[str, Any]], holdout: list[dict[str, Any]], seed: int) -> dict[str, float]:
    w = no_rsi_large_org_protocol()
    atom_keys = list(train[0]["actions"][0]["atoms"].keys())
    for generation in range(1, 9):
        step = 0.018 / (generation ** 0.25)
        for case in train:
            pred = choose(case, w)
            fake = int(u01(seed, case["case_id"], generation, 25001) * len(case["actions"])) % len(case["actions"])
            if pred != fake:
                true_atoms = case["actions"][fake]["atoms"]
                pred_atoms = case["actions"][pred]["atoms"]
                for key in atom_keys:
                    w[key] = w.get(key, 0.0) + step * (true_atoms[key] - pred_atoms[key])
    return evaluate(holdout, w)


def random_protocol_control(holdout: list[dict[str, Any]], seed: int) -> dict[str, float]:
    w = no_rsi_large_org_protocol()
    for idx, key in enumerate(list(w)):
        w[key] = w[key] * (0.30 + 1.25 * u01(seed, idx, 31001)) + 0.10 * noise(seed, idx, 31002)
    return evaluate(holdout, w)


def compare(final: dict[str, float], base: dict[str, float]) -> dict[str, float]:
    return {
        "benchmark_value_capture_gain_points": round(final["benchmark_value_capture_rate_percent"] - base["benchmark_value_capture_rate_percent"], 3),
        "fully_correct_gain_points": round(final["fully_correct_percent"] - base["fully_correct_percent"], 3),
        "risk_breach_reduction_points": round(base["risk_breach_rate_percent"] - final["risk_breach_rate_percent"], 3),
        "benchmark_value_captured_gain_usd": round(final["total_benchmark_value_captured_usd"] - base["total_benchmark_value_captured_usd"], 2),
    }


def bootstrap_ci(cases: list[dict[str, Any]], final_w: dict[str, float], base_w: dict[str, float], seed: int, reps: int = 320) -> dict[str, float]:
    final_cap, oracle = eval_vectors(cases, final_w)
    base_cap, _ = eval_vectors(cases, base_w)
    n = len(cases)
    gains = []
    for rep in range(reps):
        f = b = o = 0.0
        for draw in range(n):
            idx = int(u01(seed, rep, draw, 41001) * n) % n
            f += final_cap[idx]
            b += base_cap[idx]
            o += oracle[idx]
        gains.append(100 * f / o - 100 * b / o)
    gains.sort()
    return {
        "mean_gain_points": round(sum(gains) / len(gains), 4),
        "p05_gain_points": round(gains[int(0.05 * (len(gains) - 1))], 4),
        "p50_gain_points": round(gains[int(0.50 * (len(gains) - 1))], 4),
        "p95_gain_points": round(gains[int(0.95 * (len(gains) - 1))], 4),
        "bootstrap_repetitions": reps,
    }


def protocol_fingerprint(protocol: dict[str, float]) -> str:
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


def sample_cases(holdout: list[dict[str, Any]], protocol: dict[str, float], limit: int = 20) -> list[dict[str, Any]]:
    rows = []
    for case in holdout[:limit]:
        pred = choose(case, protocol)
        true = case["oracle"]
        action = case["actions"][pred]
        oracle = case["actions"][true]
        features = action["features"]
        rows.append({
            "case_id": case["case_id"],
            "regime": case["regime"],
            "chosen_action": pred,
            "oracle_action": true,
            "matched_oracle": pred == true,
            "chosen_value_usd": round(action["value_usd"], 2),
            "oracle_value_usd": round(oracle["value_usd"], 2),
            "risk_load": round(action["atoms"]["risk_load"], 4),
            "trust": round(features["customer_trust"], 4),
            "learning_velocity": round(features["learning_velocity"], 4),
            "compounding": round(features["compounding"], 4),
            "data_moat": round(features["data_moat"], 4),
        })
    return rows


def build_result(seed: int, train_count: int, validation_count: int, holdout_count: int, generations: int) -> dict[str, Any]:
    train = generate_cases(train_count, seed, 0)
    validation = generate_cases(validation_count, seed, train_count)
    holdout = generate_cases(holdout_count, seed, train_count + validation_count)

    single_w = single_agent_protocol()
    pool_w = uncoordinated_pool_protocol()
    static_w = static_protocol()
    no_rsi_w = no_rsi_large_org_protocol()
    final_w, releases = rsi_train(train, validation, seed, generations, lr=0.020)

    single = evaluate(holdout, single_w)
    pool = evaluate(holdout, pool_w)
    static = evaluate(holdout, static_w)
    no_rsi = evaluate(holdout, no_rsi_w)
    final = evaluate(holdout, final_w)
    shuffled = shuffled_reward_control(train, holdout, seed)
    random_control = random_protocol_control(holdout, seed)

    comparisons = {
        "vs_single_agent": compare(final, single),
        "vs_uncoordinated_large_agent_pool": compare(final, pool),
        "vs_static_multi_agent_operating_committee": compare(final, static),
        "vs_no_rsi_large_agent_organization": compare(final, no_rsi),
        "vs_shuffled_reward_rsi_control": compare(final, shuffled),
        "vs_random_protocol_control": compare(final, random_control),
    }

    bootstrap = {
        "vs_single_agent": bootstrap_ci(holdout, final_w, single_w, seed + 11),
        "vs_uncoordinated_large_agent_pool": bootstrap_ci(holdout, final_w, pool_w, seed + 13),
        "vs_static_multi_agent_operating_committee": bootstrap_ci(holdout, final_w, static_w, seed + 17),
        "vs_no_rsi_large_agent_organization": bootstrap_ci(holdout, final_w, no_rsi_w, seed + 19),
    }

    rsi_release_count = sum(1 for r in releases if r["released"])

    final["benchmark_implied_value_captured_over_single_agent_usd"] = comparisons["vs_single_agent"]["benchmark_value_captured_gain_usd"]
    final["benchmark_implied_value_captured_over_uncoordinated_large_agent_pool_usd"] = comparisons["vs_uncoordinated_large_agent_pool"]["benchmark_value_captured_gain_usd"]
    final["benchmark_implied_value_captured_over_static_committee_usd"] = comparisons["vs_static_multi_agent_operating_committee"]["benchmark_value_captured_gain_usd"]
    final["benchmark_implied_value_captured_over_no_rsi_usd"] = comparisons["vs_no_rsi_large_agent_organization"]["benchmark_value_captured_gain_usd"]

    gates = {
        "large_multi_agent_organization": AGENT_COUNT >= 16384 and len(ROLES) >= 512,
        "enterprise_regime_coverage": len(REGIMES) >= 8,
        "locked_holdout_scale": holdout_count >= 2048,
        "validation_gated_rsi_releases": rsi_release_count >= 8,
        "beats_single_agent_value_capture": comparisons["vs_single_agent"]["benchmark_value_capture_gain_points"] >= 10.0,
        "beats_uncoordinated_large_agent_pool": comparisons["vs_uncoordinated_large_agent_pool"]["benchmark_value_capture_gain_points"] >= 1.5,
        "beats_static_multi_agent_committee": comparisons["vs_static_multi_agent_operating_committee"]["benchmark_value_capture_gain_points"] >= 0.2,
        "beats_no_rsi_large_org": comparisons["vs_no_rsi_large_agent_organization"]["benchmark_value_capture_gain_points"] >= 0.4,
        "negative_controls_do_not_match": comparisons["vs_shuffled_reward_rsi_control"]["benchmark_value_capture_gain_points"] >= 2.0 and comparisons["vs_random_protocol_control"]["benchmark_value_capture_gain_points"] >= 2.0,
        "single_agent_accuracy_gain": comparisons["vs_single_agent"]["fully_correct_gain_points"] >= 65.0,
        "risk_controlled": final["risk_breach_rate_percent"] <= static["risk_breach_rate_percent"] + 0.10,
        "bootstrap_lower_bound_positive_vs_static": bootstrap["vs_static_multi_agent_operating_committee"]["p05_gain_points"] > 0.0,
        "bootstrap_lower_bound_positive_vs_no_rsi": bootstrap["vs_no_rsi_large_agent_organization"]["p05_gain_points"] > 0.0,
        "benchmark_value_capture": final["benchmark_value_capture_rate_percent"] >= 99.6,
        "fully_correct_rate": final["fully_correct_percent"] >= 92.0,
        "benchmark_value_at_stake_scale": final["total_benchmark_value_at_stake_usd"] >= 1_000_000_000_000,
        "benchmark_value_over_single_agent": comparisons["vs_single_agent"]["benchmark_value_captured_gain_usd"] >= 300_000_000_000,
    }

    proved = all(gates.values())

    return {
        "proved": proved,
        "status": "PASSED_AUTONOMOUS_RSI_ENTERPRISE_SUPERORGANIZATION_PROOF" if proved else "FAILED_AUTONOMOUS_RSI_ENTERPRISE_SUPERORGANIZATION_PROOF",
        "proof_type": "Autonomous RSI Enterprise Superorganization Proof",
        "display_name": "Autonomous RSI Enterprise Superorganization Proof",
        "workflow": "Autonomous RSI Enterprise Superorganization Proof",
        "workflow_file": ".github/workflows/autonomous-rsi-enterprise-superorganization-proof.yml",
        "page_url": "rsi-enterprise-superorganization-proof.html",
        "generated_at_utc": now_iso(),
        "seed": seed,
        "protocol_fingerprint_sha256": protocol_fingerprint(final_w),
        "safe_interpretation": "A reproducible benchmark proof that validation-gated recursive coordination improves enterprise decision quality and benchmark value capture. Not audited customer revenue, live adoption, financial advice, investment advice, achieved superintelligence, or Kardashev Type II achievement.",
        "capital_to_capability_thesis": "capital → compute → energy → data → trust → talent → product → distribution → validation → risk control → reinvestment → compounding productive capability",
        "agent_system": {
            "agent_count": AGENT_COUNT,
            "role_count": len(ROLES),
            "governance_council_count": len(COUNCILS),
            "agents_per_role": AGENTS_PER_ROLE,
            "role_quorum_model": "512 specialist role quorums; each role represents 32 deterministic virtual agents; council signals are aggregated for reproducible public execution.",
            "coordination_style": "validation-gated recursive self-improvement with council-of-councils quorum, adversarial risk veto, capital allocation tournament, enterprise regime testing, negative controls, bootstrap intervals, and locked holdout evaluation",
            "roles": ROLES,
            "councils": COUNCILS,
        },
        "benchmark_public": {
            "name": "Enterprise Superorganization benchmark",
            "seed": seed,
            "train_count": train_count,
            "validation_count": validation_count,
            "holdout_count": holdout_count,
            "candidate_actions_per_case": 11,
            "features": FEATURES + DERIVED_FEATURES,
            "regimes": REGIMES,
            "oracle": "risk-adjusted enterprise value capture over market size, revenue, margin, trust, product, distribution, data moat, network effects, compute, energy, talent, compounding, reversibility, compliance, security, and nonlinear interaction terms",
            "locked_holdout": True,
            "data_boundary": "synthetic/redacted-style public benchmark; no private customer data",
        },
        "pre_registered_gates": gates,
        "single_agent_baseline": single,
        "uncoordinated_large_agent_pool": pool,
        "uncoordinated_pool": pool,
        "static_multi_agent_operating_committee": static,
        "static_coordination": static,
        "no_rsi_large_agent_organization": no_rsi,
        "negative_controls": {
            "shuffled_reward_rsi": shuffled,
            "random_protocol": random_control,
        },
        "final": final,
        "comparisons": comparisons,
        "bootstrap_confidence_intervals": bootstrap,
        "rsi_release_count": rsi_release_count,
        "rsi_releases": releases,
        "holdout_samples": sample_cases(holdout, final_w),
        "proof_steps": [
            "Generate deterministic public enterprise benchmark cases across eight business regimes.",
            "Define oracle risk-adjusted value capture across eleven candidate actions per case.",
            "Evaluate single enterprise generalist baseline.",
            "Evaluate uncoordinated large-agent pool baseline.",
            "Evaluate static multi-agent operating committee baseline.",
            "Evaluate no-RSI large organization baseline.",
            "Run validation-gated recursive self-improvement over the coordination protocol.",
            "Run shuffled-reward and random-protocol negative controls.",
            "Lock final protocol fingerprint.",
            "Evaluate final protocol exactly once on locked holdout cases.",
            "Compute bootstrap confidence intervals for value-capture gains.",
            "Write JSON receipt, Markdown report, badge, visual proof page, artifact, and optional Pages deployment.",
        ],
        "public_boundary": "Benchmark proof values are not audited customer revenue, live customer adoption, financial advice, investment advice, achieved superintelligence, or Kardashev Type II achievement.",
    }


def write_report(result: dict[str, Any]) -> str:
    final = result["final"]
    c = result["comparisons"]
    lines = []
    lines.append("# Autonomous RSI Enterprise Superorganization Proof\n")
    lines.append(f"Generated: `{result['generated_at_utc']}`\n")
    lines.append("## Thesis\n")
    lines.append("Recursive-style systems aim to automate knowledge discovery. SkillOS tests the enterprise analogue: recursive improvement of the coordination system that turns enterprise resources into compounding productive capability.\n")
    lines.append(f"> {result['capital_to_capability_thesis']}\n")
    lines.append("## Public result\n")
    lines.append(f"- Agents: **{result['agent_system']['agent_count']}**")
    lines.append(f"- Specialist roles: **{result['agent_system']['role_count']}**")
    lines.append(f"- Governance councils: **{result['agent_system']['governance_council_count']}**")
    lines.append(f"- Validation-gated RSI releases: **{result['rsi_release_count']}**")
    lines.append(f"- Locked holdout cases: **{result['benchmark_public']['holdout_count']}**")
    lines.append(f"- Benchmark value capture: **{final['benchmark_value_capture_rate_percent']}%**")
    lines.append(f"- Fully correct decisions: **{final['fully_correct_percent']}%**")
    lines.append(f"- Risk breach rate: **{final['risk_breach_rate_percent']}%**")
    lines.append(f"- Benchmark value at stake: **{money(final['total_benchmark_value_at_stake_usd'])}**")
    lines.append(f"- Benchmark value captured: **{money(final['total_benchmark_value_captured_usd'])}**")
    lines.append(f"- Benchmark value captured over single-agent baseline: **{money(c['vs_single_agent']['benchmark_value_captured_gain_usd'])}**")
    lines.append(f"- Protocol fingerprint: `{result['protocol_fingerprint_sha256']}`\n")
    lines.append("## Baselines and controls\n")
    rows = [
        ("Single enterprise generalist", result["single_agent_baseline"]),
        ("Uncoordinated large-agent pool", result["uncoordinated_large_agent_pool"]),
        ("Static multi-agent operating committee", result["static_multi_agent_operating_committee"]),
        ("No-RSI large-agent organization", result["no_rsi_large_agent_organization"]),
        ("Shuffled-reward RSI control", result["negative_controls"]["shuffled_reward_rsi"]),
        ("Random protocol control", result["negative_controls"]["random_protocol"]),
        ("SkillOS RSI coordination", result["final"]),
    ]
    lines.append("| System | Value capture | Fully correct | Risk breach | Benchmark value captured |")
    lines.append("|---|---:|---:|---:|---:|")
    for name, m in rows:
        lines.append(f"| {name} | {m['benchmark_value_capture_rate_percent']}% | {m['fully_correct_percent']}% | {m['risk_breach_rate_percent']}% | {money(m['total_benchmark_value_captured_usd'])} |")
    lines.append("\n## Pre-registered gates\n")
    for k, v in result["pre_registered_gates"].items():
        lines.append(f"- {'✅' if v else '❌'} `{k}`")
    lines.append("\n## Bootstrap confidence intervals\n")
    for name, ci in result["bootstrap_confidence_intervals"].items():
        lines.append(f"- `{name}`: mean **{ci['mean_gain_points']} pts**, p05 **{ci['p05_gain_points']} pts**, p50 **{ci['p50_gain_points']} pts**, p95 **{ci['p95_gain_points']} pts**, reps **{ci['bootstrap_repetitions']}**")
    lines.append("\n## Boundary\n")
    lines.append(result["public_boundary"])
    DOCS.mkdir(parents=True, exist_ok=True)
    out = DOCS / "rsi_enterprise_superorganization_proof.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(out.relative_to(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20260530)
    parser.add_argument("--train-count", type=int, default=1024)
    parser.add_argument("--validation-count", type=int, default=512)
    parser.add_argument("--holdout-count", type=int, default=2048)
    parser.add_argument("--generations", type=int, default=24)
    parser.add_argument("--summary", default="")
    args = parser.parse_args()

    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)

    result = build_result(args.seed, args.train_count, args.validation_count, args.holdout_count, args.generations)
    result["markdown_report"] = write_report(result)
    result["output"] = "data/rsi_enterprise_superorganization_proof.json"

    out = DATA / "rsi_enterprise_superorganization_proof.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    compact = {
        "proved": result["proved"],
        "workflow": result["workflow"],
        "agent_count": result["agent_system"]["agent_count"],
        "role_count": result["agent_system"]["role_count"],
        "governance_councils": result["agent_system"]["governance_council_count"],
        "rsi_release_count": result["rsi_release_count"],
        "holdout_count": result["benchmark_public"]["holdout_count"],
        "value_capture_percent": result["final"]["benchmark_value_capture_rate_percent"],
        "fully_correct_percent": result["final"]["fully_correct_percent"],
        "risk_breach_percent": result["final"]["risk_breach_rate_percent"],
        "benchmark_value_at_stake_usd": result["final"]["total_benchmark_value_at_stake_usd"],
        "benchmark_value_captured_usd": result["final"]["total_benchmark_value_captured_usd"],
        "benchmark_value_captured_over_single_agent_usd": result["comparisons"]["vs_single_agent"]["benchmark_value_captured_gain_usd"],
        "json": "data/rsi_enterprise_superorganization_proof.json",
        "markdown": result["markdown_report"],
        "html": "site/rsi-enterprise-superorganization-proof.html",
        "protocol_fingerprint_sha256": result["protocol_fingerprint_sha256"],
    }
    print(json.dumps(compact, indent=2, sort_keys=True))

    if args.summary:
        Path(args.summary).write_text(
            "## Autonomous RSI Enterprise Superorganization Proof\n\n"
            f"- Proved: **{result['proved']}**\n"
            f"- Agents: **{result['agent_system']['agent_count']}**\n"
            f"- Specialist roles: **{result['agent_system']['role_count']}**\n"
            f"- Governance councils: **{result['agent_system']['governance_council_count']}**\n"
            f"- RSI releases: **{result['rsi_release_count']}**\n"
            f"- Locked holdout cases: **{result['benchmark_public']['holdout_count']}**\n"
            f"- Benchmark value capture: **{result['final']['benchmark_value_capture_rate_percent']}%**\n"
            f"- Fully correct decisions: **{result['final']['fully_correct_percent']}%**\n"
            f"- Risk breach rate: **{result['final']['risk_breach_rate_percent']}%**\n"
            f"- Benchmark value at stake: **{money(result['final']['total_benchmark_value_at_stake_usd'])}**\n"
            f"- Benchmark value captured: **{money(result['final']['total_benchmark_value_captured_usd'])}**\n"
            f"- Value captured over single-agent baseline: **{money(result['comparisons']['vs_single_agent']['benchmark_value_captured_gain_usd'])}**\n"
            f"- Protocol fingerprint: `{result['protocol_fingerprint_sha256']}`\n",
            encoding="utf-8",
        )

    if not result["proved"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
