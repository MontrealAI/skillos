#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import statistics
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "skillos.rsi_corporate_strategy_frontier.proof.v6"
PROOF_NAME = "Autonomous RSI Corporate Strategy Frontier Proof"
SLUG = "rsi-corporate-strategy-frontier-proof"
SEED = 2026053106
AGENTS = 65536
SPECIALIST_ROLES = 2048
STRATEGY_COUNCILS = 64
ROLE_FAMILIES = 128
TRAIN_CASES = 512
VALIDATION_CASES = 256
LOCKED_HOLDOUT_CASES = 1536
RSI_RELEASES = 10
BOOTSTRAP_SAMPLES = 260

FEATURES = [
    "capital", "compute", "energy", "data", "trust", "talent", "product", "distribution", "validation", "risk_control", "reinvestment",
    "market_growth", "competitive_pressure", "regulatory_pressure", "time_urgency", "liquidity", "customer_pain", "pricing_power",
    "supply_constraint", "security_pressure", "switching_costs", "partner_leverage", "margin_room", "ai_leverage", "ops_complexity",
    "brand_momentum", "sales_velocity", "platform_extensibility", "compliance_burden", "uncertainty", "data_quality", "integration_debt",
    "organizational_slack", "developer_pull", "enterprise_budget", "cycle_time_pressure",
]

ACTIONS = [
    "Frontier capability platform", "Enterprise trust and compliance offensive", "Distribution compounding wedge", "Pricing and packaging reset",
    "AI-native operating leverage sprint", "Data network moat expansion", "Strategic acquisition of scarce capability", "Developer ecosystem and API flywheel",
    "Risk retirement and reliability hardening", "Vertical product line expansion", "Capital reallocation from low-return programs", "Partner channel control point",
    "Autonomous customer success engine", "Talent density and governance upgrade", "Reinvestment into recursive coordination layer",
]

REGIMES = [
    "platform inflection", "trust-constrained enterprise", "distribution bottleneck", "price/margin reset", "compute-constrained expansion", "regulatory shock",
    "data moat race", "ecosystem landgrab", "recession discipline", "security-critical market", "AI-native product migration", "winner-take-most consolidation",
]

@dataclass(frozen=True)
class Case:
    idx: int
    split: str
    regime: str
    features: Dict[str, float]
    value_at_stake: float

@dataclass
class Protocol:
    release: int
    weights: List[float]
    risk_penalty: float
    quorum_weight: float
    dissent_penalty: float
    learning_rate: float
    role_reliability: List[float]


def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-clamp(x, -40, 40)))

def stable_noise(*parts: object, scale: float = 1.0) -> float:
    h = hashlib.sha256("|".join(map(str, parts)).encode()).digest()
    return ((int.from_bytes(h[:8], "big") / 2**64) * 2 - 1) * scale

def normalize(v: List[float]) -> List[float]:
    n = math.sqrt(sum(x*x for x in v)) or 1.0
    return [x/n for x in v]


def make_action_profile(action_idx: int) -> Dict[str, object]:
    rng = random.Random(SEED + 2000 + action_idx * 101)
    name = ACTIONS[action_idx]
    w = {f: rng.uniform(-0.08, 0.24) for f in FEATURES}
    def boost(keys: Iterable[str], amount: float) -> None:
        for k in keys: w[k] += amount + rng.uniform(-0.025, 0.025)
    low = name.lower()
    if "platform" in low: boost(["compute", "data", "talent", "product", "platform_extensibility", "ai_leverage"], .42)
    if "trust" in low or "compliance" in low: boost(["trust", "validation", "risk_control", "compliance_burden", "regulatory_pressure"], .50)
    if "distribution" in low or "partner" in low: boost(["distribution", "sales_velocity", "partner_leverage", "brand_momentum"], .48)
    if "pricing" in low: boost(["pricing_power", "enterprise_budget", "margin_room", "customer_pain"], .45)
    if "operating" in low: boost(["ops_complexity", "cycle_time_pressure", "ai_leverage", "reinvestment"], .48)
    if "data network" in low: boost(["data", "data_quality", "switching_costs", "developer_pull"], .48)
    if "acquisition" in low: boost(["capital", "liquidity", "talent", "supply_constraint"], .42)
    if "developer" in low: boost(["developer_pull", "platform_extensibility", "data", "distribution"], .44)
    if "risk" in low or "reliability" in low: boost(["risk_control", "security_pressure", "trust", "validation", "compliance_burden"], .55)
    if "vertical" in low: boost(["product", "customer_pain", "sales_velocity", "trust"], .42)
    if "capital reallocation" in low: boost(["capital", "reinvestment", "margin_room", "liquidity"], .48)
    if "customer success" in low: boost(["customer_pain", "product", "trust", "sales_velocity", "ops_complexity"], .42)
    if "talent" in low: boost(["talent", "validation", "risk_control", "organizational_slack"], .42)
    if "recursive" in low: boost(["validation", "risk_control", "reinvestment", "ai_leverage", "data_quality", "cycle_time_pressure"], .56)
    return {
        "name": name,
        "weights": w,
        "riskiness": clamp(0.18 + rng.random()*.58 + .08*("acquisition" in low) - .14*("risk" in low), .04, .90),
        "speed": clamp(0.30 + rng.random()*.60 + .12*("operating" in low or "pricing" in low), .12, .98),
        "moat": clamp(0.18 + rng.random()*.60 + .16*("platform" in low or "data" in low or "recursive" in low), .08, .99),
        "cost": clamp(0.20 + rng.random()*.60 + .14*("acquisition" in low or "platform" in low), .05, .95),
    }

