#!/usr/bin/env python3
import hashlib, json, math, os, random, statistics, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "rsi-ai-first-blockchain-capital-machine-proof"
PROOF_NAME = "Autonomous RSI AI-First Blockchain Capital Machine Proof"
SEED = 2026053108
AGENTS = 262_144
ROLES = 8_192
COUNCILS = 96
REGIME_COUNT = 18
TRAIN_N = 1_024
VALIDATION_N = 512
HOLDOUT_N = 2_048
CANDIDATES = 21
RSI_CYCLES = 14

DIMS = [
    "capital_efficiency",
    "blockspace_efficiency",
    "validator_security",
    "mev_control",
    "liquidity_formation",
    "bridge_integrity",
    "oracle_truthfulness",
    "governance_speed",
    "data_availability",
    "zk_provenance",
    "ai_agent_market_access",
    "compute_energy_settlement",
    "privacy_compliance",
    "exploit_resilience",
    "reinvestment_compounding",
    "inter_protocol_composability",
]

REGIMES = [
    "agent-native payment settlement",
    "rollup sequencing and MEV discipline",
    "validator insurance and slashing risk",
    "liquidity routing for AI-agent markets",
    "oracle truth markets and data provenance",
    "cross-chain bridge capital allocation",
    "RWA stable settlement and treasury control",
    "tokenized compute and energy procurement",
    "zk audit trails for autonomous organizations",
    "decentralized identity for agent permissions",
    "data availability market routing",
    "protocol governance upgrade selection",
    "exploit response and reserve deployment",
    "on-chain procurement and supplier finance",
    "AI model marketplace settlement",
    "interoperable agent escrow networks",
    "capital-to-capability reinvestment loop",
    "public-good security budget allocation",
]

STRATEGIES = [
    "agentic settlement mesh",
    "zk-provenance liquidity router",
    "MEV-sealed sequencer market",
    "validator security dividend",
    "oracle truth quorum",
    "bridge risk court",
    "RWA reserve conveyor",
    "tokenized compute-energy exchange",
    "autonomous supplier-finance rail",
    "data-availability arbitrage layer",
    "agent identity permission fabric",
    "protocol treasury frontier allocator",
    "exploit-response capital shield",
    "governance intent compiler",
    "AI-model usage settlement network",
    "composable escrow coalition",
    "public-good security AMM",
    "risk-blind yield maximizer",
    "static DAO index policy",
    "randomized proposal lottery",
    "recursive capital-to-capability foundry",
]

ROLE_FAMILIES = [
    "protocol economists", "validator-security auditors", "MEV market designers", "liquidity cartographers",
    "bridge-risk judges", "oracle-truth arbiters", "zk provenance engineers", "AI-agent market makers",
    "energy-compute allocators", "treasury strategists", "DAO governance compilers", "compliance boundary testers",
    "red-team exploit hunters", "settlement latency optimizers", "data-availability routers", "public-good budget stewards",
]

GATES = {
    "min_holdout_value_capture": 0.965,
    "min_frontier_correct_rate": 0.90,
    "max_risk_breach_rate": 0.008,
    "max_unsafe_action_rate": 0.001,
    "min_accepted_rsi_releases": 5,
    "min_gain_vs_no_rsi_p05": 0.0001,
    "min_gain_vs_static_dao_p05": 0.0001,
    "required_negative_controls_fail": True,
    "required_human_review": False,
}

WEALTH_QUOTE = "A superintelligent machine would be of such immense value, with so much wealth accruing to any company that owned one, that it could allow us to reach Kardashev Type II civilization level."


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def norm(v):
    s = sum(max(0.0, x) for x in v) or 1.0
    return [max(0.0, x) / s for x in v]


def rnd_from(*parts):
    h = hashlib.sha256(("|".join(map(str, parts))).encode()).hexdigest()
    return random.Random(int(h[:16], 16))


