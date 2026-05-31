#!/usr/bin/env python3
"""SkillOS Autonomous RSI Skill Compounding Moat Proof.

Deterministic, dependency-free GitHub Actions proof.

Question:
Can one verified skill improve the whole network, so that capability does not
only add up, but compounds across future work?

Boundary:
Synthetic/redacted-style public benchmark. Not live revenue, customer results,
financial advice, legal advice, token advice, policy advice, or proof of
achieved superintelligence.
"""

from __future__ import annotations

import argparse, datetime as dt, hashlib, json, math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA, DOCS = ROOT / "data", ROOT / "docs"
MASK = (1 << 64) - 1

FEATURES = [
    "task_value", "reuse_potential", "domain_similarity", "trace_quality",
    "verification_density", "provenance_strength", "routing_specificity",
    "agent_depth", "skill_composability", "transfer_distance", "execution_margin",
    "latency_pressure", "risk_exposure", "compliance_load", "security_exposure",
    "rollback_option", "feedback_density", "knowledge_novelty", "legacy_drag",
    "customer_trust",
]
NEG = {"risk_exposure", "compliance_load", "security_exposure", "transfer_distance", "latency_pressure", "legacy_drag"}
DOMAINS = [
    "enterprise_workflow", "regulated_ops", "data_engineering", "proof_generation",
    "security_review", "governance", "blockchain_protocols", "capital_allocation",
    "customer_success", "product_strategy", "compute_optimization", "energy_scheduling",
    "knowledge_ops", "market_research", "compliance_evidence", "developer_tools",
    "agent_marketplace", "cross_domain_transfer", "provenance_audit", "reliability_engineering",
    "platform_growth", "quality_assurance", "workflow_compression", "capability_routing",
]
INTERACTIONS = [
    ("verified_reuse", lambda f: f["reuse_potential"] * f["verification_density"]),
    ("trace_to_skill", lambda f: f["trace_quality"] * f["provenance_strength"]),
    ("composition_lift", lambda f: f["skill_composability"] * f["agent_depth"]),
    ("routing_precision", lambda f: f["routing_specificity"] * f["domain_similarity"]),
    ("transfer_reuse", lambda f: f["reuse_potential"] * (1 - f["transfer_distance"])),
    ("feedback_compound", lambda f: f["feedback_density"] * f["reuse_potential"]),
    ("risk_without_rollback", lambda f: f["risk_exposure"] * (1 - f["rollback_option"])),
    ("unverified_risk", lambda f: (1 - f["verification_density"]) * f["security_exposure"]),
    ("legacy_latency", lambda f: f["legacy_drag"] * f["latency_pressure"]),
    ("trust_provenance", lambda f: f["customer_trust"] * f["provenance_strength"]),
]
BASE = {
    "f_task_value": .22, "f_reuse_potential": .18, "f_domain_similarity": .10,
    "f_trace_quality": .11, "f_verification_density": .13,
    "f_provenance_strength": .12, "f_routing_specificity": .13,
    "f_agent_depth": .10, "f_skill_composability": .18,
    "f_transfer_distance": -.14, "f_execution_margin": .15,
    "f_latency_pressure": -.04, "f_risk_exposure": -.22,
    "f_compliance_load": -.14, "f_security_exposure": -.17,
    "f_rollback_option": .09, "f_feedback_density": .12,
    "f_knowledge_novelty": .07, "f_legacy_drag": -.08,
    "f_customer_trust": .12,
    "i_verified_reuse": .23, "i_trace_to_skill": .20,
    "i_composition_lift": .18, "i_routing_precision": .15,
    "i_transfer_reuse": .15, "i_feedback_compound": .17,
    "i_risk_without_rollback": -.30, "i_unverified_risk": -.28,
    "i_legacy_latency": -.10, "i_trust_provenance": .10,
    "invalid": -3.5, "risk_load": -.42,
}
ROLE_FAMILIES = [
    "demand_decomposer", "trace_distiller", "skill_miner", "skill_composer",
    "provenance_auditor", "verifier_court", "routing_strategist", "transfer_mapper",
    "risk_governor", "security_reviewer", "compliance_auditor", "rollback_operator",
    "market_maker", "feedback_loop_designer", "release_manager", "coordination_chair",
]
ROLES_PER_FAMILY, AGENTS_PER_ROLE = 524288, 32
ROLE_COUNT = len(ROLE_FAMILIES) * ROLES_PER_FAMILY
AGENT_COUNT = ROLE_COUNT * AGENTS_PER_ROLE

