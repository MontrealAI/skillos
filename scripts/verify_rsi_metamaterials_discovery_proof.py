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
    require("site/index.html", "rsi-metamaterials-discovery-proof.html")
    require("site/index.html", "Autonomous RSI Metamaterials Discovery Market Proof")
    require("site/rsi-metamaterials-discovery-proof.html", "Autonomous RSI Metamaterials Discovery Proof")
    require("docs/rsi_metamaterials_discovery_market_proof.md", "Recursive Self-Improvement")
    require("data/rsi_metamaterials_discovery_market_proof.json", "PASSED_AUTONOMOUS_RSI_METAMATERIALS_DISCOVERY_MARKET_PROOF")
    print("RSI metamaterials discovery proof visibility verification passed.")

if __name__ == "__main__":
    main()
