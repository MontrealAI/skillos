# Start here: publish SkillOS with the GitHub web interface

This guide is for uploading SkillOS to GitHub without Terminal, Git, or code editors.

## Your target

```text
Organization: MontrealAI
Repository: skillos
Final website: https://montrealai.github.io/skillos/
```

## What success looks like

When everything works, GitHub will show:

```text
Actions → Deploy SkillOS website to GitHub Pages → green checkmark
Actions → SkillOS tests → green checkmark
```

Then this URL will load the polished SkillOS site:

```text
https://montrealai.github.io/skillos/
```

The page should show the Agent SkillOS hero, workflow badges, demo metrics, and the generated proof loop showing `approve_canary`.

---

## Step 1 — Create the repository

1. Go to `https://github.com/MontrealAI`.
2. Click **New repository**.
3. Repository name: `skillos`.
4. Choose **Public**.
5. Leave **Add a README file** unchecked if possible.
6. Click **Create repository**.

The repository name matters. `MontrealAI/skillos` maps to:

```text
https://montrealai.github.io/skillos/
```

---

## Step 2 — Upload the files

1. Unzip the package you downloaded.
2. Open this folder:

```text
UPLOAD_THE_CONTENTS_OF_THIS_FOLDER_TO_GITHUB
```

3. Select everything **inside** that folder.
4. In GitHub, open the new `MontrealAI/skillos` repository.
5. Click **Add file → Upload files**.
6. Drag the selected files and folders into the upload area.
7. Commit message:

```text
Initial Agent SkillOS launch
```

8. Click **Commit changes**.

Important: do **not** upload the ZIP file itself, and do **not** upload the wrapper folder as a single folder. Upload the files inside it.

---

## Step 3 — Check the workflow files

After uploading, confirm these files exist in GitHub:

```text
.github/workflows/pages.yml
.github/workflows/tests.yml
```

If you do not see `.github`, your computer probably hid that folder during upload.

Fix it this way:

1. In GitHub, click **Add file → Create new file**.
2. Paste this filename:

```text
.github/workflows/pages.yml
```

3. Open this backup file from the package:

```text
COPY_PASTE_GITHUB_ACTIONS/pages.yml
```

4. Copy all of it and paste it into GitHub.
5. Commit directly to `main`.
6. Repeat for:

```text
.github/workflows/tests.yml
```

using:

```text
COPY_PASTE_GITHUB_ACTIONS/tests.yml
```

---

## Step 4 — Enable GitHub Pages

1. Open the repository **Settings** tab.
2. In the left sidebar, click **Pages**.
3. Under **Build and deployment**, set **Source** to **GitHub Actions**.
4. Save if GitHub shows a Save button.

---

## Step 5 — Watch the launch

1. Open the **Actions** tab.
2. Click **Deploy SkillOS website to GitHub Pages**.
3. Wait for the workflow to turn green.
4. Open:

```text
https://montrealai.github.io/skillos/
```

---

## If something looks wrong

### Actions tab is empty

The `.github/workflows/pages.yml` file is missing. Use the copy/paste workflow backup.

### Website is 404

Check that:

```text
Repository owner is MontrealAI
Repository name is exactly skillos
Settings → Pages → Source is GitHub Actions
.github/workflows/pages.yml exists
Deploy workflow is green
```

### GitHub shows a folder named `UPLOAD_THE_CONTENTS_OF_THIS_FOLDER_TO_GITHUB`

That means the wrapper folder was uploaded instead of its contents. Delete the repository files and upload the contents inside that folder instead.

### Workflow is red

Open the failed workflow, click the red step, and read the error. The repo includes `scripts/verify_repo.py` so common problems fail with plain-English messages.

---

## Best next file

For a more detailed checklist, open:

```text
GITHUB_UPLOAD_GUIDE.md
```
