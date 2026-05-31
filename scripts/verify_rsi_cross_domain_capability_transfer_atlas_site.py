#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROOF_ID = "rsi-cross-domain-capability-transfer-atlas-proof"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"site verification failed: {message}")


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"site verification failed: could not parse {path}: {exc}") from exc


def main() -> None:
    site = Path("site")
    page = site / f"{PROOF_ID}.html"
    index = site / "index.html"
    registry_path = site / "proof-registry.json"
    public_json = site / "data" / f"{PROOF_ID}.json"
    public_report = site / "docs" / f"{PROOF_ID}.md"
    public_badge = site / "badges" / f"{PROOF_ID}.svg"

    for path in [page, index, registry_path, public_json, public_report, public_badge, site / "sitemap.xml", site / "robots.txt"]:
        require(path.exists(), f"missing {path}")
        require(path.stat().st_size > 0, f"empty {path}")

    proof = read_json(public_json)
    require(isinstance(proof, dict), "public proof JSON must be an object")
    require(proof.get("proof_id") == PROOF_ID, "public proof JSON proof_id mismatch")
    require(proof.get("proved") is True, "proof receipt is not marked proved")
    require(isinstance(proof.get("metrics"), dict), "proof JSON missing metrics object")

    registry = read_json(registry_path)
    require(isinstance(registry, dict), "registry must be canonical object after publisher migration")
    require(registry.get("schema_version") == 2, "registry schema_version must be 2")
    proofs = registry.get("proofs")
    require(isinstance(proofs, list), "registry.proofs must be a list")
    matching = [p for p in proofs if isinstance(p, dict) and p.get("id") == PROOF_ID]
    require(len(matching) == 1, "registry must contain exactly one current proof entry")
    entry = matching[0]
    require(entry.get("href") == f"{PROOF_ID}.html", "registry entry href mismatch")
    require(entry.get("json") == f"data/{PROOF_ID}.json", "registry entry json path mismatch")
    require(entry.get("report") == f"docs/{PROOF_ID}.md", "registry entry report path mismatch")
    require(entry.get("badge") == f"badges/{PROOF_ID}.svg", "registry entry badge path mismatch")
    require(entry.get("status") == "passing", "registry entry status must be passing")

    page_text = page.read_text(encoding="utf-8")
    require("Capability transfer is the moat" in page_text, "missing proof-page hero")
    require("Run proof on GitHub" in page_text, "missing proof-page run CTA")
    require("does not claim achieved superintelligence" in page_text, "missing public-safe boundary")
    require("public_safe_claim" not in page_text, "unrendered JSON key leaked into page")

    index_text = index.read_text(encoding="utf-8")
    require(PROOF_ID in index_text, "command center does not link current proof")
    require(f"{PROOF_ID}.html" in index_text, "command center missing proof href")
    require("Proofs that improve the proof system" in index_text, "command center hero missing")

    sitemap = (site / "sitemap.xml").read_text(encoding="utf-8")
    require(f"{PROOF_ID}.html" in sitemap, "sitemap missing proof URL")

    print(json.dumps({
        "site_verification": "passed",
        "proof_id": PROOF_ID,
        "registry_schema_version": registry.get("schema_version"),
        "registered_proofs": len(proofs),
        "page": str(page),
        "index": str(index),
    }, indent=2))


if __name__ == "__main__":
    main()
