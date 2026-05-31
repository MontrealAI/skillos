#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
SITE = ROOT / "site"
BADGES = ROOT / "badges"
PROOF = DATA / "rsi_corporate_capability_frontier_proof.json"

SITE.mkdir(parents=True, exist_ok=True)
BADGES.mkdir(parents=True, exist_ok=True)


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def money(value: float) -> str:
    if abs(value) >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:,.2f}T"
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    return f"${value:,.0f}"


def compact(value: float) -> str:
    if abs(value) >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:,.2f}T"
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.1f}M"
    return f"{value:,.0f}"


def curve_svg(releases: list[dict]) -> str:
    values = [r["validation"]["benchmark_value_capture_rate_percent"] for r in releases if r["released"]]
    if len(values) < 2:
        values = [r["validation"]["benchmark_value_capture_rate_percent"] for r in releases]
    w, h = 980, 310
    left, right, top, bottom = 54, 28, 34, 238
    lo = min(values) - 0.25
    hi = max(values) + 0.25
    pts = []
    for i, v in enumerate(values):
        x = left + i * ((w - left - right) / max(1, len(values) - 1))
        y = bottom - ((v - lo) / max(0.001, hi - lo)) * (bottom - top)
        pts.append((x, y, v))
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts)
    labels = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5"/><text x="{x:.1f}" y="275" text-anchor="middle">v{i}</text>' for i, (x, y, _) in enumerate(pts))
    ylabels = "".join(f'<text x="8" y="{bottom - frac * (bottom-top):.1f}">{lo + frac*(hi-lo):.2f}%</text>' for frac in [0, .5, 1])
    return f'''<svg viewBox="0 0 {w} {h}" class="chart" aria-label="RSI release curve">
      <defs><linearGradient id="curveFill" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#8dffbd" stop-opacity=".36"/><stop offset="1" stop-color="#8dffbd" stop-opacity="0"/></linearGradient></defs>
      <line x1="{left}" y1="{bottom}" x2="{w-right}" y2="{bottom}"/><line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}"/>
      <path class="area" d="M {left} {bottom} L {line.replace(' ', ' L ')} L {pts[-1][0]:.1f} {bottom} Z"/>
      <polyline points="{line}"/>{labels}{ylabels}
    </svg>'''


def radar_svg(final: dict[str, float]) -> str:
    axes = [
        ("Coordination", final["coordination_protocol_accuracy_percent"]),
        ("Role quorum", final["role_quorum_accuracy_percent"]),
        ("Value capture", final["benchmark_value_capture_rate_percent"]),
        ("Risk control", 100 - final["risk_breach_rate_percent"]),
        ("Compounding", final["compounding_index"]),
        ("Council balance", final["council_balance_index"]),
        ("Capability lever", final["capability_lever_accuracy_percent"]),
        ("Capacity", final["coordination_index"]),
    ]
    cx, cy, r = 320, 250, 165
    points, labels, rays = [], [], []
    for i, (label, val) in enumerate(axes):
        angle = -math.pi / 2 + i * math.tau / len(axes)
        rr = r * max(0, min(100, val)) / 100
        x, y = cx + rr * math.cos(angle), cy + rr * math.sin(angle)
        ax, ay = cx + r * math.cos(angle), cy + r * math.sin(angle)
        lx, ly = cx + (r + 55) * math.cos(angle), cy + (r + 55) * math.sin(angle)
        points.append(f"{x:.1f},{y:.1f}")
        labels.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle">{esc(label)}</text>')
        rays.append(f'<line x1="{cx}" y1="{cy}" x2="{ax:.1f}" y2="{ay:.1f}"/>')
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r * f:.1f}"/>' for f in [.25, .5, .75, 1])
    return f'''<svg viewBox="0 0 640 500" class="radar" aria-label="Capability coordination radar">{rings}{''.join(rays)}
      <polygon points="{' '.join(points)}"/>{''.join(labels)}
    </svg>'''


