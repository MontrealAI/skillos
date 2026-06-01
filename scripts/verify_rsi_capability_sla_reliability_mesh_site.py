#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PROOF_ID = "rsi-capability-sla-reliability-mesh-proof"

REQUIRED_PAGE_SNIPPETS = [
    "Skills Used",
    "Demand Decomposition",
    "SLA Contract Extraction",
    "Latency-Aware Routing",
    "Capacity Market Clearing",
    "Verifier Coverage Planning",
    "Risk Veto",
    "Rollback Planning",
    "Incident Replay",
    "Release Gating",
    "Reinvestment Planner",
]

def require(path: Path, snippet: str | None = None) -> None:
    if not path.exists():
        raise SystemExit(f"Missing required file: {path}")
    if snippet and snippet not in path.read_text(encoding="utf-8", errors="ignore"):
        raise SystemExit(f"Missing snippet {snippet!r} in {path}")

def main() -> None:
    page=SITE/f"{PROOF_ID}.html"
    require(page, "Capability SLA Reliability Mesh")
    for snippet in REQUIRED_PAGE_SNIPPETS:
        require(page, snippet)
    require(SITE/"data"/f"{PROOF_ID}.json", "PASSED_AUTONOMOUS_RSI_CAPABILITY_SLA_RELIABILITY_MESH_PROOF")
    require(SITE/"docs"/f"{PROOF_ID}.md", "Autonomous RSI Capability SLA Reliability Mesh Proof")
    require(SITE/"badges"/f"{PROOF_ID}.svg", "capability SLA reliability mesh")
    require(SITE/"index.html", PROOF_ID)
    require(SITE/"proof-registry.json", PROOF_ID)
    raw=json.loads((SITE/"proof-registry.json").read_text(encoding="utf-8"))
    proofs=raw.get("proofs",[]) if isinstance(raw,dict) else raw
    if not any(isinstance(p,dict) and p.get("id")==PROOF_ID for p in proofs):
        raise SystemExit("Proof registry does not contain capability SLA reliability mesh proof")
    print(json.dumps({"status":"SITE_VERIFIED","proof":PROOF_ID,"skills_display_verified":True}, indent=2))

if __name__=="__main__":
    main()
