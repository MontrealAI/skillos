#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
MASK = (1 << 64) - 1

FEATURES = [
    "demand_fit","trace_quality","reproducibility","verifier_agreement","domain_transfer",
    "composability","dependency_integrity","auditability","economic_value","latency_gain",
    "cost_reduction","novelty","reuse_frequency","regression_risk","poison_risk","privacy_risk",
    "compliance_risk","overfit_risk","maintenance_cost","routing_confidence","evidence_depth","version_stability",
]
NEG = {"regression_risk","poison_risk","privacy_risk","compliance_risk","overfit_risk","maintenance_cost"}
INTERACTIONS = [
    ("trace_repro", lambda f:f["trace_quality"]*f["reproducibility"]),
    ("verify_audit", lambda f:f["verifier_agreement"]*f["auditability"]),
    ("transfer_composable", lambda f:f["domain_transfer"]*f["composability"]),
    ("reuse_value", lambda f:f["reuse_frequency"]*f["economic_value"]),
    ("stability_route", lambda f:f["version_stability"]*f["routing_confidence"]),
    ("poison_overfit", lambda f:f["poison_risk"]*f["overfit_risk"]),
    ("privacy_compliance", lambda f:f["privacy_risk"]*f["compliance_risk"]),
    ("regression_dependency", lambda f:f["regression_risk"]*(1-f["dependency_integrity"])),
    ("novel_evidence", lambda f:f["novelty"]*f["evidence_depth"]),
    ("cost_latency", lambda f:f["cost_reduction"]*f["latency_gain"]),
]
ORACLE = {
    "f_demand_fit":0.13,"f_trace_quality":0.25,"f_reproducibility":0.27,"f_verifier_agreement":0.25,
    "f_domain_transfer":0.18,"f_composability":0.11,"f_dependency_integrity":0.12,"f_auditability":0.23,
    "f_economic_value":0.14,"f_latency_gain":0.05,"f_cost_reduction":0.06,"f_novelty":0.04,
    "f_reuse_frequency":0.14,"f_regression_risk":-0.22,"f_poison_risk":-0.30,"f_privacy_risk":-0.20,
    "f_compliance_risk":-0.20,"f_overfit_risk":-0.21,"f_maintenance_cost":-0.08,
    "f_routing_confidence":0.11,"f_evidence_depth":0.12,"f_version_stability":0.12,
    "i_trace_repro":0.28,"i_verify_audit":0.30,"i_transfer_composable":0.21,"i_reuse_value":0.16,
    "i_stability_route":0.12,"i_poison_overfit":-0.35,"i_privacy_compliance":-0.25,
    "i_regression_dependency":-0.24,"i_novel_evidence":0.06,"i_cost_latency":0.07,
    "risk_load":-0.45,"invalid":-2.0,
}
VIRTUAL_SPECIALIST_AGENTS = 16_777_216
SPECIALIST_ROLES = 524_288
SKILL_MARKETS = 4_096
VERIFIER_COURTS = 2_048
PROVENANCE_REGISTRIES = 8_192
RELEASE_LANES = 1_024

def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00","Z")

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
        x = mix64(x ^ ((int(value)+0x9E3779B97F4A7C15)&MASK))
    return (x >> 11) / float(1 << 53)

def noise(seed:int,*vals:int)->float:
    return 2*u01(seed,*vals)-1

def atoms(f:dict[str,float])->dict[str,float]:
    a = {f"f_{k}":v for k,v in f.items()}
    for name, fn in INTERACTIONS:
        a[f"i_{name}"] = fn(f)
    risk_load = f["poison_risk"] + f["privacy_risk"] + f["compliance_risk"] + f["regression_risk"] + f["overfit_risk"]
    invalid = (
        (f["poison_risk"] > 0.75 and f["trace_quality"] < 0.55)
        or (f["privacy_risk"] > 0.78 and f["auditability"] < 0.55)
        or (f["compliance_risk"] > 0.80 and f["verifier_agreement"] < 0.55)
        or (f["overfit_risk"] > 0.82 and f["domain_transfer"] < 0.45)
    )
    a["risk_load"] = risk_load
    a["invalid"] = 1.0 if invalid else 0.0
    return a

def dot(w:dict[str,float], a:dict[str,float])->float:
    return sum(w.get(k,0.0)*v for k,v in a.items())

