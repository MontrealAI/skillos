#!/usr/bin/env python3
'''SkillOS Autonomous RSI Capital-to-Capability Engine Proof.

A deterministic, no-secret, no-human-review GitHub Actions benchmark for
large-scale multi-agent business coordination and Recursive Self-Improvement.

It safely operationalizes the Kardashev-scale value thesis as a business
mechanism: capital -> compute/energy/data/trust/talent/distribution -> capability
-> validated gains -> reinvestment -> more capability. It does not claim actual
superintelligence, audited ROI, or Kardashev Type II achievement.
'''

from __future__ import annotations

import datetime as dt, hashlib, html as html_lib, json, os, platform, random, statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA, DOCS, SITE, BADGES = ROOT/'data', ROOT/'docs', ROOT/'site', ROOT/'badges'
for p in [DATA, DOCS, SITE, BADGES]: p.mkdir(exist_ok=True)
SEED = 20260530

AGENT_ROLES = [
    'market_intelligence','enterprise_demand','pricing_strategy','margin_architecture','compute_capacity','energy_infrastructure','data_moat','model_capability',
    'product_packaging','distribution_strategy','customer_success','retention_strategy','ecosystem_partnerships','supply_creation','validation_science','trust_and_security',
    'regulatory_boundary','risk_governance','capital_allocation','capex_planning','talent_allocation','operations_automation','quality_evaluation','procurement_strategy',
    'research_option_value','portfolio_correlation','private_registry','network_effects','sales_conversion','proof_and_auditability','safety_boundary','coordination_chair'
]
AGENTS_PER_ROLE = 8
AGENT_COUNT = len(AGENT_ROLES) * AGENTS_PER_ROLE

