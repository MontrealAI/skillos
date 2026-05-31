#!/usr/bin/env python3
import html, json, math, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "rsi-ai-first-governance-capital-engine-proof"
TITLE = "AI-First Governance Capital Engine"
PROOF_NAME = "Autonomous RSI AI-First Governance Capital Engine Proof"


def money(value):
    if abs(value) >= 1e12:
        return f"${value/1e12:,.2f}T"
    if abs(value) >= 1e9:
        return f"${value/1e9:,.2f}B"
    if abs(value) >= 1e6:
        return f"${value/1e6:,.2f}M"
    return f"${value:,.0f}"


def pct(value, digits=3):
    return f"{value*100:,.{digits}f}%"


def esc(x):
    return html.escape(str(x), quote=True)


def line_chart(curve):
    w, h, pad = 720, 230, 38
    vals = [p["validation_value_capture"] for p in curve]
    ymin = max(0.0, min(vals) - 0.02)
    ymax = min(1.02, max(vals) + 0.01)
    def xy(i, v):
        x = pad + (w - 2*pad) * i / max(1, len(vals) - 1)
        y = h - pad - (h - 2*pad) * ((v - ymin) / max(1e-9, ymax - ymin))
        return x, y
    pts = [xy(i, v) for i, v in enumerate(vals)]
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"{pad},{h-pad} " + poly + f" {w-pad},{h-pad}"
    dots = "".join(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='4' fill='#79ffd0'/>" for x, y in pts)
    labels = "".join(f"<text x='{xy(i,v)[0]:.1f}' y='{h-10}' text-anchor='middle' font-size='10' fill='#b9d6e7'>v{i}</text>" for i, v in enumerate(vals) if i % 2 == 0 or i == len(vals)-1)
    return f"""<svg viewBox='0 0 {w} {h}' class='chart' role='img' aria-label='RSI release curve'>
<defs><linearGradient id='area' x1='0' x2='0' y1='0' y2='1'><stop offset='0' stop-color='#79ffd0' stop-opacity='.45'/><stop offset='1' stop-color='#79ffd0' stop-opacity='.05'/></linearGradient></defs>
<line x1='{pad}' y1='{h-pad}' x2='{w-pad}' y2='{h-pad}' stroke='rgba(255,255,255,.22)'/><line x1='{pad}' y1='{pad}' x2='{pad}' y2='{h-pad}' stroke='rgba(255,255,255,.22)'/>
<polygon points='{area}' fill='url(#area)'/><polyline points='{poly}' fill='none' stroke='#79ffd0' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>{dots}{labels}</svg>"""


def radar_chart(obj):
    m = obj["metrics"]
    profile = obj.get("average_selected_dimension_profile", {})
    axes = [
        ("Evidence", profile.get("evidence_integrity", .8)),
        ("Role quorum", profile.get("role_coverage", .8)),
        ("Risk courts", 1 - m["risk_breach_rate"]),
        ("Execution", profile.get("execution_authority", .8)),
        ("Capital", profile.get("capital_allocation_quality", .8)),
        ("Compounding", profile.get("reinvestment_compounding", .8)),
        ("Audit", profile.get("auditability", .8)),
        ("Trust", profile.get("stakeholder_trust", .8)),
    ]
    w = h = 360
    cx = cy = 180
    maxr = 126
    rings = "".join(f"<polygon points='" + " ".join(f"{cx+math.cos(2*math.pi*i/len(axes)-math.pi/2)*maxr*r/4:.1f},{cy+math.sin(2*math.pi*i/len(axes)-math.pi/2)*maxr*r/4:.1f}" for i in range(len(axes))) + f"' fill='none' stroke='rgba(255,255,255,.12)'/>" for r in range(1,5))
    spokes = "".join(f"<line x1='{cx}' y1='{cy}' x2='{cx+math.cos(2*math.pi*i/len(axes)-math.pi/2)*maxr:.1f}' y2='{cy+math.sin(2*math.pi*i/len(axes)-math.pi/2)*maxr:.1f}' stroke='rgba(255,255,255,.10)'/>" for i in range(len(axes)))
    pts = []
    labels = []
    for i, (label, val) in enumerate(axes):
        angle = 2*math.pi*i/len(axes)-math.pi/2
        r = maxr * max(0, min(1, val))
        pts.append(f"{cx+math.cos(angle)*r:.1f},{cy+math.sin(angle)*r:.1f}")
        labels.append(f"<text x='{cx+math.cos(angle)*(maxr+28):.1f}' y='{cy+math.sin(angle)*(maxr+28):.1f}' text-anchor='middle' dominant-baseline='middle' fill='#d9f4ff' font-size='12'>{esc(label)}</text>")
    return f"""<svg viewBox='0 0 {w} {h}' class='chart' role='img' aria-label='Governance coordination radar'>
{rings}{spokes}<polygon points='{' '.join(pts)}' fill='rgba(126,247,255,.24)' stroke='#7ef7ff' stroke-width='4'/>{''.join(labels)}</svg>"""


def bar_chart(obj):
    m = obj["metrics"]
    baselines = obj["baselines"]
    rows = [("SkillOS RSI", m["holdout_value_capture"]), ("No-RSI org", baselines["no_rsi_governance_org"]["value_capture"]), ("Uncoordinated swarm", baselines["uncoordinated_agent_swarm"]["value_capture"]), ("Static committee", baselines["static_committee"]["value_capture"]), ("Single executive", baselines["single_executive"]["value_capture"])]
    width = 680
    rowh = 42
    h = 60 + rowh * len(rows)
    parts = [f"<svg viewBox='0 0 {width} {h}' class='chart' role='img' aria-label='Baseline comparison'>"]
    for i, (label, val) in enumerate(rows):
        y = 36 + i * rowh
        bw = 430 * val
        color = '#79ffd0' if i == 0 else '#7ef7ff'
        parts.append(f"<text x='18' y='{y+18}' fill='#eaf9ff' font-size='14' font-weight='800'>{esc(label)}</text>")
        parts.append(f"<rect x='210' y='{y}' width='430' height='24' rx='12' fill='rgba(255,255,255,.08)'/>")
        parts.append(f"<rect x='210' y='{y}' width='{bw:.1f}' height='24' rx='12' fill='{color}' opacity='{1 if i==0 else .55}'/>")
        parts.append(f"<text x='650' y='{y+18}' fill='#eaf9ff' font-size='13' text-anchor='end'>{pct(val,1)}</text>")
    parts.append("</svg>")
    return "".join(parts)


def lattice_svg(m):
    nodes = []
    links = []
    center = (340, 180)
    groups = [
        ("Evidence", 120, 68), ("Risk", 280, 44), ("Capital", 500, 70), ("Policy", 600, 190),
        ("Audit", 480, 310), ("RSI", 280, 330), ("Execution", 110, 260), ("Trust", 70, 150),
    ]
    for i, (label, x, y) in enumerate(groups):
        links.append(f"<line x1='{center[0]}' y1='{center[1]}' x2='{x}' y2='{y}' stroke='rgba(126,247,255,.26)' stroke-width='2'/>")
        nodes.append(f"<circle cx='{x}' cy='{y}' r='{22+i%3*4}' fill='rgba(126,247,255,.20)' stroke='#7ef7ff'/><text x='{x}' y='{y+42}' fill='#d9f4ff' font-size='12' text-anchor='middle'>{label}</text>")
    core = f"<circle cx='{center[0]}' cy='{center[1]}' r='46' fill='rgba(121,255,208,.26)' stroke='#79ffd0' stroke-width='3'/><text x='{center[0]}' y='{center[1]-5}' fill='#eafff8' font-size='13' font-weight='900' text-anchor='middle'>Governance</text><text x='{center[0]}' y='{center[1]+14}' fill='#eafff8' font-size='13' font-weight='900' text-anchor='middle'>lattice</text>"
    return f"""<svg viewBox='0 0 680 380' class='chart' role='img' aria-label='Large specialist agent governance lattice'>
<defs><radialGradient id='pulse'><stop offset='0' stop-color='#79ffd0' stop-opacity='.7'/><stop offset='1' stop-color='#7ef7ff' stop-opacity='.04'/></radialGradient></defs>
<rect width='680' height='380' rx='24' fill='rgba(5,18,32,.45)'/><circle cx='340' cy='180' r='150' fill='url(#pulse)'/>{''.join(links)}{core}{''.join(nodes)}
<text x='24' y='344' fill='#b8d8e7' font-size='13'>{m['virtual_specialist_agents']:,} virtual specialists · {m['specialist_roles']:,} roles · {m['strategy_councils']} councils · zero human-review gate</text></svg>"""


def decision_rows(records):
    rows = []
    for rec in records[:12]:
        rows.append(f"<tr><td>{esc(rec['case_id'])}</td><td>{esc(rec['regime'])}</td><td>{esc(rec['selected_architecture'])}</td><td>{pct(rec['case_capture'], 2)}</td><td>{money(rec['capital_equivalent_value_at_stake'])}</td></tr>")
    return "".join(rows)


def main():
    obj = json.loads((ROOT / "data" / f"{SLUG}.json").read_text())
    m = obj["metrics"]
    site = ROOT / "site"
    site.mkdir(exist_ok=True)
    run_url = f"https://github.com/{m.get('github_repository','MontrealAI/skillos')}/actions/workflows/autonomous-rsi-ai-first-governance-capital-engine-proof.yml"
    proof_url = f"https://montrealai.github.io/skillos/{SLUG}.html"
    status = "PROOF PASSED" if m["proved"] else "PROOF FAILED"
    html_doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{esc(PROOF_NAME)}</title>
<meta name="description" content="A public autonomous SkillOS proof for AI-first governance RSI and large specialist-agent coordination."/>
<style>
:root{{--bg:#061220;--panel:rgba(255,255,255,.095);--line:rgba(255,255,255,.19);--text:#effbff;--muted:#bdd5e4;--cyan:#7ef7ff;--green:#79ffd0;--violet:#afa4ff;}}
*{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 20% 10%,rgba(21,161,183,.34),transparent 32%),linear-gradient(135deg,#061220,#112746 50%,#302c6b);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;}}
body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:34px 34px;mask-image:linear-gradient(to bottom,black,transparent 95%);pointer-events:none}}
a{{color:var(--cyan);text-decoration:none;font-weight:800}} nav{{position:sticky;top:0;z-index:3;backdrop-filter:blur(18px);background:#061220e8;border-bottom:1px solid var(--line);height:58px;display:flex;align-items:center;justify-content:space-between;padding:0 22px}} .brand{{color:var(--cyan);font-weight:950}} .navlinks{{display:flex;gap:18px;font-size:14px}} main{{max-width:1200px;margin:auto;padding:64px 22px 90px}} .hero{{display:grid;grid-template-columns:1.15fr .85fr;gap:28px;align-items:center}} .eyebrow{{color:var(--cyan);font-size:12px;letter-spacing:.27em;text-transform:uppercase;font-weight:950}} h1{{font-size:clamp(58px,8.5vw,122px);line-height:.84;letter-spacing:-.085em;margin:14px 0 24px}} h2{{font-size:clamp(34px,5vw,72px);line-height:.9;letter-spacing:-.07em;margin:18px 0}} h3{{font-size:22px;margin:0 0 12px}} p{{color:var(--muted);font-size:17px;line-height:1.55}} .panel{{background:linear-gradient(145deg,rgba(255,255,255,.115),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:28px;padding:28px;box-shadow:0 30px 90px rgba(0,0,0,.28)}} .metric-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:34px 0}} .metric b{{display:block;color:var(--green);font-size:31px;letter-spacing:-.04em}} .metric span{{color:var(--muted)}} .grid2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}} .grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}} .pill{{display:inline-flex;border-radius:999px;padding:8px 12px;background:rgba(121,255,208,.18);border:1px solid rgba(121,255,208,.35);color:var(--green);font-size:12px;font-weight:950;letter-spacing:.12em;text-transform:uppercase}} .button{{display:inline-block;border-radius:999px;padding:13px 18px;background:var(--cyan);color:#04121e;font-weight:950;margin:6px 8px 6px 0}} .button.secondary{{background:transparent;color:var(--text);border:1px solid var(--line)}} .chart{{width:100%;height:auto}} table{{width:100%;border-collapse:collapse;font-size:14px;color:#dff8ff}} th,td{{border-bottom:1px solid rgba(255,255,255,.12);padding:12px;text-align:left;vertical-align:top}} th{{font-size:11px;text-transform:uppercase;letter-spacing:.18em;color:#a9c5d7}} .quote{{font-size:24px;line-height:1.35;color:#eefbff}} .note{{color:#ffd887}} .small{{font-size:13px;color:#a8c2d4}} @media(max-width:920px){{.hero,.grid2,.grid3,.metric-grid{{grid-template-columns:1fr}} h1{{font-size:56px}} .navlinks{{display:none}}}}
</style></head>
<body>
<nav><a class="brand" href="./index.html">SkillOS Governance Proof</a><div class="navlinks"><a href="./index.html">Command Center</a><a href="#proof">Proof</a><a href="#coordination">Multi-Agent</a><a href="#receipts">Receipts</a><a href="{esc(run_url)}">Run</a><a href="https://github.com/{esc(m.get('github_repository','MontrealAI/skillos'))}">GitHub</a></div></nav>
<main>
<section class="hero">
  <div><div class="eyebrow">Montreal.AI / SkillOS / AI-first governance RSI</div><h1>Governance Capital Engine.</h1><p>Autonomous proof that a large specialist-agent governance lattice can recursively improve how an AI-first organization turns evidence, decision rights, incentives, capital, compute, energy, policy, execution, auditing, risk courts, and reinvestment into compounding institutional capability.</p><p class="note">{esc(obj['public_note'])}</p><a class="button" href="{esc(run_url)}">Run proof on GitHub</a><a class="button secondary" href="./proof-registry.json">Proof registry</a><a class="button secondary" href="./data/{SLUG}.json">JSON receipt</a></div>
  <div class="panel"><span class="pill">{status}</span><h3 style="font-size:34px;line-height:1.05;margin-top:18px">{m['virtual_specialist_agents']:,} agents. {m['specialist_roles']:,} roles. {m['accepted_rsi_releases']} accepted RSI releases. {m['locked_holdout_cases']:,} locked holdout cases.</h3><p>A public, deterministic benchmark with train / validation / locked-holdout splits, negative controls, bootstrap confidence intervals, and no human-review gate.</p></div>
</section>
<section class="metric-grid" id="proof">
  <div class="panel metric"><b>{pct(m['holdout_value_capture'])}</b><span>locked-holdout value capture</span></div>
  <div class="panel metric"><b>{pct(m['frontier_correct_decision_rate'])}</b><span>frontier-correct decisions</span></div>
  <div class="panel metric"><b>{money(m['benchmark_capital_equivalent_value_captured'])}</b><span>capital-equivalent value captured</span></div>
  <div class="panel metric"><b>{pct(m['risk_breach_rate'])}</b><span>risk breach rate</span></div>
</section>
<section class="panel"><div class="eyebrow">Kardashev-scale value thesis, public-safe mechanism</div><h2>Make the wealth thesis testable.</h2><p class="quote">“{esc(obj['wealth_quote'])}”</p><p>This page does not claim that outcome. It makes one required substrate measurable: whether autonomous governance can convert scarce capital, compute, energy, trust, policy, and execution authority into a compounding capability loop under explicit risk gates.</p><h3>{esc(obj['mechanism'])}</h3></section>
<section class="grid2" style="margin-top:22px"><div class="panel"><h3>RSI release curve</h3>{line_chart(obj['rsi_release_curve'])}<p>Validation-gated governance releases are accepted only when the autonomous system improves capability without increasing unsafe action rates.</p></div><div class="panel"><h3>Governance coordination radar</h3>{radar_chart(obj)}<p>Evidence, role quorum, risk courts, execution, capital allocation, compounding, auditability, and trust are measured as one coordination system.</p></div></section>
<section id="coordination" class="grid2" style="margin-top:22px"><div class="panel"><h3>Large specialist-agent governance lattice</h3>{lattice_svg(m)}</div><div class="panel"><h3>Baseline comparison</h3>{bar_chart(obj)}<p>The test separates coordinated RSI from a single executive, static committee, uncoordinated swarm, no-RSI organization, risk-blind speed optimizer, random policy, and shuffled-evidence controls.</p></div></section>
<section class="grid3" style="margin-top:22px">
  <div class="panel"><span class="pill">No-RSI delta</span><h3>{money(m['value_over_no_rsi_governance_org'])}</h3><p>Capital-equivalent holdout value above the same organization before validation-gated recursive self-improvement.</p></div>
  <div class="panel"><span class="pill">Swarm delta</span><h3>{money(m['value_over_uncoordinated_agent_swarm'])}</h3><p>Value above a large but uncoordinated agent swarm. Many agents alone are not the moat; governance coordination is.</p></div>
  <div class="panel"><span class="pill">Autonomy</span><h3>0 human-review gates</h3><p>The GitHub Action runs, verifies, renders, publishes, and refreshes the command center autonomously.</p></div>
</section>
<section class="panel" style="margin-top:22px"><h2>Locked holdout decision receipts.</h2><table><thead><tr><th>Case</th><th>Governance regime</th><th>Selected architecture</th><th>Capture</th><th>Value at stake</th></tr></thead><tbody>{decision_rows(obj['sample_locked_holdout_decisions'])}</tbody></table></section>
<section id="receipts" class="panel" style="margin-top:22px"><h2>Receipts and reproducibility.</h2><p><a class="button" href="{esc(run_url)}">Run the GitHub Action</a><a class="button secondary" href="./data/{SLUG}.json">Open JSON receipt</a><a class="button secondary" href="./docs/{SLUG}.md">Open report</a><a class="button secondary" href="./badges/{SLUG}.svg">Open badge</a></p><p class="small">Fingerprint: <code>{esc(m['proof_fingerprint_sha256'])}</code></p></section>
</main></body></html>"""
    (site / f"{SLUG}.html").write_text(html_doc)
    for sub in ["data", "docs", "badges"]:
        (site / sub).mkdir(exist_ok=True)
    shutil.copy2(ROOT / "data" / f"{SLUG}.json", site / "data" / f"{SLUG}.json")
    shutil.copy2(ROOT / "docs" / f"{SLUG}.md", site / "docs" / f"{SLUG}.md")
    shutil.copy2(ROOT / "badges" / f"{SLUG}.svg", site / "badges" / f"{SLUG}.svg")
    print(json.dumps({"generated": True, "html": str(site / f"{SLUG}.html"), "url": proof_url}, indent=2))


if __name__ == "__main__":
    main()
