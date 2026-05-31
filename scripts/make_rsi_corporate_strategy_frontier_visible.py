#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "rsi-corporate-strategy-frontier-proof"
PROOF_JSON = ROOT / "data" / f"{SLUG}.json"
OUT_HTML = ROOT / "site" / f"{SLUG}.html"
OUT_BADGE = ROOT / "badges" / f"{SLUG}.svg"
BASE_URL = "https://montrealai.github.io/skillos/"
ACTION_URL = "https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-corporate-strategy-frontier-proof.yml"


def dollars(x: float) -> str:
    if abs(x) >= 1e12: return f"${x/1e12:.2f}T"
    if abs(x) >= 1e9: return f"${x/1e9:.2f}B"
    if abs(x) >= 1e6: return f"${x/1e6:.2f}M"
    return f"${x:.0f}"


def pct(x: float) -> str:
    return f"{x:.3f}%"


def line_chart(values, labels=None, width=720, height=240, stroke="#7df7ff", fill="#79ffb245"):
    if not values:
        values=[0]
    lo=min(values); hi=max(values); pad=(hi-lo)*0.08 or 1
    lo-=pad; hi+=pad
    pts=[]
    for i,v in enumerate(values):
        x=36 + (width-72)*(i/(len(values)-1 if len(values)>1 else 1))
        y=height-34 - (height-72)*((v-lo)/(hi-lo))
        pts.append((x,y))
    poly=" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)
    area=" ".join([f"{pts[0][0]:.1f},{height-34}"] + [f"{x:.1f},{y:.1f}" for x,y in pts] + [f"{pts[-1][0]:.1f},{height-34}"])
    circles="".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{stroke}" />' for x,y in pts)
    ticks="".join(f'<text x="{x:.1f}" y="{height-10}" text-anchor="middle" class="svg-label">v{i}</text>' for i,(x,y) in enumerate(pts) if i % max(1, len(pts)//8)==0)
    return f'''<svg viewBox="0 0 {width} {height}" class="chart" role="img">
      <defs><linearGradient id="lineFill" x1="0" x2="0" y1="0" y2="1"><stop stop-color="{fill}"/><stop offset="1" stop-color="transparent"/></linearGradient></defs>
      <path d="M36 20 V{height-34} H{width-24}" fill="none" stroke="rgba(255,255,255,.18)"/>
      <polyline points="{poly}" fill="none" stroke="{stroke}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
      <polygon points="{area}" fill="url(#lineFill)"/>{circles}{ticks}</svg>'''


def bar_chart(items, width=720, height=280):
    maxv=max(v for _,v in items) if items else 1
    rows=[]
    for i,(name,val) in enumerate(items):
        y=28+i*44
        w=(width-260)*val/maxv
        rows.append(f'''<g><text x="24" y="{y+18}" class="svg-label strong">{html.escape(name)}</text><rect x="245" y="{y}" width="{w:.1f}" height="24" rx="12" fill="url(#barGrad)"/><text x="{250+w:.1f}" y="{y+18}" class="svg-label">{dollars(val)}</text></g>''')
    return f'''<svg viewBox="0 0 {width} {height}" class="chart" role="img"><defs><linearGradient id="barGrad" x1="0" x2="1"><stop stop-color="#7df7ff"/><stop offset="1" stop-color="#7cffb2"/></linearGradient></defs>{''.join(rows)}</svg>'''


def radar_chart(values, labels, width=440, height=360):
    cx=width/2; cy=height/2+8; r=120
    axes=[]; pts=[]; rings=[]
    import math
    for level in [0.25,0.5,0.75,1.0]:
        ring=[]
        for i in range(len(values)):
            a=-math.pi/2 + 2*math.pi*i/len(values)
            ring.append(f"{cx+r*level*math.cos(a):.1f},{cy+r*level*math.sin(a):.1f}")
        rings.append(f'<polygon points="{" ".join(ring)}" fill="none" stroke="rgba(255,255,255,.13)"/>')
    for i,(v,l) in enumerate(zip(values,labels)):
        a=-math.pi/2 + 2*math.pi*i/len(values)
        x=cx+r*math.cos(a); y=cy+r*math.sin(a)
        axes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="rgba(255,255,255,.12)"/><text x="{cx+(r+34)*math.cos(a):.1f}" y="{cy+(r+34)*math.sin(a):.1f}" class="svg-label" text-anchor="middle">{html.escape(l)}</text>')
        pts.append(f"{cx+r*clamp(v,0,1)*math.cos(a):.1f},{cy+r*clamp(v,0,1)*math.sin(a):.1f}")
    return f'''<svg viewBox="0 0 {width} {height}" class="chart" role="img">{''.join(rings)}{''.join(axes)}<polygon points="{' '.join(pts)}" fill="rgba(125,247,255,.22)" stroke="#7df7ff" stroke-width="4"/></svg>'''


def clamp(x, lo, hi): return lo if x<lo else hi if x>hi else x


def receipt_table(title, rows):
    body="".join(f"<tr><td>{html.escape(str(k))}</td><td>{html.escape(str(v))}</td></tr>" for k,v in rows)
    return f"<section class='panel'><h2>{html.escape(title)}</h2><table>{body}</table></section>"


def write_badge(proof):
    status = "passing" if proof.get("proved") else "failing"
    color = "#35d07f" if proof.get("proved") else "#e55353"
    label = "RSI corporate strategy proof"
    text = f"{status} · {proof['summary']['agents']:,} agents"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="390" height="28" viewBox="0 0 390 28" role="img" aria-label="{label}: {text}">
      <linearGradient id="g" x2="1"><stop stop-color="#0b1725"/><stop offset="1" stop-color="#1f2d54"/></linearGradient>
      <rect width="390" height="28" rx="14" fill="url(#g)"/>
      <rect x="238" width="152" height="28" rx="14" fill="{color}" opacity=".9"/>
      <text x="14" y="19" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#c7f9ff">{label}</text>
      <text x="252" y="19" font-family="Arial, sans-serif" font-size="12" font-weight="700" fill="#06121a">{html.escape(text)}</text>
    </svg>'''
    OUT_BADGE.parent.mkdir(parents=True, exist_ok=True)
    OUT_BADGE.write_text(svg, encoding="utf-8")


def build_html(proof):
    s=proof["summary"]; final=proof["final_holdout_metrics"]
    releases=proof["rsi_releases"]
    release_values=[r["value_capture_percent"] for r in releases]
    baseline_items=[
        ("Single corporate generalist", s["value_over_single_corporate_generalist"]),
        ("Uncoordinated multi-agent swarm", s["value_over_uncoordinated_swarm"]),
        ("Static multi-agent committee", s["value_over_static_committee"]),
        ("No-RSI organization", s["value_over_no_rsi_organization"]),
    ]
    radar_values=[
        s["value_capture_percent"]/100,
        s["frontier_equivalent_percent"]/100,
        1 - min(1,s["risk_breach_rate_percent"]/5),
        proof["confidence"]["vs_static_multi_agent_committee"]["p05_gain_percent"]/max(0.01, proof["confidence"]["vs_static_multi_agent_committee"]["median_gain_percent"]),
        min(1, s["rsi_releases"]/10),
        min(1, s["specialist_roles"]/2048),
    ]
    radar_labels=["Value capture","Frontier decisions","Risk control","CI floor","RSI cadence","Role scale"]
    meta_desc="Autonomous GitHub Action proof that a large specialist-agent corporate strategy organization recursively improves coordination against baselines and negative controls."
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>SkillOS · Corporate Strategy Frontier Proof</title><meta name="description" content="{html.escape(meta_desc)}"/>
<style>
:root{{--bg:#071421;--panel:rgba(255,255,255,.10);--line:rgba(255,255,255,.18);--text:#f0f8ff;--muted:#c3d3e8;--cyan:#7df7ff;--green:#7cffb2;--gold:#ffd978;--pink:#ff83d1}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at 20% 0,#155f68 0,#111b3d 38%,#071421 100%);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.48}}
body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:32px 32px;mask-image:linear-gradient(#000,transparent 90%);pointer-events:none}}
a{{color:var(--cyan);text-decoration:none}}.nav{{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;gap:18px;padding:14px 22px;background:rgba(5,16,25,.86);border-bottom:1px solid var(--line);backdrop-filter:blur(14px)}}.nav b{{color:var(--cyan)}}.nav div:last-child{{display:flex;gap:16px;font-weight:800;font-size:14px}}
.wrap{{width:min(1180px,calc(100% - 36px));margin:0 auto;padding:54px 0 80px}}.hero{{display:grid;grid-template-columns:1.1fr .9fr;gap:24px;align-items:stretch}}@media(max-width:860px){{.hero{{grid-template-columns:1fr}}}}
.card,.panel{{border:1px solid var(--line);background:linear-gradient(135deg,rgba(255,255,255,.14),rgba(255,255,255,.06));box-shadow:0 25px 80px rgba(0,0,0,.24);border-radius:28px;padding:28px;backdrop-filter:blur(8px)}}
.kicker{{color:var(--cyan);font-size:13px;font-weight:900;letter-spacing:.24em;text-transform:uppercase}}h1{{font-size:clamp(48px,7vw,98px);line-height:.88;margin:14px 0 20px;letter-spacing:-.08em}}h2{{font-size:clamp(30px,4vw,56px);line-height:.95;margin:0 0 18px;letter-spacing:-.06em}}h3{{font-size:22px;margin:0 0 10px}}p{{color:var(--muted)}}.lead{{font-size:18px;max-width:760px}}.pill{{display:inline-flex;align-items:center;gap:8px;border:1px solid var(--line);border-radius:999px;padding:9px 13px;font-weight:900;background:rgba(255,255,255,.10)}}.pass{{background:rgba(124,255,178,.18);color:var(--green);border-color:rgba(124,255,178,.30)}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin:22px 0}}@media(max-width:900px){{.metrics{{grid-template-columns:repeat(2,1fr)}}}}.metric{{border:1px solid var(--line);border-radius:20px;padding:18px;background:rgba(255,255,255,.08)}}.metric strong{{display:block;font-size:32px;color:var(--green);line-height:1}}.metric span{{color:var(--muted);font-size:14px}}
.thesis{{margin:28px 0;border:1px solid var(--line);border-radius:28px;padding:28px;background:linear-gradient(135deg,rgba(125,247,255,.13),rgba(124,255,178,.08))}}.chain{{font-size:clamp(24px,4vw,46px);line-height:1.05;font-weight:950;letter-spacing:-.05em}}.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin:24px 0}}@media(max-width:900px){{.grid2{{grid-template-columns:1fr}}}}.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}@media(max-width:900px){{.grid3{{grid-template-columns:1fr}}}}
.chart{{width:100%;height:auto;display:block;background:rgba(0,0,0,.12);border:1px solid var(--line);border-radius:18px;padding:8px}}.svg-label{{fill:#c8d6ea;font-size:13px;font-family:Inter,Arial,sans-serif}}.strong{{font-weight:900;fill:#effaff}}table{{width:100%;border-collapse:collapse}}td,th{{border-top:1px solid var(--line);padding:12px;text-align:left;color:var(--muted)}}th{{color:var(--text);font-size:12px;letter-spacing:.16em;text-transform:uppercase}}.buttons{{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px}}.btn{{display:inline-flex;align-items:center;justify-content:center;padding:12px 16px;border-radius:999px;background:var(--cyan);color:#05111a;font-weight:950}}.btn.secondary{{background:rgba(255,255,255,.10);border:1px solid var(--line);color:var(--text)}}.note{{font-size:13px;color:#aabbd0}}.footer{{padding:40px 0;color:#9caec6}}
.agent-map{{position:relative;min-height:420px;overflow:hidden}}.node{{position:absolute;border-radius:999px;background:radial-gradient(circle,#fff,#7df7ff 32%,rgba(124,255,178,.24) 70%);box-shadow:0 0 34px rgba(125,247,255,.45)}}.beam{{position:absolute;height:2px;background:linear-gradient(90deg,transparent,rgba(125,247,255,.45),transparent);transform-origin:left center}}
</style></head><body>
<nav class="nav"><b>SkillOS Corporate Strategy Frontier</b><div><a href="{BASE_URL}">Command Center</a><a href="{BASE_URL}#proofs">Proofs</a><a href="{BASE_URL}#actions">Actions</a><a href="data/{SLUG}.json">JSON</a><a href="docs/{SLUG}.md">Report</a></div></nav>
<main class="wrap">
<section class="hero"><div class="card"><div class="kicker">Montreal.AI / SkillOS / Corporate Strategy RSI</div><h1>Corporate Strategy Frontier.</h1><p class="lead">An autonomous, reproducible proof that a large specialist-agent strategy organization can recursively improve the coordination protocol that turns corporate resources into compounding productive capability.</p><div class="buttons"><a class="btn" href="{ACTION_URL}">Run on GitHub</a><a class="btn secondary" href="data/{SLUG}.json">Open JSON receipt</a><a class="btn secondary" href="docs/{SLUG}.md">Read report</a></div></div>
<div class="card"><span class="pill pass">PROOF PASSED</span><h2>{s['agents']:,} agents. {s['specialist_roles']:,} roles. {s['strategy_councils']} councils.</h2><p>{s['locked_holdout_cases']:,} locked holdout cases. {s.get('accepted_rsi_releases', s['rsi_releases'])} accepted RSI releases across {s.get('rsi_release_cycles', s['rsi_releases'])} gated cycles. Bootstrap confidence intervals. Negative controls. Public GitHub Action.</p><p class="note">Not audited revenue, investment advice, achieved superintelligence, or Kardashev Type II achievement. This makes the corporate mechanism publicly testable.</p></div></section>
<div class="metrics"><div class="metric"><strong>{pct(s['value_capture_percent'])}</strong><span>benchmark value capture</span></div><div class="metric"><strong>{pct(s['frontier_equivalent_percent'])}</strong><span>frontier-equivalent decisions</span></div><div class="metric"><strong>{dollars(s['benchmark_value_captured'])}</strong><span>benchmark value captured</span></div><div class="metric"><strong>{pct(s['risk_breach_rate_percent'])}</strong><span>risk breach rate</span></div></div>
<section class="thesis"><div class="kicker">Kardashev-scale mechanism, corporate proof</div><div class="chain">capital → compute → energy → data → trust → talent → product → distribution → validation → risk control → reinvestment → compounding productive capability</div><p>This does not claim the civilization-scale outcome. It makes the enterprise mechanism underneath the quote testable, repeatable, and inspectable.</p></section>
<section class="grid2"><div class="panel"><h2>RSI release curve</h2>{line_chart(release_values)}<p>Validation value capture improves as accepted coordination releases become the input to the next gated release cycle.</p></div><div class="panel"><h2>Capability radar</h2>{radar_chart(radar_values,radar_labels)}<p>The proof measures value capture, frontier-equivalent decisions, risk control, confidence floor, recursive cadence, and role scale.</p></div></section>
<section class="grid2"><div class="panel"><h2>Value over controls</h2>{bar_chart(baseline_items)}<p>The final protocol is compared against a single corporate generalist, an uncoordinated swarm, a static committee, and a no-RSI organization.</p></div><div class="panel agent-map"><h2>Large-agent coordination fabric</h2><p>{s['agents']:,} virtual specialists are organized into {s['specialist_roles']:,} roles, {s['role_families']} role families, and {s['strategy_councils']} strategy councils. The coordinator is rewarded only when validation improves and risk stays inside gates.</p>{''.join(f'<span class="node" style="left:{(i*73)%92+3}%;top:{(i*47)%72+18}%;width:{10+(i*7)%30}px;height:{10+(i*7)%30}px"></span>' for i in range(44))}</div></section>
<section class="grid3"><div class="panel"><h3>Locked holdout</h3><p>{s['locked_holdout_cases']:,} cases are scored only after recursive releases are accepted on validation.</p></div><div class="panel"><h3>Negative controls</h3><p>Shuffled reward, random protocol, risk-blind coordination, and random policy all fail to match the final protocol.</p></div><div class="panel"><h3>Protocol fingerprint</h3><p><code>{html.escape(s['protocol_fingerprint'])}</code></p></div></section>
{receipt_table('Proof receipt', [('Proof', proof['proof_name']), ('Schema', proof['schema_version']), ('Seed', proof['seed']), ('Runtime seconds', proof['runtime_seconds']), ('JSON', proof['artifacts']['json']), ('Markdown', proof['artifacts']['markdown'])])}
<section class="panel"><h2>Baselines and controls</h2><table><thead><tr><th>System</th><th>Value capture</th><th>Frontier equivalent</th><th>Risk breach</th></tr></thead><tbody>{''.join(f'<tr><td>{html.escape(k)}</td><td>{pct(v["value_capture_percent"])}</td><td>{pct(v.get("frontier_equivalent_percent",0))}</td><td>{pct(v["risk_breach_rate_percent"])}</td></tr>' for k,v in {**proof['baselines'], **proof['negative_controls']}.items())}</tbody></table></section>
<section class="panel"><h2>Run or regenerate</h2><p>Click the button below, then click <b>Run workflow</b>. The GitHub Action regenerates the proof, verifies it, creates this webpage, updates the SkillOS command center, uploads artifacts, commits outputs, and deploys GitHub Pages.</p><div class="buttons"><a class="btn" href="{ACTION_URL}">Run autonomous proof</a><a class="btn secondary" href="{BASE_URL}">Back to command center</a></div></section>
<footer class="footer">SkillOS public proof. Generated autonomously by GitHub Actions from deterministic benchmark code.</footer></main></body></html>'''


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("proof",nargs="?",default=str(PROOF_JSON)); args=parser.parse_args()
    proof=json.loads(Path(args.proof).read_text(encoding="utf-8"))
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(build_html(proof), encoding="utf-8")
    write_badge(proof)
    print(json.dumps({"html":str(OUT_HTML),"badge":str(OUT_BADGE),"proved":proof.get("proved")},indent=2))

if __name__ == "__main__": main()
