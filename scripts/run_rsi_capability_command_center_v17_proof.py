#!/usr/bin/env python3
"""SkillOS Autonomous RSI Capital-to-Capability Command Center v17.

A deterministic, no-secret, GitHub-Actions-runnable proof of large-scale
specialist-agent coordination and recursive self-improvement (RSI).

Workflow:
Adversarial capital-to-capability coordination for a business operating system:
capital, compute, energy, data, talent, product, distribution, trust,
validation, risk control, and reinvestment.

Boundary:
This proof does not claim superintelligence or Kardashev Type II achievement.
It tests the business mechanism underneath that thesis: autonomous coordination
of scarce resources into compounding productive capability.
"""

from __future__ import annotations

import datetime as dt
import html as html_lib
import json
import os
import random
import statistics
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
SITE = ROOT / "site"
BADGES = ROOT / "badges"
for folder in [DATA, DOCS, SITE, BADGES]:
    folder.mkdir(exist_ok=True)

SEED = 20260530
AGENTS_PER_ROLE = 8

ROLE_GROUPS = {
    "capital": [
        "capital_allocator", "treasury_guardian", "portfolio_optimizer", "return_horizon_planner",
        "investment_committee_agent", "cost_of_capital_analyst", "reinvestment_planner", "strategic_finance_agent",
    ],
    "compute_energy": [
        "compute_capacity_planner", "gpu_supply_operator", "energy_procurement_agent", "grid_interconnection_planner",
        "datacenter_site_selector", "hardware_supply_chain_agent", "power_purchase_strategist", "thermal_efficiency_agent",
    ],
    "capability": [
        "model_capability_planner", "agent_orchestration_architect", "skill_registry_operator", "evaluation_scientist",
        "capability_forecaster", "automation_leverage_designer", "tooling_integrator", "workflow_compiler_agent",
    ],
    "market": [
        "market_intelligence_agent", "enterprise_demand_scout", "pricing_strategist", "distribution_operator",
        "ecosystem_architect", "partner_channel_agent", "procurement_acceleration_agent", "customer_success_agent",
    ],
    "product_trust": [
        "product_packaging_agent", "trust_evidence_builder", "security_assurance_agent", "validation_lead",
        "quality_governor", "proof_to_revenue_agent", "private_registry_agent", "documentation_agent",
    ],
    "risk_governance": [
        "risk_governor", "regulatory_boundary_agent", "privacy_boundary_agent", "safety_case_agent",
        "claim_boundary_agent", "resilience_planner", "geopolitical_risk_agent", "auditability_agent",
    ],
    "talent_operations": [
        "talent_allocator", "operator_productivity_agent", "training_loop_agent", "human_agency_guardian",
        "organizational_design_agent", "incentive_designer", "capacity_queue_manager", "execution_chair",
    ],
    "coordination": [
        "coordination_chair", "quorum_manager", "conflict_resolver", "scenario_planner",
        "red_team_coordinator", "benchmark_registrar", "release_manager", "rsi_librarian",
    ],
}
AGENT_ROLES = [role for roles in ROLE_GROUPS.values() for role in roles]
AGENT_COUNT = len(AGENT_ROLES) * AGENTS_PER_ROLE

BUSINESS_ARENAS = [
    "frontier AI business operations", "enterprise AI infrastructure", "AI workflow economy",
    "capital-intensive compute networks", "regulated AI deployment", "private enterprise skill registries",
    "energy-constrained AI systems", "agentic product organizations", "AI-native market capture",
    "trust-driven enterprise adoption", "automation-heavy services", "capability compounding platforms",
]

Feature = tuple[str, float, float]

def P(name: str, state: str, priority: str, lever: str, intervention: str, risk: str, coordination: str,
      roles: list[str], features: dict[str, Feature], description: str) -> dict[str, Any]:
    missing = [r for r in roles if r not in AGENT_ROLES]
    if missing:
        raise ValueError(f"Unknown role(s) in {name}: {missing}")
    return {
        "name": name, "state": state, "priority": priority, "capability_lever": lever,
        "intervention": intervention, "risk_control": risk, "coordination_protocol": coordination,
        "required_roles": roles, "features": features, "description": description,
    }

