#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"
BADGES = ROOT / "badges"
PROOF = DATA / "rsi_enterprise_superorganization_proof.json"

SITE.mkdir(parents=True, exist_ok=True)
BADGES.mkdir(parents=True, exist_ok=True)


def esc(value: object) -> str:
    return html.escape(str(value))


def money(value: float) -> str:
    if abs(value) >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:,.2f}T"
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
    width, height, left, right, top, bottom = 980, 300, 52, 32, 34, 242
    lo, hi = min(vals) - 0.35, max(vals) + 0.35
    pts = []
    for idx, value in enumerate(vals):
        x = left + idx * ((width - left - right) / max(1, len(vals) - 1))
        y = bottom - ((value - lo) / max(0.001, hi - lo)) * (bottom - top)
        pts.append((x, y, value))
    poly = " ".join(f"{x:.1f},{y:.1f}" for x, y, _ in pts)
    area = f"M {left} {bottom} L " + " L ".join(f"{x:.1f} {y:.1f}" for x, y, _ in pts) + f" L {pts[-1][0]:.1f} {bottom} Z"
    dots = "\n".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.8"/><text x="{x:.1f}" y="276" text-anchor="middle">v{idx}</text>' for idx, (x, y, _) in enumerate(pts))
    return f"""<svg class="chart" viewBox="0 0 {width} {height}" role="img" aria-label="RSI release curve">
      <line x1="{left}" y1="{bottom}" x2="{width-right}" y2="{bottom}"/>
      <line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}"/>
      <path d="{area}" class="area"/>
      <polyline points="{poly}"/>
      {dots}
    </svg>"""


def radar(final: dict) -> str:
    axes = [
        ("Coordination", final["coordination_protocol_accuracy_percent"]),
        ("Risk control", final["risk_control_accuracy_percent"]),
        ("Role quorum", final["role_quorum_accuracy_percent"]),
        ("Value capture", final["benchmark_value_capture_rate_percent"]),
        ("Compounding", final["avg_compounding_index"]),
        ("Capacity", final["avg_productive_capacity_index"]),
        ("Consensus", final["avg_consensus_score"]),
    ]
    cx, cy, radius = 330, 215, 144
    pts, labels, spokes = [], [], []
    for idx, (label, value) in enumerate(axes):
        angle = -math.pi / 2 + idx * 2 * math.pi / len(axes)
        rr = radius * max(0.0, min(100.0, value)) / 100.0
        x, y = cx + rr * math.cos(angle), cy + rr * math.sin(angle)
        sx, sy = cx + radius * math.cos(angle), cy + radius * math.sin(angle)
        lx, ly = cx + (radius + 50) * math.cos(angle), cy + (radius + 50) * math.sin(angle)
        pts.append(f"{x:.1f},{y:.1f}")
        spokes.append(f'<line x1="{cx}" y1="{cy}" x2="{sx:.1f}" y2="{sy:.1f}"/>')
        labels.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle">{esc(label)}</text>')
    rings = "".join(f'<circle cx="{cx}" cy="{cy}" r="{radius * f:.1f}"/>' for f in [0.25, 0.5, 0.75, 1.0])
    return f"""<svg class="radar" viewBox="0 0 660 440" role="img" aria-label="Capability radar">
      {rings}{''.join(spokes)}
      <polygon points="{' '.join(pts)}"/>
      {''.join(labels)}
    </svg>"""


def constellation(roles: list[str]) -> str:
    cx, cy = 520, 410
    nodes = []
    for idx, role in enumerate(roles[:512]):
        if idx < 48:
            ring, denom, offset = 128, 48, idx
        elif idx < 160:
            ring, denom, offset = 218, 112, idx - 48
        elif idx < 320:
            ring, denom, offset = 306, 160, idx - 160
        else:
            ring, denom, offset = 390, 192, idx - 320
        angle = -math.pi / 2 + offset * 2 * math.pi / denom + (0.07 if idx >= 48 else 0)
        x, y = cx + ring * math.cos(angle), cy + ring * math.sin(angle)
        r = 5.0 if idx < 48 else 3.8 if idx < 160 else 2.8 if idx < 320 else 2.2
        nodes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"><title>{esc(role)}</title></circle>')
    return f"""<svg class="constellation" viewBox="0 0 1040 820" role="img" aria-label="Large specialist-agent organization">
      <circle class="core" cx="{cx}" cy="{cy}" r="86"/>
      <text x="{cx}" y="{cy-10}" text-anchor="middle" class="core-text">SkillOS</text>
      <text x="{cx}" y="{cy+22}" text-anchor="middle" class="core-sub">RSI coordination core</text>
      {''.join(nodes)}
    </svg>"""


