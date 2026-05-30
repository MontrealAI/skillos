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
    require("site/index.html", "enterprise-ops-proof.html")
    require("site/index.html", "Enterprise Ops Market Proof")
    require("site/enterprise-ops-proof.html", "Enterprise Ops Market Proof")
    require("docs/enterprise_ops_market_proof.md", "Procurement invoice reconciliation")
    require("data/enterprise_ops_market_proof.json", "PASSED_AUTONOMOUS_ENTERPRISE_OPS_MARKET_PROOF")
    print("Enterprise ops proof visibility verification passed.")

if __name__ == "__main__":
    main()