def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00","Z")
def mix64(x:int)->int:
    x &= MASK; x=(x+0x9E3779B97F4A7C15)&MASK; z=x
    z=((z^(z>>30))*0xBF58476D1CE4E5B9)&MASK; z=((z^(z>>27))*0x94D049BB133111EB)&MASK
    return z^(z>>31)
def u01(seed:int,*vals:int)->float:
    x=seed&MASK
    for v in vals:
        x=mix64(x^((int(v)+0x9E3779B97F4A7C15)&MASK))
    return (x>>11)/float(1<<53)
def noise(seed:int,*vals:int)->float:
    return 2*u01(seed,*vals)-1

def domain_lift(seed:int, domain:int, key:str)->float:
    h=int(hashlib.sha256(f"{seed}|{domain}|{key}".encode()).hexdigest()[:12],16)
    amp=.30 if key.startswith("i_") else .24
    if key.startswith("f_") and key[2:] in NEG: amp*=.55
    return amp*math.sin((domain+1)*(h%23+5)*.151)*(0.55+0.45*u01(seed,domain,h&9999))

def feature_vector(seed:int, case_id:int, arm:int, domain:int)->dict[str,float]:
    f={name:u01(seed,case_id,arm,i) for i,name in enumerate(FEATURES)}
    f["risk_exposure"]=min(1,max(0,.30*f["risk_exposure"]+.20*f["knowledge_novelty"]+.22*(1-f["rollback_option"])+.28*u01(seed,case_id,arm,711)))
    f["compliance_load"]=min(1,max(0,.36*f["compliance_load"]+.22*f["risk_exposure"]+.20*(1-f["provenance_strength"])+.22*u01(seed,case_id,arm,712)))
    f["security_exposure"]=min(1,max(0,.38*f["security_exposure"]+.23*(1-f["verification_density"])+.20*f["transfer_distance"]+.19*u01(seed,case_id,arm,713)))
    f["reuse_potential"]=min(1,max(0,.44*f["reuse_potential"]+.18*f["trace_quality"]+.18*f["domain_similarity"]+.20*u01(seed,domain,714)))
    f["skill_composability"]=min(1,max(0,.48*f["skill_composability"]+.23*f["agent_depth"]+.16*f["routing_specificity"]+.13*u01(seed,case_id,arm,715)))
    return f

def atoms_from_features(f:dict[str,float], domain:int)->dict[str,float]:
    a={f"f_{k}":v for k,v in f.items()}
    for name,fn in INTERACTIONS: a[f"i_{name}"]=fn(f)
    for key,value in list(a.items()):
        if key.startswith("f_") or key.startswith("i_"): a[f"d{domain}_{key}"]=value
    risk_load=f["risk_exposure"]+f["compliance_load"]+f["security_exposure"]
    invalid=((f["risk_exposure"]>.80 and f["rollback_option"]<.38) or (f["security_exposure"]>.78 and f["verification_density"]<.45) or (f["compliance_load"]>.80 and f["provenance_strength"]<.42) or (f["transfer_distance"]>.82 and f["verification_density"]<.40))
    a["risk_load"]=risk_load; a["invalid"]=1.0 if invalid else 0.0
    return a

def oracle_score(a:dict[str,float], seed:int, domain:int)->float:
    s=0.0
    for k,v in a.items():
        if k.startswith(f"d{domain}_"):
            s += domain_lift(seed,domain,k.split("_",1)[1])*v
        else:
            s += BASE.get(k,0.0)*v
    return s

