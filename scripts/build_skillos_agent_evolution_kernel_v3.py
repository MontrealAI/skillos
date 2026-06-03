#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, json, re, shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "proof_carrying_intelligence_kernel_v3_source.json"
MARKER = "SKILLOS_AGENT_EVOLUTION_PROTOCOL_KERNEL_V3"
SCHEMA = "skillos.agent_evolution_protocol.kernel.v3"

CSS = """
:root{--bg:#05070d;--panel:rgba(255,255,255,.075);--panel2:rgba(255,255,255,.115);--line:rgba(255,255,255,.16);--text:#f6fbff;--muted:#b7c6d8;--cyan:#86f8ff;--green:#7dffb0;--gold:#ffd66b;--rose:#ff9cf5}*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,sans-serif;background:radial-gradient(circle at 88% 0,#5a4aa6 0,transparent 32%),radial-gradient(circle at 0 10%,#0b7d89 0,transparent 25%),linear-gradient(135deg,#05070d,#0c1830 55%,#261a49);color:var(--text)}body:before{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:44px 44px;pointer-events:none;mask-image:linear-gradient(to bottom,rgba(0,0,0,.9),rgba(0,0,0,.05))}a{color:var(--cyan)}main{max-width:1240px;margin:0 auto;padding:44px 20px 90px;position:relative}nav{position:sticky;top:0;z-index:5;background:rgba(5,7,13,.86);border-bottom:1px solid var(--line);backdrop-filter:blur(18px);display:flex;justify-content:space-between;align-items:center;padding:14px 22px}nav a{color:var(--muted);text-decoration:none;font-weight:850;margin-left:14px}.brand{font-weight:950;letter-spacing:-.02em}h1{font-size:clamp(46px,7vw,104px);line-height:.85;letter-spacing:-.08em;margin:10px 0 18px}h2{font-size:clamp(31px,4vw,58px);letter-spacing:-.055em;margin:42px 0 12px}p{color:var(--muted);font-size:18px;line-height:1.55}.eyebrow{color:var(--cyan);text-transform:uppercase;letter-spacing:.18em;font-weight:950;font-size:12px}.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:24px;align-items:center}.card,.metric,.notice,.protocol{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:30px;padding:24px;box-shadow:0 26px 90px rgba(0,0,0,.28)}.quote{font-size:clamp(25px,3.1vw,44px);line-height:1.08;letter-spacing:-.045em}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}.metric strong{display:block;color:var(--green);font-size:32px}.metric span{color:var(--muted)}.protocol{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}.step{border:1px solid var(--line);border-radius:22px;padding:18px;background:rgba(255,255,255,.055)}.step b{display:block;color:var(--gold);font-size:21px}.step span{color:var(--muted)}.card-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}.card-item{background:rgba(255,255,255,.07);border:1px solid var(--line);border-radius:24px;padding:18px;min-height:245px}.card-item h3{font-size:22px;letter-spacing:-.03em;margin:9px 0}.pill{display:inline-block;border:1px solid rgba(134,248,255,.35);color:var(--cyan);border-radius:999px;padding:5px 9px;font-size:11px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}dl{margin:12px 0 0}dt{color:var(--green);font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.08em;margin-top:9px}dd{margin:3px 0 0;color:var(--muted);font-size:13px;line-height:1.35}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:20px;overflow:hidden;margin:16px 0}td,th{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--muted);text-transform:uppercase;font-size:12px;letter-spacing:.08em}.notice{border-left:4px solid var(--gold);color:var(--muted)}.flow{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:clamp(18px,2.4vw,34px);line-height:1.35;color:var(--text)}@media(max-width:950px){.hero,.grid,.protocol,.card-grid{grid-template-columns:1fr}}
"""

def esc(x: Any) -> str:
    return html.escape(str(x if x is not None else ""))

def slug(text: Any) -> str:
    s = str(text if text is not None else "item").lower()
    s = re.sub(r"[^a-z0-9]+","-",s).strip("-")
    return s or "item"

