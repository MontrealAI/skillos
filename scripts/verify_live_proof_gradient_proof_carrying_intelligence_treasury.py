#!/usr/bin/env python3
import json, sys, time, urllib.request
BASE='https://montrealai.github.io/skillos/'
MARKER='SKILLOS_PROOF_GRADIENT_PROOF_CARRYING_INTELLIGENCE_TREASURY_V1'
def fetch(path):
    with urllib.request.urlopen(BASE+path, timeout=25) as r: return r.read().decode('utf-8',errors='replace')
def fail(m): print('ERROR:',m,file=sys.stderr); sys.exit(1)
def main():
    time.sleep(8)
    root=fetch('?v=proof-gradient-pci'); index=fetch('index.html?v=proof-gradient-pci'); proof=fetch('proof-gradient-proof-carrying-intelligence-treasury.html?v=proof-gradient-pci'); manifest=fetch('data/command-center-manifest.json?v=proof-gradient-pci')
    if 'Public SkillOS Command Center' not in root: fail('Live root is not Public SkillOS Command Center')
    if 'Public SkillOS Command Center' not in index: fail('Live index is not Public SkillOS Command Center')
    if 'Proof-Carrying Intelligence Treasury' not in proof: fail('Live proof page missing title')
    if MARKER not in manifest: fail('Live manifest marker mismatch')
    for bad in ['Autonomous Proof Command Center','SkillOS Sovereign Command Center v5']:
        if bad in root: fail('Live root contains legacy phrase: '+bad)
    print(json.dumps({'live_verified':True,'base':BASE,'marker':MARKER},indent=2))
if __name__=='__main__': main()
