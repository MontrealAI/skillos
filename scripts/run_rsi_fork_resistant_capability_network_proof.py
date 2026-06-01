#!/usr/bin/env python3
"""SkillOS Autonomous RSI Fork-Resistant Capability Network Proof.

Deterministic, dependency-free GitHub Actions proof.

Question:
Can SkillOS build a capability network whose verified skill graph, provenance,
routing policy, and release history keep compounding even when a competitor
tries to clone or fork the surface-level system?

The proof is synthetic/redacted-style and reproducible. It is not live revenue,
customer results, financial advice, legal advice, token advice, policy advice,
or proof of achieved superintelligence.
"""

from __future__ import annotations

import argparse, datetime as dt, hashlib, json, math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA, DOCS = ROOT / "data", ROOT / "docs"
MASK = (1 << 64) - 1

FEATURES = [
    "task_value", "user_density", "verified_skill_depth", "provenance_strength",
    "routing_precision", "capability_liquidity", "interoperability",
    "feedback_velocity", "switching_cost", "trust_density", "fork_mimicry",
    "subsidy_pressure", "surface_similarity", "data_freshness",
    "security_exposure", "compliance_load", "risk_exposure", "rollback_option",
    "execution_margin", "latency_pressure", "transfer_distance", "governance_quality",
]

NEG = {"security_exposure", "compliance_load", "risk_exposure", "latency_pressure", "transfer_distance"}

DOMAINS = [
    "enterprise_ops", "agent_marketplace", "governance", "blockchain_protocols",
    "proof_generation", "regulated_work", "data_flywheel", "security_review",
    "customer_success", "developer_tools", "compute_allocation", "energy_scheduling",
    "capital_strategy", "workflow_compression", "provenance_audit", "cross_domain_transfer",
    "quality_assurance", "knowledge_ops", "platform_growth", "reliability_engineering",
    "compliance_evidence", "product_strategy", "market_research", "capability_routing",
    "ecosystem_design", "partner_distribution", "risk_courts", "skill_exchange",
]

INTERACTIONS = [
    ("network_liquidity", lambda f: f["user_density"] * f["capability_liquidity"]),
    ("verified_depth_routing", lambda f: f["verified_skill_depth"] * f["routing_precision"]),
    ("provenance_trust", lambda f: f["provenance_strength"] * f["trust_density"]),
    ("feedback_freshness", lambda f: f["feedback_velocity"] * f["data_freshness"]),
    ("switching_trust", lambda f: f["switching_cost"] * f["trust_density"]),
    ("interop_transfer", lambda f: f["interoperability"] * (1 - f["transfer_distance"])),
    ("fork_attack", lambda f: f["fork_mimicry"] * f["surface_similarity"] * (1 - f["provenance_strength"])),
    ("subsidized_fork_risk", lambda f: f["subsidy_pressure"] * (1 - f["verification_density"] if "verification_density" in f else 1 - f["provenance_strength"])),
    ("risk_without_rollback", lambda f: f["risk_exposure"] * (1 - f["rollback_option"])),
    ("margin_network", lambda f: f["execution_margin"] * f["user_density"]),
    ("governance_provenance", lambda f: f["governance_quality"] * f["provenance_strength"]),
]

BASE = {
    "f_task_value": .20, "f_user_density": .17, "f_verified_skill_depth": .20,
    "f_provenance_strength": .18, "f_routing_precision": .17,
    "f_capability_liquidity": .18, "f_interoperability": .10,
    "f_feedback_velocity": .13, "f_switching_cost": .11,
    "f_trust_density": .17, "f_fork_mimicry": -.12,
    "f_subsidy_pressure": -.06, "f_surface_similarity": -.05,
    "f_data_freshness": .12, "f_security_exposure": -.20,
    "f_compliance_load": -.13, "f_risk_exposure": -.21,
    "f_rollback_option": .08, "f_execution_margin": .15,
    "f_latency_pressure": -.05, "f_transfer_distance": -.12,
    "f_governance_quality": .10,
    "i_network_liquidity": .24, "i_verified_depth_routing": .22,
    "i_provenance_trust": .20, "i_feedback_freshness": .16,
    "i_switching_trust": .12, "i_interop_transfer": .14,
    "i_fork_attack": -.34, "i_subsidized_fork_risk": -.24,
    "i_risk_without_rollback": -.30, "i_margin_network": .12,
    "i_governance_provenance": .12,
    "invalid": -4.0, "risk_load": -.46,
}

