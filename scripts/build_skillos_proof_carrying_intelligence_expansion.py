
#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, html, json, shutil
from pathlib import Path
PROTOCOL_ID='proof-carrying-intelligence-agent-evolution-protocol'
MANIFEST='skillos-proof-carrying-intelligence-expansion-manifest.json'
MARKER='SKILLOS_PROOF_CARRYING_INTELLIGENCE_EXPANSION_V1'
SCHEMA='skillos.proof_carrying_intelligence.expansion.v1'

def esc(x): return html.escape(str(x))
def now_iso(): return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace('+00:00','Z')
def load_source(root):
    p=root/'data'/'proof_carrying_intelligence_expansion_source.json'
    if not p.exists(): raise SystemExit('missing '+str(p))
    return json.loads(p.read_text(encoding='utf-8'))
def css():
    return ':root{--panel:rgba(255,255,255,.075);--line:rgba(255,255,255,.16);--text:#f6fbff;--muted:#b7c6d8;--cyan:#86f8ff;--green:#7dffb0;--gold:#ffd66b}*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;background:radial-gradient(circle at 85% 0,#5640a0,transparent 30%),radial-gradient(circle at 0 12%,#086a75,transparent 26%),linear-gradient(135deg,#05070d,#0c1830 55%,#261a49);color:var(--text)}a{color:var(--cyan)}main{max-width:1220px;margin:0 auto;padding:44px 20px 90px}nav{position:sticky;top:0;background:rgba(5,7,13,.88);border-bottom:1px solid var(--line);backdrop-filter:blur(16px);display:flex;justify-content:space-between;padding:14px 22px;z-index:5}nav a{color:var(--muted);text-decoration:none;font-weight:850;margin-left:14px}h1{font-size:clamp(44px,7vw,98px);line-height:.86;letter-spacing:-.08em;margin:10px 0 18px}h2{font-size:clamp(30px,4vw,54px);letter-spacing:-.05em;margin:40px 0 12px}p{color:var(--muted);font-size:18px;line-height:1.55}.eyebrow{color:var(--cyan);text-transform:uppercase;letter-spacing:.18em;font-weight:950;font-size:12px}.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:24px;align-items:center}.card,.metric,.protocol,.chart,.notice{background:linear-gradient(180deg,rgba(255,255,255,.105),var(--panel));border:1px solid var(--line);border-radius:28px;padding:24px;box-shadow:0 22px 80px rgba(0,0,0,.25)}.quote{font-size:clamp(25px,3.1vw,42px);line-height:1.08;letter-spacing:-.045em}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}.metric strong{display:block;color:var(--green);font-size:30px}.metric span{color:var(--muted)}.protocol{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}.step{border:1px solid var(--line);border-radius:20px;padding:16px;background:rgba(255,255,255,.055)}.step b{display:block;color:var(--gold);font-size:21px}.step span{color:var(--muted)}.card-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}.card-item{background:rgba(255,255,255,.07);border:1px solid var(--line);border-radius:22px;padding:18px;min-height:230px}.card-item h3{font-size:22px;letter-spacing:-.03em;margin:9px 0}.pill{display:inline-block;border:1px solid rgba(134,248,255,.35);color:var(--cyan);border-radius:999px;padding:5px 9px;font-size:11px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}dl{margin:12px 0 0}dt{color:var(--green);font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.08em;margin-top:9px}dd{margin:3px 0 0;color:var(--muted);font-size:13px;line-height:1.35}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:18px;overflow:hidden;margin:16px 0}td,th{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--muted);text-transform:uppercase;font-size:12px;letter-spacing:.08em}.notice{border-left:4px solid var(--gold);color:var(--muted)}.flow{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.flow div{padding:18px;border:1px solid var(--line);border-radius:20px;background:rgba(255,255,255,.065)}@media(max-width:950px){.hero,.grid,.protocol,.card-grid,.flow{grid-template-columns:1fr}}'
