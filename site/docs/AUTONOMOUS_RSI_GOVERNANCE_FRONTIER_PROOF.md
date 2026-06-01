# Autonomous RSI Governance Frontier Proof

This package adds a public GitHub Action proof that tests whether an AI-first institution can recursively improve its own governance coordination layer.

## Core thesis

SkillOS tests a governance-to-capability loop:

> judgment → evidence → role quorum → incentive design → policy → permissions → capital allocation → execution → audit → measurement → risk courts → reinvestment → compounding institutional capability

The proof is designed for the AI-first corporate and governance domain. It is not an email example, not a toy demo, and not a claim of live deployment. It is a deterministic, public, reproducible benchmark that anyone can run from GitHub Actions.

## What the workflow does

1. Runs a locked-holdout governance benchmark.
2. Simulates a large virtual specialist-agent governance lattice.
3. Applies validation-gated Recursive Self-Improvement across releases.
4. Compares SkillOS against a single executive agent, an uncoordinated agent swarm, a static DAO/committee, a no-RSI organization, and random policy control.
5. Runs negative controls that remove risk courts, reinvestment, or role quorum.
6. Verifies proof gates and public-safe wording.
7. Generates JSON receipts, a Markdown report, an SVG badge, an executive proof webpage, and a refreshed SkillOS command center.
8. Commits generated outputs back to the repository.
9. Optionally deploys GitHub Pages directly, or lets the existing Pages workflow deploy after the generated outputs are committed.

## Public-safe boundary

Use this wording:

> SkillOS does not claim achieved superintelligence or Kardashev Type II civilization; it makes the governance-and-capital coordination mechanism underneath that value thesis publicly runnable, measurable, and repeatable.

The proof does not provide legal advice, policy advice, investment advice, live revenue claims, customer-result claims, or financial guarantees.

## Run

```bash
python scripts/run_rsi_governance_frontier_proof.py
python scripts/verify_rsi_governance_frontier_proof.py
python scripts/render_rsi_governance_frontier_site.py
python scripts/publish_rsi_governance_frontier_to_hub.py
python scripts/verify_rsi_governance_frontier_site.py
```

Or run it from GitHub:

```text
GitHub → Actions → Autonomous RSI Governance Frontier Proof → Run workflow
```

Recommended setting:

```text
publish_to_repo: true
deploy_pages: false
```

Use `deploy_pages: true` only if this workflow should deploy GitHub Pages directly. Keeping it false avoids deployment collisions when another repository workflow already publishes the site on push.

## Expected public pages

```text
https://montrealai.github.io/skillos/
https://montrealai.github.io/skillos/rsi-governance-frontier-proof.html
```
