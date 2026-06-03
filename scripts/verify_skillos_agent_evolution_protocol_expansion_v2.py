#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

REQUIRED=[
    "Public SkillOS Command Center","Aim. Act. Prove. Evolve.","GoalOS gives direction",
    "PlanOS","SkillOS","Proof Gradient","Artifact Vault","Run Fabric","Proof Ledger",
    "Selection Gate","Goals Used","Plans Used","Skills Used","Commit Compiler",
    "Artifact Vault Curator","Command Center Integrator","Every job leaves proof"
]

def fail(msg):
    print("ERROR:", msg)
    raise SystemExit(1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="dist")
    args=p.parse_args()
    out=Path(args.out)
    required_files=[
        "index.html","proof-carrying-intelligence.html","agent-evolution-protocol.html",
        "goals-plans-skills.html","skills.html","proof-archive-standard.html",
        "data/skillos-agent-evolution-protocol-expansion-v2-manifest.json",
        "data/proof-carrying-intelligence-agent-evolution-protocol.json",
        "docs/PROOF_CARRYING_INTELLIGENCE_AGENT_EVOLUTION_PROTOCOL.md",
        "badges/proof-carrying-intelligence.svg","proof-registry.json"
    ]
    for rel in required_files:
        if not (out/rel).exists(): fail(f"missing {rel}")
    combined=""
    for rel in ["index.html","proof-carrying-intelligence.html","goals-plans-skills.html","proof-archive-standard.html"]:
        combined += (out/rel).read_text(encoding="utf-8")
    for snippet in REQUIRED:
        if snippet not in combined: fail(f"missing snippet {snippet!r}")
    idx=(out/"index.html").read_text(encoding="utf-8")
    if "<h1>The Agent Evolution Protocol" in idx or "<h1>Proof-Carrying Intelligence" in idx:
        fail("root appears to be protocol room, not command center")
    receipt=json.loads((out/"data/proof-carrying-intelligence-agent-evolution-protocol.json").read_text(encoding="utf-8"))
    if not receipt.get("proved"): fail("receipt is not proved")
    metrics=receipt["metrics"]
    checks=[
        (metrics["negative_control_rejection_rate_percent"] == 100, "negative control rejection must be 100%"),
        (metrics["archive_completeness_rate_percent"] == 100, "archive completeness must be 100%"),
        (metrics["internal_link_integrity_rate_percent"] == 100, "internal link integrity must be 100%"),
        (metrics["root_contract_preserved"] is True, "root contract must be preserved"),
        (len(receipt["goals_used"]) >= 7, "goals count"),
        (len(receipt["plans_used"]) >= 7, "plans count"),
        (len(receipt["skills_used"]) >= 14, "skills count"),
    ]
    problems=[msg for ok,msg in checks if not ok]
    if problems: fail("; ".join(problems))
    hrefs=re.findall(r'href="([^"]+)"', combined)
    missing=[]
    for h in hrefs:
        if h.startswith(("http","#","mailto:")): continue
        target=out/h.split("#",1)[0]
        if not target.exists(): missing.append(h)
    if missing: fail("missing internal links: "+", ".join(sorted(set(missing))[:30]))
    print(json.dumps({"status":"VERIFIED","mode":"additive-expansion-no-removal","root_contract":"command_center_owns_root"},indent=2))
if __name__=="__main__":
    main()
