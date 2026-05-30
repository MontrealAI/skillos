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
    require("site/index.html", "rsi-revenue-experiment-factory-proof.html")
    require("site/index.html", "Autonomous RSI Revenue Experiment Factory")
    require("site/rsi-revenue-experiment-factory-proof.html", "Autonomous RSI Revenue Experiment Factory")
    require("docs/rsi_revenue_experiment_factory_market_proof.md", "Recursive Self-Improvement")
    require("data/rsi_revenue_experiment_factory_market_proof.json", "PASSED_AUTONOMOUS_RSI_REVENUE_EXPERIMENT_FACTORY_MARKET_PROOF")
    print("RSI revenue experiment factory proof visibility verification passed.")

if __name__ == "__main__":
    main()
