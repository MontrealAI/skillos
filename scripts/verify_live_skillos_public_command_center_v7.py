#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys, time, urllib.request

MARKER="SKILLOS_PUBLIC_COMMAND_CENTER_V7_ROOT_AUTHORITY"
FORBIDDEN=["Autonomous Proof Command Center","SkillOS Proof Command Center","SkillOS Public Command Center v2","SkillOS Public Command Center v3","SkillOS Sovereign Command Center v5"]

def fetch(url: str) -> str:
    req=urllib.request.Request(url, headers={'User-Agent':'SkillOS-v7-live-verifier','Cache-Control':'no-cache'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode('utf-8', errors='ignore')

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('--base-url', default='https://montrealai.github.io/skillos/'); ap.add_argument('--retries', type=int, default=8); ap.add_argument('--delay', type=int, default=15); args=ap.parse_args()
    base=args.base_url.rstrip('/')+'/'
    last=''
    for i in range(args.retries):
        try:
            root=fetch(base+f'?v=v7-{int(time.time())}')
            idx=fetch(base+f'index.html?v=v7-{int(time.time())}')
            manifest=fetch(base+'data/command-center-manifest.json')
            ok=(MARKER in root and MARKER in idx and MARKER in manifest and 'Public SkillOS Command Center' in root and 'Public SkillOS Command Center' in idx and not any(p in root for p in FORBIDDEN) and '<h1>Capability Governance Twin' not in root)
            if ok:
                print(json.dumps({'status':'LIVE_VERIFIED','base_url':base,'marker':MARKER}, indent=2)); return
            last=f'Marker/root check failed on attempt {i+1}'
        except Exception as e:
            last=repr(e)
        time.sleep(args.delay)
    print('ERROR: live root verification failed:', last)
    sys.exit(1)
if __name__=='__main__': main()