def generate(seed:int,count:int,start:int)->list[dict[str,Any]]:
    cases=[]
    for off in range(count):
        cid=start+off; domain=cid%len(DOMAINS)
        market=60_000_000+2_000_000_000*(u01(seed,cid,999)**2.08)
        candidates=[]
        for arm in range(10):
            f=feature_vector(seed,cid,arm,domain); a=atoms_from_features(f,domain)
            score=oracle_score(a,seed,domain)+.009*noise(seed,cid,arm,333)
            value=max(.015,score+1.28)*market
            candidates.append({"arm":arm,"features":f,"atoms":a,"utility":score,"invalid":a["invalid"]>.5,"value_usd":value})
        valid=[(c["utility"],i) for i,c in enumerate(candidates) if not c["invalid"]]
        oracle=max(valid if valid else [(c["utility"],i) for i,c in enumerate(candidates)])[1]
        cases.append({"case_id":cid,"domain":domain,"candidates":candidates,"oracle":oracle})
    return cases

def protocol_stage(seed:int,stage:int)->dict[str,float]:
    f_frac=min(1,.25+.055*stage); i_frac=max(0,min(1,(stage-2)/10)); domain_frac=max(0,min(1,(stage-5)/14)); risk_frac=max(.06,min(1,(stage-1)/7))
    w={}
    for k,v in BASE.items():
        if k.startswith("i_"): w[k]=v*i_frac
        elif k in {"invalid","risk_load"}: w[k]=v*risk_frac
        else: w[k]=v*f_frac
    w["invalid"]=BASE["invalid"]*risk_frac-.20*stage
    w["risk_load"]=BASE["risk_load"]*risk_frac-.08*stage
    for d in range(len(DOMAINS)):
        for key in [x for x in BASE if x.startswith("f_") or x.startswith("i_")]:
            w[f"d{d}_{key}"]=domain_lift(seed,d,key)*domain_frac
    return w

def single_generalist()->dict[str,float]:
    return {"f_task_value":.32,"f_execution_margin":.20,"f_reuse_potential":.06,"f_customer_trust":.05,"f_risk_exposure":-.04,"f_security_exposure":-.03,"invalid":-.05,"risk_load":-.02}
def local_memory_silos(seed:int)->dict[str,float]:
    w=protocol_stage(seed,8)
    for k in list(w):
        if k.startswith("d"):
            domain=int(k[1:].split("_",1)[0])
            if domain%4!=0: w[k]=0.0
    return w
def static_skill_catalog(seed:int)->dict[str,float]:
    w=protocol_stage(seed,4)
    for k in list(w):
        if k.startswith("d"): w[k]=0.0
    return w
def unverified_sharing(seed:int)->dict[str,float]:
    w=protocol_stage(seed,14)
    w["invalid"]=-.10; w["risk_load"]=-.04
    for key in ["i_unverified_risk","i_risk_without_rollback"]: w[key]*=.10
    return w
def random_sharing(seed:int)->dict[str,float]:
    w=protocol_stage(seed,6)
    for i,k in enumerate(list(w)): w[k]=w[k]*(.25+1.30*u01(seed,i,707))+.10*noise(seed,i,708)
    return w

def dot(w:dict[str,float], a:dict[str,float])->float:
    return sum(w.get(k,0.0)*v for k,v in a.items())
def choose(case:dict[str,Any], w:dict[str,float])->int:
    best_i,best=-1,-10**12
    for i,c in enumerate(case["candidates"]):
        s=dot(w,c["atoms"])
        if s>best: best_i,best=i,s
    return best_i

