#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

PROOF_ID = "rsi-governance-frontier-proof"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default=f"data/{PROOF_ID}.json")
    parser.add_argument("--site", default="site")
    args = parser.parse_args()
    proof = json.loads(Path(args.json).read_text(encoding="utf-8"))
    site = Path(args.site)
    proof_page = site / f"{PROOF_ID}.html"
    index = site / "index.html"
    registry = site / "proof-registry.json"
    public_json = site / "data" / f"{PROOF_ID}.json"
    public_doc = site / "docs" / f"{PROOF_ID}.md"
    public_badge = site / "badges" / f"{PROOF_ID}.svg"
    sitemap = site / "sitemap.xml"
    robots = site / "robots.txt"

    for p in [proof_page, index, registry, public_json, public_doc, public_badge, sitemap, robots]:
        assert_true(p.exists(), f"missing site output: {p}")

    index_text = index.read_text(encoding="utf-8")
    page_text = proof_page.read_text(encoding="utf-8")
    assert_true(f"{PROOF_ID}.html" in index_text, "homepage must link to proof page")
    assert_true("Run latest proof" in index_text or "Run on GitHub" in index_text, "homepage must expose run/regenerate affordance")
    assert_true("Large specialist-agent coordination" in page_text, "proof page must explain large-agent coordination")
    assert_true("Validation-gated RSI" in page_text, "proof page must show RSI release curve")
    assert_true("does not claim achieved superintelligence" in page_text.lower(), "proof page must include public-safe boundary")

    reg = json.loads(registry.read_text(encoding="utf-8"))
    proofs = reg.get("proofs", []) if isinstance(reg, dict) else reg
    match = [p for p in proofs if p.get("id") == PROOF_ID]
    assert_true(match, "registry must contain governance frontier proof")
    assert_true(match[0].get("proved") is True, "registry proof status must be true")
    assert_true(match[0].get("workflow_url"), "registry must include workflow URL")

    public = json.loads(public_json.read_text(encoding="utf-8"))
    assert_true(public["proof_sha256"] == proof["proof_sha256"], "public JSON hash must match source proof")

    print(json.dumps({
        "site_verified": True,
        "proof_id": PROOF_ID,
        "proof_page": str(proof_page),
        "index": str(index),
        "registry": str(registry),
    }, indent=2))


if __name__ == "__main__":
    main()