def shell(title,body):
    nav='<nav><strong>Public SkillOS Command Center</strong><div><a href="index.html">Home</a><a href="proof-carrying-intelligence.html">Protocol</a><a href="goals-plans-skills.html">Goals / Plans / Skills</a><a href="proof-archive-standard.html">Archive Standard</a></div></nav>'
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+css()+'</style></head><body>'+nav+'<main>'+body+'</main></body></html>'
def table(rows,headers):
    return '<table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table>'
def card_grid(items,kind):
    cards=[]
    for item in items:
        if kind=='goals':
            cards.append('<article class="card-item"><div class="pill">GoalOS</div><h3>'+esc(item['name'])+'</h3><p>'+esc(item['direction'])+'</p><dl><dt>Measure</dt><dd>'+esc(item['measure'])+'</dd><dt>Threshold</dt><dd>'+esc(item['threshold'])+'</dd><dt>Why</dt><dd>'+esc(item['why'])+'</dd></dl></article>')
        elif kind=='plans':
            cards.append('<article class="card-item"><div class="pill">PlanOS</div><h3>'+esc(item['name'])+'</h3><p>'+esc(item['strategy'])+'</p><dl><dt>Steps</dt><dd>'+esc(' → '.join(item['steps']))+'</dd><dt>Linked goals</dt><dd>'+esc(', '.join(item['linked_goals']))+'</dd><dt>Risk budget</dt><dd>'+esc(item['risk_budget'])+'</dd></dl></article>')
        elif kind=='skills':
            cards.append('<article class="card-item"><div class="pill">'+esc(item['layer'])+'</div><h3>'+esc(item['name'])+'</h3><p>'+esc(item['purpose'])+'</p><dl><dt>Input</dt><dd>'+esc(item['input_signal'])+'</dd><dt>Output</dt><dd>'+esc(item['output'])+'</dd><dt>Verifier</dt><dd>'+esc(item['verifier'])+'</dd></dl></article>')
        else:
            cards.append('<article class="card-item"><div class="pill">'+esc(item['system'])+'</div><h3>'+esc(item['class'])+'</h3><p>'+esc(item['examples'])+'</p></article>')
    return '<div class="card-grid">'+''.join(cards)+'</div>'
def mini_graph():
    labels=['Commit','Execute','Prove','Evolve','Network']; values=[100,96,93,55,52]; parts=[]
    for i,(label,val) in enumerate(zip(labels,values)):
        x=30+i*180; y=250-val*1.8
        parts.append(f'<rect x="{x}" y="{y:.1f}" width="128" height="{val*1.8:.1f}" rx="18" fill="rgba(134,248,255,{0.22+i*.08:.2f})" stroke="rgba(255,255,255,.25)"/>')
        parts.append(f'<text x="{x+64}" y="{y+30:.1f}" text-anchor="middle" fill="#f6fbff" font-size="18" font-weight="900">{val}%</text>')
        parts.append(f'<text x="{x+64}" y="282" text-anchor="middle" fill="#b7c6d8" font-size="14">{label}</text>')
    return '<div class="chart"><svg viewBox="0 0 940 310">'+''.join(parts)+'</svg></div>'
