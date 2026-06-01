#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/"site"
REQUIRED=["index.html","executive.html","proofs.html","actions.html","skills.html","receipts.html","multi-agent.html","architecture.html","flywheel.html","health.html","runbook.html","404.html","force-refresh.html","proof-registry.json","data/command-center-manifest.json","data/command-center-health.json","badges/command-center-fresh.svg","sitemap.xml","robots.txt",".nojekyll","version.txt"]
def fail(msg): print("ERROR:",msg); raise SystemExit(1)
def req(rel):
    p=SITE/rel
    if not p.exists(): fail(f"missing site/{rel}")
    return p
def contains(rel,snippet):
    if snippet not in req(rel).read_text(encoding="utf-8",errors="ignore"): fail(f"missing {snippet!r} in site/{rel}")
def main():
    for rel in REQUIRED: req(rel)
    for s in ["Public SkillOS Command Center","SkillOS Public Command Center v3","Every job can become a reusable skill","Operational skill stack","Run or regenerate","command-center-manifest.json"]: contains("index.html",s)
    if "Autonomous Proof Command Center" in req("index.html").read_text(encoding="utf-8",errors="ignore"): fail("old homepage copy still present")
    for s in ["SkillOS turns work into compounding capability","One agent learns. The network levels up."]: contains("executive.html",s)
    for s in ["Skills Used","agent system"]: contains("skills.html",s)
    for s in ["Command Center Health","command-center-health.json"]: contains("health.html",s)
    for s in ["Run / Regenerate","SkillOS Command Center Autopublisher v3","deploy_pages=true"]: contains("actions.html",s)
    for s in ["Many agents are not the moat","Verified skill compounding is the moat","Skills Used across the network"]: contains("multi-agent.html",s)
    manifest=json.loads(req("data/command-center-manifest.json").read_text())
    registry=json.loads(req("proof-registry.json").read_text())
    health=json.loads(req("data/command-center-health.json").read_text())
    if manifest.get("schema")!="skillos.command_center.v3": fail("bad manifest schema")
    if not isinstance(registry,dict) or not isinstance(registry.get("proofs",[]),list): fail("registry must be object with proofs list")
    if manifest.get("counts",{}).get("workflows_indexed",0)<1: fail("no workflows indexed")
    if manifest.get("counts",{}).get("skills_surfaced",0)<9: fail("too few skills surfaced")
    if health.get("status")!="fresh": fail("health not fresh")
    for p in registry.get("proofs",[]):
        href=p.get("href","")
        if href.endswith(".html") and not (SITE/href).exists(): fail(f"proof page missing for {href}")
    wf=ROOT/".github/workflows/skillos-command-center-autopublisher-v3.yml"
    if wf.exists():
        text=wf.read_text()
        for s in ["workflow_dispatch","schedule","push","actions/deploy-pages@v4","publish_to_repo","deploy_pages"]:
            if s not in text: fail(f"workflow missing {s}")
    print(json.dumps({"status":"VERIFIED_SKILLOS_COMMAND_CENTER_V3","proofs_indexed":manifest["counts"]["proofs_indexed"],"workflows_indexed":manifest["counts"]["workflows_indexed"],"skills_surfaced":manifest["counts"]["skills_surfaced"],"generated_at_utc":manifest["generated_at_utc"]},indent=2,sort_keys=True))
if __name__=="__main__":
    main()
