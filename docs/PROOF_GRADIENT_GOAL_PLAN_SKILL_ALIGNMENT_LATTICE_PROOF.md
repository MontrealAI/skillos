# Proof Gradient · Goal-Plan-Skill Alignment Lattice

**Status:** PASSED  
**Generated:** 2026-06-13T06:05:15Z  
**Receipt hash:** `f4dbbc4fb2d293571d7723ee95308b1a3d745868b2f82692ab2956fdfc72e183`

> One agent tries. Proof decides. The network evolves.

GoalOS gives the network Direction.  
PlanOS gives it Strategy.  
SkillOS gives it Capability.  
Proof Gradient gives it Evolution.

## What this incremental proof adds

The first Proof Gradient proof tested proof-gated propagation. This second proof adds the full alignment lattice:

```text
GoalOS direction
→ PlanOS strategy
→ SkillOS capability
→ Proof Gradient evolution
```

## Passed gates

```text
success uplift over static: 19.4%
value uplift over static: 18.9%
risk breach rate: 0.40%
negative-control rejection: 100.0%
goal alignment: 93.1%
plan fidelity: 91.9%
skill validity: 93.9%
```

## Comparison

| Protocol | Holdout success | Value capture | Risk breach | Goal alignment | Plan fidelity | Skill validity |
|---|---:|---:|---:|---:|---:|---:|
| Single agent | 61.2% | 58.7% | 4.70% | 58.0% | 52.0% | 60.0% |
| SkillOS without GoalOS / PlanOS gates | 72.4% | 71.1% | 5.50% | 66.0% | 57.0% | 77.0% |
| GoalOS + PlanOS + SkillOS static | 77.1% | 78.6% | 2.70% | 83.0% | 81.0% | 80.0% |
| Unverified gradient propagation | 74.1% | 75.2% | 6.80% | 62.0% | 59.0% | 70.0% |
| Proof Gradient alignment lattice | 96.5% | 97.5% | 0.40% | 93.1% | 91.9% | 93.9% |

## Skills Used

### Goal Contract Compilation

- **OS:** GoalOS
- **Layer:** Direction
- **Purpose:** Convert high-level objectives into measurable acceptance gates.
- **Input:** mission statement, public claim boundary, desired outcomes
- **Output:** weighted goal contract
- **Verifier:** goal weights sum to 1.0 and each goal has a threshold

### Plan Route Decomposition

- **OS:** PlanOS
- **Layer:** Strategy
- **Purpose:** Turn each goal into a testable route with steps, risk budgets, and dependencies.
- **Input:** goal contract and workflow context
- **Output:** candidate plan route
- **Verifier:** each plan links to goals and contains a risk budget

### Skill Binding

- **OS:** SkillOS
- **Layer:** Capability
- **Purpose:** Bind reusable skills to the goals and plans they are allowed to support.
- **Input:** trace-derived skills, plan routes, policy constraints
- **Output:** goal-plan-skill binding map
- **Verifier:** skill must declare input, output, and verifier

### Attempt Trace Capture

- **OS:** SkillOS
- **Layer:** Observation
- **Purpose:** Record agent work as structured evidence so successful behavior can become reusable.
- **Input:** agent attempt, task, outcome, role, risk signal
- **Output:** provenance-bound trace
- **Verifier:** trace hash and holdout isolation

### Proof-Gated Selection

- **OS:** Proof Gradient
- **Layer:** Evolution
- **Purpose:** Accept only upgrades that improve holdout results while respecting goals, plans, and risk gates.
- **Input:** candidate skill, goal alignment, plan fidelity, holdout result
- **Output:** accept, revise, reject, or retire decision
- **Verifier:** proof score threshold and negative-control rejection

### Gradient Attribution

- **OS:** Proof Gradient
- **Layer:** Selection Signal
- **Purpose:** Compute which goals, plans, and skills contributed to improvement or regression.
- **Input:** release metrics, proof outcomes, risk events
- **Output:** signed evolution gradient
- **Verifier:** gradient sign must match holdout delta

### Network Propagation Control

- **OS:** Proof Gradient
- **Layer:** Routing Upgrade
- **Purpose:** Propagate accepted skills to compatible agents without allowing unverified capability drift.
- **Input:** accepted skill, role map, plan compatibility
- **Output:** network routing upgrade
- **Verifier:** post-propagation holdout and risk check

### Adversarial Goal Injection

- **OS:** Proof Gradient
- **Layer:** Robustness
- **Purpose:** Test whether attractive but goal-inconsistent upgrades are blocked.
- **Input:** poisoned candidates and misleading high-value shortcuts
- **Output:** negative-control rejection receipt
- **Verifier:** adversarial candidates must not propagate

### Capability Governance Twin

- **OS:** SkillOS
- **Layer:** Governed Release
- **Purpose:** Simulate a capability release before it changes live routing.
- **Input:** candidate upgrade, policy boundary, rollback path
- **Output:** governed release decision
- **Verifier:** policy, rollback, permission, and verifier coverage gates

### Executive Evidence Rendering

- **OS:** SkillOS
- **Layer:** Communication
- **Purpose:** Render goals, plans, skills, proof results, and claim boundaries into a viewer-friendly public artifact.
- **Input:** receipt, metrics, goals, plans, skills
- **Output:** webpage, report, badge, manifest
- **Verifier:** link integrity and required-section check


## Public boundary

This benchmark is a reproducible proof artifact. It is not audited customer ROI, financial advice, legal advice, medical advice, employment advice, credit advice, policy advice, token advice, or a claim of achieved superintelligence.
