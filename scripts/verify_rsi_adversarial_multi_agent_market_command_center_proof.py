#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def require(path: str, phrase: str) -> None:
    p = ROOT / path
    if not p.exists():
        raise SystemExit(f"Missing {path}")
    text = p.read_text(encoding="utf-8", errors="ignore")
    if phrase not in text:
        raise SystemExit(f"Missing {phrase!r} in {path}")

def main() -> None:
    require("site/index.html", "rsi-adversarial-multi-agent-market-command-center-proof.html")
    require("site/index.html", "Autonomous RSI Adversarial Multi-Agent Market Command Center")
    require("site/rsi-adversarial-multi-agent-market-command-center-proof.html", "Adversarial RSI Multi-Agent Market Command Center")
    require("docs/rsi_adversarial_multi_agent_market_command_center_proof.md", "Pre-registered pass/fail gates")
    require("docs/rsi_adversarial_multi_agent_market_command_center_proof.md", "Single-agent baseline")
    require("data/rsi_adversarial_multi_agent_market_command_center_proof.json", "PASSED_AUTONOMOUS_RSI_ADVERSARIAL_MULTI_AGENT_MARKET_COMMAND_CENTER_PROOF")
    print("RSI adversarial multi-agent market command center proof visibility verification passed.")

if __name__ == "__main__":
    main()