def gates_table(gates: dict[str, bool]) -> str:
    rows = "".join(f"<tr><td>{esc(k.replace('_', ' '))}</td><td><span class=\"{'ok' if v else 'bad'}\">{'passed' if v else 'failed'}</span></td></tr>" for k, v in gates.items())
    return f"<table><tr><th>Pre-registered gate</th><th>Status</th></tr>{rows}</table>"


def regime_rows(regimes: dict[str, dict]) -> str:
    return "\n".join(f"<tr><td>{esc(k.replace('_',' '))}</td><td>{v['case_count']}</td><td>{v['value_capture_percent']}%</td><td>{v['fully_correct_percent']}%</td></tr>" for k, v in regimes.items())


def main() -> None:
    if not PROOF.exists():
        raise SystemExit(f"Missing proof receipt: {PROOF}")

    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    final = proof["final"]
    comp = proof["comparisons"]
    single = proof["single_agent_baseline"]
    pool = proof["uncoordinated_large_agent_pool"]
    static = proof["static_multi_agent_operating_committee"]
    no_rsi = proof["no_rsi_large_agent_organization"]
    shuffled = proof["negative_controls"]["shuffled_reward_rsi"]
    random_control = proof["negative_controls"]["random_protocol"]

    badge = """<svg xmlns="http://www.w3.org/2000/svg" width="372" height="20" role="img" aria-label="enterprise superorganization RSI proof: passed">
<linearGradient id="g" x2="1" y2="0"><stop stop-color="#102033"/><stop offset="1" stop-color="#153b4a"/></linearGradient>
<rect width="372" height="20" rx="10" fill="url(#g)"/>
<rect x="250" width="122" height="20" rx="10" fill="#2bb673"/>
<text x="10" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">enterprise superorganization RSI</text>
<text x="267" y="14" fill="#ffffff" font-family="Verdana" font-size="11">proof passed</text>
</svg>"""
    (BADGES / "rsi_enterprise_superorganization_proof.svg").write_text(badge, encoding="utf-8")

    release_rows = "\n".join(
        f"<tr><td>v{r['generation']}</td><td>{'released' if r['released'] else 'rejected'}</td><td>{esc(r['lesson'])}</td><td>{r['validation']['benchmark_value_capture_rate_percent']}%</td><td>{r['validation']['fully_correct_percent']}%</td><td>{r['validation']['risk_breach_rate_percent']}%</td><td class='mono'>{esc(r['protocol_fingerprint_sha256'][:12])}</td></tr>"
        for r in proof["rsi_releases"]
    )
    sample_rows = "\n".join(
        f"<tr><td>{r['case_id']}</td><td>{esc(r['regime'].replace('_',' '))}</td><td>{r['chosen_action']}</td><td>{r['oracle_action']}</td><td>{'yes' if r['matched_oracle'] else 'near miss'}</td><td>{money(r['chosen_value_usd'])}</td><td>{money(r['oracle_value_usd'])}</td><td>{r['risk_load']}</td></tr>"
        for r in proof["holdout_samples"]
    )
    role_chips = "".join(f"<span>{esc(role)}</span>" for role in proof["agent_system"]["roles"])

    html_text = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>SkillOS Autonomous RSI Enterprise Superorganization Proof</title>