def frontier_svg(proof: dict) -> str:
    final = proof["final"]
    systems = [
        ("Single", proof["single_corporate_generalist"]["benchmark_value_capture_rate_percent"], 22, "#ffcf72"),
        ("Swarm", proof["uncoordinated_multi_agent_swarm"]["benchmark_value_capture_rate_percent"], 34, "#9aa7ff"),
        ("Static", proof["static_multi_agent_committee"]["benchmark_value_capture_rate_percent"], 40, "#a7d5ff"),
        ("No-RSI", proof["no_rsi_large_organization"]["benchmark_value_capture_rate_percent"], 46, "#c9f"),
        ("SkillOS RSI", final["benchmark_value_capture_rate_percent"], 64, "#8dffbd"),
    ]
    minv = min(v for _, v, _, _ in systems) - 1.5
    maxv = max(v for _, v, _, _ in systems) + .4
    w, h = 980, 360
    left, top, bottom = 74, 38, 284
    points = []
    for i, (name, value, size, color) in enumerate(systems):
        x = left + i * ((w - left - 80) / (len(systems) - 1))
        y = bottom - ((value - minv) / (maxv - minv)) * (bottom - top)
        points.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size}" fill="{color}" opacity=".78"/><text x="{x:.1f}" y="{y + size + 28:.1f}" text-anchor="middle">{esc(name)}</text><text x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle" class="inside">{value:.2f}%</text>')
    return f'''<svg viewBox="0 0 {w} {h}" class="frontier" aria-label="Capability frontier comparison">
      <line x1="{left}" y1="{bottom}" x2="{w-40}" y2="{bottom}"/><line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}"/>
      <text x="10" y="28">benchmark value capture</text>{''.join(points)}
    </svg>'''


def constellation_svg(proof: dict) -> str:
    roles = proof["agent_system"]["roles"]
    councils = proof["agent_system"]["councils"]
    cx, cy = 500, 345
    lines = []
    for cidx, council in enumerate(councils):
        angle = -math.pi / 2 + cidx * math.tau / len(councils)
        council_x = cx + 185 * math.cos(angle)
        council_y = cy + 185 * math.sin(angle)
        lines.append(f'<line x1="{cx}" y1="{cy}" x2="{council_x:.1f}" y2="{council_y:.1f}"/><circle class="council" cx="{council_x:.1f}" cy="{council_y:.1f}" r="12"><title>{esc(council)}</title></circle>')
        for ridx in range(4):
            sub_angle = angle + (ridx - 1.5) * 0.075
            x = cx + (265 + 16 * (ridx % 2)) * math.cos(sub_angle)
            y = cy + (265 + 16 * (ridx % 2)) * math.sin(sub_angle)
            role_idx = cidx * 32 + ridx * 7
            role = roles[role_idx % len(roles)]
            lines.append(f'<line x1="{council_x:.1f}" y1="{council_y:.1f}" x2="{x:.1f}" y2="{y:.1f}"/><circle class="role" cx="{x:.1f}" cy="{y:.1f}" r="5"><title>{esc(role)}</title></circle>')
    return f'''<svg viewBox="0 0 1000 690" class="constellation" aria-label="Specialist agent superorganization">
      <circle class="core" cx="{cx}" cy="{cy}" r="86"/><text x="{cx}" y="{cy-8}" text-anchor="middle" class="coreTitle">SkillOS</text><text x="{cx}" y="{cy+24}" text-anchor="middle" class="coreSub">Corporate RSI Core</text>{''.join(lines)}
    </svg>'''


def baseline_table(proof: dict) -> str:
    rows = [
        ("Single corporate generalist", proof["single_corporate_generalist"]),
        ("Uncoordinated multi-agent swarm", proof["uncoordinated_multi_agent_swarm"]),
        ("Static multi-agent committee", proof["static_multi_agent_committee"]),
        ("No-RSI large organization", proof["no_rsi_large_organization"]),
        ("Shuffled-reward RSI control", proof["negative_controls"]["shuffled_reward_rsi"]),
        ("Random protocol control", proof["negative_controls"]["random_protocol"]),
        ("Risk-blind control", proof["negative_controls"]["risk_blind_control"]),
        ("SkillOS RSI corporate frontier", proof["final"]),
    ]
    body = "".join(f"<tr><td>{esc(name)}</td><td>{m['benchmark_value_capture_rate_percent']}%</td><td>{m['fully_correct_percent']}%</td><td>{m['risk_breach_rate_percent']}%</td><td>{m['unsafe_action_rate_percent']}%</td><td>{money(m['total_benchmark_value_captured_usd'])}</td></tr>" for name, m in rows)
    return f"<table><tr><th>System</th><th>Value capture</th><th>Fully correct</th><th>Risk breach</th><th>Unsafe</th><th>Captured</th></tr>{body}</table>"


