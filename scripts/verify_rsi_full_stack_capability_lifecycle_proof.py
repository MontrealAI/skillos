#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PROOF = ROOT / 'data' / 'rsi-full-stack-capability-lifecycle-proof.json'
def fail(msg):
    print(f'ERROR: {msg}')
    raise SystemExit(1)
def main():
    if not PROOF.exists(): fail(f'Missing proof receipt: {PROOF}')
    proof=json.loads(PROOF.read_text(encoding='utf-8'))
    for key in ['proved','status','agent_system','benchmark_public','pre_registered_gates','baselines_and_controls','final','comparisons','bootstrap_confidence_intervals','rsi_releases','protocol_fingerprint_sha256']:
        if key not in proof: fail(f'Missing key: {key}')
    if not proof['proved']: fail('Proof receipt says proved=false')
    failed=[k for k,v in proof['pre_registered_gates'].items() if not v]
    if failed: fail(f'Pre-registered gates failed: {failed}')
    f=proof['final']; a=proof['agent_system']
    checks=[
        (a['virtual_specialist_agents']>=300_000_000,'virtual specialist agents must be at least 300M'),
        (a['specialist_roles']>=10_000_000,'specialist roles must be at least 10M'),
        (proof['benchmark_public']['locked_holdout_count']>=2048,'locked holdout must be at least 2048'),
        (proof['rsi_release_count']>=10,'must have at least 10 RSI releases'),
        (f['value_capture_rate_percent']>=96.0,'value capture must be at least 96%'),
        (f['minimum_domain_value_capture_percent']>=90.0,'minimum domain capture must be at least 90%'),
        (f['proxy_gaming_rate_percent']==0.0,'proxy gaming must be zero'),
        (f['risk_breach_rate_percent']==0.0,'risk breach must be zero'),
        (proof['bootstrap_confidence_intervals']['vs_strongest_control']['p05_gain_points']>0.0,'bootstrap p05 over strongest control must be positive'),
    ]
    failures=[msg for ok,msg in checks if not ok]
    if failures:
        for msg in failures: print('-',msg)
        raise SystemExit(1)
    print(json.dumps({'status':'PASSED','proof':str(PROOF.relative_to(ROOT)),'value_capture_percent':f['value_capture_rate_percent'],'strongest_control':f['strongest_control'],'gain_over_strongest_control_usd':f['benchmark_implied_value_captured_over_strongest_control_usd']}, indent=2))
if __name__=='__main__': main()