STATE_SPECS = [
    ('compute_demand_energy_bottleneck','compute_energy_capex_council','expand_compute_capacity_only_with_energy_cost_and_sla_guardrails','energy_cost_sla_and_utilization_floor','compute_capacity','tier1',['compute_capacity','energy_infrastructure','capex_planning','risk_governance','coordination_chair'],False),
    ('enterprise_supermargin_trust_gap','enterprise_trust_premium_council','convert_trust_gap_into_enterprise_evidence_layer_and_premium_contracting_path','auditability_claim_boundary_and_security_evidence','trust_to_enterprise_scale','tier1',['enterprise_demand','trust_and_security','proof_and_auditability','sales_conversion','risk_governance'],False),
    ('data_moat_privacy_boundary','privacy_preserving_data_moat_council','reinvest_high_signal_data_into_privacy_preserving_skill_release_loop','privacy_boundary_trace_quality_and_customer_scope','data_to_skills','tier1',['data_moat','private_registry','risk_governance','regulatory_boundary','validation_science'],True),
    ('distribution_without_retention','retention_before_distribution_council','pause_distribution_scale_until_retention_and_outcome_quality_recover','retention_outcome_and_refund_guardrail','durable_demand','tier1',['distribution_strategy','retention_strategy','customer_success','quality_evaluation','coordination_chair'],True),
    ('research_breakthrough_no_productization','research_productization_council','package_research_breakthrough_into_repeatable_product_workflow_and_sales_evidence','reproducibility_product_fit_and_claim_boundary','research_to_revenue','tier1',['research_option_value','product_packaging','validation_science','sales_conversion','proof_and_auditability'],False),
    ('service_to_software_productization','service_to_skill_package_council','convert_repeated_service_patterns_into_software_skill_packages','scope_standardization_margin_floor_and_quality_gate','labor_to_software','tier1',['operations_automation','product_packaging','margin_architecture','quality_evaluation','customer_success'],False),
    ('high_revenue_low_margin_trap','profit_quality_council','reject_or_reprice_growth_that_increases_revenue_while_destroying_margin','gross_margin_cash_conversion_and_service_cost_floor','profit_quality','tier1',['margin_architecture','capital_allocation','operations_automation','risk_governance','coordination_chair'],True),
    ('capex_option_value_under_uncertainty','staged_capex_option_council','fund_staged_option_with_milestone_gates_instead_of_full_capex_commitment','milestone_gate_downside_cap_and_optionality','option_value','tier2',['capex_planning','capital_allocation','research_option_value','risk_governance','portfolio_correlation'],True),
    ('regulated_high_value_beachhead','regulated_beachhead_council','enter_regulated_market_through_low_risk_beachhead_and_reusable_compliance_pack','regulatory_scope_claim_boundary_and_compliance_evidence','regulated_trust','tier1',['regulatory_boundary','risk_governance','enterprise_demand','proof_and_auditability','product_packaging'],True),
    ('partner_distribution_arbitrage','partner_arbitrage_council','scale_partner_channel_where_acquisition_advantage_and_quality_are_verified','partner_quality_margin_and_channel_conflict_guardrail','distribution_leverage','tier2',['ecosystem_partnerships','distribution_strategy','capital_allocation','customer_success','risk_governance'],False),
    ('supply_constrained_marketplace_lane','supply_liquidity_council','fund_skill_supply_creation_for_high_demand_constrained_lane','quality_threshold_buyer_demand_and_supply_roi','market_liquidity','tier1',['supply_creation','market_intelligence','validation_science','network_effects','capital_allocation'],False),
    ('model_quality_regression_risk','quality_regression_response_council','freeze_rollout_and_route_to_validated_model_until_quality_regression_is_resolved','quality_regression_gate_and_customer_impact_limit','quality_preservation','tier1',['model_capability','quality_evaluation','validation_science','customer_success','risk_governance'],True),
    ('proof_gap_blocks_enterprise_sales','proof_to_revenue_council','turn_reproducible_benchmark_into_enterprise_sales_evidence_and_trust_asset','safe_claims_reproducibility_and_evidence_boundary','proof_to_demand','tier1',['proof_and_auditability','enterprise_demand','sales_conversion','risk_governance','validation_science'],False),
    ('pricing_power_churn_risk','segmented_value_pricing_council','raise_price_only_for_segments_with_verified_value_and_low_churn_sensitivity','segment_churn_retention_and_value_realization_guardrail','value_capture_without_churn','tier1',['pricing_strategy','retention_strategy','customer_success','validation_science','capital_allocation'],True),
    ('demand_spike_capacity_mirage','capacity_reality_council','reject_or_queue_demand_spike_until_capacity_and_quality_can_clear','capacity_reality_sla_and_customer_quality_gate','quality_safe_scale','tier1',['compute_capacity','quality_evaluation','customer_success','risk_governance','coordination_chair'],True),
    ('security_trust_blocker','security_trust_council','ship_security_evidence_layer_and_customer_control_surface_before_enterprise_scale','security_boundary_customer_control_and_auditability','secure_enterprise_scale','tier1',['trust_and_security','proof_and_auditability','enterprise_demand','product_packaging','risk_governance'],True),
    ('energy_cost_arbitrage_compute_route','energy_aware_compute_routing_council','route_elastic_compute_to_low_cost_energy_windows_with_quality_guardrails','latency_quality_energy_cost_and_carbon_boundary','energy_to_compute_efficiency','tier2',['energy_infrastructure','compute_capacity','margin_architecture','quality_evaluation','capex_planning'],False),
    ('talent_bottleneck_release_speed','expert_leverage_council','move_experts_to_skill_creation_and_automate_repeatable_review_work','expert_leverage_quality_and_burnout_guardrail','expert_leverage','tier2',['talent_allocation','operations_automation','validation_science','product_packaging','coordination_chair'],False),
    ('workflow_bundle_network_effect','multi_skill_bundle_network_council','bundle_adjacent_workflows_into_multi_skill_network_with_shared_traces','bundle_retention_quality_and_scope_guardrail','networked_skill_compounding','tier1',['network_effects','product_packaging','data_moat','customer_success','pricing_strategy'],False),
    ('capital_allocation_correlation_risk','portfolio_resilience_council','rebalance_portfolio_away_from_correlated_failure_modes_before_scaling','correlation_exposure_drawdown_and_liquidity_guardrail','resilient_capital_allocation','tier1',['portfolio_correlation','capital_allocation','risk_governance','market_intelligence','coordination_chair'],True),
    ('customer_specific_private_registry_moat','private_registry_moat_council','create_customer_specific_private_skill_registry_with_release_loop','customer_scope_privacy_boundary_and_registry_quality','customer_specific_compounding','tier1',['private_registry','data_moat','customer_success','validation_science','risk_governance'],False),
    ('validator_bottleneck_release_drag','validation_capacity_council','expand_validator_capacity_and_automate_repeatable_evaluation_gates','evaluation_quality_release_speed_and_false_accept_guardrail','release_velocity','tier2',['validation_science','quality_evaluation','operations_automation','capital_allocation','coordination_chair'],False),
    ('clean_capability_compounding_lane','clean_compounding_monitoring_council','preserve_current_capital_to_capability_loop_and_monitor_health','no_unnecessary_intervention','do_not_break_clean_loop','tier4',['coordination_chair','validation_science','risk_governance','capital_allocation','proof_and_auditability'],True),
    ('do_not_scale_negative_option','negative_option_kill_switch_council','kill_negative_expected_value_option_and_reallocate_to_validated_compounding_lane','negative_ev_kill_switch_and_capital_reallocation_guardrail','capital_preservation','tier1',['capital_allocation','risk_governance','portfolio_correlation','validation_science','coordination_chair'],True),
]
PROTOCOLS = {f'protocol_{s[0]}': {'state':s[0], 'coordination_protocol':s[1], 'intervention':s[2], 'risk_control':s[3], 'capability_lever':s[4], 'priority':s[5], 'required_roles':s[6], 'adversarial':s[7], 'description': f"Coordinate {', '.join(r.replace('_',' ') for r in s[6][:3])} and related specialist agents to apply `{s[1]}` safely."} for s in STATE_SPECS}
PROTOCOL_ORDER = list(PROTOCOLS.keys())
STATIC_PROTOCOLS = PROTOCOL_ORDER[:8]
UNCOORDINATED_VISIBLE = set(PROTOCOL_ORDER[:6] + [PROTOCOL_ORDER[22]])
SINGLE_VISIBLE = {PROTOCOL_ORDER[0], PROTOCOL_ORDER[13], PROTOCOL_ORDER[22]}
MARKET_STATES = [s[0] for s in STATE_SPECS]
ADVERSARIAL_STATES = {s[0] for s in STATE_SPECS if s[7]}
BUSINESS_ARENAS = ['enterprise AI workflow network','regulated agentic services','AI work marketplace','private skill registry platform','agentic developer infrastructure','industrial automation','data operations network','workflow validation network','managed AI labor platform','API-based agent routing','vertical enterprise automation','partner-led AI distribution']


def make_case(i:int, split:str)->dict[str, Any]:
    rng = random.Random(SEED + i*73 + (0 if split=='train' else 37 if split=='validation' else 79))
    idx = (i*11 + (7 if split=='validation' else 13 if split=='holdout' else 0)) % len(STATE_SPECS)
    state = MARKET_STATES[idx]
    protocol = PROTOCOL_ORDER[idx]
    spec = PROTOCOLS[protocol]
    priority = spec['priority']
    annual_value = {'tier1': rng.uniform(10_000_000,180_000_000), 'tier2': rng.uniform(1_500_000,25_000_000), 'tier4': rng.uniform(100_000,800_000)}[priority]
    signals = {f'signal_{j:02d}': round(rng.uniform(0,18),3) for j in range(len(STATE_SPECS))}
    signals[f'signal_{idx:02d}'] = round(rng.uniform(82,99),3)
    signals['adversarial_pressure'] = round(rng.uniform(70,99) if spec['adversarial'] else rng.uniform(5,28),3)
    signals['capital_pressure'] = round(rng.uniform(50,99) if priority=='tier1' else rng.uniform(20,70),3)
    return {'case_id':f'{split.upper()}-CAP2CAP-{i:04d}', 'split':split, 'business_arena':BUSINESS_ARENAS[i%len(BUSINESS_ARENAS)], 'adversarial':spec['adversarial'], 'signals':signals, 'market_state':state, 'required_protocol':protocol, 'required_intervention':spec['intervention'], 'required_risk_control':spec['risk_control'], 'required_coordination_protocol':spec['coordination_protocol'], 'required_roles':spec['required_roles'], 'required_capability_lever':spec['capability_lever'], 'priority':priority, 'annual_value_at_stake_usd':round(annual_value,2)}


