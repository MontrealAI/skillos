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
PROOF = DATA / "rsi_enterprise_eureka_factory_proof.json"

SITE.mkdir(parents=True, exist_ok=True)
BADGES.mkdir(parents=True, exist_ok=True)


def esc(value: object) -> str:
    return html.escape(str(value))


def money(value: float) -> str:
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"
    return f"${value:,.0f}"


def pct_bar(label: str, value: float, note: str = "") -> str:
    width = max(0.0, min(100.0, value))
    return f"""
    <div class="bar-row">
      <div class="bar-label">{esc(label)}</div>
      <div class="bar-track"><div class="bar-fill" style="width:{width:.2f}%"></div></div>
      <div class="bar-value">{esc(note or (str(value) + '%'))}</div>
    </div>
    """


def rsi_curve(releases: list[dict]) -> str:
    vals = [release["validation"]["benchmark_value_capture_rate_percent"] for release in releases]
    width, height, left, right, top, bottom = 940, 280, 46, 28, 28, 228
    lo, hi = min(vals) - 0.4, max(vals) + 0.4
    points = []
    for idx, value in enumerate(vals):
        x = left + idx * ((width - left - right) / max(1, len(vals) - 1))
        y = bottom - ((value - lo) / max(0.001, hi - lo)) * (bottom - top)
        points.append((x, y, value))
    polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in points)
    circles = "\n".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5"/><text x="{x:.1f}" y="258" text-anchor="middle">v{idx}</text>'
        for idx, (x, y, _) in enumerate(points)
    )
    return f"""<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="RSI release curve">
      <line x1="{left}" y1="{bottom}" x2="{width-right}" y2="{bottom}" />
      <line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" />
      <path d="M {left} {bottom} L {polyline.replace(' ', ' L ')} L {points[-1][0]:.1f} {bottom} Z" class="area"/>
      <polyline points="{polyline}" />
      {circles}
    </svg>"""


def radar(final: dict) -> str:
    axes = [
        ("Coordination", final["coordination_protocol_accuracy_percent"]),
        ("Risk control", final["risk_control_accuracy_percent"]),
        ("Role quorum", final["role_quorum_accuracy_percent"]),
        ("Value capture", final["benchmark_value_capture_rate_percent"]),
        ("Compounding", final["avg_compounding_index"]),
        ("Capacity", final["avg_productive_capacity_index"]),
    ]
    cx, cy, radius = 310, 200, 138
    pts, labels, axes_lines = [], [], []
    for idx, (label, value) in enumerate(axes):
        angle = -math.pi / 2 + idx * 2 * math.pi / len(axes)
        rr = radius * max(0.0, min(100.0, value)) / 100.0
        x, y = cx + rr * math.cos(angle), cy + rr * math.sin(angle)
        lx, ly = cx + (radius + 42) * math.cos(angle), cy + (radius + 42) * math.sin(angle)
        ax, ay = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        pts.append(f"{x:.1f},{y:.1f}")
        labels.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle">{esc(label)}</text>')
        axes_lines.append(f'<line x1="{cx}" y1="{cy}" x2="{ax:.1f}" y2="{ay:.1f}" />')
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{radius * frac:.1f}" />' for frac in [0.25, 0.50, 0.75, 1.0])
    return f"""<svg class="radar" viewBox="0 0 620 410" role="img" aria-label="Capability radar">
      {rings}{''.join(axes_lines)}
      <polygon points="{' '.join(pts)}" />
      {''.join(labels)}
    </svg>"""


def constellation(roles: list[str]) -> str:
    cx, cy = 470, 310
    nodes = []
    for idx, role in enumerate(roles[:128]):
        if idx < 32:
            ring, denom, offset = 122, 32, idx
        elif idx < 80:
            ring, denom, offset = 206, 48, idx - 32
        else:
            ring, denom, offset = 270, 48, idx - 80
        angle = -math.pi / 2 + offset * 2 * math.pi / denom + (0.10 if idx >= 32 else 0.0)
        x, y = cx + ring * math.cos(angle), cy + ring * math.sin(angle)
        nodes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{5 if idx >= 32 else 6}"><title>{esc(role)}</title></circle>')
    return f"""<svg class="constellation" viewBox="0 0 940 620" role="img" aria-label="Large specialist-agent organization">
      <circle class="core" cx="{cx}" cy="{cy}" r="78"/>
      <text x="{cx}" y="{cy-8}" text-anchor="middle" class="core-text">SkillOS</text>
      <text x="{cx}" y="{cy+22}" text-anchor="middle" class="core-sub">RSI coordination core</text>
      {''.join(nodes)}
    </svg>"""


