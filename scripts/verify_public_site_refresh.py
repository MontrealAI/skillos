#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "site/index.html": [
        "Autonomous Proof Command Center",
        "Capital-to-capability thesis",
        "data-chart=\"rsi-curve\"",
        "Run all proofs",
        "Public boundary",
        "multi-agent.html",
    ],
    "site/assets/command-center.css": [":root", ".chart", ".hero"],
    "site/assets/command-center.js": ["function render", "data-chart", "agent-constellation"],
    "site/proofs.html": ["Proof Library", "data-chart=\"proof-status\""],
    "site/actions.html": ["GitHub Actions Status", "data-chart=\"workflow-status\""],
    "site/multi-agent.html": ["Multi-Agent Command Center", "Ablation comparison", "data-chart=\"ablation-bars\"", "SkillOS RSI"],
    "site/runbook.html": ["Run and regenerate everything"],
    "docs/SKILLOS_PUBLIC_SITE_STATUS.md": ["SkillOS Public Proof Command Center Status"],
    "data/public_site_status.json": ["generated_at_utc", "workflow_count", "proof_count", "flagship"],
}

def main() -> None:
    failures = []
    for rel, phrases in REQUIRED.items():
        p = ROOT / rel
        if not p.exists():
            failures.append(f"Missing {rel}")
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"Missing {phrase!r} in {rel}")

    status_path = ROOT / "data" / "public_site_status.json"
    if status_path.exists():
        try:
            obj = json.loads(status_path.read_text(encoding="utf-8"))
            if obj.get("workflow_count", 0) < 1:
                failures.append("workflow_count should be at least 1")
            if "safe_boundary" not in obj:
                failures.append("safe_boundary missing")
            if "flagship_raw" not in obj:
                failures.append("flagship_raw missing")
        except Exception as exc:
            failures.append(f"Invalid public_site_status.json: {exc}")

    if failures:
        print("Public proof command center verification failed:")
        for f in failures:
            print(f"- {f}")
        raise SystemExit(1)
    print("Public proof command center verification passed.")

if __name__ == "__main__":
    main()
