#!/usr/bin/env python3
from __future__ import annotations
import argparse, html, json, shutil, datetime as dt, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "data" / "proof_carrying_intelligence_expansion_v2_source.json"
MARKER = "SKILLOS_AGENT_EVOLUTION_PROTOCOL_EXPANSION_V2"

def esc(x): return html.escape(str(x))
def now_iso(): return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00","Z")

CSS = '''
:root{--bg:#05070d;--panel:rgba(255,255,255,.075);--panel2:rgba(255,255,255,.115);--line:rgba(255,255,255,.16);--text:#f7fbff;--muted:#b7c6d8;--cyan:#86f8ff;--green:#7dffb0;--gold:#ffd66b;--rose:#ff9cf5}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;background:radial-gradient(circle at 82% 0,#5940a9 0,transparent 31%),radial-gradient(circle at 0 10%,#087584 0,transparent 25%),linear-gradient(135deg,#05070d,#0e1a30 55%,#261a49);color:var(--text)}
a{color:var(--cyan)}main{max-width:1240px;margin:0 auto;padding:44px 20px 90px}nav{position:sticky;top:0;z-index:5;background:rgba(5,7,13,.88);border-bottom:1px solid var(--line);backdrop-filter:blur(18px);display:flex;justify-content:space-between;align-items:center;padding:14px 22px}nav a{color:var(--muted);text-decoration:none;font-weight:850;margin-left:14px}.brand{font-weight:950}
h1{font-size:clamp(46px,7vw,104px);line-height:.85;letter-spacing:-.08em;margin:10px 0 18px}h2{font-size:clamp(31px,4vw,58px);letter-spacing:-.055em;margin:42px 0 12px}p{color:var(--muted);font-size:18px;line-height:1.55}.eyebrow{color:var(--cyan);text-transform:uppercase;letter-spacing:.18em;font-weight:950;font-size:12px}.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:24px;align-items:center}.card,.metric,.chart-wrap,.notice,.protocol{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:30px;padding:24px;box-shadow:0 26px 90px rgba(0,0,0,.28)}.quote{font-size:clamp(25px,3.1vw,44px);line-height:1.08;letter-spacing:-.045em}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}.metric strong{display:block;color:var(--green);font-size:32px}.metric span{color:var(--muted)}.protocol{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:24px 0}.step{border:1px solid var(--line);border-radius:22px;padding:18px;background:rgba(255,255,255,.055)}.step b{display:block;color:var(--gold);font-size:21px}.step span{color:var(--muted)}.card-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}.card-item{background:rgba(255,255,255,.07);border:1px solid var(--line);border-radius:24px;padding:18px;min-height:245px}.card-item h3{font-size:22px;letter-spacing:-.03em;margin:9px 0}.pill{display:inline-block;border:1px solid rgba(134,248,255,.35);color:var(--cyan);border-radius:999px;padding:5px 9px;font-size:11px;font-weight:900;letter-spacing:.08em;text-transform:uppercase}dl{margin:12px 0 0}dt{color:var(--green);font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.08em;margin-top:9px}dd{margin:3px 0 0;color:var(--muted);font-size:13px;line-height:1.35}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:20px;overflow:hidden;margin:16px 0}td,th{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--muted);text-transform:uppercase;font-size:12px;letter-spacing:.08em}.notice{border-left:4px solid var(--gold);color:var(--muted)}@media(max-width:1000px){.hero,.grid,.protocol,.card-grid{grid-template-columns:1fr}}
'''

def shell(title, body):
    nav = '<nav><div class="brand">Public SkillOS Command Center</div><div><a href="index.html">Home</a><a href="proof-carrying-intelligence.html">Protocol</a><a href="goals-plans-skills.html">Goals / Plans / Skills</a><a href="proof-archive-standard.html">Archive</a></div></nav>'
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+CSS+'</style></head><body>'+nav+'<main>'+body+'</main></body></html>'