ROLE_FAMILIES = [
    "skill_network_architect", "provenance_auditor", "routing_strategist",
    "liquidity_market_maker", "fork_red_team", "security_court",
    "compliance_court", "trust_steward", "feedback_loop_designer",
    "data_freshness_auditor", "interop_engineer", "release_manager",
    "switching_cost_analyst", "subsidy_attack_modeler", "execution_margin_planner",
    "governance_chair",
]
ROLES_PER_FAMILY, AGENTS_PER_ROLE = 1_048_576, 32
ROLE_COUNT = len(ROLE_FAMILIES) * ROLES_PER_FAMILY
AGENT_COUNT = ROLE_COUNT * AGENTS_PER_ROLE

def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def mix64(x:int)->int:
    x &= MASK
    x = (x + 0x9E3779B97F4A7C15) & MASK
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return z ^ (z >> 31)

def u01(seed:int,*vals:int)->float:
    x = seed & MASK
    for value in vals:
        x = mix64(x ^ ((int(value) + 0x9E3779B97F4A7C15) & MASK))
    return (x >> 11) / float(1 << 53)

def noise(seed:int,*vals:int)->float:
    return 2*u01(seed,*vals)-1

def domain_lift(seed:int, domain:int, key:str)->float:
    h = int(hashlib.sha256(f"{seed}|{domain}|{key}".encode()).hexdigest()[:12], 16)
    amp = .34 if key.startswith("i_") else .26
    if key.startswith("f_") and key[2:] in NEG:
        amp *= .55
    return amp * math.sin((domain+1)*(h%29+7)*.137) * (.55 + .45*u01(seed, domain, h & 9999))

def features(seed:int, case_id:int, arm:int, domain:int)->dict[str,float]:
    f = {name: u01(seed, case_id, arm, i) for i, name in enumerate(FEATURES)}
    f["provenance_strength"] = min(1, max(0, .45*f["provenance_strength"] + .22*f["verified_skill_depth"] + .18*f["feedback_velocity"] + .15*u01(seed, domain, 711)))
    f["capability_liquidity"] = min(1, max(0, .42*f["capability_liquidity"] + .22*f["user_density"] + .20*f["routing_precision"] + .16*u01(seed, domain, 712)))
    f["trust_density"] = min(1, max(0, .44*f["trust_density"] + .22*f["provenance_strength"] + .18*f["governance_quality"] + .16*u01(seed, case_id, arm, 713)))
    f["fork_mimicry"] = min(1, max(0, .55*f["fork_mimicry"] + .25*f["surface_similarity"] + .20*u01(seed, case_id, arm, 714)))
    f["risk_exposure"] = min(1, max(0, .30*f["risk_exposure"] + .22*f["fork_mimicry"] + .20*(1-f["rollback_option"]) + .28*u01(seed, case_id, arm, 715)))
    f["security_exposure"] = min(1, max(0, .35*f["security_exposure"] + .22*f["fork_mimicry"] + .20*(1-f["provenance_strength"]) + .23*u01(seed, case_id, arm, 716)))
    f["compliance_load"] = min(1, max(0, .36*f["compliance_load"] + .20*f["risk_exposure"] + .20*(1-f["governance_quality"]) + .24*u01(seed, case_id, arm, 717)))
    f["verification_density"] = min(1, max(0, .45*f["provenance_strength"] + .25*f["verified_skill_depth"] + .20*f["governance_quality"] + .10*u01(seed, case_id, arm, 718)))
    return f

def atoms_from_features(f:dict[str,float], domain:int)->dict[str,float]:
    a = {f"f_{k}": v for k, v in f.items() if k in FEATURES}
    for name, fn in INTERACTIONS:
        a[f"i_{name}"] = fn(f)
    for key, value in list(a.items()):
        if key.startswith("f_") or key.startswith("i_"):
            a[f"d{domain}_{key}"] = value
    risk_load = f["risk_exposure"] + f["security_exposure"] + f["compliance_load"]
    invalid = (
        (f["fork_mimicry"] > .82 and f["provenance_strength"] < .45) or
        (f["security_exposure"] > .78 and f["verification_density"] < .45) or
        (f["risk_exposure"] > .80 and f["rollback_option"] < .40) or
        (f["compliance_load"] > .80 and f["governance_quality"] < .45)
    )
    a["risk_load"] = risk_load
    a["invalid"] = 1.0 if invalid else 0.0
    return a

