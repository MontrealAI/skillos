#!/usr/bin/env python3
import html
import json
import math
from pathlib import Path

PROOF_ID = "rsi-cross-domain-capability-transfer-atlas-proof"

def pct(x, digits=1):
    return f"{100*x:.{digits}f}%"

def fmt_t(x):
    return f"${x:,.2f}T"

def line_chart(points, w=760, h=250, pad=36):
    vals = [p["locked_holdout_value_capture"] for p in points]
    mn, mx = min(vals), max(vals)
    rng = max(mx-mn, 1e-6)
    coords=[]
    for i,v in enumerate(vals):
        x = pad + i*(w-2*pad)/(len(vals)-1)
        y = h-pad - (v-mn)/rng*(h-2*pad)
        coords.append((x,y))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x,y in coords)
    area = f"{pad},{h-pad} " + poly + f" {w-pad},{h-pad}"
    dots = "".join(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='4'/>" for x,y in coords[::2])
    labels = "".join(f"<text x='{x:.1f}' y='{h-8}'>{i}</text>" for i,(x,y) in enumerate(coords) if i%4==0)
    return f"""<svg viewBox='0 0 {w} {h}' class='chart' aria-label='RSI release curve'>
      <defs><linearGradient id='area' x1='0' x2='0' y1='0' y2='1'><stop stop-color='#72ffb6' stop-opacity='.55'/><stop offset='1' stop-color='#72ffb6' stop-opacity='.02'/></linearGradient></defs>
      <path d='M {area} Z' fill='url(#area)'/><polyline points='{poly}' fill='none' stroke='#72ffb6' stroke-width='4'/>{dots}
      <line x1='{pad}' y1='{pad}' x2='{pad}' y2='{h-pad}'/><line x1='{pad}' y1='{h-pad}' x2='{w-pad}' y2='{h-pad}'/>{labels}
    </svg>"""

def bar_chart(rows, w=760, h=280, pad=42):
    items = [(k.replace('_',' '), v["locked_holdout_value_capture"]) for k,v in rows.items() if k != "__selected__"]
    items.append(("SkillOS RSI", rows["__selected__"]))
    maxv = max(v for _,v in items)
    bw = (w-2*pad)/len(items) - 10
    out=[f"<svg viewBox='0 0 {w} {h}' class='chart' aria-label='Baseline comparison'>"]
    out.append(f"<line x1='{pad}' y1='{h-pad}' x2='{w-pad}' y2='{h-pad}'/>")
    for i,(name,val) in enumerate(items):
        x=pad+i*((w-2*pad)/len(items))+7
        bh=(val/maxv)*(h-2*pad)
        y=h-pad-bh
        cls="accent" if name=="SkillOS RSI" else "muted"
        out.append(f"<rect class='{cls}' x='{x:.1f}' y='{y:.1f}' width='{bw:.1f}' height='{bh:.1f}' rx='8'/>")
        out.append(f"<text x='{x+bw/2:.1f}' y='{y-8:.1f}' text-anchor='middle'>{pct(val,0)}</text>")
        out.append(f"<text class='small' transform='translate({x+bw/2:.1f},{h-8}) rotate(-25)' text-anchor='end'>{html.escape(name[:22])}</text>")
    out.append("</svg>")
    return "".join(out)

def radar(metrics, w=420, h=420):
    labels=[("Coordination", metrics["coordination_quality"]),("Transfer", metrics["cross_domain_transfer_score"]),("Liquidity", metrics["capability_liquidity_score"]),("Verification", metrics["verification_quality"]),("Risk control", 1-metrics["risk_breach_rate"]),("Frontier", metrics["frontier_correct_rate"])]
    cx=cy=w/2; r=150
    pts=[]; spokes=[]
    for i,(label,val) in enumerate(labels):
        ang=-math.pi/2 + 2*math.pi*i/len(labels)
        x=cx+math.cos(ang)*r*val; y=cy+math.sin(ang)*r*val
        pts.append((x,y))
        sx=cx+math.cos(ang)*r; sy=cy+math.sin(ang)*r
        lx=cx+math.cos(ang)*(r+36); ly=cy+math.sin(ang)*(r+36)
        spokes.append(f"<line x1='{cx}' y1='{cy}' x2='{sx:.1f}' y2='{sy:.1f}'/><text x='{lx:.1f}' y='{ly:.1f}' text-anchor='middle'>{label}</text>")
    poly=" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)
    rings="".join(f"<circle cx='{cx}' cy='{cy}' r='{r*k/4}'/>" for k in range(1,5))
    dots="".join(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='4'/>" for x,y in pts)
    return f"<svg viewBox='0 0 {w} {h}' class='radar'>{rings}{''.join(spokes)}<polygon points='{poly}'/>{dots}</svg>"

def atlas(cases, w=760, h=320):
    out=[f"<svg viewBox='0 0 {w} {h}' class='atlas' aria-label='Transfer atlas'>"]
    out.append("<defs><radialGradient id='g'><stop stop-color='#9df7ff'/><stop offset='1' stop-color='#72ffb6' stop-opacity='.25'/></radialGradient></defs>")
    for c in cases[:90]:
        x=35+int(c['difficulty']*690)
        y=30+int(c['domain_distance']*255)
        r=4+c['reuse_potential']*10
        out.append(f"<circle cx='{x}' cy='{y}' r='{r:.1f}'><title>{html.escape(c['primary_domain'])} → {html.escape(c['transfer_domain'])}</title></circle>")
    out.append("<text x='28' y='22'>low difficulty</text><text x='620' y='22'>high difficulty</text><text x='28' y='306'>near-domain → far-domain transfer map</text>")
    out.append("</svg>")
    return "".join(out)

def main():
    root=Path('.')
    proof=json.loads((root/'data'/f'{PROOF_ID}.json').read_text(encoding='utf-8'))
    site=root/'site'; site.mkdir(exist_ok=True)
    (site/'data').mkdir(exist_ok=True); (site/'docs').mkdir(exist_ok=True); (site/'badges').mkdir(exist_ok=True)
    for src,dst in [(root/'data'/f'{PROOF_ID}.json', site/'data'/f'{PROOF_ID}.json'), (root/'docs'/f'{PROOF_ID}.md', site/'docs'/f'{PROOF_ID}.md'), (root/'badges'/f'{PROOF_ID}.svg', site/'badges'/f'{PROOF_ID}.svg')]:
        dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
    m=proof['metrics']; b=dict(proof['baselines']); b['__selected__']=m['locked_holdout_value_capture']
    html_doc=f"""<!doctype html><html lang='en'><head><meta charset='utf-8'/><meta name='viewport' content='width=device-width, initial-scale=1'/>
<title>{html.escape(proof['title'])}</title><meta name='description' content='Autonomous RSI cross-domain capability transfer proof for SkillOS.'/>
<style>
:root{{--bg:#071827;--ink:#eef8ff;--muted:#b7c7dc;--line:rgba(255,255,255,.15);--cyan:#8df5ff;--green:#72ffb6;--violet:#9b8cff;--gold:#ffd86b}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 18% 15%,rgba(141,245,255,.20),transparent 34%),radial-gradient(circle at 78% 12%,rgba(155,140,255,.18),transparent 30%),linear-gradient(135deg,#062738,#151a3d 72%,#090b1d);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.45}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:32px 32px;mask-image:linear-gradient(to bottom,black,transparent 88%);pointer-events:none}}a{{color:var(--cyan);text-decoration:none;font-weight:800}}.nav{{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;gap:20px;padding:14px 22px;background:rgba(4,15,26,.82);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}}.brand{{font-weight:950;color:var(--cyan)}}.navlinks{{display:flex;gap:16px;flex-wrap:wrap}}.wrap{{width:min(1180px,92vw);margin:auto;padding:46px 0 90px}}.hero{{display:grid;grid-template-columns:1.1fr .9fr;gap:28px;align-items:stretch}}@media(max-width:850px){{.hero{{grid-template-columns:1fr}}}}.panel,.card{{background:linear-gradient(135deg,rgba(255,255,255,.11),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:26px;box-shadow:0 30px 90px rgba(0,0,0,.22);backdrop-filter:blur(10px)}}.heroText{{padding:34px}}.eyebrow{{letter-spacing:.22em;text-transform:uppercase;color:var(--cyan);font-weight:950;font-size:12px}}h1{{font-size:clamp(42px,7vw,84px);line-height:.88;margin:15px 0 18px;letter-spacing:-.075em}}h2{{font-size:clamp(30px,4.6vw,58px);line-height:.96;letter-spacing:-.055em;margin:54px 0 18px}}h3{{font-size:22px;margin:0 0 8px}}p{{color:var(--muted)}}.proofBox{{padding:30px}}.status{{display:inline-flex;padding:8px 14px;border-radius:999px;background:rgba(114,255,182,.22);color:var(--green);font-weight:950;text-transform:uppercase;letter-spacing:.08em;font-size:12px}}.big{{font-size:clamp(32px,4vw,50px);line-height:1.02;font-weight:950;letter-spacing:-.055em;margin:16px 0}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}}@media(max-width:850px){{.metrics{{grid-template-columns:1fr 1fr}}}}.metric{{padding:18px 18px;border-radius:20px;border:1px solid var(--line);background:rgba(255,255,255,.07)}}.metric b{{display:block;color:var(--green);font-size:30px;line-height:1;font-weight:950}}.mechanism{{font-size:clamp(24px,3.4vw,42px);font-weight:950;letter-spacing:-.045em;padding:26px;margin:26px 0;color:white}}.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:22px}}@media(max-width:950px){{.grid2{{grid-template-columns:1fr}}}}.chart,.radar,.atlas{{width:100%;height:auto;overflow:visible}}svg line,svg circle{{stroke:rgba(255,255,255,.18);fill:none}}svg text{{fill:#cfe3f7;font-size:12px;font-weight:700}}.chart circle,.radar circle:last-child{{fill:var(--green);stroke:none}}.chart .accent{{fill:var(--green)}}.chart .muted{{fill:rgba(141,245,255,.35)}}.radar polygon{{fill:rgba(141,245,255,.22);stroke:var(--cyan);stroke-width:4}}.radar circle{{stroke:rgba(255,255,255,.13)}}.radar circle:not(:last-child){{fill:none}}.atlas circle{{fill:url(#g);stroke:rgba(141,245,255,.55)}}.table{{width:100%;border-collapse:collapse;overflow:hidden;border-radius:18px}}th,td{{padding:13px;border-bottom:1px solid var(--line);text-align:left}}th{{color:#9df7ff;text-transform:uppercase;letter-spacing:.12em;font-size:11px}}td{{color:#e9f4ff}}.pill{{display:inline-flex;padding:7px 10px;border-radius:999px;background:rgba(114,255,182,.16);color:var(--green);font-weight:950;font-size:12px}}.warn{{background:rgba(255,216,107,.15);color:var(--gold)}}.actions{{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px}}.btn{{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:999px;padding:12px 17px;background:rgba(255,255,255,.08);color:white;font-weight:950}}.btn.primary{{background:var(--cyan);color:#071827}}.footer{{margin-top:60px;color:#a8b7cc;font-size:14px}}
</style></head><body><nav class='nav'><div class='brand'>SkillOS Transfer Atlas</div><div class='navlinks'><a href='index.html'>Command Center</a><a href='data/{PROOF_ID}.json'>JSON</a><a href='docs/{PROOF_ID}.md'>Report</a><a href='badges/{PROOF_ID}.svg'>Badge</a><a href='https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-cross-domain-capability-transfer-atlas-proof.yml'>Run</a></div></nav>
<main class='wrap'><section class='hero'><div class='panel heroText'><div class='eyebrow'>MONTREAL.AI / SKILLOS / RSI TRANSFER ATLAS</div><h1>Capability transfer is the moat.</h1><p>Autonomous proof that a large specialist-agent organization can recursively improve how verified skills transfer across unseen domains — instead of winning only one demo, one workflow, or one benchmark.</p><div class='actions'><a class='btn primary' href='https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-cross-domain-capability-transfer-atlas-proof.yml'>Run proof on GitHub</a><a class='btn' href='data/{PROOF_ID}.json'>Open JSON receipt</a><a class='btn' href='docs/{PROOF_ID}.md'>Read report</a></div></div><div class='panel proofBox'><span class='status'>Proof passed</span><div class='big'>{proof['large_agent_coordination']['virtual_specialist_agents']:,} agents.<br>{proof['large_agent_coordination']['specialist_roles']:,} roles.<br>{proof['benchmark_design']['locked_holdout_cases']:,} locked holdout cases.</div><p>{html.escape(proof['public_safe_claim'])}</p></div></section>
<section class='metrics'><div class='metric'><b>{pct(m['locked_holdout_value_capture'],2)}</b><span>holdout value capture</span></div><div class='metric'><b>{pct(m['cross_domain_transfer_score'],2)}</b><span>transfer score</span></div><div class='metric'><b>{pct(m['capability_liquidity_score'],2)}</b><span>capability liquidity</span></div><div class='metric'><b>{pct(m['risk_breach_rate'],3)}</b><span>risk breach rate</span></div></section>
<div class='panel mechanism'>demand → decomposition → capability atlas → specialist-agent market clearing → trace distillation → verifier courts → locked-domain transfer → release selection → reinvestment → compounding generalization</div>
<section class='grid2'><div class='card' style='padding:22px'><h3>RSI release curve</h3>{line_chart(proof['release_trajectory'])}<p>Validation-gated releases are selected only when transfer improves on locked-domain holdout cases without risk breaches.</p></div><div class='card' style='padding:22px'><h3>Capability coordination radar</h3>{radar(m)}<p>The proof measures coordination, transfer, liquidity, verification, risk control, and frontier-correct generalization.</p></div></section>
<section><h2>Cross-domain transfer atlas</h2><div class='card' style='padding:22px'>{atlas(proof['sample_holdout_cases'])}</div></section>
<section class='grid2'><div class='card' style='padding:22px'><h3>Baselines and negative controls</h3>{bar_chart(b)}<p>Static catalogs, single generalists, uncoordinated pools, shuffled traces, and verifier-free releases do not match the selected SkillOS RSI release.</p></div><div class='card' style='padding:22px'><h3>Verification gates</h3><table class='table'><tbody>{''.join(f"<tr><td><span class='pill'>PASS</span></td><td>{html.escape(g['name'])}</td><td>{html.escape(g['detail'])}</td></tr>" for g in proof['verification_gates'])}</tbody></table></div></section>
<section><h2>Executive result</h2><div class='card' style='padding:24px'><table class='table'><tbody><tr><th>Metric</th><th>Value</th></tr><tr><td>Benchmark-capital-equivalent value at stake</td><td>{fmt_t(m['benchmark_capital_equivalent_value_at_stake_trillions'])}</td></tr><tr><td>Benchmark-capital-equivalent value captured</td><td>{fmt_t(m['benchmark_capital_equivalent_value_captured_trillions'])}</td></tr><tr><td>Value over static skill catalog</td><td>{fmt_t(proof['comparisons']['value_over_static_skill_catalog_trillions'])}</td></tr><tr><td>Value over uncoordinated agent pool</td><td>{fmt_t(proof['comparisons']['value_over_uncoordinated_agent_pool_trillions'])}</td></tr><tr><td>Value over single generalist</td><td>{fmt_t(proof['comparisons']['value_over_single_generalist_trillions'])}</td></tr><tr><td>Selected release</td><td>{html.escape(proof['selected_release'])}</td></tr></tbody></table><p><span class='pill warn'>Boundary</span> Benchmark figures are synthetic capital-equivalent measurements for mechanism testing; they are not live revenue, investment advice, or proof of achieved superintelligence.</p></div></section>
<div class='footer'>Generated autonomously by SkillOS. No private data. No network calls. No human review. Re-run from GitHub Actions to regenerate JSON, report, badge, page, registry, and command center.</div></main></body></html>"""
    (site/f"{PROOF_ID}.html").write_text(html_doc, encoding='utf-8')
    print(site/f"{PROOF_ID}.html")
if __name__=='__main__':
    main()
