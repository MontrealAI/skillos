# Proof Gradient · Goal-Plan-Skill Alignment Lattice Proof

This is the second incremental Proof Gradient proof.

It extends the first Proof Gradient proof from proof-gated skill propagation to a full alignment lattice:

```text
GoalOS gives Direction.
PlanOS gives Strategy.
SkillOS gives Capability.
Proof Gradient gives Evolution.
```

## What it proves

The proof compares:

```text
single agent
SkillOS without GoalOS / PlanOS gates
GoalOS + PlanOS + SkillOS static coordination
unverified gradient propagation
Proof Gradient alignment lattice
```

The proof passes only if the full Proof Gradient lattice:

```text
beats static coordination on holdout success
beats static coordination on value capture
beats unverified propagation
stays under the risk breach ceiling
rejects adversarial negative controls
shows goal alignment, plan fidelity, and skill validity
renders goals, plans, and skills beautifully on the webpage
preserves the Public SkillOS Command Center root contract
```

## Root contract

```text
/skillos/                                             = Public SkillOS Command Center
/skillos/index.html                                   = Public SkillOS Command Center
/skillos/proof-gradient-goal-plan-skill-alignment-lattice.html = Proof Gradient proof room
```

The root is the lobby. Proofs are rooms.

## Run

Upload the files in `UPLOAD_TO_GITHUB_SKILLOS/`, then run:

```text
GitHub → Actions → Proof Gradient Goal-Plan-Skill Alignment Lattice Proof → Run workflow
```

Recommended inputs:

```text
deploy_pages: true
verify_live: true
cancel_legacy_runs: true
```