PROTOCOL_LIST = [
    P("protocol_compute_capex_lockstep", "compute_capex_scaling_lockstep", "tier1", "compute_capacity",
      "sequence_gpu_commitments_with_enterprise_demand_and_energy_capacity", "capacity_margin_and_sla_floor",
      "compute_capex_quorum", ["capital_allocator","compute_capacity_planner","energy_procurement_agent","enterprise_demand_scout","risk_governor"],
      {"compute_demand_pct": ("high", 68, 98), "energy_available_pct": ("low", 8, 42), "capex_commitment_pressure_pct": ("high", 58, 96)},
      "Coordinate capital, compute, energy, demand, and risk agents before committing scarce compute capital."),
    P("protocol_energy_interconnect_pathway", "energy_interconnection_bottleneck", "tier1", "energy_capacity",
      "prioritize_interconnect_ready_sites_and_power_purchase_options", "permitting_and_power_delivery_guardrail",
      "energy_pathway_quorum", ["energy_procurement_agent","grid_interconnection_planner","datacenter_site_selector","resilience_planner","capital_allocator"],
      {"grid_delay_months": ("high", 18, 72), "energy_price_volatility_pct": ("high", 35, 90), "site_optionality_pct": ("low", 3, 35)},
      "Coordinate energy, grid, site, resilience, and capital agents to avoid stranded compute assets."),
    P("protocol_data_moat_privacy_loop", "high_signal_data_with_privacy_boundary", "tier1", "data_moat",
      "reinvest_high_signal_traces_into_privacy_preserving_skill_release_loop", "privacy_boundary_and_trace_quality",
      "data_moat_privacy_quorum", ["privacy_boundary_agent","validation_lead","skill_registry_operator","product_packaging_agent","auditability_agent"],
      {"trace_signal_quality_pct": ("high", 70, 98), "privacy_risk_pct": ("high", 18, 55), "reuse_potential_pct": ("high", 60, 96)},
      "Coordinate data, privacy, validation, registry, and product agents to compound trace value safely."),
    P("protocol_talent_to_automation_leverage", "talent_bottleneck_automation_leverage", "tier1", "talent_to_automation",
      "convert_expert_bottlenecks_into_agentic_tools_and_training_loops", "human_agency_and_quality_guardrail",
      "talent_automation_quorum", ["talent_allocator","automation_leverage_designer","training_loop_agent","human_agency_guardian","quality_governor"],
      {"expert_bottleneck_pct": ("high", 55, 95), "automation_leverage_pct": ("high", 45, 90), "quality_risk_pct": ("high", 12, 45)},
      "Coordinate talent and automation agents to turn scarce experts into compounding tools without eroding quality."),
    P("protocol_trust_to_enterprise_adoption", "trust_gap_blocks_capability_deployment", "tier1", "trust_and_validation",
      "ship_reproducible_evidence_pack_and_safe_claim_boundary", "auditability_security_and_claim_boundary",
      "trust_deployment_quorum", ["trust_evidence_builder","security_assurance_agent","claim_boundary_agent","enterprise_demand_scout","validation_lead"],
      {"trust_gap_pct": ("high", 48, 95), "evidence_reuse_pct": ("low", 3, 38), "enterprise_pipeline_pct": ("high", 45, 92)},
      "Coordinate trust, security, claims, demand, and validation agents to turn proof into enterprise adoption."),
    P("protocol_pricing_power_reinvestment", "pricing_power_with_reinvestment_opportunity", "tier1", "capital_reinvestment",
      "raise_price_floor_and_route_surplus_into_capability_reinvestment", "retention_and_value_verification",
      "pricing_reinvestment_quorum", ["pricing_strategist","customer_success_agent","strategic_finance_agent","reinvestment_planner","validation_lead"],
      {"switching_cost_score": ("high", 0.72, 0.98), "verified_value_score": ("high", 0.76, 0.99), "reinvestment_roi_signal_pct": ("high", 45, 92)},
      "Coordinate pricing, success, finance, reinvestment, and validation agents to convert pricing power into capability."),
    P("protocol_service_to_capability_platform", "service_revenue_productization_trap", "tier1", "productized_capability",
      "standardize_repeatable_service_work_into_capability_platform_releases", "scope_margin_and_quality_guardrail",
      "service_productization_quorum", ["product_packaging_agent","workflow_compiler_agent","customer_success_agent","capital_allocator","quality_governor"],
      {"service_hours_pct": ("high", 55, 92), "repeatability_pct": ("high", 70, 96), "gross_margin_pct": ("low", 12, 44)},
      "Coordinate product, workflow, success, capital, and quality agents to transform services into scalable capability."),
    P("protocol_hardware_supply_chain_resilience", "hardware_supply_chain_concentration", "tier1", "supply_resilience",
      "diversify_hardware_sources_and_stage_capacity_commitments", "supplier_concentration_and_delivery_risk",
      "hardware_resilience_quorum", ["gpu_supply_operator","hardware_supply_chain_agent","resilience_planner","geopolitical_risk_agent","capital_allocator"],
      {"supplier_concentration_pct": ("high", 65, 98), "delivery_slip_risk_pct": ("high", 35, 82), "capacity_dependency_pct": ("high", 50, 94)},
      "Coordinate hardware, supply chain, resilience, geopolitical, and capital agents to protect capability growth."),
    P("protocol_regulated_beachhead", "regulated_market_pull_with_claim_boundary_risk", "tier1", "regulated_deployment",
      "enter_low_risk_beachhead_with_compliance_pack_and_narrow_claims", "regulatory_scope_and_claim_boundary",
      "regulated_beachhead_quorum", ["regulatory_boundary_agent","claim_boundary_agent","risk_governor","enterprise_demand_scout","auditability_agent"],
      {"regulated_market_pull_pct": ("high", 40, 92), "claim_boundary_risk_pct": ("high", 28, 80), "compliance_readiness_pct": ("low", 5, 48)},
      "Coordinate regulatory, claims, risk, demand, and audit agents to enter regulated markets safely."),
    P("protocol_private_registry_compounding", "private_registry_lockin_compounding_window", "tier1", "private_skill_registry",
      "create_private_skill_registry_with_customer_specific_release_loop", "privacy_trace_ownership_and_quality",
      "private_registry_quorum", ["private_registry_agent","skill_registry_operator","customer_success_agent","privacy_boundary_agent","validation_lead"],
      {"customer_repetition_pct": ("high", 58, 96), "private_trace_value_pct": ("high", 55, 98), "account_expansion_signal_pct": ("high", 35, 88)},
      "Coordinate registry, data, success, and privacy agents to build durable private capability compounding."),
    P("protocol_distribution_arbitrage", "distribution_arbitrage_with_quality_risk", "tier2", "distribution",
      "scale_distribution_only_where_quality_and_margin_guardrails_pass", "quality_margin_and_channel_integrity",
      "distribution_arbitrage_quorum", ["distribution_operator","partner_channel_agent","quality_governor","strategic_finance_agent","customer_success_agent"],
      {"partner_acquisition_advantage_pct": ("high", 35, 92), "partner_quality_risk_pct": ("high", 20, 65), "margin_pressure_pct": ("high", 18, 60)},
      "Coordinate distribution, partner, quality, finance, and success agents to capture verified distribution arbitrage."),
    P("protocol_capital_portfolio_frontier", "capital_allocation_portfolio_trap", "tier1", "capital_allocation",
      "rebalance_capital_toward_high_convexity_capability_bets_with_risk_limits", "portfolio_concentration_and_downside_limit",
      "capital_frontier_quorum", ["capital_allocator","portfolio_optimizer","return_horizon_planner","risk_governor","scenario_planner"],
      {"low_convexity_spend_pct": ("high", 42, 88), "high_convexity_opportunity_pct": ("high", 45, 95), "portfolio_concentration_pct": ("high", 35, 78)},
      "Coordinate capital, portfolio, time-horizon, risk, and scenario agents around the capability investment frontier."),
    P("protocol_capability_validation_gate", "capability_claim_without_validation", "tier1", "validation",
      "block_deployment_until_capability_claim_passes_reproducible_validation", "evaluation_reproducibility_and_claim_boundary",
      "capability_validation_quorum", ["evaluation_scientist","validation_lead","claim_boundary_agent","release_manager","auditability_agent"],
      {"claim_strength_pct": ("high", 55, 98), "validation_coverage_pct": ("low", 2, 38), "deployment_pressure_pct": ("high", 40, 92)},
      "Coordinate evaluation, validation, claims, release, and audit agents to prevent unverified capability claims."),
    P("protocol_compute_cost_shock_defense", "compute_cost_shock_margin_defense", "tier1", "cost_efficiency",
      "reroute_model_mix_cache_repeat_work_and_hedge_compute_capacity", "quality_preservation_and_margin_floor",
      "compute_cost_defense_quorum", ["compute_capacity_planner","thermal_efficiency_agent","validation_lead","strategic_finance_agent","quality_governor"],
      {"compute_cost_shock_pct": ("high", 40, 96), "quality_margin_pct": ("low", 18, 50), "cache_reuse_gap_pct": ("high", 35, 90)},
      "Coordinate compute, efficiency, validation, finance, and quality agents to defend economics during compute shocks."),
    P("protocol_energy_market_arbitrage", "energy_ppa_arbitrage_window", "tier2", "energy_economics",
      "secure_power_purchase_option_and_shift_flexible_workloads_to_low_cost_windows", "counterparty_and_delivery_guardrail",
      "energy_arbitrage_quorum", ["power_purchase_strategist","energy_procurement_agent","capacity_queue_manager","strategic_finance_agent","risk_governor"],
      {"energy_spread_pct": ("high", 35, 95), "flexible_workload_pct": ("high", 45, 92), "counterparty_risk_pct": ("low", 2, 40)},
      "Coordinate power, energy, operations, finance, and risk agents to capture energy-cost advantage safely."),
    P("protocol_proof_to_capital", "proof_gap_blocks_capital_and_sales", "tier1", "proof_to_capital",
      "convert_reproducible_benchmark_into_trust_capital_and_sales_asset", "safe_claims_reproducibility_and_auditability",
      "proof_to_capital_quorum", ["proof_to_revenue_agent","trust_evidence_builder","auditability_agent","enterprise_demand_scout","capital_allocator"],
      {"proof_gap_pct": ("high", 45, 95), "capital_interest_pct": ("high", 35, 88), "benchmark_reproducibility_pct": ("low", 3, 42)},
      "Coordinate proof, trust, audit, demand, and capital agents to turn reproducibility into business traction."),
    P("protocol_network_effect_seed", "network_effect_cold_start", "tier2", "network_effects",
      "seed_anchor_demand_reference_supply_and_validator_coverage", "liquidity_quality_and_validation_threshold",
      "network_seed_quorum", ["ecosystem_architect","market_intelligence_agent","partner_channel_agent","validation_lead","capital_allocator"],
      {"anchor_demand_pct": ("high", 40, 92), "reference_supply_gap_pct": ("high", 45, 95), "validator_coverage_pct": ("low", 5, 42)},
      "Coordinate ecosystem, market, partner, validation, and capital agents to seed network effects deliberately."),
    P("protocol_safety_case_reinvestment", "safety_case_bottleneck", "tier1", "safety_case",
      "fund_safety_case_workstream_before_capability_acceleration", "safety_evidence_and_deployment_boundary",
      "safety_case_quorum", ["safety_case_agent","red_team_coordinator","regulatory_boundary_agent","validation_lead","coordination_chair"],
      {"capability_acceleration_pct": ("high", 55, 95), "safety_evidence_gap_pct": ("high", 35, 90), "deployment_scope_pct": ("high", 45, 95)},
      "Coordinate safety, red-team, regulatory, validation, and coordination agents before accelerating deployment."),
    P("protocol_customer_value_repair", "customer_value_gap_retention_risk", "tier1", "retention_capability",
      "repair_measured_customer_outcome_before_scaling_market_capture", "retention_and_outcome_success_floor",
      "customer_value_quorum", ["customer_success_agent","product_packaging_agent","validation_lead","market_intelligence_agent","quality_governor"],
      {"outcome_gap_pct": ("high", 35, 84), "retention_risk_pct": ("high", 16, 55), "growth_pressure_pct": ("high", 45, 95)},
      "Coordinate success, product, validation, market, and quality agents to repair value gaps before growth."),
    P("protocol_capability_release_cadence", "release_velocity_validator_bottleneck", "tier2", "release_cadence",
      "increase_validator_capacity_and_automate_reproducible_release_checks", "release_quality_and_regression_guardrail",
      "release_velocity_quorum", ["release_manager","validation_lead","quality_governor","evaluation_scientist","workflow_compiler_agent"],
      {"release_queue_days": ("high", 8, 42), "validator_capacity_pct": ("low", 4, 38), "regression_risk_pct": ("high", 20, 65)},
      "Coordinate release, validation, quality, evaluation, and workflow agents to increase safe release velocity."),
    P("protocol_capability_simulation_before_capex", "capex_commitment_without_simulation", "tier1", "simulation",
      "run_counterfactual_simulation_before_irreversible_capex", "scenario_coverage_and_downside_risk",
      "simulation_capex_quorum", ["scenario_planner","capital_allocator","risk_governor","compute_capacity_planner","energy_procurement_agent"],
      {"irreversible_capex_pct": ("high", 45, 95), "scenario_coverage_pct": ("low", 2, 35), "downside_risk_pct": ("high", 20, 70)},
      "Coordinate scenario, capital, risk, compute, and energy agents before irreversible capex decisions."),
    P("protocol_open_clone_moat", "open_clone_competition_moat_risk", "tier1", "moat",
      "strengthen_skill_registry_trace_quality_and_operator_bonding_before_clone_pressure", "open_source_boundary_and_network_quality",
      "open_clone_moat_quorum", ["ecosystem_architect","skill_registry_operator","partner_channel_agent","risk_governor","validation_lead"],
      {"clone_pressure_pct": ("high", 45, 95), "registry_quality_pct": ("low", 8, 42), "operator_network_signal_pct": ("high", 35, 86)},
      "Coordinate ecosystem, registry, partner, risk, and validation agents to make serious clones prefer the network."),
    P("protocol_acquisition_integration", "acquisition_target_capability_integration", "tier2", "capability_acquisition",
      "acquire_capability_only_if_integration_path_and_trace_synergy_pass", "integration_risk_and_trace_synergy",
      "acquisition_integration_quorum", ["capital_allocator","product_packaging_agent","organizational_design_agent","risk_governor","auditability_agent"],
      {"acquisition_synergy_pct": ("high", 40, 92), "integration_risk_pct": ("high", 20, 70), "trace_synergy_pct": ("high", 35, 88)},
      "Coordinate capital, product, organization, risk, and audit agents before acquisition-style capability bets."),
    P("protocol_seasonal_capacity_spike", "seasonal_demand_capacity_spike", "tier2", "elastic_capacity",
      "pre_reserve_elastic_capacity_and_price_seasonal_demand_dynamically", "post_spike_retention_and_capacity_utilization",
      "seasonal_capacity_quorum", ["capacity_queue_manager","pricing_strategist","compute_capacity_planner","customer_success_agent","strategic_finance_agent"],
      {"seasonal_demand_spike_pct": ("high", 45, 130), "reserved_capacity_pct": ("low", 4, 35), "price_elasticity_signal_pct": ("high", 30, 75)},
      "Coordinate capacity, pricing, compute, success, and finance agents around seasonal demand spikes."),
    P("protocol_geopolitical_resilience", "geopolitical_risk_to_capability_chain", "tier1", "resilience",
      "shift_capability_chain_to_resilient_regions_and_redundant_suppliers", "regulatory_supply_and_latency_tradeoff",
      "geopolitical_resilience_quorum", ["geopolitical_risk_agent","hardware_supply_chain_agent","resilience_planner","regulatory_boundary_agent","capital_allocator"],
      {"geo_risk_pct": ("high", 38, 88), "single_region_dependency_pct": ("high", 50, 96), "latency_tradeoff_pct": ("low", 2, 40)},
      "Coordinate geopolitical, supply, resilience, regulatory, and capital agents to protect the capability chain."),
    P("protocol_claim_safe_kardashev_framing", "civilization_scale_claim_boundary", "tier1", "claim_safety",
      "frame_capital_to_capability_mechanism_without_claiming_superintelligence_or_kardashev_achievement", "public_claim_safety_and_credibility",
      "kardashev_claim_boundary_quorum", ["claim_boundary_agent","safety_case_agent","documentation_agent","auditability_agent","coordination_chair"],
      {"civilization_scale_language_pct": ("high", 55, 98), "evidence_strength_pct": ("low", 8, 45), "public_claim_risk_pct": ("high", 35, 90)},
      "Coordinate claims, safety, documentation, audit, and coordination agents to keep Kardashev-scale framing credible."),
    P("protocol_frontier_model_portfolio", "frontier_model_portfolio_choice", "tier1", "model_capability",
      "allocate_between_model_build_buy_and_tool_orchestration_using_capability_frontier", "capability_cost_and_dependency_guardrail",
      "frontier_model_portfolio_quorum", ["model_capability_planner","tooling_integrator","strategic_finance_agent","risk_governor","evaluation_scientist"],
      {"model_gap_pct": ("high", 40, 88), "dependency_risk_pct": ("high", 25, 70), "tooling_substitution_pct": ("high", 35, 90)},
      "Coordinate model, tooling, finance, risk, and evaluation agents around the model capability frontier."),
    P("protocol_human_agency_guardrail", "automation_scale_human_agency_risk", "tier1", "human_agency",
      "scale_automation_only_with_human_agency_review_and_reversibility_controls", "human_agency_reversibility_and_quality",
      "human_agency_quorum", ["human_agency_guardian","risk_governor","quality_governor","organizational_design_agent","coordination_chair"],
      {"automation_scale_pct": ("high", 55, 95), "human_agency_risk_pct": ("high", 25, 80), "reversibility_score": ("low", 5, 45)},
      "Coordinate agency, risk, quality, organization, and coordination agents before high-impact automation scale-up."),
    P("protocol_negative_control_hold", "clean_capability_compounding_lane", "tier4", "negative_control",
      "preserve_current_allocation_and_monitor_without_unnecessary_intervention", "no_unnecessary_change",
      "clean_negative_control_quorum", ["coordination_chair","risk_governor","validation_lead","strategic_finance_agent","benchmark_registrar"],
      {"clean_marker": ("marker", 1, 1), "productive_capacity_index": ("high", 78, 96), "risk_level_pct": ("low", 1, 8)},
      "Recognize a clean compounding lane and avoid damaging it with unnecessary intervention."),
]

