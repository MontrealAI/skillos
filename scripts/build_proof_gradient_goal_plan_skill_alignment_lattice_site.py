#!/usr/bin/env python3
import html, json, os, re, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

PROOF_ID = "proof-gradient-goal-plan-skill-alignment-lattice"
RECEIPT_PATH = Path("data") / f"{PROOF_ID}.json"
SCHEMA = "skillos.public_command_center.proof_gradient_goal_plan_skill_alignment_lattice.v1"
MARKER = "SKILLOS_PROOF_GRADIENT_GOAL_PLAN_SKILL_ALIGNMENT_LATTICE_V1"


def safe_text(x, default=""):
    if x is None:
        return default
    if isinstance(x, (str, int, float, bool)):
        return str(x)
    if isinstance(x, dict):
        for k in ("title", "name", "id", "label", "value"):
            if k in x:
                return safe_text(x[k], default)
        return json.dumps(x, sort_keys=True)[:220]
    if isinstance(x, list):
        return ", ".join(safe_text(i) for i in x[:5])
    return str(x)

def pct(x, digits=1):
    try:
        return f"{float(x)*100:.{digits}f}%"
    except Exception:
        return "—"

def esc(x):
    return html.escape(safe_text(x))

def load_receipt():
    if not RECEIPT_PATH.exists():
        raise SystemExit(f"Missing receipt: {RECEIPT_PATH}. Run scripts/run_proof_gradient_goal_plan_skill_alignment_lattice.py first.")
    return json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def css():
    return r'''
:root{--bg:#070b17;--panel:rgba(255,255,255,.085);--panel2:rgba(255,255,255,.13);--line:rgba(255,255,255,.17);--text:#f4f9ff;--muted:#b9c7db;--cyan:#72f7ff;--green:#6cffad;--gold:#ffd76d;--violet:#a696ff;--red:#ff7c8a;--shadow:0 30px 100px rgba(0,0,0,.32)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(circle at 15% 10%,rgba(0,229,255,.18),transparent 28%),radial-gradient(circle at 85% 20%,rgba(166,150,255,.26),transparent 30%),linear-gradient(135deg,#081523,#161943 58%,#0b1021);color:var(--text);font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;line-height:1.55}body:before{content:"";position:fixed;inset:0;pointer-events:none;background-image:linear-gradient(rgba(255,255,255,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.055) 1px,transparent 1px);background-size:36px 36px;mask-image:linear-gradient(to bottom,black,transparent 90%)}a{color:var(--cyan);text-decoration:none}a:hover{text-decoration:underline}.nav{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;padding:16px 22px;background:rgba(3,10,20,.84);backdrop-filter:blur(18px);border-bottom:1px solid var(--line)}.brand{font-weight:900;letter-spacing:-.03em;color:var(--cyan)}.navlinks{display:flex;gap:16px;flex-wrap:wrap}.navlinks a{color:#dce8fb;font-weight:800;font-size:14px}.wrap{max-width:1220px;margin:0 auto;padding:70px 24px}.hero{display:grid;grid-template-columns:1.16fr .84fr;gap:34px;align-items:center}.eyebrow{color:var(--cyan);font-weight:950;letter-spacing:.22em;text-transform:uppercase;font-size:12px}.h1{font-size:clamp(56px,8vw,118px);line-height:.88;letter-spacing:-.09em;margin:12px 0 18px}.lead{font-size:clamp(18px,2.2vw,26px);color:#d9e9ff;max-width:800px}.panel{background:linear-gradient(140deg,rgba(255,255,255,.14),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:30px;padding:30px;box-shadow:var(--shadow)}.heroCard{min-height:330px;position:relative;overflow:hidden}.heroCard:before{content:"";position:absolute;inset:-20%;background:radial-gradient(circle at 50% 45%,rgba(114,247,255,.22),transparent 18%),radial-gradient(circle at 75% 70%,rgba(255,215,109,.20),transparent 14%)}.heroCard>*{position:relative}.bigMetric{font-size:56px;font-weight:950;color:var(--green);letter-spacing:-.06em}.btns{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}.btn{display:inline-flex;align-items:center;gap:9px;padding:14px 18px;border-radius:999px;border:1px solid var(--line);font-weight:950;color:var(--text);background:rgba(255,255,255,.08)}.btn.primary{background:var(--gold);color:#141007}.btn.cyan{background:var(--cyan);color:#061019}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.grid2{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}.metric{padding:22px;border-radius:22px;background:var(--panel);border:1px solid var(--line)}.metric b{display:block;font-size:34px;color:var(--green);line-height:1}.metric span{color:var(--muted)}h2{font-size:clamp(34px,5vw,64px);line-height:.95;letter-spacing:-.06em;margin:80px 0 22px}h3{font-size:24px;letter-spacing:-.03em}.kicker{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:var(--cyan);font-weight:950}.quote{font-size:clamp(28px,4.2vw,54px);line-height:1.02;letter-spacing:-.055em}.card{border:1px solid var(--line);background:var(--panel);border-radius:24px;padding:24px;min-height:180px}.card strong{color:var(--green)}.tag{display:inline-block;padding:7px 10px;border-radius:99px;background:rgba(108,255,173,.16);color:var(--green);font-weight:950;font-size:12px;letter-spacing:.08em;text-transform:uppercase}.tag.gold{background:rgba(255,215,109,.16);color:var(--gold)}.tag.cyan{background:rgba(114,247,255,.16);color:var(--cyan)}.tag.violet{background:rgba(166,150,255,.18);color:#d7d0ff}.muted{color:var(--muted)}.axis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.axis .card{min-height:220px}.svgbox{background:rgba(0,0,0,.18);border:1px solid var(--line);border-radius:22px;padding:14px;overflow:hidden}.table{width:100%;border-collapse:collapse;overflow:hidden;border-radius:18px}.table th,.table td{padding:13px 14px;text-align:left;border-bottom:1px solid var(--line)}.table th{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:#b8d5ff}.table tr:last-child td{border-bottom:0}.footer{padding:42px 24px;color:var(--muted);border-top:1px solid var(--line);text-align:center}.small{font-size:13px}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}.timeline{display:grid;grid-template-columns:repeat(7,1fr);gap:10px}.dot{height:10px;border-radius:99px;background:linear-gradient(90deg,var(--cyan),var(--green))}@media(max-width:920px){.hero,.grid2,.grid3,.grid,.axis{grid-template-columns:1fr}.h1{font-size:58px}.wrap{padding:46px 18px}.nav{align-items:flex-start;gap:12px;flex-direction:column}.navlinks{gap:10px}}
'''