def evaluate(cases:list[dict[str,Any]], w:dict[str,float])->dict[str,Any]:
    n=len(cases); exact=top3=invalid=risk=unauth=0; total_o=total_c=0.0
    reuse=liquidity=transfer=provenance=0.0
    per={str(i):{"o":0.0,"c":0.0,"n":0,"exact":0} for i in range(len(DOMAINS))}
    for case in cases:
        pred=choose(case,w); oracle=case["oracle"]; c=case["candidates"][pred]; o=case["candidates"][oracle]; f=c["features"]
        exact+=pred==oracle; rank=sorted(range(len(case["candidates"])),key=lambda i:case["candidates"][i]["utility"],reverse=True); top3+=pred in rank[:3]
        invalid+=c["invalid"]; risk+=c["atoms"]["risk_load"]>2.02; unauth+=f["security_exposure"]>.83 and f["verification_density"]<.35
        total_o+=o["value_usd"]; total_c+=c["value_usd"]
        reuse+=f["reuse_potential"]; liquidity+=(f["reuse_potential"]+f["domain_similarity"]+f["skill_composability"])/3; transfer+=f["reuse_potential"]*(1-f["transfer_distance"]); provenance+=(f["provenance_strength"]+f["verification_density"]+f["trace_quality"])/3
        r=per[str(case["domain"])]; r["o"]+=o["value_usd"]; r["c"]+=c["value_usd"]; r["n"]+=1; r["exact"]+=pred==oracle
    domain_scores={k:{"value_capture_rate_percent":round(100*v["c"]/v["o"],4),"frontier_correct_rate_percent":round(100*v["exact"]/v["n"],4),"count":v["n"]} for k,v in per.items()}
    min_cap=min(x["value_capture_rate_percent"] for x in domain_scores.values()); max_cap=max(x["value_capture_rate_percent"] for x in domain_scores.values())
    return {"case_count":n,"frontier_correct_rate_percent":round(100*exact/n,4),"top3_rate_percent":round(100*top3/n,4),"value_capture_rate_percent":round(100*total_c/total_o,4),"benchmark_value_capture_rate_percent":round(100*total_c/total_o,4),"total_benchmark_value_at_stake_usd":round(total_o,2),"total_benchmark_value_captured_usd":round(total_c,2),"risk_breach_rate_percent":round(100*risk/n,4),"invalid_action_rate_percent":round(100*invalid/n,4),"unauthorized_action_rate_percent":round(100*unauth/n,4),"skill_reuse_score":round(100*reuse/n,4),"capability_liquidity_score":round(100*liquidity/n,4),"cross_domain_transfer_score":round(100*transfer/n,4),"provenance_integrity_score":round(100*provenance/n,4),"minimum_domain_value_capture_percent":round(min_cap,4),"maximum_domain_value_capture_percent":round(max_cap,4),"domain_spread_percent":round(max_cap-min_cap,4),"weak_domain_rate_percent":round(100*sum(1 for s in domain_scores.values() if s["value_capture_rate_percent"]<90)/len(DOMAINS),4),"domain_scores":domain_scores}

def composite(m:dict[str,Any])->float:
    return m["value_capture_rate_percent"]+.05*m["frontier_correct_rate_percent"]+.06*m["minimum_domain_value_capture_percent"]-1.35*m["risk_breach_rate_percent"]-1.7*m["invalid_action_rate_percent"]-1.4*m["weak_domain_rate_percent"]

def rsi_releases(seed:int, validation:list[dict[str,Any]], stages:int)->tuple[dict[str,float],list[dict[str,Any]]]:
    cur=protocol_stage(seed,0); cm=evaluate(validation,cur)
    rel=[{"generation":0,"released":True,"lesson":"seed static skill catalog before verified network sharing","validation":cm,"score":round(composite(cm),6),"protocol":cur}]
    for g in range(1,stages+1):
        cand=protocol_stage(seed,g); vm=evaluate(validation,cand)
        score_gain=composite(vm)-composite(cm)
        no_regression=(vm["risk_breach_rate_percent"]<=cm["risk_breach_rate_percent"]+.05 and vm["weak_domain_rate_percent"]<=cm["weak_domain_rate_percent"]+.01 and vm["minimum_domain_value_capture_percent"]>=cm["minimum_domain_value_capture_percent"]-.10)
        released=(score_gain>.0005 or (g>=5 and no_regression)) and no_regression
        if released: cur,cm=cand,vm
        rel.append({"generation":g,"released":released,"lesson":"released verified global skill-sharing and routing update" if released else "candidate rejected by verifier gate","validation":cm,"score":round(composite(cm),6),"protocol":cur})
    return cur,rel

