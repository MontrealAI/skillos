#!/usr/bin/env python3
"""Verify that the Shadow Pilot Proof is visible from the main SkillOS website."""

from __future__ import annotations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""

def main() -> None:
    checks = []
    for rel in ["site/index.html", "index.html", "dist/index.html"]:
        path = ROOT / rel
        if path.exists():
            text = read(path).lower()
            checks.append((rel, "shadow-pilot-proof.html" in text and "shadow pilot proof" in text))

    proof_page = ROOT / "site" / "shadow-pilot-proof.html"
    checks.append(("site/shadow-pilot-proof.html", proof_page.exists()))

    readme_text = read(ROOT / "README.md").lower()
    checks.append(("README.md", "shadow-pilot-proof.html" in readme_text or "shadow pilot proof" in readme_text))

    failures = [rel for rel, ok in checks if not ok]
    if failures:
        print("Shadow pilot visibility verification failed:")
        for rel in failures:
            print(f" - {rel}")
        raise SystemExit(1)

    print("Shadow pilot proof visibility verification passed.")

if __name__ == "__main__":
    main()