def layout(title, body, active=""):
    nav = [("Home","index.html"),("Proof","proof-gradient-goal-plan-skill-alignment-lattice.html"),("Goals","goals.html"),("Plans","plans.html"),("Skills","skills.html"),("Receipts","receipts.html"),("Run","run.html"),("GitHub","https://github.com/MontrealAI/skillos")]
    links = "".join(f'<a href="{href}">{name}</a>' for name, href in nav)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta name="theme-color" content="#070b17"><title>{esc(title)}</title><style>{css()}</style></head><body><nav class="nav"><a class="brand" href="index.html">Public SkillOS Command Center</a><div class="navlinks">{links}</div></nav>{body}<footer class="footer"><b>Proof Gradient · Goal-Plan-Skill Alignment Lattice</b><br><span>Generated from repository evidence. The root is the Command Center; proofs are rooms.</span></footer></body></html>'''

def line_chart(curve):
    pts=[]; vals=[c["holdout_success_rate"] for c in curve]
    minv,maxv=min(vals),max(vals); w,h=720,260; pad=34
    for i,v in enumerate(vals):
        x=pad+i*(w-2*pad)/(len(vals)-1); y=h-pad-(v-minv)/(maxv-minv+1e-9)*(h-2*pad)
        pts.append((x,y))
    poly=" ".join(f"{x:.1f},{y:.1f}" for x,y in pts)
    circles="".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#6cffad"/>' for x,y in pts)
    labels="".join(f'<text x="{x:.1f}" y="244" text-anchor="middle" fill="#b9c7db" font-size="10">r{curve[i]["release"]}</text>' for i,(x,y) in enumerate(pts) if i%2==0)
    return f'''<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="Proof Gradient release curve"><defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6cffad" stop-opacity=".42"/><stop offset="1" stop-color="#6cffad" stop-opacity="0"/></linearGradient></defs><path d="M {pts[0][0]:.1f},{h-pad} L {poly} L {pts[-1][0]:.1f},{h-pad} Z" fill="url(#area)"/><polyline points="{poly}" fill="none" stroke="#6cffad" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>{circles}{labels}<line x1="{pad}" y1="{h-pad}" x2="{w-pad}" y2="{h-pad}" stroke="rgba(255,255,255,.18)"/><line x1="{pad}" y1="{pad}" x2="{pad}" y2="{h-pad}" stroke="rgba(255,255,255,.18)"/></svg>'''

