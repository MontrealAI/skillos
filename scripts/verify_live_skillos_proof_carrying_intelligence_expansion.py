#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, urllib.request
MARKER='SKILLOS_PROOF_CARRYING_INTELLIGENCE_EXPANSION_V1'
def fetch(url):
    with urllib.request.urlopen(url,timeout=30) as r: return r.read().decode('utf-8','replace')
def main():
    p=argparse.ArgumentParser(); p.add_argument('--base-url',default='https://montrealai.github.io/skillos/'); a=p.parse_args(); base=a.base_url.rstrip('/')+'/'
    root=fetch(base+'?v=pci-expansion'); manifest=fetch(base+'data/skillos-proof-carrying-intelligence-expansion-manifest.json?v=pci-expansion')
    if 'Public SkillOS Command Center' not in root: raise SystemExit('root is not Public SkillOS Command Center')
    if MARKER not in manifest: raise SystemExit('live manifest marker mismatch')
    print(json.dumps({'status':'LIVE_VERIFIED','base_url':base},indent=2))
if __name__=='__main__': main()
