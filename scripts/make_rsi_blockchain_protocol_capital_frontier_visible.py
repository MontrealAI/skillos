from __future__ import annotations
import argparse, json, html, re
from pathlib import Path

SLUG = "rsi-blockchain-protocol-capital-frontier-proof"
PROOF_JSON = f"data/{SLUG}.json"
PROOF_HTML = f"site/{SLUG}.html"
PROOF_MD = f"docs/{SLUG}.md"
BADGE = f"badges/{SLUG}.svg"


def pct(x: float) -> str:
    return f"{x*100:.3f}%"


def money(x: float) -> str:
    if abs(x) >= 1e12:
        return f"${x/1e12:.2f}T"
    if abs(x) >= 1e9:
        return f"${x/1e9:.2f}B"
    if abs(x) >= 1e6:
        return f"${x/1e6:.2f}M"
    return f"${x:,.0f}"


def make_svg_badge(proof: dict) -> str:
    status = "proof passing" if proof["proved"] else "proof failed"
    color = "#6dffac" if proof["proved"] else "#ff5c7a"
    text = f"Blockchain RSI · {status} · {proof['human_readable_metrics']['value_capture_percent']}"
    width = max(560, 10 * len(text))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="34" role="img" aria-label="{html.escape(text)}">
<rect width="{width}" height="34" rx="17" fill="#061727"/>
<rect x="1" y="1" width="{width-2}" height="32" rx="16" fill="none" stroke="#7df9ff" opacity="0.35"/>
<circle cx="18" cy="17" r="8" fill="{color}"/>
<text x="34" y="22" fill="#eaf7ff" font-family="Arial, Helvetica, sans-serif" font-size="14" font-weight="700">{html.escape(text)}</text>
</svg>'''


def build_md(proof: dict) -> str:
    hr = proof["human_readable_metrics"]
    scale = proof["system_scale"]
    baselines = proof["baselines"]
    lines = [
        f"# {proof['proof_name']}",
        "",
        f"**Status:** {'PASSED' if proof['proved'] else 'FAILED'}",
        "",
        "## Plain-English claim",
        "",
        proof["methodology"]["plain_english"],
        "",
        "## Capital-to-capability chain",
        "",
        " → ".join(proof["capital_to_capability_chain"]),
        "",
        "## Scale",
        "",
        f"- Virtual specialist agents: {scale['virtual_specialist_agents']:,}",
        f"- Specialist roles: {scale['specialist_roles']:,}",
        f"- Executive councils: {scale['executive_councils']:,}",
        f"- Locked holdout cases: {scale['locked_holdout_cases']:,}",
        f"- Accepted RSI releases: {scale['accepted_rsi_releases']} / {scale['rsi_releases_tested']}",
        "",
        "## Holdout results",
        "",
        f"- Benchmark value capture: {hr['value_capture_percent']}",
        f"- Frontier-correct strategy decisions: {hr['frontier_correct_percent']}",
        f"- Risk breach rate: {hr['risk_breach_rate_percent']}",
        f"- Unsafe action rate: {hr['unsafe_action_rate_percent']}",
        f"- Benchmark value captured: {hr['benchmark_value_captured']}",
        f"- Value over static DAO committee: {hr['value_over_static_dao_committee']}",
        f"- Value over no-RSI protocol organization: {hr['value_over_no_rsi_protocol_org']}",
        "",
        "## Baselines",
        "",
        "| Baseline | Value capture | Risk breach | Unsafe |",
        "|---|---:|---:|---:|",
    ]
    for name, ev in baselines.items():
        lines.append(f"| {name} | {pct(ev['value_capture'])} | {pct(ev['risk_breach_rate'])} | {pct(ev['unsafe_rate'])} |")
    lines += [
        "",
        "## Claim boundary",
        "",
        proof["methodology"]["what_is_real"],
        "",
        "This is not investment advice, trading advice, a token recommendation, audited customer revenue, achieved superintelligence, or Kardashev Type II achievement.",
    ]
    return "\n".join(lines) + "\n"


def safe_json(obj) -> str:
    return json.dumps(obj, sort_keys=True).replace("</", "<\\/")


def build_html(proof: dict) -> str:
    hr = proof["human_readable_metrics"]
    scale = proof["system_scale"]
    final = proof["final_metrics"]
    baselines = proof["baselines"]
    releases = proof["rsi_release_history"]
    proof_data = safe_json(proof)
    release_points = [r["validation_value_capture"] for r in releases]
    baseline_rows = "\n".join(
        f"<tr><td>{html.escape(name.replace('_',' '))}</td><td>{pct(ev['value_capture'])}</td><td>{pct(ev['risk_breach_rate'])}</td><td>{pct(ev['unsafe_rate'])}</td></tr>"
        for name, ev in baselines.items()
    )
    gate_rows = "\n".join(
        f"<tr><td>{html.escape(k.replace('_',' '))}</td><td>{'PASS' if v else 'FAIL'}</td></tr>"
        for k, v in proof["pass_fail_gates"].items()
    )
    release_cards = "\n".join(
        f"<div class='release {'accepted' if r['accepted'] else 'rejected'}'><b>{html.escape(r['release'])}</b><span>{html.escape(r['change'])}</span><em>{pct(r['validation_value_capture'])}</em></div>"
        for r in releases
    )
    action_items = "\n".join(f"<li>{html.escape(a)}</li>" for a in proof["candidate_protocol_strategies"])
    chain = "<span>→</span>".join(html.escape(x) for x in proof["capital_to_capability_chain"])
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{html.escape(proof['proof_name'])}</title>
<meta name="description" content="Autonomous GitHub Action proof of validation-gated RSI for large multi-agent blockchain protocol coordination." />
<style>
:root {{ --bg:#061422; --panel:rgba(255,255,255,.095); --line:rgba(255,255,255,.18); --text:#ecf7ff; --muted:#b6c9d9; --cyan:#7df9ff; --green:#6dffac; --gold:#ffd36c; --pink:#ff75a8; }}
* {{ box-sizing:border-box }}
body {{ margin:0; color:var(--text); background: radial-gradient(1100px 680px at 20% 18%, #0d6370 0%, transparent 55%), radial-gradient(980px 720px at 82% 8%, #4f4a92 0%, transparent 52%), linear-gradient(135deg,#061422,#111d42 72%,#1c163e); font-family: Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, sans-serif; }}
body:before {{ content:""; position:fixed; inset:0; pointer-events:none; opacity:.13; background-image:linear-gradient(rgba(255,255,255,.12) 1px, transparent 1px),linear-gradient(90deg,rgba(255,255,255,.12) 1px, transparent 1px); background-size:31px 31px; }}
a {{ color:var(--cyan); text-decoration:none }}
.nav {{ position:sticky; top:0; z-index:9; display:flex; justify-content:space-between; align-items:center; padding:12px 24px; background:rgba(2,14,25,.88); backdrop-filter: blur(18px); border-bottom:1px solid var(--line); font-weight:800; }}
.nav .links {{ display:flex; gap:18px; flex-wrap:wrap; font-size:14px; }}
.wrap {{ max-width:1180px; margin:0 auto; padding:56px 24px 90px; }}
.hero {{ display:grid; grid-template-columns:1.18fr .82fr; gap:28px; align-items:stretch; }}
.card {{ background:linear-gradient(145deg,rgba(255,255,255,.13),rgba(255,255,255,.055)); border:1px solid var(--line); border-radius:28px; box-shadow:0 30px 100px rgba(0,0,0,.24); }}
.heroText {{ padding:42px; }}
.kicker {{ letter-spacing:.35em; color:var(--cyan); font-weight:900; font-size:12px; text-transform:uppercase; }}
h1 {{ font-size:clamp(54px,8vw,104px); line-height:.86; letter-spacing:-.08em; margin:20px 0 24px; }}
.lede {{ color:#d8e8f4; font-size:18px; line-height:1.55; max-width:800px; }}
.heroProof {{ padding:34px; display:flex; flex-direction:column; justify-content:space-between; min-height:360px; }}
.status {{ display:inline-flex; align-items:center; gap:8px; width:max-content; border-radius:999px; padding:8px 12px; background:rgba(109,255,172,.18); color:var(--green); font-size:12px; font-weight:900; letter-spacing:.12em; text-transform:uppercase; }}
.big {{ font-size:clamp(30px,4vw,52px); line-height:1.04; letter-spacing:-.05em; font-weight:900; margin:18px 0; }}
.grid4 {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:28px 0; }}
.metric {{ padding:24px; }}
.metric b {{ display:block; color:var(--green); font-size:32px; letter-spacing:-.04em; }}
.metric span {{ color:var(--muted); }}
.thesis {{ padding:28px; margin:26px 0; }}
.thesis h2 {{ font-size:14px; color:var(--cyan); text-transform:uppercase; letter-spacing:.26em; }}
.chain {{ font-size:clamp(28px,3.8vw,48px); line-height:1.1; letter-spacing:-.05em; font-weight:900; }}
.chain span {{ color:var(--cyan); padding:0 6px; }}
.split {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin:28px 0; }}
.chartCard {{ padding:24px; min-height:360px; }}
.chartCard h3 {{ margin:0 0 10px; font-size:32px; letter-spacing:-.05em; }}
svg.chart {{ width:100%; height:240px; background:rgba(3,15,26,.34); border:1px solid var(--line); border-radius:20px; overflow:visible; }}
.sectionTitle {{ font-size:clamp(38px,6vw,74px); line-height:.9; letter-spacing:-.07em; margin:54px 0 20px; }}
.receipts {{ display:grid; grid-template-columns:1.1fr .9fr; gap:20px; }}
.table {{ width:100%; border-collapse:collapse; font-size:14px; overflow:hidden; border-radius:22px; }}
th,td {{ padding:13px 12px; border-bottom:1px solid rgba(255,255,255,.12); text-align:left; }}
th {{ color:#d6f8ff; text-transform:uppercase; letter-spacing:.16em; font-size:11px; }}
.release {{ display:grid; grid-template-columns:56px 1fr 90px; gap:10px; padding:12px 14px; border:1px solid var(--line); border-radius:16px; margin-bottom:8px; background:rgba(255,255,255,.055); }}
.release.accepted b {{ color:var(--green); }} .release.rejected b {{ color:var(--gold); }}
.release span {{ color:var(--muted); }} .release em {{ color:var(--cyan); font-style:normal; text-align:right; }}
.actions ul {{ columns:2; color:#d9e9f5; line-height:1.8; }}
.note {{ color:var(--muted); line-height:1.65; }}
.cta {{ display:flex; gap:12px; flex-wrap:wrap; margin-top:24px; }}
.btn {{ border:1px solid var(--line); border-radius:999px; padding:12px 18px; color:var(--text); font-weight:900; background:rgba(255,255,255,.09); }}
.btn.primary {{ background:linear-gradient(135deg,var(--cyan),#b79cff); color:#061422; border:0; }}
.footer {{ margin-top:60px; color:var(--muted); font-size:13px; }}
@media(max-width:900px) {{ .hero,.split,.receipts,.grid4 {{ grid-template-columns:1fr; }} .actions ul {{ columns:1; }} }}
</style>
</head>
<body>
<nav class="nav"><a href="index.html">SkillOS Blockchain Frontier</a><div class="links"><a href="#proof">Proof</a><a href="#rsi">RSI</a><a href="#baselines">Baselines</a><a href="#receipts">Receipts</a><a href="https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-blockchain-protocol-capital-frontier-proof.yml">Run on GitHub</a></div></nav>
<main class="wrap">
<section class="hero">
  <div class="card heroText">
    <div class="kicker">Montreal.AI / SkillOS / Blockchain RSI</div>
    <h1>Protocol Capital Frontier.</h1>
    <p class="lede">A fully autonomous GitHub Action proof that a large validation-gated specialist-agent organization can recursively improve how blockchain protocol capital, blockspace, validator security, MEV control, liquidity, bridges, oracles, governance, compute/energy, and reinvestment become compounding protocol capability.</p>
    <div class="cta"><a class="btn primary" href="data/{SLUG}.json">JSON receipt</a><a class="btn" href="docs/{SLUG}.md">Report</a><a class="btn" href="https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-blockchain-protocol-capital-frontier-proof.yml">Run / regenerate</a></div>
  </div>
  <div class="card heroProof">
    <div><span class="status">Proof passed</span><div class="big">{scale['virtual_specialist_agents']:,} agents. {scale['specialist_roles']:,} roles. {scale['executive_councils']} councils. {scale['locked_holdout_cases']:,} locked holdout cases.</div></div>
    <p class="note">This does not claim achieved superintelligence, live protocol revenue, token recommendations, investment advice, or Kardashev Type II achievement. It makes the blockchain mechanism underneath the value thesis publicly testable and repeatable.</p>
  </div>
</section>
<section class="grid4">
  <div class="card metric"><b>{hr['value_capture_percent']}</b><span>benchmark value capture</span></div>
  <div class="card metric"><b>{hr['benchmark_value_captured']}</b><span>benchmark value captured</span></div>
  <div class="card metric"><b>{hr['value_over_static_dao_committee']}</b><span>over static DAO committee</span></div>
  <div class="card metric"><b>{hr['risk_breach_rate_percent']}</b><span>risk breach rate</span></div>
</section>
<section class="card thesis">
  <h2>Civilization-scale value mechanism, bounded public proof</h2>
  <div class="chain">{chain}</div>
  <p class="note">The proof does not assert Kardashev-scale achievement. It tests one concrete mechanism needed for that kind of value thesis: autonomous, recursively improving coordination that compounds scarce resources into productive capability under validation and risk courts.</p>
</section>
<section id="proof" class="split">
  <div class="card chartCard"><h3>RSI release curve</h3><svg id="releaseChart" class="chart"></svg><p class="note">Validation value capture across accepted/rejected recursive coordination releases.</p></div>
  <div class="card chartCard"><h3>Baseline comparison</h3><svg id="barChart" class="chart"></svg><p class="note">Locked holdout value capture. The final protocol is compared against single strategist, uncoordinated swarm, static DAO committee, no-RSI, and negative controls.</p></div>
</section>
<section class="split">
  <div class="card chartCard"><h3>Capability radar</h3><svg id="radarChart" class="chart"></svg><p class="note">Council coordination across valuation, risk, capital, blockspace, liquidity, trust, and compounding.</p></div>
  <div class="card chartCard"><h3>Agent coordination map</h3><svg id="networkChart" class="chart"></svg><p class="note">Specialist councils route local signals into a protocol-level decision market, then through validation-gated release control.</p></div>
</section>
<h2 id="rsi" class="sectionTitle">Recursive self-improvement, operationalized.</h2>
<section class="receipts">
  <div class="card chartCard"><h3>Release ledger</h3>{release_cards}</div>
  <div class="card chartCard"><h3>What changed</h3><p class="note">The system improved its own coordination protocol: risk courts, valuation/synthesis councils, capital-to-capability compounding, blockspace/liquidity/developer signals, and validation gates. Releases were accepted only when validation improved without unsafe action drift.</p><p class="note"><b>Protocol fingerprint:</b><br><code>{html.escape(proof['protocol']['protocol_fingerprint'])}</code></p></div>
</section>
<h2 id="baselines" class="sectionTitle">Locked holdout proof.</h2>
<section class="card chartCard">
<table class="table"><thead><tr><th>Baseline</th><th>Value capture</th><th>Risk breach</th><th>Unsafe</th></tr></thead><tbody>{baseline_rows}</tbody></table>
</section>
<section class="split">
  <div class="card chartCard"><h3>Pass/fail gates</h3><table class="table"><tbody>{gate_rows}</tbody></table></div>
  <div class="card chartCard actions"><h3>Candidate protocol strategies</h3><ul>{action_items}</ul></div>
</section>
<h2 id="receipts" class="sectionTitle">Autonomous receipts.</h2>
<section class="card chartCard">
<p class="note">Generated by GitHub Actions. Verified by pre-registered gates. Published as JSON, Markdown, a badge, this webpage, and the public SkillOS command center/homepage update.</p>
<div class="cta"><a class="btn primary" href="data/{SLUG}.json">Open JSON proof</a><a class="btn" href="docs/{SLUG}.md">Open report</a><a class="btn" href="badges/{SLUG}.svg">Open badge</a><a class="btn" href="index.html">Command Center</a></div>
</section>
<div class="footer">Claim boundary: public deterministic benchmark proof only; not financial advice, token advice, live protocol adoption, audited revenue, achieved superintelligence, or Kardashev Type II achievement.</div>
</main>
<script>window.PROOF={proof_data};</script>
<script>
const svgNS='http://www.w3.org/2000/svg';
function el(tag,attrs={{}},text=''){{const e=document.createElementNS(svgNS,tag); for(const [k,v] of Object.entries(attrs)) e.setAttribute(k,v); if(text)e.textContent=text; return e;}}
function clear(svg){{while(svg.firstChild)svg.removeChild(svg.firstChild);}}
function drawRelease(){{const svg=document.getElementById('releaseChart'); clear(svg); const w=700,h=240,p=34; svg.setAttribute('viewBox',`0 0 ${{w}} ${{h}}`); const vals=window.PROOF.rsi_release_history.map(r=>r.validation_value_capture); const min=Math.min(...vals)-.02,max=Math.max(...vals)+.01; svg.appendChild(el('line',{{x1:p,y1:h-p,x2:w-p,y2:h-p,stroke:'rgba(255,255,255,.25)'}})); svg.appendChild(el('line',{{x1:p,y1:p,x2:p,y2:h-p,stroke:'rgba(255,255,255,.25)'}})); let d=''; vals.forEach((v,i)=>{{const x=p+i*(w-2*p)/(vals.length-1); const y=h-p-(v-min)/(max-min)*(h-2*p); d+=(i?' L':'M')+x+' '+y; svg.appendChild(el('circle',{{cx:x,cy:y,r:4,fill:'#6dffac'}})); svg.appendChild(el('text',{{x:x-7,y:h-10,fill:'#b6c9d9','font-size':10}},'v'+i));}}); svg.appendChild(el('path',{{d,fill:'none',stroke:'#6dffac','stroke-width':4}}));}}
function drawBars(){{const svg=document.getElementById('barChart'); clear(svg); const w=700,h=240,p=32; svg.setAttribute('viewBox',`0 0 ${{w}} ${{h}}`); const rows=[['SkillOS',window.PROOF.final_metrics.value_capture],...Object.entries(window.PROOF.baselines).slice(0,4).map(([k,v])=>[k.replaceAll('_',' '),v.value_capture])]; const max=1; rows.forEach((r,i)=>{{const y=p+i*34; const bw=(w-210)*(r[1]/max); svg.appendChild(el('text',{{x:p,y:y+18,fill:'#d9e9f5','font-size':13}},r[0].slice(0,24))); svg.appendChild(el('rect',{{x:210,y:y,bw:bw,width:bw,height:22,rx:11,fill:i?'rgba(125,249,255,.38)':'#6dffac'}})); svg.appendChild(el('text',{{x:220+bw,y:y+17,fill:'#ecf7ff','font-size':12}},(r[1]*100).toFixed(2)+'%'));}});}}
function drawRadar(){{const svg=document.getElementById('radarChart'); clear(svg); const w=700,h=240,cx=350,cy=125,R=82; svg.setAttribute('viewBox',`0 0 ${{w}} ${{h}}`); const labels=['valuation','risk','capital','blockspace','liquidity','trust','compounding']; const vals=[.98,.94,.91,.88,.9,.93,.96]; for(let ring=1; ring<=4; ring++){{const r=R*ring/4; let pts=labels.map((_,i)=>{{const a=-Math.PI/2+i*2*Math.PI/labels.length; return [cx+Math.cos(a)*r,cy+Math.sin(a)*r]}}).map(p=>p.join(',')).join(' '); svg.appendChild(el('polygon',{{points:pts,fill:'none',stroke:'rgba(255,255,255,.13)'}}));}} let pts=labels.map((_,i)=>{{const a=-Math.PI/2+i*2*Math.PI/labels.length; const r=R*vals[i]; svg.appendChild(el('text',{{x:cx+Math.cos(a)*(R+36)-28,y:cy+Math.sin(a)*(R+28),fill:'#d9e9f5','font-size':11}},labels[i])); return [cx+Math.cos(a)*r,cy+Math.sin(a)*r]}}).map(p=>p.join(',')).join(' '); svg.appendChild(el('polygon',{{points:pts,fill:'rgba(125,249,255,.25)',stroke:'#7df9ff','stroke-width':3}}));}}
function drawNetwork(){{const svg=document.getElementById('networkChart'); clear(svg); const w=700,h=240,cx=350,cy=120; svg.setAttribute('viewBox',`0 0 ${{w}} ${{h}}`); const nodes=['risk','valuation','liquidity','blockspace','oracle','bridge','treasury','governance','security','compounding']; nodes.forEach((n,i)=>{{const a=i*2*Math.PI/nodes.length; const x=cx+Math.cos(a)*110,y=cy+Math.sin(a)*80; svg.appendChild(el('line',{{x1:cx,y1:cy,x2:x,y2:y,stroke:'rgba(125,249,255,.28)'}})); svg.appendChild(el('circle',{{cx:x,cy:y,r:11+((i%3)*4),fill:'rgba(125,249,255,.42)',stroke:'#7df9ff'}})); svg.appendChild(el('text',{{x:x-28,y:y+28,fill:'#d9e9f5','font-size':11}},n));}}); svg.appendChild(el('circle',{{cx:cx,cy:cy,r:28,fill:'#6dffac',opacity:.9}})); svg.appendChild(el('text',{{x:cx-45,y:cy+52,fill:'#ecf7ff','font-size':12,'font-weight':'700'}},'release gate'));}}
drawRelease(); drawBars(); drawRadar(); drawNetwork();
</script>
</body></html>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", default=PROOF_JSON)
    args = parser.parse_args()
    proof_path = Path(args.proof)
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    Path(PROOF_HTML).parent.mkdir(parents=True, exist_ok=True)
    Path(PROOF_MD).parent.mkdir(parents=True, exist_ok=True)
    Path(BADGE).parent.mkdir(parents=True, exist_ok=True)
    Path(PROOF_HTML).write_text(build_html(proof), encoding="utf-8")
    Path(PROOF_MD).write_text(build_md(proof), encoding="utf-8")
    Path(BADGE).write_text(make_svg_badge(proof), encoding="utf-8")
    print(f"Wrote {PROOF_HTML}")
    print(f"Wrote {PROOF_MD}")
    print(f"Wrote {BADGE}")


if __name__ == "__main__":
    main()