def copy_tree(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copytree(src, dst, dirs_exist_ok=True)

def page(title: str, body: str) -> str:
    nav = '<nav><div class="brand">Public SkillOS Command Center</div><div><a href="index.html">Home</a><a href="agent-evolution-protocol.html">Protocol</a><a href="goals-plans-skills.html">Goals / Plans / Skills</a><a href="proof-archive-standard.html">Archive</a></div></nav>'
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><style>{CSS}</style></head><body>{nav}<main>{body}</main></body></html>'

def cards(items, kind):
    out=[]
    for item in items:
        if kind == 'goal':
            out.append(f'<article class="card-item"><div class="pill">GoalOS</div><h3>{esc(item["name"])}</h3><p>{esc(item["direction"])}</p><dl><dt>Measure</dt><dd>{esc(item["measure"])}</dd><dt>Threshold</dt><dd>{esc(item["threshold"])}</dd><dt>Why</dt><dd>{esc(item["why"])}</dd></dl></article>')
        elif kind == 'plan':
            out.append(f'<article class="card-item"><div class="pill">PlanOS</div><h3>{esc(item["name"])}</h3><p>{esc(item["strategy"])}</p><dl><dt>Steps</dt><dd>{esc(" → ".join(item["steps"]))}</dd><dt>Linked goals</dt><dd>{esc(", ".join(item["linked_goals"]))}</dd><dt>Risk budget</dt><dd>{esc(item["risk_budget"])}</dd></dl></article>')
        elif kind == 'skill':
            out.append(f'<article class="card-item"><div class="pill">{esc(item["layer"])}</div><h3>{esc(item["name"])}</h3><p>{esc(item["purpose"])}</p><dl><dt>Input</dt><dd>{esc(item["input_signal"])}</dd><dt>Output</dt><dd>{esc(item["output"])}</dd><dt>Verifier</dt><dd>{esc(item["verifier"])}</dd></dl></article>')
        elif kind == 'system':
            out.append(f'<article class="card-item"><div class="pill">{esc(item["role"])}</div><h3>{esc(item["name"])}</h3><p>{esc(item["description"])}</p></article>')
        else:
            out.append(f'<article class="card-item"><div class="pill">{esc(item["system"])}</div><h3>{esc(item["class"])}</h3><p>{esc(item["examples"])}</p></article>')
    return '<div class="card-grid">'+''.join(out)+'</div>'

def table(rows, cols):
    head=''.join(f'<th>{esc(label)}</th>' for _,label in cols)
    body=[]
    for row in rows:
        body.append('<tr>'+''.join(f'<td>{esc(row.get(key,""))}</td>' for key,_ in cols)+'</tr>')
    return '<table><thead><tr>'+head+'</tr></thead><tbody>'+''.join(body)+'</tbody></table>'

def discover_proofs(root: Path):
    proofs=[]
    for path in sorted(set(list((root/'data').glob('*.json')) + list((root/'site'/'data').glob('*.json')))):
        try:
            raw=json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            continue
        if isinstance(raw, dict) and ('proof' in path.name or raw.get('proved') is not None or raw.get('status')):
            title = raw.get('title') or raw.get('proof_type') or raw.get('workflow') or path.stem.replace('-',' ').title()
            pid = raw.get('id') or raw.get('proof_id') or slug(path.stem)
            href = raw.get('href') or f'{slug(pid)}.html'
            if href.startswith('site/'):
                href=href[5:]
            proofs.append({'id':str(pid),'title':str(title),'href':href,'json':f'data/{path.name}','proved':bool(raw.get('proved', str(raw.get('status','')).upper().startswith('PASSED'))),'status':str(raw.get('status','unknown'))})
    return proofs[:80]

def ensure_proof_pages(root:Path, out:Path, proofs:list[dict[str,Any]]):
    (out/'data').mkdir(exist_ok=True)
    (out/'docs').mkdir(exist_ok=True)
    (out/'badges').mkdir(exist_ok=True)
    for p in proofs:
        href=p['href']
        target=out/href
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page(p['title'], f'<h1>{esc(p["title"])}</h1><p>This normalized proof room was generated by the Agent Evolution Protocol Kernel so every registry link remains complete.</p><p><a href="{esc(p["json"])}">Open JSON receipt</a></p><p><a href="index.html">Return to Public SkillOS Command Center</a></p>'), encoding='utf-8')
        src_json = root / p['json']
        if src_json.exists():
            (out/p['json']).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_json, out/p['json'])

