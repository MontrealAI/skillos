# Root Fix v5.1 Runbook

Run:

`GitHub → Actions → SkillOS Sovereign Command Center v5.1 Canonical Deploy → Run workflow`

Inputs:

- `publish_to_repo: true`
- `deploy_pages: true`
- `verify_live: true`
- `cancel_legacy_runs: true`

Verify:

- `https://montrealai.github.io/skillos/data/command-center-manifest.json` contains `skillos.command_center.sovereign.v5.1`
- `https://montrealai.github.io/skillos/?v=sovereign-v5-1` contains `SKILLOS_COMMAND_CENTER_V5_1_CANONICAL_ROOT`
- `https://montrealai.github.io/skillos/index.html?v=sovereign-v5-1` contains `SKILLOS_COMMAND_CENTER_V5_1_CANONICAL_ROOT`
- Neither page contains `Autonomous Proof Command Center`.
