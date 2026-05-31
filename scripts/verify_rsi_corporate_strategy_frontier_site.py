#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SLUG = "rsi-corporate-strategy-frontier-proof"
BASE_URL = "https://montrealai.github.io/skillos/"


def fail(message: str) -> None:
    raise SystemExit(f"Corporate Strategy Frontier site verification failed: {message}")


def main() -> None:
    index = SITE / "index.html"
    page = SITE / f"{SLUG}.html"
    proof_json = ROOT / "data" / f"{SLUG}.json"
    report = ROOT / "docs" / f"{SLUG}.md"
    badge = ROOT / "badges" / f"{SLUG}.svg"
    registry = SITE / "proof-registry.json"
    sitemap = SITE / "sitemap.xml"
    for path in [index, page, proof_json, report, badge, registry, sitemap]:
        if not path.exists():
            fail(f"missing required file: {path}")
    index_text = index.read_text(encoding="utf-8")
    for needle in ["SKILLOS_CORPORATE_STRATEGY_FRONTIER_START", f"{SLUG}.html", f"data/{SLUG}.json", "Corporate Strategy Frontier Proof", "Run on GitHub"]:
        if needle not in index_text:
            fail(f"homepage missing: {needle}")
    page_text = page.read_text(encoding="utf-8")
    for needle in ["Corporate Strategy Frontier", "PROOF PASSED", "Run on GitHub", "capital → compute", f"data/{SLUG}.json"]:
        if needle not in page_text:
            fail(f"proof page missing: {needle}")
    proof = json.loads(proof_json.read_text(encoding="utf-8"))
    if proof.get("proved") is not True:
        fail("proof JSON does not say proved=true")
    registry_payload = json.loads(registry.read_text(encoding="utf-8"))
    if not any(p.get("slug") == SLUG and p.get("page") == f"{SLUG}.html" for p in registry_payload.get("proofs", [])):
        fail("proof registry missing corporate strategy frontier entry")
    sitemap_text = sitemap.read_text(encoding="utf-8")
    if BASE_URL + f"{SLUG}.html" not in sitemap_text:
        fail("sitemap missing proof URL")
    print(json.dumps({
        "site_verified": True,
        "homepage": str(index),
        "proof_page": str(page),
        "public_url": BASE_URL + f"{SLUG}.html",
        "value_capture_percent": proof["summary"]["value_capture_percent"],
    }, indent=2))

if __name__ == "__main__":
    main()