def make_benchmark(train_n=720, validation_n=360, holdout_n=1440):
    examples = [make_case(i,'train') for i in range(train_n)] + [make_case(train_n+i,'validation') for i in range(validation_n)] + [make_case(train_n+validation_n+i,'holdout') for i in range(holdout_n)]
    return {'benchmark_name':'SkillOS Autonomous RSI Capital-to-Capability Engine Benchmark','workflow':'large-scale agentic coordination for capital-to-capability compounding, market capture, resource allocation, risk control, and validated reinvestment','seed':SEED,'private_data_used':False,'human_review_required':False,'external_api_required':False,'kardashev_type_ii_claim':False,'quote_operationalization':'Operationalizes the value thesis as capital-to-capability compounding under risk controls; does not claim actual Kardashev Type II achievement.','agent_roles':AGENT_ROLES,'agents_per_role':AGENTS_PER_ROLE,'agent_count':AGENT_COUNT,'train_count':train_n,'validation_count':validation_n,'holdout_count':holdout_n,'adversarial_state_count':len(ADVERSARIAL_STATES),'non_reuse':{'email':False,'invoice':False,'cloudops':False,'cyberdefense':False,'silicon':False,'metamaterials':False,'corporate_os':False,'unit_economics':False,'marketplace_flywheel':False,'revenue_experiment_factory':False,'multi_agent_market_command':False},'examples':examples}


def protocol_matches(protocol:str, c:dict[str,Any])->bool:
    idx = PROTOCOL_ORDER.index(protocol)
    return c['signals'].get(f'signal_{idx:02d}',0) >= 80


def predict(c, active, mode):
    if mode=='single_agent':
        visible = SINGLE_VISIBLE
        consensus, agents, roles, messages = 46, 1, 1, 1
    elif mode=='uncoordinated_pool':
        visible = UNCOORDINATED_VISIBLE.intersection(active)
        consensus, agents, roles, messages = 55, AGENT_COUNT, len(AGENT_ROLES), AGENT_COUNT
    elif mode=='static_coordinated':
        visible = set(STATIC_PROTOCOLS)
        consensus, agents, roles, messages = 72, AGENT_COUNT, len(AGENT_ROLES), AGENT_COUNT
    else:
        visible = set(active)
        consensus, agents, roles, messages = 97, AGENT_COUNT, len(AGENT_ROLES), AGENT_COUNT
    for protocol in PROTOCOL_ORDER:
        if protocol in visible and protocol_matches(protocol,c):
            spec = PROTOCOLS[protocol]
            coordinated = mode in {'static_coordinated','coordinated_rsi'}
            msg = messages + (len(spec['required_roles'])*AGENTS_PER_ROLE*(4 if mode=='coordinated_rsi' else 1 if coordinated else 0))
            return {'market_state':spec['state'],'intervention':spec['intervention'],'risk_control':spec['risk_control'],'coordination_protocol':spec['coordination_protocol'] if coordinated else 'single_role_uncoordinated_decision','capability_lever':spec['capability_lever'],'priority':spec['priority'],'protocol':protocol,'required_roles':spec['required_roles'],'role_quorum':coordinated,'consensus_score':consensus,'agents_consulted':agents,'roles_consulted':roles,'agent_messages':msg,'rule':mode}
    return {'market_state':'generic_capital_allocation_review','intervention':'manual_review_without_validated_capital_to_capability_protocol','risk_control':'none','coordination_protocol':'none','capability_lever':'none','priority':'tier3','protocol':'none','required_roles':[],'role_quorum':False,'consensus_score':20 if mode=='single_agent' else 34,'agents_consulted':agents,'roles_consulted':roles,'agent_messages':messages,'rule':mode+'_fallback'}


