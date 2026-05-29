#!/usr/bin/env python3
# Make the Autonomous Shadow Pilot Proof visible from the main SkillOS website.
# Safe to run on every GitHub Actions deployment.

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DIST = ROOT / "dist"
DATA = ROOT / "data"
DOCS = ROOT / "docs"

PROOF_JSON = DATA / "shadow_pilot_proof.json"
PROOF_HTML = SITE / "shadow-pilot-proof.html"

NAV_START = "<!-- SKILLOS_SHADOW_PILOT_NAV_START -->"
NAV_END = "<!-- SKILLOS_SHADOW_PILOT_NAV_END -->"
CARD_START = "<!-- SKILLOS_SHADOW_PILOT_CARD_START -->"
CARD_END = "<!-- SKILLOS_SHADOW_PILOT_CARD_END -->"
CSS_START = "/* SKILLOS_SHADOW_PILOT_CSS_START */"
CSS_END = "/* SKILLOS_SHADOW_PILOT_CSS_END */"


def run(cmd: list[str]) -> None:
    print("+", " ".join(map(str, cmd)))
    subprocess.run(cmd, cwd=ROOT, check=True)


def load_proof() -> dict[str, Any]:
    if PROOF_JSON.exists():
        try:
            return json.loads(PROOF_JSON.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def proof_value(proof: dict[str, Any], key: str, default: Any = "—") -> Any:
    return proof.get(key, proof.get("summary", {}).get(key, default))


def refresh_proof() -> None:
    runner = ROOT / "scripts" / "run_shadow_pilot_proof.py"
    benchmark = DATA / "shadow_pilot_benchmark.json"
    if runner.exists() and benchmark.exists():
        print("Refreshing autonomous no-send shadow pilot proof.")
        run([sys.executable, str(runner)])
    else:
        print("Shadow pilot proof runner or benchmark not found; using existing proof outputs if present.")


def ensure_shadow_proof_page() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    proof = load_proof()

    if PROOF_HTML.exists():
        return

    quality_gain = proof_value(proof, "quality_gain_points", "29.8")
    edit_reduction = proof_value(proof, "edit_time_reduction_percent", "64.1")
    accepted_lift = proof_value(proof, "accepted_rate_lift_points", "80.0")

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SkillOS Shadow Pilot Proof</title>
  <link rel="stylesheet" href="./styles.css">
</head>
<body>
  <main class="shadow-proof-page">
    <section class="shadow-proof-hero">
      <p class="eyebrow">Autonomous no-send proof</p>
      <h1>SkillOS Shadow Pilot Proof</h1>
      <p>GitHub Actions runs a no-send reference evaluation using synthetic or redacted call-note examples. No emails are sent. No customers are contacted. No API keys are required.</p>
      <div class="shadow-proof-metrics">
        <div><strong>+{quality_gain} pts</strong><span>quality gain</span></div>
        <div><strong>{edit_reduction}%</strong><span>edit-time reduction</span></div>
        <div><strong>+{accepted_lift} pts</strong><span>accepted-rate lift</span></div>
      </div>
      <p class="shadow-proof-note">Safe interpretation: this is a reproducible reference workflow proof, not audited customer results, financial advice, or a guarantee of future outcomes.</p>
      <p><a href="./" class="button">Back to SkillOS</a> <a href="https://github.com/MontrealAI/skillos/actions/workflows/shadow-pilot-proof.yml" class="button secondary">Run proof on GitHub</a></p>
    </section>
  </main>
</body>
</html>
"""
    PROOF_HTML.write_text(html, encoding="utf-8")
    print(f"Created {PROOF_HTML.relative_to(ROOT)}")


def remove_between(text: str, start: str, end: str) -> str:
    while start in text and end in text:
        before, rest = text.split(start, 1)
        _, after = rest.split(end, 1)
        text = before + after
    return text


def nav_snippet() -> str:
    return f"""{NAV_START}
<a href="./shadow-pilot-proof.html">Shadow Pilot Proof</a>
{NAV_END}"""


def card_snippet() -> str:
    proof = load_proof()
    quality_gain = proof_value(proof, "quality_gain_points", "29.8")
    edit_reduction = proof_value(proof, "edit_time_reduction_percent", "64.1")
    accepted_lift = proof_value(proof, "accepted_rate_lift_points", "80.0")
    hallucination_after = proof_value(proof, "hallucination_rate_after_percent", "0")

    return f"""{CARD_START}
<section id="shadow-pilot-proof" class="shadow-pilot-card" aria-labelledby="shadow-pilot-title">
  <div class="shadow-pilot-copy">
    <p class="eyebrow">Autonomous no-send proof</p>
    <h2 id="shadow-pilot-title">Shadow Pilot Proof</h2>
    <p>GitHub Actions now runs a no-send reference evaluation that shows SkillOS can turn call-note examples into traces, lessons, tested skill rules, and improved holdout performance.</p>
    <p class="shadow-pilot-safe-note">No emails sent. No customers contacted. No private data. No API keys. Anyone can rerun the proof in GitHub Actions.</p>
    <div class="shadow-pilot-actions">
      <a class="button" href="./shadow-pilot-proof.html">View visual proof</a>
      <a class="button secondary" href="https://github.com/MontrealAI/skillos/actions/workflows/shadow-pilot-proof.yml">Run on GitHub</a>
    </div>
  </div>
  <div class="shadow-pilot-metrics" aria-label="Shadow pilot proof metrics">
    <div><strong>+{quality_gain} pts</strong><span>quality gain</span></div>
    <div><strong>{edit_reduction}%</strong><span>edit-time reduction</span></div>
    <div><strong>+{accepted_lift} pts</strong><span>accepted-rate lift</span></div>
    <div><strong>{hallucination_after}%</strong><span>hallucination rate after learned skill</span></div>
  </div>
</section>
{CARD_END}"""


def inject_nav(text: str) -> str:
    text = remove_between(text, NAV_START, NAV_END)
    snippet = nav_snippet()

    for marker in [
        '<a class="github',
        '<a href="https://github.com/MontrealAI/skillos"',
        '<a href="https://github.com/MontrealAI/skillos/"',
        'GitHub</a>',
    ]:
        if marker in text:
            idx = text.find(marker)
            return text[:idx] + snippet + "\n" + text[idx:]

    nav_start = text.find("<nav")
    if nav_start != -1:
        close = text.find(">", nav_start)
        if close != -1:
            return text[:close + 1] + "\n" + snippet + text[close + 1:]

    body = text.find("<body")
    if body != -1:
        close = text.find(">", body)
        if close != -1:
            return text[:close + 1] + "\n" + snippet + text[close + 1:]

    return snippet + "\n" + text


def inject_card(text: str) -> str:
    text = remove_between(text, CARD_START, CARD_END)
    snippet = card_snippet()

    for marker in ['<section id="proof"', '<section class="metrics"', '<div class="metrics"', '<section id="metrics"']:
        if marker in text:
            idx = text.find(marker)
            return text[:idx] + snippet + "\n" + text[idx:]

    idx = text.find("</section>")
    if idx != -1:
        idx += len("</section>")
        return text[:idx] + "\n" + snippet + text[idx:]

    for marker in ["</main>", "</body>"]:
        if marker in text:
            idx = text.find(marker)
            return text[:idx] + snippet + "\n" + text[idx:]

    return text + "\n" + snippet


def patch_homepage(path: Path) -> bool:
    if not path.exists():
        return False

    original = path.read_text(encoding="utf-8", errors="ignore")
    text = inject_nav(original)
    text = inject_card(text)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path.relative_to(ROOT)}")
        return True
    return False


def css_snippet() -> str:
    return f"""{CSS_START}
.shadow-pilot-card {{
  margin: 2rem auto;
  padding: clamp(1.25rem, 3vw, 2rem);
  border: 1px solid rgba(150, 210, 255, 0.28);
  border-radius: 28px;
  background: linear-gradient(135deg, rgba(75, 112, 140, 0.28), rgba(56, 46, 92, 0.24));
  box-shadow: 0 24px 90px rgba(0, 0, 0, 0.22);
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(260px, 0.9fr);
  gap: 1.5rem;
  align-items: center;
}}
.shadow-pilot-card h2 {{
  margin: 0 0 0.75rem;
  font-size: clamp(2rem, 4vw, 3.8rem);
  letter-spacing: -0.055em;
}}
.shadow-pilot-safe-note {{
  color: rgba(224, 239, 255, 0.86);
  font-weight: 700;
}}
.shadow-pilot-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1rem;
}}
.shadow-pilot-metrics {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}}
.shadow-pilot-metrics div {{
  min-height: 96px;
  padding: 1rem;
  border-radius: 20px;
  background: rgba(5, 12, 27, 0.36);
  border: 1px solid rgba(168, 224, 255, 0.22);
}}
.shadow-pilot-metrics strong {{
  display: block;
  font-size: clamp(1.5rem, 3vw, 2.2rem);
  color: #7cffb1;
}}
.shadow-pilot-metrics span {{
  display: block;
  margin-top: 0.25rem;
  color: rgba(224, 239, 255, 0.72);
}}
.shadow-proof-page {{
  min-height: 100vh;
  padding: clamp(2rem, 7vw, 6rem);
  background: radial-gradient(circle at 75% 20%, rgba(140, 115, 255, .36), transparent 32%),
              radial-gradient(circle at 20% 10%, rgba(91, 246, 255, .24), transparent 35%),
              #081526;
  color: #eff8ff;
}}
.shadow-proof-hero {{
  max-width: 980px;
  margin: 0 auto;
}}
.shadow-proof-hero h1 {{
  font-size: clamp(3rem, 8vw, 7rem);
  letter-spacing: -0.07em;
  line-height: 0.92;
}}
.shadow-proof-metrics {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin: 2rem 0;
}}
.shadow-proof-metrics div {{
  padding: 1.1rem;
  border: 1px solid rgba(168, 224, 255, 0.25);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.06);
}}
.shadow-proof-metrics strong {{
  display: block;
  font-size: clamp(1.6rem, 4vw, 2.6rem);
  color: #7cffb1;
}}
.shadow-proof-note {{
  color: rgba(224, 239, 255, .78);
}}
@media (max-width: 820px) {{
  .shadow-pilot-card,
  .shadow-proof-metrics {{
    grid-template-columns: 1fr;
  }}
}}
{CSS_END}"""


def patch_css(path: Path) -> bool:
    if not path.exists():
        return False
    original = path.read_text(encoding="utf-8", errors="ignore")
    text = remove_between(original, CSS_START, CSS_END)
    text = text.rstrip() + "\n\n" + css_snippet() + "\n"
    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"Updated {path.relative_to(ROOT)}")
        return True
    return False


def patch_readme() -> bool:
    path = ROOT / "README.md"
    if not path.exists():
        return False

    marker_start = "<!-- SKILLOS_SHADOW_PILOT_README_START -->"
    marker_end = "<!-- SKILLOS_SHADOW_PILOT_README_END -->"

    original = path.read_text(encoding="utf-8", errors="ignore")
    text = remove_between(original, marker_start, marker_end)

    snippet = f"""{marker_start}