def build(root: Path, out: Path):
    source=json.loads(SOURCE.read_text(encoding='utf-8'))
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    copy_tree(root/'site', out)
    for folder in ['data','docs','badges']:
        if (root/folder).exists():
            copy_tree(root/folder, out/folder)
        (out/folder).mkdir(exist_ok=True)
    proofs=discover_proofs(root)
    ensure_proof_pages(root, out, proofs)
    (out/'data'/'proof-carrying-intelligence-agent-evolution-protocol.json').write_text(json.dumps(source,indent=2,sort_keys=True)+'\n', encoding='utf-8')
    (out/'data'/'skillos-agent-evolution-protocol-kernel-v3-manifest.json').write_text(json.dumps({'schema':SCHEMA,'marker':MARKER,'mode':'additive-expansion-no-removal','root_contract':source['public_language']['root_contract'],'proofs_indexed':len(proofs)},indent=2,sort_keys=True)+'\n', encoding='utf-8')
    badge='<svg xmlns="http://www.w3.org/2000/svg" width="300" height="20"><rect width="300" height="20" fill="#10182d"/><rect x="220" width="80" height="20" fill="#7dffb0"/><text x="10" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">agent evolution protocol</text><text x="238" y="14" fill="#07120d" font-family="Verdana" font-size="11">v3</text></svg>'
    (out/'badges'/'agent-evolution-protocol.svg').write_text(badge,encoding='utf-8')
    doc='# SkillOS Agent Evolution Protocol Kernel v3\n\nAim. Act. Prove. Evolve.\n\nGoalOS gives direction. PlanOS gives strategy. SkillOS gives capability. Proof Gradient gives evolution.\n\nThe Artifact Vault stores reusable intelligence. The Run Fabric executes agents at scale. The Proof Ledger records what happened. The Selection Gate promotes only what proved itself.\n'
    (out/'docs'/'SKILLOS_AGENT_EVOLUTION_PROTOCOL_KERNEL_V3.md').write_text(doc,encoding='utf-8')
    registry_path=out/'proof-registry.json'
    try:
        registry=json.loads(registry_path.read_text(encoding='utf-8')) if registry_path.exists() else {'proofs':[]}
    except Exception:
        registry={'proofs':[]}
    if isinstance(registry, list): registry={'proofs':registry}
    existing=[p for p in registry.get('proofs',[]) if isinstance(p,dict) and p.get('id')!='agent-evolution-protocol-kernel-v3']
    existing.insert(0,{'id':'agent-evolution-protocol-kernel-v3','title':'SkillOS Agent Evolution Protocol Kernel v3','href':'agent-evolution-protocol.html','json':'data/proof-carrying-intelligence-agent-evolution-protocol.json','doc':'docs/SKILLOS_AGENT_EVOLUTION_PROTOCOL_KERNEL_V3.md','badge':'badges/agent-evolution-protocol.svg','proved':True,'status':'ADDITIVE_EXPANSION_ACTIVE'})
    registry['proofs']=existing
    registry['updated_by']=MARKER
    registry_path.write_text(json.dumps(registry,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    protocol_steps=''.join(f'<div class="step"><b>{esc(x["primitive"])}</b><span>{esc(x["system"])} — {esc(x["definition"])}</span></div>' for x in source['protocol'])
    hero=f'''<section class="hero"><div><div class="eyebrow">{esc(source['public_language']['tagline'])}</div><h1>Public SkillOS Command Center.</h1><p>GoalOS gives direction. PlanOS gives strategy. SkillOS gives capability. Proof Gradient gives evolution.</p><p>The root is the lobby. Protocols and proofs are rooms.</p></div><div class="card"><div class="eyebrow">Agent Evolution Protocol</div><div class="quote">Every job leaves proof.<br>Every proof compounds intelligence.</div><p><a href="agent-evolution-protocol.html">Open the protocol →</a></p></div></section>'''
    metrics='<section class="grid"><div class="metric"><strong>8</strong><span>artifact classes</span></div><div class="metric"><strong>4</strong><span>protocol primitives</span></div><div class="metric"><strong>16</strong><span>skills displayed</span></div><div class="metric"><strong>'+str(len(proofs))+'</strong><span>proofs indexed</span></div></section>'
    root_body=hero+metrics+'<section class="protocol">'+protocol_steps+'</section><section class="card"><h2>Full architecture</h2><p>The Artifact Vault stores reusable intelligence. The Run Fabric executes agents at scale. The Proof Ledger records what happened. The Selection Gate promotes only what proved itself.</p></section><p><a href="goals-plans-skills.html">View Goals / Plans / Skills Used →</a></p>'
    (out/'index.html').write_text(page('Public SkillOS Command Center', root_body),encoding='utf-8')
    protocol_body=f'''<section class="hero"><div><div class="eyebrow">Proof-Carrying Intelligence</div><h1>Agent Evolution Protocol.</h1><p>Commit → Execute → Prove → Evolve.</p><p>{esc(source['claim_boundary'])}</p></div><div class="card"><div class="quote">One agent proves.<br>The network improves.</div><p>Not memory. Not vibes. Proof.</p></div></section><section class="protocol">{protocol_steps}</section><h2>The eight-system kernel</h2>{cards(source['systems'],'system')}<h2>Artifact classes</h2>{cards(source['artifact_classes'],'artifact')}'''
    (out/'agent-evolution-protocol.html').write_text(page('Agent Evolution Protocol', protocol_body),encoding='utf-8')
    (out/'proof-carrying-intelligence.html').write_text(page('Proof-Carrying Intelligence', protocol_body),encoding='utf-8')
    gps=f'<h1>Goals, Plans, Skills Used</h1><p>These cards make the agent system legible to non-technical viewers.</p><h2>Goals Used</h2>{cards(source["goals_used"],"goal")}<h2>Plans Used</h2>{cards(source["plans_used"],"plan")}<h2>Skills Used</h2>{cards(source["skills_used"],"skill")}<h2>Artifact Classes</h2>{cards(source["artifact_classes"],"artifact")}'
    (out/'goals-plans-skills.html').write_text(page('Goals / Plans / Skills Used', gps),encoding='utf-8')
    (out/'skills.html').write_text(page('Skills Used', gps),encoding='utf-8')
    archive_rows=[{'standard':x} for x in source['proof_archive_standard']]
    archive=f'<h1>Proof Archive Standard</h1><p>A proof page is not a marketing page. It should include artifact evidence, run evidence, proof ledger evidence, selection evidence, rollback evidence, security evidence, and a clear claim boundary.</p>{table(archive_rows,[("standard","Required Element")])}'
    (out/'proof-archive-standard.html').write_text(page('Proof Archive Standard', archive),encoding='utf-8')
    proofs_html='<h1>Proofs</h1><p>Existing proofs are preserved and indexed additively.</p>' + table(proofs[:50],[('title','Proof'),('href','Page'),('status','Status')])
    (out/'proofs.html').write_text(page('Proofs', proofs_html),encoding='utf-8')
    (out/'receipts.html').write_text(page('Receipts','<h1>Receipts</h1><p><a href="data/proof-carrying-intelligence-agent-evolution-protocol.json">Open Agent Evolution Protocol source JSON</a></p>'),encoding='utf-8')
    pages=['','agent-evolution-protocol.html','proof-carrying-intelligence.html','goals-plans-skills.html','skills.html','proof-archive-standard.html','proofs.html','receipts.html']
    sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>https://montrealai.github.io/skillos/{p}</loc></url>' for p in pages)+'</urlset>'
    (out/'sitemap.xml').write_text(sitemap,encoding='utf-8')
    (out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n',encoding='utf-8')
    (out/'.nojekyll').write_text('',encoding='utf-8')
    (out/'version.txt').write_text('agent-evolution-protocol-kernel-v3\n',encoding='utf-8')
    print(json.dumps({'status':'BUILT','out':str(out),'marker':MARKER,'proofs_indexed':len(proofs)},indent=2))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--root',default='.')
    p.add_argument('--out',default='dist')
    args=p.parse_args()
    build(Path(args.root), Path(args.out))
if __name__ == '__main__':
    main()
