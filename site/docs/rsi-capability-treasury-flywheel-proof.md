# Autonomous RSI Capability Treasury Flywheel Proof

Generated: `2026-06-01T03:30:09Z`

## Thesis

SkillOS tests whether verified capability-market signals can be reinvested into a compounding capability treasury.

Core mechanism:

> proof receipts -> value signals -> treasury allocation -> skill bounties -> verifier capacity -> routing upgrades -> reinvestment -> compounding capability supply

## Final locked holdout result

- Value capture: **97.0953%**
- Minimum domain capture: **96.7831%**
- Frontier-correct rate: **98.2728%**
- Treasury discipline score: **62.7984%**
- Reinvestment yield score: **55.3254%**
- Utilization efficiency score: **59.8972%**
- Verifier capacity score: **65.1014%**
- Moat reinvestment score: **57.3033%**
- Risk breach rate: **0.0%**
- Benchmark value at stake: **$3.99T**
- Benchmark value captured: **$3.87T**
- Strongest safe control: **local_treasury_silos**
- Gain over strongest safe control: **$141.00B**

## Baselines and controls

| System | Value capture | Minimum domain capture | Risk breach | Invalid action |
|---|---:|---:|---:|---:|
| static_budget_committee | 82.6575% | 80.3931% | 2.1% | 3.4% |
| spend_only_growth | 88.1575% | 85.8931% | 4.3% | 6.2% |
| local_treasury_silos | 93.5595% | 92.5331% | 0.0% | 0.0% |
| no_reinvestment_treasury | 92.0595% | 91.0331% | 0.0% | 0.0% |
| unverified_spend | 95.2595% | 94.2331% | 1.8% | 3.1% |

## Pre-registered gates

- PASSED `large_capability_treasury`
- PASSED `locked_holdout_scale`
- PASSED `domain_coverage`
- PASSED `rsi_release_count`
- PASSED `value_capture_threshold`
- PASSED `minimum_domain_capture_threshold`
- PASSED `weak_domain_zero`
- PASSED `risk_breach_zero`
- PASSED `unauthorized_action_zero`
- PASSED `beats_static_budget_committee`
- PASSED `beats_no_reinvestment_treasury`
- PASSED `beats_local_treasury_silos`
- PASSED `rejects_spend_only_growth`
- PASSED `rejects_unverified_spend`
- PASSED `bootstrap_p05_vs_strongest_safe_control_positive`

## Boundary

Benchmark-capital-equivalent values are not live revenue, customer results, financial guarantees, legal advice, policy advice, token advice, or proof of achieved superintelligence.
