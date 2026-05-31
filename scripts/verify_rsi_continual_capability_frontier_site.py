#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PROOF_ID = "rsi-continual-capability-frontier-proof"

def require(path: Path, snippet: str | None = None) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")
    if snippet is not None and snippet not in path.read_text(encoding="utf-8", errors="ignore"):
        raise SystemExit(f"Missing snippet {snippet!r} in {path}")

def main() -> None:
    require(SITE / f"{PROOF_ID}.html", "Continual Capability Frontier")
    require(SITE / "data" / f"{PROOF_ID}.json", "PASSED_AUTONOMOUS_RSI_CONTINUAL_CAPABILITY_FRONTIER_PROOF")
    require(SITE / "docs" / f"{PROOF_ID}.md", "Autonomous RSI Continual Capability Frontier Proof")
    require(SITE / "badges" / f"{PROOF_ID}.svg", "continual capability frontier")
    require(SITE / "index.html", PROOF_ID)
    require(SITE / "proof-registry.json", PROOF_ID)
    registry = json.loads((SITE / "proof-registry.json").read_text(encoding="utf-8"))
    proofs = registry.get("proofs", []) if isinstance(registry, dict) else registry
    if not any(isinstance(p, dict) and p.get("id") == PROOF_ID for p in proofs):
        raise SystemExit("Proof registry does not contain continual capability frontier proof")
    print(json.dumps({"status": "SITE_VERIFIED", "proof": PROOF_ID}, indent=2))

if __name__ == "__main__":
    main()
