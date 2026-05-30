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
    require("site/index.html", "rsi-silicon-verification-proof.html")
    require("site/index.html", "Autonomous RSI Silicon Verification Market Proof")
    require("site/rsi-silicon-verification-proof.html", "Autonomous RSI Silicon Verification Proof")
    require("docs/rsi_silicon_verification_market_proof.md", "Recursive Self-Improvement")
    require("data/rsi_silicon_verification_market_proof.json", "PASSED_AUTONOMOUS_RSI_SILICON_VERIFICATION_MARKET_PROOF")
    print("RSI silicon verification proof visibility verification passed.")

if __name__ == "__main__":
    main()
