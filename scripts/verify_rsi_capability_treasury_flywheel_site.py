#!/usr/bin/env python3
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'; PROOF_ID='rsi-capability-treasury-flywheel-proof'
def req(p,s):
    if not p.exists(): raise SystemExit(f'Missing {p}')
    if s not in p.read_text(encoding='utf-8',errors='ignore'): raise SystemExit(f'Missing {s} in {p}')
def main():
    req(SITE/(PROOF_ID+'.html'),'Capability Treasury Flywheel'); req(SITE/'data'/(PROOF_ID+'.json'),'PASSED_AUTONOMOUS_RSI_CAPABILITY_TREASURY_FLYWHEEL_PROOF'); req(SITE/'docs'/(PROOF_ID+'.md'),'Capability Treasury Flywheel'); req(SITE/'index.html',PROOF_ID); req(SITE/'proof-registry.json',PROOF_ID); print(json.dumps({'status':'SITE_VERIFIED','proof':PROOF_ID},indent=2))
if __name__=='__main__': main()
