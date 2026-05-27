# Demo Walkthrough

Run:

```bash
python -m skillos.cli demo
```

## What happens

### 1. Seed

SkillOS creates:

- Sales Agent
- Finance Agent
- Research Agent
- Sales Follow-Up Email skill
- Invoice Reconciliation skill
- Research Summary skill

### 2. Work

The Sales Agent drafts several follow-up emails.

### 3. Feedback

Each job includes the same human edit signal:

```text
Moved the next step to the opening lines.
```

### 4. Learn

The Learning Engine discovers a lesson:

```text
Put the agreed next step in the first three lines of the email.
```

### 5. Train

The Skill Trainer creates a candidate skill version.

### 6. Test

The Test Lab compares the candidate against the baseline.

### 7. Release

If the candidate wins and passes safety checks, the Release Center publishes it with a rollback version.

## Expected outcome

```text
Candidate score: 0.92
Baseline score: 0.74
Recommendation: approve_canary
Release: v1 → v2
```


## v3 wealth proof

This repository now includes `scripts/prove_wealth_loop.py`, `skillos/wealth_proof.py`, and `data/wealth_proof.json`. The proof uses the sales follow-up workflow to verify that each completed job creates a tested release and that the workflow gets cheaper, faster, and better after every release. The GitHub Pages deploy refuses to publish if the monotonic economic checks fail.