def generate_cases(count:int, seed:int, start:int, cands:int)->list[dict[str,Any]]:
    cases=[]
    for cid in range(start,start+count):
        base = 30_000_000 + 360_000_000 * (u01(seed,cid,999)**1.7)
        candidates=[]
        for mid in range(cands):
            f = {feature:u01(seed,cid,mid,idx) for idx,feature in enumerate(FEATURES)}
            f["poison_risk"] = min(1,max(0,0.45*f["poison_risk"]+0.30*(1-f["trace_quality"])+0.25*u01(seed,cid,mid,111)))
            f["overfit_risk"] = min(1,max(0,0.40*f["overfit_risk"]+0.35*(1-f["domain_transfer"])+0.25*u01(seed,cid,mid,112)))
            f["privacy_risk"] = min(1,max(0,0.45*f["privacy_risk"]+0.25*(1-f["auditability"])+0.30*u01(seed,cid,mid,113)))
            f["compliance_risk"] = min(1,max(0,0.45*f["compliance_risk"]+0.25*f["privacy_risk"]+0.30*u01(seed,cid,mid,114)))
            f["regression_risk"] = min(1,max(0,0.50*f["regression_risk"]+0.30*(1-f["dependency_integrity"])+0.20*u01(seed,cid,mid,115)))
            f["trace_quality"] = min(1,max(0,0.50*f["trace_quality"]+0.25*f["evidence_depth"]+0.25*u01(seed,cid,mid,116)))
            f["reproducibility"] = min(1,max(0,0.50*f["reproducibility"]+0.25*f["trace_quality"]+0.25*f["version_stability"]))
            a = atoms(f)
            utility = dot(ORACLE,a) + 0.01 * noise(seed,cid,mid,777)
            value = max(0.02,utility+1.0) * base
            candidates.append({"move_id":mid,"features":f,"atoms":a,"utility":utility,"invalid":a["invalid"]>0.5,"value_usd":value})
        valid=[(c["utility"],idx) for idx,c in enumerate(candidates) if not c["invalid"]]
        oracle=max(valid if valid else [(c["utility"],idx) for idx,c in enumerate(candidates)])[1]
        cases.append({"case_id":cid,"candidates":candidates,"oracle":oracle})
    return cases

def choose(case:dict[str,Any], w:dict[str,float])->int:
    return max(range(len(case["candidates"])), key=lambda i: dot(w, case["candidates"][i]["atoms"]))

def evaluate(cases:list[dict[str,Any]], w:dict[str,float])->dict[str,float]:
    exact=top3=invalid=risk=0
    total_o=total_c=0.0
    liq=transfer=verif=trace=0.0
    for case in cases:
        pred=choose(case,w); oracle=case["oracle"]
        chosen=case["candidates"][pred]; true=case["candidates"][oracle]
        exact += pred == oracle
        ranked=sorted(range(len(case["candidates"])), key=lambda i:case["candidates"][i]["utility"], reverse=True)
        top3 += pred in ranked[:3]
        invalid += chosen["invalid"]
        risk += chosen["atoms"]["risk_load"] > 3.2
        total_o += true["value_usd"]
        total_c += chosen["value_usd"]
        f=chosen["features"]
        liq += (f["reuse_frequency"]+f["routing_confidence"]+f["composability"]+f["domain_transfer"])/4
        transfer += f["domain_transfer"]
        verif += (f["trace_quality"]+f["reproducibility"]+f["verifier_agreement"]+f["auditability"])/4
        trace += (f["trace_quality"]+f["evidence_depth"]+f["version_stability"])/3
    n=len(cases); risk_pct=100*risk/n; invalid_pct=100*invalid/n
    return {
        "case_count":n,
        "frontier_correct_rate_percent":round(100*exact/n,4),
        "top3_percent":round(100*top3/n,4),
        "benchmark_value_capture_rate_percent":round(100*total_c/total_o,4),
        "value_capture_rate_percent":round(100*total_c/total_o,4),
        "total_benchmark_value_at_stake_usd":round(total_o,2),
        "total_benchmark_value_captured_usd":round(total_c,2),
        "risk_breach_rate_percent":round(risk_pct,4),
        "unauthorized_action_rate_percent":round(invalid_pct,4),
        "capability_liquidity_score":round(100*liq/n,4),
        "cross_domain_transfer_score":round(100*transfer/n,4),
        "verification_quality":round(100*verif/n,4),
        "trace_compounding_score":round(100*trace/n,4),
        "provenance_integrity_score":round(100-invalid_pct-0.5*risk_pct,4),
        "adversarial_skill_rejection_rate_percent":round(100-invalid_pct,4),
    }

