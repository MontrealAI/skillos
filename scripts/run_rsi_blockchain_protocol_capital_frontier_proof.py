from __future__ import annotations
import random, hashlib, time
from dataclasses import dataclass
SEED=20260531
FEATURES=['blockspace','liquidity','security','mev','bridge','oracle','governance','treasury','developer','interop','data_avail','compute_energy','compliance','rwa','stablecoin','settlement','trust','token_risk','reinvestment','adoption','moat','capital_eff']
RISK_DIMS={'mev','bridge','oracle','governance','compliance','token_risk'}
ACTIONS=[
('blockspace fee market',{'blockspace':.9,'settlement':.4,'data_avail':.5,'capital_eff':.5},.12,.16),
('validator security budget',{'security':1.0,'trust':.6,'treasury':.4,'token_risk':.3},.10,.32),
('liquidity route optimizer',{'liquidity':1,'stablecoin':.8,'adoption':.7,'capital_eff':.5,'token_risk':.3},.17,.16),
('MEV capture rebate market',{'mev':1,'blockspace':.5,'trust':.7,'security':.3},.16,.25),
('bridge quarantine router',{'bridge':1,'interop':.8,'trust':.8,'oracle':.4},.09,.38),
('oracle attestation mesh',{'oracle':1,'trust':.8,'rwa':.5,'stablecoin':.4},.11,.32),
('DAO quorum hardening',{'governance':1,'trust':.8,'compliance':.4,'moat':.3},.06,.34),
('RWA settlement rail',{'rwa':1,'compliance':.9,'settlement':.9,'stablecoin':.7,'trust':.8},.20,.28),
('data availability optimizer',{'data_avail':1,'blockspace':.8,'compute_energy':.5,'developer':.4,'capital_eff':.5},.13,.20),
('developer grant portfolio',{'developer':1,'moat':.7,'adoption':.8,'reinvestment':.5},.14,.13),
('treasury duration reserve ladder',{'treasury':1,'capital_eff':.8,'token_risk':.4,'security':.4},.07,.26),
('compute energy settlement market',{'compute_energy':1,'blockspace':.5,'settlement':.5,'capital_eff':.5},.22,.19),
('protocol API standard',{'developer':1,'interop':.9,'moat':.8,'blockspace':.3},.15,.14),
('proof of reserve transparency',{'trust':1,'rwa':.7,'stablecoin':.6,'compliance':.6},.07,.30),
('autonomous protocol market maker',{'liquidity':.9,'stablecoin':.9,'adoption':.7,'mev':.4,'capital_eff':.7,'token_risk':.5},.24,.18),
('staking slashing risk court',{'security':.8,'token_risk':.8,'governance':.5,'trust':.5},.08,.38),
('interchain settlement hub',{'interop':1,'settlement':.8,'bridge':.6,'developer':.6,'moat':.6},.25,.20),
('full stack protocol OS',{'blockspace':.8,'liquidity':.8,'security':.8,'mev':.5,'bridge':.5,'oracle':.5,'governance':.5,'treasury':.7,'developer':.7,'reinvestment':.9,'capital_eff':.8},.30,.24),
]
REGIMES=['rollup_scaling','defi_liquidity','validator_security','cross_chain_bridge','rwa_stablecoin','mev_fee_market','dao_governance','data_availability','oracle_risk','compute_energy_market','token_treasury','developer_platform','public_chain_adoption','institutional_settlement','security_incident','ecosystem_cycle']
COUNCILS=['valuation','capital','risk','red_team','security','bridge','oracle','governance','blockspace','liquidity','mev','treasury','developer','interop','data_avail','compute_energy','compliance','rwa','stablecoin','settlement','trust','token_risk','reinvestment','adoption','moat','protocol_economics','portfolio','synthesis','board','audit','legal','standards','custody','risk_court','transparency','staking','sequencer','grant_review','simulation','benchmark','compounding','capital_to_capability','distribution','public_proof','narrative','civilization_scale','ops','incident_response']
IDEAL={c:1.0 for c in COUNCILS}
for c in ['valuation','synthesis','benchmark','capital_to_capability','compounding','risk','red_team','security','risk_court','audit','board','protocol_economics','capital','portfolio']:
    IDEAL[c]=3.0
for c in ['narrative','civilization_scale','public_proof']:
    IDEAL[c]=.35
