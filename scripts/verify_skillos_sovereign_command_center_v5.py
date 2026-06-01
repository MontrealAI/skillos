#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
MARKER = "SKILLOS_COMMAND_CENTER_V5_CANONICAL_ROOT"
FORBIDDEN = [
    "Autonomous Proof Command Center",
    "SkillOS Public Command Center v2",
    "SkillOS Public Command Center v3",
    "Public SkillOS Command Center v2",
]
REQUIRED = [
    "index.html", "executive.html", "proofs.html", "actions.html", "skills.html",
    "multi-agent.html", "receipts.html", "architecture.html", "flywheel.html",
    "health.html", "runbook.html", "force-refresh.html", "404.html",
    "data/command-center-manifest.json", "data/command-center-health.json",
    "proof-registry.json", "sitemap.xml", "robots.txt", ".nojekyll",
    "version.txt", "service-worker.js",
]

def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    raise SystemExit(1)

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")

def main() -> None:
    for rel in REQUIRED:
        if not (SITE / rel).exists():
            fail(f"Missing required file: site/{rel}")
    index = read(SITE / "index.html")
    if MARKER not in index:
        fail("index.html missing canonical v5 marker")
    for phrase in FORBIDDEN:
        if phrase in index:
            fail(f"index.html contains forbidden legacy phrase: {phrase}")
    for snippet in ["Sovereign SkillOS Command Center", "Every job can become a reusable skill", "one artifact", "Skills Used", "Large multi-agent coordination"]:
        if snippet not in index:
            fail(f"index.html missing required snippet: {snippet}")
    manifest = json.loads(read(SITE / "data" / "command-center-manifest.json"))
    if manifest.get("schema") != "skillos.command_center.sovereign.v5":
        fail("manifest schema is not v5")
    if manifest.get("marker") != MARKER:
        fail("manifest marker mismatch")
    registry = json.loads(read(SITE / "proof-registry.json"))
    if not isinstance(registry.get("proofs"), list):
        fail("proof registry missing proofs list")
    missing = []
    for proof in registry.get("proofs", []):
        href = proof.get("href")
        if href and not re.match(r"^https?://", href) and not (SITE / href).exists():
            missing.append(href)
    if missing:
        fail(f"Missing proof pages for registry hrefs: {missing[:10]}")
    print(json.dumps({"status": "PASSED", "marker": MARKER, "proof_count": manifest.get("proof_count"), "workflow_count": manifest.get("workflow_count"), "skills_used_count": manifest.get("skills_used_count")}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
