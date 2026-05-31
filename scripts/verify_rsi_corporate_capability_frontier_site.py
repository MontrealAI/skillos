#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
DOCS = ROOT / "docs"

PROOF_JSON = DATA / "rsi_corporate_capability_frontier_proof.json"
PROOF_PAGE = SITE / "rsi-corporate-capability-frontier-proof.html"
INDEX = SITE / "index.html"
PROOFS = SITE / "proofs.html"
REGISTRY = SITE / "proof-index.json"
SITEMAP = SITE / "sitemap.xml"


def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    raise SystemExit(1)


def contains(path: Path, text: str) -> bool:
    return path.exists() and text in path.read_text(encoding="utf-8")


def main() -> None:
    for path in [PROOF_JSON, PROOF_PAGE, INDEX, PROOFS, REGISTRY, SITEMAP]:
        if not path.exists():
            fail(f"Missing required public site file: {path.relative_to(ROOT)}")

    proof = json.loads(PROOF_JSON.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    page = PROOF_PAGE.read_text(encoding="utf-8")
    index = INDEX.read_text(encoding="utf-8")
    proofs = PROOFS.read_text(encoding="utf-8")
    sitemap = SITEMAP.read_text(encoding="utf-8")

    checks = [
        (proof.get("proved") is True, "proof JSON must say proved=true"),
        ("Corporate Capability Frontier" in page, "specific proof page must show the proof title"),
        ("large specialist-agent superorganization" in page, "specific page must explain large multi-agent coordination"),
        ("does not claim achieved superintelligence" in page, "specific page must include safe boundary"),
        ("Kardashev Type II civilization" in page, "specific page must include Kardashev boundary"),
        ("rsi-corporate-capability-frontier-proof.html" in index, "home page must link to specific proof page"),
        ("Corporate Capability Frontier Proof" in index, "home page must feature the proof title"),
        ("rsi-corporate-capability-frontier-proof.html" in proofs, "proofs page must link to specific proof page"),
        (any(p.get("id") == "rsi-corporate-capability-frontier-proof" for p in registry.get("proofs", [])), "proof-index.json must register the proof"),
        ("https://montrealai.github.io/skillos/rsi-corporate-capability-frontier-proof.html" in sitemap, "sitemap must include the specific proof URL"),
        (str(proof["agent_system"]["agent_count"]) in page.replace(",", ""), "specific page must show agent count"),
        (str(proof["rsi_release_count"]) in page, "specific page must show RSI release count"),
    ]

    failures = [msg for ok, msg in checks if not ok]
    if failures:
        for failure in failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print(json.dumps({
        "status": "PASSED",
        "proof_page": str(PROOF_PAGE.relative_to(ROOT)),
        "home_page_updated": True,
        "proofs_page_updated": True,
        "registry_updated": True,
        "sitemap_updated": True,
        "agents": proof["agent_system"]["agent_count"],
        "rsi_releases": proof["rsi_release_count"],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