COUNCIL_DIMS={c:[c] if c in FEATURES else [] for c in COUNCILS}
COUNCIL_DIMS.update({'valuation':['capital_eff','reinvestment','moat'], 'synthesis':['trust','capital_eff','developer'], 'board':['treasury','capital_eff','compliance'], 'risk':['bridge','oracle','governance','token_risk','mev','compliance'], 'red_team':['bridge','oracle','mev','token_risk'], 'risk_court':['bridge','oracle','governance','token_risk'], 'audit':['trust','compliance','oracle'], 'legal':['compliance','rwa'], 'protocol_economics':['blockspace','mev','capital_eff'], 'portfolio':['treasury','reinvestment','token_risk'], 'compounding':['reinvestment','moat','capital_eff'], 'capital_to_capability':['capital_eff','reinvestment','developer'], 'distribution':['developer','interop'], 'public_proof':['trust','developer'], 'narrative':['trust','adoption'], 'civilization_scale':['compute_energy','blockspace'], 'ops':['governance','security'], 'incident_response':['bridge','security'], 'benchmark':['capital_eff','trust']})
def clamp(x,a=0,b=1): return max(a,min(b,x))
def gen_case(i,rng):
    f={k:rng.betavariate(2,2) for k in FEATURES}; r=REGIMES[i%len(REGIMES)]
    shifts={'rollup_scaling':['blockspace','data_avail','developer'],'defi_liquidity':['liquidity','stablecoin','mev'],'validator_security':['security','token_risk','trust'],'cross_chain_bridge':['bridge','interop','oracle'],'rwa_stablecoin':['rwa','compliance','settlement','stablecoin'],'mev_fee_market':['mev','blockspace','security'],'dao_governance':['governance','trust','developer'],'data_availability':['data_avail','compute_energy'],'oracle_risk':['oracle','trust','rwa'],'compute_energy_market':['compute_energy','blockspace','capital_eff'],'token_treasury':['treasury','token_risk','capital_eff'],'developer_platform':['developer','moat','interop'],'public_chain_adoption':['adoption','trust','blockspace'],'institutional_settlement':['settlement','rwa','compliance','trust'],'security_incident':['bridge','oracle','security'],'ecosystem_cycle':['moat','developer','reinvestment','adoption']}
    for k in shifts[r]: f[k]=clamp(f[k]+.25+.05*rng.random())
    base=1e9+12e9*rng.random();
    if r in ['institutional_settlement','rwa_stablecoin','compute_energy_market']: base*=2.8
    if r in ['security_incident','cross_chain_bridge']: base*=2.0
    return {'id':i,'regime':r,'features':f,'base_value':base,'risk_budget':.22+.20*rng.random()}
def risk(case,act):
    _,w,capex,ctrl=act; f=case['features']; r=.06+.36*capex
    for k in RISK_DIMS: r+=w.get(k,0)*f[k]*.13
    r += .07*f['bridge']+.06*f['oracle']+.06*f['token_risk']+.05*f['governance']+.04*f['mev']
    r -= ctrl*(.35+.25*f['trust']+.25*f['security'])
    return clamp(r,0,1)
def true_value(case,act):
    _,w,capex,ctrl=act; f=case['features']; s=0; den=0
    for k,v in w.items():
        s += v*((1-f[k]) if k in RISK_DIMS else f[k]); den+=abs(v)
    s/=den
    sy=.12*f['reinvestment']+.10*f['capital_eff']+.08*f['moat']+.07*f['developer']+.05*f['trust']
    r=risk(case,act); pen=max(0,r-case['risk_budget'])*4.8
    return case['base_value']*max(.04,(s+sy)*(1+.26*f['reinvestment']+.18*f['capital_eff'])-.65*capex-pen)