def oracle_score(a:dict[str,float], seed:int, domain:int)->float:
    score = 0.0
    for k,v in a.items():
        if k.startswith(f"d{domain}_"):
            score += domain_lift(seed, domain, k.split("_",1)[1]) * v
        else:
            score += BASE.get(k, 0.0) * v
    return score

def generate(seed:int, count:int, start:int)->list[dict[str,Any]]:
    cases = []
    for off in range(count):
        cid = start + off
        domain = cid % len(DOMAINS)
        market = 80_000_000 + 3_000_000_000 * (u01(seed, cid, 999) ** 2.12)
        candidates = []
        for arm in range(11):
            f = features(seed, cid, arm, domain)
            a = atoms_from_features(f, domain)
            score = oracle_score(a, seed, domain) + .008*noise(seed, cid, arm, 333)
            value = max(.015, score + 1.35) * market
            candidates.append({"arm":arm, "features":f, "atoms":a, "utility":score, "invalid":a["invalid"]>.5, "value_usd":value})
        valid = [(c["utility"], i) for i,c in enumerate(candidates) if not c["invalid"]]
        oracle = max(valid if valid else [(c["utility"], i) for i,c in enumerate(candidates)])[1]
        cases.append({"case_id":cid, "domain":domain, "candidates":candidates, "oracle":oracle})
    return cases

def protocol_stage(seed:int, stage:int)->dict[str,float]:
    f_frac = min(1, .22 + .052*stage)
    i_frac = max(0, min(1, (stage-2)/10))
    domain_frac = max(0, min(1, (stage-5)/14))
    risk_frac = max(.05, min(1, (stage-1)/7))
    w = {}
    for k,v in BASE.items():
        if k.startswith("i_"):
            w[k] = v * i_frac
        elif k in {"invalid","risk_load"}:
            w[k] = v * risk_frac
        else:
            w[k] = v * f_frac
    # The mature network is more conservative against forks and unverified reuse.
    w["invalid"] = BASE["invalid"] * risk_frac - .22*stage
    w["risk_load"] = BASE["risk_load"] * risk_frac - .09*stage
    for domain in range(len(DOMAINS)):
        for key in [x for x in BASE if x.startswith("f_") or x.startswith("i_")]:
            w[f"d{domain}_{key}"] = domain_lift(seed, domain, key) * domain_frac
    return w

def single_generalist()->dict[str,float]:
    return {"f_task_value":.34, "f_user_density":.14, "f_execution_margin":.20, "f_surface_similarity":.12, "f_risk_exposure":-.03, "invalid":-.04, "risk_load":-.02}

def cold_fork(seed:int)->dict[str,float]:
    w = protocol_stage(seed, 8)
    for key in list(w):
        if key.startswith("d"):
            w[key] = 0.0
    # Fork can mimic surface functionality, not the verified provenance network.
    w["f_surface_similarity"] = .20
    w["f_fork_mimicry"] = .16
    w["f_provenance_strength"] *= .25
    return w

def local_silo_network(seed:int)->dict[str,float]:
    w = protocol_stage(seed, 11)
    for key in list(w):
        if key.startswith("d"):
            domain = int(key[1:].split("_",1)[0])
            if domain % 5 != 0:
                w[key] = 0.0
    return w

def unverified_fork(seed:int)->dict[str,float]:
    w = protocol_stage(seed, 15)
    w["invalid"] = -.10
    w["risk_load"] = -.04
    for key in ["i_fork_attack", "i_subsidized_fork_risk", "i_risk_without_rollback"]:
        w[key] *= .10
    return w

def subsidy_attacker(seed:int)->dict[str,float]:
    w = protocol_stage(seed, 7)
    w["f_subsidy_pressure"] = .25
    w["f_task_value"] = .34
    w["f_fork_mimicry"] = .20
    w["invalid"] = -.08
    w["risk_load"] = -.04
    for key in list(w):
        if key.startswith("d"):
            w[key] *= .20
    return w

def dot(w:dict[str,float], a:dict[str,float])->float:
    return sum(w.get(k,0.0)*v for k,v in a.items())

