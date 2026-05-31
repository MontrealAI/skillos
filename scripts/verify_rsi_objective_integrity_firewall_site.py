#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
PROOF_ID = "rsi-objective-integrity-firewall-proof"

def fail(msg): print(f"ERROR: {msg}", file=sys.stderr); raise SystemExit(1)

def main():
    required = [
        Path("site")/f"{PROOF_ID}.html", Path("site")/"index.html", Path("site")/"proof-registry.json",
        Path("site")/"sitemap.xml", Path("site")/"robots.txt", Path("site")/"data"/f"{PROOF_ID}.json",
        Path("site")/"docs"/f"{PROOF_ID}.md", Path("site")/"badges"/f"{PROOF_ID}.svg",
    ]
    for p in required:
        if not p.exists(): fail(f"missing site artifact: {p}")
    registry = json.loads((Path("site")/"proof-registry.json").read_text(encoding="utf-8"))
    proofs = registry.get("proofs") if isinstance(registry, dict) else None
    if not isinstance(proofs, list): fail("registry must contain proofs list")
    if not any(isinstance(p, dict) and p.get("id") == PROOF_ID for p in proofs): fail("proof not in registry")
    html = (Path("site")/f"{PROOF_ID}.html").read_text(encoding="utf-8")
    for token in ["Optimization that refuses to cheat", "Goodhart", "Objective Integrity", "Run on GitHub"]:
        if token not in html: fail(f"missing page token: {token}")
    index = (Path("site")/"index.html").read_text(encoding="utf-8")
    if PROOF_ID not in index: fail("index does not link proof")
    print(json.dumps({"site_verified": True, "proof_id": PROOF_ID, "files": [str(p) for p in required]}, indent=2))
if __name__ == "__main__": main()
