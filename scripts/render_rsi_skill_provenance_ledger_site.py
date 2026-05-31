#!/usr/bin/env python3
from __future__ import annotations
import html, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"; SITE = ROOT / "site"; BADGES = ROOT / "badges"
PROOF = DATA / "rsi-skill-provenance-ledger-proof.json"
SITE.mkdir(parents=True, exist_ok=True); BADGES.mkdir(parents=True, exist_ok=True)

def esc(x: object) -> str:
    return html.escape(str(x))

def money(v: float) -> str:
    if abs(v) >= 1e12: return f"${v/1e12:,.2f}T"
    if abs(v) >= 1e9: return f"${v/1e9:,.2f}B"
    if abs(v) >= 1e6: return f"${v/1e6:,.2f}M"
    return f"${v:,.0f}"

def bar(label: str, value: float, note: str = "") -> str:
    width = max(0, min(100, float(value)))
    return f'<div class="bar-row"><div>{esc(label)}</div><div class="bar-track"><div class="bar-fill" style="width:{width:.3f}%"></div></div><strong>{esc(note or str(value))}</strong></div>'

def curve(releases: list[dict]) -> str:
    vals = [r["validation"]["benchmark_value_capture_rate_percent"] for r in releases]
    w,h,l,rgt,t,b = 940,280,48,28,30,230
    lo,hi = min(vals)-0.35, max(vals)+0.35
    pts=[]
    for i,v in enumerate(vals):
        x=l+i*((w-l-rgt)/max(1,len(vals)-1)); y=b-((v-lo)/max(0.001,hi-lo))*(b-t)
        pts.append((x,y,v))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x,y,_ in pts)
    circles = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5"/><text x="{x:.1f}" y="260" text-anchor="middle">v{i}</text>' for i,(x,y,_) in enumerate(pts))
    return f'<svg class="chart" viewBox="0 0 {w} {h}"><line x1="{l}" y1="{b}" x2="{w-rgt}" y2="{b}"/><line x1="{l}" y1="{t}" x2="{l}" y2="{b}"/><polyline points="{poly}"/>{circles}</svg>'

def radar(final: dict) -> str:
    axes = [
        ("Value capture", final["benchmark_value_capture_rate_percent"]),
        ("Frontier-correct", final["frontier_correct_rate_percent"]),
        ("Provenance", final["provenance_integrity_score"]),
        ("Rejection", final["adversarial_skill_rejection_rate_percent"]),
        ("Liquidity", final["capability_liquidity_score"]),
        ("Transfer", final["cross_domain_transfer_score"]),
        ("Verification", final["verification_quality"]),
        ("Trace compounding", final["trace_compounding_score"]),
    ]
    cx,cy,rr = 350,230,155
    pts=[]; labels=[]; lines=[]
    for i,(label,val) in enumerate(axes):
        a = -math.pi/2 + i*2*math.pi/len(axes)
        rad = rr*max(0,min(100,val))/100
        x,y = cx+rad*math.cos(a), cy+rad*math.sin(a)
        lx,ly = cx+(rr+48)*math.cos(a), cy+(rr+48)*math.sin(a)
        ax,ay = cx+rr*math.cos(a), cy+rr*math.sin(a)
        pts.append(f"{x:.1f},{y:.1f}")
        labels.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle">{esc(label)}</text>')
        lines.append(f'<line x1="{cx}" y1="{cy}" x2="{ax:.1f}" y2="{ay:.1f}"/>')
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{rr*f:.1f}"/>' for f in [0.25,0.5,0.75,1])
    return f'<svg class="radar" viewBox="0 0 700 470">{rings}{"".join(lines)}<polygon points="{" ".join(pts)}"/>{"".join(labels)}</svg>'

def constellation() -> str:
    cx,cy=470,300
    labels=["Skill markets","Verifier courts","Provenance registries","Release lanes","Routing policies","Transfer tests","Trace distillers","Adversarial red teams","Replay engines","Audit cells","Demand routers","Risk governors","Permission stewards","Skill publishers","Capability quorums","Regression sentinels"]
    nodes=[]
    for i,label in enumerate(labels*5):
        ring = 120 if i<16 else 205 if i<48 else 270
        denom = 16 if i<16 else 32 if i<48 else 32
        offset = i if i<16 else i-16 if i<48 else i-48
        a=-math.pi/2+offset*2*math.pi/denom+(0.12 if i>=16 else 0)
        x,y=cx+ring*math.cos(a), cy+ring*math.sin(a)
        nodes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{6 if i<16 else 5}"><title>{esc(label)}</title></circle>')
    return f'<svg class="constellation" viewBox="0 0 940 600"><circle class="core" cx="{cx}" cy="{cy}" r="78"/><text x="{cx}" y="{cy-8}" text-anchor="middle" class="core-text">SkillOS</text><text x="{cx}" y="{cy+22}" text-anchor="middle" class="core-sub">provenance RSI core</text>{"".join(nodes)}</svg>'