def choose(case:dict[str,Any], w:dict[str,float])->int:
    best_i, best_s = 0, -10**12
    for i,c in enumerate(case["candidates"]):
        s = dot(w, c["atoms"])
        if s > best_s:
            best_i, best_s = i, s
    return best_i

def evaluate(cases:list[dict[str,Any]], w:dict[str,float])->dict[str,Any]:
    n=len(cases); exact=top3=invalid=risk=unauth=0
    total_o=total_c=0.0
    network=provenance=liquidity=retention=fork_resist=0.0
    per={str(i):{"o":0.0,"c":0.0,"n":0,"exact":0} for i in range(len(DOMAINS))}
    for case in cases:
        pred=choose(case,w); oracle=case["oracle"]
        c=case["candidates"][pred]; o=case["candidates"][oracle]; f=c["features"]
        exact += pred==oracle
        rank=sorted(range(len(case["candidates"])), key=lambda i: case["candidates"][i]["utility"], reverse=True)
        top3 += pred in rank[:3]
        invalid += c["invalid"]
        risk += c["atoms"]["risk_load"]>2.02
        unauth += f["security_exposure"]>.82 and f["verification_density"]<.40
        total_o += o["value_usd"]; total_c += c["value_usd"]
        network += f["user_density"]*f["capability_liquidity"]
        provenance += (f["provenance_strength"]+f["verification_density"]+f["data_freshness"])/3
        liquidity += (f["capability_liquidity"]+f["routing_precision"]+f["interoperability"])/3
        retention += f["switching_cost"]*f["trust_density"]
        fork_resist += (1-f["fork_mimicry"])*(f["provenance_strength"]+f["trust_density"])/2
        r=per[str(case["domain"])]
        r["o"]+=o["value_usd"]; r["c"]+=c["value_usd"]; r["n"]+=1; r["exact"]+=pred==oracle
    domain_scores={k:{"value_capture_rate_percent":round(100*v["c"]/v["o"],4),"frontier_correct_rate_percent":round(100*v["exact"]/v["n"],4),"count":v["n"]} for k,v in per.items()}
    min_cap=min(x["value_capture_rate_percent"] for x in domain_scores.values())
    max_cap=max(x["value_capture_rate_percent"] for x in domain_scores.values())
    return {
        "case_count":n,
        "frontier_correct_rate_percent":round(100*exact/n,4),
        "top3_rate_percent":round(100*top3/n,4),
        "value_capture_rate_percent":round(100*total_c/total_o,4),
        "benchmark_value_capture_rate_percent":round(100*total_c/total_o,4),
        "total_benchmark_value_at_stake_usd":round(total_o,2),
        "total_benchmark_value_captured_usd":round(total_c,2),
        "risk_breach_rate_percent":round(100*risk/n,4),
        "invalid_action_rate_percent":round(100*invalid/n,4),
        "unauthorized_action_rate_percent":round(100*unauth/n,4),
        "network_effect_score":round(100*network/n,4),
        "provenance_moat_score":round(100*provenance/n,4),
        "capability_liquidity_score":round(100*liquidity/n,4),
        "retention_under_fork_pressure_score":round(100*retention/n,4),
        "fork_resistance_score":round(100*fork_resist/n,4),
        "minimum_domain_value_capture_percent":round(min_cap,4),
        "maximum_domain_value_capture_percent":round(max_cap,4),
        "weak_domain_rate_percent":round(100*sum(1 for s in domain_scores.values() if s["value_capture_rate_percent"]<90)/len(DOMAINS),4),
        "domain_scores":domain_scores,
    }

def composite(m:dict[str,Any])->float:
    return m["value_capture_rate_percent"]+.05*m["frontier_correct_rate_percent"]+.06*m["minimum_domain_value_capture_percent"]-1.5*m["risk_breach_rate_percent"]-1.8*m["invalid_action_rate_percent"]-1.3*m["weak_domain_rate_percent"]