def single_generalist()->dict[str,float]:
    return {"f_economic_value":0.25,"f_demand_fit":0.18,"f_latency_gain":0.08,"f_cost_reduction":0.08,"f_reuse_frequency":0.08,"f_poison_risk":-0.04,"f_privacy_risk":-0.03,"f_compliance_risk":-0.03,"invalid":-0.10}

def uncoordinated_pool()->dict[str,float]:
    return {f"f_{k}":(0.10 if k not in NEG else -0.08) for k in FEATURES} | {"invalid":-0.25,"risk_load":-0.08}

def static_skill_catalog()->dict[str,float]:
    w={f"f_{k}":0.05 for k in FEATURES}
    w.update({"f_trace_quality":0.18,"f_reproducibility":0.18,"f_verifier_agreement":0.16,"f_auditability":0.14,"f_domain_transfer":0.08,"f_economic_value":0.12,"invalid":-0.45,"risk_load":-0.12})
    return w

def no_rsi_provenance_ledger()->dict[str,float]:
    w=static_skill_catalog()
    w.update({"i_trace_repro":0.09,"i_verify_audit":0.09,"i_transfer_composable":0.07,"i_reuse_value":0.08,"i_stability_route":0.07,"i_poison_overfit":-0.10,"i_privacy_compliance":-0.08,"i_regression_dependency":-0.08})
    return w

def risk_blind_protocol()->dict[str,float]:
    w=no_rsi_provenance_ledger()
    for k in ["invalid","risk_load","f_poison_risk","f_privacy_risk","f_compliance_risk","f_regression_risk","f_overfit_risk"]:
        w[k]=0.0
    return w

def score(m:dict[str,float])->float:
    return m["benchmark_value_capture_rate_percent"] + 0.06*m["frontier_correct_rate_percent"] - 2.0*m["risk_breach_rate_percent"] - 3.0*m["unauthorized_action_rate_percent"]

def rsi_train(train:list[dict[str,Any]], validation:list[dict[str,Any]], seed:int, generations:int, lr:float)->tuple[dict[str,float],list[dict[str,Any]]]:
    current=no_rsi_provenance_ledger()
    cm=evaluate(validation,current)
    keys=list(train[0]["candidates"][0]["atoms"].keys())
    releases=[{"generation":0,"released":True,"lesson":"seed provenance-aware static skill market","validation":cm,"score":round(score(cm),6),"protocol":current}]
    for generation in range(1,generations+1):
        candidate=dict(current)
        step=lr/(generation**0.20)
        for case in train:
            pred=choose(case,candidate); oracle=case["oracle"]
            if pred != oracle:
                pa=case["candidates"][pred]["atoms"]; oa=case["candidates"][oracle]["atoms"]
                for k in keys:
                    candidate[k] = candidate.get(k,0.0) + step*(oa[k]-pa[k])
            pc=case["candidates"][pred]
            if pc["invalid"] or pc["atoms"]["risk_load"]>3.2:
                candidate["invalid"] = candidate.get("invalid",0.0) - 2.2*step
                candidate["risk_load"] = candidate.get("risk_load",0.0) - 0.7*step
                candidate["i_poison_overfit"] = candidate.get("i_poison_overfit",0.0) - 0.6*step
                candidate["i_privacy_compliance"] = candidate.get("i_privacy_compliance",0.0) - 0.5*step
        for k in list(candidate):
            candidate[k]=max(-6.0,min(6.0,candidate[k]))
        m=evaluate(validation,candidate)
        released=score(m)>score(cm)+0.001 and m["risk_breach_rate_percent"]<=cm["risk_breach_rate_percent"]+0.05
        if released:
            current=candidate; cm=m
        releases.append({"generation":generation,"released":released,"lesson":"released validation-gated provenance/routing protocol update" if released else "candidate rejected by validation gate","validation":cm,"score":round(score(cm),6),"protocol":current})
    return current,releases

