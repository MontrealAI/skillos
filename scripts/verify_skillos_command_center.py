#!/usr/bin/env python3
"""Verify autonomous SkillOS command center output."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
MANIFEST = SITE / "data" / "command-center-manifest.json"

REQUIRED_FILES = [
    SITE / "index.html",
    SITE / "proofs.html",
    SITE / "actions.html",
    SITE / "data" / "command-center-manifest.json",
    SITE / "proof-registry.json",
    SITE / "sitemap.xml",
    SITE / "robots.txt",
    ROOT / "badges" / "command-center-fresh.svg",
    ROOT / "docs" / "SKILLOS_PUBLIC_COMMAND_CENTER.md",
]

REQUIRED_INDEX_SNIPPETS = [
    "Public SkillOS Command Center",
    "Autonomous proof, always refreshed",
    "How to see the proof",
    "Skills Used",
    "GitHub Actions",
    "work → traces → skills",
]

DISALLOWED_SNIPPETS = [
    "guaranteed wealth",
    "guaranteed returns",
    "real results",
]

def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def main() -> None:
    for path in REQUIRED_FILES:
        if not path.exists():
            fail(f"Missing required output: {path}")

    index = read(SITE / "index.html")
    for snippet in REQUIRED_INDEX_SNIPPETS:
        if snippet not in index:
            fail(f"Missing required homepage snippet: {snippet}")

    combined = "\n".join(read(path) for path in [SITE / "index.html", SITE / "proofs.html", SITE / "actions.html"])
    lowered = combined.lower()
    for bad in DISALLOWED_SNIPPETS:
        if bad.lower() in lowered:
            fail(f"Unsafe phrase found: {bad}")

    manifest = json.loads(read(MANIFEST))
    registry = json.loads(read(SITE / "proof-registry.json"))
    if not isinstance(registry, dict) or not isinstance(registry.get("proofs"), list):
        fail("proof-registry.json must be a dict with a proofs list")

    if manifest.get("proof_count", 0) != len(manifest.get("proofs", [])):
        fail("Manifest proof_count does not match proofs length")

    registry_ids = {p.get("id") for p in registry.get("proofs", []) if isinstance(p, dict)}
    for p in manifest.get("proofs", []):
        if p.get("id") and p.get("id") not in registry_ids:
            fail(f"Proof missing from registry: {p.get('id')}")

    if manifest.get("workflow_count", 0) != len(manifest.get("workflows", [])):
        fail("Manifest workflow_count does not match workflows length")

    print(json.dumps({
        "status": "COMMAND_CENTER_VERIFIED",
        "proof_count": manifest.get("proof_count"),
        "proved_count": manifest.get("proved_count"),
        "workflow_count": manifest.get("workflow_count"),
        "unique_skills_count": manifest.get("unique_skills_count"),
    }, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