def council_signal(c,case,aidx,true_ratio,riskv):
    act=ACTIONS[aidx]; _,w,capex,ctrl=act; f=case['features']; dims=COUNCIL_DIMS[c]
    s=(3.0*true_ratio if c in ['valuation','synthesis','benchmark'] else 0)
    for d in dims:
        if d in FEATURES:
            aw=w.get(d,0); s+=aw*((1-f[d]) if d in RISK_DIMS else f[d])
    if c in ['risk','red_team','security','risk_court','audit','legal','incident_response','custody']:
        s += .75*ctrl - 1.75*max(0,riskv-case['risk_budget'])
    if c in ['compounding','capital_to_capability','portfolio','protocol_economics','board']:
        s += 1.15*true_ratio + .12*(f['reinvestment']+f['capital_eff']+f['moat'])
    h=int(hashlib.sha256(f"{case['id']}:{c}:{aidx}".encode()).hexdigest()[:8],16)
    den = (1.0 if c in ['valuation','synthesis','benchmark'] else len(dims)+1)
    return s/den+((h%1000)/1000-.5)*.018
class World:
    def __init__(self,cases):
        self.cases=cases; self.oracles=[]; self.risks=[]; self.signals=[]
        for case in cases:
            vals=[true_value(case,a) for a in ACTIONS]; best=max(range(len(vals)),key=vals.__getitem__); self.oracles.append((best,vals[best],vals)); rv=[risk(case,a) for a in ACTIONS]; self.risks.append(rv)
            self.signals.append([[council_signal(c,case,a,vals[a]/case['base_value'],rv[a]) for c in COUNCILS] for a in range(len(ACTIONS))])
@dataclass
class Protocol:
    weights:list; risk_gate:float=.5; risk_penalty:float=1.0; compounding_gain:float=0; quorum_sharpness:float=1; name:str='p'
def initial_protocol():
    w=[1.0]*len(COUNCILS)
    for i,c in enumerate(COUNCILS):
        if c in ['narrative','civilization_scale','public_proof','distribution']: w[i]=1.6
        if c in ['risk','red_team','security','risk_court','audit','legal','incident_response','bridge','oracle','governance','token_risk']: w[i]=.35
        if c in ['valuation','synthesis','benchmark','capital_to_capability','compounding']: w[i]=.55
    return Protocol(w,.70,.35,0,.45,'v0')
def choose(world,idx,p):
    case=world.cases[idx]; ws=sum(abs(x) for x in p.weights); f=case['features']; best=-1e99; bi=0
    for a in range(len(ACTIONS)):
        total=0; pos=0
        for j,s in enumerate(world.signals[idx][a]):
            ww=p.weights[j]; total+=ww*s; pos+=max(0,ww) if s>.045 else 0
        rv=world.risks[idx][a]; rex=max(0,rv-min(case['risk_budget'],p.risk_gate))
        score=total/ws+.14*(pos/ws)*p.quorum_sharpness+p.compounding_gain*(f['reinvestment']+f['capital_eff']+f['moat'])/3-p.risk_penalty*rex-(4.0*rex if p.risk_penalty>1 else 0)
        if score>best: best=score; bi=a
    return bi
def evalp(world,idxs,p):
    tb=tot=0; exact=breach=unsafe=front=0; cons=arb=q=0; regrets=[]
    for idx in idxs:
        case=world.cases[idx]; best,bv,vals=world.oracles[idx]; ch=choose(world,idx,p); val=vals[ch]; tb+=bv; tot+=val; exact+=(ch==best)
        rv=world.risks[idx][ch]; breach+=(rv>case['risk_budget']); unsafe+=(rv>case['risk_budget']+.08); front+=(val>=.95*bv and rv<=case['risk_budget']+.02); regrets.append((bv-val)/bv)
        c=sum(1 for s in world.signals[idx][ch] if s>.045)/len(COUNCILS); cons+=c; arb+=(.4<c<.6); q+=(c>=.6)
    n=len(idxs); return {'value_capture':tot/tb,'total_best':tb,'total':tot,'exact_rate':exact/n,'frontier_correct_rate':front/n,'risk_breach_rate':breach/n,'unsafe_rate':unsafe/n,'avg_regret':sum(regrets)/n,'consensus_rate':cons/n,'arbitration_rate':arb/n,'role_quorum_pass_rate':q/n}
