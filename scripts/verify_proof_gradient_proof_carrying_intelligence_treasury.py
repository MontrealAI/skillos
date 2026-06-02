#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
from html.parser import HTMLParser

PID='proof-gradient-proof-carrying-intelligence-treasury'
MARKER='SKILLOS_PROOF_GRADIENT_PROOF_CARRYING_INTELLIGENCE_TREASURY_V1'
REQUIRED=['index.html','proof-gradient-proof-carrying-intelligence-treasury.html','goals.html','plans.html','skills.html','receipts.html','run.html','architecture.html','health.html',f'data/{PID}.json','data/command-center-manifest.json','proof-registry.json','docs/PROOF_GRADIENT_PROOF_CARRYING_INTELLIGENCE_TREASURY_PROOF.md',f'badges/{PID}.svg','version.txt','.nojekyll']
FORBIDDEN=['Autonomous Proof Command Center','SkillOS Proof Command Center','SkillOS Sovereign Command Center v5','SkillOS Public Command Center v2','SkillOS Public Command Center v3']
class P(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]
    def handle_starttag(self, tag, attrs):
        for k,v in attrs:
            if k in ('href','src') and v: self.links.append(v)
def fail(m): print('ERROR:',m,file=sys.stderr); sys.exit(1)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',default='dist'); args=ap.parse_args(); out=Path(args.out)
    missing=[p for p in REQUIRED if not (out/p).exists()]
    if missing: fail('Missing required files: '+', '.join(missing))
    root=(out/'index.html').read_text(encoding='utf-8')
    if 'Public SkillOS Command Center' not in root: fail('Root does not contain Public SkillOS Command Center')
    for f in FORBIDDEN:
        if f in root: fail('Forbidden legacy root phrase present: '+f)
    proof=(out/'proof-gradient-proof-carrying-intelligence-treasury.html').read_text(encoding='utf-8')
    for t in ['Goals Used','Plans Used','Skills Used','Kardashev-scale mechanism','Commit','Execute','Prove','Evolve','Proof-Carrying Intelligence Treasury']:
        if t not in proof: fail('Proof page missing required text: '+t)
    r=json.loads((out/f'data/{PID}.json').read_text(encoding='utf-8'))
    if not r.get('passed'): fail('Receipt is not passed')
    if len(r.get('goals_used',[])) < 7: fail('Too few goals')
    if len(r.get('plans_used',[])) < 6: fail('Too few plans')
    if len(r.get('skills_used',[])) < 12: fail('Too few skills')
    if r.get('observed',{}).get('negative_control_rejection_rate',0) < 0.99: fail('Negative control rejection too low')
    if r.get('observed',{}).get('risk_breach_rate',1) > 0.02: fail('Risk breach too high')
    m=json.loads((out/'data/command-center-manifest.json').read_text(encoding='utf-8'))
    if m.get('marker') != MARKER: fail('Manifest marker mismatch')
    bad=[]
    for hp in out.glob('*.html'):
        parser=P(); parser.feed(hp.read_text(encoding='utf-8'))
        for link in parser.links:
            if link.startswith(('http://','https://','mailto:','#','javascript:')): continue
            clean=link.split('#')[0].split('?')[0]
            if clean and not (out/clean).exists(): bad.append(f'{hp.name}->{clean}')
    if bad: fail('Missing internal links: '+', '.join(bad[:50]))
    print(json.dumps({'verified':True,'out':str(out),'marker':MARKER,'proof':PID,'pages':len(list(out.glob('*.html')))},indent=2))
if __name__=='__main__': main()