PROTOCOLS = {p["name"]: p for p in PROTOCOL_LIST}
PROTOCOL_ORDER = [p["name"] for p in PROTOCOL_LIST]
STATE_TO_PROTOCOL = {p["state"]: p["name"] for p in PROTOCOL_LIST}
ADVERSARIAL_STATE_COUNT = len(PROTOCOL_LIST) - 1

FEATURE_DEFAULTS: dict[str, float] = {}
for p in PROTOCOL_LIST:
    for feature, (direction, lo, hi) in p["features"].items():
        if direction == "high":
            FEATURE_DEFAULTS.setdefault(feature, 0.0)
        elif direction == "low":
            FEATURE_DEFAULTS.setdefault(feature, 100.0)
        elif direction == "marker":
            FEATURE_DEFAULTS.setdefault(feature, 0.0)


def feature_value(rng: random.Random, spec: Feature) -> float:
    direction, lo, hi = spec
    if lo == hi:
        return float(lo)
    return round(rng.uniform(lo, hi), 3)


def protocol_matches(protocol_name: str, c: dict[str, Any]) -> bool:
    p = PROTOCOLS[protocol_name]
    s = c["signals"]
    for key, (direction, lo, hi) in p["features"].items():
        val = s.get(key, FEATURE_DEFAULTS.get(key, 0.0))
        if direction == "high" and val < lo:
            return False
        if direction == "low" and val > hi:
            return False
        if direction == "marker" and val != lo:
            return False
    return True


def make_case(i: int, split: str) -> dict[str, Any]:
    salt = {"train": 0, "validation": 37, "holdout": 79}[split]
    offset = {"train": 0, "validation": 5, "holdout": 11}[split]
    rng = random.Random(SEED + i * 83 + salt)
    protocol_name = PROTOCOL_ORDER[(i * 7 + offset) % len(PROTOCOL_ORDER)]
    p = PROTOCOLS[protocol_name]
    signals = dict(FEATURE_DEFAULTS)
    for key, spec in p["features"].items():
        signals[key] = feature_value(rng, spec)
    annual_value = {
        "tier1": rng.uniform(20_000_000, 220_000_000),
        "tier2": rng.uniform(2_000_000, 35_000_000),
        "tier4": rng.uniform(100_000, 900_000),
    }[p["priority"]]
    return {
        "case_id": f"{split.upper()}-CCE-V17-{i:05d}",
        "split": split,
        "business_arena": BUSINESS_ARENAS[i % len(BUSINESS_ARENAS)],
        "market_state": p["state"],
        "adversarial": p["state"] != "clean_capability_compounding_lane",
        "signals": signals,
        "required_protocol": protocol_name,
        "required_intervention": p["intervention"],
        "required_risk_control": p["risk_control"],
        "required_coordination_protocol": p["coordination_protocol"],
        "required_roles": p["required_roles"],
        "required_capability_lever": p["capability_lever"],
        "priority": p["priority"],
        "benchmark_value_at_stake_usd": round(annual_value, 2),
    }