def bar_chart(comparisons):
    keys=list(comparisons.keys()); w,h=760,300; pad=48; barw=(w-2*pad)/len(keys)*0.58
    bars=[]; labels=[]
    for i,k in enumerate(keys):
        row=comparisons[k]; v=row["holdout_success_rate"]; x=pad+i*(w-2*pad)/len(keys)+22; bh=v*(h-2*pad); y=h-pad-bh
        color="#6cffad" if k=="proof_gradient_lattice" else "#72f7ff" if "static" in k else "#a696ff"
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{barw:.1f}" height="{bh:.1f}" rx="10" fill="{color}" opacity=".82"/><text x="{x+barw/2:.1f}" y="{y-8:.1f}" text-anchor="middle" fill="#eaf7ff" font-size="13" font-weight="800">{v*100:.1f}%</text>')
        short={"single_agent":"single","skill_only":"skill","goal_plan_static":"static","unverified_gradient":"unverified","proof_gradient_lattice":"PG lattice"}[k]
        labels.append(f'<text x="{x+barw/2:.1f}" y="{h-22}" text-anchor="middle" fill="#b9c7db" font-size="12">{short}</text>')
    return f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="Protocol comparison"><line x1="{pad}" y1="{h-pad}" x2="{w-pad}" y2="{h-pad}" stroke="rgba(255,255,255,.18)"/>{"".join(bars)}{"".join(labels)}</svg>'

def cards(items, kind):
    out=[]
    for it in items:
        if kind=="goal":
            out.append(f'''<article class="card"><span class="tag cyan">{esc(it.get('os'))} · Direction</span><h3>{esc(it.get('name'))}</h3><p>{esc(it.get('direction'))}</p><p class="muted"><b>Measure:</b> {esc(it.get('measure'))}<br><b>Weight:</b> {pct(it.get('weight'),0)} · <b>Threshold:</b> {pct(it.get('threshold'),0)}</p></article>''')
        elif kind=="plan":
            steps=" → ".join(esc(s) for s in it.get("steps",[]))
            out.append(f'''<article class="card"><span class="tag gold">{esc(it.get('os'))} · Strategy</span><h3>{esc(it.get('name'))}</h3><p>{esc(it.get('strategy'))}</p><p class="muted"><b>Steps:</b> {steps}<br><b>Risk budget:</b> {pct(it.get('risk_budget'),1)}</p></article>''')
        else:
            out.append(f'''<article class="card"><span class="tag violet">{esc(it.get('os'))} · {esc(it.get('layer'))}</span><h3>{esc(it.get('name'))}</h3><p>{esc(it.get('purpose'))}</p><p class="muted"><b>Input:</b> {esc(it.get('input'))}<br><b>Output:</b> {esc(it.get('output'))}<br><b>Verifier:</b> {esc(it.get('verifier'))}</p></article>''')
    return "".join(out)

