#!/usr/bin/env python3
import json
from pathlib import Path

PROOF_ID = "rsi-cross-domain-capability-transfer-atlas-proof"

def pct(x): return f"{100*x:.1f}%"

def main():
    root=Path('.')
    site=root/'site'; site.mkdir(exist_ok=True)
    proof=json.loads((root/'data'/f'{PROOF_ID}.json').read_text(encoding='utf-8'))
    registry_path=site/'proof-registry.json'
    if registry_path.exists():
        try:
            registry=json.loads(registry_path.read_text(encoding='utf-8'))
        except Exception:
            registry={"proofs":[]}
    else:
        registry={"proofs":[]}
    proofs=[p for p in registry.get('proofs',[]) if p.get('id')!=PROOF_ID]
    m=proof['metrics']
    entry={
        "id": PROOF_ID,
        "title": proof['title'],
        "href": f"{PROOF_ID}.html",
        "json": f"data/{PROOF_ID}.json",
        "report": f"docs/{PROOF_ID}.md",
        "badge": f"badges/{PROOF_ID}.svg",
        "status": "passing" if proof['proved'] else "failing",
        "generated_at_utc": proof['generated_at_utc'],
        "headline": "Cross-domain capability transfer becomes a measurable, reusable SkillOS asset.",
        "metrics": {
            "value_capture": m['locked_holdout_value_capture'],
            "transfer": m['cross_domain_transfer_score'],
            "liquidity": m['capability_liquidity_score'],
            "risk": m['risk_breach_rate'],
        }
    }
    proofs.insert(0, entry)
    registry={"updated_at_utc": proof['generated_at_utc'], "proofs": proofs[:80]}
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding='utf-8')
    cards=[]
    for p in registry['proofs'][:24]:
        mt=p.get('metrics',{})
        cards.append(f"""<article class='card'><span class='pill'>{p.get('status','unknown')}</span><h3><a href='{p.get('href','#')}'>{p.get('title','Proof')}</a></h3><p>{p.get('headline','Autonomous public proof')}</p><div class='mini'><b>{pct(mt.get('value_capture',0))}</b><span>value capture</span><b>{pct(mt.get('transfer',0))}</b><span>transfer</span></div><div class='links'><a href='{p.get('href','#')}'>View proof</a><a href='{p.get('json','#')}'>JSON</a><a href='{p.get('report','#')}'>Report</a></div></article>""")
    html=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'/><meta name='viewport' content='width=device-width,initial-scale=1'/><title>SkillOS Proof Command Center</title><style>
:root{{--bg:#071827;--ink:#eef8ff;--muted:#b7c7dc;--line:rgba(255,255,255,.15);--cyan:#8df5ff;--green:#72ffb6;--violet:#9b8cff}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 15% 8%,rgba(141,245,255,.20),transparent 32%),linear-gradient(135deg,#061d2b,#111838 70%,#090b1d);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:32px 32px;pointer-events:none}}a{{color:var(--cyan);text-decoration:none;font-weight:900}}nav{{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;padding:14px 22px;background:rgba(4,15,26,.84);border-bottom:1px solid var(--line);backdrop-filter:blur(14px)}}.wrap{{width:min(1180px,92vw);margin:auto;padding:48px 0 90px}}h1{{font-size:clamp(44px,7vw,88px);line-height:.88;letter-spacing:-.075em;margin:18px 0}}h2{{font-size:clamp(30px,4vw,56px);letter-spacing:-.05em}}p{{color:var(--muted)}}.hero,.card{{background:linear-gradient(135deg,rgba(255,255,255,.11),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:26px;box-shadow:0 30px 90px rgba(0,0,0,.23)}}.hero{{padding:34px}}.eyebrow{{color:var(--cyan);letter-spacing:.22em;text-transform:uppercase;font-weight:950;font-size:12px}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}@media(max-width:850px){{.grid{{grid-template-columns:1fr}}}}.card{{padding:22px}}.pill{{display:inline-flex;padding:7px 10px;border-radius:999px;background:rgba(114,255,182,.17);color:var(--green);font-size:12px;font-weight:950;text-transform:uppercase}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0}}.metric{{padding:18px;border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.07)}}.metric b,.mini b{{color:var(--green);font-size:26px}}.mini{{display:grid;grid-template-columns:auto 1fr auto 1fr;gap:8px;align-items:baseline}}.links{{display:flex;gap:12px;flex-wrap:wrap;margin-top:15px}}.btn{{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:12px 16px;background:var(--cyan);color:#071827;font-weight:950}}
</style></head><body><nav><strong><a href='index.html'>SkillOS Proof Command Center</a></strong><span><a href='proof-registry.json'>Registry</a> &nbsp; <a href='https://github.com/MontrealAI/skillos/actions'>Actions</a> &nbsp; <a href='https://github.com/MontrealAI/skillos'>GitHub</a></span></nav><main class='wrap'><section class='hero'><div class='eyebrow'>AUTONOMOUS RSI PUBLIC PROOF SYSTEM</div><h1>Proofs that improve the proof system.</h1><p>SkillOS turns work into traces, traces into verified skills, skills into releases, and releases into stronger future work. This command center is regenerated by GitHub Actions from public receipts.</p><div class='metrics'><div class='metric'><b>{len(registry['proofs'])}</b><br>registered proofs</div><div class='metric'><b>{pct(entry['metrics']['value_capture'])}</b><br>latest value capture</div><div class='metric'><b>{pct(entry['metrics']['transfer'])}</b><br>latest transfer</div><div class='metric'><b>{pct(entry['metrics']['risk'])}</b><br>latest risk breach</div></div><a class='btn' href='{PROOF_ID}.html'>Open latest proof</a></section><h2>Latest proofs</h2><section class='grid'>{''.join(cards)}</section></main></body></html>"""
    (site/'index.html').write_text(html, encoding='utf-8')
    (site/'sitemap.xml').write_text("<?xml version='1.0' encoding='UTF-8'?><urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>"+"".join(f"<url><loc>https://montrealai.github.io/skillos/{p.get('href','')}</loc></url>" for p in registry['proofs'])+"</urlset>", encoding='utf-8')
    (site/'robots.txt').write_text("User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n", encoding='utf-8')
    print(site/'index.html')
if __name__=='__main__': main()
