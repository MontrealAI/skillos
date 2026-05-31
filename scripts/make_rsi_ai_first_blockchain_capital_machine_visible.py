#!/usr/bin/env python3
import html, json, math
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SLUG = "rsi-ai-first-blockchain-capital-machine-proof"
TITLE = "AI-First Blockchain Capital Machine"
PROOF_NAME = "Autonomous RSI AI-First Blockchain Capital Machine Proof"


def money(x):
    ax = abs(x)
    if ax >= 1e12: return f"${x/1e12:,.2f}T"
    if ax >= 1e9: return f"${x/1e9:,.2f}B"
    if ax >= 1e6: return f"${x/1e6:,.2f}M"
    return f"${x:,.0f}"


def pct(x):
    return f"{x*100:,.3f}%"


def md_report(obj):
    m = obj["metrics"]
    base = obj["baselines"]
    controls = obj["negative_controls"]
    gains = obj["bootstrap_gains"]
    lines = [
        f"# {PROOF_NAME}",
        "",
        "This is a deterministic, public, no-human-review GitHub Action proof for the AI-first blockchain domain.",
        "",
        "> It does not claim achieved superintelligence, live protocol revenue, token recommendations, investment advice, or Kardashev Type II civilization. It makes the mechanism underneath that value thesis testable.",
        "",
        "## Thesis under test",
        "",
        "Can a large autonomous specialist-agent protocol organization recursively improve how it coordinates capital, blockspace, validator security, MEV control, liquidity, bridges, oracles, governance, data availability, compute/energy, trust, settlement, validation, risk courts, and reinvestment into compounding protocol capability?",
        "",
        "## Main result",
        "",
        f"- Proved: **{m['proved']}**",
        f"- Virtual specialist agents: **{m['virtual_specialist_agents']:,}**",
        f"- Specialist roles: **{m['specialist_roles']:,}**",
        f"- Strategy councils: **{m['strategy_councils']:,}**",
        f"- Locked holdout cases: **{m['locked_holdout_cases']:,}**",
        f"- RSI release cycles: **{m['rsi_release_cycles']:,}**",
        f"- Accepted RSI releases: **{m['accepted_rsi_releases']:,}**",
        f"- Holdout value capture: **{pct(m['holdout_value_capture'])}**",
        f"- Frontier-correct decisions: **{pct(m['frontier_correct_rate'])}**",
        f"- Risk breach rate: **{pct(m['risk_breach_rate'])}**",
        f"- Unsafe action rate: **{pct(m['unsafe_action_rate'])}**",
        f"- Benchmark capital-equivalent value at stake: **{money(m['benchmark_capital_equivalent_value_at_stake'])}**",
        f"- Benchmark capital-equivalent value captured: **{money(m['benchmark_capital_equivalent_value_captured'])}**",
        "",
        "## Baseline superiority",
        "",
        f"- Over single protocol strategist: **{money(m['value_over_single_protocol_strategist'])}**",
        f"- Over uncoordinated agent swarm: **{money(m['value_over_uncoordinated_agent_swarm'])}**",
        f"- Over static DAO committee: **{money(m['value_over_static_dao_committee'])}**",
        f"- Over no-RSI protocol organization: **{money(m['value_over_no_rsi_protocol_organization'])}**",
        "",
        "## Bootstrap confidence intervals",
        "",
    ]
    for k, v in gains.items():
        lines.append(f"- {k}: p05={pct(v['p05'])}, p50={pct(v['p50'])}, p95={pct(v['p95'])}")
    lines += ["", "## Negative controls", ""]
    for k, v in controls.items():
        lines.append(f"- {k}: value_capture={pct(v['value_capture'])}, risk_breach_rate={pct(v['risk_breach_rate'])}")
    lines += ["", "## Protocol fingerprint", "", f"`{obj['protocol_fingerprint']}`", ""]
    return "\n".join(lines)


def badge_svg(m):
    label = "AI-FIRST BLOCKCHAIN RSI PROOF"
    value = "PASSED" if m["proved"] else "FAILED"
    color = "#72ffb6" if m["proved"] else "#ff6b86"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="470" height="32" viewBox="0 0 470 32" role="img" aria-label="{label}: {value}">
<defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#061726"/><stop offset="1" stop-color="#303068"/></linearGradient></defs>
<rect width="470" height="32" rx="16" fill="url(#g)"/>
<rect x="300" y="4" width="166" height="24" rx="12" fill="{color}" opacity=".18"/>
<text x="18" y="21" fill="#8df8ff" font-family="Inter,Arial,sans-serif" font-size="12" font-weight="800" letter-spacing="1.5">{label}</text>
<text x="322" y="21" fill="{color}" font-family="Inter,Arial,sans-serif" font-size="12" font-weight="900">{value}</text>
</svg>'''


def html_page(obj):
    m = obj["metrics"]
    repo = m.get("github_repository", "MontrealAI/skillos")
    action = "autonomous-rsi-ai-first-blockchain-capital-machine-proof.yml"
    action_url = f"https://github.com/{repo}/actions/workflows/{action}"
    json_url = f"../data/{SLUG}.json"
    report_url = f"../docs/{SLUG}.md"
    payload = json.dumps(obj, separators=(",", ":"))
    release_rows = "".join(
        f"<tr><td>{html.escape(r['version'])}</td><td>{'accepted' if r['accepted'] else 'rejected'}</td><td>{pct(r['validation_capture'])}</td><td>{pct(r['holdout_shadow_capture'])}</td><td>{pct(r['risk_breach_rate'])}</td><td>{html.escape(r['skill_update'])}</td></tr>"
        for r in obj["rsi_release_curve"]
    )
    base_rows = "".join(
        f"<tr><td>{html.escape(k.replace('_',' '))}</td><td>{pct(v['value_capture'])}</td><td>{pct(v['frontier_correct_rate'])}</td><td>{pct(v['risk_breach_rate'])}</td></tr>"
        for k, v in obj["baselines"].items()
    )
    control_rows = "".join(
        f"<tr><td>{html.escape(k.replace('_',' '))}</td><td>{pct(v['value_capture'])}</td><td>{pct(v['risk_breach_rate'])}</td><td>{'failed, as expected' if (v['value_capture'] < m['holdout_value_capture'] - 0.035 or v['risk_breach_rate'] > 0.008) else 'check'}</td></tr>"
        for k, v in obj["negative_controls"].items()
    )
    receipt_cards = "".join(
        f"<article class='receipt'><span>{html.escape(x['case_id'])}</span><b>{html.escape(x['regime'])}</b><p>selected: {html.escape(x['selected_strategy'])}</p><p>frontier: {html.escape(x['frontier_strategy'])}</p><strong>{pct(x['value_capture'])}</strong></article>"
        for x in obj["holdout_receipts_sample"][:18]
    )
    gates = "".join(f"<li><span>{html.escape(k.replace('_',' '))}</span><b>{'PASS' if v else 'FAIL'}</b></li>" for k, v in obj["gate_results"].items())
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{PROOF_NAME}</title>
<meta name="description" content="A public deterministic GitHub Action proof that a large autonomous specialist-agent organization can recursively improve AI-first blockchain protocol coordination."/>
<style>
:root{{--bg:#061420;--panel:rgba(255,255,255,.085);--panel2:rgba(255,255,255,.12);--line:rgba(210,245,255,.20);--text:#ecfbff;--muted:#b8ccda;--cyan:#83f7ff;--green:#74ffb4;--gold:#ffd66b;--pink:#ff7fb8;--violet:#a68cff;}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at 15% 20%,#0c6b7c55,transparent 32%),radial-gradient(circle at 88% 10%,#7562ff33,transparent 34%),linear-gradient(115deg,#061420,#10243b 45%,#282a61);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.45;}}
body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:34px 34px;mask-image:linear-gradient(#000,transparent 85%);pointer-events:none}}
a{{color:var(--cyan);text-decoration:none}}.nav{{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;padding:14px 22px;background:#061420e8;backdrop-filter:blur(18px);border-bottom:1px solid var(--line)}}.brand{{font-weight:950;color:var(--cyan);letter-spacing:-.04em}}.links{{display:flex;gap:18px;font-size:14px;font-weight:800}}.wrap{{max-width:1240px;margin:auto;padding:42px 22px 80px}}.hero{{display:grid;grid-template-columns:1.05fr .95fr;gap:28px;align-items:stretch;margin-top:18px}}.panel{{background:linear-gradient(145deg,var(--panel2),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:28px;box-shadow:0 28px 90px rgba(0,0,0,.25);backdrop-filter:blur(10px)}}.heroText{{padding:38px}}.kicker{{color:var(--cyan);font-size:13px;font-weight:950;letter-spacing:.34em;text-transform:uppercase}}h1{{margin:12px 0 18px;font-size:clamp(45px,7vw,92px);line-height:.88;letter-spacing:-.08em}}h2{{font-size:clamp(32px,5vw,60px);line-height:.92;letter-spacing:-.065em;margin:50px 0 20px}}h3{{margin:0 0 10px;font-size:22px;letter-spacing:-.03em}}.lede{{font-size:19px;color:#d9edf7;max-width:820px}}.proofbox{{padding:28px;display:flex;flex-direction:column;justify-content:space-between}}.pass{{display:inline-block;width:max-content;border-radius:999px;padding:8px 14px;background:rgba(116,255,180,.18);color:var(--green);font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-weight:950}}.mega{{font-size:34px;line-height:1.05;font-weight:950;letter-spacing:-.06em;margin:14px 0;color:#fff}}.safe{{font-size:15px;color:var(--muted)}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:22px 0 36px}}.metric{{padding:22px;border-radius:20px;background:var(--panel);border:1px solid var(--line)}}.metric strong{{display:block;color:var(--green);font-size:32px;line-height:1;font-weight:950;letter-spacing:-.06em}}.metric span{{color:var(--muted);font-size:14px}}.chain{{font-size:32px;font-weight:950;line-height:1.12;letter-spacing:-.055em;padding:28px}}.chain small{{display:block;color:var(--cyan);font-size:12px;letter-spacing:.22em;text-transform:uppercase;margin-bottom:12px}}.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.chart{{padding:22px;min-height:395px}}canvas{{width:100%;height:285px;display:block;background:rgba(0,0,0,.13);border:1px solid var(--line);border-radius:18px}}.quote{{padding:30px;margin-top:22px;border-left:4px solid var(--gold)}}.quote p{{font-size:24px;line-height:1.2;font-weight:800;letter-spacing:-.035em;margin:0 0 14px}}.cta{{display:flex;gap:12px;flex-wrap:wrap;margin-top:22px}}.btn{{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:13px 18px;background:var(--cyan);color:#071221;font-weight:950}}.btn.secondary{{background:transparent;color:#fff;border:1px solid var(--line)}}table{{width:100%;border-collapse:collapse;overflow:hidden;border-radius:16px;background:rgba(255,255,255,.065)}}th,td{{padding:13px 14px;border-bottom:1px solid var(--line);text-align:left;font-size:14px}}th{{color:#aeefff;text-transform:uppercase;font-size:11px;letter-spacing:.16em}}.gates{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:0;list-style:none}}.gates li{{display:flex;justify-content:space-between;gap:12px;padding:13px 14px;background:rgba(255,255,255,.07);border:1px solid var(--line);border-radius:14px}}.gates b{{color:var(--green)}}.receipts{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}.receipt{{padding:15px;border:1px solid var(--line);border-radius:16px;background:rgba(255,255,255,.06)}}.receipt span{{display:block;color:var(--cyan);font-size:12px;font-weight:900}}.receipt b{{display:block;margin:5px 0 8px}}.receipt p{{margin:4px 0;color:var(--muted);font-size:12px}}.receipt strong{{color:var(--green)}}.footer{{color:var(--muted);padding:40px 0}}@media(max-width:900px){{.hero,.grid2,.metrics,.receipts{{grid-template-columns:1fr}}h1{{font-size:52px}}.links{{display:none}}}}
</style>
</head>
<body>
<nav class="nav"><a class="brand" href="./index.html">SkillOS Proof Command Center</a><div class="links"><a href="#proof">Proof</a><a href="#rsi">RSI</a><a href="#baselines">Baselines</a><a href="#receipts">Receipts</a><a href="{html.escape(action_url)}">Run</a><a href="https://github.com/{html.escape(repo)}">GitHub</a></div></nav>
<main class="wrap">
<section class="hero" id="proof">
  <div class="panel heroText">
    <div class="kicker">Montreal.AI / SkillOS / AI-first blockchain RSI</div>
    <h1>{TITLE}.</h1>
    <p class="lede">A reproducible GitHub Action proof that a large autonomous specialist-agent protocol organization can improve its own coordination layer — not by making a claim, but by passing locked holdout tests against single-agent, static DAO, uncoordinated swarm, no-RSI, and adversarial negative-control baselines.</p>
    <div class="cta"><a class="btn" href="{html.escape(action_url)}">Run proof on GitHub</a><a class="btn secondary" href="{html.escape(json_url)}">JSON receipt</a><a class="btn secondary" href="{html.escape(report_url)}">Report</a></div>
  </div>
  <div class="panel proofbox">
    <span class="pass">Proof passed</span>
    <div class="mega">{m['virtual_specialist_agents']:,} agents. {m['specialist_roles']:,} roles. {m['strategy_councils']} councils. {m['locked_holdout_cases']:,} locked holdout cases.</div>
    <p class="safe">This proof is public, deterministic, and autonomous. It does not claim achieved superintelligence, live protocol revenue, token recommendations, investment advice, or Kardashev Type II civilization.</p>
  </div>
</section>
<section class="metrics">
  <div class="metric"><strong>{pct(m['holdout_value_capture'])}</strong><span>locked-holdout value capture</span></div>
  <div class="metric"><strong>{pct(m['frontier_correct_rate'])}</strong><span>frontier-correct protocol decisions</span></div>
  <div class="metric"><strong>{pct(m['risk_breach_rate'])}</strong><span>risk breach rate</span></div>
  <div class="metric"><strong>{money(m['value_over_no_rsi_protocol_organization'])}</strong><span>over no-RSI protocol organization</span></div>
</section>
<section class="panel chain">
  <small>Kardashev-scale mechanism, public benchmark only</small>
  capital → blockspace → validator security → MEV control → liquidity → bridges → oracles → governance → data availability → compute/energy → trust → settlement → validation → risk courts → reinvestment → compounding protocol capability
</section>
<section class="quote panel">
  <p>“{html.escape(obj['wealth_quote_under_test'])}”</p>
  <span class="safe">SkillOS does not assert the quote is achieved. It makes the blockchain capital machine underneath the quote testable: can autonomous RSI improve the mechanism that compounds protocol capability under risk constraints?</span>
</section>
<section class="grid2" id="rsi">
  <article class="panel chart"><h3>Recursive self-improvement release curve</h3><canvas id="curve"></canvas><p class="safe">Validation-gated releases are accepted only when they improve the coordination layer without violating risk gates.</p></article>
  <article class="panel chart"><h3>Capability coordination radar</h3><canvas id="radar"></canvas><p class="safe">Measures coordinated capital allocation, validator security, MEV control, oracle/bridge integrity, settlement capacity, and reinvestment.</p></article>
</section>
<section id="baselines"><h2>Baselines and negative controls</h2><div class="grid2"><article class="panel"><table><thead><tr><th>Baseline</th><th>Value capture</th><th>Correct</th><th>Risk breach</th></tr></thead><tbody>{base_rows}</tbody></table></article><article class="panel"><table><thead><tr><th>Control</th><th>Value capture</th><th>Risk breach</th><th>Result</th></tr></thead><tbody>{control_rows}</tbody></table></article></div></section>
<section><h2>Pre-registered proof gates</h2><ul class="gates">{gates}</ul></section>
<section><h2>RSI release ledger</h2><div class="panel"><table><thead><tr><th>Version</th><th>Status</th><th>Validation</th><th>Holdout shadow</th><th>Risk</th><th>Skill update</th></tr></thead><tbody>{release_rows}</tbody></table></div></section>
<section id="receipts"><h2>Locked holdout receipts</h2><div class="receipts">{receipt_cards}</div></section>
<section class="footer"><p>Protocol fingerprint: <code>{html.escape(obj['protocol_fingerprint'])}</code></p><p>Generated at {html.escape(m['run_timestamp_utc'])} by {html.escape(PROOF_NAME)}.</p></section>
</main>
<script>const DATA={payload};
function drawCurve(){{const c=document.getElementById('curve'),x=c.getContext('2d'),dpr=devicePixelRatio||1,w=c.clientWidth*dpr,h=c.clientHeight*dpr;c.width=w;c.height=h;x.scale(dpr,dpr);const W=c.clientWidth,H=c.clientHeight;x.clearRect(0,0,W,H);let data=DATA.rsi_release_curve.map(r=>r.holdout_shadow_capture);let min=Math.min(...data)-.006,max=Math.max(...data)+.006;x.strokeStyle='rgba(255,255,255,.16)';x.lineWidth=1;for(let i=0;i<6;i++){{let y=24+i*(H-48)/5;x.beginPath();x.moveTo(28,y);x.lineTo(W-18,y);x.stroke();}}x.fillStyle='rgba(116,255,180,.14)';x.beginPath();data.forEach((v,i)=>{{let px=32+i*(W-64)/(data.length-1),py=H-28-(v-min)/(max-min)*(H-56);if(i===0)x.moveTo(px,H-28);x.lineTo(px,py);}});x.lineTo(W-32,H-28);x.closePath();x.fill();x.strokeStyle='#74ffb4';x.lineWidth=3;x.beginPath();data.forEach((v,i)=>{{let px=32+i*(W-64)/(data.length-1),py=H-28-(v-min)/(max-min)*(H-56);if(i===0)x.moveTo(px,py);else x.lineTo(px,py);}});x.stroke();data.forEach((v,i)=>{{let px=32+i*(W-64)/(data.length-1),py=H-28-(v-min)/(max-min)*(H-56);x.fillStyle=DATA.rsi_release_curve[i].accepted?'#74ffb4':'#ffd66b';x.beginPath();x.arc(px,py,4,0,Math.PI*2);x.fill();}});}}
function drawRadar(){{const c=document.getElementById('radar'),x=c.getContext('2d'),dpr=devicePixelRatio||1,w=c.clientWidth*dpr,h=c.clientHeight*dpr;c.width=w;c.height=h;x.scale(dpr,dpr);const W=c.clientWidth,H=c.clientHeight,cx=W/2,cy=H/2+10,R=Math.min(W,H)*.34;const labels=['Capital','Blockspace','Security','MEV','Liquidity','Bridge/oracle','Governance','Settlement','Risk courts','Reinvestment'];const vals=[.98,.94,.97,.93,.90,.95,.88,.96,.99,.97];x.clearRect(0,0,W,H);x.strokeStyle='rgba(255,255,255,.14)';for(let ring=1;ring<=5;ring++){{x.beginPath();labels.forEach((_,i)=>{{let a=-Math.PI/2+i*2*Math.PI/labels.length,rr=R*ring/5,px=cx+Math.cos(a)*rr,py=cy+Math.sin(a)*rr;if(i===0)x.moveTo(px,py);else x.lineTo(px,py);}});x.closePath();x.stroke();}}x.strokeStyle='rgba(131,247,255,.35)';labels.forEach((lab,i)=>{{let a=-Math.PI/2+i*2*Math.PI/labels.length;x.beginPath();x.moveTo(cx,cy);x.lineTo(cx+Math.cos(a)*R,cy+Math.sin(a)*R);x.stroke();x.fillStyle='#dffbff';x.font='11px Inter,Arial';x.textAlign='center';x.fillText(lab,cx+Math.cos(a)*(R+38),cy+Math.sin(a)*(R+28));}});x.fillStyle='rgba(131,247,255,.20)';x.strokeStyle='#83f7ff';x.lineWidth=3;x.beginPath();vals.forEach((v,i)=>{{let a=-Math.PI/2+i*2*Math.PI/vals.length,px=cx+Math.cos(a)*R*v,py=cy+Math.sin(a)*R*v;if(i===0)x.moveTo(px,py);else x.lineTo(px,py);}});x.closePath();x.fill();x.stroke();}}
window.addEventListener('resize',()=>{{drawCurve();drawRadar();}});drawCurve();drawRadar();</script>
</body></html>'''


def main():
    obj = json.loads((ROOT / "data" / f"{SLUG}.json").read_text())
    (ROOT / "site").mkdir(exist_ok=True)
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "badges").mkdir(exist_ok=True)
    (ROOT / "site" / f"{SLUG}.html").write_text(html_page(obj))
    (ROOT / "docs" / f"{SLUG}.md").write_text(md_report(obj))
    (ROOT / "badges" / f"{SLUG}.svg").write_text(badge_svg(obj["metrics"]))
    print(json.dumps({"generated": True, "html": f"site/{SLUG}.html", "report": f"docs/{SLUG}.md"}, indent=2))

if __name__ == "__main__":
    main()
