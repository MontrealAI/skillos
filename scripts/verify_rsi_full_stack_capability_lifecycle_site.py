#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'; PROOF_ID='rsi-full-stack-capability-lifecycle-proof'
def require(path,snippet=None):
    if not path.exists(): raise SystemExit(f'Missing {path}')
    if snippet and snippet not in path.read_text(encoding='utf-8',errors='ignore'): raise SystemExit(f'Missing {snippet!r} in {path}')
def main():
    require(SITE/f'{PROOF_ID}.html','Full-Stack Capability Lifecycle')
    require(SITE/'data'/f'{PROOF_ID}.json','PASSED_AUTONOMOUS_RSI_FULL_STACK_CAPABILITY_LIFECYCLE_PROOF')
    require(SITE/'docs'/f'{PROOF_ID}.md','Autonomous RSI Full-Stack Capability Lifecycle Proof')
    require(SITE/'badges'/f'{PROOF_ID}.svg','full-stack lifecycle RSI')
    require(SITE/'index.html',PROOF_ID); require(SITE/'proof-registry.json',PROOF_ID)
    reg=json.loads((SITE/'proof-registry.json').read_text(encoding='utf-8')); proofs=reg.get('proofs',[]) if isinstance(reg,dict) else reg
    if not any(isinstance(p,dict) and p.get('id')==PROOF_ID for p in proofs): raise SystemExit('Registry missing proof')
    print(json.dumps({'status':'SITE_VERIFIED','proof':PROOF_ID},indent=2))
if __name__=='__main__': main()
