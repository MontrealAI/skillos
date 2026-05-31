#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path

PROOF_ID = "rsi-governance-frontier-proof"
PROOF_PAGE = f"{PROOF_ID}.html"


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def money(x: float) -> str:
    ax = abs(x)
    if ax >= 1e12:
        return f"${x/1e12:,.2f}T"
    if ax >= 1e9:
        return f"${x/1e9:,.2f}B"
    if ax >= 1e6:
        return f"${x/1e6:,.2f}M"
    return f"${x:,.0f}"


def pct(x: float, places: int = 3) -> str:
    return f"{100*x:.{places}f}%"


def svg_line_chart(points: list[dict], key: str, title: str) -> str:
    pts = [(p["release"], p[key]) for p in points]
    w, h = 760, 260
    pad_l, pad_r, pad_t, pad_b = 54, 24, 28, 40
    min_x, max_x = min(x for x, _ in pts), max(x for x, _ in pts)
    min_y = min(y for _, y in pts)
    max_y = max(y for _, y in pts)
    span = max(max_y - min_y, 0.01)
    min_y = max(0, min_y - 0.08 * span)
    max_y = min(1, max_y + 0.10 * span)
    def xy(x: float, y: float) -> tuple[float, float]:
        px = pad_l + (x - min_x) / (max_x - min_x or 1) * (w - pad_l - pad_r)
        py = h - pad_b - (y - min_y) / (max_y - min_y or 1) * (h - pad_t - pad_b)
        return px, py
    poly = " ".join(f"{xy(x,y)[0]:.1f},{xy(x,y)[1]:.1f}" for x, y in pts)
    area = f"{pad_l},{h-pad_b} " + poly + f" {w-pad_r},{h-pad_b}"
    circles = "".join(f"<circle cx='{xy(x,y)[0]:.1f}' cy='{xy(x,y)[1]:.1f}' r='4.5'/>" for x, y in pts if x % 2 == 0 or x == max_x)
    labels = "".join(f"<text x='{xy(x,y)[0]:.1f}' y='{h-14}' text-anchor='middle'>v{x}</text>" for x, y in pts if x % 3 == 0 or x == max_x)
    return f"""
<svg class="chart" viewBox="0 0 {w} {h}" aria-label="{html.escape(title)}">
  <defs><linearGradient id="linefill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#78ffb0" stop-opacity="0.34"/><stop offset="1" stop-color="#78ffb0" stop-opacity="0"/></linearGradient></defs>
  <rect x="0" y="0" width="{w}" height="{h}" rx="22" fill="rgba(5,17,33,.45)"/>
  <g stroke="rgba(191,231,255,.17)" stroke-width="1">
    <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h-pad_b}"/><line x1="{pad_l}" y1="{h-pad_b}" x2="{w-pad_r}" y2="{h-pad_b}"/>
  </g>
  <polygon points="{area}" fill="url(#linefill)"/>
  <polyline points="{poly}" fill="none" stroke="#78ffb0" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <g fill="#8fffd4">{circles}</g>
  <g fill="#b9d8e8" font-size="12" font-family="ui-monospace, SFMono-Regular, Menlo, monospace">{labels}</g>
  <text x="{pad_l}" y="21" fill="#eef8ff" font-size="17" font-weight="900" font-family="Inter, Arial">{html.escape(title)}</text>
  <text x="{w-pad_r}" y="21" fill="#78ffb0" font-size="15" font-weight="900" text-anchor="end" font-family="Inter, Arial">{pct(pts[-1][1])}</text>
</svg>"""