def gates_table(gates: dict[str, bool]) -> str:
    rows = "".join(f"<tr><td>{esc(key.replace('_', ' '))}</td><td>{'passed' if value else 'failed'}</td></tr>" for key, value in gates.items())
    return f"<table><tr><th>Gate</th><th>Status</th></tr>{rows}</table>"


def main() -> None:
    if not PROOF.exists():
        raise SystemExit(f"Missing proof receipt: {PROOF}")

    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    final = proof["final"]
    single = proof["single_agent_baseline"]
    pool = proof["uncoordinated_multi_agent_pool"]
    static = proof["static_multi_agent_coordination"]
    shuffled = proof["negative_controls"]["shuffled_reward_rsi"]
    random_control = proof["negative_controls"]["random_protocol"]
    comparisons = proof["comparisons"]

    badge = f"""<svg xmlns="http://www.w3.org/2000/svg" width="340" height="20" role="img" aria-label="enterprise eureka RSI proof: passed">
<linearGradient id="g" x2="1" y2="0"><stop stop-color="#102033"/><stop offset="1" stop-color="#153b4a"/></linearGradient>
<rect width="340" height="20" rx="10" fill="url(#g)"/>
<rect x="222" width="118" height="20" rx="10" fill="#2bb673"/>
<text x="10" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">enterprise eureka RSI</text>
<text x="239" y="14" fill="#ffffff" font-family="Verdana" font-size="11">proof passed</text>
</svg>"""
    (BADGES / "rsi_enterprise_eureka_factory_proof.svg").write_text(badge, encoding="utf-8")

    release_rows = "\n".join(
        f"<tr><td>v{r['generation']}</td><td>{'released' if r['released'] else 'rejected'}</td><td>{esc(r['lesson'])}</td><td>{r['validation']['benchmark_value_capture_rate_percent']}%</td><td>{r['validation']['fully_correct_percent']}%</td><td>{r['validation']['risk_breach_rate_percent']}%</td><td>{r['score']}</td></tr>"
        for r in proof["rsi_releases"]
    )
    sample_rows = "\n".join(
        f"<tr><td>{row['scenario_id']}</td><td>{row['chosen_move']}</td><td>{row['oracle_move']}</td><td>{'yes' if row['matched_oracle'] else 'near miss'}</td><td>{money(row['chosen_value_usd'])}</td><td>{money(row['oracle_value_usd'])}</td><td>{row['risk_load']}</td><td>{row['compounding']}</td></tr>"
        for row in proof["holdout_samples"]
    )
    role_chips = "".join(f"<span>{esc(role)}</span>" for role in proof["agent_system"]["roles"])

    html_text = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SkillOS Autonomous RSI Enterprise Eureka Factory Proof</title>