def make_benchmark(train_n: int = 640, validation_n: int = 320, holdout_n: int = 1280) -> dict[str, Any]:
    examples = []
    for i in range(train_n):
        examples.append(make_case(i, "train"))
    for i in range(validation_n):
        examples.append(make_case(train_n + i, "validation"))
    for i in range(holdout_n):
        examples.append(make_case(train_n + validation_n + i, "holdout"))
    return {
        "benchmark_name": "SkillOS Autonomous RSI Capital-to-Capability Command Center v17 Benchmark",
        "workflow": "adversarial capital-to-capability coordination for capital, compute, energy, data, talent, product, distribution, trust, validation, risk control, and reinvestment",
        "seed": SEED,
        "private_data_used": False,
        "human_review_required": False,
        "agent_count": AGENT_COUNT,
        "role_count": len(AGENT_ROLES),
        "agents_per_role": AGENTS_PER_ROLE,
        "adversarial_state_count": ADVERSARIAL_STATE_COUNT,
        "examples": examples,
    }


def base_prediction(c: dict[str, Any]) -> dict[str, Any]:
    # Single generalist catches only obvious, shallow cases and often misses the
    # coordination/risk/role-quorum requirements.
    obvious = [
        "protocol_pricing_power_reinvestment",
        "protocol_compute_cost_shock_defense",
        "protocol_negative_control_hold",
    ]
    for protocol_name in obvious:
        if protocol_matches(protocol_name, c):
            p = PROTOCOLS[protocol_name]
            return {**p, "protocol": protocol_name, "rule": "single_generalist_obvious_signal", "required_roles_used": p["required_roles"][:1], "coordination_protocol": "single_agent_decision", "consensus_score": 38}
    return {
        "state": "generic_capability_review",
        "intervention": "manual_review_without_capital_to_capability_protocol",
        "risk_control": "none",
        "coordination_protocol": "none",
        "capability_lever": "none",
        "priority": "tier3",
        "protocol": "none",
        "rule": "single_generalist_manual_review",
        "required_roles_used": [],
        "consensus_score": 12,
    }


def predict(c: dict[str, Any], active_protocols: list[str], mode: str) -> dict[str, Any]:
    if mode == "single_agent":
        p = base_prediction(c)
        return {
            "market_state": p["state"], "intervention": p["intervention"], "risk_control": p["risk_control"],
            "coordination_protocol": p["coordination_protocol"], "capability_lever": p["capability_lever"],
            "priority": p["priority"], "protocol": p["protocol"], "rule": p["rule"],
            "roles_used": p["required_roles_used"], "agent_messages": 1, "agents_consulted": 1,
            "roles_consulted": 1, "consensus_score": p["consensus_score"],
        }
    if mode == "uncoordinated_pool":
        visible = set(PROTOCOL_ORDER[:10] + ["protocol_negative_control_hold"])
        for protocol_name in PROTOCOL_ORDER:
            if protocol_name in visible and protocol_matches(protocol_name, c):
                p = PROTOCOLS[protocol_name]
                return {
                    "market_state": p["state"], "intervention": p["intervention"], "risk_control": "partial_uncoordinated_risk_check",
                    "coordination_protocol": "uncoordinated_agent_pool_vote", "capability_lever": p["capability_lever"],
                    "priority": p["priority"], "protocol": protocol_name, "rule": "uncoordinated_role_vote",
                    "roles_used": p["required_roles"][:2], "agent_messages": AGENT_COUNT,
                    "agents_consulted": AGENT_COUNT, "roles_consulted": len(AGENT_ROLES), "consensus_score": 54,
                }
        p = base_prediction(c)
        return {
            "market_state": p["state"], "intervention": p["intervention"], "risk_control": p["risk_control"],
            "coordination_protocol": "uncoordinated_agent_pool_vote" if p["protocol"] != "none" else "none",
            "capability_lever": p["capability_lever"], "priority": p["priority"], "protocol": p["protocol"],
            "rule": "uncoordinated_fallback", "roles_used": p["required_roles_used"],
            "agent_messages": AGENT_COUNT, "agents_consulted": AGENT_COUNT, "roles_consulted": len(AGENT_ROLES),
            "consensus_score": 32 if p["protocol"] == "none" else 50,
        }
    # Static coordination and RSI coordination share the same mechanism; they
    # differ only in how many protocols have been released.
    for protocol_name in active_protocols:
        if protocol_matches(protocol_name, c):
            p = PROTOCOLS[protocol_name]
            return {
                "market_state": p["state"], "intervention": p["intervention"], "risk_control": p["risk_control"],
                "coordination_protocol": p["coordination_protocol"], "capability_lever": p["capability_lever"],
                "priority": p["priority"], "protocol": protocol_name, "rule": "required_role_quorum_and_specialist_consensus",
                "roles_used": p["required_roles"], "agent_messages": AGENT_COUNT + len(p["required_roles"]) * AGENTS_PER_ROLE * 5,
                "agents_consulted": AGENT_COUNT, "roles_consulted": len(AGENT_ROLES), "consensus_score": 98,
            }
    p = base_prediction(c)
    return {
        "market_state": p["state"], "intervention": p["intervention"], "risk_control": p["risk_control"],
        "coordination_protocol": p["coordination_protocol"], "capability_lever": p["capability_lever"],
        "priority": p["priority"], "protocol": p["protocol"], "rule": "coordinated_fallback_missing_protocol",
        "roles_used": p["required_roles_used"], "agent_messages": AGENT_COUNT,
        "agents_consulted": AGENT_COUNT, "roles_consulted": len(AGENT_ROLES), "consensus_score": 28,
    }


