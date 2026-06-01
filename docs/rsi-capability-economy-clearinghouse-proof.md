# Autonomous RSI Capability Economy Clearinghouse Proof

Generated: `2026-06-01T01:48:41Z`

## Thesis

SkillOS tests whether capabilities can become an efficiently cleared economy.

Core mechanism:

> demand → verified skill supply → price discovery → liquidity → settlement trust → routing upgrade → reinvestment → compounding capability economy

## Final locked holdout result

- Value capture: **96.6013%**
- Minimum domain capture: **93.3161%**
- Frontier-correct rate: **60.0586%**
- Clearing liquidity score: **53.5639%**
- Price discovery score: **54.764%**
- Verified quality score: **58.2434%**
- Settlement trust score: **61.1373%**
- Reinvestment compounding score: **53.3541%**
- Risk breach rate: **0.0%**
- Benchmark value at stake: **$7.48T**
- Benchmark value captured: **$7.23T**
- Strongest safe control: **local_silo_markets**
- Gain over strongest safe control: **$90.46B**

## Baselines and controls

| System | Value capture | Minimum domain capture | Risk breach | Invalid action |
|---|---:|---:|---:|---:|
| single_buyer_agent | 80.6461% | 68.3123% | 2.6367% | 5.1758% |
| static_price_book | 83.3368% | 70.5135% | 1.7578% | 3.6133% |
| local_silo_markets | 95.392% | 91.0606% | 0.0% | 0.0% |
| subsidy_market | 91.6237% | 73.0548% | 0.6836% | 4.3457% |
| unverified_clearing | 96.158% | 90.6244% | 0.3418% | 2.3926% |

## Pre-registered gates

- ✅ `large_capability_economy`
- ✅ `locked_holdout_scale`
- ✅ `domain_coverage`
- ✅ `rsi_release_count`
- ✅ `value_capture_threshold`
- ✅ `minimum_domain_capture_threshold`
- ✅ `weak_domain_zero`
- ✅ `risk_breach_zero`
- ✅ `unauthorized_action_zero`
- ✅ `beats_static_price_book`
- ✅ `beats_local_silo_markets`
- ✅ `rejects_subsidy_market`
- ✅ `rejects_unverified_clearing`
- ✅ `bootstrap_p05_vs_strongest_safe_control_positive`

## Boundary

Benchmark-capital-equivalent values are not live revenue, customer results, financial guarantees, legal advice, policy advice, token advice, or proof of achieved superintelligence.
