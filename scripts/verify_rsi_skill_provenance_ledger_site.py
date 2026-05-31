#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SLUG = "rsi-skill-provenance-ledger-proof"

def require(path: Path, *phrases: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required site file: {path}")
    text = path.read_text(encoding="utf-8", errors="ignore")
    for phrase in phrases:
        if phrase not in text:
            raise SystemExit(f"Missing phrase {phrase!r} in {path}")

def main() -> None:
    require(SITE / f"{SLUG}.html", "Skill Provenance Ledger", "provenance integrity", "Pre-registered gates")
    require(SITE / "index.html", "Autonomous RSI Skill Provenance Ledger Proof")
    require(SITE / "proof-registry.json", SLUG)
    registry = json.loads((SITE / "proof-registry.json").read_text(encoding="utf-8"))
    if not any(item.get("slug") == SLUG for item in registry):
        raise SystemExit("Proof registry missing Skill Provenance Ledger entry")
    print(json.dumps({"status": "SITE_VERIFICATION_PASSED", "page": f"site/{SLUG}.html"}, indent=2))

if __name__ == "__main__":
    main()