def svg_bar_chart(proof: dict) -> str:
    m = proof["metrics"]
    rows = [("SkillOS RSI", m["locked_holdout_value_capture_rate"], "#78ffb0")]
    for key, row in proof["baseline_metrics"].items():
        if key == "random_policy_control":
            continue
        rows.append((row["label"], row["value_capture_rate"], "#8edbff"))
    w, h = 760, 330
    max_v = max(v for _, v, _ in rows)
    bars = []
    for i, (label, v, color) in enumerate(rows):
        y = 55 + i * 52
        bw = 520 * v / max_v
        bars.append(f"""<text x="28" y="{y+20}" fill="#dff7ff" font-size="14" font-weight="800">{html.escape(label)}</text>
<rect x="260" y="{y}" width="520" height="28" rx="14" fill="rgba(255,255,255,.08)"/>
<rect x="260" y="{y}" width="{bw:.1f}" height="28" rx="14" fill="{color}" opacity=".95"/>
<text x="{270+bw:.1f}" y="{y+20}" fill="#06131f" font-size="12" font-weight="900" text-anchor="end">{pct(v,1)}</text>""")
    return f"""
<svg class="chart" viewBox="0 0 {w} {h}" aria-label="Baseline comparison">
  <rect x="0" y="0" width="{w}" height="{h}" rx="22" fill="rgba(5,17,33,.45)"/>
  <text x="28" y="30" fill="#eef8ff" font-size="18" font-weight="900" font-family="Inter, Arial">Holdout value capture by organization design</text>
  <g font-family="Inter, Arial">{''.join(bars)}</g>
</svg>"""


def svg_radar(proof: dict) -> str:
    m = proof["metrics"]
    items = [
        ("Coordination", m["role_quorum_pass_rate"]),
        ("Evidence", m["frontier_correct_rate"]),
        ("Risk", 1.0 - m["risk_breach_rate"]),
        ("Capital", m["locked_holdout_value_capture_rate"]),
        ("RSI", m["accepted_rsi_releases"] / max(1, m["rsi_release_cycles"])),
        ("Audit", m["median_decision_fit"]),
        ("Safety", 1.0 - m["unsafe_action_rate"]),
    ]
    w, h, cx, cy, r = 560, 380, 280, 204, 122
    rings = []
    for frac in [0.25, 0.5, 0.75, 1.0]:
        pts = []
        for i in range(len(items)):
            ang = -math.pi/2 + 2*math.pi*i/len(items)
            pts.append(f"{cx + r*frac*math.cos(ang):.1f},{cy + r*frac*math.sin(ang):.1f}")
        rings.append(f"<polygon points='{ ' '.join(pts) }' fill='none' stroke='rgba(191,231,255,.16)'/>")
    axes = []
    poly = []
    labels = []
    for i, (label, val) in enumerate(items):
        ang = -math.pi/2 + 2*math.pi*i/len(items)
        axes.append(f"<line x1='{cx}' y1='{cy}' x2='{cx + r*math.cos(ang):.1f}' y2='{cy + r*math.sin(ang):.1f}' stroke='rgba(191,231,255,.13)'/>")
        poly.append(f"{cx + r*clamp(val)*math.cos(ang):.1f},{cy + r*clamp(val)*math.sin(ang):.1f}")
        labels.append(f"<text x='{cx + (r+36)*math.cos(ang):.1f}' y='{cy + (r+36)*math.sin(ang):.1f}' fill='#cfe8f5' font-size='12' text-anchor='middle'>{html.escape(label)}</text>")
    return f"""
<svg class="chart" viewBox="0 0 {w} {h}" aria-label="Governance capability radar">
  <rect width="{w}" height="{h}" rx="22" fill="rgba(5,17,33,.45)"/>
  <text x="26" y="32" fill="#eef8ff" font-size="18" font-weight="900" font-family="Inter, Arial">Governance capability radar</text>
  <g>{''.join(rings)}{''.join(axes)}</g>
  <polygon points="{' '.join(poly)}" fill="rgba(126,247,255,.26)" stroke="#7ef7ff" stroke-width="4"/>
  <g font-family="Inter, Arial">{''.join(labels)}</g>
</svg>"""


