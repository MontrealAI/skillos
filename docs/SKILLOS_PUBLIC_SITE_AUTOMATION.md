# SkillOS Public Proof Command Center Automation v2

This automation turns `https://montrealai.github.io/skillos/` into a living public proof command center.

## What it does

It scans:

- GitHub Actions workflow files
- latest GitHub Actions runs
- proof HTML pages
- proof Markdown reports
- proof JSON receipts
- generated badges and site files

It regenerates:

- `site/index.html`
- `site/proofs.html`
- `site/actions.html`
- `site/multi-agent.html`
- `site/runbook.html`
- `site/public_site_status.json`
- `data/public_site_status.json`
- `docs/SKILLOS_PUBLIC_SITE_STATUS.md`

## What viewers see

The public website makes the proof system user-friendly:

- flagship multi-agent proof
- proof library
- workflow status board
- run/regenerate instructions
- proof receipts
- safe public boundaries

## Flagship posture

The site spotlights the large-scale multi-agent RSI capability proof:

> capital → compute → energy → data → trust → talent → product → distribution → validation → risk control → reinvestment → compounding productive capability

It does **not** claim superintelligence or Kardashev Type II achievement. It tests the business mechanism underneath that thesis.

## Autonomy

The refresh workflow runs on:

- manual dispatch
- hourly schedule
- relevant pushes
- known proof workflow completions

For future proof workflows, include `Proof` or `RSI` in the workflow name and generate:

- visual HTML into `site/`
- report Markdown into `docs/`
- proof JSON into `data/`

The command center discovers them automatically.

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
Add autonomous SkillOS public proof command center
```

Workflow files:

```text
Add autonomous SkillOS public proof command center workflows
```

## Run

```text
GitHub → Actions → SkillOS Public Proof Command Center Refresh → Run workflow
```