def build(root,out):
    src=load_source(root)
    if out.exists(): shutil.rmtree(out)
    if (root/'site').exists(): shutil.copytree(root/'site',out,dirs_exist_ok=True)
    else: out.mkdir(parents=True,exist_ok=True)
    for d in ['data','docs','badges']: (out/d).mkdir(exist_ok=True)
    manifest={'schema':SCHEMA,'marker':MARKER,'generated_at_utc':now_iso(),'root_contract':'/skillos/ and /skillos/index.html are the Public SkillOS Command Center. Proofs are subpages.','mode':'additive-expansion-no-removal'}
    (out/'data'/MANIFEST).write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    receipt={'schema':SCHEMA,'marker':MARKER,'generated_at_utc':manifest['generated_at_utc'],'title':'Proof-Carrying Intelligence · Agent Evolution Protocol','definition':src['final_language']['definition'],'final_language':src['final_language'],'goals_used':src['goals_used'],'plans_used':src['plans_used'],'skills_used':src['skills_used'],'artifact_classes':src['artifact_classes'],'proof_standard':src['proof_standard'],'public_boundary':'Proof Gradient is a proof-carrying intelligence protocol for governed agent evolution. It does not claim achieved superintelligence, Kardashev Type II capability, guaranteed wealth, or autonomous self-improvement without controls.'}
    (out/'data'/(PROTOCOL_ID+'.json')).write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    (out/'docs'/'PROOF_CARRYING_INTELLIGENCE_AGENT_EVOLUTION_PROTOCOL.md').write_text('# Proof-Carrying Intelligence · Agent Evolution Protocol\n\nAim. Act. Prove. Evolve.\n\nThe root remains the Public SkillOS Command Center. This expansion adds protocol rooms without deleting existing proofs.\n',encoding='utf-8')
    (out/'badges'/'proof-carrying-intelligence.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="330" height="20"><rect width="330" height="20" rx="10" fill="#14233a"/><rect x="222" width="108" height="20" rx="10" fill="#7dffb0"/><text x="10" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">proof-carrying intelligence</text><text x="247" y="14" fill="#05120d" font-family="Verdana" font-size="11">active</text></svg>',encoding='utf-8')
    hero='<section class="hero"><div><div class="eyebrow">Aim. Act. Prove. Evolve.</div><h1>Proof-Carrying Intelligence.</h1><p>GoalOS gives the network direction. PlanOS gives it strategy. SkillOS gives it capability. Proof Gradient gives it evolution.</p></div><div class="card"><div class="eyebrow">Agent Evolution Protocol</div><div class="quote">One agent proves.<br>The network improves.</div><p>'+esc(src['final_language']['definition'])+'</p></div></section>'
    protocol='<section class="protocol"><div class="step"><b>Aim</b><span>GoalOS creates explicit direction.</span></div><div class="step"><b>Act</b><span>Run Fabric executes agents at scale.</span></div><div class="step"><b>Prove</b><span>Proof Ledger records what happened.</span></div><div class="step"><b>Evolve</b><span>Selection Gate promotes only what proved itself.</span></div></section>'
    systems='<section class="grid">'+''.join('<div class="metric"><strong>'+esc(s[0])+'</strong><span>'+esc(s[1])+'</span></div>' for s in src['final_language']['systems'][:4])+'</section>'
    root_hero='<section class="hero"><div><div class="eyebrow">Public SkillOS Command Center</div><h1>Public SkillOS Command Center.</h1><p>SkillOS now includes the Proof-Carrying Intelligence expansion: Aim, Act, Prove, Evolve. Existing proofs remain rooms. The root remains the lobby.</p></div><div class="card"><div class="eyebrow">New protocol layer</div><div class="quote">One agent proves.<br>The network improves.</div><p>'+esc(src['final_language']['definition'])+'</p></div></section>'; root_body=root_hero+protocol+systems+'<section class="card"><h2>Expansion installed</h2><p>This Command Center was expanded additively. Existing proofs remain rooms. The root remains the lobby.</p><p><a href="proof-carrying-intelligence.html">Open the Proof-Carrying Intelligence protocol →</a></p></section>'
    (out/'index.html').write_text(shell('Public SkillOS Command Center',root_body),encoding='utf-8')
    standard=table([[x] for x in src['proof_standard']],['Required evidence'])
    dos=table([[x['do'],x['dont']] for x in src['do_say_do_not_say']],['Do say','Do not say'])
    proof_body=hero+protocol+'<h2>Scalable platform</h2><div class="flow"><div><h3>Artifact Vault</h3><p>Stores reusable intelligence: goals, plans, skills, tools, policies, evals, rubrics, and context recipes.</p></div><div><h3>Run Fabric</h3><p>Resolves artifacts, executes agents statelessly, and emits proof.</p></div><div><h3>Proof Ledger</h3><p>Append-only evidence: traces, scores, feedback, policy decisions, costs, failures, and credit assignment.</p></div><div><h3>Selection Gate</h3><p>Propose, evaluate, approve, canary, promote, monitor, and rollback.</p></div></div>'+mini_graph()+'<h2>Proof archive standard</h2>'+standard+'<h2>Do say / do not say</h2>'+dos+'<section class="notice"><strong>Boundary:</strong> Kardashev-scale ambition is a strategic scenario, not a present-tense achievement. No proof, no evolution. No eval, no propagation. No rollback, no release.</section>'
    (out/'proof-carrying-intelligence.html').write_text(shell('Proof-Carrying Intelligence',proof_body),encoding='utf-8')
    (out/'agent-evolution-protocol.html').write_text(shell('Agent Evolution Protocol',proof_body),encoding='utf-8')
    gps='<h1>Goals, Plans, and Skills Used</h1><p>These cards explain the operating system in non-technical language. Every card shows the purpose, input, output, and verifier.</p><h2>Goals Used</h2>'+card_grid(src['goals_used'],'goals')+'<h2>Plans Used</h2>'+card_grid(src['plans_used'],'plans')+'<h2>Skills Used</h2>'+card_grid(src['skills_used'],'skills')+'<h2>Artifact Classes</h2>'+card_grid(src['artifact_classes'],'artifacts')
    (out/'goals-plans-skills.html').write_text(shell('Goals, Plans, Skills Used',gps),encoding='utf-8')
    (out/'skills.html').write_text(shell('Skills Used',gps),encoding='utf-8')
    archive='<h1>Proof Archive Standard</h1><p>Every proof should have its own permanent page, evidence JSON, checksum, and link back to the main command center.</p>'+standard+'<p><a href="data/'+PROTOCOL_ID+'.json">Open the machine-readable protocol receipt →</a></p>'
    (out/'proof-archive-standard.html').write_text(shell('Proof Archive Standard',archive),encoding='utf-8')
    (out/'receipts.html').write_text(shell('Receipts','<h1>Receipts</h1><p><a href="data/'+MANIFEST+'">Command Center expansion manifest</a></p><p><a href="data/'+PROTOCOL_ID+'.json">Proof-Carrying Intelligence receipt</a></p><p><a href="docs/PROOF_CARRYING_INTELLIGENCE_AGENT_EVOLUTION_PROTOCOL.md">Markdown documentation</a></p>'),encoding='utf-8')
    (out/'404.html').write_text(shell('Not Found','<h1>Proof room not found.</h1><p><a href="index.html">Return to the Public SkillOS Command Center.</a></p>'),encoding='utf-8')
    regp=out/'proof-registry.json'
    try:
        reg=json.loads(regp.read_text(encoding='utf-8')) if regp.exists() else {'proofs':[]}
        if isinstance(reg,list): reg={'proofs':reg}
        if not isinstance(reg,dict): reg={'proofs':[]}
    except Exception: reg={'proofs':[]}
    proofs=[p for p in reg.get('proofs',[]) if not (isinstance(p,dict) and p.get('id')==PROTOCOL_ID)]
    proofs.insert(0,{'id':PROTOCOL_ID,'title':'Proof-Carrying Intelligence · Agent Evolution Protocol','href':'proof-carrying-intelligence.html','json':'data/'+PROTOCOL_ID+'.json','doc':'docs/PROOF_CARRYING_INTELLIGENCE_AGENT_EVOLUTION_PROTOCOL.md','badge':'badges/proof-carrying-intelligence.svg','status':'ACTIVE','proved':True})
    reg['proofs']=proofs; reg['updated_at_utc']=manifest['generated_at_utc']; regp.write_text(json.dumps(reg,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>https://montrealai.github.io/skillos/'+p+'</loc></url>' for p in ['', 'proof-carrying-intelligence.html','goals-plans-skills.html','proof-archive-standard.html','receipts.html'])+'</urlset>'
    (out/'sitemap.xml').write_text(sitemap,encoding='utf-8'); (out/'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n',encoding='utf-8'); (out/'.nojekyll').write_text('',encoding='utf-8'); (out/'version.txt').write_text('proof-carrying-intelligence-expansion-v1\n',encoding='utf-8')
    print(json.dumps({'status':'BUILT','out':str(out),'marker':MARKER},indent=2))
def main():
    p=argparse.ArgumentParser(); p.add_argument('--root',default='.'); p.add_argument('--out',default='dist'); a=p.parse_args(); build(Path(a.root),Path(a.out))
if __name__=='__main__': main()
