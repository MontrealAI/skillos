#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SITE,DATA,DOCS,BADGES=ROOT/'site',ROOT/'data',ROOT/'docs',ROOT/'badges'
PROOF_ID='rsi-full-stack-capability-lifecycle-proof'
TITLE='Autonomous RSI Full-Stack Capability Lifecycle Proof'
HTML,JSON_NAME,MD_NAME,BADGE_NAME=f'{PROOF_ID}.html',f'{PROOF_ID}.json',f'{PROOF_ID}.md',f'{PROOF_ID}.svg'
def atomic_write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('w',delete=False,encoding='utf-8',dir=str(path.parent)) as tmp:
        tmp.write(text); name=tmp.name
    os.replace(name,path)
def load_registry(path):
    if not path.exists(): return {'proofs':[]}
    try: raw=json.loads(path.read_text(encoding='utf-8'))
    except Exception: return {'proofs':[]}
    if isinstance(raw,list): return {'proofs':[x for x in raw if isinstance(x,dict)]}
    if isinstance(raw,dict): raw['proofs']=[x for x in raw.get('proofs',[]) if isinstance(x,dict)]; return raw
    return {'proofs':[]}
def main():
    SITE.mkdir(parents=True,exist_ok=True)
    for d in ['data','docs','badges']:(SITE/d).mkdir(exist_ok=True)
    shutil.copy2(DATA/JSON_NAME,SITE/'data'/JSON_NAME); shutil.copy2(DOCS/MD_NAME,SITE/'docs'/MD_NAME); shutil.copy2(BADGES/BADGE_NAME,SITE/'badges'/BADGE_NAME)
    proof=json.loads((DATA/JSON_NAME).read_text(encoding='utf-8')); reg=load_registry(SITE/'proof-registry.json')
    entry={'id':PROOF_ID,'title':TITLE,'href':HTML,'json':f'data/{JSON_NAME}','doc':f'docs/{MD_NAME}','badge':f'badges/{BADGE_NAME}','status':proof['status'],'proved':proof['proved'],'value_capture_rate_percent':proof['final']['value_capture_rate_percent'],'minimum_domain_value_capture_percent':proof['final']['minimum_domain_value_capture_percent'],'virtual_specialist_agents':proof['agent_system']['virtual_specialist_agents'],'specialist_roles':proof['agent_system']['specialist_roles'],'rsi_release_count':proof['rsi_release_count'],'generated_at_utc':proof['generated_at_utc']}
    proofs=[p for p in reg.get('proofs',[]) if p.get('id')!=PROOF_ID and p.get('href')!=HTML]; proofs.insert(0,entry); reg['proofs']=proofs; reg['updated_at_utc']=proof['generated_at_utc']; atomic_write(SITE/'proof-registry.json',json.dumps(reg,indent=2,sort_keys=True)+'\n')
    card=f'''<section id="{PROOF_ID}" style="margin:32px 0;padding:28px;border:1px solid rgba(255,255,255,.16);border-radius:28px;background:rgba(255,255,255,.07)"><p style="color:#86f8ff;text-transform:uppercase;letter-spacing:.18em;font-weight:900;font-size:12px">New autonomous proof</p><h2 style="font-size:clamp(30px,4.5vw,58px);line-height:.95;margin:0 0 12px">{TITLE}</h2><p style="color:#b8c8d8;font-size:18px;line-height:1.55">SkillOS proves the full lifecycle: demand, decomposition, routing, execution traces, provenance, verification, objective integrity, transfer, replication, drift control, releases, and future routing.</p><p><a href="{HTML}" style="display:inline-block;padding:12px 18px;border-radius:999px;background:#86f8ff;color:#06131f;font-weight:900;text-decoration:none">Open proof page</a></p></section>'''
    idx=SITE/'index.html'
    if idx.exists():
        text=idx.read_text(encoding='utf-8')
        if PROOF_ID not in text:
            text=text.replace('</main>',card+'\n</main>',1) if '</main>' in text else text+card; atomic_write(idx,text)
    else: atomic_write(idx,f'<!doctype html><html><body><main>{card}</main></body></html>')
    sm=SITE/'sitemap.xml'; urls=['https://montrealai.github.io/skillos/',f'https://montrealai.github.io/skillos/{HTML}']
    if sm.exists():
        s=sm.read_text(encoding='utf-8')
        for u in urls:
            if u not in s: s=s.replace('</urlset>',f'<url><loc>{u}</loc></url>\n</urlset>') if '</urlset>' in s else s+f'\n{u}\n'
        atomic_write(sm,s)
    else: atomic_write(sm,'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{u}</loc></url>' for u in urls)+'</urlset>')
    if not (SITE/'robots.txt').exists(): atomic_write(SITE/'robots.txt','User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n')
    print(json.dumps({'status':'PUBLISHED_TO_HUB','proof':PROOF_ID},indent=2))
if __name__=='__main__': main()