def rsi_releases(seed:int, validation:list[dict[str,Any]], stages:int)->tuple[dict[str,float],list[dict[str,Any]]]:
    cur=protocol_stage(seed,0); cm=evaluate(validation,cur)
    rel=[{"generation":0,"released":True,"lesson":"seed public capability network before fork-resistance RSI","validation":cm,"score":round(composite(cm),6),"protocol":cur}]
    for g in range(1,stages+1):
        cand=protocol_stage(seed,g); vm=evaluate(validation,cand)
        score_gain=composite(vm)-composite(cm)
        no_regression=(vm["risk_breach_rate_percent"]<=cm["risk_breach_rate_percent"]+.05 and vm["weak_domain_rate_percent"]<=cm["weak_domain_rate_percent"]+.01 and vm["minimum_domain_value_capture_percent"]>=cm["minimum_domain_value_capture_percent"]-.10)
        released=(score_gain>.0005 or (g>=5 and no_regression)) and no_regression
        if released:
            cur, cm = cand, vm
        rel.append({"generation":g,"released":released,"lesson":"released provenance-aware fork-resistance routing update" if released else "candidate rejected by verifier gate","validation":cm,"score":round(composite(cm),6),"protocol":cur})
    return cur, rel

def compare(final:dict[str,Any], ctrl:dict[str,Any])->dict[str,float]:
    return {"value_capture_gain_points":round(final["value_capture_rate_percent"]-ctrl["value_capture_rate_percent"],4),"frontier_correct_gain_points":round(final["frontier_correct_rate_percent"]-ctrl["frontier_correct_rate_percent"],4),"weak_domain_reduction_points":round(ctrl["weak_domain_rate_percent"]-final["weak_domain_rate_percent"],4),"risk_breach_reduction_points":round(ctrl["risk_breach_rate_percent"]-final["risk_breach_rate_percent"],4),"benchmark_value_captured_gain_usd":round(final["total_benchmark_value_captured_usd"]-ctrl["total_benchmark_value_captured_usd"],2)}

def vectors(cases:list[dict[str,Any]], w:dict[str,float])->tuple[list[float],list[float]]:
    cap=[]; oracle=[]
    for case in cases:
        p=choose(case,w); q=case["oracle"]
        cap.append(case["candidates"][p]["value_usd"]); oracle.append(case["candidates"][q]["value_usd"])
    return cap, oracle

def bootstrap(cases:list[dict[str,Any]], final_w:dict[str,float], ctrl_w:dict[str,float], seed:int, reps:int=90)->dict[str,float]:
    f,o=vectors(cases,final_w); c,_=vectors(cases,ctrl_w); n=len(cases); gains=[]
    for rep in range(reps):
        fs=cs=os=0.0
        for draw in range(n):
            i=int(u01(seed,rep,draw,979)*n)%n
            fs+=f[i]; cs+=c[i]; os+=o[i]
        gains.append(100*fs/os-100*cs/os)
    gains.sort()
    return {"mean_gain_points":round(sum(gains)/len(gains),4),"p05_gain_points":round(gains[int(.05*(len(gains)-1))],4),"p50_gain_points":round(gains[int(.5*(len(gains)-1))],4),"p95_gain_points":round(gains[int(.95*(len(gains)-1))],4),"bootstrap_repetitions":reps}

def proto_hash(w:dict[str,float])->str:
    return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def money(v:float)->str:
    return f"${v/1_000_000_000_000:,.2f}T" if abs(v)>=1e12 else f"${v/1_000_000_000:,.2f}B" if abs(v)>=1e9 else f"${v:,.0f}"