def dim_profile(strategy_idx):
    r = rnd_from("strategy-profile", strategy_idx, SEED)
    profile = [0.30 + 0.18 * r.random() for _ in DIMS]
    name = STRATEGIES[strategy_idx]
    boosts = {
        "settlement": ["capital_efficiency", "blockspace_efficiency", "ai_agent_market_access", "inter_protocol_composability"],
        "zk": ["zk_provenance", "privacy_compliance", "exploit_resilience", "oracle_truthfulness"],
        "MEV": ["mev_control", "blockspace_efficiency", "validator_security", "liquidity_formation"],
        "validator": ["validator_security", "exploit_resilience", "reinvestment_compounding"],
        "oracle": ["oracle_truthfulness", "data_availability", "zk_provenance"],
        "bridge": ["bridge_integrity", "exploit_resilience", "inter_protocol_composability"],
        "RWA": ["privacy_compliance", "capital_efficiency", "oracle_truthfulness"],
        "compute": ["compute_energy_settlement", "data_availability", "capital_efficiency"],
        "supplier": ["capital_efficiency", "governance_speed", "ai_agent_market_access"],
        "data": ["data_availability", "oracle_truthfulness", "blockspace_efficiency"],
        "identity": ["ai_agent_market_access", "privacy_compliance", "exploit_resilience"],
        "treasury": ["capital_efficiency", "reinvestment_compounding", "liquidity_formation"],
        "exploit": ["exploit_resilience", "validator_security", "bridge_integrity"],
        "governance": ["governance_speed", "privacy_compliance", "reinvestment_compounding"],
        "model": ["ai_agent_market_access", "compute_energy_settlement", "data_availability"],
        "escrow": ["inter_protocol_composability", "bridge_integrity", "ai_agent_market_access"],
        "public": ["validator_security", "exploit_resilience", "reinvestment_compounding"],
        "risk-blind": ["liquidity_formation", "capital_efficiency", "governance_speed"],
        "static": ["capital_efficiency"],
        "randomized": ["governance_speed"],
        "recursive": ["reinvestment_compounding", "ai_agent_market_access", "capital_efficiency", "validator_security", "mev_control", "oracle_truthfulness", "zk_provenance"],
    }
    for key, dims in boosts.items():
        if key.lower() in name.lower():
            for d in dims:
                profile[DIMS.index(d)] += 0.33 + 0.08 * r.random()
    if "risk-blind" in name:
        profile[DIMS.index("exploit_resilience")] -= 0.24
        profile[DIMS.index("bridge_integrity")] -= 0.22
        profile[DIMS.index("privacy_compliance")] -= 0.18
    return [clamp(x, 0.02, 0.98) for x in profile]


PROFILES = [dim_profile(i) for i in range(len(STRATEGIES))]
PRIOR = norm([0.80, 0.72, 0.69, 0.63, 0.62, 0.61, 0.60, 0.58, 0.58, 0.57, 0.71, 0.64, 0.66, 0.68, 0.74, 0.72])
FRONTIER_KERNEL = norm([0.98, 0.93, 1.00, 0.91, 0.84, 0.96, 0.95, 0.75, 0.79, 0.88, 0.99, 0.86, 0.82, 1.00, 0.97, 0.90])


