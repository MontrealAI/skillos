#!/usr/bin/env python3
"""Verify SkillOS safe public copy.

This verifier is designed for GitHub Actions. It checks the source website and,
when present, the generated dist website. It does not fail merely because dist
has not been generated yet unless a checked file actually contains unsafe copy.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

UNSAFE_PHRASES = [
    "The wealth-accumulation layer for self-improving AI agents",
    "wealth-accumulation layer",
    "Wealth-accumulation proof",
    "wealth-accumulation proof",
    "Wealth Proof",
    "one real workflow",
    "real workflow gets cheaper",
    "real skill releases",
    "Skills become margin",
    "wealth-producing capability",
    "Real workflows. Real results.",
]

CHECK_RELATIVE = [
    "site/index.html",
    "index.html",
    "site/app.js",
    "app.js",
    "README.md",
    "PROOF_OF_WEALTH_ACCUMULATION.md",
    "data/wealth_proof.json",
    "dist/index.html",
    "dist/app.js",
    "dist/wealth_accumulation_proof.md",
    "dist/data/wealth_proof.json",
]

PUBLIC_PAGE_FILES = [
    "site/index.html",
    "index.html",
    "dist/index.html",
]


def read(rel: str) -> str | None:
    path = ROOT / rel
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="ignore")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    findings: list[str] = []
    checked = 0

    for rel in CHECK_RELATIVE:
        text = read(rel)
        if text is None:
            continue
        checked += 1
        lower_text = text.lower()
        for phrase in UNSAFE_PHRASES:
            if phrase.lower() in lower_text:
                findings.append(f"Unsafe phrase in {rel}: {phrase}")

    page_texts = [read(rel) for rel in PUBLIC_PAGE_FILES if read(rel) is not None]
    combined_pages = "\n".join(t for t in page_texts if t).lower()

    required_phrases = [
        "reference workflow",
        "unit economics",
        "demo assumptions",
    ]
    for phrase in required_phrases:
        if phrase not in combined_pages:
            findings.append(f"Missing required safe phrase in public page copy: {phrase}")

    if checked == 0:
        findings.append("No public copy files were available to check.")

    if findings:
        print("Safe public copy verification failed:")
        for item in findings:
            print(f" - {item}")
        raise SystemExit(1)

    print(f"Safe public copy verification passed ({checked} files checked).")


if __name__ == "__main__":
    main()
