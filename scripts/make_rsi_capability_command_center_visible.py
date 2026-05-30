#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "index.html"

CARD = """
<section id="rsi-capability-command-center-proof" style="margin:48px 0;padding:28px;border:1px solid rgba(255,255,255,.14);border-radius:24px;background:rgba(255,255,255,.06)">
  <p style="text-transform:uppercase;letter-spacing:.16em;color:#74f7ff;font-weight:800;font-size:12px;margin:0 0 10px">Adversarial capital-to-capability RSI</p>
  <h2 style="font-size:clamp(30px,4vw,54px);line-height:1;margin:0 0 14px">Autonomous RSI Capital-to-Capability Command Center</h2>
  <p style="color:#aab8c8;font-size:18px;max-width:980px">A 100% autonomous GitHub Actions proof coordinating a 320-agent specialist organization across 32 roles to test capital, compute, energy, data, trust, talent, product, distribution, validation, risk control, and reinvestment as a compounding business-capability engine. Includes adversarial traps, ablations, pre-registered gates, proof receipts, and safe Kardashev-scale framing.</p>
  <p>
    <a href="rsi-capability-command-center-proof.html" style="display:inline-block;margin-right:12px;padding:12px 18px;border-radius:999px;background:#8af7ff;color:#071421;font-weight:800;text-decoration:none">View capability proof</a>
    <a href="https://github.com/MontrealAI/skillos/actions/workflows/rsi-capability-command-center-proof.yml" style="display:inline-block;padding:12px 18px;border-radius:999px;border:1px solid rgba(255,255,255,.25);color:#eef7ff;font-weight:800;text-decoration:none">Run on GitHub</a>
  </p>
</section>
""".strip()

def main() -> None:
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    if INDEX.exists():
        text = INDEX.read_text(encoding="utf-8")
    else:
        text = "<!doctype html><html><body><main></main></body></html>"
    if "rsi-capability-command-center-proof.html" in text and "Autonomous RSI Capital-to-Capability Command Center" in text:
        print("RSI capability command center proof card already visible.")
        return
    if "</main>" in text:
        text = text.replace("</main>", CARD + "\n</main>", 1)
    else:
        text = text.replace("</body>", CARD + "\n</body>", 1)
    INDEX.write_text(text, encoding="utf-8")
    print("RSI capability command center proof card added to homepage.")

if __name__ == "__main__":
    main()
