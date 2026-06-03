#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
MARKER='SKILLOS_PROOF_CARRYING_INTELLIGENCE_EXPANSION_V1'
REQUIRED=['Public SkillOS Command Center','Aim. Act. Prove. Evolve.','Proof-Carrying Intelligence','GoalOS gives the network direction','PlanOS gives it strategy','SkillOS gives it capability','Proof Gradient gives it evolution','Artifact Vault','Run Fabric','Proof Ledger','Selection Gate','Goals Used','Plans Used','Skills Used','Commit Compiler','Selection Gate Judge']
FORBIDDEN_ROOT=['<h1>Capability Governance Twin','<h1>Proof-Carrying Intelligence.</h1>']
def fail(msg): print('ERROR: '+msg); raise SystemExit(1)
def main():
    p=argparse.ArgumentParser(); p.add_argument('--out',default='dist'); a=p.parse_args(); out=Path(a.out)
    for path in [out/'index.html',out/'proof-carrying-intelligence.html',out/'goals-plans-skills.html',out/'data'/'skillos-proof-carrying-intelligence-expansion-manifest.json',out/'data'/'proof-carrying-intelligence-agent-evolution-protocol.json',out/'proof-registry.json']:
        if not path.exists(): fail(f'missing {path}')
    root=(out/'index.html').read_text(encoding='utf-8')
    for s in FORBIDDEN_ROOT:
        if s in root: fail('root contract violated by '+s)
    combined=''.join(p.read_text(encoding='utf-8',errors='ignore') for p in [out/'index.html',out/'proof-carrying-intelligence.html',out/'goals-plans-skills.html'])
    for s in REQUIRED:
        if s not in combined: fail('missing required text: '+s)
    manifest=json.loads((out/'data'/'skillos-proof-carrying-intelligence-expansion-manifest.json').read_text(encoding='utf-8'))
    if manifest.get('marker')!=MARKER: fail('manifest marker mismatch')
    receipt=json.loads((out/'data'/'proof-carrying-intelligence-agent-evolution-protocol.json').read_text(encoding='utf-8'))
    if len(receipt.get('goals_used',[]))<7 or len(receipt.get('plans_used',[]))<7 or len(receipt.get('skills_used',[]))<14: fail('goals/plans/skills receipt incomplete')
    hrefs=re.findall(r'href="([^"]+)"', combined); missing=[]
    for h in hrefs:
        if h.startswith(('http','#','mailto:')): continue
        if not (out/h.split('#',1)[0]).exists(): missing.append(h)
    if missing: fail('missing internal links: '+', '.join(sorted(set(missing))[:30]))
    print(json.dumps({'status':'VERIFIED','marker':MARKER,'root_contract':'command_center_owns_root'},indent=2))
if __name__=='__main__': main()