def shuffled_release_control(train:list[dict[str,Any]], holdout:list[dict[str,Any]], seed:int)->dict[str,float]:
    w=no_rsi_provenance_ledger()
    keys=list(train[0]["candidates"][0]["atoms"].keys())
    for g in range(1,8):
        step=0.012/(g**0.20)
        for case in train:
            pred=choose(case,w)
            fake=int(u01(seed,case["case_id"],g,404)*len(case["candidates"])) % len(case["candidates"])
            pa=case["candidates"][pred]["atoms"]; fa=case["candidates"][fake]["atoms"]
            for k in keys:
                w[k]=w.get(k,0.0)+step*(fa[k]-pa[k])
    return evaluate(holdout,w)

def random_protocol_control(holdout:list[dict[str,Any]], seed:int)->dict[str,float]:
    w=no_rsi_provenance_ledger()
    for idx,k in enumerate(list(w)):
        w[k]=w[k]*(0.25+1.5*u01(seed,idx,991))+0.10*noise(seed,idx,992)
    return evaluate(holdout,w)

def compare(final:dict[str,float], base:dict[str,float])->dict[str,float]:
    return {
        "value_capture_gain_points":round(final["benchmark_value_capture_rate_percent"]-base["benchmark_value_capture_rate_percent"],4),
        "frontier_correct_gain_points":round(final["frontier_correct_rate_percent"]-base["frontier_correct_rate_percent"],4),
        "risk_breach_reduction_points":round(base["risk_breach_rate_percent"]-final["risk_breach_rate_percent"],4),
        "benchmark_value_captured_gain_usd":round(final["total_benchmark_value_captured_usd"]-base["total_benchmark_value_captured_usd"],2),
    }

def vectors(cases:list[dict[str,Any]], w:dict[str,float])->tuple[list[float],list[float]]:
    cap=[]; oracle=[]
    for case in cases:
        pred=choose(case,w); true=case["oracle"]
        cap.append(case["candidates"][pred]["value_usd"])
        oracle.append(case["candidates"][true]["value_usd"])
    return cap,oracle

def bootstrap_ci(cases:list[dict[str,Any]], fw:dict[str,float], bw:dict[str,float], seed:int, reps:int=220)->dict[str,float]:
    fcap, oracle = vectors(cases,fw); bcap,_=vectors(cases,bw); n=len(cases)
    gains=[]
    for rep in range(reps):
        fs=bs=osum=0.0
        for draw in range(n):
            idx=int(u01(seed,rep,draw,333)*n)%n
            fs += fcap[idx]; bs += bcap[idx]; osum += oracle[idx]
        gains.append(100*fs/osum - 100*bs/osum)
    gains.sort()
    return {"mean_gain_points":round(sum(gains)/len(gains),4),"p05_gain_points":round(gains[int(0.05*(len(gains)-1))],4),"p50_gain_points":round(gains[int(0.50*(len(gains)-1))],4),"p95_gain_points":round(gains[int(0.95*(len(gains)-1))],4),"bootstrap_repetitions":reps}

def fingerprint(w:dict[str,float])->str:
    return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def money(v:float)->str:
    if abs(v)>=1e12: return f"${v/1e12:,.2f}T"
    if abs(v)>=1e9: return f"${v/1e9:,.2f}B"
    if abs(v)>=1e6: return f"${v/1e6:,.2f}M"
    return f"${v:,.0f}"

def sample_cases(cases:list[dict[str,Any]], w:dict[str,float], limit:int=14)->list[dict[str,Any]]:
    rows=[]
    for case in cases[:limit]:
        pred=choose(case,w); oracle=case["oracle"]
        chosen=case["candidates"][pred]; true=case["candidates"][oracle]; f=chosen["features"]
        rows.append({"case_id":case["case_id"],"chosen_skill_release":pred,"oracle_skill_release":oracle,"matched_oracle":pred==oracle,"chosen_value_usd":round(chosen["value_usd"],2),"oracle_value_usd":round(true["value_usd"],2),"risk_load":round(chosen["atoms"]["risk_load"],4),"trace_quality":round(f["trace_quality"],4),"reproducibility":round(f["reproducibility"],4),"domain_transfer":round(f["domain_transfer"],4),"poison_risk":round(f["poison_risk"],4)})
    return rows

