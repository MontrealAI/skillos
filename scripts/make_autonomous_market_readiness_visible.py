#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "index.html"

CARD = """
<section id="autonomous-market-readiness" style="margin:48px 0;padding:28px;border:1px solid rgba(255,255,255,.14);border-radius:24px;background:rgba(255,255,255,.06)">
  <p style="text-transform:uppercase;letter-spacing:.16em;color:#74f7ff;font-weight:800;font-size:12px;margin:0 0 10px">100% autonomous proof</p>
  <h2 style="font-size:clamp(30px,4vw,54px);line-height:1;margin:0 0 14px">Market-Readiness Proof</h2>
  <p style="color:#aab8c8;font-size:18px;max-width:780px">Runs entirely in GitHub Actions with no human review, no emails sent, no customers contacted, no private data, no API keys, and a deterministic holdout benchmark.</p>
  <p>
    <a href="autonomous-market-readiness.html" style="display:inline-block;margin-right:12px;padding:12px 18px;border-radius:999px;background:#8af7ff;color:#071421;font-weight:800;text-decoration:none">View autonomous proof</a>
    <a href="https://github.com/MontrealAI/skillos/actions/workflows/autonomous-market-readiness.yml" style="display:inline-block;padding:12px 18px;border-radius:999px;border:1px solid rgba(255,255,255,.25);color:#eef7ff;font-weight:800;text-decoration:none">Run on GitHub</a>
  </p>
</section>
""".strip()

def main():
    if not INDEX.exists():
        raise SystemExit("site/index.html not found")
    text = INDEX.read_text(encoding="utf-8")
    if "autonomous-market-readiness.html" in text and "Market-Readiness Proof" in text:
        print("Autonomous market-readiness card already visible.")
        return
    marker = "</main>"
    if marker in text:
        text = text.replace(marker, CARD + "\n" + marker, 1)
    else:
        text = text.replace("</body>", CARD + "\n</body>", 1)
    INDEX.write_text(text, encoding="utf-8")
    print("Autonomous market-readiness card added to homepage.")

if __name__ == "__main__":
    main()
