#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; SITE=ROOT/'site'; DATA=ROOT/'data'; DOCS=ROOT/'docs'; BADGES=ROOT/'badges'
PROOF_ID='rsi-capability-treasury-flywheel-proof'; HTML=PROOF_ID+'.html'; JSON_NAME=PROOF_ID+'.json'; MD_NAME=PROOF_ID+'.md'; BADGE_NAME=PROOF_ID+'.svg'
def atomic(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile('w',delete=False,encoding='utf-8',dir=str(path.parent)) as t: t.write(text); name=t.name
    os.replace(name,path)
def load(path):
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
    proof=json.loads((DATA/JSON_NAME).read_text(encoding='utf-8')); f=proof['final']; reg=load(SITE/'proof-registry.json')
    entry={'id':PROOF_ID,'title':'Autonomous RSI Capability Treasury Flywheel Proof','href':HTML,'json':'data/'+JSON_NAME,'doc':'docs/'+MD_NAME,'badge':'badges/'+BADGE_NAME,'proved':proof['proved'],'status':proof['status'],'value_capture_rate_percent':f['value_capture_rate_percent'],'virtual_specialist_agents':proof['agent_system']['virtual_specialist_agents'],'rsi_release_count':proof['rsi_release_count'],'generated_at_utc':proof['generated_at_utc']}
    proofs=[p for p in reg['proofs'] if p.get('id')!=PROOF_ID]; proofs.insert(0,entry); reg['proofs']=proofs; reg['updated_at_utc']=proof['generated_at_utc']; atomic(SITE/'proof-registry.json',json.dumps(reg,indent=2,sort_keys=True)+'\n')
    card=f'<section id="{PROOF_ID}"><h2>Autonomous RSI Capability Treasury Flywheel Proof</h2><p>SkillOS proves proof receipts can be reinvested into skill bounties, verifier capacity, routing upgrades, and compounding capability supply.</p><p><a href="{HTML}">Open proof page</a></p></section>'
    index=SITE/'index.html'
    if index.exists():
        text=index.read_text(encoding='utf-8');
        if PROOF_ID not in text: text=text.replace('</main>',card+'</main>',1) if '</main>' in text else text+card
    else: text='<!doctype html><html><body><main>'+card+'</main></body></html>'
    atomic(index,text)
    atomic(SITE/'robots.txt','User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n')
    atomic(SITE/'sitemap.xml','<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://montrealai.github.io/skillos/</loc></url><url><loc>https://montrealai.github.io/skillos/'+HTML+'</loc></url></urlset>')
    print(json.dumps({'status':'PUBLISHED_TO_HUB','proof':PROOF_ID},indent=2))
if __name__=='__main__': main()
