#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import math
from pathlib import Path

PROOF_ID = "rsi-capability-liquidity-engine-proof"
REPO_URL = "https://github.com/MontrealAI/skillos"
WORKFLOW_URL = f"{REPO_URL}/actions/workflows/autonomous-rsi-capability-liquidity-engine-proof.yml"


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


def line_chart(trace: list[dict]) -> str:
    accepted = [r for r in trace if r.get("accepted")]
    points = [(r["release"], r["validation_value_capture_rate"]) for r in accepted]
    width, height, pad = 560, 190, 32
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    ymax = max(ymax, ymin + 1e-9)
    coords = []
    dots = []
    for x, y in points:
        px = pad + (x - xmin) / (xmax - xmin if xmax != xmin else 1) * (width - 2 * pad)
        py = height - pad - (y - ymin) / (ymax - ymin) * (height - 2 * pad)
        coords.append(f"{px:.1f},{py:.1f}")
        dots.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3.8" fill="#7dffb2"/>')
    poly = " ".join(coords)
    return f'''<svg viewBox="0 0 560 190" role="img" aria-label="RSI release curve"><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#78ffb0" stop-opacity=".35"/><stop offset="1" stop-color="#78ffb0" stop-opacity=".02"/></linearGradient></defs><path d="M32 158 L{poly} L528 158 Z" fill="url(#area)"/><polyline points="{poly}" fill="none" stroke="#78ffb0" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>{''.join(dots)}<line x1="32" y1="158" x2="528" y2="158" stroke="rgba(255,255,255,.18)"/><line x1="32" y1="30" x2="32" y2="158" stroke="rgba(255,255,255,.18)"/></svg>'''


def radar(m: dict) -> str:
    labels = ["Liquidity", "Verification", "Coordination", "Trace RSI", "Role quorum", "Risk discipline"]
    vals = [m["capability_liquidity_score"], 1.0 - m["risk_breach_rate"], m["coordination_quality"], m["trace_compounding_score"], m["role_quorum_pass_rate"], 1.0 - m["unsafe_action_rate"]]
    cx, cy, rmax = 250, 200, 132
    rings = []
    for rr in [0.25, 0.5, 0.75, 1.0]:
        pts = []
        for i in range(6):
            a = -math.pi / 2 + i * 2 * math.pi / 6
            pts.append(f"{cx + rmax * rr * math.cos(a):.1f},{cy + rmax * rr * math.sin(a):.1f}")
        rings.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="rgba(255,255,255,.12)"/>')
    pts = []
    text = []
    for i, v in enumerate(vals):
        a = -math.pi / 2 + i * 2 * math.pi / 6
        pts.append(f"{cx + rmax * v * math.cos(a):.1f},{cy + rmax * v * math.sin(a):.1f}")
        tx = cx + (rmax + 46) * math.cos(a)
        ty = cy + (rmax + 46) * math.sin(a)
        text.append(f'<text x="{tx:.1f}" y="{ty:.1f}" text-anchor="middle" fill="#d9f6ff" font-size="13">{labels[i]}</text>')
    return f'<svg viewBox="0 0 500 400" role="img" aria-label="Capability radar">{"".join(rings)}<polygon points="{" ".join(pts)}" fill="#7ef7ff33" stroke="#7ef7ff" stroke-width="4"/>{"".join(text)}</svg>'


def bars(proof: dict) -> str:
    m = proof["metrics"]
    b = proof["baseline_metrics"]
    rows = [
        ("SkillOS RSI", m["locked_holdout_value_capture_rate"]),
        ("No-RSI marketplace", b["no_rsi_marketplace"]["value_capture_rate"]),
        ("Uncoordinated pool", b["uncoordinated_agent_pool"]["value_capture_rate"]),
        ("Static catalog", b["static_skill_catalog"]["value_capture_rate"]),
        ("Single agent", b["single_general_agent"]["value_capture_rate"]),
    ]
    out = []
    for label, val in rows:
        out.append(f'<div class="barrow"><div>{html.escape(label)}</div><div class="bar"><span style="width:{100 * val:.2f}%"></span></div><strong>{pct(val,2)}</strong></div>')
    return "".join(out)


