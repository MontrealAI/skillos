# SkillOS Public Command Center Autopublisher

This patch makes `https://montrealai.github.io/skillos/` regenerate automatically from the repository itself.

## What it does

The GitHub Action scans:

```text
data/*.json
site/data/*.json
docs/*.md
badges/*.svg
site/*.html
.github/workflows/*.yml
.github/workflows/*.yaml
```

Then it rebuilds:

```text
site/index.html
site/proofs.html
site/actions.html
site/data/command-center-manifest.json
site/proof-registry.json
site/sitemap.xml
site/robots.txt
badges/command-center-fresh.svg
site/badges/command-center-fresh.svg
docs/SKILLOS_PUBLIC_COMMAND_CENTER.md
```

## Why it matters

The command center no longer needs manual homepage edits after proof workflows run. When proof outputs are committed, this workflow refreshes the public hub.

## Viewer promise

A non-technical viewer can use the public command center to:

1. see all proof pages,
2. open JSON receipts,
3. understand the Skills Used cards,
4. find GitHub Actions workflows,
5. rerun the proof workflows,
6. see the latest generated proof registry.

## Safe boundary

The command center uses benchmark-safe language. It does not claim live customer results, independent financial-performance claims, financial advice, legal advice, medical advice, token advice, or achieved superintelligence.
