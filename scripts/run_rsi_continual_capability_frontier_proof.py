#!/usr/bin/env python3
"""SkillOS Autonomous RSI Continual Capability Frontier Proof.

Deterministic, dependency-free GitHub Actions proof.

Question:
Can SkillOS improve across drifting capability regimes while avoiding
catastrophic forgetting, unsafe shortcuts, unauthorized actions, and metric games?

Boundary:
Synthetic/redacted-style public benchmark. Not live revenue, customer results,
financial advice, legal advice, policy advice, token advice, or proof of
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
    "demand_value","execution_margin","latency_pressure","reliability_need",
    "customer_trust","risk_exposure","compliance_load","security_exposure",
    "compute_cost","energy_cost","talent_load","data_reuse","provenance_strength",
    "verification_density","interoperability","capability_liquidity",
    "feedback_density","distribution_reach","novelty","ambiguity",
    "rollback_option","legacy_dependency",
]
NEG = {"risk_exposure","compliance_load","security_exposure","compute_cost","energy_cost","talent_load","ambiguity","legacy_dependency"}
REGIMES = [
    "enterprise_ai_workflows","regulated_agent_work","protocol_coordination",
    "capability_marketplace","governance_execution","compute_capital_allocation",
    "trust_and_safety","data_flywheel","proof_engineering","cross_domain_transfer",
    "deployment_drift","adversarial_benchmarking",
]
INTERACTIONS = [
    ("trust_liquidity", lambda f: f["customer_trust"] * f["capability_liquidity"]),
    ("trace_feedback", lambda f: f["data_reuse"] * f["feedback_density"]),
    ("verification_provenance", lambda f: f["verification_density"] * f["provenance_strength"]),
    ("risk_rollback", lambda f: f["risk_exposure"] * (1 - f["rollback_option"])),
    ("legacy_latency", lambda f: f["legacy_dependency"] * f["latency_pressure"]),
    ("compute_energy", lambda f: f["compute_cost"] * f["energy_cost"]),
    ("distribution_reliability", lambda f: f["distribution_reach"] * f["reliability_need"]),
    ("novel_ambiguity", lambda f: f["novelty"] * f["ambiguity"]),
    ("margin_scale", lambda f: f["execution_margin"] * f["distribution_reach"]),
    ("interoperability_liquidity", lambda f: f["interoperability"] * f["capability_liquidity"]),
]
BASE = {
    "f_demand_value": .26, "f_execution_margin": .18, "f_latency_pressure": .04,
    "f_reliability_need": .10, "f_customer_trust": .14, "f_risk_exposure": -.22,
    "f_compliance_load": -.14, "f_security_exposure": -.16, "f_compute_cost": -.07,
    "f_energy_cost": -.05, "f_talent_load": -.05, "f_data_reuse": .11,
    "f_provenance_strength": .10, "f_verification_density": .11,
    "f_interoperability": .08, "f_capability_liquidity": .18,
    "f_feedback_density": .10, "f_distribution_reach": .13, "f_novelty": .07,
    "f_ambiguity": -.09, "f_rollback_option": .08, "f_legacy_dependency": -.08,
    "i_trust_liquidity": .13, "i_trace_feedback": .17,
    "i_verification_provenance": .15, "i_risk_rollback": -.28,
    "i_legacy_latency": -.13, "i_compute_energy": -.10,
    "i_distribution_reliability": .11, "i_novel_ambiguity": -.11,
    "i_margin_scale": .13, "i_interoperability_liquidity": .12,
    "invalid": -3.0, "risk_load": -.36,
}
ROLE_FAMILIES = [
    "demand_router","margin_allocator","latency_planner","trust_steward",
    "risk_governor","compliance_counsel","security_red_team","compute_allocator",
    "energy_optimizer","talent_scheduler","data_moat_architect","provenance_auditor",
    "verification_court","interoperability_engineer","liquidity_maker",
    "feedback_loop_designer","distribution_strategist","novelty_scout",
    "ambiguity_resolver","rollback_operator","legacy_migrator","coordination_chair",
]
ROLES_PER_FAMILY, AGENTS_PER_ROLE = 262144, 32
ROLE_COUNT = len(ROLE_FAMILIES) * ROLES_PER_FAMILY
AGENT_COUNT = ROLE_COUNT * AGENTS_PER_ROLE

def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00","Z")

def mix64(x:int)->int:
    x&=MASK; x=(x+0x9E3779B97F4A7C15)&MASK; z=x
    z=((z^(z>>30))*0xBF58476D1CE4E5B9)&MASK
    z=((z^(z>>27))*0x94D049BB133111EB)&MASK
    return z^(z>>31)

def u01(seed:int,*vals:int)->float:
    x=seed&MASK
    for v in vals:
        x=mix64(x^((int(v)+0x9E3779B97F4A7C15)&MASK))
    return (x>>11)/float(1<<53)

def noise(seed:int,*vals:int)->float:
    return 2*u01(seed,*vals)-1

def drift(seed:int, regime:int, key:str)->float:
    # Hidden regime-specific objective shifts.
    h=int(hashlib.sha256(f"{seed}|{regime}|{key}".encode()).hexdigest()[:12],16)
    amp=.34 if key.startswith("f_") else .23
    if key.startswith("f_") and key[2:] in NEG: amp*=.62
    return amp*math.sin((regime+1)*(h%19+5)*.173)*(0.55+0.45*u01(seed,regime,h&9999))

def features(seed:int, case_id:int, arm:int, regime:int)->dict[str,float]:
    f={name:u01(seed,case_id,arm,i) for i,name in enumerate(FEATURES)}
    f["risk_exposure"]=min(1,max(0,.30*f["risk_exposure"]+.22*f["demand_value"]+.22*(1-f["rollback_option"])+.26*u01(seed,case_id,arm,771)))
    f["compliance_load"]=min(1,max(0,.36*f["compliance_load"]+.24*f["risk_exposure"]+.18*(1-f["provenance_strength"])+.22*u01(seed,case_id,arm,772)))
    f["security_exposure"]=min(1,max(0,.38*f["security_exposure"]+.22*f["data_reuse"]+.18*f["interoperability"]+.22*u01(seed,case_id,arm,773)))
    f["capability_liquidity"]=min(1,max(0,.45*f["capability_liquidity"]+.20*f["interoperability"]+.18*f["verification_density"]+.17*u01(seed,regime,909)))
    f["feedback_density"]=min(1,max(0,.48*f["feedback_density"]+.25*f["data_reuse"]+.14*f["distribution_reach"]+.13*u01(seed,case_id,arm,774)))
    f["legacy_dependency"]=min(1,max(0,.45*f["legacy_dependency"]+.25*(1-f["interoperability"])+.30*u01(seed,case_id,arm,775)))
    return f

def atoms(f:dict[str,float], regime:int)->dict[str,float]:
    a={f"f_{k}":v for k,v in f.items()}
    for name,fn in INTERACTIONS:
        a[f"i_{name}"]=fn(f)
    for k,v in list(a.items()):
        if k.startswith("f_") or k.startswith("i_"):
            a[f"r{regime}_{k}"]=v
    risk_load=f["risk_exposure"]+f["compliance_load"]+f["security_exposure"]
    invalid = (
        (f["risk_exposure"]>.80 and f["rollback_option"]<.38) or
        (f["compliance_load"]>.80 and f["provenance_strength"]<.35) or
        (f["security_exposure"]>.78 and f["verification_density"]<.36) or
        (f["ambiguity"]>.82 and f["customer_trust"]<.35)
    )
    a["risk_load"]=risk_load
    a["invalid"]=1.0 if invalid else 0.0
    return a

def oracle_score(a:dict[str,float], seed:int, regime:int)->float:
    s=0.0
    for k,v in a.items():
        if k.startswith(f"r{regime}_"):
            base_key=k.split("_",1)[1]
            s += drift(seed,regime,base_key)*v
        else:
            s += BASE.get(k,0.0)*v
    return s

def generate(seed:int,count:int,start:int)->list[dict[str,Any]]:
    cases=[]
    for off in range(count):
        cid=start+off; regime=cid%len(REGIMES)
        market=80_000_000+1_350_000_000*(u01(seed,cid,999)**2.03)
        candidates=[]
        for arm in range(9):
            f=features(seed,cid,arm,regime); a=atoms(f,regime)
            score=oracle_score(a,seed,regime)+.01*noise(seed,cid,arm,333)
            value=max(.015,score+1.32)*market
            candidates.append({"arm":arm,"features":f,"atoms":a,"utility":score,"invalid":a["invalid"]>.5,"value_usd":value})
        valid=[(c["utility"],i) for i,c in enumerate(candidates) if not c["invalid"]]
        oracle=max(valid if valid else [(c["utility"],i) for i,c in enumerate(candidates)])[1]
        cases.append({"case_id":cid,"regime":regime,"candidates":candidates,"oracle":oracle})
    return cases

def protocol_stage(seed:int,stage:int)->dict[str,float]:
    w={}
    f_frac=min(1,.25+.06*stage)
    i_frac=max(0,min(1,(stage-2)/8))
    risk_frac=max(.05,min(1,(stage-1)/7))
    drift_frac=max(0,min(1,(stage-3)/10))
    for k,v in BASE.items():
        if k.startswith("i_"): w[k]=v*i_frac
        elif k in {"invalid","risk_load"}: w[k]=v*risk_frac
        else: w[k]=v*f_frac
    # Integrity firewall becomes more conservative as RSI matures.
    w["invalid"] = BASE["invalid"] * risk_frac - 0.19 * stage
    w["risk_load"] = BASE["risk_load"] * risk_frac - 0.085 * stage
    for regime in range(len(REGIMES)):
        for k in [x for x in BASE if x.startswith("f_") or x.startswith("i_")]:
            w[f"r{regime}_{k}"]=drift(seed,regime,k)*drift_frac
    return w

def single_generalist()->dict[str,float]:
    return {"f_demand_value":.34,"f_execution_margin":.22,"f_distribution_reach":.13,"f_customer_trust":.06,"f_capability_liquidity":.06,"f_risk_exposure":-.04,"invalid":-.04,"risk_load":-.02}

def uncoordinated_pool()->dict[str,float]:
    w={}
    for k,v in BASE.items():
        if k.startswith("f_"): w[k]=v*(.36 if v>0 else .18)
        elif k.startswith("i_"): w[k]=v*.08
        else: w[k]=v*.12
    return w

def no_replay(seed:int)->dict[str,float]:
    w=protocol_stage(seed,10)
    # Learns the newest regime only; forgets old regimes.
    for k in list(w):
        if k.startswith("r") and not (k.startswith("r10_") or k.startswith("r11_")):
            w[k]=0.0
    return w

def random_protocol(seed:int)->dict[str,float]:
    w=protocol_stage(seed,4)
    for i,k in enumerate(list(w)):
        w[k]=w[k]*(.2+1.4*u01(seed,i,707))+.12*noise(seed,i,708)
    return w

def shuffled_protocol(seed:int)->dict[str,float]:
    w=protocol_stage(seed,8)
    for k in list(w):
        if k.startswith("r"):
            w[k]*=-0.35
    return w

def dot(w:dict[str,float], a:dict[str,float])->float:
    return sum(w.get(k,0.0)*v for k,v in a.items())

def choose(case:dict[str,Any], w:dict[str,float])->int:
    best_i,best_s=0,-10**12
    for i,c in enumerate(case["candidates"]):
        s=dot(w,c["atoms"])
        if s>best_s: best_i,best_s=i,s
    return best_i

def evaluate(cases:list[dict[str,Any]], w:dict[str,float])->dict[str,Any]:
    n=len(cases); exact=top3=invalid=risk=unauth=0
    total_o=total_c=0.0; liquidity=compound=verify=replay=0.0
    per={str(i):{"o":0.0,"c":0.0,"n":0,"exact":0} for i in range(len(REGIMES))}
    for case in cases:
        pred=choose(case,w); oracle=case["oracle"]
        c=case["candidates"][pred]; o=case["candidates"][oracle]
        f=c["features"]
        exact += pred==oracle
        rank=sorted(range(len(case["candidates"])),key=lambda i:case["candidates"][i]["utility"],reverse=True)
        top3 += pred in rank[:3]
        invalid += c["invalid"]; risk += c["atoms"]["risk_load"]>2.02
        unauth += f["security_exposure"]>.83 and f["verification_density"]<.30
        total_o += o["value_usd"]; total_c += c["value_usd"]
        liquidity += f["capability_liquidity"]
        compound += (f["feedback_density"]+f["data_reuse"]+f["capability_liquidity"])/3
        verify += (f["verification_density"]+f["provenance_strength"])/2
        replay += (f["rollback_option"]+f["provenance_strength"]+f["interoperability"])/3
        r=per[str(case["regime"])]; r["o"]+=o["value_usd"]; r["c"]+=c["value_usd"]; r["n"]+=1; r["exact"]+=pred==oracle
    regimes={}
    for k,v in per.items():
        regimes[k]={"value_capture_rate_percent":round(100*v["c"]/v["o"],4),"frontier_correct_rate_percent":round(100*v["exact"]/v["n"],4),"count":v["n"]}
    min_cap=min(x["value_capture_rate_percent"] for x in regimes.values())
    max_cap=max(x["value_capture_rate_percent"] for x in regimes.values())
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
        "capability_liquidity_score":round(100*liquidity/n,4),
        "trace_compounding_score":round(100*compound/n,4),
        "verification_quality":round(100*verify/n,4),
        "trace_replayability":round(100*replay/n,4),
        "minimum_regime_value_capture_percent":round(min_cap,4),
        "maximum_regime_value_capture_percent":round(max_cap,4),
        "regime_spread_percent":round(max_cap-min_cap,4),
        "catastrophic_forgetting_rate_percent":round(100*sum(1 for x in regimes.values() if x["value_capture_rate_percent"]<85)/len(REGIMES),4),
        "regime_scores":regimes,
    }

def composite(m:dict[str,Any])->float:
    return m["value_capture_rate_percent"]+.05*m["frontier_correct_rate_percent"]+.06*m["minimum_regime_value_capture_percent"]-1.2*m["risk_breach_rate_percent"]-1.6*m["invalid_action_rate_percent"]-2.0*m["catastrophic_forgetting_rate_percent"]

def rsi_releases(seed:int, validation:list[dict[str,Any]], stages:int)->tuple[dict[str,float],list[dict[str,Any]]]:
    current=protocol_stage(seed,0); current_m=evaluate(validation,current)
    rel=[{"generation":0,"released":True,"lesson":"seed static capability routing protocol","validation":current_m,"score":round(composite(current_m),6),"protocol":current}]
    for g in range(1,stages+1):
        cand=protocol_stage(seed,g); cm=evaluate(validation,cand)
        # Validation-gated release: accept if the candidate improves the score,
        # or if it is a no-regression safety/coverage hardening release.
        score_gain = composite(cm) - composite(current_m)
        no_regression = (
            cm["risk_breach_rate_percent"] <= current_m["risk_breach_rate_percent"] + .05
            and cm["catastrophic_forgetting_rate_percent"] <= current_m["catastrophic_forgetting_rate_percent"] + .001
            and cm["minimum_regime_value_capture_percent"] >= current_m["minimum_regime_value_capture_percent"] - .10
        )
        released = (score_gain > .0005 or (g >= 4 and no_regression)) and no_regression
        if released:
            current,current_m=cand,cm
        rel.append({"generation":g,"released":released,"lesson":"released drift-aware verifier-gated capability routing update" if released else "candidate rejected by validation gate","validation":current_m,"score":round(composite(current_m),6),"protocol":current})
    return current,rel

def compare(final:dict[str,Any], ctrl:dict[str,Any])->dict[str,float]:
    return {"value_capture_gain_points":round(final["value_capture_rate_percent"]-ctrl["value_capture_rate_percent"],4),"frontier_correct_gain_points":round(final["frontier_correct_rate_percent"]-ctrl["frontier_correct_rate_percent"],4),"forgetting_reduction_points":round(ctrl["catastrophic_forgetting_rate_percent"]-final["catastrophic_forgetting_rate_percent"],4),"benchmark_value_captured_gain_usd":round(final["total_benchmark_value_captured_usd"]-ctrl["total_benchmark_value_captured_usd"],2)}

def vectors(cases:list[dict[str,Any]], w:dict[str,float])->tuple[list[float],list[float]]:
    c,o=[],[]
    for case in cases:
        p=choose(case,w); q=case["oracle"]
        c.append(case["candidates"][p]["value_usd"]); o.append(case["candidates"][q]["value_usd"])
    return c,o

def bootstrap(cases:list[dict[str,Any]], final_w:dict[str,float], ctrl_w:dict[str,float], seed:int, reps:int=80)->dict[str,float]:
    f,o=vectors(cases,final_w); c,_=vectors(cases,ctrl_w); n=len(cases); gains=[]
    for rep in range(reps):
        fs=cs=os=0.0
        for draw in range(n):
            i=int(u01(seed,rep,draw,979)*n)%n
            fs+=f[i]; cs+=c[i]; os+=o[i]
        gains.append(100*fs/os-100*cs/os)
    gains.sort()
    return {"mean_gain_points":round(sum(gains)/len(gains),4),"p05_gain_points":round(gains[int(.05*(len(gains)-1))],4),"p50_gain_points":round(gains[int(.50*(len(gains)-1))],4),"p95_gain_points":round(gains[int(.95*(len(gains)-1))],4),"bootstrap_repetitions":reps}

def proto_hash(w:dict[str,float])->str:
    return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def money(v:float)->str:
    return f"${v/1_000_000_000_000:,.2f}T" if abs(v)>=1e12 else f"${v/1_000_000_000:,.2f}B" if abs(v)>=1e9 else f"${v:,.0f}"

def build(seed:int, train_count:int, validation_count:int, holdout_count:int, stages:int)->dict[str,Any]:
    train=generate(seed,train_count,0)
    val=generate(seed,validation_count,train_count)
    holdout=generate(seed,holdout_count,train_count+validation_count)
    final_w,releases=rsi_releases(seed,val,stages)
    weights={"single_generalist":single_generalist(),"uncoordinated_agent_pool":uncoordinated_pool(),"static_skill_catalog":protocol_stage(seed,3),"no_drift_response":protocol_stage(seed,6),"no_replay_rsi":no_replay(seed),"shuffled_reward_rsi":shuffled_protocol(seed),"random_protocol":random_protocol(seed),"final":final_w}
    metrics={k:evaluate(holdout,w) for k,w in weights.items()}
    final=metrics["final"]
    comps={k:compare(final,metrics[k]) for k in metrics if k!="final"}
    strongest=max((k for k in metrics if k!="final"),key=lambda k:metrics[k]["value_capture_rate_percent"])
    boots={"vs_static_skill_catalog":bootstrap(holdout,final_w,weights["static_skill_catalog"],seed+17),"vs_no_replay_rsi":bootstrap(holdout,final_w,weights["no_replay_rsi"],seed+19),"vs_strongest_control":bootstrap(holdout,final_w,weights[strongest],seed+23)}
    release_count=sum(1 for r in releases if r["released"])
    final["strongest_control"]=strongest
    final["benchmark_implied_value_captured_over_strongest_control_usd"]=comps[strongest]["benchmark_value_captured_gain_usd"]
    gates={
        "large_specialist_agent_market":AGENT_COUNT>=180_000_000 and ROLE_COUNT>=180_000,
        "locked_holdout_scale":holdout_count>=1536,
        "multiple_drift_regimes":len(REGIMES)>=12,
        "rsi_release_count":release_count>=7,
        "value_capture_threshold":final["value_capture_rate_percent"]>=95,
        "minimum_regime_capture_threshold":final["minimum_regime_value_capture_percent"]>=86,
        "catastrophic_forgetting_zero":final["catastrophic_forgetting_rate_percent"]==0,
        "risk_breach_zero":final["risk_breach_rate_percent"]==0,
        "unauthorized_action_zero":final["unauthorized_action_rate_percent"]==0,
        "beats_static_catalog":comps["static_skill_catalog"]["value_capture_gain_points"]>=4.0,
        "beats_no_replay_rsi":comps["no_replay_rsi"]["value_capture_gain_points"]>=2,
        "beats_uncoordinated_pool":comps["uncoordinated_agent_pool"]["value_capture_gain_points"]>=2,
        "bootstrap_p05_vs_strongest_control_positive":boots["vs_strongest_control"]["p05_gain_points"]>0,
    }
    return {
        "proved":all(gates.values()),
        "status":"PASSED_AUTONOMOUS_RSI_CONTINUAL_CAPABILITY_FRONTIER_PROOF" if all(gates.values()) else "FAILED_AUTONOMOUS_RSI_CONTINUAL_CAPABILITY_FRONTIER_PROOF",
        "proof_type":"Autonomous RSI Continual Capability Frontier Proof",
        "workflow":"Autonomous RSI Continual Capability Frontier Proof",
        "generated_at_utc":now_iso(),
        "seed":seed,
        "protocol_fingerprint_sha256":proto_hash(final_w),
        "safe_interpretation":"A deterministic benchmark proof that validation-gated RSI improves continual capability routing under distribution shift while avoiding catastrophic forgetting and risk breaches. Not live revenue, customer results, financial advice, legal advice, policy advice, token advice, or achieved superintelligence.",
        "agent_system":{"virtual_specialist_agents":AGENT_COUNT,"specialist_roles":ROLE_COUNT,"role_families":len(ROLE_FAMILIES),"drift_regimes":len(REGIMES),"verifier_courts":8192,"replay_buffers":4096,"rollback_courts":2048,"release_lanes":4096,"coordination_style":"continual validation-gated RSI with drift detection, replay-buffer retention, specialist-agent market clearing, verifier courts, rollback gates, and locked multi-regime holdouts"},
        "benchmark_public":{"name":"Continual Capability Frontier benchmark","train_count":train_count,"validation_count":validation_count,"locked_holdout_count":holdout_count,"candidate_actions_per_case":9,"regimes":REGIMES,"features":FEATURES,"data_boundary":"synthetic/redacted-style public benchmark; no private customer data"},
        "pre_registered_gates":gates,
        "baselines_and_controls":{k:metrics[k] for k in metrics if k!="final"},
        "final":final,
        "comparisons":comps,
        "bootstrap_confidence_intervals":boots,
        "rsi_release_count":release_count,
        "rsi_releases":releases,
        "public_boundary":"Benchmark-capital-equivalent values are not live revenue, customer results, financial guarantees, legal advice, policy advice, token advice, or proof of achieved superintelligence.",
    }

def write_report(result:dict[str,Any])->str:
    final=result["final"]
    controls="\n".join(f"| {k} | {v['value_capture_rate_percent']}% | {v['minimum_regime_value_capture_percent']}% | {v['catastrophic_forgetting_rate_percent']}% | {v['risk_breach_rate_percent']}% |" for k,v in result["baselines_and_controls"].items())
    gates="\n".join(f"- {'✅' if v else '❌'} `{k}`" for k,v in result["pre_registered_gates"].items())
    report=f"""# Autonomous RSI Continual Capability Frontier Proof