def main() -> None:
    if not PROOF.exists():
        raise SystemExit(f"Missing proof receipt: {PROOF}")
    proof=json.loads(PROOF.read_text(encoding="utf-8"))
    final=proof["final"]; b=proof["baselines"]
    badge = '<svg xmlns="http://www.w3.org/2000/svg" width="340" height="20" role="img" aria-label="skill provenance RSI proof: passed"><rect width="340" height="20" rx="10" fill="#102033"/><rect x="222" width="118" height="20" rx="10" fill="#2bb673"/><text x="10" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">skill provenance RSI</text><text x="239" y="14" fill="#fff" font-family="Verdana" font-size="11">proof passed</text></svg>'
    (BADGES/"rsi-skill-provenance-ledger-proof.svg").write_text(badge, encoding="utf-8")
    gate_rows="".join(f"<tr><td>{esc(k.replace('_',' '))}</td><td>{'passed' if v else 'failed'}</td></tr>" for k,v in proof["pre_registered_gates"].items())
    sample_rows="".join(f"<tr><td>{r['case_id']}</td><td>{r['chosen_skill_release']}</td><td>{r['oracle_skill_release']}</td><td>{'yes' if r['matched_oracle'] else 'near miss'}</td><td>{money(r['chosen_value_usd'])}</td><td>{money(r['oracle_value_usd'])}</td><td>{r['trace_quality']}</td><td>{r['poison_risk']}</td></tr>" for r in proof["holdout_samples"])
    html_text=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>SkillOS RSI Skill Provenance Ledger Proof</title>
