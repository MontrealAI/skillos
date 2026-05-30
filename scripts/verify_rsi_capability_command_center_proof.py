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
    require("site/index.html", "rsi-capability-command-center-proof.html")
    require("site/index.html", "Autonomous RSI Capital-to-Capability Command Center")
    require("site/rsi-capability-command-center-proof.html", "Autonomous RSI Capital-to-Capability Command Center")
    require("docs/rsi_capability_command_center_proof.md", "The quote made operational")
    require("docs/rsi_capability_command_center_proof.md", "Pre-registered proof gates")
    require("data/rsi_capability_command_center_proof.json", "PASSED_AUTONOMOUS_RSI_ADVERSARIAL_CAPABILITY_COMMAND_CENTER_PROOF")
    require("data/rsi_capability_command_center_preregistered_gates.json", "safe_kardashev_boundary_present")
    print("RSI capability command center proof visibility verification passed.")

if __name__ == "__main__":
    main()
