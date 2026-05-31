#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

PROOF_ID = "rsi-capability-liquidity-engine-proof"
REQUIRED = [
    "Capabilities become liquid", "PROOF PASSED", "Run proof on GitHub", "Baseline dominance",
    "does not claim achieved superintelligence", "specialist-agent marketplace", "verifier courts",
]


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default=f"data/{PROOF_ID}.json")
    parser.add_argument("--site", default="site")
    args = parser.parse_args()
    site = Path(args.site)
    proof = json.loads(Path(args.json).read_text(encoding="utf-8"))
    proof_page = site / f"{PROOF_ID}.html"
    index = site / "index.html"
    registry = site / "proof-registry.json"
    for path in [proof_page, index, registry, site / "sitemap.xml", site / "robots.txt", site / "data" / f"{PROOF_ID}.json", site / "docs" / f"{PROOF_ID}.md", site / "badges" / f"{PROOF_ID}.svg"]:
        if not path.exists():
            fail(f"missing site artifact: {path}")
    page_text = proof_page.read_text(encoding="utf-8", errors="ignore")
    for term in REQUIRED:
        if term not in page_text:
            fail(f"missing term in proof page: {term}")
    index_text = index.read_text(encoding="utf-8", errors="ignore")
    if PROOF_ID not in index_text or "RSI Capability Liquidity Engine" not in index_text:
        fail("homepage does not link capability liquidity proof")
    data = json.loads(registry.read_text(encoding="utf-8"))
    proofs = data.get("proofs", []) if isinstance(data, dict) else data
    if not any(p.get("id") == PROOF_ID for p in proofs):
        fail("registry missing proof")
    copied = json.loads((site / "data" / f"{PROOF_ID}.json").read_text(encoding="utf-8"))
    if copied.get("proof_sha256") != proof.get("proof_sha256"):
        fail("site proof JSON hash mismatch")
    print(json.dumps({"site_verified": True, "proof_id": PROOF_ID, "proof_page": str(proof_page), "index": str(index)}, indent=2))


if __name__ == "__main__":
    main()