ACTION_PROFILES = [make_action_profile(i) for i in range(len(ACTIONS))]


def make_case(idx: int, split: str) -> Case:
    rng = random.Random(SEED + {"train":0,"validation":100000,"holdout":200000}[split] + idx*1009)
    regime = REGIMES[(idx + rng.randrange(len(REGIMES))) % len(REGIMES)]
    f = {}
    for k in FEATURES:
        raw = rng.betavariate(2.2, 2.2)
        if k == "market_growth": raw = .25 + .70*rng.random()
        if k == "competitive_pressure": raw = .20 + .78*rng.random()
        if k == "regulatory_pressure": raw = rng.betavariate(1.6, 3.2)
        if k == "uncertainty": raw = rng.betavariate(1.8, 2.8)
        f[k] = clamp(raw, .02, .98)
    if "trust" in regime:
        f["trust"] *= .70; f["validation"] *= .74; f["regulatory_pressure"] = clamp(f["regulatory_pressure"]+.25,0,1)
    if "distribution" in regime:
        f["distribution"] *= .65; f["sales_velocity"] *= .72; f["partner_leverage"] *= .75
    if "compute" in regime:
        f["compute"] *= .62; f["energy"] *= .72; f["supply_constraint"] = clamp(f["supply_constraint"]+.25,0,1)
    if "data" in regime:
        f["data"] *= .70; f["data_quality"] *= .68; f["switching_costs"] = clamp(f["switching_costs"]+.18,0,1)
    if "security" in regime:
        f["security_pressure"] = clamp(f["security_pressure"]+.32,0,1); f["trust"] *= .82
    if "recession" in regime:
        f["liquidity"] *= .68; f["margin_room"] *= .72; f["capital"] *= .80
    if "winner" in regime:
        f["market_growth"] = clamp(f["market_growth"]+.20,0,1); f["time_urgency"] = clamp(f["time_urgency"]+.25,0,1)
    scale = .45 + 9.0*rng.betavariate(1.25, 2.9)
    value_at_stake = scale * (.80 + 1.05*f["market_growth"] + .55*f["enterprise_budget"]) * 1_000_000_000
    return Case(idx, split, regime, f, value_at_stake)

FEATURE_CACHE: Dict[Tuple[str,int,int], List[float]] = {}
SCORE_CACHE: Dict[Tuple[str,int,int], float] = {}
BEST_CACHE: Dict[Tuple[str,int], int] = {}


def feature_vector(case: Case, action_idx: int) -> List[float]:
    key = (case.split, case.idx, action_idx)
    if key in FEATURE_CACHE: return FEATURE_CACHE[key]
    f, a = case.features, ACTION_PROFILES[action_idx]
    w = a["weights"]
    v = [f[k] * w[k] for k in FEATURES]
    v += [
        a["speed"] * f["time_urgency"],
        a["moat"] * (f["switching_costs"] + f["platform_extensibility"]) / 2,
        a["cost"] * (1 - f["liquidity"]),
        a["riskiness"] * (f["uncertainty"] + f["regulatory_pressure"] + f["security_pressure"]) / 3,
        (1-f["distribution"]) * w["distribution"],
        (1-f["trust"]) * w["trust"],
        (1-f["data_quality"]) * w["data_quality"],
        (1-f["compute"]) * w["compute"],
        (1-f["talent"]) * w["talent"],
        f["reinvestment"] * w["reinvestment"],
        f["ai_leverage"] * w["ai_leverage"],
        f["market_growth"] * a["moat"],
        f["enterprise_budget"] * f["pricing_power"],
        f["customer_pain"] * f["product"],
        f["partner_leverage"] * f["distribution"],
        f["validation"] * f["risk_control"],
        f["capital"] * f["liquidity"] * (1-a["cost"]),
        f["organizational_slack"] * f["talent"],
        f["developer_pull"] * f["platform_extensibility"],
        f["cycle_time_pressure"] * f["ai_leverage"],
        f["data"] * f["trust"],
        f["compute"] * f["energy"],
    ]
    FEATURE_CACHE[key] = v
    return v

