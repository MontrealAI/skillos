#!/usr/bin/env python3
"""Verify SkillOS public copy stays in the safe reference-workflow posture."""

from __future__ import annotations
import argparse, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", ".mypy_cache", ".pytest_cache"}
TEXT_EXTS = {".html", ".js", ".md", ".json", ".txt", ".xml", ".css", ".webmanifest"}

UNSAFE_PATTERNS = [
    r"\bwealth[- ]accumulation layer\b",
    r"\bwealth[- ]accumulation proof\b",
    r"\bwealth proof\b",
    r"\bone real workflow\b",
    r"\breal workflow gets cheaper\b",
    r"\breal skill releases\b",
    r"\bskills become margin\b",
    r"\bwealth[- ]producing capability\b",
    r"\breal workflows\. real results\b",
]

def iter_public_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(ROOT).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if path.suffix.lower() in TEXT_EXTS:
            yield path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    findings = []
    checked = 0
    for path in iter_public_text_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        checked += 1
        for pattern in UNSAFE_PATTERNS:
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append(f"Unsafe phrase in {path.relative_to(ROOT)}: {pattern}")

    public_pages = []
    for rel in ["site/index.html", "index.html", "dist/index.html"]:
        path = ROOT / rel
        if path.exists():
            public_pages.append(path.read_text(encoding="utf-8", errors="ignore").lower())
    combined = "\n".join(public_pages)

    if not public_pages:
        findings.append("No public page files found to verify.")

    for phrase in ["reference workflow", "unit economics", "demo assumptions"]:
        if phrase not in combined:
            findings.append(f"Missing required safe phrase in public page copy: {phrase}")

    if findings:
        print("Safe public copy verification failed:")
        for finding in findings:
            print(f" - {finding}")
        raise SystemExit(1)

    print(f"Safe public copy verification passed ({checked} files checked).")

if __name__ == "__main__":
    main()
