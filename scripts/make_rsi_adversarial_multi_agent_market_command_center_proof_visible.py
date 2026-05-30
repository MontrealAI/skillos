#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "index.html"

CARD = """
<section id="rsi-adversarial-multi-agent-market-command-center-proof" style="margin:48px 0;padding:28px;border:1px solid rgba(255,255,255,.14);border-radius:24px;background:rgba(255,255,255,.06)">
  <p style="text-transform:uppercase;letter-spacing:.16em;color:#74f7ff;font-weight:800;font-size:12px;margin:0 0 10px">Adversarial large-scale agentic coordination</p>
  <h2 style="font-size:clamp(30px,4vw,54px);line-height:1;margin:0 0 14px">Autonomous RSI Adversarial Multi-Agent Market Command Center</h2>
  <p style="color:#aab8c8;font-size:18px;max-width:960px">A 100% autonomous GitHub Actions proof that coordinates a 160-agent specialist collective across 20 business roles, tests adversarial market-capture traps, compares single-agent, uncoordinated-pool, static-coordination, and coordinated-RSI systems, then releases only validation-gated coordination protocols.</p>
  <p style="color:#aab8c8;font-size:15px;max-width:960px">No human review, no customers, no private data, no API keys, and no reuse of previous proof domains.</p>
  <p>
    <a href="rsi-adversarial-multi-agent-market-command-center-proof.html" style="display:inline-block;margin-right:12px;padding:12px 18px;border-radius:999px;background:#8af7ff;color:#071421;font-weight:800;text-decoration:none">View adversarial multi-agent proof</a>
    <a href="https://github.com/MontrealAI/skillos/actions/workflows/rsi-adversarial-multi-agent-market-command-center-proof.yml" style="display:inline-block;padding:12px 18px;border-radius:999px;border:1px solid rgba(255,255,255,.25);color:#eef7ff;font-weight:800;text-decoration:none">Run on GitHub</a>
  </p>
</section>
""".strip()

def main() -> None:
    if not INDEX.exists():
        raise SystemExit("site/index.html not found")
    text = INDEX.read_text(encoding="utf-8")
    if "rsi-adversarial-multi-agent-market-command-center-proof.html" in text and "Autonomous RSI Adversarial Multi-Agent Market Command Center" in text:
        print("RSI adversarial multi-agent market command center proof card already visible.")
        return
    if "</main>" in text:
        text = text.replace("</main>", CARD + "\n</main>", 1)
    else:
        text = text.replace("</body>", CARD + "\n</body>", 1)
    INDEX.write_text(text, encoding="utf-8")
    print("RSI adversarial multi-agent market command center proof card added to homepage.")

if __name__ == "__main__":
    main()
