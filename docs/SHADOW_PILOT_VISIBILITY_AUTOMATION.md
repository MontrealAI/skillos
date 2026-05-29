# Shadow Pilot Proof Visibility Automation

This automation makes the autonomous no-send Shadow Pilot Proof visible from the main SkillOS website.

## What it does

Every GitHub Pages deployment now:

1. Runs the autonomous no-send Shadow Pilot Proof.
2. Creates or refreshes `site/shadow-pilot-proof.html`.
3. Adds a clear Shadow Pilot Proof card to the main SkillOS homepage.
4. Adds a navigation link to the proof.
5. Verifies that the link exists before deployment.
6. Deploys the updated site to GitHub Pages.

## Public-safe interpretation

The Shadow Pilot Proof is a reproducible reference workflow proof. It uses synthetic or redacted call-note examples. No emails are sent, no customers are contacted, no private data is used, and no API keys are required.

It is not audited customer results, financial advice, or a guarantee of future outcomes.

## Main public links

- Main SkillOS site: https://montrealai.github.io/skillos/
- Shadow Pilot Proof page: https://montrealai.github.io/skillos/shadow-pilot-proof.html
- GitHub Action: https://github.com/MontrealAI/skillos/actions/workflows/shadow-pilot-proof.yml

## Best meeting explanation

The main site now shows the proof ladder clearly:

Reference proof → autonomous no-send shadow proof → private historical no-send evaluation → human-approved production drafts.
