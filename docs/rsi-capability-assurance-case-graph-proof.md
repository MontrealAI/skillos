# Autonomous RSI Capability Assurance Case Graph Proof

Generated: `2026-06-01T03:45:45Z`

## Thesis

SkillOS tests whether verified skills can become audit-ready assurance cases.

Core mechanism:

> capability claim → evidence packet → control coverage → verifier independence → red-team challenge → residual-risk disclosure → release gate → public assurance receipt

## Final locked holdout result

- Value capture: **97.6571%**
- Minimum domain capture: **94.1398%**
- Frontier-correct rate: **70.752%**
- Assurance gap rate: **0.0%**
- Risk breach rate: **0.0%**
- Evidence quality score: **58.4301%**
- Control coverage score: **61.1722%**
- Verifier independence score: **75.7215%**
- Audit readiness score: **58.0494%**
- Benchmark value at stake: **$11.65T**
- Benchmark value captured: **$11.37T**
- Strongest safe control: **local_audit_silos**
- Gain over strongest safe control: **$230.21B**

## Skills used

- **Assurance Claim Decomposition** (Assurance): Breaks broad capability claims into testable subclaims.
- **Evidence Packet Assembly** (Evidence): Builds auditable evidence packets from traces, receipts, metrics, and verifier decisions.
- **Control Coverage Mapping** (Controls): Maps every material risk to a control, owner, verifier, and residual-risk score.
- **Trace Replay Verification** (Verification): Checks that claimed outcomes can be replayed from deterministic receipts.
- **Provenance Integrity Check** (Trust): Validates the origin and chain of skill, evidence, and release artifacts.
- **Verifier Independence Scoring** (Verification): Scores whether verifier decisions are sufficiently separated from the generator.
- **Residual Risk Quantification** (Safety): Quantifies residual risk after controls, rollbacks, and evidence review.
- **Red-Team Challenge Routing** (Adversarial): Routes each assurance case through adversarial challenge panels.
- **Policy Boundary Extraction** (Governance): Extracts what the proof does and does not claim, preventing unsafe overstatement.
- **SLA Evidence Binding** (Reliability): Binds SLA performance metrics to evidence nodes and control owners.
- **Counterfactual Coverage Test** (Causality): Checks that causal lift claims are supported by controls and counterfactual cells.
- **Release Gate Assurance** (RSI): Promotes only assurance updates that improve evidence quality without hiding risk.
- **Audit Readiness Scoring** (Assurance): Scores whether an executive or external reviewer can understand and rerun the proof.
- **Disclosure Quality Audit** (Credibility): Ensures all public claims use benchmark-safe language and clear boundaries.
- **Control Gap Mining** (Compounding): Turns failed checks and weak controls into new skill and verifier capacity requests.
- **Verifier Capacity Allocation** (Operations): Allocates verifier courts to the highest-value and highest-risk assurance cases.
- **Executive Evidence Rendering** (Communication): Renders assurance claims, controls, evidence, risks, and skills into a readable public page.
- **Registry Publication** (Publication): Publishes proof page, receipt, report, badge, registry entry, sitemap, and robots file.

## Baselines and controls

| System | Value capture | Assurance gap | Risk breach | Invalid action |
|---|---:|---:|---:|---:|
| single_assurance_writer | 73.8757% | 11.2793% | 0.4883% | 1.0742% |
| static_checklist | 76.2417% | 9.7656% | 0.3418% | 0.7812% |
| local_audit_silos | 95.6805% | 0.0% | 0.0% | 0.0% |
| paper_compliance_theater | 93.8617% | 2.6855% | 0.0% | 0.4395% |
| risk_blind_release | 92.7661% | 2.9785% | 0.0488% | 0.6836% |

## Pre-registered gates

- ✅ `large_assurance_case_graph`
- ✅ `locked_holdout_scale`
- ✅ `domain_coverage`
- ✅ `skills_catalog_present`
- ✅ `rsi_release_count`
- ✅ `value_capture_threshold`
- ✅ `minimum_domain_capture_threshold`
- ✅ `assurance_gap_zero`
- ✅ `risk_breach_zero`
- ✅ `unauthorized_action_zero`
- ✅ `beats_static_checklist`
- ✅ `beats_local_audit_silos`
- ✅ `rejects_paper_compliance_theater`
- ✅ `rejects_risk_blind_release`
- ✅ `bootstrap_p05_vs_strongest_safe_control_positive`

## Boundary

Benchmark-capital-equivalent values are not live revenue, customer results, financial guarantees, legal advice, audit certification, policy advice, token advice, medical advice, or proof of achieved superintelligence.