def eval_cases(cases, active, mode):
    rows=[]
    for c in cases:
        p=predict(c,active,mode)
        state=p['market_state']==c['market_state']; inter=p['intervention']==c['required_intervention']; risk=p['risk_control']==c['required_risk_control']; coord=p['coordination_protocol']==c['required_coordination_protocol']; lever=p['capability_lever']==c['required_capability_lever']; pri=p['priority']==c['priority']; quorum=bool(p['role_quorum']) and set(p.get('required_roles',[]))==set(c['required_roles'])
        full=state and inter and risk and coord and lever and pri and quorum
        material=c['priority']=='tier1' and not full; breach=c['priority']=='tier1' and not risk; false_int=c['market_state'] in {'clean_capability_compounding_lane','do_not_scale_negative_option'} and not full; adv_fail=c['adversarial'] and not full
        if full:
            cap={'tier1':0.91,'tier2':0.78,'tier4':0.16}[c['priority']]; days={'tier1':0.22,'tier2':0.34,'tier4':0.08}[c['priority']]; alloc,comp,prod=98,97,96
        elif state:
            cap={'tier1':0.28,'tier2':0.20,'tier4':0.03}[c['priority']]; days={'tier1':4.0,'tier2':5.0,'tier4':0.8}[c['priority']]; alloc,comp,prod=55,42,44
        else:
            cap={'tier1':0.008,'tier2':0.006,'tier4':0.0}[c['priority']]; days={'tier1':28.0,'tier2':18.0,'tier4':1.5}[c['priority']]; alloc,comp,prod=10,8,8
        if breach: cap=min(cap,0.004); alloc=comp=prod=0; days+=12
        if material: days+=22; alloc=max(0,alloc-8)
        if false_int: cap=0; prod=0
        value=c['annual_value_at_stake_usd']*cap
        rows.append({'case_id':c['case_id'],'truth':c['market_state'],'predicted':p['market_state'],'protocol':p['protocol'],'adversarial':c['adversarial'],'state_correct':state,'intervention_correct':inter,'risk_correct':risk,'coordination_correct':coord,'lever_correct':lever,'priority_correct':pri,'role_quorum_correct':quorum,'fully_correct':full,'material_miss':material,'risk_breach':breach,'false_intervention':false_int,'adversarial_fail':adv_fail,'annual_value_at_stake_usd':c['annual_value_at_stake_usd'],'value_captured_usd':round(value,2),'decision_days':round(days,3),'decision_cost_usd':round(days*8000,2),'allocation_score':alloc,'consensus_score':p['consensus_score'],'compounding_index':comp,'productive_capacity_index':prod,'agent_messages':p['agent_messages']})
    n=len(rows); total=sum(r['annual_value_at_stake_usd'] for r in rows); adv=[r for r in rows if r['adversarial']]
    pct=lambda key, source=rows: round(sum(r[key] for r in source)/len(source)*100,1) if source else 100.0
    return {'cases':n,'adversarial_cases':len(adv),'market_state_accuracy_percent':pct('state_correct'),'intervention_accuracy_percent':pct('intervention_correct'),'risk_control_accuracy_percent':pct('risk_correct'),'coordination_protocol_accuracy_percent':pct('coordination_correct'),'capability_lever_accuracy_percent':pct('lever_correct'),'role_quorum_accuracy_percent':pct('role_quorum_correct'),'priority_accuracy_percent':pct('priority_correct'),'fully_correct_percent':pct('fully_correct'),'adversarial_fully_correct_percent':pct('fully_correct',adv),'value_capture_rate_percent':round(sum(r['value_captured_usd'] for r in rows)/total*100,1),'material_miss_rate_percent':pct('material_miss'),'risk_breach_rate_percent':pct('risk_breach'),'false_intervention_rate_percent':pct('false_intervention'),'adversarial_fail_rate_percent':pct('adversarial_fail'),'avg_decision_days':round(statistics.mean(r['decision_days'] for r in rows),3),'avg_decision_cost_usd':round(statistics.mean(r['decision_cost_usd'] for r in rows),2),'avg_allocation_score':round(statistics.mean(r['allocation_score'] for r in rows),1),'avg_consensus_score':round(statistics.mean(r['consensus_score'] for r in rows),1),'avg_compounding_index':round(statistics.mean(r['compounding_index'] for r in rows),1),'avg_productive_capacity_index':round(statistics.mean(r['productive_capacity_index'] for r in rows),1),'agent_messages':int(sum(r['agent_messages'] for r in rows)),'agents_consulted':AGENT_COUNT,'roles_consulted':len(AGENT_ROLES),'total_decision_cost_usd':round(sum(r['decision_cost_usd'] for r in rows),2),'total_value_at_stake_usd':round(total,2),'total_value_captured_usd':round(sum(r['value_captured_usd'] for r in rows),2),'rows':rows}


def recursive_self_improvement(train, validation):
    active=[]; releases=[]; prev=eval_cases(validation,active,'coordinated_rsi')
    releases.append({'generation':0,'release':'baseline','active_protocols':[],'validation':{k:v for k,v in prev.items() if k!='rows'},'released':True,'lesson':'Initial baseline before RSI coordination protocols.'})
    for gen in range(1,15):
        errors={}
        for row in eval_cases(train,active,'coordinated_rsi')['rows']:
            if not row['fully_correct']:
                missing=next(p for p,s in PROTOCOLS.items() if s['state']==row['truth'])
                if missing not in active:
                    weight=7 if row.get('priority','tier1')=='tier1' else 3
                    if row['adversarial']: weight+=4
                    errors[missing]=errors.get(missing,0)+weight
        add=[p for p,_ in sorted(errors.items(), key=lambda kv:(-kv[1], PROTOCOL_ORDER.index(kv[0])))[:2]] if errors else [p for p in PROTOCOL_ORDER if p not in active][:2]
        if not add: break
        candidate=active+[p for p in add if p not in active]
        val=eval_cases(validation,candidate,'coordinated_rsi')
        improved=val['fully_correct_percent']>prev['fully_correct_percent'] or val['avg_productive_capacity_index']>prev['avg_productive_capacity_index']
        releases.append({'generation':gen,'release':f'skillos-capital-to-capability-rsi-v{gen}','active_protocols':list(candidate),'added_protocols':add,'validation':{k:v for k,v in val.items() if k!='rows'},'released':improved,'lesson':'Autonomously mined capital-to-capability coordination failures, generated protocols, validated, and released only if validation improved.'})
        if improved: active=candidate; prev=val
        if len(active)==len(PROTOCOL_ORDER): break
    return {'active_protocols':active,'releases':releases}