def metric_cards(receipt):
    o=receipt["observed"]
    data=[("Agents", f"{o['agents']:,}"),("Specialist roles", str(o['specialist_roles'])),("Accepted skills", str(o['accepted_skills'])),("Holdout uplift", pct(o['success_uplift_over_static'],1)),("Value uplift", pct(o['value_uplift_over_static'],1)),("Risk breach", pct(o['risk_breach_rate'],2)),("Goal alignment", pct(o['goal_alignment'],1)),("Negative-control rejection", pct(o['negative_control_rejection_rate'],1))]
    return "".join(f'<div class="metric"><b>{esc(v)}</b><span>{esc(k)}</span></div>' for k,v in data)

def build_index(out, receipt):
    body=f'''<main class="wrap"><section class="hero"><div><div class="eyebrow">Montreal.AI / SkillOS / Proof Gradient</div><h1 class="h1">Public SkillOS Command Center</h1><p class="lead">The canonical root for SkillOS proofs. Generated from repository evidence, refreshed by GitHub Actions, and organized so viewers can inspect proofs, agents, goals, plans, skills, receipts, and rerun paths.</p><div class="btns"><a class="btn primary" href="proof-gradient-goal-plan-skill-alignment-lattice.html">View Proof Gradient proof</a><a class="btn cyan" href="skills.html">See skills, plans, and goals</a><a class="btn" href="run.html">Run on GitHub</a></div></div><aside class="panel heroCard"><span class="tag">root authority</span><h2 style="margin:16px 0 10px">The root is the lobby.</h2><p class="lead">Proofs are rooms. A proof page must never replace the Public SkillOS Command Center.</p><p class="muted mono">{MARKER}</p></aside></section><section><div class="panel"><div class="kicker">Incremental flagship proof</div><p class="quote">GoalOS gives Direction. PlanOS gives Strategy. SkillOS gives Capability. Proof Gradient gives Evolution.</p><p class="lead">This second Proof Gradient proof tests whether the network improves more reliably when evolution is constrained by goals, plans, skills, proofs, and risk gates.</p></div></section><section class="grid">{metric_cards(receipt)}</section><section class="grid2"><div class="panel"><h3>Recursive release curve</h3><div class="svgbox">{line_chart(receipt['release_curve'])}</div></div><div class="panel"><h3>Protocol comparison</h3><div class="svgbox">{bar_chart(receipt['comparisons'])}</div></div></section><section><h2>Featured proof room</h2><div class="grid2"><article class="card"><span class="tag">passed proof</span><h3>{esc(receipt['title'])}</h3><p>{esc(receipt['incremental_position'])}</p><a class="btn cyan" href="proof-gradient-goal-plan-skill-alignment-lattice.html">Open proof room</a></article><article class="card"><span class="tag gold">viewer path</span><h3>How to inspect it</h3><p>Start with the proof page, then inspect the goals, plans, skills, JSON receipt, Markdown report, badge, and GitHub workflow.</p><a class="btn" href="receipts.html">Inspect receipt</a></article></div></section></main>'''
    write(out/"index.html", layout("Public SkillOS Command Center", body))