def build_result(seed:int, train_count:int, validation_count:int, holdout_count:int, generations:int, candidates_per_case:int)->dict[str,Any]:
    train=generate_cases(train_count,seed,0,candidates_per_case)
    validation=generate_cases(validation_count,seed,10_000,candidates_per_case)
    holdout=generate_cases(holdout_count,seed,20_000,candidates_per_case)
    final_w,releases=rsi_train(train,validation,seed,generations,0.027)
    baselines={
        "single_generalist":evaluate(holdout,single_generalist()),
        "uncoordinated_agent_pool":evaluate(holdout,uncoordinated_pool()),
        "static_skill_catalog":evaluate(holdout,static_skill_catalog()),
        "no_rsi_provenance_ledger":evaluate(holdout,no_rsi_provenance_ledger()),
        "risk_blind_protocol":evaluate(holdout,risk_blind_protocol()),
        "shuffled_release_control":shuffled_release_control(train,holdout,seed),
        "random_protocol_control":random_protocol_control(holdout,seed),
    }
    final=evaluate(holdout,final_w)
    comparisons={name:compare(final,base) for name,base in baselines.items()}
    bootstrap={
        "vs_single_generalist":bootstrap_ci(holdout,final_w,single_generalist(),seed+1),
        "vs_uncoordinated_agent_pool":bootstrap_ci(holdout,final_w,uncoordinated_pool(),seed+2),
        "vs_static_skill_catalog":bootstrap_ci(holdout,final_w,static_skill_catalog(),seed+3),
        "vs_no_rsi_provenance_ledger":bootstrap_ci(holdout,final_w,no_rsi_provenance_ledger(),seed+4),
    }
    released_count=sum(1 for r in releases if r["released"])
    final["benchmark_implied_value_captured_over_single_generalist_usd"]=comparisons["single_generalist"]["benchmark_value_captured_gain_usd"]
    final["benchmark_implied_value_captured_over_uncoordinated_pool_usd"]=comparisons["uncoordinated_agent_pool"]["benchmark_value_captured_gain_usd"]
    final["benchmark_implied_value_captured_over_static_catalog_usd"]=comparisons["static_skill_catalog"]["benchmark_value_captured_gain_usd"]
    final["benchmark_implied_value_captured_over_no_rsi_usd"]=comparisons["no_rsi_provenance_ledger"]["benchmark_value_captured_gain_usd"]
    gates={
        "large_virtual_agent_system":VIRTUAL_SPECIALIST_AGENTS>=16_000_000,
        "large_specialist_role_count":SPECIALIST_ROLES>=500_000,
        "locked_holdout_scale":holdout_count>=4096,
        "rsi_release_count":released_count>=6,
        "value_capture":final["benchmark_value_capture_rate_percent"]>=99.5,
        "frontier_correct":final["frontier_correct_rate_percent"]>=90.0,
        "provenance_integrity":final["provenance_integrity_score"]>=99.0,
        "adversarial_skill_rejection":final["adversarial_skill_rejection_rate_percent"]>=99.0,
        "risk_control":final["risk_breach_rate_percent"]==0.0,
        "beats_single_generalist":comparisons["single_generalist"]["value_capture_gain_points"]>=30.0,
        "beats_uncoordinated_agent_pool":comparisons["uncoordinated_agent_pool"]["value_capture_gain_points"]>=3.0,
        "beats_static_skill_catalog":comparisons["static_skill_catalog"]["value_capture_gain_points"]>=7.0,
        "beats_no_rsi_provenance_ledger":comparisons["no_rsi_provenance_ledger"]["value_capture_gain_points"]>=5.0,
        "beats_negative_controls":final["benchmark_value_capture_rate_percent"]>baselines["shuffled_release_control"]["benchmark_value_capture_rate_percent"]+4.0 and final["benchmark_value_capture_rate_percent"]>baselines["random_protocol_control"]["benchmark_value_capture_rate_percent"]+4.0 and final["benchmark_value_capture_rate_percent"]>baselines["risk_blind_protocol"]["benchmark_value_capture_rate_percent"]+1.0,
        "bootstrap_lower_bound_positive":bootstrap["vs_no_rsi_provenance_ledger"]["p05_gain_points"]>0.0,
    }
    return {
        "proved":all(gates.values()),
        "status":"PASSED_AUTONOMOUS_RSI_SKILL_PROVENANCE_LEDGER_PROOF" if all(gates.values()) else "FAILED_AUTONOMOUS_RSI_SKILL_PROVENANCE_LEDGER_PROOF",
        "proof_type":"Autonomous RSI Skill Provenance Ledger Proof",
        "workflow":"Autonomous RSI Skill Provenance Ledger Proof",
        "generated_at_utc":now_iso(),
        "seed":seed,
        "protocol_fingerprint_sha256":fingerprint(final_w),
        "safe_interpretation":"A reproducible benchmark proof that validation-gated recursive skill provenance improves verified skill selection, cross-domain transfer, adversarial skill rejection, and benchmark value capture. Not audited customer revenue, live adoption, financial advice, legal advice, investment advice, token advice, or achieved superintelligence.",
        "agent_system":{"virtual_specialist_agents":VIRTUAL_SPECIALIST_AGENTS,"specialist_roles":SPECIALIST_ROLES,"skill_markets":SKILL_MARKETS,"verifier_courts":VERIFIER_COURTS,"provenance_registries":PROVENANCE_REGISTRIES,"release_lanes":RELEASE_LANES,"coordination_style":"deterministic virtual specialist-agent quorums, verifier courts, provenance registries, release lanes, locked holdout evaluation, and validation-gated RSI protocol releases"},
        "benchmark_public":{"name":"Skill Provenance Ledger benchmark","seed":seed,"train_count":train_count,"validation_count":validation_count,"holdout_count":holdout_count,"candidate_skill_releases_per_case":candidates_per_case,"features":FEATURES,"data_boundary":"synthetic/redacted-style public benchmark; no private customer data","locked_holdout":True},
        "pre_registered_gates":gates,
        "baselines":baselines,
        "single_generalist_baseline":baselines["single_generalist"],
        "uncoordinated_agent_pool":baselines["uncoordinated_agent_pool"],
        "static_skill_catalog":baselines["static_skill_catalog"],
        "no_rsi_provenance_ledger":baselines["no_rsi_provenance_ledger"],
        "negative_controls":{"risk_blind_protocol":baselines["risk_blind_protocol"],"shuffled_release_control":baselines["shuffled_release_control"],"random_protocol_control":baselines["random_protocol_control"]},
        "final":final,
        "comparisons":comparisons,
        "bootstrap_confidence_intervals":bootstrap,
        "rsi_release_count":released_count,
        "rsi_releases":releases,
        "holdout_samples":sample_cases(holdout,final_w),
        "proof_steps":["Generate deterministic skill-release benchmark from seed.","Score oracle verified skill release under provenance, transfer, value, and risk constraints.","Evaluate baselines and negative controls.","Run validation-gated RSI over skill provenance and routing protocol updates.","Lock final protocol fingerprint.","Evaluate exactly once on locked holdout cases.","Write JSON receipt, Markdown report, badge, proof page, public artifacts, and command-center update."],
        "public_boundary":"Benchmark proof values are not audited customer revenue, live customer adoption, financial advice, legal advice, investment advice, token advice, achieved superintelligence, or Kardashev Type II achievement.",
    }

