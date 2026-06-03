#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path

REQUIRED=[
    'Public SkillOS Command Center','Aim. Act. Prove. Evolve.','GoalOS gives direction',
    'PlanOS gives strategy','SkillOS gives capability','Proof Gradient gives evolution',
    'Artifact Vault','Run Fabric','Proof Ledger','Selection Gate','Goals Used','Plans Used','Skills Used',
    'Commit Compiler','Plan Graph Resolver','Skill Resolver','Selection Gate Judge','Negative-Control Generator'
]

def fail(msg):
    print('ERROR:',msg)
    raise SystemExit(1)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',default='dist')
    args=p.parse_args()
    out=Path(args.out)
    needed=['index.html','agent-evolution-protocol.html','proof-carrying-intelligence.html','goals-plans-skills.html','proof-archive-standard.html','data/skillos-agent-evolution-protocol-kernel-v3-manifest.json','data/proof-carrying-intelligence-agent-evolution-protocol.json','proof-registry.json']
    for n in needed:
        if not (out/n).exists(): fail(f'missing {n}')
    combined=''
    for n in ['index.html','agent-evolution-protocol.html','goals-plans-skills.html','proof-archive-standard.html']:
        combined += (out/n).read_text(encoding='utf-8')
    for s in REQUIRED:
        if s not in combined: fail(f'missing text {s!r}')
    idx=(out/'index.html').read_text(encoding='utf-8')
    if '<h1>Agent Evolution Protocol' in idx or '<h1>Proof-Carrying Intelligence' in idx:
        fail('root is a protocol room, not command center')
    source=json.loads((out/'data/proof-carrying-intelligence-agent-evolution-protocol.json').read_text(encoding='utf-8'))
    if len(source.get('goals_used',[]))<7 or len(source.get('plans_used',[]))<7 or len(source.get('skills_used',[]))<16:
        fail('insufficient goals/plans/skills')
    hrefs=re.findall(r'href="([^"]+)"', combined)
    missing=[]
    for h in hrefs:
        if h.startswith(('http','#','mailto:')): continue
        target=out/h.split('#',1)[0]
        if not target.exists(): missing.append(h)
    if missing: fail('missing internal links: '+', '.join(sorted(set(missing))[:20]))
    print(json.dumps({'status':'VERIFIED','root_contract':'command_center_owns_root','goals':len(source['goals_used']),'plans':len(source['plans_used']),'skills':len(source['skills_used'])},indent=2))
if __name__=='__main__': main()
