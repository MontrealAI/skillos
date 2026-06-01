#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
MARKER = "SKILLOS_FLAGSHIP_GOVERNANCE_TWIN_LAUNCH_V1"
SCHEMA = "skillos.flagship.capability_governance_twin.launch.v1"
OLD_PHRASES = [
    "Autonomous Proof Command Center",
    "SkillOS Proof Command Center",
    "Public SkillOS Command Center v2",
    "SkillOS Public Command Center v3",
]
REQUIRED_FILES = [
    "index.html",
    "capability-governance-twin.html",
    "skills.html",
    "run.html",
    "receipts.html",
    "health.html",
    "architecture.html",
    "proofs.html",
    "actions.html",
    "data/flagship-capability-governance-twin-manifest.json",
    "data/rsi-capability-governance-twin-proof.json",
    "docs/FLAGSHIP_CAPABILITY_GOVERNANCE_TWIN_LAUNCH.md",
    "badges/flagship-capability-governance-twin.svg",
    "proof-registry.json",
    "sitemap.xml",
    "robots.txt",
    ".nojekyll",
    "version.txt",
]

REQUIRED_SNIPPETS = [
    "Capability Governance Twin",
    "Operational sovereignty",
    "Every job can become a reusable skill",
    "Skills Used",
    "Governance Twin Construction",
    "Policy-as-Code Compilation",
    "Permission Boundary Mapping",
    "Shadow Route Simulation",
    "Control Plane Release Gating",
    "large specialist-agent",
]

def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")

def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as exc:
        fail(f"Cannot read {path}: {exc}")

def main() -> None:
    for rel in REQUIRED_FILES:
        path = SITE / rel
        if not path.exists():
            fail(f"Missing {rel}")

    index = read(SITE / "index.html")
    flagship = read(SITE / "capability-governance-twin.html")
    skills = read(SITE / "skills.html")
    combined = "\n".join([index, flagship, skills])

    if MARKER not in index or MARKER not in flagship:
        fail("Missing canonical marker on root or flagship page")

    for phrase in OLD_PHRASES:
        if phrase in index:
            fail(f"Old root phrase still present: {phrase}")

    for snippet in REQUIRED_SNIPPETS:
        if snippet not in combined:
            fail(f"Missing required snippet: {snippet}")

    manifest = json.loads(read(SITE / "data" / "flagship-capability-governance-twin-manifest.json"))
    if manifest.get("schema") != SCHEMA:
        fail(f"Bad manifest schema: {manifest.get('schema')}")
    if manifest.get("marker") != MARKER:
        fail("Bad manifest marker")

    proof = json.loads(read(SITE / "data" / "rsi-capability-governance-twin-proof.json"))
    skills_used = proof.get("skills_used", [])
    if not isinstance(skills_used, list) or len(skills_used) < 8:
        fail("Proof receipt does not contain enough Skills Used")
    if not proof.get("proved", False):
        fail("Flagship proof is not marked proved")

    registry = json.loads(read(SITE / "proof-registry.json"))
    proofs = registry.get("proofs", []) if isinstance(registry, dict) else []
    if not any(isinstance(p, dict) and p.get("id") == "skillos-flagship-capability-governance-twin-launch" for p in proofs):
        fail("Proof registry missing flagship entry")

    hrefs = re.findall(r'href="([^"]+)"', index + flagship)
    for href in hrefs:
        if href.startswith(("http://","https://","#","mailto:")):
            continue
        path = SITE / href.split("#", 1)[0].split("?", 1)[0]
        if href and not path.exists():
            fail(f"Broken local link: {href}")

    print(json.dumps({
        "status": "PASSED_SKILLOS_FLAGSHIP_GOVERNANCE_TWIN_LAUNCH_VERIFICATION",
        "marker": MARKER,
        "skills_displayed": len(skills_used),
        "root": "site/index.html",
        "flagship": "site/capability-governance-twin.html"
    }, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