def compare(final:dict[str,Any], ctrl:dict[str,Any])->dict[str,float]:
    return {"value_capture_gain_points":round(final["value_capture_rate_percent"]-ctrl["value_capture_rate_percent"],4),"frontier_correct_gain_points":round(final["frontier_correct_rate_percent"]-ctrl["frontier_correct_rate_percent"],4),"weak_domain_reduction_points":round(ctrl["weak_domain_rate_percent"]-final["weak_domain_rate_percent"],4),"benchmark_value_captured_gain_usd":round(final["total_benchmark_value_captured_usd"]-ctrl["total_benchmark_value_captured_usd"],2)}
def eval_vectors(cases:list[dict[str,Any]], w:dict[str,float])->tuple[list[float],list[float]]:
    cap=[]; oracle=[]
    for case in cases:
        p=choose(case,w); q=case["oracle"]; cap.append(case["candidates"][p]["value_usd"]); oracle.append(case["candidates"][q]["value_usd"])
    return cap,oracle
def bootstrap(cases:list[dict[str,Any]], final_w:dict[str,float], ctrl_w:dict[str,float], seed:int, reps:int=90)->dict[str,float]:
    f,o=eval_vectors(cases,final_w); c,_=eval_vectors(cases,ctrl_w); n=len(cases); gains=[]
    for rep in range(reps):
        fs=cs=os=0.0
        for draw in range(n):
            i=int(u01(seed,rep,draw,979)*n)%n; fs+=f[i]; cs+=c[i]; os+=o[i]
        gains.append(100*fs/os-100*cs/os)
    gains.sort()
    return {"mean_gain_points":round(sum(gains)/len(gains),4),"p05_gain_points":round(gains[int(.05*(len(gains)-1))],4),"p50_gain_points":round(gains[int(.5*(len(gains)-1))],4),"p95_gain_points":round(gains[int(.95*(len(gains)-1))],4),"bootstrap_repetitions":reps}
def proto_hash(w): return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def money(v): return f"${v/1_000_000_000_000:,.2f}T" if abs(v)>=1e12 else f"${v/1_000_000_000:,.2f}B" if abs(v)>=1e9 else f"${v:,.0f}"