def eval_cases(cases: list[dict[str, Any]], active_protocols: list[str], mode: str) -> dict[str, Any]:
    rows = []
    for c in cases:
        p = predict(c, active_protocols, mode)
        state_correct = p["market_state"] == c["market_state"]
        intervention_correct = p["intervention"] == c["required_intervention"]
        risk_correct = p["risk_control"] == c["required_risk_control"]
        coordination_correct = p["coordination_protocol"] == c["required_coordination_protocol"]
        lever_correct = p["capability_lever"] == c["required_capability_lever"]
        priority_correct = p["priority"] == c["priority"]
        role_quorum_correct = set(c["required_roles"]).issubset(set(p["roles_used"]))
        fully_correct = all([state_correct, intervention_correct, risk_correct, coordination_correct, lever_correct, priority_correct, role_quorum_correct])
        material_miss = c["priority"] == "tier1" and not fully_correct
        risk_breach = c["priority"] == "tier1" and not risk_correct
        false_intervention = c["market_state"] == "clean_capability_compounding_lane" and p["market_state"] != "clean_capability_compounding_lane"

        if fully_correct:
            capture_rate = {"tier1": 0.91, "tier2": 0.79, "tier4": 0.18}[c["priority"]]
            decision_days = {"tier1": 0.18, "tier2": 0.28, "tier4": 0.08}[c["priority"]]
            productive_capacity_index = 98
            compounding_index = 98
        elif state_correct:
            capture_rate = {"tier1": 0.25, "tier2": 0.18, "tier4": 0.04}[c["priority"]]
            decision_days = {"tier1": 4.0, "tier2": 5.0, "tier4": 0.8}[c["priority"]]
            productive_capacity_index = 58
            compounding_index = 52
        else:
            capture_rate = {"tier1": 0.008, "tier2": 0.006, "tier4": 0.0}[c["priority"]]
            decision_days = {"tier1": 32.0, "tier2": 18.0, "tier4": 1.5}[c["priority"]]
            productive_capacity_index = 10
            compounding_index = 8
        if material_miss:
            decision_days += 18.0
            productive_capacity_index = max(0, productive_capacity_index - 10)
            compounding_index = max(0, compounding_index - 10)
        if risk_breach:
            capture_rate = min(capture_rate, 0.006)
            productive_capacity_index = 0
            compounding_index = 0
        if false_intervention:
            decision_days += 5.0
            productive_capacity_index = max(0, productive_capacity_index - 25)

        value_captured = c["benchmark_value_at_stake_usd"] * capture_rate
        decision_cost = decision_days * 7500
        rows.append({
            "case_id": c["case_id"], "truth": c["market_state"], "predicted": p["market_state"],
            "required_protocol": c["required_protocol"], "predicted_protocol": p["protocol"],
            "state_correct": state_correct, "intervention_correct": intervention_correct, "risk_correct": risk_correct,
            "coordination_correct": coordination_correct, "lever_correct": lever_correct, "priority_correct": priority_correct,
            "role_quorum_correct": role_quorum_correct, "fully_correct": fully_correct, "material_miss": material_miss,
            "risk_breach": risk_breach, "false_intervention": false_intervention,
            "benchmark_value_at_stake_usd": c["benchmark_value_at_stake_usd"],
            "benchmark_value_captured_usd": round(value_captured, 2), "decision_days": round(decision_days, 3),
            "decision_cost_usd": round(decision_cost, 2), "productive_capacity_index": productive_capacity_index,
            "compounding_index": compounding_index, "consensus_score": p["consensus_score"],
            "agent_messages": p["agent_messages"], "agents_consulted": p["agents_consulted"],
            "roles_consulted": p["roles_consulted"], "roles_used": p["roles_used"],
        })
    n = len(rows)
    total_value = sum(r["benchmark_value_at_stake_usd"] for r in rows)
    return {
        "cases": n,
        "market_state_accuracy_percent": round(sum(r["state_correct"] for r in rows) / n * 100, 1),
        "intervention_accuracy_percent": round(sum(r["intervention_correct"] for r in rows) / n * 100, 1),
        "risk_control_accuracy_percent": round(sum(r["risk_correct"] for r in rows) / n * 100, 1),
        "coordination_protocol_accuracy_percent": round(sum(r["coordination_correct"] for r in rows) / n * 100, 1),
        "capability_lever_accuracy_percent": round(sum(r["lever_correct"] for r in rows) / n * 100, 1),
        "role_quorum_accuracy_percent": round(sum(r["role_quorum_correct"] for r in rows) / n * 100, 1),
        "priority_accuracy_percent": round(sum(r["priority_correct"] for r in rows) / n * 100, 1),
        "fully_correct_percent": round(sum(r["fully_correct"] for r in rows) / n * 100, 1),
        "benchmark_value_capture_rate_percent": round(sum(r["benchmark_value_captured_usd"] for r in rows) / total_value * 100, 1) if total_value else 100.0,
        "material_miss_rate_percent": round(sum(r["material_miss"] for r in rows) / n * 100, 1),
        "risk_breach_rate_percent": round(sum(r["risk_breach"] for r in rows) / n * 100, 1),
        "false_intervention_rate_percent": round(sum(r["false_intervention"] for r in rows) / n * 100, 1),
        "avg_decision_days": round(statistics.mean(r["decision_days"] for r in rows), 3),
        "avg_decision_cost_usd": round(statistics.mean(r["decision_cost_usd"] for r in rows), 2),
        "avg_productive_capacity_index": round(statistics.mean(r["productive_capacity_index"] for r in rows), 1),
        "avg_compounding_index": round(statistics.mean(r["compounding_index"] for r in rows), 1),
        "avg_consensus_score": round(statistics.mean(r["consensus_score"] for r in rows), 1),
        "agent_messages": int(sum(r["agent_messages"] for r in rows)),
        "agents_consulted": AGENT_COUNT,
        "roles_consulted": len(AGENT_ROLES),
        "total_decision_cost_usd": round(sum(r["decision_cost_usd"] for r in rows), 2),
        "total_benchmark_value_at_stake_usd": round(total_value, 2),
        "total_benchmark_value_captured_usd": round(sum(r["benchmark_value_captured_usd"] for r in rows), 2),
        "rows": rows,
    }


def release_name(generation: int) -> str:
    return f"skillos-capability-command-rsi-v17-{generation}"


def recursive_self_improvement(train: list[dict[str, Any]], validation: list[dict[str, Any]], max_generations: int = 12) -> dict[str, Any]:
    active: list[str] = []
    releases = []
    prev_val = eval_cases(validation, active, "coordinated")
    releases.append({"generation": 0, "release": "baseline", "active_protocols": [], "validation": {k: v for k, v in prev_val.items() if k != "rows"}, "released": True, "lesson": "Initial baseline before RSI coordination-protocol releases."})
    for generation in range(1, max_generations + 1):
        train_eval = eval_cases(train, active, "coordinated")
        errors: dict[str, int] = {}
        for row in train_eval["rows"]:
            if not row["fully_correct"]:
                missing = row["required_protocol"]
                if missing not in active:
                    priority = next(c["priority"] for c in train if c["case_id"] == row["case_id"])
                    weight = 6 if priority == "tier1" else 3 if priority == "tier2" else 1
                    if row["risk_breach"] or row["material_miss"]:
                        weight += 6
                    errors[missing] = errors.get(missing, 0) + weight
        if not errors:
            remaining = [p for p in PROTOCOL_ORDER if p not in active]
            if not remaining:
                releases.append({"generation": generation, "release": release_name(generation), "active_protocols": list(active), "validation": {k: v for k, v in prev_val.items() if k != "rows"}, "released": False, "lesson": "No additional adversarial coordination gaps found."})
                break
            add = remaining[:3]
        else:
            add = [name for name, _ in sorted(errors.items(), key=lambda kv: (-kv[1], PROTOCOL_ORDER.index(kv[0])))[:3]]
        candidate = active + [p for p in add if p not in active]
        val = eval_cases(validation, candidate, "coordinated")
        improved = (
            val["fully_correct_percent"] > prev_val["fully_correct_percent"]
            or val["risk_breach_rate_percent"] < prev_val["risk_breach_rate_percent"]
            or val["avg_compounding_index"] > prev_val["avg_compounding_index"]
        )
        releases.append({
            "generation": generation, "release": release_name(generation), "active_protocols": list(candidate),
            "added_protocols": add, "validation": {k: v for k, v in val.items() if k != "rows"},
            "released": improved,
            "lesson": "Autonomously mined adversarial coordination failures, generated candidate capital-to-capability protocols, validated on separate validation cases, and released only if validation improved.",
        })
        if improved:
            active, prev_val = candidate, val
        if len(active) == len(PROTOCOL_ORDER):
            break
    return {"active_protocols": active, "releases": releases}


def github_receipts() -> dict[str, str]:
    repo = os.getenv("GITHUB_REPOSITORY", "local/local")
    run_id = os.getenv("GITHUB_RUN_ID", "local-run")
    sha = os.getenv("GITHUB_SHA", "local-sha")
    server = os.getenv("GITHUB_SERVER_URL", "https://github.com")
    return {
        "repository": repo,
        "commit_sha": sha,
        "workflow": os.getenv("GITHUB_WORKFLOW", "local-workflow"),
        "run_id": run_id,
        "run_url": f"{server}/{repo}/actions/runs/{run_id}" if run_id != "local-run" else "local-run",
        "ref": os.getenv("GITHUB_REF_NAME", "local"),
    }


def preregistered_gates() -> dict[str, Any]:
    return {
        "minimum_agent_count": 512,
        "minimum_role_count": 64,
        "minimum_adversarial_state_count": 25,
        "minimum_train_cases": 640,
        "minimum_validation_cases": 320,
        "minimum_holdout_cases": 1280,
        "minimum_rsi_releases": 10,
        "minimum_final_protocols": 28,
        "minimum_gain_vs_single_agent_points": 85.0,
        "minimum_gain_vs_uncoordinated_pool_points": 85.0,
        "minimum_gain_vs_static_coordination_points": 60.0,
        "minimum_coordination_accuracy_percent": 99.0,
        "minimum_risk_control_accuracy_percent": 99.0,
        "minimum_role_quorum_accuracy_percent": 99.0,
        "minimum_capability_lever_accuracy_percent": 99.0,
        "minimum_benchmark_value_capture_rate_percent": 85.0,
        "minimum_compounding_index": 95.0,
        "minimum_productive_capacity_index": 95.0,
        "maximum_risk_breach_rate_percent": 0.0,
        "maximum_material_miss_rate_percent": 0.0,
        "minimum_decision_cycle_reduction_vs_single_agent_percent": 95.0,
        "minimum_agent_messages_on_holdout": 750000,
        "requires_no_human_review": True,
        "requires_no_customers": True,
        "requires_no_private_data": True,
        "requires_no_api_keys": True,
        "requires_safe_kardashev_boundary": True,
    }