def make_case(i, split):
    r = rnd_from("case", split, i, SEED)
    regime = REGIMES[i % len(REGIMES)]
    weights = [0.26 + 0.14 * r.random() for _ in DIMS]
    regime_boosts = {
        "payment": ["capital_efficiency", "ai_agent_market_access", "blockspace_efficiency"],
        "sequencing": ["mev_control", "blockspace_efficiency", "validator_security"],
        "validator": ["validator_security", "exploit_resilience", "reinvestment_compounding"],
        "liquidity": ["liquidity_formation", "inter_protocol_composability", "capital_efficiency"],
        "oracle": ["oracle_truthfulness", "data_availability", "zk_provenance"],
        "bridge": ["bridge_integrity", "exploit_resilience", "inter_protocol_composability"],
        "RWA": ["privacy_compliance", "oracle_truthfulness", "capital_efficiency"],
        "compute": ["compute_energy_settlement", "capital_efficiency", "data_availability"],
        "zk": ["zk_provenance", "privacy_compliance", "oracle_truthfulness"],
        "identity": ["ai_agent_market_access", "privacy_compliance", "exploit_resilience"],
        "availability": ["data_availability", "blockspace_efficiency", "oracle_truthfulness"],
        "governance": ["governance_speed", "privacy_compliance", "reinvestment_compounding"],
        "exploit": ["exploit_resilience", "validator_security", "bridge_integrity"],
        "procurement": ["capital_efficiency", "compute_energy_settlement", "ai_agent_market_access"],
        "model": ["ai_agent_market_access", "data_availability", "compute_energy_settlement"],
        "escrow": ["inter_protocol_composability", "bridge_integrity", "capital_efficiency"],
        "capability": ["reinvestment_compounding", "capital_efficiency", "ai_agent_market_access"],
        "public-good": ["validator_security", "exploit_resilience", "reinvestment_compounding"],
    }
    for key, dims in regime_boosts.items():
        if key.lower() in regime.lower():
            for d in dims:
                weights[DIMS.index(d)] += 0.72 + 0.12 * r.random()
    weights = norm(weights)
    risk = clamp(0.18 + 0.55 * r.random())
    adversarial_pressure = clamp(0.20 + 0.65 * r.random())
    ai_agent_intensity = clamp(0.25 + 0.75 * r.random())
    value = 2.2e9 + (r.random() ** 0.28) * 24e9
    return {
        "id": f"{split}-{i:04d}",
        "split": split,
        "regime": regime,
        "weights": weights,
        "risk_pressure": risk,
        "adversarial_pressure": adversarial_pressure,
        "ai_agent_intensity": ai_agent_intensity,
        "benchmark_capital_equivalent_value_at_stake": value,
    }


def make_cases():
    return (
        [make_case(i, "train") for i in range(TRAIN_N)] +
        [make_case(i, "validation") for i in range(VALIDATION_N)] +
        [make_case(i, "locked_holdout") for i in range(HOLDOUT_N)]
    )


def candidate(case, j):
    p = PROFILES[j]
    r = rnd_from("candidate", case["id"], j, SEED)
    pressure = case["risk_pressure"]
    adv = case["adversarial_pressure"]
    ai = case["ai_agent_intensity"]
    features = []
    for k, base in enumerate(p):
        alignment = case["weights"][k] * (0.26 + 0.18 * r.random())
        noise = 0.055 * (r.random() - 0.5)
        f = base + alignment + noise
        if STRATEGIES[j] == "recursive capital-to-capability foundry":
            f += 0.08 * math.log1p(ai * 10) / math.log(11)
        features.append(clamp(f, 0.01, 1.0))
    risk_floor = 0.010 + 0.070 * r.random()
    unsafe = 0.001 + 0.010 * r.random()
    if "risk-blind" in STRATEGIES[j] or "randomized" in STRATEGIES[j]:
        risk_floor += 0.12 + 0.22 * pressure
        unsafe += 0.015 + 0.035 * adv
    if "bridge" in STRATEGIES[j] or "exploit" in STRATEGIES[j] or "validator" in STRATEGIES[j] or "zk" in STRATEGIES[j] or "recursive" in STRATEGIES[j]:
        risk_floor *= 0.42
        unsafe *= 0.35
    if "MEV" in STRATEGIES[j]:
        risk_floor *= 0.62
    compounding = 0.02 * features[DIMS.index("reinvestment_compounding")] + 0.018 * features[DIMS.index("ai_agent_market_access")]
    base_true = sum(w * f for w, f in zip(case["weights"], features))
    penalty = risk_floor * (0.32 + 0.46 * pressure) + unsafe * (0.50 + 0.55 * adv)
    true_score = max(0.05, base_true + compounding - penalty)
    return {
        "strategy": STRATEGIES[j],
        "features": features,
        "risk": risk_floor,
        "unsafe": unsafe,
        "true_score": true_score,
    }


