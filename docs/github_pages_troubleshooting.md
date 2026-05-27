# GitHub Pages troubleshooting

## Expected live URL

```text
https://montrealai.github.io/skillos/
```

## Expected repository

```text
https://github.com/MontrealAI/skillos
```

## Check 1 — repository name

The repository must be named exactly:

```text
skillos
```

If the repository is named `Agent-SkillOS`, `skill-os`, or anything else, the project site URL will be different.

## Check 2 — Pages source

Go to:

```text
Settings → Pages
```

Set:

```text
Source: GitHub Actions
```

## Check 3 — workflow files

Make sure these files exist in GitHub:

```text
.github/workflows/pages.yml
.github/workflows/tests.yml
```

If the `.github` folder is missing, use the visible backup files in:

```text
COPY_PASTE_GITHUB_ACTIONS/
```

Create the missing workflow files manually with GitHub's **Add file → Create new file** button.

## Check 4 — upload location

The repository root should show files like:

```text
README.md
README_FIRST_GITHUB_WEB_USERS.md
skillos/
site/
scripts/
.github/
```

If GitHub shows a single folder named `UPLOAD_THE_CONTENTS_OF_THIS_FOLDER_TO_GITHUB`, then the files were uploaded one level too deep. Move the contents to the repository root.

## Check 5 — Actions result

Open:

```text
Actions → Deploy SkillOS website to GitHub Pages
```

A green check means the website deployed. A red X means the workflow failed. Click the failed run and open the failing step.

## Check 6 — wait briefly and hard-refresh

After a green deployment, the website can take a short time to become visible. Try a hard refresh or private browsing window.

## What the workflow does

The deployment workflow runs:

```text
python scripts/qa_check.py
python scripts/build_pages.py
```

Then it uploads `dist/` to GitHub Pages.