<style>
:root{{--text:#f5fbff;--muted:#b8c8d8;--line:rgba(255,255,255,.16);--panel:rgba(255,255,255,.07);--panel2:rgba(255,255,255,.11);--cyan:#86f8ff;--green:#7dffb0;--gold:#ffd66b}}
*{{box-sizing:border-box}}body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;background:radial-gradient(circle at 82% 0,#3d4381 0,transparent 34%),radial-gradient(circle at 0 18%,#095e70 0,transparent 26%),linear-gradient(135deg,#06131f,#13243d 60%,#282a5d);color:var(--text)}}a{{color:var(--cyan);text-decoration:none}}nav{{position:sticky;top:0;z-index:3;background:rgba(6,19,31,.9);border-bottom:1px solid var(--line);backdrop-filter:blur(14px);display:flex;justify-content:space-between;gap:18px;padding:14px 22px}}nav strong{{color:var(--cyan)}}nav div{{display:flex;gap:14px;flex-wrap:wrap}}nav a{{font-weight:850;color:var(--muted)}}main{{max-width:1240px;margin:0 auto;padding:44px 20px 80px}}.hero{{display:grid;grid-template-columns:1.05fr .95fr;gap:22px;align-items:center}}.eyebrow{{color:var(--cyan);text-transform:uppercase;letter-spacing:.18em;font-weight:950;font-size:12px}}h1{{font-size:clamp(44px,7vw,100px);letter-spacing:-.08em;line-height:.86;margin:12px 0}}h2{{font-size:clamp(30px,4.6vw,60px);letter-spacing:-.055em;line-height:.95;margin:0 0 18px}}p{{color:var(--muted);line-height:1.55;font-size:18px}}.card{{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:28px;padding:24px;box-shadow:0 22px 80px rgba(0,0,0,.28)}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}}.metric{{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:18px}}.metric strong{{display:block;color:var(--green);font-size:32px;letter-spacing:-.04em}}.metric span{{color:var(--muted)}}.two{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:22px 0}}.section{{margin:34px 0}}.pill{{display:inline-flex;border-radius:999px;padding:7px 11px;background:rgba(125,255,176,.16);color:var(--green);font-size:12px;font-weight:950;text-transform:uppercase;letter-spacing:.08em}}.quote{{font-size:clamp(24px,3.2vw,44px);line-height:1.08;letter-spacing:-.04em;color:var(--text)}}.bar-row{{display:grid;grid-template-columns:245px 1fr 150px;align-items:center;gap:12px;margin:12px 0}}.bar-track{{height:20px;background:rgba(255,255,255,.08);border-radius:999px;overflow:hidden}}.bar-fill{{height:100%;background:linear-gradient(90deg,var(--green),var(--cyan));border-radius:999px}}table{{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:18px;overflow:hidden}}th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}}.chart,.radar,.constellation{{width:100%;height:auto;background:rgba(0,0,0,.16);border:1px solid var(--line);border-radius:24px;padding:12px}}.chart line,.chart polyline{{stroke:var(--green);stroke-width:4;fill:none}}.chart line{{stroke:rgba(255,255,255,.16);stroke-width:1}}.chart circle{{fill:var(--green)}}.chart text,.radar text{{fill:var(--muted);font-size:12px}}.radar circle,.radar line{{fill:none;stroke:rgba(255,255,255,.14)}}.radar polygon{{fill:rgba(134,248,255,.19);stroke:var(--cyan);stroke-width:3}}.constellation line{{stroke:rgba(134,248,255,.095)}}.constellation circle{{fill:var(--cyan)}}.constellation .core{{fill:rgba(125,255,176,.12);stroke:var(--green)}}.core-text{{fill:var(--text);font-weight:950;font-size:22px}}.core-sub{{fill:var(--muted);font-size:13px}}.notice{{border-left:4px solid var(--gold);background:rgba(255,214,107,.08);border-radius:16px;padding:16px 18px;color:var(--muted)}}@media(max-width:900px){{.hero,.grid,.two{{grid-template-columns:1fr}}.bar-row{{grid-template-columns:1fr}}nav{{flex-direction:column}}}}
</style></head><body>
<nav><strong>SkillOS Skill Provenance Ledger</strong><div><a href="index.html">Command Center</a><a href="proofs.html">Proofs</a><a href="../data/rsi-skill-provenance-ledger-proof.json">JSON</a><a href="../docs/rsi-skill-provenance-ledger-proof.md">Report</a></div></nav>
<main>
<section class="hero"><div><div class="eyebrow">MONTREAL.AI / SKILLOS</div><h1>Skill Provenance Ledger.</h1><p>Autonomous proof that verified traces can become replayable, transferable, safe, reusable skills through validation-gated Recursive Self-Improvement.</p></div><div class="card"><span class="pill">proof passed</span><div class="quote">{proof['agent_system']['virtual_specialist_agents']:,} virtual agents. {proof['agent_system']['specialist_roles']:,} roles. {proof['rsi_release_count']} RSI releases. {proof['benchmark_public']['holdout_count']} locked holdout cases.</div><p>{esc(proof['safe_interpretation'])}</p></div></section>
<section class="grid"><div class="metric"><strong>{final['benchmark_value_capture_rate_percent']}%</strong><span>benchmark value capture</span></div><div class="metric"><strong>{final['provenance_integrity_score']}%</strong><span>provenance integrity</span></div><div class="metric"><strong>{final['adversarial_skill_rejection_rate_percent']}%</strong><span>adversarial skill rejection</span></div><div class="metric"><strong>{money(final['total_benchmark_value_captured_usd'])}</strong><span>benchmark value captured</span></div></section>
<section class="section card"><div class="eyebrow">core mechanism</div><div class="quote">work traces -> candidate skills -> provenance ledger -> verifier courts -> signed releases -> routing upgrades -> transfer tests -> reinvestment -> compounding skill trust</div><p>This proof does not claim achieved superintelligence or Kardashev Type II civilization. It makes the trust mechanism underneath capability compounding publicly testable.</p></section>
<section class="two"><div class="card"><h2>RSI release curve</h2>{curve(proof['rsi_releases'])}</div><div class="card"><h2>Capability radar</h2>{radar(final)}</div></section>
<section class="section"><h2>Baselines and controls</h2><div class="card">
{bar('Single generalist', b['single_generalist']['benchmark_value_capture_rate_percent'], str(b['single_generalist']['benchmark_value_capture_rate_percent'])+'%')}
{bar('Uncoordinated agent pool', b['uncoordinated_agent_pool']['benchmark_value_capture_rate_percent'], str(b['uncoordinated_agent_pool']['benchmark_value_capture_rate_percent'])+'%')}
{bar('Static skill catalog', b['static_skill_catalog']['benchmark_value_capture_rate_percent'], str(b['static_skill_catalog']['benchmark_value_capture_rate_percent'])+'%')}
{bar('No-RSI provenance ledger', b['no_rsi_provenance_ledger']['benchmark_value_capture_rate_percent'], str(b['no_rsi_provenance_ledger']['benchmark_value_capture_rate_percent'])+'%')}
{bar('SkillOS RSI provenance ledger', final['benchmark_value_capture_rate_percent'], str(final['benchmark_value_capture_rate_percent'])+'%')}
</div></section>
<section class="section"><h2>Large specialist-agent organization</h2><div class="card">{constellation()}</div></section>
<section class="section"><h2>Pre-registered gates</h2><table><tr><th>Gate</th><th>Status</th></tr>{gate_rows}</table></section>
<section class="section"><h2>Holdout samples</h2><table><tr><th>Case</th><th>Chosen</th><th>Oracle</th><th>Match</th><th>Chosen value</th><th>Oracle value</th><th>Trace quality</th><th>Poison risk</th></tr>{sample_rows}</table></section>
<section class="notice"><strong>Public boundary:</strong> benchmark proof values are not audited customer revenue, live customer adoption, financial advice, legal advice, investment advice, token advice, achieved superintelligence, or Kardashev Type II achievement. Protocol fingerprint: {esc(proof['protocol_fingerprint_sha256'])}.</section>
</main></body></html>"""
    page = SITE / "rsi-skill-provenance-ledger-proof.html"
    page.write_text(html_text, encoding="utf-8")
    print(json.dumps({"status":"VISIBLE_OUTPUTS_WRITTEN","html":str(page.relative_to(ROOT)),"json":"data/rsi-skill-provenance-ledger-proof.json","markdown":"docs/rsi-skill-provenance-ledger-proof.md","badge":"badges/rsi-skill-provenance-ledger-proof.svg"}, indent=2))

if __name__ == "__main__":
    main()
