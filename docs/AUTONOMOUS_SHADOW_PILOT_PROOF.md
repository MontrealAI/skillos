# Autonomous Shadow Pilot Proof

This proof lets anyone inspect and rerun a no-send evaluation of the SkillOS mechanism through GitHub Actions.

## What it proves

It demonstrates the mechanism:

```text
call notes → draft → evaluation trace → lessons → tested skill rules → holdout improvement
```

The action uses a transparent synthetic/redacted benchmark. It does not send emails, contact customers, use private customer data, require API keys, or make claims about audited customer results.

## How to run it

1. Open the repository Actions tab.
2. Select **Autonomous Shadow Pilot Proof**.
3. Click **Run workflow**.
4. Open the run summary and artifacts.

Generated outputs:

```text
data/shadow_pilot_proof.json
docs/shadow_pilot_proof.md
site/shadow-pilot-proof.html
badges/shadow_pilot_proof.svg
```

If the regular GitHub Pages workflow runs after the generated proof is committed, the HTML page should become available at:

```text
https://montrealai.github.io/skillos/shadow-pilot-proof.html
```

## Safe interpretation

This is a reference workflow proof. It shows that the SkillOS loop can improve benchmark draft quality on holdout examples. It is not audited customer ROI, financial advice, a guarantee, or an investment claim.
