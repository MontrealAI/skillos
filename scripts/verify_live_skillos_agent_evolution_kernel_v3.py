#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, urllib.request

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode('utf-8','replace')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--base-url',default='https://montrealai.github.io/skillos/')
    args=p.parse_args()
    base=args.base_url.rstrip('/')+'/'
    root=fetch(base+'?v=agent-evolution-kernel-v3')
    manifest=fetch(base+'data/skillos-agent-evolution-protocol-kernel-v3-manifest.json?v=agent-evolution-kernel-v3')
    if 'Public SkillOS Command Center' not in root:
        raise SystemExit('root missing Public SkillOS Command Center')
    if 'SKILLOS_AGENT_EVOLUTION_PROTOCOL_KERNEL_V3' not in manifest:
        raise SystemExit('manifest marker missing')
    print(json.dumps({'status':'LIVE_VERIFIED','base_url':base},indent=2))
if __name__=='__main__': main()
