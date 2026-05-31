# Autonomous RSI Continual Capability Frontier Proof

Generated: `2026-05-31T23:19:17Z`

## Thesis

SkillOS tests whether recursive self-improvement can continue under distribution shift without catastrophic forgetting.

## Final locked holdout result

- Value capture: **96.652%**
- Minimum regime value capture: **95.0635%**
- Frontier-correct rate: **61.3932%**
- Catastrophic forgetting rate: **0.0%**
- Risk breach rate: **0.0%**
- Unauthorized action rate: **0.0%**
- Benchmark value at stake: **$1.72T**
- Benchmark value captured: **$1.66T**
- Strongest control: **no_drift_response**
- Gain over strongest control: **$24.39B**

## Baselines and controls

| System | Value capture | Minimum regime capture | Forgetting | Risk breach |
|---|---:|---:|---:|---:|
| single_generalist | 79.0747% | 60.2005% | 75.0% | 2.9297% |
| uncoordinated_agent_pool | 93.6625% | 75.8094% | 8.3333% | 0.5208% |
| static_skill_catalog | 92.2525% | 84.5316% | 8.3333% | 0.0% |
| no_drift_response | 95.2298% | 93.0065% | 0.0% | 0.0% |
| no_replay_rsi | 94.5273% | 74.7735% | 8.3333% | 1.237% |
| shuffled_reward_rsi | 85.1286% | 57.799% | 50.0% | 4.1667% |
| random_protocol | 86.6931% | 80.0927% | 33.3333% | 0.0% |

## Gates

- ✅ `large_specialist_agent_market`
- ✅ `locked_holdout_scale`
- ✅ `multiple_drift_regimes`
- ✅ `rsi_release_count`
- ✅ `value_capture_threshold`
- ✅ `minimum_regime_capture_threshold`
- ✅ `catastrophic_forgetting_zero`
- ✅ `risk_breach_zero`
- ✅ `unauthorized_action_zero`
- ✅ `beats_static_catalog`
- ✅ `beats_no_replay_rsi`
- ✅ `beats_uncoordinated_pool`
- ✅ `bootstrap_p05_vs_strongest_control_positive`

## Boundary

Benchmark-capital-equivalent values are not live revenue, customer results, financial guarantees, legal advice, policy advice, token advice, or proof of achieved superintelligence.