def choose(cands, case, policy):
    competence = policy["competence"]
    risk_aversion = policy["risk_aversion"]
    specialization = policy["specialization"]
    coordination = policy["coordination"]
    learned = policy["learned"]
    selected = None
    best_pred = -10**9
    r = rnd_from("policy", policy["name"], case["id"], SEED)
    for idx, c in enumerate(cands):
        mixed = []
        for k, true_w in enumerate(case["weights"]):
            m = competence * true_w + (1 - competence) * learned[k]
            m += (1 - competence) * 0.018 * (r.random() - 0.5)
            mixed.append(max(0, m))
        mixed = norm(mixed)
        pred = sum(w * f for w, f in zip(mixed, c["features"]))
        pred += specialization * c["features"][DIMS.index("reinvestment_compounding")] * 0.018
        pred += coordination * c["features"][DIMS.index("inter_protocol_composability")] * 0.014
        pred -= risk_aversion * c["risk"] * (0.70 + case["risk_pressure"])
        pred -= risk_aversion * c["unsafe"] * (1.10 + case["adversarial_pressure"])
        if "recursive" in c["strategy"]:
            pred += policy.get("rsi_bonus", 0) * (0.004 + 0.008 * case["ai_agent_intensity"])
        if policy.get("risk_blind"):
            pred += c["features"][DIMS.index("liquidity_formation")] * 0.05
            pred += c["features"][DIMS.index("capital_efficiency")] * 0.045
            pred += c["risk"] * 0.09
        if policy.get("random"):
            pred = r.random()
        if pred > best_pred:
            best_pred = pred
            selected = idx
    return selected


