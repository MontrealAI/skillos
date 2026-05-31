#!/usr/bin/env python3
import argparse, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "rsi-ai-first-governance-capital-engine-proof"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    site = ROOT / "site"
    failures = []
    proof = site / f"{SLUG}.html"
    index = site / "index.html"
    registry = site / "proof-registry.json"
    sitemap = site / "sitemap.xml"
    receipt = ROOT / "data" / f"{SLUG}.json"
    public_receipt = site / "data" / f"{SLUG}.json"
    public_report = site / "docs" / f"{SLUG}.md"
    public_badge = site / "badges" / f"{SLUG}.svg"
    for path in [proof, index, registry, sitemap, receipt, public_receipt, public_report, public_badge]:
        if not path.exists():
            failures.append(f"missing {path}")
    if proof.exists():
        text = proof.read_text()
        for phrase in ["Governance Capital Engine", "large specialist-agent governance lattice", "Run proof on GitHub", "Kardashev", "not claim", "zero human-review gate"]:
            if phrase not in text:
                failures.append(f"proof page missing phrase: {phrase}")
    if index.exists():
        text = index.read_text()
        if SLUG not in text:
            failures.append("index does not link to proof slug")
        if "Flagship autonomous RSI governance proof" not in text:
            failures.append("index missing governance flagship section")
    if registry.exists():
        data = json.loads(registry.read_text())
        if not any(item.get("slug") == SLUG for item in data):
            failures.append("proof registry missing slug")
    if sitemap.exists() and SLUG not in sitemap.read_text():
        failures.append("sitemap missing proof slug")
    if args.strict and receipt.exists():
        obj = json.loads(receipt.read_text())
        if not obj["metrics"].get("proved"):
            failures.append("strict: receipt proof did not pass")
        if obj["metrics"].get("required_human_review") is not False:
            failures.append("strict: human review is required")
    if failures:
        print(json.dumps({"site_verified": False, "failures": failures}, indent=2))
        raise SystemExit(1)
    print(json.dumps({"site_verified": True, "proof_page": str(proof), "index": str(index)}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