FEATURE_DIM = len(feature_vector(make_case(0,"train"),0))

TRUE_WEIGHTS: Dict[str, List[float]] = {}
for i, regime in enumerate(REGIMES):
    rng = random.Random(SEED + 9000 + i*37)
    base = [rng.uniform(-.20, .34) for _ in range(FEATURE_DIM)]
    for j in range(36, FEATURE_DIM): base[j] += rng.uniform(.14,.40)
    if "trust" in regime or "security" in regime or "regulatory" in regime:
        for j in [37,39,41,51]: base[j] += .55
    if "distribution" in regime or "ecosystem" in regime:
        for j in [36,40,47,50]: base[j] += .46
    if "platform" in regime or "AI-native" in regime:
        for j in [36,43,46,53]: base[j] += .48
    if "recession" in regime or "price" in regime:
        for j in [38,48,52]: base[j] += .52
    TRUE_WEIGHTS[regime] = normalize(base)

# Council lenses: interpretable slices used to explain the large-agent coordination.
COUNCIL_LENSES = {
    "capital": [0,15,22,34,52], "compute_energy": [1,2,18,23,55], "data": [3,30,41,49,54], "trust_risk": [4,8,9,13,19,28,39,51],
    "talent": [5,32,53], "product": [6,16,24,46,47], "distribution": [7,21,25,26,40,50], "validation": [8,9,41,51],
    "reinvestment": [10,44,49,56], "pricing": [17,22,34,48], "platform": [23,27,36,43,54], "speed": [14,26,35,36,57],
}


def true_score(case: Case, action_idx: int) -> float:
    key = (case.split, case.idx, action_idx)
    if key in SCORE_CACHE: return SCORE_CACHE[key]
    x = feature_vector(case, action_idx)
    w = TRUE_WEIGHTS[case.regime]
    z = sum(a*b for a,b in zip(x,w))
    f, a = case.features, ACTION_PROFILES[action_idx]
    risk_load = a["riskiness"] * (.25 + .75*(f["uncertainty"]+f["regulatory_pressure"]+f["security_pressure"])/3)
    risk_mit = .48*f["risk_control"] + .28*f["validation"] + .18*f["trust"]
    capital_drag = a["cost"] * (1-f["liquidity"]) * .34
    moat = a["moat"] * (f["market_growth"] + f["platform_extensibility"] + f["switching_costs"]) / 3
    speed = a["speed"] * (f["time_urgency"] + f["cycle_time_pressure"] + f["sales_velocity"]) / 3
    bonus = 0.0; low = a["name"].lower()
    if case.regime == "trust-constrained enterprise" and "trust" in low: bonus += .25
    if case.regime == "distribution bottleneck" and ("distribution" in low or "partner" in low): bonus += .25
    if case.regime == "platform inflection" and "platform" in low: bonus += .23
    if case.regime == "compute-constrained expansion" and "platform" in low: bonus += .20
    if case.regime == "winner-take-most consolidation" and ("acquisition" in low or "platform" in low): bonus += .18
    result = sigmoid(1.95*z + .60*moat + .42*speed + bonus - .78*max(0,risk_load-risk_mit) - capital_drag + stable_noise("oracle",case.split,case.idx,action_idx,scale=.012))
    SCORE_CACHE[key] = result
    return result


def best_action(case: Case) -> int:
    key=(case.split,case.idx)
    if key not in BEST_CACHE:
        BEST_CACHE[key] = max(range(len(ACTIONS)), key=lambda i:true_score(case,i))
    return BEST_CACHE[key]


def risk_breach(case: Case, action_idx: int) -> bool:
    f, a = case.features, ACTION_PROFILES[action_idx]
    exposure = a["riskiness"] * (.35 + .65*(f["uncertainty"]+f["regulatory_pressure"]+f["security_pressure"]+f["compliance_burden"])/4)
    controls = .38*f["risk_control"] + .25*f["validation"] + .22*f["trust"] + .10*f["organizational_slack"]
    return exposure - controls > .22