def svg_lattice(proof: dict) -> str:
    domains = proof["agent_lattice"]["specialist_domains"]
    w, h = 980, 390
    cx, cy = 490, 195
    nodes = []
    links = []
    for i, d in enumerate(domains):
        ang = -math.pi/2 + 2*math.pi*i/len(domains)
        x = cx + 310*math.cos(ang)
        y = cy + 135*math.sin(ang)
        links.append(f"<path d='M {cx:.1f} {cy:.1f} Q {(cx+x)/2 + 30*math.sin(ang):.1f} {(cy+y)/2 - 25*math.cos(ang):.1f} {x:.1f} {y:.1f}' fill='none' stroke='rgba(126,247,255,.18)' stroke-width='2'/>")
        nodes.append(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='17' fill='#78ffb0' opacity='.85'/><text x='{x:.1f}' y='{y+39:.1f}' text-anchor='middle' fill='#dff7ff' font-size='12' font-weight='800'>{html.escape(d)}</text>")
    center = "<circle cx='490' cy='195' r='42' fill='#7ef7ff' opacity='.95'/><text x='490' y='189' text-anchor='middle' fill='#06131f' font-size='15' font-weight='900'>ROLE</text><text x='490' y='207' text-anchor='middle' fill='#06131f' font-size='15' font-weight='900'>QUORUM</text>"
    return f"""
<svg class="widechart" viewBox="0 0 {w} {h}" aria-label="Large specialist-agent governance lattice">
  <defs><radialGradient id="lglow"><stop offset="0" stop-color="#7ef7ff" stop-opacity=".34"/><stop offset="1" stop-color="#7ef7ff" stop-opacity="0"/></radialGradient></defs>
  <rect width="{w}" height="{h}" rx="26" fill="rgba(5,17,33,.45)"/>
  <circle cx="490" cy="195" r="230" fill="url(#lglow)"/>
  <text x="28" y="34" fill="#eef8ff" font-size="20" font-weight="900" font-family="Inter, Arial">Large-agent coordination lattice</text>
  <text x="28" y="60" fill="#b9d8e8" font-size="13" font-family="Inter, Arial">Evidence courts, risk courts, capital councils, audit, compute/energy, incentives, and reinvestment coordinate through role quorum.</text>
  <g>{''.join(links)}</g><g font-family="Inter, Arial">{center}{''.join(nodes)}</g>
</svg>"""


def gate_cards(proof: dict) -> str:
    cards = []
    for g in proof["proof_gates"]:
        cards.append(f"""<div class="gate"><div class="gate-status">{'PASS' if g['passed'] else 'FAIL'}</div><h4>{html.escape(g['name'])}</h4><p>{html.escape(g['detail'])}</p></div>""")
    return "\n".join(cards)


def baseline_table(proof: dict) -> str:
    m = proof["metrics"]
    rows = []
    for key, b in proof["baseline_metrics"].items():
        delta = m["benchmark_capital_equivalent_value_captured"] - b["capital_equivalent_value_captured"]
        rows.append(f"<tr><td>{html.escape(b['label'])}</td><td>{pct(b['value_capture_rate'])}</td><td>{pct(b['risk_breach_rate'])}</td><td>{money(delta)}</td></tr>")
    return """<table class="proof-table"><thead><tr><th>Control / baseline</th><th>Capture</th><th>Risk breach</th><th>Delta vs SkillOS</th></tr></thead><tbody>""" + "".join(rows) + "</tbody></table>"


def release_table(proof: dict) -> str:
    rows = []
    for r in proof["rsi_release_trace"]:
        if r["release"] in [0, 1, 2, 3, 5, 8, 13, 18] or r.get("accepted"):
            rows.append(f"<tr><td>v{r['release']}</td><td>{'accepted' if r.get('accepted') else 'rejected'}</td><td>{pct(r['validation_value_capture_rate'])}</td><td>{html.escape(r['lesson'])}</td></tr>")
    return """<table class="proof-table"><thead><tr><th>Release</th><th>Status</th><th>Validation capture</th><th>What improved</th></tr></thead><tbody>""" + "".join(rows) + "</tbody></table>"


def render(proof: dict) -> str:
    m = proof["metrics"]
    title = proof["proof_title"]
    claim_boundary = proof["claim_boundary"]
    public_json = f"data/{PROOF_ID}.json"
    public_doc = f"docs/{PROOF_ID}.md"
    public_badge = f"badges/{PROOF_ID}.svg"
    line = svg_line_chart(proof["rsi_release_trace"], "validation_value_capture_rate", "Validation-gated RSI release curve")
    bars = svg_bar_chart(proof)
    radar = svg_radar(proof)
    lattice = svg_lattice(proof)
    gates = gate_cards(proof)
    baselines = baseline_table(proof)
    releases = release_table(proof)
    rows_sample = proof["holdout_receipts_sample"][:8]
    receipts = "".join(f"<tr><td>{html.escape(r['case_id'])}</td><td>{html.escape(r['regime'])}</td><td>{pct(r['skillos_capture_rate'])}</td><td>{money(r['potential_value'])}</td><td>{'pass' if r['role_quorum_passed'] else 'fail'}</td></tr>" for r in rows_sample)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)} · SkillOS</title>
