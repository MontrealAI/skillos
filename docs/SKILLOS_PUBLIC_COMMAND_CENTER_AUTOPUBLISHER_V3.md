# SkillOS Public Command Center Autopublisher v3

This is the elevated public-site autopublisher for the SkillOS proof ecosystem.

It regenerates and directly deploys the live GitHub Pages Command Center from repository evidence:

```text
proof JSON receipts
Markdown proof reports
badges
visual proof pages
GitHub Actions workflows
latest workflow run metadata
Skills Used sections
proof registry
site health
```

## Why v3 exists

A commit-only refresh can update files without necessarily replacing the live site immediately. v3 builds, verifies, commits, and deploys the GitHub Pages artifact in the same workflow run.

## Recommended run settings

```text
publish_to_repo: true
deploy_pages: true
force_rebuild: true
```

## Verify

Open:

```text
https://montrealai.github.io/skillos/data/command-center-manifest.json
```

It should contain:

```text
schema: skillos.command_center.v3
```

Then open:

```text
https://montrealai.github.io/skillos/?v=latest
```

The homepage should say `SkillOS Public Command Center v3`.
