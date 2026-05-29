# SkillOS Autonomous No-Send Shadow Pilot Proof — PASSED

SkillOS v1.0.0 can be tested without sending emails, contacting customers, or using private data.

This proof runs entirely inside GitHub Actions. It uses a transparent synthetic/redacted benchmark and a deterministic evaluator to test whether SkillOS turns repeated corrections into tested skill rules that improve holdout examples.

> Important: this is a reference workflow proof, not audited customer results, financial advice, a guarantee, or an investment claim.

## Proof loop

`call notes → draft → evaluation trace → lessons → tested skill rules → holdout improvement`

## Results on holdout set

| Metric | Baseline agent | SkillOS learned skill | Improvement |
|---|---:|---:|---:|
| Quality score | 68.1 | 97.9 | +29.8 pts |
| Edit minutes / job | 6.55 | 2.35 | -64.1% |
| Cost / job | $8.26 | $3.02 | -63.4% |
| Accepted rate | 20.0% | 100.0% | +80.0 pts |
| Hallucination rate | 15.0% | 0.0% | zero after learned skill |

## Learned skill rules

1. Carry forward important constraints so the draft stays accurate.
2. Match the requested tone: executive, technical, warm, or concise.
3. Put the agreed next step and date in the first three body paragraphs.
4. Anchor the message in the buyer's stated pain point.
5. Preserve exact dates from call notes instead of using vague timing.
6. Do not invent guarantees, savings, or commitments not present in the notes.

## Proof gates

- ✅ `no_send_mode`
- ✅ `holdout_examples_at_least_15`
- ✅ `learned_at_least_5_skill_rules`
- ✅ `holdout_quality_gain_at_least_15_points`
- ✅ `holdout_edit_time_reduction_at_least_25_percent`
- ✅ `holdout_acceptance_lift_at_least_20_points`
- ✅ `skillos_hallucination_rate_zero`
- ✅ `all_holdout_jobs_improve`

## How to rerun

In GitHub, open **Actions → Autonomous Shadow Pilot Proof** and click **Run workflow**.

Generated outputs:

- `data/shadow_pilot_proof.json`
- `docs/shadow_pilot_proof.md`
- `site/shadow-pilot-proof.html`
- `badges/shadow_pilot_proof.svg`

## Safe interpretation

This proves the mechanism in a no-send reference evaluation. The next step is to repeat the same measurement on private historical call notes or a live shadow workflow, still without sending anything automatically.