def case_table(rows: list[dict]) -> str:
    body = []
    for r in rows[:10]:
        body.append(f'<tr><td>{html.escape(r["case_id"])}</td><td>{html.escape(r["regime"])}</td><td>{pct(r["capture_rate"],2)}</td><td>{pct(r["liquidity_score"],2)}</td><td>{"yes" if r["frontier_correct"] else "no"}</td></tr>')
    return "".join(body)


def render(proof: dict) -> str:
    m = proof["metrics"]
    curve = line_chart(proof["rsi_release_trace"])
    rad = radar(m)
    chartbars = bars(proof)
    sample = case_table(proof["holdout_evaluation_rows"])
    mechanism = html.escape(proof["mechanism"]["chain"])
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(proof["proof_title"])} | SkillOS</title>
<meta name="description" content="Autonomous SkillOS RSI proof for capability liquidity, large specialist-agent coordination, verifier courts, skill releases, and compounding capability."/>
<style>
:root{{--bg:#071827;--text:#f1f8ff;--muted:#bdd3e3;--line:rgba(220,245,255,.18);--cyan:#7ef7ff;--green:#78ffb0;--violet:#aaa0ff;--gold:#f6d76a}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at 10% 10%,#0c6570 0,#092a44 34%,#151b3e 78%,#070b16 100%);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.45}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:32px 32px;pointer-events:none;opacity:.85}}a{{color:var(--cyan);text-decoration:none}}a:hover{{text-decoration:underline}}.nav{{position:sticky;top:0;z-index:20;height:54px;padding:0 20px;display:flex;align-items:center;justify-content:space-between;background:rgba(4,14,26,.88);backdrop-filter:blur(20px);border-bottom:1px solid var(--line)}}.brand{{font-weight:1000;color:var(--cyan)}}.links{{display:flex;gap:16px;font-size:14px;font-weight:900}}.wrap{{width:min(1180px,calc(100% - 40px));margin:auto;position:relative}}.hero{{min-height:660px;padding:70px 0 35px;display:grid;grid-template-columns:1.05fr .95fr;gap:30px;align-items:center}}.eyebrow{{font-size:12px;letter-spacing:.34em;text-transform:uppercase;color:var(--cyan);font-weight:1000}}h1{{font-size:clamp(58px,8.2vw,124px);line-height:.86;letter-spacing:-.085em;margin:14px 0 22px}}.lead{{font-size:18px;color:#d5eaf8;max-width:820px}}.panel,.stat,.card,table{{border:1px solid var(--line);background:linear-gradient(135deg,rgba(255,255,255,.15),rgba(255,255,255,.055));border-radius:28px;box-shadow:0 28px 92px rgba(0,0,0,.22)}}.panel{{padding:30px}}.status{{display:inline-flex;border-radius:999px;padding:8px 12px;background:rgba(120,255,176,.18);color:var(--green);font-size:12px;font-weight:1000;letter-spacing:.16em}}.huge{{font-size:38px;line-height:1.02;letter-spacing:-.055em;font-weight:1000;margin:16px 0}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:8px 0 34px}}.stat{{padding:21px}}.stat strong{{display:block;color:var(--green);font-size:34px;letter-spacing:-.045em}}.stat span{{color:var(--muted)}}.mechanism{{font-size:clamp(28px,4vw,48px);line-height:1.08;letter-spacing:-.05em;font-weight:1000}}.section-title{{font-size:clamp(42px,5.6vw,74px);line-height:.9;letter-spacing:-.075em;margin:52px 0 22px}}.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.card{{padding:24px}}.card h3{{font-size:28px;margin:0 0 14px;letter-spacing:-.04em}}.chart{{background:rgba(6,17,32,.42);border:1px solid var(--line);border-radius:24px;padding:14px}}.barrow{{display:grid;grid-template-columns:180px 1fr 80px;gap:12px;align-items:center;margin:14px 0;color:#dff6ff}}.bar{{height:16px;border-radius:999px;border:1px solid var(--line);overflow:hidden;background:rgba(255,255,255,.06)}}.bar span{{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,var(--cyan),var(--green))}}table{{width:100%;border-collapse:separate;border-spacing:0;overflow:hidden}}th,td{{padding:14px 15px;text-align:left;border-bottom:1px solid var(--line)}}th{{font-size:12px;letter-spacing:.16em;text-transform:uppercase;color:#a9c0d2}}tr:last-child td{{border-bottom:0}}.btns{{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}}.btn{{display:inline-flex;border-radius:999px;border:1px solid var(--line);padding:12px 17px;color:var(--text);font-weight:1000}}.btn.primary{{background:var(--cyan);color:#06131f;border-color:transparent}}.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:#b9d6e9}}canvas{{width:100%;height:340px;border-radius:24px;background:rgba(3,12,24,.4);border:1px solid var(--line)}}footer{{padding:60px 0 80px;color:var(--muted)}}@media(max-width:900px){{.hero,.grid2,.stats{{grid-template-columns:1fr}}.links{{display:none}}h1{{font-size:58px}}.barrow{{grid-template-columns:1fr}}}}
</style></head><body>
<nav class="nav"><div class="brand">SkillOS Capability Liquidity Engine</div><div class="links"><a href="index.html">Command Center</a><a href="#proof">Proof</a><a href="#receipts">Receipts</a><a href="data/{PROOF_ID}.json">JSON</a><a href="{WORKFLOW_URL}">Run</a><a href="{REPO_URL}">GitHub</a></div></nav>
<main class="wrap">
<section class="hero"><div><div class="eyebrow">Montreal.AI / SkillOS / RSI proof</div><h1>Capabilities become liquid.</h1><p class="lead">A public, deterministic proof that a large autonomous specialist-agent marketplace can recursively improve how work is decomposed, routed, verified, released as skills, reused, and reinvested into compounding institutional capability.</p><div class="btns"><a class="btn primary" href="{WORKFLOW_URL}">Run proof on GitHub</a><a class="btn" href="data/{PROOF_ID}.json">Open JSON receipt</a><a class="btn" href="docs/{PROOF_ID}.md">Read report</a></div></div><aside class="panel"><div class="status">PROOF PASSED</div><div class="huge">{m['virtual_specialist_agents']:,} agents. {m['specialist_roles']:,} roles. {m['accepted_rsi_releases']} accepted RSI releases.</div><p class="lead">Locked holdout benchmark with verifier courts, role quorum, skill release lanes, negative controls, bootstrap confidence intervals, and public-safe claim boundaries.</p><p class="mono">proof sha256: {html.escape(proof['proof_sha256'][:24])}...</p></aside></section>
<section class="stats"><div class="stat"><strong>{pct(m['locked_holdout_value_capture_rate'])}</strong><span>locked-holdout value capture</span></div><div class="stat"><strong>{pct(m['capability_liquidity_score'])}</strong><span>capability liquidity</span></div><div class="stat"><strong>{pct(m['frontier_correct_rate'])}</strong><span>frontier-correct decisions</span></div><div class="stat"><strong>{pct(m['risk_breach_rate'])}</strong><span>risk breach rate</span></div></section>
<section class="panel"><div class="eyebrow">Capability-market mechanism</div><div class="mechanism">{mechanism}</div><p class="lead">This proof does not claim achieved superintelligence or Kardashev Type II civilization. It makes one mechanism under that thesis runnable: if capabilities become measurable, tradable, verifiable, and recursively released, coordination quality can compound.</p></section>
<section id="proof"><h2 class="section-title">Large-agent coordination, made testable.</h2><div class="grid2"><div class="card"><h3>RSI release curve</h3><div class="chart">{curve}</div><p>Validation-gated releases are accepted only when the system improves without breaching safety gates.</p></div><div class="card"><h3>Capability radar</h3><div class="chart">{rad}</div><p>Liquidity, verifier courts, role quorum, trace memory, and risk discipline are measured separately so the proof is not just a single score.</p></div></div></section>
<section><h2 class="section-title">Baseline dominance.</h2><div class="card">{chartbars}<p class="lead">The benchmark compares SkillOS RSI against a single general agent, an uncoordinated agent pool, a static skill catalog, and a no-RSI marketplace.</p></div></section>
<section><h2 class="section-title">What the proof measured.</h2><div class="grid2"><div class="card"><h3>Public benchmark scale</h3><p>{m['locked_holdout_cases']:,} locked holdout cases across {m['enterprise_regimes']} enterprise regimes; {m['candidate_routing_policies_per_case']} candidate routing policies per case; {m['capability_markets']} capability markets; {m['verifier_courts']} verifier courts; {m['skill_release_lanes']} skill release lanes.</p></div><div class="card"><h3>Benchmark-capital-equivalent impact</h3><p>Value at stake: <b>{money(m['benchmark_capital_equivalent_value_at_stake'])}</b><br/>Value captured: <b>{money(m['benchmark_capital_equivalent_value_captured'])}</b><br/>Over no-RSI marketplace: <b>{money(m['value_over_no_rsi_marketplace'])}</b></p></div></div></section>
<section id="receipts"><h2 class="section-title">Receipts.</h2><table><thead><tr><th>Holdout case</th><th>Regime</th><th>Capture</th><th>Liquidity</th><th>Beat baselines</th></tr></thead><tbody>{sample}</tbody></table></section>
<section><h2 class="section-title">Run / regenerate.</h2><div class="grid2"><div class="card"><h3>GitHub Action</h3><p>Click Run workflow. The action runs the benchmark, verifies proof gates, renders this webpage, updates the command center, uploads artifacts, and commits generated outputs.</p><a class="btn primary" href="{WORKFLOW_URL}">Run on GitHub</a></div><div class="card"><h3>Public-safe boundary</h3><p>No live revenue, no customer result, no investment advice, no guaranteed profit, no legal or policy advice, and no claim of achieved superintelligence or Kardashev Type II civilization.</p></div></div></section>
</main><footer class="wrap">SkillOS public benchmark artifact. Generated autonomously from a deterministic proof harness. <span class="mono">{html.escape(proof['generated_at'])}</span></footer>
<script>
const c=document.createElement('canvas');
const host=document.querySelector('.hero aside');
host.appendChild(c); const ctx=c.getContext('2d'); let w,h,pts=[];
function resize(){{w=c.width=c.clientWidth*devicePixelRatio;h=c.height=340*devicePixelRatio;pts=Array.from({{length:140}},()=>({{x:Math.random()*w,y:Math.random()*h,r:(Math.random()*4+1)*devicePixelRatio,vx:(Math.random()-.5)*.35,vy:(Math.random()-.5)*.35}}));}}
function draw(){{ctx.clearRect(0,0,w,h);ctx.fillStyle='rgba(126,247,255,.18)';ctx.strokeStyle='rgba(126,247,255,.12)';for(let i=0;i<pts.length;i++){{let p=pts[i];p.x=(p.x+p.vx+w)%w;p.y=(p.y+p.vy+h)%h;ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,7);ctx.fill();for(let j=i+1;j<pts.length;j++){{let q=pts[j],dx=p.x-q.x,dy=p.y-q.y,d=Math.hypot(dx,dy);if(d<90*devicePixelRatio){{ctx.globalAlpha=(1-d/(90*devicePixelRatio))*.8;ctx.beginPath();ctx.moveTo(p.x,p.y);ctx.lineTo(q.x,q.y);ctx.stroke();ctx.globalAlpha=1;}}}}requestAnimationFrame(draw);}}
addEventListener('resize',resize);resize();draw();
</script>
</body></html>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="data/rsi-capability-liquidity-engine-proof.json")
    parser.add_argument("--out", default="site/rsi-capability-liquidity-engine-proof.html")
    args = parser.parse_args()
    proof = json.loads(Path(args.json).read_text(encoding="utf-8"))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(proof), encoding="utf-8")
    print(json.dumps({"rendered": True, "html": str(out)}, indent=2))


if __name__ == "__main__":
    main()
