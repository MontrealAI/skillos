# SkillOS Public Command Center Root Authority v7

This pack fixes the root contract permanently:

```text
/skillos/           = Public SkillOS Command Center
/skillos/index.html = Public SkillOS Command Center
/skillos/capability-governance-twin.html = flagship proof subpage
```

## Why this pack exists

A previous flagship deployment could replace the root with the Capability Governance Twin page. That is the wrong public shape. The root must always be the full Command Center.

## Important design decision

This pack does not rely on pre-made HTML files as source.

The canonical workflow builds a fresh `dist/` artifact from repository evidence at run time:

```text
proof JSON receipts
Markdown reports
badges
workflow metadata
skills metadata
proof registry entries
```

Then it verifies the artifact, uploads it to GitHub Pages, deploys it, and live-checks `/skillos/` and `/skillos/index.html`.

## Recommended run

```text
GitHub → Actions → Public SkillOS Command Center Root Authority v7 → Run workflow
```

Inputs:

```text
deploy_pages: true
verify_live: true
cancel_legacy_runs: true
```

## Success criteria

```text
https://montrealai.github.io/skillos/
https://montrealai.github.io/skillos/index.html
```

both show `Public SkillOS Command Center`, not a single proof page.

The manifest should show:

```text
schema: skillos.public_command_center.root_authority.v7
marker: SKILLOS_PUBLIC_COMMAND_CENTER_V7_ROOT_AUTHORITY
```