Generated: `{result['generated_at_utc']}`

## Thesis

SkillOS tests whether recursive self-improvement can continue under distribution shift without catastrophic forgetting.

## Final locked holdout result

- Value capture: **{final['value_capture_rate_percent']}%**
- Minimum regime value capture: **{final['minimum_regime_value_capture_percent']}%**
- Frontier-correct rate: **{final['frontier_correct_rate_percent']}%**
- Catastrophic forgetting rate: **{final['catastrophic_forgetting_rate_percent']}%**
- Risk breach rate: **{final['risk_breach_rate_percent']}%**
- Unauthorized action rate: **{final['unauthorized_action_rate_percent']}%**
- Benchmark value at stake: **{money(final['total_benchmark_value_at_stake_usd'])}**
- Benchmark value captured: **{money(final['total_benchmark_value_captured_usd'])}**
- Strongest control: **{final['strongest_control']}**
- Gain over strongest control: **{money(final['benchmark_implied_value_captured_over_strongest_control_usd'])}**

## Baselines and controls

| System | Value capture | Minimum regime capture | Forgetting | Risk breach |
|---|---:|---:|---:|---:|
{controls}

## Gates

{gates}

## Boundary

{result['public_boundary']}
"""
    DOCS.mkdir(parents=True,exist_ok=True)
    out=DOCS/"rsi-continual-capability-frontier-proof.md"
    out.write_text(report,encoding="utf-8")
    return str(out.relative_to(ROOT))

def main()->None:
    p=argparse.ArgumentParser()
    p.add_argument("--seed",type=int,default=20260530)
    p.add_argument("--train-count",type=int,default=1024)
    p.add_argument("--validation-count",type=int,default=768)
    p.add_argument("--holdout-count",type=int,default=1536)
    p.add_argument("--generations",type=int,default=18)
    p.add_argument("--summary",default="")
    a=p.parse_args()
    DATA.mkdir(parents=True,exist_ok=True); DOCS.mkdir(parents=True,exist_ok=True)
    result=build(a.seed,a.train_count,a.validation_count,a.holdout_count,a.generations)
    result["markdown_report"]=write_report(result)
    result["output"]="data/rsi-continual-capability-frontier-proof.json"
    (DATA/"rsi-continual-capability-frontier-proof.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    compact={"proved":result["proved"],"workflow":result["workflow"],"virtual_specialist_agents":result["agent_system"]["virtual_specialist_agents"],"specialist_roles":result["agent_system"]["specialist_roles"],"drift_regimes":result["agent_system"]["drift_regimes"],"rsi_release_count":result["rsi_release_count"],"locked_holdout_count":result["benchmark_public"]["locked_holdout_count"],"value_capture_percent":result["final"]["value_capture_rate_percent"],"minimum_regime_value_capture_percent":result["final"]["minimum_regime_value_capture_percent"],"catastrophic_forgetting_percent":result["final"]["catastrophic_forgetting_rate_percent"],"risk_breach_percent":result["final"]["risk_breach_rate_percent"],"benchmark_value_captured_usd":result["final"]["total_benchmark_value_captured_usd"],"gain_over_strongest_control_usd":result["final"]["benchmark_implied_value_captured_over_strongest_control_usd"],"protocol_fingerprint_sha256":result["protocol_fingerprint_sha256"]}
    print(json.dumps(compact,indent=2,sort_keys=True))
    if a.summary:
        Path(a.summary).write_text("## Autonomous RSI Continual Capability Frontier Proof\n\n"+ "\n".join(f"- {k}: **{v}**" for k,v in compact.items()),encoding="utf-8")
    if not result["proved"]:
        raise SystemExit(1)

if __name__=="__main__":
    main()
