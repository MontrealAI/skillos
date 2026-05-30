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
    require("site/index.html", "rsi-unit-economics-proof.html")
    require("site/index.html", "Autonomous RSI Unit Economics Profit Engine")
    require("site/rsi-unit-economics-proof.html", "Autonomous RSI Unit Economics Profit Engine")
    require("docs/rsi_unit_economics_market_proof.md", "Recursive Self-Improvement")
    require("data/rsi_unit_economics_market_proof.json", "PASSED_AUTONOMOUS_RSI_UNIT_ECONOMICS_PROFIT_ENGINE_MARKET_PROOF")
    print("RSI unit economics proof visibility verification passed.")

if __name__ == "__main__":
    main()
