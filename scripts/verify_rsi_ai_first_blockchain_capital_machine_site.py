#!/usr/bin/env python3
import argparse, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SLUG = "rsi-ai-first-blockchain-capital-machine-proof"

def need(cond, msg):
    if not cond: raise SystemExit(msg)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    site = ROOT / "site"
    page = site / f"{SLUG}.html"
    index = site / "index.html"
    registry = site / "proof-registry.json"
    data = ROOT / "data" / f"{SLUG}.json"
    badge = ROOT / "badges" / f"{SLUG}.svg"
    report = ROOT / "docs" / f"{SLUG}.md"
    for p in [page, index, registry, data, badge, report, site / "sitemap.xml", site / "robots.txt"]:
        need(p.exists(), f"missing generated site artifact: {p}")
    html = page.read_text().lower()
    idx = index.read_text().lower()
    for phrase in ["ai-first blockchain capital machine", "large autonomous specialist-agent", "recursive self-improvement", "not live protocol revenue", "run proof on github", "json receipt"]:
        need(phrase in html, f"proof page missing phrase: {phrase}")
    need(f"{SLUG}.html" in idx, "homepage does not link to the specific proof page")
    reg = json.loads(registry.read_text())
    need(any(p.get("slug") == SLUG for p in reg), "proof registry missing slug")
    receipt = json.loads(data.read_text())
    need(receipt.get("metrics", {}).get("proved") is True, "proof receipt not passing")
    print(json.dumps({"site_verified": True, "proof_page": f"site/{SLUG}.html", "homepage": "site/index.html"}, indent=2))

if __name__ == "__main__":
    main()