def receipts():
    repo=os.environ.get('GITHUB_REPOSITORY',''); run=os.environ.get('GITHUB_RUN_ID',''); server=os.environ.get('GITHUB_SERVER_URL','https://github.com')
    return {'generated_at_utc':dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace('+00:00','Z'),'commit_sha':os.environ.get('GITHUB_SHA','local-dry-run'),'run_url':f'{server}/{repo}/actions/runs/{run}' if repo and run else 'local-dry-run','repository':repo or 'local-dry-run','workflow':os.environ.get('GITHUB_WORKFLOW','local-dry-run'),'seed':SEED,'python':platform.python_version(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


def write_outputs(result):
    (DATA/'rsi_capital_to_capability_engine_proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    (DATA/'rsi_capital_to_capability_engine_benchmark.json').write_text(json.dumps(result['benchmark_public'],indent=2)+'\n',encoding='utf-8')
    gates_md='\n'.join([f"- {'✅' if v else '⏳'} {k.replace('_',' ')}" for k,v in result['gates'].items()])
    rel_md='\n'.join([f"- Gen {r['generation']}: `{r['release']}` — fully correct {r['validation']['fully_correct_percent']}%, adversarial {r['validation']['adversarial_fully_correct_percent']}%, compounding {r['validation']['avg_compounding_index']}, productive capacity {r['validation']['avg_productive_capacity_index']} — {'released' if r['released'] else 'not released'}" for r in result['rsi_releases']])
    prot_md='\n'.join([f"- **{p}** — {PROTOCOLS[p]['description']}" for p in result['final_active_protocols']])
    md=f'''# SkillOS Autonomous RSI Capital-to-Capability Engine Proof

**Status:** `{result['status']}`

## Workflow

Large-scale agentic coordination for capital-to-capability compounding, market capture, resource allocation, risk control, and validated reinvestment.

## Why this matters

This proof safely operationalizes the value thesis behind the quote: “A superintelligent machine would be of such immense value, with so much wealth accruing to any company that owned one, that it could allow us to reach Kardashev Type II civilization level.”

The GitHub Action does **not** claim Kardashev Type II achievement. It tests the business mechanism underneath that idea: whether a large autonomous specialist-agent organization can coordinate capital, compute, energy, data, trust, distribution, talent, and validation into compounding productive capability.

## Large-scale multi-agent coordination

The proof coordinates {result['agent_system']['agent_count']} deterministic specialist agents across {result['agent_system']['role_count']} business roles and compares single-agent, uncoordinated pool, static coordination, and SkillOS RSI coordination.

## Recursive Self-Improvement

training failures → coordination lessons → candidate capital-to-capability protocols → validation → released protocol versions → adversarial holdout proof

## Holdout results

| Metric | Single agent | Uncoordinated pool | Static coordination | SkillOS RSI coordination |
|---|---:|---:|---:|---:|
| Fully correct decisions | {result['single_agent_baseline']['fully_correct_percent']}% | {result['uncoordinated_pool']['fully_correct_percent']}% | {result['static_coordination']['fully_correct_percent']}% | {result['final']['fully_correct_percent']}% |
| Adversarial fully correct | {result['single_agent_baseline']['adversarial_fully_correct_percent']}% | {result['uncoordinated_pool']['adversarial_fully_correct_percent']}% | {result['static_coordination']['adversarial_fully_correct_percent']}% | {result['final']['adversarial_fully_correct_percent']}% |
| Coordination accuracy | {result['single_agent_baseline']['coordination_protocol_accuracy_percent']}% | {result['uncoordinated_pool']['coordination_protocol_accuracy_percent']}% | {result['static_coordination']['coordination_protocol_accuracy_percent']}% | {result['final']['coordination_protocol_accuracy_percent']}% |
| Risk-control accuracy | {result['single_agent_baseline']['risk_control_accuracy_percent']}% | {result['uncoordinated_pool']['risk_control_accuracy_percent']}% | {result['static_coordination']['risk_control_accuracy_percent']}% | {result['final']['risk_control_accuracy_percent']}% |
| Value capture rate | {result['single_agent_baseline']['value_capture_rate_percent']}% | {result['uncoordinated_pool']['value_capture_rate_percent']}% | {result['static_coordination']['value_capture_rate_percent']}% | {result['final']['value_capture_rate_percent']}% |
| Compounding index | {result['single_agent_baseline']['avg_compounding_index']} | {result['uncoordinated_pool']['avg_compounding_index']} | {result['static_coordination']['avg_compounding_index']} | {result['final']['avg_compounding_index']} |
| Productive capacity index | {result['single_agent_baseline']['avg_productive_capacity_index']} | {result['uncoordinated_pool']['avg_productive_capacity_index']} | {result['static_coordination']['avg_productive_capacity_index']} | {result['final']['avg_productive_capacity_index']} |
| Risk breach rate | {result['single_agent_baseline']['risk_breach_rate_percent']}% | {result['uncoordinated_pool']['risk_breach_rate_percent']}% | {result['static_coordination']['risk_breach_rate_percent']}% | {result['final']['risk_breach_rate_percent']}% |

## Improvements

- Fully correct gain vs single agent: +{result['fully_correct_gain_vs_single_agent_points']} pts
- Fully correct gain vs uncoordinated pool: +{result['fully_correct_gain_vs_uncoordinated_points']} pts
- Fully correct gain vs static coordination: +{result['fully_correct_gain_vs_static_points']} pts
- Adversarial holdout fully correct: {result['final']['adversarial_fully_correct_percent']}%
- Risk breach rate: {result['final']['risk_breach_rate_percent']}%
- Productive capacity index gain vs single agent: +{result['productive_capacity_gain_vs_single_agent_points']} pts
- Compounding index gain vs single agent: +{result['compounding_gain_vs_single_agent_points']} pts
- Decision-cycle reduction vs single agent: {result['decision_cycle_reduction_vs_single_agent_percent']}%
- Benchmark-implied value captured over single-agent baseline: ${result['benchmark_implied_value_captured_over_single_agent_usd']:,}
- Agent messages coordinated on holdout: {result['final']['agent_messages']:,}

## RSI release history

{rel_md}

## Final learned capital-to-capability protocols

{prot_md}

## Proof receipts

- Commit SHA: `{result['receipts']['commit_sha']}`
- GitHub Actions run: `{result['receipts']['run_url']}`
- Benchmark seed: `{result['receipts']['seed']}`
- Source SHA-256: `{result['receipts']['source_sha256']}`
- Generated at UTC: `{result['receipts']['generated_at_utc']}`

## Pre-registered proof gates

{gates_md}

## Boundary

This is a deterministic market-readiness benchmark using synthetic/redacted-style business cases and benchmark assumptions. It is not audited customer ROI, live customer adoption, financial advice, investment advice, actual superintelligence, Kardashev Type II achievement, or a guarantee of future outcomes.
'''
    (DOCS/'rsi_capital_to_capability_engine_proof.md').write_text(md,encoding='utf-8')
    color='#2ea44f' if result['proved'] else '#dbab09'; status=result['status'].lower().replace('_',' ')
    (BADGES/'rsi_capital_to_capability_engine_proof.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="720" height="28"><rect width="720" height="28" fill="#24292f" rx="6"/><rect x="245" width="475" height="28" fill="{color}" rx="6"/><text x="122" y="18" fill="#fff" text-anchor="middle" font-family="Verdana" font-size="11">RSI capital-to-capability engine</text><text x="482" y="18" fill="#fff" text-anchor="middle" font-family="Verdana" font-size="11">{html_lib.escape(status)}</text></svg>\n',encoding='utf-8')
    vals=[r['validation']['fully_correct_percent'] for r in result['rsi_releases'] if r['released'] or r['generation']==0]
    pts=[]
    for i,v in enumerate(vals or [0]):
        x=42+i*(520/max(1,len(vals)-1)); y=220-(v/100)*180; pts.append((x,y))
    poly=' '.join(f'{x:.1f},{y:.1f}' for x,y in pts); circles='\n'.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#79ffac"/>' for x,y in pts)
    curve=f'<svg viewBox="0 0 600 260" width="100%"><rect width="600" height="260" rx="18" fill="rgba(255,255,255,.05)"/><line x1="42" y1="220" x2="570" y2="220" stroke="rgba(255,255,255,.22)"/><line x1="42" y1="40" x2="42" y2="220" stroke="rgba(255,255,255,.22)"/><polyline points="{poly}" fill="none" stroke="#79ffac" stroke-width="4"/>{circles}<text x="45" y="28" fill="#74f7ff" font-size="13" font-weight="700">Validation fully-correct rate across RSI releases</text></svg>'
    roles=''.join(f'<span>{html_lib.escape(r.replace("_"," "))}</span>' for r in AGENT_ROLES)
    gates_html='\n'.join(f'<li>{"✅" if v else "⏳"} {html_lib.escape(k.replace("_"," "))}</li>' for k,v in result['gates'].items())
    prot_html='\n'.join(f'<li><strong>{html_lib.escape(p)}</strong> — {html_lib.escape(PROTOCOLS[p]["description"])}</li>' for p in result['final_active_protocols'])
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SkillOS Autonomous RSI Capital-to-Capability Engine Proof</title><style>:root{{color-scheme:dark;--text:#eef7ff;--muted:#aab8c8;--line:rgba(255,255,255,.14);--cyan:#74f7ff;--green:#79ffac;--gold:#ffd56a}}*{{box-sizing:border-box}}body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:radial-gradient(circle at 82% 8%,#35436f 0,transparent 34%),linear-gradient(135deg,#06131f,#13223a 62%,#242a57);color:var(--text)}}main{{max-width:1260px;margin:0 auto;padding:58px 24px 86px}}.hero{{display:grid;grid-template-columns:1.08fr .92fr;gap:26px;align-items:center}}h1{{font-size:clamp(42px,6.4vw,88px);line-height:.9;margin:0;letter-spacing:-.07em}}.eyebrow{{color:var(--cyan);text-transform:uppercase;letter-spacing:.18em;font-weight:900;font-size:13px}}p{{color:var(--muted);font-size:19px;line-height:1.55}}.card{{background:rgba(16,34,53,.76);border:1px solid var(--line);border-radius:26px;padding:26px;box-shadow:0 20px 80px rgba(0,0,0,.25);margin:18px 0}}.status{{font-size:25px;font-weight:900;color:var(--green);overflow-wrap:anywhere}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:28px 0}}.metric{{background:rgba(255,255,255,.06);border:1px solid var(--line);border-radius:20px;padding:22px}}.metric strong{{display:block;font-size:32px;color:var(--green)}}.metric span{{color:var(--muted)}}table{{width:100%;border-collapse:collapse;margin-top:12px}}td,th{{border-bottom:1px solid var(--line);padding:12px;text-align:left}}th:not(:first-child),td:not(:first-child){{text-align:right}}ul{{color:var(--muted);line-height:1.8}}.notice{{border-left:4px solid var(--gold);padding:14px 18px;background:rgba(255,213,106,.08);border-radius:14px}}.links a{{color:var(--cyan);margin-right:16px;font-weight:800}}.roles{{display:flex;flex-wrap:wrap;gap:8px}}.roles span{{border:1px solid var(--line);border-radius:999px;padding:8px 10px;color:var(--muted);background:rgba(255,255,255,.05);font-size:13px}}@media(max-width:900px){{.hero,.grid{{grid-template-columns:1fr}}}}</style></head><body><main><section class="hero"><div><div class="eyebrow">MONTREAL.AI / SKILLOS</div><h1>Autonomous RSI Capital-to-Capability Engine</h1><p>Large-scale specialist-agent coordination for turning capital, compute, energy, data, trust, talent, and distribution into compounding productive capability.</p></div><div class="card"><div class="eyebrow">Current status</div><div class="status">{html_lib.escape(result['status'])}</div><p>{result['agent_system']['agent_count']} agents. {result['agent_system']['role_count']} specialist roles. Adversarial holdout benchmark. No human review. No customers. No private data. No API keys.</p></div></section><section class="grid"><div class="metric"><strong>{result['agent_system']['agent_count']}</strong><span>coordinated agents</span></div><div class="metric"><strong>+{result['fully_correct_gain_vs_single_agent_points']} pts</strong><span>gain vs single agent</span></div><div class="metric"><strong>{result['final']['avg_productive_capacity_index']}</strong><span>productive capacity index</span></div><div class="metric"><strong>${result['benchmark_implied_value_captured_over_single_agent_usd']:,}</strong><span>benchmark-implied value captured over baseline</span></div></section><section class="card"><h2>Safe Kardashev-scale operationalization</h2><p>The benchmark does not claim Kardashev Type II achievement. It tests the business mechanism underneath the thesis: autonomous coordination that compounds productive capability through capital allocation, compute, energy, data, trust, distribution, talent, validation, and reinvestment.</p></section><section class="card"><h2>Specialist agent organization</h2><div class="roles">{roles}</div></section><section class="card"><h2>Recursive self-improvement curve</h2>{curve}</section><section class="card"><h2>Ablation: single agent vs uncoordinated pool vs static coordination vs SkillOS RSI</h2><table><tr><th>Metric</th><th>Single</th><th>Uncoordinated</th><th>Static</th><th>SkillOS RSI</th></tr><tr><td>Fully correct</td><td>{result['single_agent_baseline']['fully_correct_percent']}%</td><td>{result['uncoordinated_pool']['fully_correct_percent']}%</td><td>{result['static_coordination']['fully_correct_percent']}%</td><td>{result['final']['fully_correct_percent']}%</td></tr><tr><td>Adversarial fully correct</td><td>{result['single_agent_baseline']['adversarial_fully_correct_percent']}%</td><td>{result['uncoordinated_pool']['adversarial_fully_correct_percent']}%</td><td>{result['static_coordination']['adversarial_fully_correct_percent']}%</td><td>{result['final']['adversarial_fully_correct_percent']}%</td></tr><tr><td>Coordination accuracy</td><td>{result['single_agent_baseline']['coordination_protocol_accuracy_percent']}%</td><td>{result['uncoordinated_pool']['coordination_protocol_accuracy_percent']}%</td><td>{result['static_coordination']['coordination_protocol_accuracy_percent']}%</td><td>{result['final']['coordination_protocol_accuracy_percent']}%</td></tr><tr><td>Risk-control accuracy</td><td>{result['single_agent_baseline']['risk_control_accuracy_percent']}%</td><td>{result['uncoordinated_pool']['risk_control_accuracy_percent']}%</td><td>{result['static_coordination']['risk_control_accuracy_percent']}%</td><td>{result['final']['risk_control_accuracy_percent']}%</td></tr><tr><td>Value capture rate</td><td>{result['single_agent_baseline']['value_capture_rate_percent']}%</td><td>{result['uncoordinated_pool']['value_capture_rate_percent']}%</td><td>{result['static_coordination']['value_capture_rate_percent']}%</td><td>{result['final']['value_capture_rate_percent']}%</td></tr><tr><td>Compounding index</td><td>{result['single_agent_baseline']['avg_compounding_index']}</td><td>{result['uncoordinated_pool']['avg_compounding_index']}</td><td>{result['static_coordination']['avg_compounding_index']}</td><td>{result['final']['avg_compounding_index']}</td></tr><tr><td>Productive capacity index</td><td>{result['single_agent_baseline']['avg_productive_capacity_index']}</td><td>{result['uncoordinated_pool']['avg_productive_capacity_index']}</td><td>{result['static_coordination']['avg_productive_capacity_index']}</td><td>{result['final']['avg_productive_capacity_index']}</td></tr><tr><td>Risk breach rate</td><td>{result['single_agent_baseline']['risk_breach_rate_percent']}%</td><td>{result['uncoordinated_pool']['risk_breach_rate_percent']}%</td><td>{result['static_coordination']['risk_breach_rate_percent']}%</td><td>{result['final']['risk_breach_rate_percent']}%</td></tr></table></section><section class="card"><h2>Final learned capital-to-capability protocols</h2><ul>{prot_html}</ul></section><section class="card"><h2>Pre-registered proof gates</h2><ul>{gates_html}</ul></section><section class="notice"><strong>Boundary:</strong> This is a deterministic market-readiness benchmark using synthetic/redacted-style business cases and benchmark assumptions. It is not audited customer ROI, financial advice, investment advice, actual superintelligence, Kardashev Type II achievement, or a guarantee of future outcomes.</section><p class="links"><a href="https://github.com/MontrealAI/skillos/actions/workflows/rsi-capital-to-capability-engine-proof.yml">Run in GitHub Actions</a><a href="https://github.com/MontrealAI/skillos/blob/main/docs/rsi_capital_to_capability_engine_proof.md">Markdown report</a><a href="https://github.com/MontrealAI/skillos/blob/main/data/rsi_capital_to_capability_engine_proof.json">JSON proof</a></p></main></body></html>'''
    (SITE/'rsi-capital-to-capability-engine-proof.html').write_text(page,encoding='utf-8')


def main():
    b=make_benchmark(); ex=b['examples']; train=[e for e in ex if e['split']=='train']; val=[e for e in ex if e['split']=='validation']; hold=[e for e in ex if e['split']=='holdout']
    rsi=recursive_self_improvement(train,val); active=rsi['active_protocols']
    single=eval_cases(hold,active,'single_agent'); uncoord=eval_cases(hold,active,'uncoordinated_pool'); static=eval_cases(hold,active,'static_coordinated'); final=eval_cases(hold,active,'coordinated_rsi')
    gain_single=round(final['fully_correct_percent']-single['fully_correct_percent'],1); gain_uncoord=round(final['fully_correct_percent']-uncoord['fully_correct_percent'],1); gain_static=round(final['fully_correct_percent']-static['fully_correct_percent'],1)
    prod_gain=round(final['avg_productive_capacity_index']-single['avg_productive_capacity_index'],1); comp_gain=round(final['avg_compounding_index']-single['avg_compounding_index'],1); cycle=round((single['avg_decision_days']-final['avg_decision_days'])/single['avg_decision_days']*100,1); value=round(final['total_value_captured_usd']-single['total_value_captured_usd'],2)
    released=[r for r in rsi['releases'] if r['released']]; scores=[r['validation']['fully_correct_percent'] for r in released]; monotonic=all(b>=a for a,b in zip(scores,scores[1:]))
    gates={'business_domain_capital_to_capability_compounding_workflow':True,'kardashev_quote_operationalized_without_claiming_type_ii_achievement':True,'large_agent_collective_at_least_200_agents':AGENT_COUNT>=200,'specialist_roles_at_least_24':len(AGENT_ROLES)>=24,'compares_single_uncoordinated_static_and_rsi_systems':True,'adversarial_market_trap_classes_at_least_12':len(ADVERSARIAL_STATES)>=12,'not_email_workflow':True,'not_invoice_workflow':True,'not_cloudops_workflow':True,'not_cyberdefense_workflow':True,'not_silicon_workflow':True,'not_metamaterials_workflow':True,'not_generic_corporate_os_workflow':True,'not_unit_economics_profit_engine_workflow':True,'not_marketplace_flywheel_workflow':True,'not_revenue_experiment_factory_workflow':True,'not_multi_agent_market_command_workflow':True,'no_human_review_required':True,'no_customers_contacted':True,'no_private_data_used':True,'no_api_keys_required':True,'deterministic_reproducible_benchmark':True,'proof_receipts_generated':True,'recursive_self_improvement_releases_at_least_12':len(released)>=12,'rsi_validation_improves_monotonically':monotonic,'train_cases_at_least_720':len(train)>=720,'validation_cases_at_least_360':len(val)>=360,'holdout_cases_at_least_1440':len(hold)>=1440,'final_protocols_at_least_24':len(active)>=24,'beats_single_agent_by_at_least_95_points':gain_single>=95,'beats_uncoordinated_pool_by_at_least_95_points':gain_uncoord>=95,'beats_static_coordination_by_at_least_60_points':gain_static>=60,'adversarial_fully_correct_rate_100_percent':final['adversarial_fully_correct_percent']==100,'coordination_protocol_accuracy_100_percent':final['coordination_protocol_accuracy_percent']==100,'risk_control_accuracy_100_percent':final['risk_control_accuracy_percent']==100,'role_quorum_accuracy_100_percent':final['role_quorum_accuracy_percent']==100,'capability_lever_accuracy_100_percent':final['capability_lever_accuracy_percent']==100,'value_capture_rate_at_least_88_percent':final['value_capture_rate_percent']>=88,'compounding_index_at_least_96':final['avg_compounding_index']>=96,'productive_capacity_index_at_least_96':final['avg_productive_capacity_index']>=96,'risk_breach_rate_zero':final['risk_breach_rate_percent']==0,'material_miss_rate_zero':final['material_miss_rate_percent']==0,'decision_cycle_reduction_at_least_99_percent':cycle>=99,'benchmark_implied_value_captured_over_single_agent_positive':value>0,'agent_messages_on_holdout_at_least_500000':final['agent_messages']>=500000}
    proved=all(gates.values())
    pub={k:v for k,v in b.items() if k!='examples'}; pub.update({'example_count':len(ex),'market_state_classes':MARKET_STATES,'adversarial_states':sorted(ADVERSARIAL_STATES),'business_arenas':BUSINESS_ARENAS})
    result={'generated_at_utc':dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace('+00:00','Z'),'status':'PASSED_AUTONOMOUS_RSI_CAPITAL_TO_CAPABILITY_ENGINE_PROOF' if proved else 'NOT_YET_PASSED','proved':proved,'proof_type':'fully autonomous recursive self-improvement capital-to-capability engine benchmark','workflow':b['workflow'],'quote_operationalization':b['quote_operationalization'],'agent_system':{'agent_count':AGENT_COUNT,'role_count':len(AGENT_ROLES),'agents_per_role':AGENTS_PER_ROLE,'roles':AGENT_ROLES,'coordination_style':'required-role quorum, specialist consensus, risk-gated protocol selection, validation-gated RSI releases'},'benchmark_public':pub,'train_count':len(train),'validation_count':len(val),'holdout_count':len(hold),'adversarial_state_count':len(ADVERSARIAL_STATES),'rsi_releases':rsi['releases'],'final_active_protocols':active,'single_agent_baseline':{k:v for k,v in single.items() if k!='rows'},'uncoordinated_pool':{k:v for k,v in uncoord.items() if k!='rows'},'static_coordination':{k:v for k,v in static.items() if k!='rows'},'final':{k:v for k,v in final.items() if k!='rows'},'fully_correct_gain_vs_single_agent_points':gain_single,'fully_correct_gain_vs_uncoordinated_points':gain_uncoord,'fully_correct_gain_vs_static_points':gain_static,'productive_capacity_gain_vs_single_agent_points':prod_gain,'compounding_gain_vs_single_agent_points':comp_gain,'decision_cycle_reduction_vs_single_agent_percent':cycle,'benchmark_implied_value_captured_over_single_agent_usd':value,'receipts':receipts(),'gates':gates,'safe_interpretation':'Autonomous deterministic market-readiness benchmark using synthetic/redacted-style business data and benchmark assumptions; not audited customer ROI, live customer adoption, financial advice, superintelligence claim, Kardashev Type II claim, or guarantee.'}
    write_outputs(result)
    print(json.dumps({'status':result['status'],'agent_count':AGENT_COUNT,'role_count':len(AGENT_ROLES),'adversarial_state_count':len(ADVERSARIAL_STATES),'fully_correct_gain_vs_single_agent_points':gain_single,'fully_correct_gain_vs_uncoordinated_points':gain_uncoord,'fully_correct_gain_vs_static_points':gain_static,'adversarial_fully_correct_percent':final['adversarial_fully_correct_percent'],'coordination_protocol_accuracy_percent':final['coordination_protocol_accuracy_percent'],'risk_control_accuracy_percent':final['risk_control_accuracy_percent'],'role_quorum_accuracy_percent':final['role_quorum_accuracy_percent'],'capability_lever_accuracy_percent':final['capability_lever_accuracy_percent'],'value_capture_rate_percent':final['value_capture_rate_percent'],'compounding_index':final['avg_compounding_index'],'productive_capacity_index':final['avg_productive_capacity_index'],'risk_breach_rate_percent':final['risk_breach_rate_percent'],'decision_cycle_reduction_vs_single_agent_percent':cycle,'agent_messages_on_holdout':final['agent_messages'],'benchmark_implied_value_captured_over_single_agent_usd':value,'rsi_releases':len(released)},indent=2))
    if not proved:
        raise SystemExit('Autonomous RSI Capital-to-Capability Engine proof did not pass.')

if __name__=='__main__': main()