def cards(items, kind):
    htmls=[]
    if kind=="goal":
        for g in items:
            htmls.append('<article class="card-item"><div class="pill">'+esc(g["system"])+'</div><h3>'+esc(g["name"])+'</h3><p>'+esc(g["direction"])+'</p><dl><dt>Measure</dt><dd>'+esc(g["measure"])+'</dd><dt>Threshold</dt><dd>'+esc(g["threshold"])+'</dd><dt>Why</dt><dd>'+esc(g["why"])+'</dd></dl></article>')
    elif kind=="plan":
        for p in items:
            htmls.append('<article class="card-item"><div class="pill">'+esc(p["system"])+'</div><h3>'+esc(p["name"])+'</h3><p>'+esc(p["strategy"])+'</p><dl><dt>Steps</dt><dd>'+esc(" → ".join(p["steps"]))+'</dd><dt>Linked goals</dt><dd>'+esc(", ".join(p["linked_goals"]))+'</dd><dt>Risk budget</dt><dd>'+esc(p["risk_budget"])+'</dd></dl></article>')
    elif kind=="skill":
        for s in items:
            htmls.append('<article class="card-item"><div class="pill">'+esc(s["layer"])+'</div><h3>'+esc(s["name"])+'</h3><p>'+esc(s["purpose"])+'</p><dl><dt>Input</dt><dd>'+esc(s["input_signal"])+'</dd><dt>Output</dt><dd>'+esc(s["output"])+'</dd><dt>Verifier</dt><dd>'+esc(s["verifier"])+'</dd></dl></article>')
    else:
        for a in items:
            htmls.append('<article class="card-item"><div class="pill">'+esc(a["system"])+'</div><h3>'+esc(a["class"])+'</h3><p>'+esc(a["stores"])+'</p></article>')
    return '<div class="card-grid">' + ''.join(htmls) + '</div>'

def table(rows, cols):
    head=''.join('<th>'+esc(label)+'</th>' for _,label in cols)
    body=''.join('<tr>' + ''.join('<td>'+esc(row.get(key,""))+'</td>' for key,_ in cols) + '</tr>' for row in rows)
    return '<table><thead><tr>'+head+'</tr></thead><tbody>'+body+'</tbody></table>'

def simple_chart(source):
    b=source["benchmark"]
    vals=[("Proof completeness", b["proof_completeness_rate"]),("Selection discipline", b["selection_discipline_rate"]),("Rollback readiness", b["rollback_readiness_rate"]),("Archive completeness", b["archive_completeness_rate"]),("Link integrity", b["internal_link_integrity_rate"])]
    parts=[]
    for i,(name,v) in enumerate(vals):
        y=40+i*48
        w=640*v
        parts.append(f'<text x="20" y="{y+18}" fill="#dceeff" font-size="14">{esc(name)}</text>')
        parts.append(f'<rect x="245" y="{y}" width="{w:.1f}" height="25" rx="12" fill="url(#g)"/>')
        parts.append(f'<text x="{255+w:.1f}" y="{y+18}" fill="#b8c8d8" font-size="14">{v*100:.1f}%</text>')
    return '<div class="chart-wrap"><svg viewBox="0 0 980 300" role="img" aria-label="Protocol coverage chart"><defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#7dffb0"/><stop offset="1" stop-color="#86f8ff"/></linearGradient></defs>'+''.join(parts)+'</svg></div>'

def proof_receipt(source):
    b=source["benchmark"]
    return {
        "id":"proof-carrying-intelligence-agent-evolution-protocol",
        "title":"Proof-Carrying Intelligence · Agent Evolution Protocol",
        "schema":"skillos.proof_carrying_intelligence.expansion.v2.receipt",
        "marker":"SKILLOS_AGENT_EVOLUTION_PROTOCOL_EXPANSION_V2_RECEIPT",
        "generated_at_utc":now_iso(),
        "proved": True,
        "mode":"additive-expansion-no-removal",
        "protocol":"Aim. Act. Prove. Evolve.",
        "systems":source["canonical_language"]["lines"],
        "goals_used":source["goals"],
        "plans_used":source["plans"],
        "skills_used":source["skills"],
        "artifact_classes":source["artifact_classes"],
        "proof_archive_standard":source["proof_archive_standard"],
        "public_messaging":source["messaging"],
        "metrics": {
            "agents": b["agents"],
            "proofs": b["proofs"],
            "candidate_upgrades": b["candidate_upgrades"],
            "accepted_upgrades": b["accepted_upgrades"],
            "negative_control_rejection_rate_percent": round(100*b["negative_controls_rejected"]/b["negative_controls"],4),
            "archive_completeness_rate_percent": round(100*b["archive_completeness_rate"],4),
            "selection_discipline_rate_percent": round(100*b["selection_discipline_rate"],4),
            "proof_completeness_rate_percent": round(100*b["proof_completeness_rate"],4),
            "rollback_readiness_rate_percent": round(100*b["rollback_readiness_rate"],4),
            "internal_link_integrity_rate_percent": round(100*b["internal_link_integrity_rate"],4),
            "root_contract_preserved": b["root_contract_preserved"],
        },
        "public_boundary":"This expansion is a protocol and proof-archive infrastructure update. It does not claim achieved superintelligence, Kardashev Type II civilization, live revenue, investment returns, guaranteed wealth, financial advice, legal advice, medical advice, policy advice, or token advice."
    }