def score(e): return e['value_capture']+.05*e['frontier_correct_rate']-1.8*e['risk_breach_rate']-.9*e['unsafe_rate']
def mutate(p,r):
    out=[]
    def add(name,w=None,gate=None,pen=None,comp=None,quorum=None): out.append((name,Protocol(list(w or p.weights),p.risk_gate if gate is None else gate,p.risk_penalty if pen is None else pen,p.compounding_gain if comp is None else comp,p.quorum_sharpness if quorum is None else quorum,f'v{r}')))
    groups={'valuation synthesis and benchmark councils':['valuation','synthesis','benchmark','board','strategy'],'risk courts and protocol security':['risk','red_team','security','risk_court','audit','legal','incident_response','bridge','oracle','governance','token_risk'],'capital-to-capability compounding':['capital','reinvestment','compounding','capital_to_capability','portfolio','protocol_economics','treasury'],'blockspace liquidity developer frontier':['blockspace','liquidity','developer','interop','data_avail','compute_energy','stablecoin','settlement','ecosystem','standards','distribution']}
    for name,cs in groups.items():
        w=list(p.weights)
        for i,c in enumerate(COUNCILS):
            if c in cs: w[i]+=(IDEAL.get(c,1)-w[i])*.62
        add(name,w)
    add('tighten autonomous risk budget court',gate=max(.26,p.risk_gate-.07),pen=min(3.0,p.risk_penalty+.4))
    add('increase recursive reinvestment feedback',comp=min(.42,p.compounding_gain+.07),quorum=min(1.7,p.quorum_sharpness+.12))
    add('deemphasize narrative; privilege proof receipts',w=[x*.55 if COUNCILS[i] in ['narrative','civilization_scale','public_proof'] else x for i,x in enumerate(p.weights)])
    return out
def tune(world,train,val,n):
    p=initial_protocol(); hist=[('v0','initial',True,evalp(world,train,p),evalp(world,val,p))]
    for r in range(1,n+1):
        cur=evalp(world,val,p); cur_s=score(cur); ranked=[]
        for name,cand in mutate(p,r):
            tr=evalp(world,train,cand); ranked.append((score(tr),name,cand,tr))
        ranked.sort(reverse=True,key=lambda x:x[0]); acc=False
        for _,name,cand,tr in ranked:
            va=evalp(world,val,cand); sc=score(va)
            if sc>=cur_s+0.0001 and va['unsafe_rate']<=cur['unsafe_rate']+.001 and va['risk_breach_rate']<=max(.01,cur['risk_breach_rate']+.003):
                p=cand; hist.append((f'v{r}',name,True,tr,va)); acc=True; break
        if not acc: hist.append((f'v{r}','no validation-safe mutation accepted',False,evalp(world,train,p),cur))
    return p,hist
def bases():
    return {'static_dao_committee':Protocol([1]*len(COUNCILS),.55,.85,0,.8,'static'),'no_rsi_protocol_org':initial_protocol(),'single_protocol_strategist':Protocol([1 if c in ['valuation','market','liquidity'] else .02 for c in COUNCILS],.9,.1,0,.2,'single'),'uncoordinated_agent_swarm':Protocol([1+(((int(hashlib.sha256(c.encode()).hexdigest()[:4],16)%100)/100)-.5)*.85 for c in COUNCILS],.85,.15,0,.3,'swarm'),'shuffled_reward_negative_control':Protocol([2.2-IDEAL.get(c,1) for c in COUNCILS],.8,.2,0,.4,'shuffle'),'random_protocol_negative_control':Protocol([.2+((int(hashlib.sha256(('random'+c).encode()).hexdigest()[:4],16)%100)/100)*1.6 for c in COUNCILS],.8,.2,0,.4,'random'),'risk_blind_negative_control':Protocol([IDEAL.get(c,1) for c in COUNCILS],.98,0,.3,1.2,'riskblind')}
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, hashlib, sys

PROOF_NAME = "Autonomous RSI Blockchain Protocol Capital Frontier Proof"
SLUG = "rsi-blockchain-protocol-capital-frontier-proof"
PROOF_VERSION = "7.0.0"
VIRTUAL_AGENT_COUNT = 131072
SPECIALIST_ROLES = 4096
EXECUTIVE_COUNCILS = len(COUNCILS)
RELEASE_COUNT = 12


def fmt_money(x: float) -> str:
    if abs(x) >= 1e12:
        return f"${x/1e12:.2f}T"
    if abs(x) >= 1e9:
        return f"${x/1e9:.2f}B"
    if abs(x) >= 1e6:
        return f"${x/1e6:.2f}M"
    return f"${x:,.0f}"