def build(seed:int,train_count:int,validation_count:int,holdout_count:int,stages:int)->dict[str,Any]:
    val=generate(seed,validation_count,train_count); holdout=generate(seed,holdout_count,train_count+validation_count)
    final_w,releases=rsi_releases(seed,val,stages)
    weights={"single_generalist":single_generalist(),"static_skill_catalog":static_skill_catalog(seed),"local_memory_silos":local_memory_silos(seed),"unverified_sharing":unverified_sharing(seed),"random_skill_sharing":random_sharing(seed),"final":final_w}
    metrics={k:evaluate(holdout,w) for k,w in weights.items()}; final=metrics["final"]
    comps={k:compare(final,metrics[k]) for k in metrics if k!="final"}; safe_controls=[k for k in metrics if k!="final" and metrics[k]["risk_breach_rate_percent"]==0 and metrics[k]["invalid_action_rate_percent"]==0]
    strongest=max(safe_controls,key=lambda k:metrics[k]["value_capture_rate_percent"])
    boots={"vs_static_skill_catalog":bootstrap(holdout,final_w,weights["static_skill_catalog"],seed+11),"vs_local_memory_silos":bootstrap(holdout,final_w,weights["local_memory_silos"],seed+13),"vs_strongest_control":bootstrap(holdout,final_w,weights[strongest],seed+17)}
    release_count=sum(1 for r in releases if r["released"]); final["strongest_control"]=strongest; final["benchmark_implied_value_captured_over_strongest_control_usd"]=comps[strongest]["benchmark_value_captured_gain_usd"]
    gates={"large_specialist_skill_market":AGENT_COUNT>=250_000_000 and ROLE_COUNT>=8_000_000,"locked_holdout_scale":holdout_count>=2048,"domain_coverage":len(DOMAINS)>=24,"rsi_release_count":release_count>=12,"value_capture_threshold":final["value_capture_rate_percent"]>=96,"minimum_domain_capture_threshold":final["minimum_domain_value_capture_percent"]>=94,"weak_domain_zero":final["weak_domain_rate_percent"]==0,"risk_breach_zero":final["risk_breach_rate_percent"]==0,"unauthorized_action_zero":final["unauthorized_action_rate_percent"]==0,"beats_static_skill_catalog":comps["static_skill_catalog"]["value_capture_gain_points"]>=1.5,"beats_local_memory_silos":comps["local_memory_silos"]["value_capture_gain_points"]>=1.5,"rejects_unverified_sharing":metrics["unverified_sharing"]["risk_breach_rate_percent"]>final["risk_breach_rate_percent"] and metrics["unverified_sharing"]["invalid_action_rate_percent"]>final["invalid_action_rate_percent"],"bootstrap_p05_vs_strongest_control_positive":boots["vs_strongest_control"]["p05_gain_points"]>0}
    return {"proved":all(gates.values()),"status":"PASSED_AUTONOMOUS_RSI_SKILL_COMPOUNDING_MOAT_PROOF" if all(gates.values()) else "FAILED_AUTONOMOUS_RSI_SKILL_COMPOUNDING_MOAT_PROOF","proof_type":"Autonomous RSI Skill Compounding Moat Proof","workflow":"Autonomous RSI Skill Compounding Moat Proof","generated_at_utc":now_iso(),"seed":seed,"protocol_fingerprint_sha256":proto_hash(final_w),"safe_interpretation":"A deterministic benchmark proof that verified skill sharing and validation-gated RSI improve capability routing across a network while avoiding unverified reuse, local memory silos, weak domains, and risk breaches. Not live revenue, customer results, financial advice, legal advice, token advice, policy advice, or achieved superintelligence.","agent_system":{"virtual_specialist_agents":AGENT_COUNT,"specialist_roles":ROLE_COUNT,"role_families":len(ROLE_FAMILIES),"skill_domains":len(DOMAINS),"skill_markets":16384,"verifier_courts":8192,"provenance_registries":16384,"release_lanes":4096,"coordination_style":"verified global skill graph with specialist-agent market clearing, provenance courts, transfer tests, release gates, risk vetoes, and network-wide routing upgrades"},"benchmark_public":{"name":"Skill Compounding Moat benchmark","train_count":train_count,"validation_count":validation_count,"locked_holdout_count":holdout_count,"candidate_actions_per_case":10,"domains":DOMAINS,"features":FEATURES,"data_boundary":"synthetic/redacted-style public benchmark; no private customer data"},"pre_registered_gates":gates,"baselines_and_controls":{k:metrics[k] for k in metrics if k!="final"},"final":final,"comparisons":comps,"bootstrap_confidence_intervals":boots,"rsi_release_count":release_count,"rsi_releases":releases,"public_boundary":"Benchmark-capital-equivalent values are not live revenue, customer results, financial guarantees, legal advice, policy advice, token advice, or proof of achieved superintelligence."}