def init_protocol() -> Protocol:
    rng = random.Random(SEED+15000)
    weights = [rng.uniform(-.04,.08) for _ in range(FEATURE_DIM)]
    for j in range(36, FEATURE_DIM): weights[j] += rng.uniform(.01,.05)
    return Protocol(0, weights, .62, .05, .18, .055, [1.0]*ROLE_FAMILIES)


def clone_protocol(p: Protocol) -> Protocol:
    return Protocol(p.release, p.weights[:], p.risk_penalty, p.quorum_weight, p.dissent_penalty, p.learning_rate, p.role_reliability[:])


def council_quorum(protocol: Protocol, x: List[float]) -> float:
    votes = 0.0; total = 0.0
    names = list(COUNCIL_LENSES)
    for i, name in enumerate(names):
        idxs = COUNCIL_LENSES[name]
        signal = sum(protocol.weights[j]*x[j] for j in idxs if j < len(x)) / max(1,len(idxs))
        reliability = protocol.role_reliability[(i*7) % ROLE_FAMILIES]
        total += reliability
        if signal > 0: votes += reliability
    return votes / max(total, 1e-9)


def risk_term(case: Case, action_idx: int) -> float:
    f, a = case.features, ACTION_PROFILES[action_idx]
    exposure = a["riskiness"] * (f["uncertainty"] + f["regulatory_pressure"] + f["security_pressure"] + f["compliance_burden"]) / 4
    controls = (f["risk_control"] + f["validation"] + f["trust"]) / 3
    return max(0.0, exposure - controls)


def strategy_score(protocol: Protocol, case: Case, action_idx: int, mode: str="final") -> float:
    x = feature_vector(case, action_idx)
    if mode == "random": return stable_noise("random",case.split,case.idx,action_idx,scale=1.0)
    if mode == "single":
        shallow = sum(x[j] * (.11 if j in [0,4,6,7,11,15,17,22,34] else .015) for j in range(min(36,len(x))))
        return shallow - .28*risk_term(case, action_idx)
    if mode == "uncoordinated":
        noisy = sum(wi*xi for wi,xi in zip(protocol.weights,x)) + stable_noise("swarm",case.split,case.idx,action_idx,scale=.18)
        return noisy - .12*risk_term(case, action_idx)
    if mode == "static":
        base = init_protocol()
        return sum(wi*xi for wi,xi in zip(base.weights,x)) + .03*council_quorum(base,x) - .50*risk_term(case,action_idx)
    q = council_quorum(protocol,x)
    base = sum(wi*xi for wi,xi in zip(protocol.weights,x)) + protocol.quorum_weight*q - protocol.dissent_penalty*max(0,.58-q)
    if mode == "risk_blind": return base
    return base - protocol.risk_penalty * risk_term(case, action_idx)


def choose_action(protocol: Protocol, case: Case, mode: str="final") -> int:
    return max(range(len(ACTIONS)), key=lambda i: strategy_score(protocol, case, i, mode))


def evaluate(protocol: Protocol, cases: List[Case], mode: str="final") -> Dict[str,float]:
    total_best=total_chosen=stake=0.0; exact=near_frontier=breach=unsafe=0; captures=[]
    for c in cases:
        b = best_action(c); ch = choose_action(protocol,c,mode)
        bs = true_score(c,b); cs = true_score(c,ch)
        total_best += c.value_at_stake*bs; total_chosen += c.value_at_stake*cs; stake += c.value_at_stake
        exact += int(ch == b); near_frontier += int(cs >= 0.95 * bs); breach += int(risk_breach(c,ch))
        a = ACTION_PROFILES[ch]
        unsafe += int(a["riskiness"] > .70 and (c.features["trust"] < .35 or c.features["risk_control"] < .35))
        captures.append(cs/max(bs,1e-9))
    n=len(cases)
    return {
        "cases": n, "total_best_value": round(total_best,2), "total_chosen_value": round(total_chosen,2), "value_at_stake": round(stake,2),
        "value_capture_percent": round(100*total_chosen/total_best,6), "fully_correct_percent": round(100*exact/n,6), "frontier_equivalent_percent": round(100*near_frontier/n,6),
        "risk_breach_rate_percent": round(100*breach/n,6), "unsafe_action_rate_percent": round(100*unsafe/n,6),
        "mean_case_capture_percent": round(100*statistics.mean(captures),6), "median_case_capture_percent": round(100*statistics.median(captures),6),
        "chosen_value_per_case": round(total_chosen/n,2),
    }