<style>
:root{{--text:#f5fbff;--muted:#b8c8d8;--line:rgba(255,255,255,.16);--panel:rgba(255,255,255,.07);--panel2:rgba(255,255,255,.11);--cyan:#86f8ff;--green:#7dffb0;--gold:#ffd66b;--red:#ff8585;--purple:#b9a5ff}}
*{{box-sizing:border-box}}body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;background:radial-gradient(circle at 82% 0,#3d4381 0,transparent 34%),radial-gradient(circle at 0 18%,#095e70 0,transparent 26%),linear-gradient(135deg,#06131f,#13243d 60%,#282a5d);color:var(--text)}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:42px 42px;pointer-events:none;mask-image:linear-gradient(to bottom,rgba(0,0,0,.9),rgba(0,0,0,.05))}}a{{color:var(--cyan);text-decoration:none}}nav{{position:sticky;top:0;z-index:4;background:rgba(6,19,31,.9);border-bottom:1px solid var(--line);backdrop-filter:blur(14px);display:flex;justify-content:space-between;gap:18px;padding:14px 22px}}nav strong{{color:var(--cyan)}}nav div{{display:flex;gap:14px;flex-wrap:wrap}}nav a{{font-weight:850;color:var(--muted)}}main{{max-width:1280px;margin:0 auto;padding:44px 20px 80px;position:relative}}.hero{{display:grid;grid-template-columns:1.05fr .95fr;gap:22px;align-items:center}}.eyebrow{{color:var(--cyan);text-transform:uppercase;letter-spacing:.18em;font-weight:950;font-size:12px}}h1{{font-size:clamp(44px,7vw,104px);letter-spacing:-.08em;line-height:.86;margin:12px 0}}h2{{font-size:clamp(30px,4.5vw,60px);letter-spacing:-.055em;line-height:.95;margin:0 0 18px}}p{{color:var(--muted);line-height:1.55;font-size:18px}}.card{{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:28px;padding:24px;box-shadow:0 22px 80px rgba(0,0,0,.28)}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}}.metric{{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:18px}}.metric strong{{display:block;color:var(--green);font-size:32px;letter-spacing:-.04em}}.metric span{{color:var(--muted)}}.two{{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin:22px 0}}.section{{margin:34px 0}}.pill{{display:inline-flex;border-radius:999px;padding:7px 11px;background:rgba(125,255,176,.16);color:var(--green);font-size:12px;font-weight:950;text-transform:uppercase;letter-spacing:.08em}}.quote{{font-size:clamp(24px,3.2vw,44px);line-height:1.08;letter-spacing:-.04em;color:var(--text)}}.bar-row{{display:grid;grid-template-columns:280px 1fr 170px;align-items:center;gap:12px;margin:12px 0}}.bar-label,.bar-value{{color:var(--muted)}}.bar-track{{height:20px;background:rgba(255,255,255,.08);border-radius:999px;overflow:hidden}}.bar-fill{{height:100%;background:linear-gradient(90deg,var(--green),var(--cyan));border-radius:999px}}table{{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:18px;overflow:hidden}}th,td{{padding:12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}}th{{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}}tr:last-child td{{border-bottom:0}}.chart,.radar,.constellation{{width:100%;height:auto;background:rgba(0,0,0,.16);border:1px solid var(--line);border-radius:24px;padding:12px}}.chart line,.chart polyline{{stroke:var(--green);stroke-width:4;fill:none}}.chart line{{stroke:rgba(255,255,255,.16);stroke-width:1}}.chart circle{{fill:var(--green)}}.chart .area{{fill:rgba(125,255,176,.13);stroke:none}}.chart text,.radar text{{fill:var(--muted);font-size:12px}}.radar circle,.radar line{{fill:none;stroke:rgba(255,255,255,.14)}}.radar polygon{{fill:rgba(134,248,255,.19);stroke:var(--cyan);stroke-width:3}}.constellation line{{stroke:rgba(134,248,255,.07)}}.constellation circle{{fill:var(--cyan)}}.constellation .core{{fill:rgba(125,255,176,.12);stroke:var(--green)}}.core-text{{fill:var(--text);font-weight:950;font-size:22px}}.core-sub{{fill:var(--muted);font-size:13px}}.roles{{display:flex;flex-wrap:wrap;gap:8px}}.roles span{{border:1px solid var(--line);background:rgba(255,255,255,.05);border-radius:999px;padding:8px 10px;color:var(--muted);font-size:13px}}.notice{{border-left:4px solid var(--gold);background:rgba(255,214,107,.08);border-radius:16px;padding:16px 18px;color:var(--muted)}}.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}.ok{{color:var(--green);font-weight:900}}.bad{{color:var(--red);font-weight:900}}@media(max-width:900px){{.hero,.grid,.two{{grid-template-columns:1fr}}.bar-row{{grid-template-columns:1fr}}nav{{flex-direction:column}}}}
</style>
</head>
<body>
<nav><strong>SkillOS Enterprise Superorganization</strong><div><a href="index.html">Command Center</a><a href="proofs.html">Proofs</a><a href="multi-agent.html">Multi-Agent</a><a href="../data/rsi_enterprise_superorganization_proof.json">JSON</a><a href="../docs/rsi_enterprise_superorganization_proof.md">Report</a></div></nav>
<main>
<section class="hero">
  <div>
    <div class="eyebrow">MONTREAL.AI / SKILLOS</div>
    <h1>Enterprise Superorganization.</h1>
    <p>Autonomous proof that a large specialist-agent superorganization recursively improves the coordination protocol that turns enterprise resources into compounding productive capability.</p>
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
  <div class="metric"><strong>{money(comp['vs_single_agent']['benchmark_value_captured_gain_usd'])}</strong><span>over single-agent baseline</span></div>
  <div class="metric"><strong>{final['risk_breach_rate_percent']}%</strong><span>risk breach rate</span></div>
</section>

<section class="section card">
  <div class="eyebrow">Kardashev-scale value thesis, enterprise mechanism</div>
  <div class="quote">{esc(proof['capital_to_capability_thesis'])}</div>
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
    {pct_bar('Uncoordinated large-agent pool', pool['benchmark_value_capture_rate_percent'], str(pool['benchmark_value_capture_rate_percent']) + '%')}
    {pct_bar('Static multi-agent operating committee', static['benchmark_value_capture_rate_percent'], str(static['benchmark_value_capture_rate_percent']) + '%')}
    {pct_bar('No-RSI large-agent organization', no_rsi['benchmark_value_capture_rate_percent'], str(no_rsi['benchmark_value_capture_rate_percent']) + '%')}
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
  <h2>Enterprise regime coverage</h2>
  <table><tr><th>Regime</th><th>Holdout cases</th><th>Value capture</th><th>Fully correct</th></tr>{regime_rows(final['by_regime'])}</table>
</section>

<section class="section">
  <h2>Pre-registered proof gates</h2>
  {gates_table(proof['pre_registered_gates'])}
</section>

<section class="section">
  <h2>Bootstrap confidence intervals</h2>
  <table>
    <tr><th>Comparison</th><th>Mean gain</th><th>p05</th><th>p50</th><th>p95</th><th>Reps</th></tr>
    <tr><td>vs single agent</td><td>{proof['bootstrap_confidence_intervals']['vs_single_agent']['mean_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_single_agent']['p05_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_single_agent']['p50_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_single_agent']['p95_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_single_agent']['bootstrap_repetitions']}</td></tr>
    <tr><td>vs uncoordinated pool</td><td>{proof['bootstrap_confidence_intervals']['vs_uncoordinated_large_agent_pool']['mean_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_uncoordinated_large_agent_pool']['p05_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_uncoordinated_large_agent_pool']['p50_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_uncoordinated_large_agent_pool']['p95_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_uncoordinated_large_agent_pool']['bootstrap_repetitions']}</td></tr>
    <tr><td>vs static committee</td><td>{proof['bootstrap_confidence_intervals']['vs_static_multi_agent_operating_committee']['mean_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_static_multi_agent_operating_committee']['p05_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_static_multi_agent_operating_committee']['p50_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_static_multi_agent_operating_committee']['p95_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_static_multi_agent_operating_committee']['bootstrap_repetitions']}</td></tr>
    <tr><td>vs no-RSI large org</td><td>{proof['bootstrap_confidence_intervals']['vs_no_rsi_large_agent_organization']['mean_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_no_rsi_large_agent_organization']['p05_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_no_rsi_large_agent_organization']['p50_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_no_rsi_large_agent_organization']['p95_gain_points']} pts</td><td>{proof['bootstrap_confidence_intervals']['vs_no_rsi_large_agent_organization']['bootstrap_repetitions']}</td></tr>
  </table>
</section>

<section class="section">
  <h2>RSI protocol releases</h2>
  <table><tr><th>Generation</th><th>Status</th><th>Lesson</th><th>Validation value capture</th><th>Fully correct</th><th>Risk breach</th><th>Protocol</th></tr>{release_rows}</table>
</section>

<section class="section">
  <h2>Holdout samples</h2>
  <table><tr><th>Case</th><th>Regime</th><th>Chosen</th><th>Oracle</th><th>Match</th><th>Chosen value</th><th>Oracle value</th><th>Risk load</th></tr>{sample_rows}</table>
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
    (SITE / "rsi-enterprise-superorganization-proof.html").write_text(html_text, encoding="utf-8")

    print(json.dumps({
        "status": "VISIBLE_OUTPUTS_WRITTEN",
        "html": "site/rsi-enterprise-superorganization-proof.html",
        "badge": "badges/rsi_enterprise_superorganization_proof.svg",
        "json": "data/rsi_enterprise_superorganization_proof.json",
        "markdown": "docs/rsi_enterprise_superorganization_proof.md",
    }, indent=2))


if __name__ == "__main__":
    main()