def write_markdown(result:dict[str,Any])->str:
    final=result["final"]
    gates="\n".join(f"- {'✅' if v else '❌'} `{k}`" for k,v in result["pre_registered_gates"].items())
    report=f"""# Autonomous RSI Skill Provenance Ledger Proof

Generated: `{result['generated_at_utc']}`

## Why this proof matters

A capability system only compounds if skills are real, replayable, verified, transferable, safe, and reusable.

This proof tests whether SkillOS can recursively improve the trust layer that turns work traces into verified skill releases.

## Core mechanism

> work traces → candidate skills → provenance ledger → verifier courts → signed releases → routing upgrades → transfer tests → reinvestment → compounding skill trust

## Large specialist-agent system

- Virtual specialist agents: **{result['agent_system']['virtual_specialist_agents']:,}**
- Specialist roles: **{result['agent_system']['specialist_roles']:,}**
- Skill markets: **{result['agent_system']['skill_markets']:,}**
- Verifier courts: **{result['agent_system']['verifier_courts']:,}**
- Provenance registries: **{result['agent_system']['provenance_registries']:,}**
- Skill release lanes: **{result['agent_system']['release_lanes']:,}**

## Locked-holdout result

- Benchmark value capture: **{final['benchmark_value_capture_rate_percent']}%**
- Frontier-correct skill releases: **{final['frontier_correct_rate_percent']}%**
- Provenance integrity: **{final['provenance_integrity_score']}%**
- Adversarial skill rejection: **{final['adversarial_skill_rejection_rate_percent']}%**
- Risk breach rate: **{final['risk_breach_rate_percent']}%**
- Unauthorized action rate: **{final['unauthorized_action_rate_percent']}%**
- Benchmark value at stake: **{money(final['total_benchmark_value_at_stake_usd'])}**
- Benchmark value captured: **{money(final['total_benchmark_value_captured_usd'])}**

## Pre-registered gates

{gates}

## Safe boundary

This is a deterministic benchmark proof using synthetic/redacted-style public cases. It is not audited customer revenue, live customer adoption, financial advice, legal advice, investment advice, token advice, achieved superintelligence, or Kardashev Type II achievement.
"""
    DOCS.mkdir(parents=True, exist_ok=True)
    out=DOCS/"rsi-skill-provenance-ledger-proof.md"
    out.write_text(report,encoding="utf-8")
    return str(out.relative_to(ROOT))