<style>
:root{{--text:#f5fbff;--muted:#b8c8d8;--line:rgba(255,255,255,.16);--panel:rgba(255,255,255,.07);--panel2:rgba(255,255,255,.11);--cyan:#86f8ff;--green:#7dffb0;--gold:#ffd66b;--red:#ff8585;--purple:#b9a5ff}}
*{{box-sizing:border-box}}body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;background:radial-gradient(circle at 82% 0,#3d4381 0,transparent 34%),radial-gradient(circle at 0 18%,#095e70 0,transparent 26%),linear-gradient(135deg,#06131f,#13243d 60%,#282a5d);color:var(--text)}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:42px 42px;pointer-events:none;mask-image:linear-gradient(to bottom,rgba(0,0,0,.9),rgba(0,0,0,.06))}}a{{color:var(--cyan);text-decoration:none}}nav{{position:sticky;top:0;z-index:4;background:rgba(6,19,31,.9);border-bottom:1px solid var(--line);backdrop-filter:blur(14px);display:flex;justify-content:space-between;gap:18px;padding:14px 22px}}nav strong{{color:var(--cyan)}}nav div{{display:flex;gap:14px;flex-wrap:wrap}}nav a{{font-weight:850;color:var(--muted)}}main{{max-width:1240px;margin:0 auto;padding:44px 20px 80px;position:relative}}.hero{{display:grid;grid-template-columns:1.05fr .95fr;gap:22px;align-items:center}}.eyebrow{{color:var(--cyan);text-transform:uppercase;letter-spacing:.18em;font-weight:950;font-size:12px}}h1{{font-size:clamp(44px,7vw,100px);letter-spacing:-.08em;line-height:.86;margin:12px 0}}h2{{font-size:clamp(30px,4.6vw,60px);letter-spacing:-.055em;line-height:.95;margin:0 0 18px}}p{{color:var(--muted);line-height:1.55;font-size:18px}}.card{{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:28px;padding:24px;box-shadow:0 22px 80px rgba(0,0,0,.28)}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}}.metric{{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:18px}}.metric strong{{display:block;color:var(--green);font-size:32px;letter-spacing:-.04em}}.metric span{{color:var(--muted)}}.two{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:22px 0}}.section{{margin:34px 0}}.pill{{display:inline-flex;border-radius:999px;padding:7px 11px;background:rgba(125,255,176,.16);color:var(--green);font-size:12px;font-weight:950;text-transform:uppercase;letter-spacing:.08em}}.quote{{font-size:clamp(24px,3.2vw,44px);line-height:1.08;letter-spacing:-.04em;color:var(--text)}}.bar-row{{display:grid;grid-template-columns:245px 1fr 150px;align-items:center;gap:12px;margin:12px 0}}.bar-label,.bar-value{{color:var(--muted)}}.bar-track{{height:20px;background:rgba(255,255,255,.08);border-radius:999px;overflow:hidden}}.bar-fill{{height:100%;background:linear-gradient(90deg,var(--green),var(--cyan));border-radius:999px}}table{{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:18px;overflow:hidden}}th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}}tr:last-child td{{border-bottom:0}}.chart,.radar,.constellation{{width:100%;height:auto;background:rgba(0,0,0,.16);border:1px solid var(--line);border-radius:24px;padding:12px}}.chart line,.chart polyline{{stroke:var(--green);stroke-width:4;fill:none}}.chart line{{stroke:rgba(255,255,255,.16);stroke-width:1}}.chart circle{{fill:var(--green)}}.chart .area{{fill:rgba(125,255,176,.13);stroke:none}}.chart text,.radar text{{fill:var(--muted);font-size:12px}}.radar circle,.radar line{{fill:none;stroke:rgba(255,255,255,.14)}}.radar polygon{{fill:rgba(134,248,255,.19);stroke:var(--cyan);stroke-width:3}}.constellation line{{stroke:rgba(134,248,255,.095)}}.constellation circle{{fill:var(--cyan)}}.constellation .core{{fill:rgba(125,255,176,.12);stroke:var(--green)}}.core-text{{fill:var(--text);font-weight:950;font-size:22px}}.core-sub{{fill:var(--muted);font-size:13px}}.roles{{display:flex;flex-wrap:wrap;gap:8px}}.roles span{{border:1px solid var(--line);background:rgba(255,255,255,.05);border-radius:999px;padding:8px 10px;color:var(--muted);font-size:13px}}.notice{{border-left:4px solid var(--gold);background:rgba(255,214,107,.08);border-radius:16px;padding:16px 18px;color:var(--muted)}}.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}@media(max-width:900px){{.hero,.grid,.two{{grid-template-columns:1fr}}.bar-row{{grid-template-columns:1fr}}nav{{flex-direction:column}}}}
</style>
</head>
<body>
<nav><strong>SkillOS Enterprise Eureka Factory</strong><div><a href="index.html">Command Center</a><a href="proofs.html">Proofs</a><a href="multi-agent.html">Multi-Agent</a><a href="../data/rsi_enterprise_eureka_factory_proof.json">JSON</a><a href="../docs/rsi_enterprise_eureka_factory_proof.md">Report</a></div></nav>
<main>
<section class="hero">
  <div>
    <div class="eyebrow">MONTREAL.AI / SKILLOS</div>
    <h1>Enterprise Eureka Factory.</h1>
    <p>Autonomous proof that a large specialist-agent organization can recursively improve its coordination protocol and capture more benchmark enterprise value than a single agent, an uncoordinated multi-agent pool, static coordination, and negative controls.</p>
  </div>
  <div class="card">
    <span class="pill">proof passed</span>
    <div class="quote">{proof['agent_system']['agent_count']} agents. {proof['agent_system']['role_count']} roles. {proof['rsi_release_count']} RSI releases. {proof['benchmark_public']['holdout_count']} locked holdout cases.</div>
    <p>{esc(proof['safe_interpretation'])}</p>
  </div>
</section>

<section class="grid">
  <div class="metric"><strong>{final['benchmark_value_capture_rate_percent']}%</strong><span>benchmark value capture</span></div>
  <div class="metric"><strong>{money(final['total_benchmark_value_captured_usd'])}</strong><span>benchmark value captured</span></div>
  <div class="metric"><strong>{money(comparisons['vs_single_agent']['benchmark_value_captured_gain_usd'])}</strong><span>over single-agent baseline</span></div>
  <div class="metric"><strong>{final['risk_breach_rate_percent']}%</strong><span>risk breach rate</span></div>
</section>

<section class="section card">
  <div class="eyebrow">Kardashev-scale mechanism, enterprise proof</div>
  <div class="quote">capital → compute → energy → data → trust → talent → product → distribution → validation → risk control → reinvestment → compounding productive capability</div>
  <p>This does not claim achieved superintelligence or Kardashev Type II civilization. It makes the enterprise mechanism underneath the value thesis publicly testable and repeatable.</p>
</section>

<section class="two">
  <div class="card"><h2>RSI release curve</h2>{rsi_curve(proof['rsi_releases'])}</div>
  <div class="card"><h2>Capability radar</h2>{radar(final)}</div>
</section>

<section class="section">
  <h2>Baselines and controls</h2>
  <div class="card">
    {pct_bar('Single enterprise generalist', single['benchmark_value_capture_rate_percent'], str(single['benchmark_value_capture_rate_percent']) + '%')}
    {pct_bar('Uncoordinated multi-agent pool', pool['benchmark_value_capture_rate_percent'], str(pool['benchmark_value_capture_rate_percent']) + '%')}
    {pct_bar('Static multi-agent coordination', static['benchmark_value_capture_rate_percent'], str(static['benchmark_value_capture_rate_percent']) + '%')}
    {pct_bar('Shuffled-reward RSI control', shuffled['benchmark_value_capture_rate_percent'], str(shuffled['benchmark_value_capture_rate_percent']) + '%')}
    {pct_bar('Random protocol control', random_control['benchmark_value_capture_rate_percent'], str(random_control['benchmark_value_capture_rate_percent']) + '%')}
    {pct_bar('SkillOS RSI coordination', final['benchmark_value_capture_rate_percent'], str(final['benchmark_value_capture_rate_percent']) + '%')}
  </div>
</section>

<section class="section">
  <h2>Large specialist-agent organization</h2>
  <div class="card">{constellation(proof['agent_system']['roles'])}</div>
</section>

<section class="section">
  <h2>Pre-registered proof gates</h2>
  {gates_table(proof['pre_registered_gates'])}
</section>

<section class="section">
  <h2>Statistical check</h2>
  <table>
    <tr><th>Comparison</th><th>Mean gain</th><th>p05</th><th>p50</th><th>p95</th><th>Bootstrap reps</th></tr>
    <tr><td>vs single agent</td><td>{proof['bootstrap_confidence_intervals']['vs_single_agent']['mean_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_single_agent']['p05_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_single_agent']['p50_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_single_agent']['p95_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_single_agent']['bootstrap_repetitions']}</td></tr>
    <tr><td>vs uncoordinated pool</td><td>{proof['bootstrap_confidence_intervals']['vs_uncoordinated_multi_agent_pool']['mean_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_uncoordinated_multi_agent_pool']['p05_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_uncoordinated_multi_agent_pool']['p50_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_uncoordinated_multi_agent_pool']['p95_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_uncoordinated_multi_agent_pool']['bootstrap_repetitions']}</td></tr>
    <tr><td>vs static coordination</td><td>{proof['bootstrap_confidence_intervals']['vs_static_multi_agent_coordination']['mean_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_static_multi_agent_coordination']['p05_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_static_multi_agent_coordination']['p50_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_static_multi_agent_coordination']['p95_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_static_multi_agent_coordination']['bootstrap_repetitions']}</td></tr>
  </table>
</section>

<section class="section">
  <h2>RSI protocol releases</h2>
  <table><tr><th>Generation</th><th>Status</th><th>Lesson</th><th>Validation value capture</th><th>Fully correct</th><th>Risk breach</th><th>Score</th></tr>{release_rows}</table>
</section>

<section class="section">
  <h2>Holdout samples</h2>
  <table><tr><th>Case</th><th>Chosen</th><th>Oracle</th><th>Match</th><th>Chosen value</th><th>Oracle value</th><th>Risk load</th><th>Compounding</th></tr>{sample_rows}</table>
</section>

<section class="section card">
  <h2>Specialist roles</h2>
  <div class="roles">{role_chips}</div>
</section>

<section class="notice">
  <strong>Public boundary:</strong> benchmark proof values are not audited customer revenue, investment advice, financial advice, live customer adoption, achieved superintelligence, or Kardashev Type II achievement. Protocol fingerprint: <span class="mono">{esc(proof['protocol_fingerprint_sha256'])}</span>.
</section>
</main>
</body>
</html>
"""
    page = SITE / "rsi-enterprise-eureka-factory-proof.html"
    page.write_text(html_text, encoding="utf-8")

    print(json.dumps({
        "status": "VISIBLE_OUTPUTS_WRITTEN",
        "html": str(page.relative_to(ROOT)),
        "badge": "badges/rsi_enterprise_eureka_factory_proof.svg",
        "json": "data/rsi_enterprise_eureka_factory_proof.json",
        "markdown": "docs/rsi_enterprise_eureka_factory_proof.md",
    }, indent=2))


if __name__ == "__main__":
    main()
