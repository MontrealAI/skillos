#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; PROOF=ROOT/'data'/'rsi-capability-treasury-flywheel-proof.json'
def main():
    if not PROOF.exists(): raise SystemExit(f'Missing proof receipt: {PROOF}')
    proof=json.loads(PROOF.read_text(encoding='utf-8'))
    if not proof.get('proved'): raise SystemExit('Proof receipt says proved=false')
    failed=[k for k,v in proof['pre_registered_gates'].items() if not v]
    if failed: raise SystemExit(f'Pre-registered gates failed: {failed}')
    print(json.dumps({'status':'PASSED','proof':str(PROOF.relative_to(ROOT)),'value_capture_percent':proof['final']['value_capture_rate_percent'],'rsi_releases':proof['rsi_release_count']}, indent=2, sort_keys=True))
if __name__=='__main__': main()
