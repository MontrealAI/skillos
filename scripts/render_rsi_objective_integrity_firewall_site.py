#!/usr/bin/env python3
from __future__ import annotations
import html, json, math, sys
from pathlib import Path

PROOF_ID = "rsi-objective-integrity-firewall-proof"
TITLE = "Autonomous RSI Objective Integrity Firewall Proof"

def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)

def pct(x: float, digits: int = 1) -> str:
    return f"{100*x:.{digits}f}%"

def money_t(x: float) -> str:
    return f"${x:,.2f}T"

def sparkline(points, w=620, h=190, color="#82fff7"):
    vals = [float(p["validation_hidden_objective_capture"]) for p in points]
    if not vals: return ""
    lo = min(vals); hi = max(vals); span = max(hi-lo, 1e-9)
    coords=[]
    for i,v in enumerate(vals):
        x = 36 + i*(w-70)/max(len(vals)-1,1)
        y = h - 28 - (v-lo)/span*(h-60)
        coords.append((x,y))
    path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x,y in coords)
    circles = "".join(f"<circle cx='{x:.1f}' cy='{y:.1f}' r='3.2' fill='{color}'/>" for x,y in coords[::max(len(coords)//14,1)])
    labels = "".join(f"<text x='{x:.1f}' y='{h-8}' fill='#b9d5ef' font-size='10' text-anchor='middle'>v{points[i]['release_index']}</text>" for i,(x,y) in enumerate(coords) if i % 4 == 0)
    return f"<svg viewBox='0 0 {w} {h}' class='chart'><rect width='{w}' height='{h}' rx='18' fill='rgba(5,18,36,.66)'/><line x1='34' y1='{h-28}' x2='{w-24}' y2='{h-28}' stroke='rgba(255,255,255,.16)'/><line x1='34' y1='22' x2='34' y2='{h-28}' stroke='rgba(255,255,255,.16)'/><path d='{path}' fill='none' stroke='{color}' stroke-width='4'/>{circles}{labels}</svg>"

def bars(summaries):
    names = ["skillos_objective_integrity_firewall", "no_firewall_rsi", "static_metric_guardrail_catalog", "uncoordinated_agent_swarm", "proxy_maximizer", "synthetic_receipt_generator", "single_generalist"]
    rows=[]
    for name in names:
        s = summaries[name]
        truew = max(4, 96*s["locked_holdout_value_capture"])
        proxyw = max(4, 96*s["proxy_score"])
        gap = s["goodhart_gap"]
        label = name.replace("_", " ").title()
        rows.append(f"<div class='barrow'><span>{html.escape(label)}</span><div class='barbox'><i style='width:{truew:.1f}%'></i><em style='width:{proxyw:.1f}%'></em></div><b>{pct(s['locked_holdout_value_capture'])}</b><small>gap {pct(gap,2)}</small></div>")
    return "".join(rows)

def radar(m):
    labels = ["Objective fidelity", "Verifier power", "Adversarial rejection", "Coordination", "Transfer", "Risk control"]
    vals = [m["objective_fidelity_score"], m["verifier_power"], m["adversarial_rejection_rate"], m["coordination_quality"], m["transfer_score"], m["risk_control"]]
    cx=180; cy=150; r=102; pts=[]; axes=[]; rings=[]
    for ring in [0.25,0.5,0.75,1.0]:
        ringpts=[]
        for i in range(len(vals)):
            a=-math.pi/2 + i*2*math.pi/len(vals)
            ringpts.append(f"{cx+math.cos(a)*r*ring:.1f},{cy+math.sin(a)*r*ring:.1f}")
        rings.append(f"<polygon points='{' '.join(ringpts)}' fill='none' stroke='rgba(255,255,255,.12)'/>")
    for i,(lab,v) in enumerate(zip(labels,vals)):
        a=-math.pi/2 + i*2*math.pi/len(vals)
        x=cx+math.cos(a)*r*v; y=cy+math.sin(a)*r*v
        pts.append(f"{x:.1f},{y:.1f}")
        lx=cx+math.cos(a)*(r+42); ly=cy+math.sin(a)*(r+30)
        axes.append(f"<line x1='{cx}' y1='{cy}' x2='{cx+math.cos(a)*r:.1f}' y2='{cy+math.sin(a)*r:.1f}' stroke='rgba(255,255,255,.1)'/><text x='{lx:.1f}' y='{ly:.1f}' fill='#d8eaff' font-size='11' text-anchor='middle'>{html.escape(lab)}</text>")
    return f"<svg viewBox='0 0 360 300' class='radar'><rect width='360' height='300' rx='18' fill='rgba(5,18,36,.66)'/>{''.join(rings)}{''.join(axes)}<polygon points='{' '.join(pts)}' fill='rgba(141,245,255,.18)' stroke='#8df5ff' stroke-width='4'/></svg>"

def main() -> None:
    path = Path("data") / f"{PROOF_ID}.json"
    if not path.exists(): fail(f"missing receipt: {path}")
    r = json.loads(path.read_text(encoding="utf-8"))
    m = r["metrics"]
    site = Path("site"); site.mkdir(exist_ok=True)
    page = site / f"{PROOF_ID}.html"
    systems = r["system_summaries"]
    html_doc = f"""<!doctype html>
<html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{html.escape(TITLE)} | SkillOS</title>
<meta name='description' content='A public deterministic benchmark proof that SkillOS RSI resists Goodhart failures, proxy gaming, and synthetic receipts through objective-integrity courts and validation-gated releases.'>
<style>
:root{{--bg:#061321;--panel:rgba(255,255,255,.075);--line:rgba(255,255,255,.16);--text:#f2f8ff;--muted:#c4d5e7;--cyan:#8df5ff;--green:#7dffb2;--gold:#ffd479;}}
*{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 18% 10%,rgba(44,205,223,.22),transparent 32%),radial-gradient(circle at 80% 0%,rgba(131,91,255,.22),transparent 36%),linear-gradient(135deg,#071a25,#111a3c 65%,#0b1326);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;line-height:1.45}} 
body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:32px 32px;mask-image:linear-gradient(to bottom,black,transparent 88%);pointer-events:none}}
a{{color:var(--cyan);text-decoration:none}} nav{{position:sticky;top:0;z-index:5;height:58px;background:rgba(4,15,27,.88);backdrop-filter:blur(14px);border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 22px}} nav strong{{color:var(--cyan)}} nav span{{display:flex;gap:20px;font-weight:800;font-size:14px}}
.wrap{{width:min(1220px,92vw);margin:0 auto;padding:64px 0}} .hero{{display:grid;grid-template-columns:1.05fr .95fr;gap:28px;align-items:stretch}} .panel,.metric,.card{{background:linear-gradient(180deg,rgba(255,255,255,.10),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:28px;box-shadow:0 22px 80px rgba(0,0,0,.28)}} .panel{{padding:34px}}
.eyebrow{{color:var(--cyan);letter-spacing:.18em;text-transform:uppercase;font-weight:900;font-size:13px}} h1{{font-size:clamp(48px,7vw,96px);line-height:.88;margin:14px 0 20px;letter-spacing:-.08em}} h2{{font-size:clamp(34px,4vw,58px);letter-spacing:-.06em;margin:54px 0 20px}} h3{{font-size:25px;margin:0 0 10px;letter-spacing:-.04em}} p{{color:var(--muted)}} .lede{{font-size:19px;max-width:830px}} .warning{{color:#d9edff;background:rgba(255,212,121,.10);border:1px solid rgba(255,212,121,.28);border-radius:18px;padding:14px 16px}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:28px 0}} .metric{{padding:19px}} .metric b{{display:block;color:var(--green);font-size:34px;line-height:1}} .metric span{{color:var(--muted);font-size:13px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:22px}} .card{{padding:24px}} .chart,.radar{{width:100%;height:auto}} .barrow{{display:grid;grid-template-columns:220px 1fr 72px 80px;gap:14px;align-items:center;margin:12px 0;font-size:13px}} .barbox{{height:18px;background:rgba(255,255,255,.08);border-radius:100px;position:relative;overflow:hidden;border:1px solid rgba(255,255,255,.12)}} .barbox i,.barbox em{{position:absolute;left:0;top:0;bottom:0;border-radius:100px}} .barbox i{{background:linear-gradient(90deg,#7dffb2,#8df5ff)}} .barbox em{{height:5px;top:auto;background:#ffd479;opacity:.85}} .barrow b{{color:var(--green)}} .barrow small{{color:var(--gold)}}
.flow{{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}} .flow span{{padding:9px 12px;border:1px solid var(--line);border-radius:999px;background:rgba(255,255,255,.06);font-weight:800;font-size:12px;color:#dff7ff}} .btns{{display:flex;gap:14px;flex-wrap:wrap;margin-top:22px}} .btn{{display:inline-block;padding:13px 18px;border-radius:999px;background:var(--cyan);color:#001522;font-weight:900}} .btn.secondary{{background:transparent;color:var(--text);border:1px solid var(--line)}} code{{color:#8df5ff}} table{{width:100%;border-collapse:collapse;background:rgba(255,255,255,.045);border-radius:20px;overflow:hidden}} th,td{{text-align:left;padding:14px;border-bottom:1px solid rgba(255,255,255,.12);font-size:14px}} th{{color:#8df5ff;text-transform:uppercase;letter-spacing:.12em;font-size:11px}} td.num{{text-align:right;font-variant-numeric:tabular-nums}}
@media(max-width:900px){{.hero,.grid,.metrics{{grid-template-columns:1fr}} h1{{font-size:54px}} .barrow{{grid-template-columns:1fr}} nav span{{display:none}}}}
</style></head><body>
<nav><strong>SkillOS Objective Integrity Firewall</strong><span><a href='index.html'>Command Center</a><a href='proof-registry.json'>Registry</a><a href='data/{PROOF_ID}.json'>JSON</a><a href='docs/{PROOF_ID}.md'>Report</a><a href='https://github.com/MontrealAI/skillos/actions'>Run</a></span></nav>
<main class='wrap'>
<section class='hero'>
  <div class='panel'><div class='eyebrow'>Objective Integrity / Goodhart Firewall</div><h1>Optimization that refuses to cheat.</h1><p class='lede'>A deterministic public benchmark showing that SkillOS RSI can improve hidden-objective performance while resisting proxy gaming, synthetic receipts, reward tampering, benchmark memorization, and coordination theater.</p><div class='flow'>{''.join(f"<span>{html.escape(x)}</span>" for x in r['mechanism'])}</div><div class='btns'><a class='btn' href='data/{PROOF_ID}.json'>Open receipt</a><a class='btn secondary' href='docs/{PROOF_ID}.md'>Read report</a><a class='btn secondary' href='https://github.com/MontrealAI/skillos/actions'>Run on GitHub</a></div></div>
  <div class='panel'><div class='eyebrow'>Proof passed · {html.escape(r['selected_release'])}</div><h3>{m['virtual_specialist_agents']:,} virtual specialists. {m['objective_integrity_courts']:,} objective courts.</h3><p>Large-scale specialist-agent coordination is tested against deliberately adversarial metric environments. The system must preserve true hidden-objective value, not just produce attractive public proxy scores.</p><p class='warning'>{html.escape(r['public_claim_boundary'])}</p></div>
</section>
<section class='metrics'>
  <div class='metric'><b>{pct(m['locked_holdout_value_capture'])}</b><span>hidden-objective value capture</span></div>
  <div class='metric'><b>{pct(m['objective_fidelity_score'])}</b><span>objective fidelity</span></div>
  <div class='metric'><b>{pct(m['goodhart_gap'],2)}</b><span>Goodhart gap</span></div>
  <div class='metric'><b>{pct(m['risk_breach_rate'],2)}</b><span>risk breach rate</span></div>
</section>
<section class='grid'>
  <div class='card'><h3>RSI release curve</h3>{sparkline(r['release_curve'])}<p>Validation selects releases by hidden-objective capture, objective fidelity, low Goodhart gap, and zero risk breach.</p></div>
  <div class='card'><h3>Objective integrity radar</h3>{radar(m)}<p>Objective fidelity, verifier power, adversarial rejection, coordination, transfer, and risk control must all remain strong.</p></div>
</section>
<h2>Proxy scores are not enough</h2>
<div class='card'><p>The gold line is the public proxy score. The cyan bar is value captured against the locked hidden objective. Proxy maximizers can look excellent while failing the real target.</p>{bars(systems)}</div>
<h2>Control comparison</h2>
<table><thead><tr><th>System</th><th class='num'>Hidden capture</th><th class='num'>Proxy score</th><th class='num'>Goodhart gap</th><th class='num'>Risk breach</th></tr></thead><tbody>
{''.join(f"<tr><td>{html.escape(name.replace('_',' '))}</td><td class='num'>{pct(s['locked_holdout_value_capture'])}</td><td class='num'>{pct(s['proxy_score'])}</td><td class='num'>{pct(s['goodhart_gap'],2)}</td><td class='num'>{pct(s['risk_breach_rate'],2)}</td></tr>" for name,s in systems.items())}
</tbody></table>
<section class='metrics'>
  <div class='metric'><b>{money_t(m['benchmark_capital_equivalent_value_at_stake_trillions'])}</b><span>benchmark value at stake</span></div>
  <div class='metric'><b>{money_t(m['benchmark_capital_equivalent_value_captured_trillions'])}</b><span>captured by SkillOS</span></div>
  <div class='metric'><b>{money_t(m['benchmark_capital_equivalent_gain_vs_best_control_trillions'])}</b><span>gain over strongest control</span></div>
  <div class='metric'><b>{pct(m['causal_gain_vs_best_control_p05'])}</b><span>bootstrap p05 gain</span></div>
</section>
<div class='card'><h3>Receipt</h3><p>SHA-256: <code>{html.escape(r['receipt_sha256'])}</code></p><p>Generated at: <code>{html.escape(r['generated_at_utc'])}</code></p></div>
</main></body></html>"""
    page.write_text(html_doc, encoding="utf-8")
    print(json.dumps({"rendered": True, "html": str(page)}, indent=2))

if __name__ == "__main__":
    main()