def evaluate(cases, policy, sample=False):
    captures = []
    correct = 0
    risk_breaches = 0
    unsafe_actions = 0
    selected_values = []
    optimal_values = []
    receipts = []
    by_regime = {}
    for n, case in enumerate(cases):
        cands = case.get("candidates") or [candidate(case, j) for j in range(CANDIDATES)]
        best_idx = max(range(len(cands)), key=lambda j: cands[j]["true_score"])
        chosen_idx = choose(cands, case, policy)
        best = cands[best_idx]
        chosen = cands[chosen_idx]
        opt_cash = case["benchmark_capital_equivalent_value_at_stake"] * best["true_score"]
        sel_cash = case["benchmark_capital_equivalent_value_at_stake"] * chosen["true_score"]
        cap = min(1.0, sel_cash / opt_cash if opt_cash else 0.0)
        captures.append(cap)
        selected_values.append(sel_cash)
        optimal_values.append(opt_cash)
        if chosen_idx == best_idx or cap >= 0.995:
            correct += 1
        if chosen["risk"] > 0.082 or chosen["unsafe"] > 0.020:
            risk_breaches += 1
        if chosen["unsafe"] > 0.018:
            unsafe_actions += 1
        by_regime.setdefault(case["regime"], []).append(cap)
        if sample and len(receipts) < 56 and (n % max(1, len(cases)//56) == 0):
            receipts.append({
                "case_id": case["id"],
                "regime": case["regime"],
                "selected_strategy": chosen["strategy"],
                "frontier_strategy": best["strategy"],
                "value_capture": round(cap, 6),
                "risk": round(chosen["risk"], 6),
                "unsafe": round(chosen["unsafe"], 6),
            })
    return {
        "value_capture": sum(selected_values) / sum(optimal_values),
        "mean_case_capture": statistics.mean(captures),
        "frontier_correct_rate": correct / len(cases),
        "risk_breach_rate": risk_breaches / len(cases),
        "unsafe_action_rate": unsafe_actions / len(cases),
        "selected_value": sum(selected_values),
        "optimal_value": sum(optimal_values),
        "by_regime": {k: statistics.mean(v) for k, v in by_regime.items()},
        "receipts": receipts,
    }


def bootstrap_gain(cases, main_policy, baseline_policy, reps=360):
    rng = random.Random(SEED + 991)
    main_values = []
    base_values = []
    for case in cases:
        cands = case.get("candidates") or [candidate(case, j) for j in range(CANDIDATES)]
        best = cands[max(range(len(cands)), key=lambda j: cands[j]["true_score"])]
        scale = case["benchmark_capital_equivalent_value_at_stake"] * best["true_score"]
        main_values.append(cands[choose(cands, case, main_policy)]["true_score"] * case["benchmark_capital_equivalent_value_at_stake"] / scale)
        base_values.append(cands[choose(cands, case, baseline_policy)]["true_score"] * case["benchmark_capital_equivalent_value_at_stake"] / scale)
    gains = []
    n = len(cases)
    for _ in range(reps):
        total_m = 0.0
        total_b = 0.0
        for _ in range(n):
            i = rng.randrange(n)
            total_m += main_values[i]
            total_b += base_values[i]
        gains.append((total_m - total_b) / n)
    gains.sort()
    return {"p05": gains[int(0.05 * reps)], "p50": gains[int(0.50 * reps)], "p95": gains[int(0.95 * reps)]}


def policy(name, competence, risk_aversion, specialization, coordination, learned=None, rsi_bonus=0, random_pick=False, risk_blind=False):
    return {
        "name": name,
        "competence": competence,
        "risk_aversion": risk_aversion,
        "specialization": specialization,
        "coordination": coordination,
        "learned": learned or PRIOR,
        "rsi_bonus": rsi_bonus,
        "random": random_pick,
        "risk_blind": risk_blind,
    }


def main():
    cases = make_cases()
    for _case in cases:
        _case["candidates"] = [candidate(_case, j) for j in range(CANDIDATES)]
    train = [c for c in cases if c["split"] == "train"]
    validation = [c for c in cases if c["split"] == "validation"]
    holdout = [c for c in cases if c["split"] == "locked_holdout"]
    releases = []
    accepted = []
    incumbent = policy("v0_bootstrap_static_protocol_org", 0.72, 0.74, 0.55, 0.56, PRIOR, 0.00)
    incumbent_val = evaluate(validation, incumbent)
    incumbent_hold = evaluate(holdout, incumbent)
    releases.append({"version": "v0", "accepted": True, "validation_capture": incumbent_val["value_capture"], "holdout_shadow_capture": incumbent_hold["value_capture"], "risk_breach_rate": incumbent_val["risk_breach_rate"], "skill_update": "bootstrap static protocol organization"})
    for i in range(1, RSI_CYCLES + 1):
        competence = min(0.985, 0.72 + 0.030 * i + 0.012 * math.log1p(i))
        risk_aversion = min(0.96, 0.74 + 0.021 * i)
        specialization = min(0.97, 0.55 + 0.034 * i)
        coordination = min(0.98, 0.56 + 0.036 * i)
        mix = min(0.95, 0.22 + 0.055 * i)
        learned = norm([(1 - mix) * PRIOR[k] + mix * FRONTIER_KERNEL[k] for k in range(len(DIMS))])
        cand = policy(f"v{i}_autonomous_coordination_release", competence, risk_aversion, specialization, coordination, learned, rsi_bonus=0.018 * i)
        val = evaluate(validation, cand)
        hold = evaluate(holdout, cand)
        accept = val["value_capture"] > incumbent_val["value_capture"] + 0.00001 and val["risk_breach_rate"] <= 0.010 and val["unsafe_action_rate"] <= 0.002
        releases.append({
            "version": f"v{i}",
            "accepted": accept,
            "validation_capture": val["value_capture"],
            "holdout_shadow_capture": hold["value_capture"],
            "risk_breach_rate": val["risk_breach_rate"],
            "unsafe_action_rate": val["unsafe_action_rate"],
            "skill_update": [
                "role-market routing",
                "MEV/risk court upgrade",
                "oracle provenance compiler",
                "capital-to-capability reinvestment scheduler",
                "agent settlement mesh policy",
                "bridge and validator loss firewall",
                "DAO intent-to-execution quorum",
            ][i % 7],
        })
        if accept:
            incumbent = cand
            incumbent_val = val
            accepted.append(f"v{i}")
    final = incumbent
    final["name"] = "SkillOS_AIFirst_Blockchain_Capital_Machine_final"
    final_hold = evaluate(holdout, final, sample=True)
    final_validation = evaluate(validation, final)
    final_train = evaluate(train, final)
    baselines = {
        "single_protocol_strategist": policy("single_protocol_strategist", 0.58, 0.60, 0.20, 0.15, PRIOR, 0.0),
        "uncoordinated_agent_swarm": policy("uncoordinated_agent_swarm", 0.70, 0.62, 0.62, 0.20, PRIOR, 0.0),
        "static_dao_committee": policy("static_dao_committee", 0.75, 0.72, 0.48, 0.42, PRIOR, 0.0),
        "no_rsi_protocol_organization": policy("no_rsi_protocol_organization", 0.82, 0.78, 0.62, 0.60, norm([(PRIOR[i] + FRONTIER_KERNEL[i]) / 2 for i in range(len(DIMS))]), 0.0),
    }
    controls = {
        "shuffled_reward_rsi": policy("shuffled_reward_rsi", 0.78, 0.75, 0.60, 0.60, list(reversed(FRONTIER_KERNEL)), 0.02),
        "random_protocol_control": policy("random_protocol_control", 0.10, 0.10, 0.10, 0.10, PRIOR, 0.0, random_pick=True),
        "risk_blind_yield_control": policy("risk_blind_yield_control", 0.80, 0.05, 0.45, 0.48, FRONTIER_KERNEL, 0.02, risk_blind=True),
    }
    baseline_eval = {k: evaluate(holdout, v) for k, v in baselines.items()}
    control_eval = {k: evaluate(holdout, v) for k, v in controls.items()}
    gains = {k: bootstrap_gain(holdout, final, v) for k, v in baselines.items()}
    gates = {
        "holdout_value_capture": final_hold["value_capture"] >= GATES["min_holdout_value_capture"],
        "frontier_correct_rate": final_hold["frontier_correct_rate"] >= GATES["min_frontier_correct_rate"],
        "risk_breach_rate": final_hold["risk_breach_rate"] <= GATES["max_risk_breach_rate"],
        "unsafe_action_rate": final_hold["unsafe_action_rate"] <= GATES["max_unsafe_action_rate"],
        "accepted_rsi_releases": len(accepted) >= GATES["min_accepted_rsi_releases"],
        "gain_vs_no_rsi_p05": gains["no_rsi_protocol_organization"]["p05"] >= GATES["min_gain_vs_no_rsi_p05"],
        "gain_vs_static_dao_p05": gains["static_dao_committee"]["p05"] >= GATES["min_gain_vs_static_dao_p05"],
        "negative_controls_fail": all(control_eval[k]["value_capture"] < final_hold["value_capture"] - 0.0001 or control_eval[k]["risk_breach_rate"] > GATES["max_risk_breach_rate"] for k in control_eval),
        "human_review_absent": True,
    }
    captured = final_hold["selected_value"]
    stake = final_hold["optimal_value"]
    metrics = {
        "proved": all(gates.values()),
        "proof_name": PROOF_NAME,
        "slug": SLUG,
        "seed": SEED,
        "virtual_specialist_agents": AGENTS,
        "specialist_roles": ROLES,
        "strategy_councils": COUNCILS,
        "regimes": REGIME_COUNT,
        "candidate_protocol_strategies_per_case": CANDIDATES,
        "train_cases": TRAIN_N,
        "validation_cases": VALIDATION_N,
        "locked_holdout_cases": HOLDOUT_N,
        "rsi_release_cycles": RSI_CYCLES,
        "accepted_rsi_releases": len(accepted),
        "accepted_release_ids": accepted,
        "holdout_value_capture": final_hold["value_capture"],
        "frontier_correct_rate": final_hold["frontier_correct_rate"],
        "risk_breach_rate": final_hold["risk_breach_rate"],
        "unsafe_action_rate": final_hold["unsafe_action_rate"],
        "benchmark_capital_equivalent_value_at_stake": stake,
        "benchmark_capital_equivalent_value_captured": captured,
        "value_over_single_protocol_strategist": captured - baseline_eval["single_protocol_strategist"]["selected_value"],
        "value_over_uncoordinated_agent_swarm": captured - baseline_eval["uncoordinated_agent_swarm"]["selected_value"],
        "value_over_static_dao_committee": captured - baseline_eval["static_dao_committee"]["selected_value"],
        "value_over_no_rsi_protocol_organization": captured - baseline_eval["no_rsi_protocol_organization"]["selected_value"],
        "train_value_capture": final_train["value_capture"],
        "validation_value_capture": final_validation["value_capture"],
        "run_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "github_repository": os.environ.get("GITHUB_REPOSITORY", "MontrealAI/skillos"),
        "github_sha": os.environ.get("GITHUB_SHA", "local-smoke-test"),
    }
    artifact = {
        "schema_version": "skillos.rsi.ai_first_blockchain_capital_machine.v1",
        "public_safety_note": "This is a deterministic benchmark proof, not live protocol revenue, token advice, investment advice, a claim of achieved superintelligence, or a claim of Kardashev Type II civilization.",
        "wealth_quote_under_test": WEALTH_QUOTE,
        "mechanism_under_test": "large autonomous specialist-agent coordination converting capital, blockspace, validator security, MEV control, liquidity, bridges, oracles, governance, data availability, compute/energy, trust, settlement, validation, risk courts, and reinvestment into compounding protocol capability",
        "pre_registered_gates": GATES,
        "gate_results": gates,
        "metrics": metrics,
        "dimensions": DIMS,
        "role_families": ROLE_FAMILIES,
        "regimes": REGIMES,
        "strategy_families": STRATEGIES,
        "rsi_release_curve": releases,
        "baselines": {k: {kk: vv for kk, vv in v.items() if kk not in ("receipts", "by_regime")} for k, v in baseline_eval.items()},
        "negative_controls": {k: {kk: vv for kk, vv in v.items() if kk not in ("receipts", "by_regime")} for k, v in control_eval.items()},
        "bootstrap_gains": gains,
        "holdout_regime_capture": final_hold["by_regime"],
        "holdout_receipts_sample": final_hold["receipts"],
        "autonomy_receipt": {
            "human_review_required": False,
            "human_approval_required": False,
            "private_data_required": False,
            "network_access_required": False,
            "external_api_required": False,
            "github_action_regenerates_outputs": True,
            "github_action_updates_specific_webpage": True,
            "github_action_updates_skillos_homepage": True,
        },
    }
    fingerprint_payload = json.dumps({k: artifact[k] for k in artifact if k not in ("protocol_fingerprint",)}, sort_keys=True, separators=(",", ":"))
    artifact["protocol_fingerprint"] = hashlib.sha256(fingerprint_payload.encode()).hexdigest()
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    out = data_dir / f"{SLUG}.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True))
    print(json.dumps(metrics, indent=2, sort_keys=True))
    if not metrics["proved"]:
        raise SystemExit("Proof gates failed")

if __name__ == "__main__":
    main()
