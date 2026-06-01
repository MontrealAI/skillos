# SkillOS Public Proof Command Center Automation v4

This is the pushed-as-far-as-possible public website automation for `https://montrealai.github.io/skillos/`.

## What it creates

A living, visual, GitHub-native command center with:

- homepage
- proof library
- GitHub Actions status board
- multi-agent proof spotlight
- proof receipts page
- proof leaderboard
- capital-to-capability architecture page
- run/regenerate guide
- dynamic self-contained SVG charts
- public status JSON
- generated sitemap, robots, manifest, and OG card

## Dynamic visual system

The site includes dynamic charts generated from `site/public_site_status.json`:

- proof status donut chart
- workflow status donut chart
- RSI release curve
- multi-agent ablation chart
- capability coordination radar
- agent-role constellation
- business-effect metric chart
- proof tables and workflow tables

No external JavaScript libraries are required.

## Flagship thesis

The site centers the large-scale multi-agent RSI capability proof:

> capital → compute → energy → data → trust → talent → product → distribution → validation → risk control → reinvestment → compounding productive capability

It does not claim superintelligence or Kardashev Type II achievement. It makes the mechanism publicly testable.

## Autonomy

The refresh workflow runs on:

- manual dispatch
- hourly schedule
- relevant pushes
- workflow completion events

It scans:

- workflow files
- latest GitHub Action runs
- proof HTML pages
- proof Markdown reports
- proof JSON receipts
- badges and assets

Then it regenerates and deploys the site.

## Upload order

Upload source files first:

```text
docs/SKILLOS_PUBLIC_SITE_AUTOMATION.md
scripts/refresh_public_site.py
scripts/verify_public_site_refresh.py
scripts/run_all_public_proofs.py
```

Then upload workflow files:

```text
.github/workflows/skillos-public-proof-command-center-refresh.yml
.github/workflows/skillos-run-all-public-proofs.yml
.github/workflows/_skillos-public-proof-command-center-refresh-reusable.yml
```

## Commit messages

Source files:

```text
Add autonomous SkillOS visual proof command center
```

Workflow files:

```text
Add autonomous SkillOS visual proof command center workflows
```

## Run

```text
GitHub → Actions → SkillOS Public Proof Command Center Refresh → Run workflow
```
