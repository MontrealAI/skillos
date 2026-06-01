# SkillOS Command Center Autopublisher v2

This package fixes the common reason the public page still looks old:

> A workflow that commits files with `GITHUB_TOKEN` does not reliably trigger a second Pages deployment workflow, and a refresh workflow with `deploy_pages=false` may update the repository without replacing the live GitHub Pages artifact.

This v2 workflow builds, verifies, commits, and deploys the GitHub Pages artifact directly in the same run.

## Recommended manual run

```text
GitHub → Actions → SkillOS Command Center Autopublisher v2 → Run workflow
```

Use:

```text
publish_to_repo: true
deploy_pages: true
force_rebuild: true
```

## Verification

Open:

```text
https://montrealai.github.io/skillos/data/command-center-manifest.json
```

The timestamp should match the latest green run. Then open:

```text
https://montrealai.github.io/skillos/?v=latest
```
