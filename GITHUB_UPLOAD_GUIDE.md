# SkillOS GitHub Web Upload Guide

This guide assumes you are using only the GitHub website.

Target repository:

```text
https://github.com/MontrealAI/skillos
```

Target website:

```text
https://montrealai.github.io/skillos/
```

---

## 1. Create `MontrealAI/skillos`

1. Go to GitHub.
2. Open the `MontrealAI` organization.
3. Click **New repository**.
4. Name it exactly:

```text
skillos
```

5. Set visibility to **Public**.
6. Click **Create repository**.

---

## 2. Upload the repository files

1. Download and unzip the SkillOS package.
2. Open this folder on your computer:

```text
UPLOAD_THE_CONTENTS_OF_THIS_FOLDER_TO_GITHUB
```

3. Select everything inside that folder.
4. In GitHub, click **Add file → Upload files**.
5. Drag the selected files into GitHub.
6. Before committing, look for these important files in the upload list:

```text
README.md
site/index.html
.github/workflows/pages.yml
.github/workflows/tests.yml
scripts/build_pages.py
scripts/verify_repo.py
skillos/cli.py
tests/test_end_to_end.py
```

7. Commit message:

```text
Initial SkillOS implementation
```

8. Choose **Commit directly to the main branch**.
9. Click **Commit changes**.

---

## 3. If the `.github` folder is missing

Some computers hide folders that start with a dot.

If GitHub does not show this file:

```text
.github/workflows/pages.yml
```

create it manually:

1. Click **Add file → Create new file**.
2. In the filename box, paste:

```text
.github/workflows/pages.yml
```

3. Open this package file:

```text
COPY_PASTE_GITHUB_ACTIONS/pages.yml
```

4. Copy all contents and paste into GitHub.
5. Commit to `main`.

Repeat for:

```text
.github/workflows/tests.yml
```

using:

```text
COPY_PASTE_GITHUB_ACTIONS/tests.yml
```

---

## 4. Enable Pages

1. Open the repository.
2. Click **Settings**.
3. Click **Pages** in the left sidebar.
4. Under **Build and deployment**, set **Source** to:

```text
GitHub Actions
```

---

## 5. Confirm the launch

1. Click **Actions**.
2. Open **Deploy SkillOS website to GitHub Pages**.
3. Wait for a green checkmark.
4. Open:

```text
https://montrealai.github.io/skillos/
```

The website should show a live demo card with:

```text
Lesson found
Candidate skill
Test result: approve_canary
Release: team · 10_percent_canary
```

---

## Recommended GitHub repository settings

Repository description:

```text
The operating system for self-improving AI agents.
```

Website:

```text
https://montrealai.github.io/skillos/
```

Topics:

```text
ai-agents
agents
skill-learning
github-pages
self-improving-ai
agent-os
```

---

## Quick troubleshooting

### The website shows 404

Usually one of these is wrong:

```text
Repository owner is not MontrealAI
Repository name is not exactly skillos
Pages Source is not GitHub Actions
.github/workflows/pages.yml is missing
Deploy workflow is not green yet
```

### The Actions tab is empty

Create `.github/workflows/pages.yml` manually using `COPY_PASTE_GITHUB_ACTIONS/pages.yml`.

### The site loads but looks broken

Confirm these files exist:

```text
site/index.html
site/styles.css
site/app.js
site/assets/skillos-mark.svg
```

### The generated demo is missing

The deploy workflow runs:

```text
python scripts/build_pages.py
```

That creates:

```text
dist/data/demo.json
```

If the workflow is green, the live site should have the generated demo data.

### Uploading all files at once fails

Upload in batches:

```text
Batch 1: README.md, START_HERE.html, pyproject.toml, LICENSE
Batch 2: site, scripts, tests, docs
Batch 3: skillos, web, examples, skills
Batch 4: .github/workflows, or create workflows manually
```


## v3 reference workflow proof

This repository now includes `scripts/prove_wealth_loop.py`, `skillos/wealth_proof.py`, and `data/wealth_proof.json`. The proof uses the sales follow-up workflow to verify that each completed job creates a tested release and that the workflow gets cheaper, faster, and better after every release. The GitHub Pages deploy refuses to publish if the monotonic economic checks fail.
