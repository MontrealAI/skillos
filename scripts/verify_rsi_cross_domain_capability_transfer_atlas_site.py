#!/usr/bin/env python3
from pathlib import Path

PROOF_ID = "rsi-cross-domain-capability-transfer-atlas-proof"

def require(x, msg):
    if not x:
        raise SystemExit(f"site verification failed: {msg}")

def main():
    site=Path('site')
    page=site/f'{PROOF_ID}.html'
    index=site/'index.html'
    registry=site/'proof-registry.json'
    for p in [page,index,registry,site/'data'/f'{PROOF_ID}.json',site/'docs'/f'{PROOF_ID}.md',site/'badges'/f'{PROOF_ID}.svg']:
        require(p.exists(), f"missing {p}")
    text=page.read_text(encoding='utf-8')
    require('Capability transfer is the moat' in text, 'missing hero')
    require('Run proof on GitHub' in text, 'missing run CTA')
    require('public_safe_claim' not in text, 'unrendered JSON key leaked')
    require('does not claim achieved superintelligence' in text, 'missing public-safe boundary')
    idx=index.read_text(encoding='utf-8')
    require(PROOF_ID in idx, 'command center does not link proof')
    print('Cross-domain transfer atlas site verification passed.')
if __name__=='__main__': main()