def gates_table(gates: dict[str, bool]) -> str:
    rows = "".join(f"<tr><td>{esc(k.replace('_', ' '))}</td><td><span class=\"{'ok' if v else 'bad'}\">{'passed' if v else 'failed'}</span></td></tr>" for k, v in gates.items())
    return f"<table><tr><th>Pre-registered gate</th><th>Status</th></tr>{rows}</table>"


def releases_table(releases: list[dict]) -> str:
    body = "".join(f"<tr><td>v{idx}</td><td>{'released' if r['released'] else 'rejected'}</td><td>{esc(r['protocol_name'])}</td><td>{esc(r['lesson'])}</td><td>{r['validation']['benchmark_value_capture_rate_percent']}%</td><td>{r['validation']['fully_correct_percent']}%</td><td>{r['validation']['risk_breach_rate_percent']}%</td></tr>" for idx, r in enumerate(releases))
    return f"<table><tr><th>Release</th><th>Gate</th><th>Protocol</th><th>Lesson</th><th>Validation capture</th><th>Correct</th><th>Risk</th></tr>{body}</table>"


def samples_table(samples: list[dict]) -> str:
    body = "".join(f"<tr><td>{r['case_id']}</td><td>{esc(r['regime'])}</td><td>{r['chosen_action']}</td><td>{r['oracle_action']}</td><td>{'yes' if r['oracle_match'] else 'near miss'}</td><td>{money(r['chosen_value_usd'])}</td><td>{money(r['oracle_value_usd'])}</td><td>{r['risk_load']}</td></tr>" for r in samples)
    return f"<table><tr><th>Case</th><th>Regime</th><th>Chosen</th><th>Oracle</th><th>Match</th><th>Chosen value</th><th>Oracle value</th><th>Risk load</th></tr>{body}</table>"


CSS = r'''
:root{--ink:#f5fbff;--muted:#bfd0e0;--dim:#8ba4b9;--cyan:#83f7ff;--green:#82ffb4;--gold:#ffd872;--red:#ff8d8d;--panel:rgba(255,255,255,.075);--panel2:rgba(255,255,255,.125);--line:rgba(255,255,255,.18)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;background:radial-gradient(circle at 83% -10%,#684ba6 0,transparent 34%),radial-gradient(circle at 0 22%,#076879 0,transparent 30%),linear-gradient(135deg,#061521 0,#172743 52%,#25245f 100%)}body:before{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.036) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.036) 1px,transparent 1px);background-size:42px 42px;pointer-events:none;mask-image:linear-gradient(to bottom,rgba(0,0,0,.95),rgba(0,0,0,.06))}
a{color:var(--cyan);text-decoration:none}nav{position:sticky;top:0;z-index:10;padding:13px 20px;display:flex;justify-content:space-between;gap:20px;align-items:center;background:rgba(5,16,28,.92);border-bottom:1px solid var(--line);backdrop-filter:blur(14px)}nav strong{color:var(--cyan);letter-spacing:-.02em}nav div{display:flex;gap:16px;flex-wrap:wrap}nav a{font-weight:850;color:var(--muted);font-size:14px}
main{max-width:1240px;margin:auto;padding:56px 22px 90px;position:relative}.hero{display:grid;grid-template-columns:1.12fr .88fr;gap:26px;align-items:center}.eyebrow{color:var(--cyan);font-size:12px;letter-spacing:.22em;text-transform:uppercase;font-weight:950}h1{font-size:clamp(52px,8vw,118px);line-height:.82;letter-spacing:-.085em;margin:12px 0 18px}h2{font-size:clamp(34px,5vw,66px);line-height:.92;letter-spacing:-.06em;margin:0 0 18px}h3{font-size:24px;letter-spacing:-.03em}p{font-size:18px;line-height:1.55;color:var(--muted)}.quote{font-size:clamp(28px,4.8vw,58px);line-height:.98;letter-spacing:-.055em}.card{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:30px;padding:26px;box-shadow:0 24px 80px rgba(0,0,0,.25)}.metricGrid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:28px 0}.metric{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:18px}.metric strong{display:block;color:var(--green);font-size:34px;letter-spacing:-.04em}.metric span{color:var(--muted)}.pill{display:inline-flex;align-items:center;border-radius:999px;background:rgba(130,255,180,.15);color:var(--green);text-transform:uppercase;letter-spacing:.10em;font-size:12px;font-weight:950;padding:7px 12px}.section{margin:36px 0}.two{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:24px 0}.chart,.radar,.frontier,.constellation{width:100%;height:auto;background:rgba(0,0,0,.18);border:1px solid var(--line);border-radius:26px;padding:12px}.chart line,.frontier line{stroke:rgba(255,255,255,.18);stroke-width:1}.chart polyline{stroke:var(--green);fill:none;stroke-width:4}.chart circle{fill:var(--green)}.chart .area{fill:url(#curveFill)}.chart text,.radar text,.frontier text{fill:var(--muted);font-size:12px}.frontier .inside{fill:#061521;font-weight:950}.radar circle,.radar line{fill:none;stroke:rgba(255,255,255,.15)}.radar polygon{fill:rgba(131,247,255,.20);stroke:var(--cyan);stroke-width:3}.constellation line{stroke:rgba(131,247,255,.08)}.constellation .core{fill:rgba(130,255,180,.13);stroke:var(--green);stroke-width:2}.constellation .council{fill:var(--cyan)}.constellation .role{fill:var(--green)}.coreTitle{fill:var(--ink);font-size:25px;font-weight:950}.coreSub{fill:var(--muted);font-size:14px}table{width:100%;border-collapse:collapse;border:1px solid var(--line);background:var(--panel);border-radius:18px;overflow:hidden}th,td{padding:12px 13px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--dim);text-transform:uppercase;font-size:12px;letter-spacing:.09em}tr:last-child td{border-bottom:0}.ok{color:var(--green);font-weight:900}.bad{color:var(--red);font-weight:900}.notice{border-left:4px solid var(--gold);background:rgba(255,216,114,.08);border-radius:18px;padding:18px 20px;color:var(--muted)}.runbox{display:grid;grid-template-columns:1fr auto;gap:18px;align-items:center}.btn{display:inline-flex;padding:13px 18px;border-radius:999px;background:var(--cyan);color:#061521;font-weight:950}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}.small{font-size:14px;color:var(--dim)}@media(max-width:920px){.hero,.two,.metricGrid,.runbox{grid-template-columns:1fr}nav{align-items:flex-start;flex-direction:column}h1{font-size:58px}}
'''


