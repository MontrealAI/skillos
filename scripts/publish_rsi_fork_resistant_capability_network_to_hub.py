#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE, DATA, DOCS, BADGES = ROOT/'site', ROOT/'data', ROOT/'docs', ROOT/'badges'
PROOF_ID = 'rsi-fork-resistant-capability-network-proof'
TITLE = 'Autonomous RSI Fork-Resistant Capability Network Proof'
HTML, JSON_NAME, MD_NAME, BADGE_NAME = f'{PROOF_ID}.html', f'{PROOF_ID}.json', f'{PROOF_ID}.md', f'{PROOF_ID}.svg'

def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile('w', delete=False, encoding='utf-8', dir=str(path.parent)) as tmp:
        tmp.write(text); name=tmp.name
    os.replace(name, path)

def load_registry(path: Path) -> dict:
    if not path.exists(): return {'proofs':[]}
    try: raw=json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {'proofs':[]}
    if isinstance(raw, list): return {'proofs':[x for x in raw if isinstance(x,dict)]}
    if isinstance(raw, dict):
        proofs=raw.get('proofs',[])
        raw['proofs']=[x for x in proofs if isinstance(x,dict)] if isinstance(proofs,list) else []
        return raw
    return {'proofs':[]}

def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    for d in ['data','docs','badges']: (SITE/d).mkdir(exist_ok=True)
    shutil.copy2(DATA/JSON_NAME, SITE/'data'/JSON_NAME)
    shutil.copy2(DOCS/MD_NAME, SITE/'docs'/MD_NAME)
    shutil.copy2(BADGES/BADGE_NAME, SITE/'badges'/BADGE_NAME)
    proof=json.loads((DATA/JSON_NAME).read_text(encoding='utf-8'))
    registry=load_registry(SITE/'proof-registry.json')
    f=proof['final']
    entry={'id':PROOF_ID,'title':TITLE,'href':HTML,'json':f'data/{JSON_NAME}','doc':f'docs/{MD_NAME}','badge':f'badges/{BADGE_NAME}','status':proof['status'],'proved':proof['proved'],'value_capture_rate_percent':f['value_capture_rate_percent'],'minimum_domain_value_capture_percent':f['minimum_domain_value_capture_percent'],'fork_resistance_score':f['fork_resistance_score'],'virtual_specialist_agents':proof['agent_system']['virtual_specialist_agents'],'specialist_roles':proof['agent_system']['specialist_roles'],'rsi_release_count':proof['rsi_release_count'],'generated_at_utc':proof['generated_at_utc']}
    proofs=[p for p in registry.get('proofs',[]) if p.get('id')!=PROOF_ID and p.get('href')!=HTML]
    proofs.insert(0,entry); registry['proofs']=proofs; registry['updated_at_utc']=proof['generated_at_utc']
    atomic_write(SITE/'proof-registry.json', json.dumps(registry,indent=2,sort_keys=True)+'\n')
    card=f'''<section id="{PROOF_ID}" style="margin:32px 0;padding:28px;border:1px solid rgba(255,255,255,.16);border-radius:28px;background:rgba(255,255,255,.07)">
<p style="color:#86f8ff;text-transform:uppercase;letter-spacing:.18em;font-weight:900;font-size:12px">New autonomous proof</p>
<h2 style="font-size:clamp(30px,4.5vw,58px);line-height:.95;margin:0 0 12px">Autonomous RSI Fork-Resistant Capability Network Proof</h2>
<p style="color:#b8c8d8;font-size:18px;line-height:1.55">SkillOS proves that verified skill graphs, provenance ledgers, trust/liquidity flywheels, and network-wide routing releases resist surface-level forks and keep compounding.</p>
<p><a href="{HTML}" style="display:inline-block;padding:12px 18px;border-radius:999px;background:#86f8ff;color:#06131f;font-weight:900;text-decoration:none">Open proof page</a></p>
</section>'''
    index=SITE/'index.html'
    if index.exists():
        text=index.read_text(encoding='utf-8')
        if PROOF_ID not in text:
            text=text.replace('</main>', card+'\n</main>', 1) if '</main>' in text else text+card
        atomic_write(index,text)
    else:
        atomic_write(index, f'<!doctype html><html><body><main>{card}</main></body></html>')
    sitemap=SITE/'sitemap.xml'
    urls=['https://montrealai.github.io/skillos/', f'https://montrealai.github.io/skillos/{HTML}']
    if sitemap.exists():
        old=sitemap.read_text(encoding='utf-8')
        for url in urls:
            if url not in old:
                old=old.replace('</urlset>', f'<url><loc>{url}</loc></url>\n</urlset>') if '</urlset>' in old else old+f'\n{url}\n'
        atomic_write(sitemap, old)
    else:
        atomic_write(sitemap, '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9)">' + ''.join(f'<url><loc>{u}</loc></url>' for u in urls) + '</urlset>')
    if not (SITE/'robots.txt').exists():
        atomic_write(SITE/'robots.txt', 'User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n')
    print(json.dumps({'status':'PUBLISHED_TO_HUB','proof':PROOF_ID}, indent=2))

if __name__ == '__main__':
    main()