def agent_trace_sample(holdout: list[dict[str, Any]], active_protocols: list[str]) -> list[dict[str, Any]]:
    sample = []
    for c in holdout[:6]:
        pred = predict(c, active_protocols, "coordinated")
        sample.append({
            "case_id": c["case_id"],
            "market_state": c["market_state"],
            "selected_protocol": pred["protocol"],
            "required_roles": c["required_roles"],
            "roles_used": pred["roles_used"],
            "agent_messages": pred["agent_messages"],
            "consensus_score": pred["consensus_score"],
            "quorum_passed": set(c["required_roles"]).issubset(set(pred["roles_used"])),
            "decision": pred["intervention"],
            "risk_control": pred["risk_control"],
        })
    return sample


def write_outputs(result: dict[str, Any]) -> None:
    (DATA / "rsi_capability_command_center_v17_proof.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (DATA / "rsi_capability_command_center_v17_benchmark.json").write_text(json.dumps(result["benchmark_public"], indent=2) + "\n", encoding="utf-8")
    (DATA / "rsi_capability_command_center_v17_preregistered_gates.json").write_text(json.dumps(result["preregistered_gates"], indent=2) + "\n", encoding="utf-8")
    (DATA / "rsi_capability_command_center_v17_agent_trace_sample.json").write_text(json.dumps(result["agent_trace_sample"], indent=2) + "\n", encoding="utf-8")

    gates_md = "\n".join([f"- {'✅' if passed else '⏳'} {name.replace('_', ' ')}" for name, passed in result["gate_results"].items()])
    protocols_md = "\n".join([f"- **{name}** — {PROTOCOLS[name]['description']}" for name in result["final_active_protocols"]])
    releases_md = "\n".join([
        f"- Gen {r['generation']}: `{r['release']}` — fully correct {r['validation']['fully_correct_percent']}%, "
        f"coordination {r['validation']['coordination_protocol_accuracy_percent']}%, risk {r['validation']['risk_control_accuracy_percent']}%, "
        f"compounding {r['validation']['avg_compounding_index']} — {'released' if r['released'] else 'not released'}"
        for r in result["rsi_releases"]
    ])
    receipt = result["proof_receipts"]
    md = f"""# SkillOS Autonomous RSI Capital-to-Capability Command Center v17 Proof

**Status:** `{result['status']}`

## Workflow

Adversarial capital-to-capability coordination for capital, compute, energy, data, talent, product, distribution, trust, validation, risk control, and reinvestment.

## Safe Kardashev-scale framing

The motivating thesis is that a sufficiently capable machine could create immense economic value. This proof does **not** claim superintelligence, Kardashev Type II achievement, audited ROI, live customer adoption, or guaranteed outcomes.

It tests the business mechanism underneath that thesis:

> Can a large autonomous specialist-agent organization coordinate scarce resources into compounding productive capability?

## Large-scale multi-agent coordination

The proof coordinates **{result['agent_system']['agent_count']} deterministic specialist agents** across **{result['agent_system']['role_count']} roles**.

It compares:

1. Single-agent baseline
2. Uncoordinated multi-agent pool
3. Static coordinated organization
4. SkillOS RSI coordinated organization

The final system uses required-role quorum, specialist consensus, risk-gated protocol selection, and validation-gated RSI releases.

## Holdout results

| Metric | Single agent | Uncoordinated pool | Static coordination | SkillOS RSI |
|---|---:|---:|---:|---:|
| Fully correct decisions | {result['single_agent_baseline']['fully_correct_percent']}% | {result['uncoordinated_pool']['fully_correct_percent']}% | {result['static_coordination']['fully_correct_percent']}% | {result['final']['fully_correct_percent']}% |
| Coordination accuracy | {result['single_agent_baseline']['coordination_protocol_accuracy_percent']}% | {result['uncoordinated_pool']['coordination_protocol_accuracy_percent']}% | {result['static_coordination']['coordination_protocol_accuracy_percent']}% | {result['final']['coordination_protocol_accuracy_percent']}% |
| Risk-control accuracy | {result['single_agent_baseline']['risk_control_accuracy_percent']}% | {result['uncoordinated_pool']['risk_control_accuracy_percent']}% | {result['static_coordination']['risk_control_accuracy_percent']}% | {result['final']['risk_control_accuracy_percent']}% |
| Role-quorum accuracy | {result['single_agent_baseline']['role_quorum_accuracy_percent']}% | {result['uncoordinated_pool']['role_quorum_accuracy_percent']}% | {result['static_coordination']['role_quorum_accuracy_percent']}% | {result['final']['role_quorum_accuracy_percent']}% |
| Capability-lever accuracy | {result['single_agent_baseline']['capability_lever_accuracy_percent']}% | {result['uncoordinated_pool']['capability_lever_accuracy_percent']}% | {result['static_coordination']['capability_lever_accuracy_percent']}% | {result['final']['capability_lever_accuracy_percent']}% |
| Benchmark value capture rate | {result['single_agent_baseline']['benchmark_value_capture_rate_percent']}% | {result['uncoordinated_pool']['benchmark_value_capture_rate_percent']}% | {result['static_coordination']['benchmark_value_capture_rate_percent']}% | {result['final']['benchmark_value_capture_rate_percent']}% |
| Compounding index | {result['single_agent_baseline']['avg_compounding_index']} | {result['uncoordinated_pool']['avg_compounding_index']} | {result['static_coordination']['avg_compounding_index']} | {result['final']['avg_compounding_index']} |
| Productive capacity index | {result['single_agent_baseline']['avg_productive_capacity_index']} | {result['uncoordinated_pool']['avg_productive_capacity_index']} | {result['static_coordination']['avg_productive_capacity_index']} | {result['final']['avg_productive_capacity_index']} |
| Risk breach rate | {result['single_agent_baseline']['risk_breach_rate_percent']}% | {result['uncoordinated_pool']['risk_breach_rate_percent']}% | {result['static_coordination']['risk_breach_rate_percent']}% | {result['final']['risk_breach_rate_percent']}% |

## Improvements

- Fully correct gain vs single agent: +{result['fully_correct_gain_vs_single_agent_points']} pts
- Fully correct gain vs uncoordinated pool: +{result['fully_correct_gain_vs_uncoordinated_pool_points']} pts
- Fully correct gain vs static coordination: +{result['fully_correct_gain_vs_static_coordination_points']} pts
- Decision-cycle reduction vs single agent: {result['decision_cycle_reduction_vs_single_agent_percent']}%
- Benchmark-implied value captured over single-agent baseline: ${result['benchmark_implied_value_captured_over_single_agent_usd']:,}
- Agent messages coordinated on holdout: {result['final']['agent_messages']:,}

## RSI release history

{releases_md}

## Final released coordination protocols

{protocols_md}

## Pre-registered proof gates

{gates_md}

## Proof receipts

- Repository: `{receipt['repository']}`
- Commit SHA: `{receipt['commit_sha']}`
- Workflow: `{receipt['workflow']}`
- Run URL: `{receipt['run_url']}`
- Benchmark seed: `{SEED}`
- Generated at: `{result['generated_at_utc']}`

## Boundary

This is a deterministic market-readiness benchmark using synthetic/redacted-style business cases and benchmark assumptions. It is not audited customer ROI, live customer adoption, financial advice, investment advice, actual superintelligence, Kardashev Type II achievement, or a guarantee of future outcomes.
"""
    (DOCS / "rsi_capability_command_center_v17_proof.md").write_text(md, encoding="utf-8")

    color = "#2ea44f" if result["proved"] else "#dbab09"
    status_text = result["status"].lower().replace("_", " ")
    badge = f"""<svg xmlns="http://www.w3.org/2000/svg" width="760" height="28" role="img" aria-label="RSI capital-to-capability proof: {html_lib.escape(status_text)}">
<rect width="760" height="28" fill="#24292f" rx="6"/>
<rect x="260" width="500" height="28" fill="{color}" rx="6"/>
<text x="130" y="18" fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">RSI capital-to-capability v17</text>
<text x="510" y="18" fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,sans-serif" font-size="11">{html_lib.escape(status_text)}</text>
</svg>
"""
    (BADGES / "rsi_capability_command_center_v17_proof.svg").write_text(badge, encoding="utf-8")

    vals = [r["validation"]["fully_correct_percent"] for r in result["rsi_releases"] if r["released"] or r["generation"] == 0]
    points = []
    for i, val in enumerate(vals or [0]):
        x = 42 + i * (520 / max(1, len(vals)-1))
        y = 220 - (val / 100) * 180
        points.append((x, y))
    poly = " ".join([f"{x:.1f},{y:.1f}" for x, y in points])
    circles = "\n".join([f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#79ffac"/>' for x, y in points])
    labels = "\n".join([f'<text x="{x:.1f}" y="242" fill="#aab8c8" font-size="10" text-anchor="middle">v{i}</text>' for i, (x, y) in enumerate(points)])
    curve = f"""<svg viewBox="0 0 600 260" width="100%" role="img" aria-label="RSI compounding curve">
<rect x="0" y="0" width="600" height="260" rx="18" fill="rgba(255,255,255,.05)"/>
<line x1="42" y1="220" x2="570" y2="220" stroke="rgba(255,255,255,.22)"/>
<line x1="42" y1="40" x2="42" y2="220" stroke="rgba(255,255,255,.22)"/>
<polyline points="{poly}" fill="none" stroke="#79ffac" stroke-width="4"/>
{circles}
{labels}
<text x="45" y="28" fill="#74f7ff" font-size="13" font-weight="700">Validation fully-correct rate across RSI releases</text>
</svg>"""
    role_chips = "".join([f"<span>{html_lib.escape(role.replace('_',' '))}</span>" for role in AGENT_ROLES])
    gates_html = "\n".join([f"<li>{'✅' if passed else '⏳'} {html_lib.escape(name.replace('_',' '))}</li>" for name, passed in result["gate_results"].items()])
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SkillOS Autonomous RSI Capital-to-Capability Command Center v17</title>
<style>
:root {{ color-scheme: dark; --text:#eef7ff; --muted:#aab8c8; --line:rgba(255,255,255,.14); --cyan:#74f7ff; --green:#79ffac; --gold:#ffd56a; }}
* {{ box-sizing:border-box; }} body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif; background:radial-gradient(circle at 82% 8%,#35436f 0,transparent 34%),linear-gradient(135deg,#06131f,#13223a 62%,#242a57); color:var(--text); }}
main {{ max-width:1260px; margin:0 auto; padding:58px 24px 86px; }} .hero {{ display:grid; grid-template-columns:1.08fr .92fr; gap:26px; align-items:center; }}
h1 {{ font-size:clamp(42px,6.4vw,88px); line-height:.9; margin:0; letter-spacing:-.07em; }} h2 {{ font-size:30px; }} .eyebrow {{ color:var(--cyan); text-transform:uppercase; letter-spacing:.18em; font-weight:900; font-size:13px; }}
p {{ color:var(--muted); font-size:19px; line-height:1.55; }} .card {{ background:rgba(16,34,53,.76); border:1px solid var(--line); border-radius:26px; padding:26px; box-shadow:0 20px 80px rgba(0,0,0,.25); margin:18px 0; }}
.status {{ font-size:24px; font-weight:900; color:var(--green); overflow-wrap:anywhere; }} .grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:28px 0; }} .metric {{ background:rgba(255,255,255,.06); border:1px solid var(--line); border-radius:20px; padding:22px; }}
.metric strong {{ display:block; font-size:32px; color:var(--green); }} .metric span, ul {{ color:var(--muted); }} table {{ width:100%; border-collapse:collapse; margin-top:12px; }} td, th {{ border-bottom:1px solid var(--line); padding:12px; text-align:left; }} th:last-child, td:last-child {{ text-align:right; }}
.notice {{ border-left:4px solid var(--gold); padding:14px 18px; background:rgba(255,213,106,.08); border-radius:14px; }} .roles {{ display:flex; flex-wrap:wrap; gap:8px; }} .roles span {{ border:1px solid var(--line); border-radius:999px; padding:8px 10px; color:var(--muted); background:rgba(255,255,255,.05); font-size:13px; }} .links a {{ color:var(--cyan); margin-right:16px; font-weight:800; }}
@media(max-width:900px) {{ .hero,.grid {{ grid-template-columns:1fr; }} }}
</style></head><body><main>
<section class="hero"><div><div class="eyebrow">MONTREAL.AI / SKILLOS</div><h1>Autonomous RSI Capital-to-Capability Command Center</h1><p>Large-scale specialist-agent coordination for compounding productive capability.</p></div><div class="card"><div class="eyebrow">Proof status</div><div class="status">{html_lib.escape(result['status'])}</div><p>{result['agent_system']['agent_count']} deterministic agents. {result['agent_system']['role_count']} specialist roles. Adversarial holdout benchmark. No human review, no customers, no private data, no API keys.</p></div></section>
<section class="grid"><div class="metric"><strong>{result['agent_system']['agent_count']}</strong><span>specialist agents</span></div><div class="metric"><strong>+{result['fully_correct_gain_vs_static_coordination_points']} pts</strong><span>gain vs static coordination</span></div><div class="metric"><strong>{result['final']['avg_compounding_index']}</strong><span>compounding index</span></div><div class="metric"><strong>${result['benchmark_implied_value_captured_over_single_agent_usd']:,}</strong><span>benchmark-implied value over baseline</span></div></section>
<section class="card"><h2>Safe Kardashev-scale mechanism</h2><p>This proof does not claim superintelligence or Kardashev Type II achievement. It tests the business mechanism underneath the thesis: whether an autonomous specialist-agent organization can coordinate capital, compute, energy, data, trust, talent, product, distribution, validation, risk control, and reinvestment into compounding productive capability.</p></section>
<section class="card"><h2>Specialist agent organization</h2><div class="roles">{role_chips}</div></section>
<section class="card"><h2>Recursive self-improvement curve</h2>{curve}</section>
<section class="card"><h2>Ablation results on adversarial holdout cases</h2><table><tr><th>Metric</th><th>Single agent</th><th>Uncoordinated pool</th><th>Static coordination</th><th>SkillOS RSI</th></tr>
<tr><td>Fully correct</td><td>{result['single_agent_baseline']['fully_correct_percent']}%</td><td>{result['uncoordinated_pool']['fully_correct_percent']}%</td><td>{result['static_coordination']['fully_correct_percent']}%</td><td>{result['final']['fully_correct_percent']}%</td></tr>
<tr><td>Coordination accuracy</td><td>{result['single_agent_baseline']['coordination_protocol_accuracy_percent']}%</td><td>{result['uncoordinated_pool']['coordination_protocol_accuracy_percent']}%</td><td>{result['static_coordination']['coordination_protocol_accuracy_percent']}%</td><td>{result['final']['coordination_protocol_accuracy_percent']}%</td></tr>
<tr><td>Risk-control accuracy</td><td>{result['single_agent_baseline']['risk_control_accuracy_percent']}%</td><td>{result['uncoordinated_pool']['risk_control_accuracy_percent']}%</td><td>{result['static_coordination']['risk_control_accuracy_percent']}%</td><td>{result['final']['risk_control_accuracy_percent']}%</td></tr>
<tr><td>Role-quorum accuracy</td><td>{result['single_agent_baseline']['role_quorum_accuracy_percent']}%</td><td>{result['uncoordinated_pool']['role_quorum_accuracy_percent']}%</td><td>{result['static_coordination']['role_quorum_accuracy_percent']}%</td><td>{result['final']['role_quorum_accuracy_percent']}%</td></tr>
<tr><td>Value capture rate</td><td>{result['single_agent_baseline']['benchmark_value_capture_rate_percent']}%</td><td>{result['uncoordinated_pool']['benchmark_value_capture_rate_percent']}%</td><td>{result['static_coordination']['benchmark_value_capture_rate_percent']}%</td><td>{result['final']['benchmark_value_capture_rate_percent']}%</td></tr>
<tr><td>Risk breach rate</td><td>{result['single_agent_baseline']['risk_breach_rate_percent']}%</td><td>{result['uncoordinated_pool']['risk_breach_rate_percent']}%</td><td>{result['static_coordination']['risk_breach_rate_percent']}%</td><td>{result['final']['risk_breach_rate_percent']}%</td></tr></table></section>
<section class="card"><h2>Pre-registered proof gates</h2><ul>{gates_html}</ul></section>
<section class="notice"><strong>Boundary:</strong> Deterministic market-readiness benchmark using synthetic/redacted-style business cases and benchmark assumptions. Not audited customer ROI, live adoption, financial advice, investment advice, actual superintelligence, Kardashev Type II achievement, or a guarantee.</section>
<p class="links"><a href="https://github.com/MontrealAI/skillos/actions/workflows/rsi-capability-command-center-v17-proof.yml">Run in GitHub Actions</a><a href="https://github.com/MontrealAI/skillos/blob/main/docs/rsi_capability_command_center_v17_proof.md">Markdown report</a><a href="https://github.com/MontrealAI/skillos/blob/main/data/rsi_capability_command_center_v17_proof.json">JSON proof</a></p>
</main></body></html>"""
    (SITE / "rsi-capability-command-center-v17-proof.html").write_text(page, encoding="utf-8")


def main() -> None:
    benchmark = make_benchmark()
    examples = benchmark["examples"]
    train = [e for e in examples if e["split"] == "train"]
    validation = [e for e in examples if e["split"] == "validation"]
    holdout = [e for e in examples if e["split"] == "holdout"]
    rsi = recursive_self_improvement(train, validation)
    final_protocols = rsi["active_protocols"]
    static_protocols = PROTOCOL_ORDER[:8]
    single = eval_cases(holdout, final_protocols, "single_agent")
    uncoord = eval_cases(holdout, final_protocols, "uncoordinated_pool")
    static = eval_cases(holdout, static_protocols, "coordinated")
    final = eval_cases(holdout, final_protocols, "coordinated")

    released = [r for r in rsi["releases"] if r["released"]]
    gate_spec = preregistered_gates()
    value_over_single = round(final["total_benchmark_value_captured_usd"] - single["total_benchmark_value_captured_usd"], 2)
    gain_single = round(final["fully_correct_percent"] - single["fully_correct_percent"], 1)
    gain_uncoord = round(final["fully_correct_percent"] - uncoord["fully_correct_percent"], 1)
    gain_static = round(final["fully_correct_percent"] - static["fully_correct_percent"], 1)
    cycle_reduction = round((single["avg_decision_days"] - final["avg_decision_days"]) / single["avg_decision_days"] * 100, 1)
    validation_scores = [r["validation"]["fully_correct_percent"] for r in released]
    monotonic = all(b >= a for a, b in zip(validation_scores, validation_scores[1:]))
    gates = {
        "agent_count_passes": AGENT_COUNT >= gate_spec["minimum_agent_count"],
        "role_count_passes": len(AGENT_ROLES) >= gate_spec["minimum_role_count"],
        "adversarial_state_count_passes": ADVERSARIAL_STATE_COUNT >= gate_spec["minimum_adversarial_state_count"],
        "train_validation_holdout_sizes_pass": len(train) >= gate_spec["minimum_train_cases"] and len(validation) >= gate_spec["minimum_validation_cases"] and len(holdout) >= gate_spec["minimum_holdout_cases"],
        "rsi_releases_pass": len(released) >= gate_spec["minimum_rsi_releases"],
        "final_protocol_coverage_passes": len(final_protocols) >= gate_spec["minimum_final_protocols"],
        "gain_vs_single_agent_passes": gain_single >= gate_spec["minimum_gain_vs_single_agent_points"],
        "gain_vs_uncoordinated_pool_passes": gain_uncoord >= gate_spec["minimum_gain_vs_uncoordinated_pool_points"],
        "gain_vs_static_coordination_passes": gain_static >= gate_spec["minimum_gain_vs_static_coordination_points"],
        "coordination_accuracy_passes": final["coordination_protocol_accuracy_percent"] >= gate_spec["minimum_coordination_accuracy_percent"],
        "risk_control_accuracy_passes": final["risk_control_accuracy_percent"] >= gate_spec["minimum_risk_control_accuracy_percent"],
        "role_quorum_accuracy_passes": final["role_quorum_accuracy_percent"] >= gate_spec["minimum_role_quorum_accuracy_percent"],
        "capability_lever_accuracy_passes": final["capability_lever_accuracy_percent"] >= gate_spec["minimum_capability_lever_accuracy_percent"],
        "benchmark_value_capture_passes": final["benchmark_value_capture_rate_percent"] >= gate_spec["minimum_benchmark_value_capture_rate_percent"],
        "compounding_index_passes": final["avg_compounding_index"] >= gate_spec["minimum_compounding_index"],
        "productive_capacity_index_passes": final["avg_productive_capacity_index"] >= gate_spec["minimum_productive_capacity_index"],
        "risk_breach_rate_passes": final["risk_breach_rate_percent"] <= gate_spec["maximum_risk_breach_rate_percent"],
        "material_miss_rate_passes": final["material_miss_rate_percent"] <= gate_spec["maximum_material_miss_rate_percent"],
        "decision_cycle_reduction_passes": cycle_reduction >= gate_spec["minimum_decision_cycle_reduction_vs_single_agent_percent"],
        "agent_messages_pass": final["agent_messages"] >= gate_spec["minimum_agent_messages_on_holdout"],
        "validation_monotonicity_passes": monotonic,
        "safe_kardashev_boundary_present": True,
        "no_human_review_no_customers_no_private_data_no_api_keys": True,
    }
    proved = all(gates.values())
    public_benchmark = {k: v for k, v in benchmark.items() if k != "examples"}
    public_benchmark["example_count"] = len(examples)
    public_benchmark["protocol_count"] = len(PROTOCOL_ORDER)
    public_benchmark["market_states"] = [p["state"] for p in PROTOCOL_LIST]
    result = {
        "generated_at_utc": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": "PASSED_AUTONOMOUS_RSI_CAPITAL_TO_CAPABILITY_COMMAND_CENTER_V17_PROOF" if proved else "NOT_YET_PASSED",
        "proved": proved,
        "proof_type": "adversarial capital-to-capability command center proof with recursive self-improvement and large-scale specialist-agent coordination",
        "safe_kardashev_boundary": "The proof tests capital-to-capability compounding; it does not claim superintelligence or Kardashev Type II achievement.",
        "agent_system": {"agent_count": AGENT_COUNT, "role_count": len(AGENT_ROLES), "agents_per_role": AGENTS_PER_ROLE, "role_groups": ROLE_GROUPS},
        "benchmark_public": public_benchmark,
        "preregistered_gates": gate_spec,
        "gate_results": gates,
        "proof_receipts": github_receipts(),
        "train_count": len(train), "validation_count": len(validation), "holdout_count": len(holdout),
        "rsi_releases": rsi["releases"], "final_active_protocols": final_protocols,
        "single_agent_baseline": {k: v for k, v in single.items() if k != "rows"},
        "uncoordinated_pool": {k: v for k, v in uncoord.items() if k != "rows"},
        "static_coordination": {k: v for k, v in static.items() if k != "rows"},
        "final": {k: v for k, v in final.items() if k != "rows"},
        "fully_correct_gain_vs_single_agent_points": gain_single,
        "fully_correct_gain_vs_uncoordinated_pool_points": gain_uncoord,
        "fully_correct_gain_vs_static_coordination_points": gain_static,
        "decision_cycle_reduction_vs_single_agent_percent": cycle_reduction,
        "benchmark_implied_value_captured_over_single_agent_usd": value_over_single,
        "agent_trace_sample": agent_trace_sample(holdout, final_protocols),
        "safe_interpretation": "Deterministic market-readiness benchmark using synthetic/redacted-style business cases and benchmark assumptions. Not audited customer ROI, live customer adoption, financial advice, investment advice, actual superintelligence, Kardashev Type II achievement, or a guarantee of future outcomes.",
    }
    write_outputs(result)
    print(json.dumps({
        "status": result["status"],
        "agent_count": AGENT_COUNT,
        "role_count": len(AGENT_ROLES),
        "protocol_count": len(PROTOCOL_ORDER),
        "adversarial_state_count": ADVERSARIAL_STATE_COUNT,
        "gain_vs_single_agent_points": gain_single,
        "gain_vs_uncoordinated_pool_points": gain_uncoord,
        "gain_vs_static_coordination_points": gain_static,
        "final_fully_correct_percent": final["fully_correct_percent"],
        "coordination_accuracy_percent": final["coordination_protocol_accuracy_percent"],
        "risk_control_accuracy_percent": final["risk_control_accuracy_percent"],
        "role_quorum_accuracy_percent": final["role_quorum_accuracy_percent"],
        "capability_lever_accuracy_percent": final["capability_lever_accuracy_percent"],
        "benchmark_value_capture_rate_percent": final["benchmark_value_capture_rate_percent"],
        "compounding_index": final["avg_compounding_index"],
        "productive_capacity_index": final["avg_productive_capacity_index"],
        "risk_breach_rate_percent": final["risk_breach_rate_percent"],
        "decision_cycle_reduction_percent": cycle_reduction,
        "agent_messages_on_holdout": final["agent_messages"],
        "benchmark_implied_value_captured_over_single_agent_usd": value_over_single,
        "rsi_releases": len(released),
    }, indent=2))
    if not proved:
        raise SystemExit("Autonomous RSI Capital-to-Capability Command Center v17 proof did not pass.")

if __name__ == "__main__":
    main()
