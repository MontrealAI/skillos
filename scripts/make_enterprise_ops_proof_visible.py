#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "index.html"

CARD = """
<section id="enterprise-ops-proof" style="margin:48px 0;padding:28px;border:1px solid rgba(255,255,255,.14);border-radius:24px;background:rgba(255,255,255,.06)">
  <p style="text-transform:uppercase;letter-spacing:.16em;color:#74f7ff;font-weight:800;font-size:12px;margin:0 0 10px">Autonomous enterprise proof</p>
  <h2 style="font-size:clamp(30px,4vw,54px);line-height:1;margin:0 0 14px">Enterprise Ops Market Proof</h2>
  <p style="color:#aab8c8;font-size:18px;max-width:820px">A 100% autonomous GitHub Actions proof for invoice reconciliation and payment-risk triage. No human review, no emails, no customers, no private data, no API keys.</p>
  <p>
    <a href="enterprise-ops-proof.html" style="display:inline-block;margin-right:12px;padding:12px 18px;border-radius:999px;background:#8af7ff;color:#071421;font-weight:800;text-decoration:none">View enterprise proof</a>
    <a href="https://github.com/MontrealAI/skillos/actions/workflows/enterprise-ops-proof.yml" style="display:inline-block;padding:12px 18px;border-radius:999px;border:1px solid rgba(255,255,255,.25);color:#eef7ff;font-weight:800;text-decoration:none">Run on GitHub</a>
  </p>
</section>
""".strip()

def main() -> None:
    if not INDEX.exists():
        raise SystemExit("site/index.html not found")
    text = INDEX.read_text(encoding="utf-8")
    if "enterprise-ops-proof.html" in text and "Enterprise Ops Market Proof" in text:
        print("Enterprise ops proof card already visible.")
        return
    if "</main>" in text:
        text = text.replace("</main>", CARD + "\n</main>", 1)
    else:
        text = text.replace("</body>", CARD + "\n</body>", 1)
    INDEX.write_text(text, encoding="utf-8")
    print("Enterprise ops proof card added to homepage.")

if __name__ == "__main__":
    main()
