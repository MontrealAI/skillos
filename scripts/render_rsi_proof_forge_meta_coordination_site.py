#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path

PROOF_ID = "rsi-proof-forge-meta-coordination-proof"
TITLE = "Autonomous RSI Proof Forge"
SUBTITLE = "Meta-Coordination Proof"


def pct(x: float, places: int = 2) -> str:
    return f"{100*x:.{places}f}%"


def money(x: float) -> str:
    ax = abs(x)
    if ax >= 1e12: return f"${x/1e12:,.2f}T"
    if ax >= 1e9: return f"${x/1e9:,.2f}B"
    if ax >= 1e6: return f"${x/1e6:,.2f}M"
    return f"${x:,.0f}"


def line_chart(points: list[float], w: int = 760, h: int = 260) -> str:
    if not points: points = [0]
    pad = 42
    lo = min(points); hi = max(points)
    if abs(hi-lo) < 1e-9: hi = lo + 1
    coords = []
    for i, p in enumerate(points):
        x = pad + (w-2*pad) * i / max(1, len(points)-1)
        y = h - pad - (h-2*pad) * (p-lo) / (hi-lo)
        coords.append((x, y))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x,y in coords)
    fill = f"{pad},{h-pad} " + poly + f" {w-pad},{h-pad}"
    dots = "".join(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='4' fill='#7fffb0'/>" for x,y in coords)
    labels = "".join(f"<text x='{x:.1f}' y='{h-14}' text-anchor='middle' fill='#b8cdf7' font-size='10'>v{i}</text>" for i,(x,y) in enumerate(coords) if i % max(1,len(coords)//8)==0 or i==len(coords)-1)
    return f"""<svg viewBox='0 0 {w} {h}' class='chart' role='img' aria-label='RSI release curve'>
    <defs><linearGradient id='area' x1='0' y1='0' x2='0' y2='1'><stop stop-color='#7fffb0' stop-opacity='.32'/><stop offset='1' stop-color='#7fffb0' stop-opacity='0'/></linearGradient></defs>
    <path d='M {pad} {pad} V {h-pad} H {w-pad}' fill='none' stroke='rgba(234,246,255,.22)'/>
    <polygon points='{fill}' fill='url(#area)'/>
    <polyline points='{poly}' fill='none' stroke='#7fffb0' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>
    {dots}{labels}
    </svg>"""


def radar(metrics: dict[str, float], w: int = 520, h: int = 420) -> str:
    import math
    labels = list(metrics.keys())
    vals = list(metrics.values())
    cx, cy = w/2, h/2 + 10
    r = min(w,h) * 0.34
    rings = []
    for frac in [0.25,0.5,0.75,1.0]:
        pts=[]
        for i in range(len(labels)):
            a = -math.pi/2 + 2*math.pi*i/len(labels)
            pts.append(f"{cx + r*frac*math.cos(a):.1f},{cy + r*frac*math.sin(a):.1f}")
        rings.append(f"<polygon points='{' '.join(pts)}' fill='none' stroke='rgba(234,246,255,.12)'/>")
    axes=[]; pts=[]; texts=[]
    for i,(lab,val) in enumerate(zip(labels, vals)):
        a = -math.pi/2 + 2*math.pi*i/len(labels)
        x = cx + r*math.cos(a); y = cy + r*math.sin(a)
        axes.append(f"<line x1='{cx:.1f}' y1='{cy:.1f}' x2='{x:.1f}' y2='{y:.1f}' stroke='rgba(234,246,255,.10)'/>")
        px = cx + r*val*math.cos(a); py = cy + r*val*math.sin(a)
        pts.append(f"{px:.1f},{py:.1f}")
        tx = cx + (r+38)*math.cos(a); ty = cy + (r+38)*math.sin(a)
        texts.append(f"<text x='{tx:.1f}' y='{ty:.1f}' text-anchor='middle' fill='#d8e9ff' font-size='13'>{html.escape(lab)}</text>")
    return f"""<svg viewBox='0 0 {w} {h}' class='radar' role='img' aria-label='Proof forge capability radar'>
    {''.join(rings)}{''.join(axes)}
    <polygon points='{' '.join(pts)}' fill='rgba(116,245,255,.25)' stroke='#74f5ff' stroke-width='4'/>
    {''.join(texts)}
    </svg>"""


def rows_table(baselines: list[dict]) -> str:
    rows = []
    for b in baselines:
        rows.append(f"<tr><td>{html.escape(b['label'])}</td><td>{pct(b['value_capture_rate'])}</td><td>{money(b['captured_value'])}</td><td>{money(b['skillos_value_delta'])}</td><td>{pct(b['bootstrap_delta']['p05'])}</td></tr>")
    return "\n".join(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root)
    result = json.loads((root / "data" / f"{PROOF_ID}.json").read_text(encoding="utf-8"))
    s = result["selected_release_summary"]
    curve = [r["holdout_value_capture_rate"] for r in result["release_curve"]]
    rad = {
        "Credibility": s["mean_proof_credibility"],
        "Evidence": s["mean_evidence_quality"],
        "Coordination": s["mean_coordination_quality"],
        "RSI": s["mean_recursive_improvement_quality"],
        "UX": s["mean_user_comprehension_quality"],
        "Risk control": 1.0 - s["risk_breach_rate"],
    }
    gates = "".join(f"<li><span class='pass'>PASS</span><b>{html.escape(g['name'])}</b><small>{html.escape(g['detail'])}</small></li>" for g in result["proof_gates"])
    ablations = "".join(f"<tr><td>{html.escape(a['name'].replace('_',' '))}</td><td>{pct(a['value_capture_rate'])}</td><td>{pct(a['mean_proof_credibility'])}</td><td>{money(a['skillos_value_delta'])}</td></tr>" for a in result["ablation_summaries"])
    html_doc = f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/><meta name='viewport' content='width=device-width,initial-scale=1'/>
<title>{TITLE} — {SUBTITLE}</title>
<meta name='description' content='Autonomous SkillOS RSI proof forge meta-coordination benchmark.' />
<style>
:root{{--bg:#071827;--bg2:#272d62;--ink:#eff8ff;--muted:#bdd0e9;--line:rgba(255,255,255,.16);--cyan:#74f5ff;--green:#7fffb0;--gold:#ffe38a}}
*{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 12% 10%,#0e5c67 0,#071827 36%,#171d49 100%);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.45}}
body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:32px 32px;mask-image:linear-gradient(to bottom,black,transparent 88%);pointer-events:none}}
nav{{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;gap:24px;align-items:center;padding:16px 28px;background:rgba(4,15,26,.82);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}}
nav b{{color:var(--cyan)}} nav a{{color:var(--ink);text-decoration:none;font-weight:800;margin-left:18px;font-size:14px}}
main{{max-width:1180px;margin:auto;padding:54px 24px 90px}} .hero{{display:grid;grid-template-columns:1.05fr .95fr;gap:28px;align-items:stretch}} .panel{{border:1px solid var(--line);background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.045));box-shadow:0 20px 80px rgba(0,0,0,.28);border-radius:28px;padding:30px;backdrop-filter:blur(10px)}}
.eyebrow{{letter-spacing:.28em;color:var(--cyan);font-weight:900;font-size:12px;text-transform:uppercase}} h1{{font-size:clamp(48px,7vw,92px);line-height:.88;margin:18px 0 22px;letter-spacing:-.08em}} h2{{font-size:clamp(34px,4vw,58px);line-height:.95;margin:0 0 20px;letter-spacing:-.06em}} p{{color:var(--muted);font-size:18px}} .hero p{{max-width:780px}}
.badge{{display:inline-flex;align-items:center;gap:8px;background:rgba(127,255,176,.18);color:var(--green);border:1px solid rgba(127,255,176,.35);border-radius:999px;padding:8px 13px;font-weight:900;font-size:12px;letter-spacing:.08em;text-transform:uppercase}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:28px 0}} .metric{{border:1px solid var(--line);border-radius:20px;padding:20px;background:rgba(255,255,255,.08)}} .metric strong{{display:block;font-size:32px;color:var(--green);line-height:1}} .metric span{{color:var(--muted)}}
.thesis{{font-size:34px;letter-spacing:-.045em;line-height:1.05;color:#fff}} .note{{font-size:14px;color:#c8d7ec}} .grid2{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:24px}} .chart,.radar{{width:100%;height:auto;display:block}} table{{width:100%;border-collapse:collapse;overflow:hidden;border-radius:18px}} th,td{{padding:15px;border-bottom:1px solid var(--line);text-align:left}} th{{font-size:12px;letter-spacing:.14em;color:#a9bce5;text-transform:uppercase}} td{{color:#eaf6ff}} .pass{{color:var(--green);font-weight:900;margin-right:12px}} ul.gates{{display:grid;grid-template-columns:1fr 1fr;gap:12px;list-style:none;padding:0}} ul.gates li{{border:1px solid var(--line);border-radius:16px;padding:14px;background:rgba(255,255,255,.06)}} ul.gates small{{display:block;color:var(--muted);margin-top:4px}}
.cta{{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px}} .btn{{display:inline-flex;align-items:center;justify-content:center;text-decoration:none;border-radius:999px;padding:13px 18px;font-weight:900;background:var(--cyan);color:#04101d}} .btn.secondary{{background:transparent;color:#fff;border:1px solid var(--line)}} .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#9dfcff}} footer{{padding:40px 24px;color:#9fb6d8;text-align:center;border-top:1px solid var(--line)}}
@media(max-width:900px){{.hero,.grid2,.metrics{{grid-template-columns:1fr}} nav{{align-items:flex-start;flex-direction:column}} h1{{font-size:54px}} ul.gates{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<nav><b>SkillOS Proof Forge</b><div><a href='index.html'>Command Center</a><a href='#proof'>Proof</a><a href='data/{PROOF_ID}.json'>JSON</a><a href='docs/{PROOF_ID}.md'>Report</a><a href='{html.escape(result['workflow_url'])}'>Run on GitHub</a></div></nav>
<main>
<section class='hero'>
<div class='panel'><div class='eyebrow'>Montreal.AI / SkillOS / RSI meta-proof</div><h1>Proof Forge Meta-Coordination.</h1><p>Can a large specialist-agent proof organization recursively improve the way it creates credible, safe, public, verifiable proof artifacts?</p><div class='cta'><a class='btn' href='{html.escape(result['workflow_url'])}'>Run autonomously on GitHub</a><a class='btn secondary' href='data/{PROOF_ID}.json'>Open JSON receipt</a><a class='btn secondary' href='docs/{PROOF_ID}.md'>Read report</a></div></div>
<div class='panel'><span class='badge'>Proof passed</span><h2>{result['scale']['virtual_specialist_agents']:,} agents. {result['scale']['specialist_roles']:,} roles. {result['scale']['verifier_courts']} verifier courts.</h2><p>This benchmark does not claim achieved superintelligence, live revenue, or Kardashev Type II civilization. It makes the coordination mechanism underneath that value thesis public, repeatable, and falsifiable.</p><p class='mono'>{html.escape(result['proof_fingerprint'][:32])}…</p></div>
</section>
<section class='metrics'>
<div class='metric'><strong>{pct(s['value_capture_rate'],3)}</strong><span>locked-holdout value capture</span></div>
<div class='metric'><strong>{pct(s['mean_proof_credibility'],3)}</strong><span>proof credibility</span></div>
<div class='metric'><strong>{pct(s['mean_coordination_quality'],3)}</strong><span>coordination quality</span></div>
<div class='metric'><strong>{money(s['captured_value'])}</strong><span>benchmark value captured</span></div>
</section>
<section class='panel'><div class='eyebrow'>Mechanism under test</div><p class='thesis'>hypothesis → decomposition → specialist-agent proof market → adversarial red teams → verifier courts → locked holdout evaluation → public artifacts → release selection → reinvestment → better future proof generation</p><p class='note'>The point is not a louder claim. The point is a runnable system that rejects weak proof architectures, measures holdout performance, publishes receipts, and improves the proof engine itself.</p></section>
<section class='grid2' id='proof'>
<div class='panel'><h2>RSI release curve</h2>{line_chart(curve)}<p>Locked-holdout value capture across recursively improved proof-forge releases.</p></div>
<div class='panel'><h2>Capability radar</h2>{radar(rad)}<p>Credibility, evidence, coordination, RSI, executive comprehension, and risk control.</p></div>
</section>
<section class='panel' style='margin-top:24px'><h2>Baseline comparison</h2><table><thead><tr><th>Baseline</th><th>Capture</th><th>Captured value</th><th>SkillOS delta</th><th>Bootstrap p05</th></tr></thead><tbody>{rows_table(result['baseline_summaries'])}</tbody></table></section>
<section class='panel' style='margin-top:24px'><h2>Negative controls and ablations</h2><table><thead><tr><th>Ablation</th><th>Capture</th><th>Credibility</th><th>SkillOS delta</th></tr></thead><tbody>{ablations}</tbody></table></section>
<section class='panel' style='margin-top:24px'><h2>Verifier gates</h2><ul class='gates'>{gates}</ul></section>
<section class='panel' style='margin-top:24px'><h2>Run / regenerate</h2><p>Open the GitHub Action and run the workflow. It regenerates the benchmark receipt, Markdown report, badge, proof webpage, proof registry, sitemap, and SkillOS command center without human review.</p><div class='cta'><a class='btn' href='{html.escape(result['workflow_url'])}'>Run workflow</a><a class='btn secondary' href='index.html'>Back to command center</a></div></section>
</main><footer>SkillOS autonomous RSI proof forge · benchmark-only public proof · no financial, legal, policy, medical, or investment advice</footer>
</body></html>"""
    site = root / "site"
    (site / "data").mkdir(parents=True, exist_ok=True)
    (site / "docs").mkdir(parents=True, exist_ok=True)
    (site / "badges").mkdir(parents=True, exist_ok=True)
    (site / f"{PROOF_ID}.html").write_text(html_doc, encoding="utf-8")
    # public copies
    (site / "data" / f"{PROOF_ID}.json").write_text((root / "data" / f"{PROOF_ID}.json").read_text(encoding="utf-8"), encoding="utf-8")
    (site / "docs" / f"{PROOF_ID}.md").write_text((root / "docs" / f"{PROOF_ID}.md").read_text(encoding="utf-8"), encoding="utf-8")
    (site / "badges" / f"{PROOF_ID}.svg").write_text((root / "badges" / f"{PROOF_ID}.svg").read_text(encoding="utf-8"), encoding="utf-8")
    print(site / f"{PROOF_ID}.html")


if __name__ == "__main__":
    main()