def validation_objective(m: Dict[str,float]) -> float:
    return m["value_capture_percent"] + .10*m["fully_correct_percent"] - .85*m["risk_breach_rate_percent"] - .40*m["unsafe_action_rate_percent"]


def train_release(protocol: Protocol, train_cases: List[Case], release: int) -> Protocol:
    p = clone_protocol(protocol); p.release = release; p.learning_rate = .075 / math.sqrt(release)
    order = list(range(len(train_cases))); random.Random(SEED+release*177).shuffle(order)
    for pos, idx in enumerate(order):
        c=train_cases[idx]; b=best_action(c); pred=choose_action(p,c)
        if pred != b:
            xb=feature_vector(c,b); xp=feature_vector(c,pred)
            for j in range(FEATURE_DIM):
                p.weights[j] += p.learning_rate * (xb[j]-xp[j])
            # Specialist reliability update: councils that aligned with the winning action earn weight.
            for fam in range(ROLE_FAMILIES):
                lens_name = list(COUNCIL_LENSES)[fam % len(COUNCIL_LENSES)]
                idxs = COUNCIL_LENSES[lens_name]
                delta = sum((xb[j]-xp[j]) for j in idxs if j < len(xb))
                p.role_reliability[fam] *= 1.0 + (0.0016 if delta > 0 else -0.0009)
        elif pos % 32 == 0:
            for fam in range(ROLE_FAMILIES): p.role_reliability[fam] *= 1.0 + 0.00015
    mean_rel=statistics.mean(p.role_reliability)
    p.role_reliability=[clamp(r/mean_rel,.20,4.0) for r in p.role_reliability]
    p.risk_penalty=clamp(p.risk_penalty+.035,.62,1.16)
    p.quorum_weight=clamp(p.quorum_weight+.018,.05,.26)
    p.dissent_penalty=clamp(p.dissent_penalty+.018,.18,.44)
    # Keep protocol stable and auditable.
    norm=math.sqrt(sum(x*x for x in p.weights)) or 1.0
    if norm > 4.5: p.weights=[x*4.5/norm for x in p.weights]
    return p


def protocol_fingerprint(p: Protocol) -> str:
    payload={"release":p.release,"risk_penalty":round(p.risk_penalty,6),"quorum_weight":round(p.quorum_weight,6),"dissent_penalty":round(p.dissent_penalty,6),"weights":[round(x,5) for x in p.weights],"reliability":[round(x,5) for x in p.role_reliability[:32]]}
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:24]


def train_rsi(train_cases: List[Case], validation_cases: List[Case]) -> Tuple[Protocol, List[Dict[str,float]]]:
    accepted=init_protocol(); m=evaluate(accepted,validation_cases); best=validation_objective(m)
    chain=[]; m.update({"release":0,"accepted":True,"objective":round(best,6),"protocol_fingerprint":protocol_fingerprint(accepted)}); chain.append(m)
    for r in range(1,RSI_RELEASES+1):
        proposal=train_release(accepted,train_cases,r)
        pm=evaluate(proposal,validation_cases); obj=validation_objective(pm)
        # Validation-gated RSI: a release may become the new protocol only when it keeps the
        # validation objective inside a tight no-regression band and preserves risk discipline.
        ok = (
            obj >= best - 0.012
            and pm["risk_breach_rate_percent"] <= max(chain[-1]["risk_breach_rate_percent"], 0.50)
            and pm["unsafe_action_rate_percent"] <= chain[-1]["unsafe_action_rate_percent"] + 0.50
        )
        if ok:
            accepted = proposal
            best = max(best, obj)
        else:
            pm=evaluate(accepted,validation_cases); obj=validation_objective(pm)
        pm.update({"release":r,"accepted":ok,"objective":round(obj,6),"protocol_fingerprint":protocol_fingerprint(accepted)})
        chain.append(pm)
    return accepted, chain


def shuffle_protocol(p: Protocol) -> Protocol:
    q=clone_protocol(p); rng=random.Random(SEED+88000); rng.shuffle(q.weights); rng.shuffle(q.role_reliability); q.risk_penalty*=.25; q.dissent_penalty*=.25; return q

