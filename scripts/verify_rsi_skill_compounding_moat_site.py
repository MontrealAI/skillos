#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
PROOF_ID = "rsi-skill-compounding-moat-proof"
def require(path: Path, snippet: str | None = None) -> None:
    if not path.exists(): raise SystemExit(f"Missing required file: {path}")
    if snippet and snippet not in path.read_text(encoding="utf-8", errors="ignore"):
        raise SystemExit(f"Missing snippet {snippet!r} in {path}")
def main() -> None:
    require(SITE/f"{PROOF_ID}.html", "Skill Compounding Moat")
    require(SITE/"data"/f"{PROOF_ID}.json", "PASSED_AUTONOMOUS_RSI_SKILL_COMPOUNDING_MOAT_PROOF")
    require(SITE/"docs"/f"{PROOF_ID}.md", "Autonomous RSI Skill Compounding Moat Proof")
    require(SITE/"badges"/f"{PROOF_ID}.svg", "skill compounding moat")
    require(SITE/"index.html", PROOF_ID)
    require(SITE/"proof-registry.json", PROOF_ID)
    raw=json.loads((SITE/"proof-registry.json").read_text(encoding="utf-8"))
    proofs=raw.get("proofs",[]) if isinstance(raw,dict) else raw
    if not any(isinstance(p,dict) and p.get("id")==PROOF_ID for p in proofs):
        raise SystemExit("Proof registry does not contain skill compounding moat proof")
    print(json.dumps({"status":"SITE_VERIFIED","proof":PROOF_ID}, indent=2))
if __name__=="__main__": main()