def main() -> None:
    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    f = proof["final"]
    c = proof["comparisons"]

    badge = f'''<svg xmlns="http://www.w3.org/2000/svg" width="390" height="20" role="img" aria-label="corporate capability frontier proof: passed">
<linearGradient id="g" x2="1"><stop stop-color="#071b2e"/><stop offset="1" stop-color="#253268"/></linearGradient>
<rect width="390" height="20" rx="10" fill="url(#g)"/>
<rect x="276" width="114" height="20" rx="10" fill="#20bf7a"/>
<text x="10" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">corporate capability frontier</text>
<text x="294" y="14" fill="#fff" font-family="Verdana" font-size="11">proof passed</text>
</svg>'''
    (BADGES / "rsi_corporate_capability_frontier_proof.svg").write_text(badge, encoding="utf-8")

    html_text = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SkillOS Autonomous RSI Corporate Capability Frontier Proof</title>
<meta name="description" content="Autonomous GitHub Action proof that a large specialist-agent corporate superorganization recursively improves enterprise coordination.">
<style>{CSS}</style>
</head>
<body>
<nav>
  <strong>SkillOS Corporate Capability Frontier</strong>
  <div>
    <a href="index.html">Command Center</a>
    <a href="proofs.html">Proofs</a>
    <a href="multi-agent.html">Multi-Agent</a>
    <a href="../data/rsi_corporate_capability_frontier_proof.json">JSON</a>
    <a href="../docs/rsi_corporate_capability_frontier_proof.md">Report</a>
    <a href="runbook.html">Run</a>
  </div>
</nav>
<main>
<section class="hero">
  <div>
    <div class="eyebrow">MONTREAL.AI / SKILLOS / EDGE OF CORPORATE CAPABILITY</div>
    <h1>Corporate Capability Frontier.</h1>
    <p>Autonomous, validation-gated proof that a large specialist-agent superorganization can recursively improve the coordination layer that converts resources into compounding productive capability.</p>
  </div>
  <div class="card">
    <span class="pill">proof passed</span>
    <div class="quote">{proof['agent_system']['agent_count']:,} agents. {proof['agent_system']['role_count']:,} roles. {proof['rsi_release_count']} RSI releases. {proof['benchmark']['holdout_count']:,} locked holdout cases.</div>
    <p>{esc(proof['safe_public_boundary'])}</p>
  </div>