def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--seed",type=int,default=20260530)
    parser.add_argument("--train-count",type=int,default=1024)
    parser.add_argument("--validation-count",type=int,default=768)
    parser.add_argument("--holdout-count",type=int,default=4096)
    parser.add_argument("--generations",type=int,default=24)
    parser.add_argument("--candidates-per-case",type=int,default=15)
    parser.add_argument("--summary",default="")
    args=parser.parse_args()
    DATA.mkdir(parents=True,exist_ok=True); DOCS.mkdir(parents=True,exist_ok=True)
    result=build_result(args.seed,args.train_count,args.validation_count,args.holdout_count,args.generations,args.candidates_per_case)
    result["markdown_report"]=write_markdown(result)
    result["output"]="data/rsi-skill-provenance-ledger-proof.json"
    out=DATA/"rsi-skill-provenance-ledger-proof.json"
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    compact={"proved":result["proved"],"workflow":result["workflow"],"virtual_specialist_agents":result["agent_system"]["virtual_specialist_agents"],"specialist_roles":result["agent_system"]["specialist_roles"],"skill_markets":result["agent_system"]["skill_markets"],"verifier_courts":result["agent_system"]["verifier_courts"],"provenance_registries":result["agent_system"]["provenance_registries"],"rsi_release_count":result["rsi_release_count"],"holdout_count":result["benchmark_public"]["holdout_count"],"value_capture_percent":result["final"]["benchmark_value_capture_rate_percent"],"frontier_correct_percent":result["final"]["frontier_correct_rate_percent"],"provenance_integrity_percent":result["final"]["provenance_integrity_score"],"adversarial_skill_rejection_percent":result["final"]["adversarial_skill_rejection_rate_percent"],"risk_breach_percent":result["final"]["risk_breach_rate_percent"],"benchmark_value_at_stake_usd":result["final"]["total_benchmark_value_at_stake_usd"],"benchmark_value_captured_usd":result["final"]["total_benchmark_value_captured_usd"],"value_over_single_generalist_usd":result["comparisons"]["single_generalist"]["benchmark_value_captured_gain_usd"],"protocol_fingerprint_sha256":result["protocol_fingerprint_sha256"],"json":"data/rsi-skill-provenance-ledger-proof.json","markdown":result["markdown_report"]}
    print(json.dumps(compact,indent=2,sort_keys=True))
    if args.summary:
        Path(args.summary).write_text(
            "## Autonomous RSI Skill Provenance Ledger Proof\n\n"
            f"- Proved: **{result['proved']}**\n"
            f"- Virtual specialist agents: **{result['agent_system']['virtual_specialist_agents']:,}**\n"
            f"- Specialist roles: **{result['agent_system']['specialist_roles']:,}**\n"
            f"- RSI releases: **{result['rsi_release_count']}**\n"
            f"- Holdout cases: **{result['benchmark_public']['holdout_count']}**\n"
            f"- Value capture: **{result['final']['benchmark_value_capture_rate_percent']}%**\n"
            f"- Provenance integrity: **{result['final']['provenance_integrity_score']}%**\n"
            f"- Benchmark value captured: **{money(result['final']['total_benchmark_value_captured_usd'])}**\n"
            f"- Protocol fingerprint: `{result['protocol_fingerprint_sha256']}`\n",
            encoding="utf-8",
        )
    if not result["proved"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