def build_proof(out, receipt):
    o=receipt["observed"]
    rows="".join(f"<tr><td>{esc(r['label'])}</td><td>{pct(r['holdout_success_rate'],1)}</td><td>{pct(r['value_capture_rate'],1)}</td><td>{pct(r['risk_breach_rate'],2)}</td><td>{pct(r['goal_alignment'],1)}</td><td>{pct(r['plan_fidelity'],1)}</td><td>{pct(r['skill_validity'],1)}</td></tr>" for r in receipt["comparisons"].values())
    accepted=[c for c in receipt["candidate_decisions"] if c["decision"]=="accepted"][:12]
    cand_rows="".join(f"<tr><td>{esc(c['id'])}</td><td>{esc(c['goal_name'])}</td><td>{esc(c['plan_name'])}</td><td>{esc(c['skill_name'])}</td><td>{pct(c['proof_score']/1.5 if c['proof_score']<1.5 else 1,1)}</td></tr>" for c in accepted)
    body=f'''<main class="wrap"><section class="hero"><div><div class="eyebrow">Proof Gradient · Incremental Proof 002</div><h1 class="h1">Goal-Plan-Skill Alignment Lattice</h1><p class="lead">One agent tries. Proof decides. The network evolves — but only when the attempted upgrade is aligned with direction, strategy, capability, and public evidence.</p><div class="btns"><a class="btn primary" href="goals.html">GoalOS</a><a class="btn cyan" href="plans.html">PlanOS</a><a class="btn" href="skills.html">SkillOS</a><a class="btn" href="receipts.html">Receipt</a></div></div><aside class="panel heroCard"><span class="tag">{esc(receipt['status'])}</span><div class="bigMetric">{pct(receipt['comparisons']['proof_gradient_lattice']['holdout_success_rate'],1)}</div><p class="lead">holdout success with Proof Gradient alignment lattice</p><p class="muted">{esc(receipt['incremental_position'])}</p></aside></section><section class="axis"><article class="card"><span class="tag cyan">GoalOS</span><h3>Direction</h3><p>What should the network pursue?</p></article><article class="card"><span class="tag gold">PlanOS</span><h3>Strategy</h3><p>How should the network pursue it?</p></article><article class="card"><span class="tag violet">SkillOS</span><h3>Capability</h3><p>What can the network do?</p></article><article class="card"><span class="tag">Proof Gradient</span><h3>Evolution</h3><p>What should improve next?</p></article></section><section><h2>What the proof tested</h2><div class="panel"><p class="quote">Direction → Strategy → Capability → Proof → Evolution</p><p class="lead">The benchmark compares single-agent execution, SkillOS without goal/plan gates, static GoalOS+PlanOS+SkillOS coordination, unverified gradient propagation, and the full Proof Gradient alignment lattice.</p></div></section><section class="grid">{metric_cards(receipt)}</section><section class="grid2"><div class="panel"><h3>Release curve</h3><div class="svgbox">{line_chart(receipt['release_curve'])}</div></div><div class="panel"><h3>Comparison</h3><div class="svgbox">{bar_chart(receipt['comparisons'])}</div></div></section><section><h2>Protocol comparison</h2><div class="panel"><table class="table"><thead><tr><th>Protocol</th><th>Success</th><th>Value</th><th>Risk</th><th>Goal</th><th>Plan</th><th>Skill</th></tr></thead><tbody>{rows}</tbody></table></div></section><section><h2>Goals used</h2><div class="grid3">{cards(receipt['goals_used'],'goal')}</div></section><section><h2>Plans used</h2><div class="grid3">{cards(receipt['plans_used'],'plan')}</div></section><section><h2>Skills used</h2><div class="grid3">{cards(receipt['skills_used'],'skill')}</div></section><section><h2>Accepted evolution signals</h2><div class="panel"><table class="table"><thead><tr><th>Candidate</th><th>Goal</th><th>Plan</th><th>Skill</th><th>Proof score</th></tr></thead><tbody>{cand_rows}</tbody></table></div></section><section><h2>Public boundary</h2><div class="panel"><p>{'<br>'.join(esc(x) for x in receipt['public_claim_boundary'])}</p></div></section></main>'''
    write(out/"proof-gradient-goal-plan-skill-alignment-lattice.html", layout(receipt["title"], body))

def simple_page(out, name, title, intro, inner):
    body=f'<main class="wrap"><div class="eyebrow">Proof Gradient</div><h1 class="h1">{esc(title)}</h1><p class="lead">{esc(intro)}</p>{inner}</main>'
    write(out/name, layout(title, body))