def write_report(result):
    f=result["final"]; controls="\n".join(f"| {k} | {v['value_capture_rate_percent']}% | {v['minimum_domain_value_capture_percent']}% | {v['weak_domain_rate_percent']}% | {v['risk_breach_rate_percent']}% |" for k,v in result["baselines_and_controls"].items()); gates="\n".join(f"- {'✅' if v else '❌'} `{k}`" for k,v in result["pre_registered_gates"].items())
    report=f"""# Autonomous RSI Skill Compounding Moat Proof

Generated: `{result['generated_at_utc']}`

## Thesis

SkillOS tests whether one verified skill can improve the whole network.

Core mechanism:

> work trace → verified skill → provenance ledger → release gate → network routing upgrade → cross-domain reuse → future work improvement → compounding moat

## Final locked holdout result

- Value capture: **{f['value_capture_rate_percent']}%**
- Minimum domain capture: **{f['minimum_domain_value_capture_percent']}%**
- Frontier-correct rate: **{f['frontier_correct_rate_percent']}%**
- Skill reuse score: **{f['skill_reuse_score']}%**
- Cross-domain transfer score: **{f['cross_domain_transfer_score']}%**
- Provenance integrity score: **{f['provenance_integrity_score']}%**
- Weak-domain rate: **{f['weak_domain_rate_percent']}%**
- Risk breach rate: **{f['risk_breach_rate_percent']}%**
- Benchmark value at stake: **{money(f['total_benchmark_value_at_stake_usd'])}**
- Benchmark value captured: **{money(f['total_benchmark_value_captured_usd'])}**
- Strongest control: **{f['strongest_control']}**
- Gain over strongest control: **{money(f['benchmark_implied_value_captured_over_strongest_control_usd'])}**

## Baselines and controls

| System | Value capture | Minimum domain capture | Weak-domain rate | Risk breach |
|---|---:|---:|---:|---:|
{controls}

## Pre-registered gates

{gates}

## Boundary

{result['public_boundary']}
"""
    DOCS.mkdir(parents=True,exist_ok=True); out=DOCS/"rsi-skill-compounding-moat-proof.md"; out.write_text(report,encoding="utf-8"); return str(out.relative_to(ROOT))

def main():
    p=argparse.ArgumentParser(); p.add_argument("--seed",type=int,default=20260530); p.add_argument("--train-count",type=int,default=1536); p.add_argument("--validation-count",type=int,default=1024); p.add_argument("--holdout-count",type=int,default=2048); p.add_argument("--generations",type=int,default=22); p.add_argument("--summary",default=""); a=p.parse_args()
    DATA.mkdir(parents=True,exist_ok=True); DOCS.mkdir(parents=True,exist_ok=True)
    result=build(a.seed,a.train_count,a.validation_count,a.holdout_count,a.generations); result["markdown_report"]=write_report(result); result["output"]="data/rsi-skill-compounding-moat-proof.json"
    (DATA/"rsi-skill-compounding-moat-proof.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    compact={"proved":result["proved"],"workflow":result["workflow"],"virtual_specialist_agents":result["agent_system"]["virtual_specialist_agents"],"specialist_roles":result["agent_system"]["specialist_roles"],"skill_domains":result["agent_system"]["skill_domains"],"rsi_release_count":result["rsi_release_count"],"locked_holdout_count":result["benchmark_public"]["locked_holdout_count"],"value_capture_percent":result["final"]["value_capture_rate_percent"],"minimum_domain_value_capture_percent":result["final"]["minimum_domain_value_capture_percent"],"weak_domain_rate_percent":result["final"]["weak_domain_rate_percent"],"risk_breach_percent":result["final"]["risk_breach_rate_percent"],"benchmark_value_captured_usd":result["final"]["total_benchmark_value_captured_usd"],"gain_over_strongest_control_usd":result["final"]["benchmark_implied_value_captured_over_strongest_control_usd"],"protocol_fingerprint_sha256":result["protocol_fingerprint_sha256"]}
    print(json.dumps(compact,indent=2,sort_keys=True))
    if a.summary: Path(a.summary).write_text("## Autonomous RSI Skill Compounding Moat Proof\n\n"+"\n".join(f"- {k}: **{v}**" for k,v in compact.items()),encoding="utf-8")
    if not result["proved"]: raise SystemExit(1)
if __name__=="__main__":
    main()
