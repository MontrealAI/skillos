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
    require("site/index.html", "rsi-marketplace-flywheel-proof.html")
    require("site/index.html", "Autonomous RSI Marketplace Flywheel")
    require("site/rsi-marketplace-flywheel-proof.html", "Autonomous RSI Marketplace Flywheel")
    require("docs/rsi_marketplace_flywheel_market_proof.md", "Recursive Self-Improvement")
    require("data/rsi_marketplace_flywheel_market_proof.json", "PASSED_AUTONOMOUS_RSI_MARKETPLACE_FLYWHEEL_MARKET_PROOF")
    print("RSI marketplace flywheel proof visibility verification passed.")

if __name__ == "__main__":
    main()