def build_aux(out, receipt):
    simple_page(out,"goals.html","GoalOS · Direction","The goals used by the proof. These decide what the network is trying to improve.", f'<section class="grid3">{cards(receipt["goals_used"],"goal")}</section>')
    simple_page(out,"plans.html","PlanOS · Strategy","The plans used by the proof. These decide how the network should pursue each direction.", f'<section class="grid3">{cards(receipt["plans_used"],"plan")}</section>')
    simple_page(out,"skills.html","SkillOS · Capability","The skills used by the proof. Each card shows the layer, purpose, input, output, and verifier.", f'<section class="grid3">{cards(receipt["skills_used"],"skill")}</section>')
    receipt_json = json.dumps(receipt, indent=2, sort_keys=True)
    simple_page(out,"receipts.html","Receipts","Machine-readable evidence generated by the proof workflow.", f'<section class="panel"><p><a class="btn cyan" href="data/{PROOF_ID}.json">Open JSON receipt</a> <a class="btn" href="docs/PROOF_GRADIENT_GOAL_PLAN_SKILL_ALIGNMENT_LATTICE_PROOF.md">Open Markdown report</a> <a class="btn" href="badges/{PROOF_ID}.svg">Open badge</a></p><pre class="svgbox mono small" style="white-space:pre-wrap;max-height:520px;overflow:auto">{esc(receipt_json[:12000])}</pre></section>')
    simple_page(out,"run.html","Run / Regenerate","Use GitHub Actions to regenerate the proof, receipt, report, badge, Command Center, and proof page.", '<section class="grid2"><article class="card"><span class="tag">workflow</span><h3>Proof Gradient Goal-Plan-Skill Alignment Lattice Proof</h3><p>Open GitHub Actions, choose the workflow, and click Run workflow.</p><a class="btn cyan" href="https://github.com/MontrealAI/skillos/actions">Open Actions</a></article><article class="card"><span class="tag gold">root contract</span><h3>Command Center owns root</h3><p>/skillos/ and /skillos/index.html are the Command Center. This proof lives in its own room.</p></article></section>')
    simple_page(out,"proofs.html","Proofs","The current generated proof registry for this incremental pack.", f'<section class="grid2"><article class="card"><span class="tag">passed</span><h3>{esc(receipt["title"])}</h3><p>{esc(receipt["tagline"])}</p><a class="btn cyan" href="proof-gradient-goal-plan-skill-alignment-lattice.html">Open proof</a></article></section>')
    simple_page(out,"actions.html","Actions","GitHub-native regeneration path.", '<section class="panel"><p>Run the workflow from GitHub Actions to regenerate the proof and deploy the Pages artifact.</p><a class="btn cyan" href="https://github.com/MontrealAI/skillos/actions">Open GitHub Actions</a></section>')
    simple_page(out,"multi-agent.html","Multi-Agent System","The proof uses coordinated specialist roles rather than a single generic agent.", '<section class="grid3">' + ''.join(f'<article class="card"><span class="tag violet">role</span><h3>{esc(r)}</h3><p class="muted">Specialist role in the GoalOS / PlanOS / SkillOS / Proof Gradient lattice.</p></article>' for r in receipt['specialist_roles']) + '</section>')
    simple_page(out,"architecture.html","Architecture","Direction, strategy, capability, and proof-driven evolution form the architecture.", '<section class="panel"><p class="quote">GoalOS → PlanOS → SkillOS → Proof Gradient</p><p class="lead">The system improves only when a candidate upgrade satisfies direction, strategy, capability, proof, risk, and evidence gates.</p></section>')
    simple_page(out,"health.html","Health","Local verification is required before deployment and live verification is required after deployment.", '<section class="grid2"><article class="card"><span class="tag">local</span><h3>Artifact verification</h3><p>Checks required files, root contract, links, goals, plans, skills, and receipts.</p></article><article class="card"><span class="tag">live</span><h3>Root verification</h3><p>Checks that the public root is the Command Center and the proof is a subpage.</p></article></section>')
    simple_page(out,"runbook.html","Runbook","Simple operator guide for non-technical users.", '<section class="panel"><ol><li>Upload the pack files to GitHub.</li><li>Open Actions.</li><li>Run the Proof Gradient workflow.</li><li>Verify /skillos/ shows the Public SkillOS Command Center.</li><li>Open the Proof Gradient proof room.</li></ol></section>')
    write(out/"404.html", layout("SkillOS Page Not Found", '<main class="wrap"><h1 class="h1">Room not found.</h1><p class="lead">Return to the Public SkillOS Command Center.</p><a class="btn cyan" href="index.html">Home</a></main>'))
    write(out/"force-refresh.html", layout("SkillOS Force Refresh", '<main class="wrap"><h1 class="h1">Refresh complete.</h1><p class="lead">This page clears old service workers and points back to the Command Center.</p><a class="btn cyan" href="index.html?v=proof-gradient-gps">Open Command Center</a><script>if(navigator.serviceWorker){navigator.serviceWorker.getRegistrations().then(rs=>rs.forEach(r=>r.unregister()))}</script></main>'))
    write(out/"sw.js", "self.addEventListener('install',e=>self.skipWaiting());self.addEventListener('activate',e=>self.registration.unregister());")

