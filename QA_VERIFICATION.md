# QA verification

This package was verified locally before delivery.

Commands run:

```bash
PYTHONDONTWRITEBYTECODE=1 python scripts/qa_check.py
python -m skillos.cli wealth-proof
node --check site/app.js
```

Expected result:

```text
✅ Repository file verification passed
Ran 6 tests ... OK
✅ Agent SkillOS verification passed
✅ Verified GitHub Pages output at dist
✅ Repository QA passed
```

What is checked:

- End-to-end SkillOS loop: Work → Trace → Learn → Skill → Test → Release.
- SQLite storage initialization.
- GitHub Pages demo snapshot generation.
- Wealth proof generation at `data/wealth_proof.json` and `dist/data/wealth_proof.json`.
- Monotonic economic checks: every release decreases cost, decreases minutes, increases quality, and increases accepted rate.
- `dist/index.html`, `dist/styles.css`, `dist/app.js`, `dist/data/demo.json`, `dist/data/wealth_proof.json`, `.nojekyll`, and manifest creation.
- Repository targets `MontrealAI/skillos` and `https://montrealai.github.io/skillos/`.
- JavaScript syntax for the static website.
- Root-level fallback website mirror is included for branch-root GitHub Pages deployment.

GitHub Actions re-runs the same QA path during deployment.

## v3.0 wealth-accumulation proof

This repository includes `scripts/prove_wealth_loop.py`, `skillos/wealth_proof.py`, `tests/test_wealth_proof.py`, and `data/wealth_proof.json`.

The proof uses the sales follow-up workflow to verify that each completed job creates a tested release and that the workflow gets cheaper, faster, and better after every release.

Current proof result:

```text
Workflow: Sales follow-up email from call notes
Final skill version: v6
Quality: 0.50 → 0.96
Minutes/job: 6.75 → 2.55
Cost/job: $8.48 → $3.23
Projected annual savings vs human baseline at 10,000 jobs: $117,700
```

The GitHub Pages deploy refuses to publish if the wealth proof fails.