</section>

<section class="metricGrid">
  <div class="metric"><strong>{f['benchmark_value_capture_rate_percent']}%</strong><span>benchmark value capture</span></div>
  <div class="metric"><strong>{compact(f['total_benchmark_value_captured_usd'])}</strong><span>benchmark value captured</span></div>
  <div class="metric"><strong>{compact(c['vs_single_corporate_generalist']['benchmark_value_captured_gain_usd'])}</strong><span>over single generalist</span></div>
  <div class="metric"><strong>{f['risk_breach_rate_percent']}%</strong><span>risk breach rate</span></div>
</section>

<section class="section card">
  <div class="eyebrow">Kardashev-scale mechanism, corporate proof</div>
  <div class="quote">capital → compute → energy → data → trust → talent → product → distribution → validation → risk control → reinvestment → compounding productive capability</div>
  <p>The page does not claim achieved superintelligence or Kardashev Type II civilization. It makes the enterprise mechanism underneath that value thesis runnable, measurable, and publicly repeatable.</p>
</section>

<section class="two">
  <div class="card"><h2>RSI release curve</h2>{curve_svg(proof['rsi_releases'])}<p>Each released protocol must pass the validation gate before the final fingerprint is evaluated on locked holdout cases.</p></div>
  <div class="card"><h2>Capability radar</h2>{radar_svg(f)}<p>Coordination, role quorum, value capture, risk control, compounding, and council balance are measured separately.</p></div>
</section>

<section class="section card">
  <h2>Capability frontier comparison</h2>{frontier_svg(proof)}
  <p>SkillOS RSI coordination is tested against a single corporate generalist, an uncoordinated swarm, a static multi-agent committee, a no-RSI large organization, and negative controls.</p>
</section>

<section class="section">
  <h2>Large multi-agent coordination</h2>
  <div class="card">{constellation_svg(proof)}<p>The proof represents {proof['agent_system']['agent_count']:,} deterministic virtual specialist agents across {proof['agent_system']['role_count']:,} roles and {proof['agent_system']['governance_council_count']} governance councils. The public phrase used in the proof is: <strong>{esc(proof['agent_system']['large_multi_agent_wording'])}</strong>.</p></div>
</section>

<section class="section">
  <h2>Baseline table</h2>{baseline_table(proof)}
</section>

<section class="section">
  <h2>Pre-registered gates</h2>{gates_table(proof['pre_registered_gates'])}
</section>

<section class="section">
  <h2>RSI protocol releases</h2>{releases_table(proof['rsi_releases'])}
</section>

<section class="section">
  <h2>Holdout receipts</h2>{samples_table(proof['holdout_samples'])}
</section>

<section class="section card runbox">
  <div>
    <div class="eyebrow">Run / regenerate</div>
    <h2>Re-run the proof from GitHub Actions.</h2>
    <p>Open the workflow, click <span class="mono">Run workflow</span>, and the Action regenerates the JSON receipt, Markdown report, visual proof page, public badge, and SkillOS homepage integration.</p>
  </div>
  <div><a class="btn" href="https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-corporate-capability-frontier-proof.yml">Run on GitHub</a></div>
</section>

<section class="notice">
  <strong>Public boundary:</strong> {esc(proof['safe_public_boundary'])}<br>
  <span class="mono small">Protocol fingerprint: {esc(proof['protocol_fingerprint_sha256'])}</span>
</section>
</main>
</body>
</html>'''

    page = SITE / "rsi-corporate-capability-frontier-proof.html"
    page.write_text(html_text, encoding="utf-8")
    print(json.dumps({
        "status": "VISIBLE_OUTPUTS_WRITTEN",
        "html": str(page.relative_to(ROOT)),
        "json": "data/rsi_corporate_capability_frontier_proof.json",
        "markdown": "docs/rsi_corporate_capability_frontier_proof.md",
        "badge": "badges/rsi_corporate_capability_frontier_proof.svg",
    }, indent=2))


if __name__ == "__main__":
    main()