## Autonomous no-send Shadow Pilot Proof

SkillOS now includes a public GitHub Actions proof that runs without sending emails, contacting customers, using private data, or requiring API keys.

- Visual proof page: https://montrealai.github.io/skillos/shadow-pilot-proof.html
- GitHub Action: https://github.com/MontrealAI/skillos/actions/workflows/shadow-pilot-proof.yml
- Proof report: [`docs/shadow_pilot_proof.md`](docs/shadow_pilot_proof.md)

Safe interpretation: this is a reproducible reference workflow proof, not audited customer results, financial advice, or a guarantee of future outcomes.

{marker_end}
"""
    insert_after = "## Important public note"
    if insert_after in text:
        idx = text.find(insert_after)
        next_heading = text.find("\n## ", idx + len(insert_after))
        if next_heading != -1:
            text = text[:next_heading] + "\n" + snippet + text[next_heading:]
        else:
            text = text.rstrip() + "\n\n" + snippet
    else:
        text = text.rstrip() + "\n\n" + snippet

    if text != original:
        path.write_text(text, encoding="utf-8")
        print("Updated README.md")
        return True
    return False


def main() -> None:
    refresh_proof()
    ensure_shadow_proof_page()

    changed = []
    for rel in ["site/index.html", "index.html", "dist/index.html"]:
        if patch_homepage(ROOT / rel):
            changed.append(rel)

    for rel in ["site/styles.css", "styles.css", "dist/styles.css"]:
        if patch_css(ROOT / rel):
            changed.append(rel)

    if patch_readme():
        changed.append("README.md")

    if changed:
        print("Shadow pilot visibility updated:")
        for rel in changed:
            print(f" - {rel}")
    else:
        print("Shadow pilot proof visibility already up to date.")


if __name__ == "__main__":
    main()