def copy_artifacts(out, receipt):
    (out/"data").mkdir(exist_ok=True); (out/"docs").mkdir(exist_ok=True); (out/"badges").mkdir(exist_ok=True)
    shutil.copy2(Path("data")/f"{PROOF_ID}.json", out/"data"/f"{PROOF_ID}.json")
    doc=Path("docs")/"PROOF_GRADIENT_GOAL_PLAN_SKILL_ALIGNMENT_LATTICE_PROOF.md"
    if doc.exists(): shutil.copy2(doc, out/"docs"/doc.name)
    badge=Path("badges")/f"{PROOF_ID}.svg"
    if badge.exists(): shutil.copy2(badge, out/"badges"/badge.name)
    manifest={"schema":SCHEMA,"marker":MARKER,"generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z'),"root_contract":{"root":"Public SkillOS Command Center","proof_room":"proof-gradient-goal-plan-skill-alignment-lattice.html"},"proof_id":PROOF_ID,"receipt_hash":receipt.get("receipt_hash"),"goals":len(receipt.get("goals_used",[])),"plans":len(receipt.get("plans_used",[])),"skills":len(receipt.get("skills_used",[]))}
    write(out/"data"/"command-center-manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
    registry=[{"id":PROOF_ID,"title":receipt["title"],"status":receipt["status"],"href":"proof-gradient-goal-plan-skill-alignment-lattice.html","receipt":"data/"+PROOF_ID+".json","report":"docs/PROOF_GRADIENT_GOAL_PLAN_SKILL_ALIGNMENT_LATTICE_PROOF.md","badge":"badges/"+PROOF_ID+".svg","skills_used":len(receipt.get("skills_used",[])),"goals_used":len(receipt.get("goals_used",[])),"plans_used":len(receipt.get("plans_used",[]))}]
    write(out/"proof-registry.json", json.dumps(registry, indent=2, sort_keys=True))
    write(out/"sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>https://montrealai.github.io/skillos/{p}</loc></url>' for p in ["","index.html","proof-gradient-goal-plan-skill-alignment-lattice.html","goals.html","plans.html","skills.html","receipts.html","run.html"]) + '</urlset>')
    write(out/"robots.txt", "User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n")
    write(out/"version.txt", MARKER + "\n")
    write(out/".nojekyll", "")

def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--out", default="dist")
    args=ap.parse_args(); out=Path(args.out)
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    receipt=load_receipt()
    copy_artifacts(out, receipt)
    build_index(out, receipt)
    build_proof(out, receipt)
    build_aux(out, receipt)
    print(json.dumps({"built":str(out),"marker":MARKER,"proof":PROOF_ID,"pages":len(list(out.glob('*.html')))}, indent=2))

if __name__ == "__main__":
    main()