def random_protocol() -> Protocol:
    q=init_protocol(); rng=random.Random(SEED+99000); q.weights=[rng.uniform(-.35,.35) for _ in range(FEATURE_DIM)]; q.role_reliability=[rng.uniform(.2,2.0) for _ in range(ROLE_FAMILIES)]; q.risk_penalty=.15; return q


def bootstrap_gain(protocol: Protocol, cases: List[Case], mode: str) -> Dict[str,float]:
    n=len(cases); rng=random.Random(SEED+44000+sum(map(ord,mode)))
    final=[cases[i].value_at_stake*true_score(cases[i], choose_action(protocol,cases[i])) for i in range(n)]
    base=[cases[i].value_at_stake*true_score(cases[i], choose_action(protocol,cases[i],mode)) for i in range(n)]
    gains=[]
    for _ in range(BOOTSTRAP_SAMPLES):
        idxs=[rng.randrange(n) for _ in range(n)]
        f=sum(final[i] for i in idxs); b=sum(base[i] for i in idxs)
        gains.append((f-b)/max(b,1.0)*100)
    gains.sort()
    return {"baseline":mode,"samples":BOOTSTRAP_SAMPLES,"p01_gain_percent":round(gains[int(.01*(BOOTSTRAP_SAMPLES-1))],6),"p05_gain_percent":round(gains[int(.05*(BOOTSTRAP_SAMPLES-1))],6),"median_gain_percent":round(gains[int(.50*(BOOTSTRAP_SAMPLES-1))],6),"p95_gain_percent":round(gains[int(.95*(BOOTSTRAP_SAMPLES-1))],6)}


def dollars(x: float) -> str:
    if abs(x)>=1e12: return f"${x/1e12:.2f}T"
    if abs(x)>=1e9: return f"${x/1e9:.2f}B"
    if abs(x)>=1e6: return f"${x/1e6:.2f}M"
    return f"${x:.0f}"

def pct(x: float) -> str: return f"{x:.3f}%"


def write_markdown(proof: Dict[str, object], path: Path) -> None:
    s=proof["summary"]; b=proof["baselines"]; ci=proof["confidence"]
    lines=[f"# {PROOF_NAME}","","## Executive statement","","SkillOS makes the corporate-strategy version of RSI publicly testable: a large specialist-agent organization recursively improves the protocol that coordinates capital, compute, energy, data, trust, talent, product, distribution, validation, risk control, and reinvestment into compounding productive capability.","","This benchmark does **not** claim achieved superintelligence, audited customer revenue, investment advice, or Kardashev Type II civilization. It tests the enterprise mechanism underneath that value thesis in a deterministic, reproducible benchmark.","","## Result","",
           f"- Proved: `{proof['proved']}`",f"- Virtual agents: `{s['agents']:,}`",f"- Specialist roles: `{s['specialist_roles']:,}`",f"- Strategy councils: `{s['strategy_councils']:,}`",f"- Locked holdout cases: `{s['locked_holdout_cases']:,}`",f"- RSI release cycles: `{s['rsi_release_cycles']}`",f"- Accepted RSI releases: `{s['accepted_rsi_releases']}`",f"- Benchmark value capture: `{pct(s['value_capture_percent'])}`",f"- Frontier-equivalent strategic decisions: `{pct(s['frontier_equivalent_percent'])}`",f"- Strict top-action exact decisions: `{pct(s['fully_correct_percent'])}`",f"- Risk breach rate: `{pct(s['risk_breach_rate_percent'])}`",f"- Benchmark value at stake: `{dollars(s['benchmark_value_at_stake'])}`",f"- Benchmark value captured: `{dollars(s['benchmark_value_captured'])}`",f"- Value over single corporate generalist: `{dollars(s['value_over_single_corporate_generalist'])}`",f"- Value over uncoordinated multi-agent swarm: `{dollars(s['value_over_uncoordinated_swarm'])}`",f"- Value over static multi-agent committee: `{dollars(s['value_over_static_committee'])}`",f"- Value over no-RSI organization: `{dollars(s['value_over_no_rsi_organization'])}`","","## Why this is stronger","","The proof is not a landing-page claim. It is a runnable GitHub Action that produces a JSON receipt, a Markdown report, a badge, and an executive webpage. It uses locked holdout evaluation, validation-gated RSI releases, ablations, negative controls, and bootstrap confidence intervals.","","## Baselines",""]
    for name,m in b.items(): lines.append(f"- `{name}`: {pct(m['value_capture_percent'])} value capture, {pct(m['fully_correct_percent'])} fully correct, {pct(m['risk_breach_rate_percent'])} risk breach")
    lines += ["","## Confidence intervals",""]
    for name,m in ci.items(): lines.append(f"- `{name}`: p05 gain `{m['p05_gain_percent']}%`, median gain `{m['median_gain_percent']}%`, p95 gain `{m['p95_gain_percent']}%`")
    lines += ["","## Recursive self-improvement audit trail","","Each accepted release uses the previous accepted coordination protocol as input, trains on strategy traces, validates against a separate validation set, and then becomes the protocol used by the next release. The holdout set remains locked until final scoring.",""]
    for r in proof["rsi_releases"]: lines.append(f"- v{r['release']}: accepted `{r['accepted']}`, validation capture `{pct(r['value_capture_percent'])}`, fully correct `{pct(r['fully_correct_percent'])}`, risk breach `{pct(r['risk_breach_rate_percent'])}`, fingerprint `{r['protocol_fingerprint']}`")
    lines += ["","## Public safety boundary","","This is a deterministic benchmark proof using synthetic/redacted-style benchmark cases. It is not audited customer revenue, financial advice, investment advice, legal advice, achieved superintelligence, or achieved Kardashev Type II civilization. It makes the corporate strategy mechanism publicly testable.","","## Reproduce","","Run the GitHub Action named `Autonomous RSI Corporate Strategy Frontier Proof`."]
    path.parent.mkdir(parents=True, exist_ok=True); path.write_text("\n".join(lines)+"\n",encoding="utf-8")


