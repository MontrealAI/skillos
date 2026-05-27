# GitHub Pages site

The public site lives in `site/` and is built into `dist/` by:

```bash
python scripts/build_pages.py
```

The build script does more than copy HTML. It runs the real SkillOS loop in a temporary SQLite database and writes a generated demo snapshot to:

```text
dist/data/demo.json
```

GitHub Actions then publishes `dist/` to:

```text
https://montrealai.github.io/skillos/
```
