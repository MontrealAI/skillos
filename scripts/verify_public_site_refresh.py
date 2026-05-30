#!/usr/bin/env python3
"""Verify that the SkillOS public site command center was generated correctly."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "site/index.html": [
        "Public Proof Command Center",
        "Run all public proofs",
        "Public boundary",
        "proofs.html",
        "actions.html",
        "runbook.html",
    ],
    "site/proofs.html": ["All public SkillOS proofs"],
    "site/actions.html": ["Workflow status command board"],
    "site/runbook.html": ["Run and regenerate the proofs"],
    "docs/SKILLOS_PUBLIC_SITE_STATUS.md": ["SkillOS Public Site Command Center Status"],
    "data/public_site_status.json": ["generated_at_utc", "workflow_count", "proof_count"],
}

def main() -> None:
    failures: list[str] = []
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
            if "site_url" not in obj:
                failures.append("site_url missing from public_site_status.json")
        except Exception as exc:
            failures.append(f"Invalid public_site_status.json: {exc}")

    if failures:
        print("Public site verification failed:")
        for f in failures:
            print(f"- {f}")
        raise SystemExit(1)

    print("Public site command center verification passed.")

if __name__ == "__main__":
    main()
