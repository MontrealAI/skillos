#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
from html.parser import HTMLParser

SCHEMA="skillos.public_command_center.root_authority.v7"
MARKER="SKILLOS_PUBLIC_COMMAND_CENTER_V7_ROOT_AUTHORITY"
FORBIDDEN=["Autonomous Proof Command Center","SkillOS Proof Command Center","SkillOS Public Command Center v2","SkillOS Public Command Center v3","SkillOS Sovereign Command Center v5"]

class LinkParser(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for k,v in attrs:
                if k=='href' and v: self.links.append(v)

def fail(msg: str) -> None:
    print(f"ERROR: {msg}")
    raise SystemExit(1)

def read(path: Path) -> str:
    if not path.exists(): fail(f"Missing file: {path}")
    return path.read_text(encoding='utf-8', errors='ignore')

def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument('--out', default='dist'); args=ap.parse_args()
    out=Path(args.out).resolve()
    index=read(out/'index.html')
    if MARKER not in index: fail('Root index missing v7 marker')
    if 'Public SkillOS Command Center' not in index: fail('Root index is not the Public SkillOS Command Center')
    for phrase in FORBIDDEN:
        if phrase in index: fail(f'Forbidden legacy phrase appears in root: {phrase}')
    if '<h1>Capability Governance Twin' in index or '<h1>Capability Governance Twin</h1>' in index:
        fail('Root was replaced by Capability Governance Twin h1')
    flag=read(out/'capability-governance-twin.html')
    if 'Capability Governance Twin' not in flag: fail('Flagship subpage missing Capability Governance Twin')
    if 'Root contract preserved' not in flag: fail('Flagship page missing root contract notice')
    skills=read(out/'skills.html')
    for snippet in ['Skills Used','Governance Twin Construction','Policy-as-Code Compilation','Release Gating','Command Center Publication']:
        if snippet not in skills and snippet not in index and snippet not in flag:
            fail(f'Missing skill/display snippet: {snippet}')
    manifest=json.loads(read(out/'data/command-center-manifest.json'))
    if manifest.get('schema') != SCHEMA or manifest.get('marker') != MARKER: fail('Manifest schema/marker mismatch')
    if manifest.get('source_of_truth','').lower().find('html is generated') < 0: fail('Manifest does not state generated source of truth')
    registry=json.loads(read(out/'proof-registry.json'))
    if registry.get('marker') != MARKER: fail('Proof registry marker mismatch')
    # local link check for internal generated pages and copied assets
    parser=LinkParser(); parser.feed(index + flag + skills + read(out/'proofs.html'))
    missing=[]
    for href in parser.links:
        if href.startswith(('http://','https://','#','mailto:')): continue
        href=href.split('#',1)[0].split('?',1)[0]
        if not href: continue
        if not (out/href).exists(): missing.append(href)
    if missing:
        fail('Missing internal links: '+', '.join(sorted(set(missing))[:20]))
    print(json.dumps({'status':'VERIFIED','schema':SCHEMA,'marker':MARKER,'root':'Public SkillOS Command Center','flagship':'capability-governance-twin.html','proofs':len(registry.get('proofs',[])),'skills_page_verified':True}, indent=2, sort_keys=True))

if __name__=='__main__': main()
