#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

PROOF_ID = "rsi-proof-forge-meta-coordination-proof"


def fail(msg: str) -> None:
    raise SystemExit(f"Site verification failed: {msg}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root)
    site = root / "site"
    required = [
        site / f"{PROOF_ID}.html",
        site / "data" / f"{PROOF_ID}.json",
        site / "docs" / f"{PROOF_ID}.md",
        site / "badges" / f"{PROOF_ID}.svg",
        site / "index.html",
        site / "proof-registry.json",
        site / "sitemap.xml",
        site / "robots.txt",
    ]
    for p in required:
        if not p.exists(): fail(f"missing {p}")
    page = (site / f"{PROOF_ID}.html").read_text(encoding="utf-8")
    index = (site / "index.html").read_text(encoding="utf-8")
    if "Proof Forge Meta-Coordination" not in page: fail("proof page missing title")
    if f"{PROOF_ID}.html" not in index: fail("homepage missing proof link")
    registry = json.loads((site / "proof-registry.json").read_text(encoding="utf-8"))
    if not any(p.get("id") == PROOF_ID and p.get("href") == f"{PROOF_ID}.html" for p in registry): fail("registry missing proof")
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    if f"{PROOF_ID}.html" not in sitemap: fail("sitemap missing proof page")
    data = json.loads((site / "data" / f"{PROOF_ID}.json").read_text(encoding="utf-8"))
    if not data.get("proved"): fail("site JSON proof not passed")
    print("Site verification passed")


if __name__ == "__main__":
    main()