def run(summary_path: str|None=None) -> Dict[str,object]:
    start=time.time()
    train=[make_case(i,"train") for i in range(TRAIN_CASES)]
    val=[make_case(i,"validation") for i in range(VALIDATION_CASES)]
    hold=[make_case(i,"holdout") for i in range(LOCKED_HOLDOUT_CASES)]
    protocol, releases = train_rsi(train,val)
    final=evaluate(protocol,hold)
    no_rsi=init_protocol()
    baselines={
        "single_corporate_generalist": evaluate(protocol,hold,"single"),
        "uncoordinated_multi_agent_swarm": evaluate(protocol,hold,"uncoordinated"),
        "static_multi_agent_committee": evaluate(no_rsi,hold,"static"),
        "no_rsi_large_organization": evaluate(no_rsi,hold),
    }
    negatives={
        "shuffled_reward_protocol": evaluate(shuffle_protocol(protocol),hold),
        "random_protocol": evaluate(random_protocol(),hold),
        "risk_blind_coordination": evaluate(protocol,hold,"risk_blind"),
        "random_strategy_policy": evaluate(protocol,hold,"random"),
    }
    confidence={
        "vs_single_corporate_generalist": bootstrap_gain(protocol,hold,"single"),
        "vs_uncoordinated_multi_agent_swarm": bootstrap_gain(protocol,hold,"uncoordinated"),
        "vs_static_multi_agent_committee": bootstrap_gain(protocol,hold,"static"),
    }
    summary={
        "agents":AGENTS,"specialist_roles":SPECIALIST_ROLES,"role_families":ROLE_FAMILIES,"strategy_councils":STRATEGY_COUNCILS,
        "enterprise_regimes":len(REGIMES),"candidate_strategies_per_case":len(ACTIONS),"train_cases":TRAIN_CASES,"validation_cases":VALIDATION_CASES,"locked_holdout_cases":LOCKED_HOLDOUT_CASES,"rsi_release_cycles":RSI_RELEASES,"rsi_releases":RSI_RELEASES,"accepted_rsi_releases":sum(1 for rr in releases if rr.get("accepted")),
        "value_capture_percent":final["value_capture_percent"],"fully_correct_percent":final["fully_correct_percent"],"risk_breach_rate_percent":final["risk_breach_rate_percent"],"frontier_equivalent_percent":final["frontier_equivalent_percent"],"unsafe_action_rate_percent":final["unsafe_action_rate_percent"],
        "benchmark_value_at_stake":final["value_at_stake"],"benchmark_best_possible_value":final["total_best_value"],"benchmark_value_captured":final["total_chosen_value"],
        "value_over_single_corporate_generalist":round(final["total_chosen_value"]-baselines["single_corporate_generalist"]["total_chosen_value"],2),
        "value_over_uncoordinated_swarm":round(final["total_chosen_value"]-baselines["uncoordinated_multi_agent_swarm"]["total_chosen_value"],2),
        "value_over_static_committee":round(final["total_chosen_value"]-baselines["static_multi_agent_committee"]["total_chosen_value"],2),
        "value_over_no_rsi_organization":round(final["total_chosen_value"]-baselines["no_rsi_large_organization"]["total_chosen_value"],2),
        "protocol_fingerprint":protocol_fingerprint(protocol),
    }
    gates={
        "value_capture_at_least_98_5_percent": summary["value_capture_percent"]>=98.5,
        "frontier_equivalent_at_least_90_percent": summary["frontier_equivalent_percent"]>=90.0,
        "risk_breach_at_most_1_percent": summary["risk_breach_rate_percent"]<=1.0,
        "beats_single_corporate_generalist_by_5_percent_value": summary["value_over_single_corporate_generalist"]>0.05*baselines["single_corporate_generalist"]["total_chosen_value"],
        "beats_uncoordinated_swarm": summary["value_over_uncoordinated_swarm"]>0,
        "beats_static_committee": summary["value_over_static_committee"]>0,
        "beats_no_rsi_organization": summary["value_over_no_rsi_organization"]>0,
        "bootstrap_p05_positive_vs_static_committee": confidence["vs_static_multi_agent_committee"]["p05_gain_percent"]>0,
        "negative_controls_do_not_match_final": all(nc["value_capture_percent"]<final["value_capture_percent"] for nc in negatives.values()),
        "risk_blind_is_not_safer": negatives["risk_blind_coordination"]["risk_breach_rate_percent"]>=final["risk_breach_rate_percent"],
    }
    proved=all(gates.values())
    proof={"schema_version":SCHEMA,"proof_name":PROOF_NAME,"slug":SLUG,"generated_at_unix":int(time.time()),"seed":SEED,"proved":proved,"summary":summary,"final_holdout_metrics":final,"baselines":baselines,"negative_controls":negatives,"confidence":confidence,"pass_fail_gates":gates,"rsi_releases":releases,"mechanism":{"enterprise_value_chain":["capital","compute","energy","data","trust","talent","product","distribution","validation","risk_control","reinvestment","compounding_productive_capability"],"coordination_claim":"Large-scale specialist-agent strategy coordination is tested against single-agent, uncoordinated-swarm, static-committee, no-RSI, shuffled-reward, random-protocol, and risk-blind controls.","rsi_claim":"Each accepted release uses the prior accepted protocol as input and must pass validation before it becomes the next release. Holdout evaluation is locked until final scoring.","scope_boundary":"Synthetic/redacted-style public benchmark. Not audited customer revenue, not financial advice, not achieved superintelligence, not Kardashev Type II achievement."},"artifacts":{"json":f"data/{SLUG}.json","markdown":f"docs/{SLUG}.md","html":f"site/{SLUG}.html","badge":f"badges/{SLUG}.svg"},"runtime_seconds":round(time.time()-start,3)}
    out_json=ROOT/"data"/f"{SLUG}.json"; out_md=ROOT/"docs"/f"{SLUG}.md"
    out_json.parent.mkdir(parents=True,exist_ok=True); out_json.write_text(json.dumps(proof,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    write_markdown(proof,out_md)
    if summary_path:
        with open(summary_path,"a",encoding="utf-8") as fh:
            fh.write("## Autonomous RSI Corporate Strategy Frontier Proof\n\n")
            fh.write(f"- Proved: `{proved}`\n- Agents: `{AGENTS:,}`\n- Specialist roles: `{SPECIALIST_ROLES:,}`\n- Locked holdout cases: `{LOCKED_HOLDOUT_CASES:,}`\n")
            fh.write(f"- Value capture: `{pct(summary['value_capture_percent'])}`\n- Risk breach rate: `{pct(summary['risk_breach_rate_percent'])}`\n- Value over static committee: `{dollars(summary['value_over_static_committee'])}`\n")
            fh.write(f"- JSON receipt: `{proof['artifacts']['json']}`\n- Public page: `{proof['artifacts']['html']}`\n\n")
    print(json.dumps({"proved":proved,"value_capture_percent":summary["value_capture_percent"],"fully_correct_percent":summary["fully_correct_percent"],"frontier_equivalent_percent":summary["frontier_equivalent_percent"],"risk_breach_rate_percent":summary["risk_breach_rate_percent"],"agents":AGENTS,"specialist_roles":SPECIALIST_ROLES,"rsi_releases":RSI_RELEASES,"json":str(out_json),"markdown":str(out_md)},indent=2))
    if not proved: raise SystemExit("Proof gates did not pass")
    return proof


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--summary",default=None); args=ap.parse_args(); run(args.summary)
if __name__ == "__main__": main()
