#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def require(path: str, phrase: str):
    p = ROOT / path
    if not p.exists():
        raise SystemExit(f"Missing {path}")
    text = p.read_text(encoding="utf-8", errors="ignore")
    if phrase not in text:
        raise SystemExit(f"Missing {phrase!r} in {path}")

def main():
    require("site/index.html", "autonomous-market-readiness.html")
    require("site/index.html", "Market-Readiness Proof")
    require("site/autonomous-market-readiness.html", "Autonomous Market-Readiness Proof")
    require("docs/autonomous_market_readiness.md", "no human review")
    require("data/autonomous_market_readiness.json", "PASSED_AUTONOMOUS_MARKET_READINESS_PROOF")
    print("Autonomous market-readiness visibility verification passed.")

if __name__ == "__main__":
    main()