<meta name="description" content="A public GitHub Action benchmark proving validation-gated recursive self-improvement for a large AI-first governance specialist-agent lattice."/>
<style>
:root{{--bg:#071827;--panel:rgba(255,255,255,.10);--panel2:rgba(255,255,255,.14);--line:rgba(218,242,255,.18);--text:#edf8ff;--muted:#b7cfdd;--cyan:#7ef7ff;--green:#78ffb0;--gold:#f6d76a;--danger:#ff7b88;--deep:#101a38}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;background:radial-gradient(circle at 8% 18%,#0b6070 0,#092b44 34%,#151b3e 74%,#090d1a 100%);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.45;min-height:100vh}}
body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:34px 34px;mask-image:linear-gradient(to bottom,rgba(0,0,0,.9),rgba(0,0,0,.25));pointer-events:none;z-index:-2}}
canvas#field{{position:fixed;inset:0;z-index:-1;opacity:.36}}
a{{color:var(--cyan);text-decoration:none}} a:hover{{text-decoration:underline}} .nav{{position:sticky;top:0;z-index:20;backdrop-filter:blur(18px);background:rgba(4,16,28,.82);border-bottom:1px solid var(--line);height:56px;display:flex;align-items:center;justify-content:space-between;padding:0 22px}} .brand{{font-weight:1000;color:var(--cyan);letter-spacing:-.02em}} .navlinks{{display:flex;gap:20px;font-size:14px;font-weight:800}} .wrap{{width:min(1180px,calc(100% - 40px));margin:0 auto}} .hero{{padding:70px 0 46px;display:grid;grid-template-columns:1.1fr .9fr;gap:34px;align-items:stretch}} .eyebrow{{font-size:13px;letter-spacing:.32em;color:var(--cyan);font-weight:1000;text-transform:uppercase}} h1{{font-size:clamp(54px,8vw,112px);line-height:.88;margin:14px 0 22px;letter-spacing:-.08em}} .lead{{font-size:18px;color:#d8edf8;max-width:780px}} .hero-card,.card,.gate,.proof-table,.stat,.callout{{border:1px solid var(--line);background:linear-gradient(135deg,rgba(255,255,255,.15),rgba(255,255,255,.06));border-radius:28px;box-shadow:0 24px 80px rgba(0,0,0,.2)}} .hero-card{{padding:32px;display:flex;flex-direction:column;justify-content:space-between}} .badge{{display:inline-flex;border-radius:999px;padding:8px 13px;background:rgba(120,255,176,.22);color:var(--green);font-size:12px;font-weight:1000;letter-spacing:.16em;text-transform:uppercase}} .hero-card .big{{font-size:38px;line-height:1.02;font-weight:1000;letter-spacing:-.04em;margin:18px 0}} .fine{{color:#c1d7e3;font-size:14px}} .stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:14px 0 38px}} .stat{{padding:20px}} .stat strong{{display:block;color:var(--green);font-size:31px;letter-spacing:-.04em}} .stat span{{display:block;color:#c3d9e6;font-size:14px}} section{{padding:38px 0}} .section-title{{font-size:clamp(38px,5vw,68px);line-height:.92;letter-spacing:-.06em;margin:0 0 22px}} .grid2{{display:grid;grid-template-columns:1fr 1fr;gap:22px}} .grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}} .card{{padding:22px;overflow:hidden}} .card h3{{margin:0 0 10px;font-size:24px;letter-spacing:-.035em}} .card p{{color:var(--muted)}} .chart,.widechart{{width:100%;height:auto;display:block}} .widechart{{margin-top:18px}} .mechanism{{font-size:clamp(28px,4vw,54px);line-height:1.05;letter-spacing:-.055em;font-weight:1000}} .callout{{padding:28px;margin:20px 0}} .smallcap{{font-size:12px;letter-spacing:.26em;text-transform:uppercase;color:var(--cyan);font-weight:1000}} .gates{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}} .gate{{padding:17px}} .gate-status{{display:inline-flex;padding:6px 10px;border-radius:999px;background:rgba(120,255,176,.18);color:var(--green);font-size:11px;font-weight:1000;letter-spacing:.14em}} .gate h4{{margin:10px 0 6px;font-size:16px}} .gate p{{font-size:13px;color:#bfd5e2;margin:0}} .proof-table{{width:100%;border-collapse:separate;border-spacing:0;overflow:hidden}} th,td{{padding:14px 16px;text-align:left;border-bottom:1px solid var(--line)}} th{{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#a7bed0}} td{{color:#e7f5ff}} tr:last-child td{{border-bottom:0}} .cta-row{{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px}} .btn{{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:13px 18px;font-weight:1000;border:1px solid var(--line);background:rgba(255,255,255,.10);color:var(--text)}} .btn.primary{{background:var(--cyan);color:#05111c;border-color:transparent}} .footer{{padding:42px 0 70px;color:#b8cfe0}} .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}} .receipt{{max-height:460px;overflow:auto}} @media(max-width:900px){{.hero,.grid2,.grid3,.stats,.gates{{grid-template-columns:1fr}}.navlinks{{display:none}}h1{{font-size:56px}}}}
</style>
</head>
<body>
<canvas id="field"></canvas>
<nav class="nav"><div class="brand">SkillOS Governance Frontier</div><div class="navlinks"><a href="index.html">Command Center</a><a href="#proof">Proof</a><a href="#agents">Multi-Agent</a><a href="#receipts">Receipts</a><a href="{html.escape(proof['workflow_url'])}">Run</a><a href="{html.escape(proof['repository'])}">GitHub</a></div></nav>
<main class="wrap">
  <section class="hero">
    <div>
      <div class="eyebrow">Montreal.AI / SkillOS / AI-first governance</div>
      <h1>Governance Frontier.</h1>
      <p class="lead">A public, reproducible proof that a large autonomous specialist-agent governance lattice can recursively improve its own coordination protocol: evidence, role quorum, incentives, policy, permissions, capital, compute, energy, execution, audit, risk courts, and reinvestment.</p>
      <div class="cta-row"><a class="btn primary" href="{html.escape(proof['workflow_url'])}">Run the GitHub Action</a><a class="btn" href="{public_json}">Open JSON receipt</a><a class="btn" href="{public_doc}">Read report</a></div>
    </div>
    <aside class="hero-card">
      <div><span class="badge">Proof passed</span><div class="big">{m['virtual_specialist_agents']:,} agents.<br>{m['specialist_roles']:,} roles.<br>{m['accepted_rsi_releases']} accepted RSI releases.</div></div>
      <p class="fine">This benchmark does not claim achieved superintelligence, live revenue, legal advice, policy advice, investment advice, or Kardashev Type II achievement. It makes the institutional coordination mechanism publicly runnable and falsifiable.</p>
    </aside>
  </section>

  <section class="stats" aria-label="Top metrics">
    <div class="stat"><strong>{pct(m['locked_holdout_value_capture_rate'])}</strong><span>locked-holdout value capture</span></div>
    <div class="stat"><strong>{pct(m['frontier_correct_rate'])}</strong><span>frontier-correct governance decisions</span></div>
    <div class="stat"><strong>{money(m['benchmark_capital_equivalent_value_captured'])}</strong><span>benchmark capital-equivalent value captured</span></div>
    <div class="stat"><strong>{pct(m['risk_breach_rate'])}</strong><span>risk breach rate</span></div>
  </section>

  <section id="proof">
    <div class="callout"><div class="smallcap">Mechanism under test</div><div class="mechanism">{html.escape(proof['coordination_mechanism'])}</div><p class="fine">The quote about superintelligent machines and civilization-scale value becomes testable here as a mechanism, not as a claim of achievement: can institutional intelligence convert capital, compute, energy, trust, and governance into compounding capability?</p></div>
    <div class="grid2"><div class="card">{line}<p>Each accepted release must improve validation performance before the final locked holdout is scored.</p></div><div class="card">{radar}<p>The radar summarizes the proof gates that matter: coordination quality, evidence handling, risk discipline, role quorum, value capture, RSI, audit, and safety.</p></div></div>
  </section>

  <section id="agents">
    <h2 class="section-title">Large specialist-agent coordination.</h2>
    <p class="lead">The proof is not a single agent and not an uncoordinated swarm. It is an institutional lattice: specialist roles, evidence courts, risk courts, strategy councils, audit loops, and reinvestment release gates.</p>
    {lattice}
  </section>

  <section>
    <h2 class="section-title">Controls and baselines.</h2>
    <div class="grid2"><div class="card">{bars}</div><div class="card"><h3>What fails without coordination</h3><p>Single agents miss institutional constraints. Uncoordinated swarms duplicate effort and collapse on correlated errors. Static committees overfit yesterday's governance. No-RSI systems fail to turn lessons into better future decisions.</p><p><strong>SkillOS wins by recursively improving the coordination layer itself.</strong></p></div></div>
    <div class="card" style="margin-top:20px">{baselines}</div>
  </section>

  <section>
    <h2 class="section-title">Proof gates.</h2>
    <div class="gates">{gates}</div>
  </section>

  <section>
    <h2 class="section-title">Release lineage.</h2>
    <div class="card receipt">{releases}</div>
  </section>

  <section id="receipts">
    <h2 class="section-title">Receipts.</h2>
    <div class="grid3">
      <div class="card"><div class="smallcap">Proof hash</div><p class="mono">{html.escape(proof['proof_sha256'])}</p></div>
      <div class="card"><div class="smallcap">Workflow</div><p><a href="{html.escape(proof['workflow_url'])}">{html.escape(proof['workflow_file'])}</a></p></div>
      <div class="card"><div class="smallcap">Public badge</div><p><img src="{public_badge}" alt="proof badge" style="max-width:100%"></p></div>
    </div>
    <div class="card receipt" style="margin-top:18px"><table class="proof-table"><thead><tr><th>Case</th><th>Regime</th><th>Capture</th><th>Stake</th><th>Quorum</th></tr></thead><tbody>{receipts}</tbody></table></div>
  </section>

  <section>
    <div class="callout"><div class="smallcap">Plain-English conclusion</div><p class="lead">SkillOS demonstrates a governance machine that improves the institution's ability to improve itself. It does this autonomously, through a GitHub Action, with locked holdout evaluation, negative controls, bootstrap confidence intervals, public receipts, and a generated executive webpage.</p><div class="cta-row"><a class="btn primary" href="{html.escape(proof['workflow_url'])}">Regenerate the proof</a><a class="btn" href="index.html">Back to Command Center</a></div></div>
  </section>
</main>
<footer class="footer wrap">Generated by SkillOS. Public benchmark only. No claim of achieved superintelligence, live revenue, legal advice, policy advice, investment advice, customer results, or Kardashev Type II achievement.</footer>
<script>
const c=document.getElementById('field'),ctx=c.getContext('2d');let w,h,pts=[];function resize(){{w=c.width=innerWidth;h=c.height=innerHeight;pts=Array.from({{length:90}},(_,i)=>({{x:Math.random()*w,y:Math.random()*h,r:1+Math.random()*3,v:.2+Math.random()*.6,a:Math.random()*6.28}}));}}addEventListener('resize',resize);resize();function tick(){{ctx.clearRect(0,0,w,h);for(const p of pts){{p.a+=.004*p.v;p.x+=Math.cos(p.a)*.18;p.y+=Math.sin(p.a)*.18;if(p.x<0)p.x=w;if(p.x>w)p.x=0;if(p.y<0)p.y=h;if(p.y>h)p.y=0;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,6.283);ctx.fillStyle='rgba(126,247,255,.42)';ctx.fill();}}for(let i=0;i<pts.length;i++)for(let j=i+1;j<pts.length;j++){{const a=pts[i],b=pts[j],dx=a.x-b.x,dy=a.y-b.y,d=Math.hypot(dx,dy);if(d<135){{ctx.strokeStyle='rgba(126,247,255,'+(0.11*(1-d/135))+')';ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();}}}}requestAnimationFrame(tick)}}tick();
</script>
</body>
</html>"""


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--json", default=f"data/{PROOF_ID}.json")
    p.add_argument("--out", default=f"site/{PROOF_PAGE}")
    args = p.parse_args()
    proof = json.loads(Path(args.json).read_text(encoding="utf-8"))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(proof), encoding="utf-8")
    print(json.dumps({"rendered": True, "html": str(out), "public_page": proof["public_page"]}, indent=2))


if __name__ == "__main__":
    main()
