#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROOF_ID = "rsi-causal-attribution-engine-proof"


def fail(message: str) -> None:
    raise SystemExit(f"site verification failed: {message}")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"could not read JSON {path}: {exc}")


def registry_proofs(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, dict):
        proofs = raw.get("proofs", [])
    elif isinstance(raw, list):
        proofs = raw
    else:
        proofs = []
    if isinstance(proofs, dict):
        proofs = list(proofs.values())
    return [p for p in proofs if isinstance(p, dict)]


def main() -> None:
    root = Path.cwd()
    site = root / "site"
    required = [
        site / "index.html",
        site / f"{PROOF_ID}.html",
        site / "proof-registry.json",
        site / "data" / f"{PROOF_ID}.json",
        site / "docs" / f"{PROOF_ID}.md",
        site / "badges" / f"{PROOF_ID}.svg",
        site / "sitemap.xml",
        site / "robots.txt",
    ]
    for path in required:
        if not path.exists():
            fail(f"missing required public artifact: {path}")
        if path.stat().st_size <= 20:
            fail(f"artifact is unexpectedly small: {path}")
    page_text = (site / f"{PROOF_ID}.html").read_text(encoding="utf-8")
    for phrase in ["Did SkillOS cause the improvement?", "Causal attribution", "paired counterfactual", "Run / regenerate"]:
        if phrase not in page_text:
            fail(f"proof page missing phrase: {phrase}")
    index_text = (site / "index.html").read_text(encoding="utf-8")
    if PROOF_ID not in index_text:
        fail("index does not link to proof page")
    registry = read_json(site / "proof-registry.json")
    proofs = registry_proofs(registry)
    entries = [p for p in proofs if str(p.get("id") or p.get("proof_id") or p.get("href") or "") in {PROOF_ID, f"{PROOF_ID}.html"}]
    if not entries:
        fail("registry does not contain proof entry")
    receipt = read_json(site / "data" / f"{PROOF_ID}.json")
    if receipt.get("proof_id") != PROOF_ID or not receipt.get("proved"):
        fail("public proof JSON does not contain a passing receipt")
    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    if f"{PROOF_ID}.html" not in sitemap:
        fail("sitemap missing proof page")
    robots = (site / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap:" not in robots:
        fail("robots.txt missing sitemap link")
    print(json.dumps({
        "site_verified": True,
        "proof_page": f"site/{PROOF_ID}.html",
        "index": "site/index.html",
        "registry_entries": len(proofs),
        "public_json": f"site/data/{PROOF_ID}.json",
    }, indent=2))


if __name__ == "__main__":
    main()