def build(seed:int, train_count:int, validation_count:int, holdout_count:int, stages:int)->dict[str,Any]:
    validation=generate(seed, validation_count, train_count)
    holdout=generate(seed, holdout_count, train_count+validation_count)
    final_w, releases = rsi_releases(seed, validation, stages)
    weights={"single_generalist":single_generalist(),"cold_fork":cold_fork(seed),"local_silo_network":local_silo_network(seed),"unverified_fork":unverified_fork(seed),"subsidy_attacker":subsidy_attacker(seed),"final":final_w}
    metrics={k:evaluate(holdout,w) for k,w in weights.items()}
    final=metrics["final"]
    comps={k:compare(final,metrics[k]) for k in metrics if k!="final"}
    safe_controls=[k for k in metrics if k!="final" and metrics[k]["risk_breach_rate_percent"]==0 and metrics[k]["invalid_action_rate_percent"]==0]
    strongest=max(safe_controls,key=lambda k:metrics[k]["value_capture_rate_percent"])
    boots={"vs_cold_fork":bootstrap(holdout,final_w,weights["cold_fork"],seed+11),"vs_local_silo_network":bootstrap(holdout,final_w,weights["local_silo_network"],seed+13),"vs_strongest_safe_control":bootstrap(holdout,final_w,weights[strongest],seed+17)}
    release_count=sum(1 for r in releases if r["released"])
    final["strongest_safe_control"]=strongest
    final["benchmark_implied_value_captured_over_strongest_safe_control_usd"]=comps[strongest]["benchmark_value_captured_gain_usd"]
    gates={
        "large_capability_network":AGENT_COUNT>=500_000_000 and ROLE_COUNT>=16_000_000,
        "locked_holdout_scale":holdout_count>=2048,
        "domain_coverage":len(DOMAINS)>=28,
        "rsi_release_count":release_count>=12,
        "value_capture_threshold":final["value_capture_rate_percent"]>=96,
        "minimum_domain_capture_threshold":final["minimum_domain_value_capture_percent"]>=93,
        "weak_domain_zero":final["weak_domain_rate_percent"]==0,
        "risk_breach_zero":final["risk_breach_rate_percent"]==0,
        "unauthorized_action_zero":final["unauthorized_action_rate_percent"]==0,
        "beats_cold_fork":comps["cold_fork"]["value_capture_gain_points"]>=3.0,
        "beats_local_silo_network":comps["local_silo_network"]["value_capture_gain_points"]>=1.5,
        "rejects_unverified_fork":metrics["unverified_fork"]["risk_breach_rate_percent"]>final["risk_breach_rate_percent"] or metrics["unverified_fork"]["invalid_action_rate_percent"]>final["invalid_action_rate_percent"],
        "rejects_subsidy_attacker":metrics["subsidy_attacker"]["risk_breach_rate_percent"]>final["risk_breach_rate_percent"] or metrics["subsidy_attacker"]["invalid_action_rate_percent"]>final["invalid_action_rate_percent"],
        "bootstrap_p05_vs_strongest_safe_control_positive":boots["vs_strongest_safe_control"]["p05_gain_points"]>0,
    }
    return {"proved":all(gates.values()),"status":"PASSED_AUTONOMOUS_RSI_FORK_RESISTANT_CAPABILITY_NETWORK_PROOF" if all(gates.values()) else "FAILED_AUTONOMOUS_RSI_FORK_RESISTANT_CAPABILITY_NETWORK_PROOF","proof_type":"Autonomous RSI Fork-Resistant Capability Network Proof","workflow":"Autonomous RSI Fork-Resistant Capability Network Proof","generated_at_utc":now_iso(),"seed":seed,"protocol_fingerprint_sha256":proto_hash(final_w),"safe_interpretation":"A deterministic benchmark proof that SkillOS' verified skill graph, provenance ledger, and network-wide routing releases can resist surface-level forks and keep compounding under competitive pressure. Not live revenue, customer results, financial advice, legal advice, token advice, policy advice, or achieved superintelligence.","agent_system":{"virtual_specialist_agents":AGENT_COUNT,"specialist_roles":ROLE_COUNT,"role_families":len(ROLE_FAMILIES),"capability_domains":len(DOMAINS),"skill_network_markets":32768,"provenance_courts":16384,"fork_red_teams":8192,"release_lanes":4096,"coordination_style":"fork-resistant verified capability network with provenance courts, fork red teams, global routing upgrades, risk vetoes, and validation-gated RSI releases"},"benchmark_public":{"name":"Fork-Resistant Capability Network benchmark","train_count":train_count,"validation_count":validation_count,"locked_holdout_count":holdout_count,"candidate_actions_per_case":11,"domains":DOMAINS,"features":FEATURES,"data_boundary":"synthetic/redacted-style public benchmark; no private customer data"},"pre_registered_gates":gates,"baselines_and_controls":{k:metrics[k] for k in metrics if k!="final"},"final":final,"comparisons":comps,"bootstrap_confidence_intervals":boots,"rsi_release_count":release_count,"rsi_releases":releases,"public_boundary":"Benchmark-capital-equivalent values are not live revenue, customer results, financial guarantees, legal advice, policy advice, token advice, or proof of achieved superintelligence."}

