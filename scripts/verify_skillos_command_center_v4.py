#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SCHEMA = "skillos.command_center.root_fix.v4"
FORBIDDEN = [
    "Autonomous Proof Command Center",
    "SkillOS Proof Command Center",
    "Public SkillOS Command Center v2",
]

REQUIRED_FILES = [
    "index.html",
    "proofs.html",
    "skills.html",
    "actions.html",
    "multi-agent.html",
    "receipts.html",
    "architecture.html",
    "flywheel.html",
    "health.html",
    "runbook.html",
    "force-refresh.html",
    "data/command-center-manifest.json",
    "data/command-center-health.json",
    "proof-registry.json",
    "service-worker.js",
    ".nojekyll",
    "version.txt",
    "robots.txt",
    "sitemap.xml",
]

def fail(message: str) -> None:
    print(f"ERROR: {message}")
    raise SystemExit(1)

def read(rel: str) -> str:
    path = SITE / rel
    if not path.exists():
        fail(f"missing {rel}")
    return path.read_text(encoding="utf-8", errors="ignore")

def main() -> None:
    for rel in REQUIRED_FILES:
        if not (SITE / rel).exists():
            fail(f"missing required file: site/{rel}")
    homepage = read("index.html")
    for phrase in FORBIDDEN:
        if phrase in homepage:
            fail(f"forbidden old homepage phrase still present: {phrase}")
    for snippet in [
        "SkillOS Public Command Center v4",
        "Every job can become a reusable skill",
        "Skills Used",
        "work → traces → skills → verification → release → routing upgrade",
        "Root fix active",
    ]:
        if snippet not in homepage:
            fail(f"homepage missing snippet: {snippet}")
    skills = read("skills.html")
    for snippet in ["Job Trace Capture", "Skill Extraction", "Release Gate", "Autonomous Pages Deployment", "Legacy Workflow Neutralization"]:
        if snippet not in skills:
            fail(f"skills page missing snippet: {snippet}")
    manifest = json.loads(read("data/command-center-manifest.json"))
    if manifest.get("schema") != SCHEMA:
        fail(f"manifest schema mismatch: {manifest.get('schema')!r}")
    registry = json.loads(read("proof-registry.json"))
    if not isinstance(registry.get("proofs"), list):
        fail("proof registry missing list")
    if "self.registration.unregister" not in read("service-worker.js"):
        fail("service worker kill file missing unregister")
    print(json.dumps({
        "status": "VERIFIED",
        "schema": SCHEMA,
        "proof_count": manifest.get("proof_count"),
        "skills_surfaced_count": manifest.get("skills_surfaced_count"),
        "version_hash": manifest.get("version_hash"),
        "old_homepage_phrases_absent": True,
    }, indent=2))

if __name__ == "__main__":
    main()