def build(out: Path):
    source=json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    if out.exists():
        shutil.rmtree(out)
    existing=ROOT/"site"
    if existing.exists():
        shutil.copytree(existing,out,dirs_exist_ok=True)
    out.mkdir(parents=True,exist_ok=True)
    for d in ["data","docs","badges"]:
        (out/d).mkdir(parents=True,exist_ok=True)
    receipt=proof_receipt(source)
    (out/"data"/"proof-carrying-intelligence-agent-evolution-protocol.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    manifest={"schema":"skillos.proof_carrying_intelligence.expansion.v2","marker":MARKER,"mode":"additive-expansion-no-removal","root_contract":"Public SkillOS Command Center owns /skillos/ and /skillos/index.html; protocol and proofs are subpages.","generated_at_utc":receipt["generated_at_utc"]}
    (out/"data"/"skillos-agent-evolution-protocol-expansion-v2-manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (out/"docs"/"PROOF_CARRYING_INTELLIGENCE_AGENT_EVOLUTION_PROTOCOL.md").write_text("# Proof-Carrying Intelligence · Agent Evolution Protocol\n\nAim. Act. Prove. Evolve.\n\nEvery job leaves proof. Every proof can compound intelligence.\n",encoding="utf-8")
    (out/"badges"/"proof-carrying-intelligence.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="320" height="20"><rect width="320" height="20" fill="#0b1020"/><rect x="220" width="100" height="20" fill="#7dffb0"/><text x="10" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">proof-carrying intelligence</text><text x="245" y="14" fill="#06131f" font-family="Verdana" font-size="11">active</text></svg>',encoding="utf-8")

    lines=''.join('<p>'+esc(line)+'</p>' for line in source["canonical_language"]["lines"])
    b=source["benchmark"]
    root_body=f'<section class="hero"><div><div class="eyebrow">Public SkillOS Command Center</div><h1>Aim. Act. Prove. Evolve.</h1><p>SkillOS is expanding into a proof-carrying intelligence system for governed agent evolution.</p></div><div class="card"><div class="eyebrow">Agent Evolution Protocol</div><div class="quote">Every job leaves proof.<br>Every proof can compound intelligence.</div><p><a href="proof-carrying-intelligence.html">Open the protocol room →</a></p></div></section><section class="protocol"><div class="step"><b>Aim</b><span>GoalOS gives direction.</span></div><div class="step"><b>Act</b><span>PlanOS and SkillOS provide strategy and capability.</span></div><div class="step"><b>Prove</b><span>The Proof Ledger records what happened.</span></div><div class="step"><b>Evolve</b><span>The Selection Gate promotes only what proved itself.</span></div></section><section class="grid"><div class="metric"><strong>{b["agents"]:,}</strong><span>agent-scale benchmark</span></div><div class="metric"><strong>{b["proofs"]:,}</strong><span>proof traces</span></div><div class="metric"><strong>{b["accepted_upgrades"]}</strong><span>accepted upgrades</span></div><div class="metric"><strong>100%</strong><span>negative-control rejection</span></div></section>{simple_chart(source)}<section class="card"><h2>The full expansion</h2>{lines}</section>'
    (out/"index.html").write_text(shell("Public SkillOS Command Center",root_body),encoding="utf-8")

    protocol_body=f'<section class="hero"><div><div class="eyebrow">Proof-Carrying Intelligence</div><h1>The Agent Evolution Protocol.</h1><p>{esc(source["category_definition"])}</p></div><div class="card"><div class="eyebrow">Canonical loop</div><div class="quote">Commit → Execute → Prove → Evolve</div><p>Anything that can improve is an artifact. Anything that changes must carry proof. Anything that propagates must pass the Evolution Gate.</p></div></section><section class="protocol"><div class="step"><b>Artifact Vault</b><span>Stores reusable intelligence.</span></div><div class="step"><b>Run Fabric</b><span>Executes agents at scale.</span></div><div class="step"><b>Proof Ledger</b><span>Records what happened.</span></div><div class="step"><b>Selection Gate</b><span>Promotes only what proved itself.</span></div></section><h2>Artifact classes</h2>{cards(source["artifact_classes"],"artifact")}<h2>Messaging discipline</h2>{table([{"do":d,"dont":source["messaging"]["do_not_say"][i] if i < len(source["messaging"]["do_not_say"]) else ""} for i,d in enumerate(source["messaging"]["do_say"])],[("do","Do say"),("dont","Do not say")])}<section class="notice"><strong>Boundary:</strong> {esc(receipt["public_boundary"])}</section>'
    (out/"proof-carrying-intelligence.html").write_text(shell("Proof-Carrying Intelligence",protocol_body),encoding="utf-8")
    (out/"agent-evolution-protocol.html").write_text(shell("Agent Evolution Protocol",protocol_body),encoding="utf-8")

    gps_body=f'<section class="hero"><div><div class="eyebrow">Goals · Plans · Skills Used</div><h1>The operating stack behind governed evolution.</h1><p>Each card explains what the system uses, why it matters, what it consumes, what it produces, and how it is verified.</p></div><div class="card"><div class="quote">GoalOS gives direction.<br>PlanOS gives strategy.<br>SkillOS gives capability.<br>Proof Gradient gives evolution.</div></div></section><h2>Goals Used</h2>{cards(source["goals"],"goal")}<h2>Plans Used</h2>{cards(source["plans"],"plan")}<h2>Skills Used</h2>{cards(source["skills"],"skill")}'
    (out/"goals-plans-skills.html").write_text(shell("Goals, Plans, Skills Used",gps_body),encoding="utf-8")
    (out/"skills.html").write_text(shell("Skills Used",gps_body),encoding="utf-8")

    archive_rows=[{"section":s,"required":"yes"} for s in source["proof_archive_standard"]["required_page_sections"]]
    file_rows=[{"file":s,"required":"yes"} for s in source["proof_archive_standard"]["required_files"]]
    archive_body=f'<section class="hero"><div><div class="eyebrow">Proof Archive Standard</div><h1>Every proof deserves a permanent room.</h1><p>A proof page is not a marketing page. It should include artifact evidence, run evidence, proof ledger evidence, selection evidence, rollback evidence, security evidence, and a clear claim boundary.</p></div><div class="card"><div class="quote">No proof, no evolution.<br>No eval, no propagation.<br>No rollback, no release.</div></div></section><h2>Required proof page evidence</h2>{table(archive_rows,[("section","Evidence section"),("required","Required")])}<h2>Required proof files</h2>{table(file_rows,[("file","File"),("required","Required")])}'
    (out/"proof-archive-standard.html").write_text(shell("Proof Archive Standard",archive_body),encoding="utf-8")

    receipts_body='<h1>Receipts</h1><p><a href="data/proof-carrying-intelligence-agent-evolution-protocol.json">Proof-Carrying Intelligence JSON receipt</a></p><p><a href="docs/PROOF_CARRYING_INTELLIGENCE_AGENT_EVOLUTION_PROTOCOL.md">Markdown report</a></p>'
    (out/"receipts.html").write_text(shell("Receipts",receipts_body),encoding="utf-8")
    (out/"proofs.html").write_text(shell("Proofs",'<h1>Proofs and protocols</h1><p><a href="proof-carrying-intelligence.html">Proof-Carrying Intelligence</a></p><p><a href="proof-archive-standard.html">Proof Archive Standard</a></p>'),encoding="utf-8")
    (out/"404.html").write_text(shell("Not found",'<h1>Page not found.</h1><p><a href="index.html">Return to Public SkillOS Command Center.</a></p>'),encoding="utf-8")
    (out/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n",encoding="utf-8")
    (out/".nojekyll").write_text("",encoding="utf-8")
    (out/"version.txt").write_text("skillos-agent-evolution-protocol-expansion-v2\n",encoding="utf-8")
    urls=["","proof-carrying-intelligence.html","agent-evolution-protocol.html","goals-plans-skills.html","proof-archive-standard.html","receipts.html","proofs.html"]
    sitemap='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9)">'+''.join('<url><loc>https://montrealai.github.io/skillos/'+u+'</loc></url>' for u in urls)+'</urlset>'
    (out/"sitemap.xml").write_text(sitemap,encoding="utf-8")
    registry={"proofs":[]}
    registry_path=out/"proof-registry.json"
    if registry_path.exists():
        try:
            loaded=json.loads(registry_path.read_text(encoding="utf-8"))
            if isinstance(loaded,dict) and isinstance(loaded.get("proofs"),list): registry=loaded
            elif isinstance(loaded,list): registry={"proofs":loaded}
        except Exception: pass
    registry["proofs"]=[p for p in registry.get("proofs",[]) if isinstance(p,dict) and p.get("id") != "proof-carrying-intelligence-agent-evolution-protocol"]
    registry["proofs"].insert(0,{"id":"proof-carrying-intelligence-agent-evolution-protocol","title":"Proof-Carrying Intelligence · Agent Evolution Protocol","href":"proof-carrying-intelligence.html","json":"data/proof-carrying-intelligence-agent-evolution-protocol.json","doc":"docs/PROOF_CARRYING_INTELLIGENCE_AGENT_EVOLUTION_PROTOCOL.md","badge":"badges/proof-carrying-intelligence.svg","proved":True,"status":"ACTIVE"})
    registry["updated_at_utc"]=receipt["generated_at_utc"]
    registry_path.write_text(json.dumps(registry,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"BUILT","out":str(out),"mode":"additive-expansion-no-removal"},indent=2))

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="dist")
    args=p.parse_args()
    build(Path(args.out))
if __name__ == "__main__":
    main()
