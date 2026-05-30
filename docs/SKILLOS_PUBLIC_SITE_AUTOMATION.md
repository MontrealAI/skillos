# SkillOS Public Site Command Center Automation

This pack makes `https://montrealai.github.io/skillos/` a living public proof hub.

It automatically scans:

- GitHub Actions workflows
- latest workflow runs
- generated proof HTML pages
- generated proof JSON receipts
- generated proof Markdown reports
- badges and site assets

It then regenerates:

- `site/index.html`
- `site/proofs.html`
- `site/actions.html`
- `site/runbook.html`
- `site/public_site_status.json`
- `data/public_site_status.json`
- `docs/SKILLOS_PUBLIC_SITE_STATUS.md`

## Public goal

Make the SkillOS site always feel fresh, complete, useful, beautiful, and easy to understand.

The viewer should immediately see:

1. what proofs exist,
2. which ones passed,
3. how to inspect the receipts,
4. how to run or regenerate the proofs,
5. what GitHub Actions recently ran,
6. where the proof boundary is.

## Autonomy

The command center refresh runs on:

- manual dispatch,
- hourly schedule,
- repository pushes that touch workflows/scripts/docs/data/site/badges,
- completion of known proof workflows.

For future workflows, include `Proof` or `RSI` in the workflow name and generate proof outputs into `data/`, `docs/`, and `site/`. The command center will discover them.

## Run all public proofs

The workflow `SkillOS Run All Public Proofs` uses the GitHub Actions workflow dispatch API to dispatch proof workflows. It supports:

- optional filter,
- dry run mode,
- one-place regeneration.

## Safe public boundary

This public site presents autonomous, deterministic market-readiness proofs using synthetic/redacted-style benchmark data.

It does not claim audited customer ROI, live customer adoption, financial advice, investment advice, superintelligence, Kardashev Type II achievement, or guaranteed future outcomes.

## Upload order

Upload the source files first:

```text
docs/SKILLOS_PUBLIC_SITE_AUTOMATION.md
scripts/refresh_public_site.py
scripts/verify_public_site_refresh.py
scripts/run_all_public_proofs.py
```

Then upload the workflows:

```text
.github/workflows/skillos-public-site-refresh.yml
.github/workflows/skillos-run-all-public-proofs.yml
.github/workflows/_skillos-public-site-refresh-reusable.yml
```

## Commit messages

For source files:

```text
Add autonomous SkillOS public proof command center
```

For workflow files:

```text
Add autonomous SkillOS public site refresh workflows
```

## After upload

Run:

```text
GitHub → Actions → SkillOS Public Site Command Center Refresh → Run workflow
```

Then view:

```text
https://montrealai.github.io/skillos/
```
