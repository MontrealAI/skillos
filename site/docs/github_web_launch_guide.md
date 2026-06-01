# Start here: publish SkillOS with the GitHub web interface

This guide is for uploading SkillOS to GitHub without using Terminal, Git, or code editors.

## Your target

```text
Organization: MontrealAI
Repository: skillos
Final website: https://montrealai.github.io/skillos/
```

## Step 1 — Create the repository

1. Go to `https://github.com/MontrealAI`.
2. Click **New repository**.
3. Repository name: `skillos`.
4. Choose **Public**.
5. Do not add a README, license, or .gitignore from GitHub. This package already includes them.
6. Click **Create repository**.

## Step 2 — Upload the files

1. Unzip the package you downloaded from ChatGPT.
2. Open the folder named:

```text
UPLOAD_THE_CONTENTS_OF_THIS_FOLDER_TO_GITHUB
```

3. Select everything inside that folder.
4. In GitHub, open the new `MontrealAI/skillos` repository.
5. Click **Add file → Upload files**.
6. Drag the selected files/folders into the upload area.
7. Commit message:

```text
Initial Agent SkillOS GitHub Pages launch
```

8. Click **Commit changes**.

## Step 3 — Make sure the workflow files exist

In the repository, confirm you can see:

```text
.github/workflows/pages.yml
.github/workflows/tests.yml
```

If you do not see `.github`, your computer may have hidden that folder during upload.

Use the backup files in:

```text
COPY_PASTE_GITHUB_ACTIONS/
```

Create these files manually in GitHub:

```text
.github/workflows/pages.yml
.github/workflows/tests.yml
```

Then paste the matching backup contents.

## Step 4 — Enable GitHub Pages

1. Open the repository **Settings** tab.
2. In the left sidebar, click **Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Save if GitHub shows a Save button.

## Step 5 — Watch the launch

1. Open the **Actions** tab.
2. Click **Deploy SkillOS website to GitHub Pages**.
3. Wait for it to turn green.
4. Open:

```text
https://montrealai.github.io/skillos/
```

## What success looks like

The page should show:

- the Agent SkillOS hero section;
- workflow badges;
- demo metrics;
- a generated result showing `approve_canary`;
- the full loop: `Work → Trace → Learn → Skill → Test → Approve → Release → Improve`.

## If it does not work

Open:

```text
docs/github_pages_troubleshooting.md
```

Most failures are caused by one of these:

- GitHub Pages source is not set to **GitHub Actions**;
- `.github/workflows/pages.yml` was not uploaded;
- the repository was not named exactly `skillos`;
- the upload accidentally created a nested folder instead of placing files at the repository root.