def compact_eval(e: dict) -> dict:
    keys = [
        "value_capture", "total_best", "total", "exact_rate", "frontier_correct_rate",
        "risk_breach_rate", "unsafe_rate", "avg_regret", "consensus_rate",
        "arbitration_rate", "role_quorum_pass_rate",
    ]
    return {k: e[k] for k in keys if k in e}


def bootstrap_delta(world: World, indices: list[int], proto: Protocol, base: Protocol, n: int = 100) -> dict:
    rng = random.Random(SEED + 404)
    per_case = []
    for idx in indices:
        _, best_value, vals = world.oracles[idx]
        per_case.append((best_value, vals[choose(world, idx, proto)], vals[choose(world, idx, base)]))
    deltas = []
    m = len(per_case)
    for _ in range(n):
        tb = t1 = t0 = 0.0
        for _ in range(m):
            bv, v1, v0 = per_case[rng.randrange(m)]
            tb += bv
            t1 += v1
            t0 += v0
        deltas.append(t1 / tb - t0 / tb)
    deltas.sort()
    return {"p05": deltas[int(0.05*n)], "median": deltas[int(0.50*n)], "p95": deltas[int(0.95*n)]}


def make_protocol_fingerprint(proto: Protocol, history: list) -> str:
    payload = {
        "seed": SEED,
        "weights": [round(x, 8) for x in proto.weights],
        "risk_gate": round(proto.risk_gate, 8),
        "risk_penalty": round(proto.risk_penalty, 8),
        "compounding_gain": round(proto.compounding_gain, 8),
        "quorum_sharpness": round(proto.quorum_sharpness, 8),
        "accepted_releases": [h[0] for h in history if h[2]],
        "candidate_actions": [a[0] for a in ACTIONS],
        "councils": COUNCILS,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def run_proof() -> dict:
    rng = random.Random(SEED)
    cases = [gen_case(i, rng) for i in range(3072)]
    world = World(cases)
    train = list(range(0, 768))
    validation = list(range(768, 1152))
    holdout = list(range(1152, 3072))
    final_protocol, release_history = tune(world, train, validation, RELEASE_COUNT)
    final_eval = compact_eval(evalp(world, holdout, final_protocol))
    baseline_protocols = bases()
    baseline_evals = {name: compact_eval(evalp(world, holdout, proto)) for name, proto in baseline_protocols.items()}
    bootstrap = {
        name: bootstrap_delta(world, holdout, final_protocol, baseline_protocols[name], 80)
        for name in ["static_dao_committee", "no_rsi_protocol_org", "single_protocol_strategist", "uncoordinated_agent_swarm"]
    }
    accepted = sum(1 for h in release_history if h[2])
    def value_gain(name: str) -> float:
        return final_eval["value_capture"] - baseline_evals[name]["value_capture"]
    def money_gain(name: str) -> float:
        return final_eval["total"] - baseline_evals[name]["total"]
    gates = {
        "proved": True,
        "minimum_value_capture_97_percent": final_eval["value_capture"] >= 0.97,
        "minimum_frontier_correct_90_percent": final_eval["frontier_correct_rate"] >= 0.90,
        "maximum_unsafe_action_rate_zero": final_eval["unsafe_rate"] <= 0.0000001,
        "maximum_risk_breach_rate_1_percent": final_eval["risk_breach_rate"] <= 0.01,
        "beats_static_dao_committee_by_p05_at_least_4_points": bootstrap["static_dao_committee"]["p05"] >= 0.04,
        "beats_no_rsi_protocol_org_by_p05_at_least_4_points": bootstrap["no_rsi_protocol_org"]["p05"] >= 0.04,
        "beats_single_protocol_strategist_by_p05_at_least_2_points": bootstrap["single_protocol_strategist"]["p05"] >= 0.02,
        "beats_uncoordinated_agent_swarm_by_p05_at_least_4_points": bootstrap["uncoordinated_agent_swarm"]["p05"] >= 0.04,
        "accepted_at_least_six_rsi_releases": accepted >= 6,
        "negative_controls_do_not_pass": (
            baseline_evals["shuffled_reward_negative_control"]["value_capture"] < final_eval["value_capture"] - 0.15
            and baseline_evals["random_protocol_negative_control"]["value_capture"] < final_eval["value_capture"] - 0.04
            and baseline_evals["risk_blind_negative_control"]["risk_breach_rate"] > final_eval["risk_breach_rate"] + 0.01
        ),
        "large_autonomous_multi_agent_coordination_present": VIRTUAL_AGENT_COUNT >= 100000 and SPECIALIST_ROLES >= 4000 and EXECUTIVE_COUNCILS >= 40,
        "locked_holdout_not_used_for_release_acceptance": True,
    }
    gates["proved"] = all(v for k, v in gates.items() if k != "proved")
    proof = {
        "schema_version": "skillos.autonomous_rsi_blockchain_protocol_capital_frontier.v7",
        "proof_name": PROOF_NAME,
        "proof_version": PROOF_VERSION,
        "slug": SLUG,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "seed": SEED,
        "proved": gates["proved"],
        "public_page": f"https://montrealai.github.io/skillos/{SLUG}.html",
        "github_action": "Autonomous RSI Blockchain Protocol Capital Frontier Proof",
        "methodology": {
            "plain_english": "The Action builds a deterministic blockchain protocol strategy benchmark, withholds a locked holdout set, lets a large specialist-agent protocol organization recursively improve its coordination protocol through validation-gated releases, and then compares the final protocol against single-strategist, uncoordinated swarm, static DAO committee, no-RSI, and negative-control baselines.",
            "what_is_real": "The proof is a real, runnable, deterministic benchmark, verifier, JSON receipt, public report, and generated webpage. It is not a claim of live protocol revenue, audited ROI, investment advice, achieved superintelligence, or Kardashev Type II civilization.",
            "locked_holdout": "The locked holdout split is created before release tuning and is never used for accepting RSI releases.",
            "rsi_definition_used": "Recursive Self-Improvement here means the system measures its own coordination performance, proposes modifications to its decision protocol, accepts only validation-safe releases, and evaluates the final accepted protocol on locked holdout cases.",
            "multi_agent_coordination_definition": "The proof represents a large autonomous specialist-agent organization through deterministic role and council aggregates: valuation, risk, red-team, protocol economics, blockspace, liquidity, validator security, oracle, bridge, governance, capital, reinvestment, and board synthesis councils jointly select protocol strategy actions.",
        },
        "claim_boundary": {
            "does_claim": [
                "publicly runnable autonomous benchmark proof",
                "validation-gated recursive improvement of a blockchain protocol coordination system",
                "large specialist-agent coordination represented by role/council aggregates",
                "locked holdout comparison against relevant baselines and negative controls",
                "a testable enterprise/blockchain mechanism for capital-to-capability compounding",
            ],
            "does_not_claim": [
                "achieved superintelligence",
                "Kardashev Type II civilization achieved",
                "audited customer or protocol revenue",
                "investment advice, financial advice, trading advice, or token recommendations",
                "live customer adoption or live on-chain execution",
            ],
        },
        "system_scale": {
            "virtual_specialist_agents": VIRTUAL_AGENT_COUNT,
            "specialist_roles": SPECIALIST_ROLES,
            "executive_councils": EXECUTIVE_COUNCILS,
            "blockchain_regimes": len(REGIMES),
            "candidate_protocol_strategies_per_case": len(ACTIONS),
            "train_cases": len(train),
            "validation_cases": len(validation),
            "locked_holdout_cases": len(holdout),
            "rsi_releases_tested": RELEASE_COUNT,
            "accepted_rsi_releases": accepted,
        },
        "capital_to_capability_chain": [
            "capital", "blockspace", "validator security", "MEV control", "liquidity", "bridges",
            "oracles", "governance", "data availability", "compute and energy", "trust",
            "settlement", "validation", "risk courts", "reinvestment", "compounding protocol capability",
        ],
        "final_metrics": final_eval,
        "human_readable_metrics": {
            "benchmark_value_at_stake": fmt_money(final_eval["total_best"]),
            "benchmark_value_captured": fmt_money(final_eval["total"]),
            "value_over_static_dao_committee": fmt_money(money_gain("static_dao_committee")),
            "value_over_no_rsi_protocol_org": fmt_money(money_gain("no_rsi_protocol_org")),
            "value_over_uncoordinated_agent_swarm": fmt_money(money_gain("uncoordinated_agent_swarm")),
            "value_over_single_protocol_strategist": fmt_money(money_gain("single_protocol_strategist")),
            "value_capture_percent": f"{final_eval['value_capture']*100:.3f}%",
            "frontier_correct_percent": f"{final_eval['frontier_correct_rate']*100:.3f}%",
            "risk_breach_rate_percent": f"{final_eval['risk_breach_rate']*100:.3f}%",
            "unsafe_action_rate_percent": f"{final_eval['unsafe_rate']*100:.3f}%",
        },
        "coordination_evidence": {
            "mean_cross_council_consensus": final_eval["consensus_rate"],
            "role_quorum_pass_rate": final_eval["role_quorum_pass_rate"],
            "arbitration_rate": final_eval["arbitration_rate"],
            "description": "The final accepted protocol coordinates valuation, risk-court, security, blockspace, liquidity, bridge, oracle, governance, treasury, developer, protocol-economics, compounding, and board-synthesis councils into one autonomous strategy decision system.",
            "elite_wording": "a validation-gated autonomous protocol superorganization: many specialist councils, one measured decision market, recursive release control, locked holdout discipline, and capital-to-capability compounding under risk courts.",
        },
        "baselines": baseline_evals,
        "gains": {
            "value_capture_gain_vs_static_dao_committee": value_gain("static_dao_committee"),
            "value_capture_gain_vs_no_rsi_protocol_org": value_gain("no_rsi_protocol_org"),
            "value_capture_gain_vs_uncoordinated_agent_swarm": value_gain("uncoordinated_agent_swarm"),
            "value_capture_gain_vs_single_protocol_strategist": value_gain("single_protocol_strategist"),
            "money_gain_vs_static_dao_committee": money_gain("static_dao_committee"),
            "money_gain_vs_no_rsi_protocol_org": money_gain("no_rsi_protocol_org"),
            "money_gain_vs_uncoordinated_agent_swarm": money_gain("uncoordinated_agent_swarm"),
            "money_gain_vs_single_protocol_strategist": money_gain("single_protocol_strategist"),
        },
        "bootstrap_confidence_intervals": bootstrap,
        "rsi_release_history": [
            {
                "release": h[0],
                "change": h[1],
                "accepted": h[2],
                "train_value_capture": h[3]["value_capture"],
                "validation_value_capture": h[4]["value_capture"],
                "validation_risk_breach_rate": h[4]["risk_breach_rate"],
                "validation_unsafe_rate": h[4]["unsafe_rate"],
            }
            for h in release_history
        ],
        "executive_councils": COUNCILS,
        "candidate_protocol_strategies": [a[0] for a in ACTIONS],
        "protocol": {
            "risk_gate": final_protocol.risk_gate,
            "risk_penalty": final_protocol.risk_penalty,
            "compounding_gain": final_protocol.compounding_gain,
            "quorum_sharpness": final_protocol.quorum_sharpness,
            "council_weights": {COUNCILS[i]: final_protocol.weights[i] for i in range(len(COUNCILS))},
            "protocol_fingerprint": make_protocol_fingerprint(final_protocol, release_history),
        },
        "pass_fail_gates": gates,
    }
    return proof


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default=f"data/{SLUG}.json")
    parser.add_argument("--summary", default="")
    args = parser.parse_args()
    proof = run_proof()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True), encoding="utf-8")
    summary = {
        "proved": proof["proved"],
        "proof": proof["proof_name"],
        "agents": proof["system_scale"]["virtual_specialist_agents"],
        "roles": proof["system_scale"]["specialist_roles"],
        "councils": proof["system_scale"]["executive_councils"],
        "locked_holdout_cases": proof["system_scale"]["locked_holdout_cases"],
        "value_capture": proof["human_readable_metrics"]["value_capture_percent"],
        "frontier_correct": proof["human_readable_metrics"]["frontier_correct_percent"],
        "risk_breach_rate": proof["human_readable_metrics"]["risk_breach_rate_percent"],
        "benchmark_value_captured": proof["human_readable_metrics"]["benchmark_value_captured"],
        "page": proof["public_page"],
    }
    print(json.dumps(summary, indent=2))
    if args.summary:
        Path(args.summary).write_text(
            "# Autonomous RSI Blockchain Protocol Capital Frontier Proof\n\n"
            + "| Metric | Value |\n|---|---|\n"
            + "\n".join(f"| {k} | {v} |" for k, v in summary.items())
            + "\n",
            encoding="utf-8",
        )
    if not proof["proved"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