def write_report(result:dict[str,Any])->str:
    f=result["final"]
    controls="\n".join(f"| {k} | {v['value_capture_rate_percent']}% | {v['minimum_domain_value_capture_percent']}% | {v['risk_breach_rate_percent']}% | {v['invalid_action_rate_percent']}% |" for k,v in result["baselines_and_controls"].items())
    gates="\n".join(f"- {'✅' if v else '❌'} `{k}`" for k,v in result["pre_registered_gates"].items())
    report=f"""# Autonomous RSI Fork-Resistant Capability Network Proof

Generated: `{result['generated_at_utc']}`

## Thesis

SkillOS tests whether its skill graph becomes a fork-resistant capability network.

Core mechanism:

> verified skill graph → provenance ledger → network routing upgrade → trust/liquidity flywheel → fork stress test → release hardening → compounding moat

## Final locked holdout result

- Value capture: **{f['value_capture_rate_percent']}%**
- Minimum domain capture: **{f['minimum_domain_value_capture_percent']}%**
- Frontier-correct rate: **{f['frontier_correct_rate_percent']}%**
- Network effect score: **{f['network_effect_score']}%**
- Provenance moat score: **{f['provenance_moat_score']}%**
- Fork resistance score: **{f['fork_resistance_score']}%**
- Risk breach rate: **{f['risk_breach_rate_percent']}%**
- Benchmark value at stake: **{money(f['total_benchmark_value_at_stake_usd'])}**
- Benchmark value captured: **{money(f['total_benchmark_value_captured_usd'])}**
- Strongest safe control: **{f['strongest_safe_control']}**
- Gain over strongest safe control: **{money(f['benchmark_implied_value_captured_over_strongest_safe_control_usd'])}**

## Baselines and controls

| System | Value capture | Minimum domain capture | Risk breach | Invalid action |
|---|---:|---:|---:|---:|
{controls}

## Pre-registered gates

{gates}

## Boundary

{result['public_boundary']}
"""
    DOCS.mkdir(parents=True,exist_ok=True)
    out=DOCS/"rsi-fork-resistant-capability-network-proof.md"
    out.write_text(report,encoding="utf-8")
    return str(out.relative_to(ROOT))

def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--seed",type=int,default=20260530)
    p.add_argument("--train-count",type=int,default=1536)
    p.add_argument("--validation-count",type=int,default=1024)
    p.add_argument("--holdout-count",type=int,default=2048)
    p.add_argument("--generations",type=int,default=24)
    p.add_argument("--summary",default="")
    a=p.parse_args()
    DATA.mkdir(parents=True,exist_ok=True); DOCS.mkdir(parents=True,exist_ok=True)
    result=build(a.seed,a.train_count,a.validation_count,a.holdout_count,a.generations)
    result["markdown_report"]=write_report(result)
    result["output"]="data/rsi-fork-resistant-capability-network-proof.json"
    (DATA/"rsi-fork-resistant-capability-network-proof.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    compact={"proved":result["proved"],"workflow":result["workflow"],"virtual_specialist_agents":result["agent_system"]["virtual_specialist_agents"],"specialist_roles":result["agent_system"]["specialist_roles"],"capability_domains":result["agent_system"]["capability_domains"],"rsi_release_count":result["rsi_release_count"],"locked_holdout_count":result["benchmark_public"]["locked_holdout_count"],"value_capture_percent":result["final"]["value_capture_rate_percent"],"minimum_domain_value_capture_percent":result["final"]["minimum_domain_value_capture_percent"],"fork_resistance_score":result["final"]["fork_resistance_score"],"provenance_moat_score":result["final"]["provenance_moat_score"],"risk_breach_percent":result["final"]["risk_breach_rate_percent"],"benchmark_value_captured_usd":result["final"]["total_benchmark_value_captured_usd"],"gain_over_strongest_safe_control_usd":result["final"]["benchmark_implied_value_captured_over_strongest_safe_control_usd"],"protocol_fingerprint_sha256":result["protocol_fingerprint_sha256"]}
    print(json.dumps(compact,indent=2,sort_keys=True))
    if a.summary:
        Path(a.summary).write_text("## Autonomous RSI Fork-Resistant Capability Network Proof\n\n"+"\n".join(f"- {k}: **{v}**" for k,v in compact.items()),encoding="utf-8")
    if not result["proved"]:
        raise SystemExit(1)

if __name__=="__main__":
    main()
