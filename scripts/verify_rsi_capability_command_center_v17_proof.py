#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def require(path: str, phrase: str) -> None:
    p = ROOT / path
    if not p.exists():
        raise SystemExit(f"Missing {path}")
    text = p.read_text(encoding="utf-8", errors="ignore")
    if phrase not in text:
        raise SystemExit(f"Missing {phrase!r} in {path}")

def main() -> None:
    require("site/index.html", "rsi-capability-command-center-v17-proof.html")
    require("site/index.html", "Autonomous RSI Capital-to-Capability Command Center")
    require("site/rsi-capability-command-center-v17-proof.html", "Safe Kardashev-scale mechanism")
    require("docs/rsi_capability_command_center_v17_proof.md", "Large-scale multi-agent coordination")
    require("data/rsi_capability_command_center_v17_proof.json", "PASSED_AUTONOMOUS_RSI_CAPITAL_TO_CAPABILITY_COMMAND_CENTER_V17_PROOF")
    result = json.loads((ROOT / "data/rsi_capability_command_center_v17_proof.json").read_text(encoding="utf-8"))
    if not result.get("proved"):
        raise SystemExit("Proof JSON does not show proved=true")
    if result["agent_system"]["agent_count"] < 512:
        raise SystemExit("Agent count gate did not pass")
    print("RSI capital-to-capability command center v17 proof visibility verification passed.")

if __name__ == "__main__":
    main()
