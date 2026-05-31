#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import math
from pathlib import Path
from typing import Any

PROOF_ID = "rsi-open-replication-mesh-proof"
TITLE = "Autonomous RSI Open Replication Mesh Proof"
SITE_BASE_URL = "https://montrealai.github.io/skillos/"


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def pct(value: float, digits: int = 2) -> str:
    return f"{100.0 * float(value):.{digits}f}%"


def money_t(value: float) -> str:
    return f"${float(value):,.2f}T"


def fail(message: str) -> None:
    raise SystemExit(f"render failed: {message}")


def svg_release_curve(curve: list[dict[str, Any]]) -> str:
    width, height = 720, 260
    pad = 38
    vals = [float(x["validation_value_capture"]) for x in curve]
    lo = min(vals) * 0.985
    hi = max(vals) * 1.005
    pts = []
    for i, v in enumerate(vals):
        x = pad + i * ((width - 2*pad) / max(1, len(vals)-1))
        y = height - pad - ((v - lo) / max(1e-9, hi - lo)) * (height - 2*pad)
        pts.append((x, y))
    line = " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)
    dots = "".join(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='4' fill='#72ffb6'/>" for x, y in pts)
    labels = "".join(f"<text x='{x:.2f}' y='{height-10}' text-anchor='middle' fill='#b7c7dc' font-size='10'>v{i}</text>" for i, (x, _) in enumerate(pts) if i % 3 == 0 or i == len(pts)-1)
    return f"""<svg viewBox='0 0 {width} {height}' class='chart' role='img' aria-label='RSI release curve'>
      <rect width='{width}' height='{height}' rx='18' fill='rgba(0,0,0,.16)'/>
      <line x1='{pad}' y1='{height-pad}' x2='{width-pad}' y2='{height-pad}' stroke='rgba(255,255,255,.18)'/>
      <line x1='{pad}' y1='{pad}' x2='{pad}' y2='{height-pad}' stroke='rgba(255,255,255,.18)'/>
      <polyline points='{line}' fill='none' stroke='#72ffb6' stroke-width='4'/>{dots}{labels}
    </svg>"""


def svg_arm_bars(arms: dict[str, dict[str, Any]]) -> str:
    width, height = 760, 320
    labels = list(arms.keys())
    vals = [float(arms[a]["weighted_value_capture"]) for a in labels]
    max_v = max(vals) or 1.0
    row_h = 34
    out = [f"<svg viewBox='0 0 {width} {height}' class='chart' role='img' aria-label='Counterfactual arm comparison'>"]
    out.append(f"<rect width='{width}' height='{height}' rx='18' fill='rgba(0,0,0,.16)'/>")
    for i, (label, val) in enumerate(zip(labels, vals)):
        y = 25 + i * row_h
        bar_w = 430 * val / max_v
        color = '#72ffb6' if label == 'skillos_open_replication_mesh' else '#8df5ff'
        out.append(f"<text x='18' y='{y+15}' fill='#dcecff' font-size='13'>{esc(label.replace('_',' '))}</text>")
        out.append(f"<rect x='260' y='{y}' width='{bar_w:.2f}' height='18' rx='9' fill='{color}' opacity='.84'/>")
        out.append(f"<text x='{270+bar_w:.2f}' y='{y+15}' fill='#fff' font-size='12' font-weight='700'>{pct(val,1)}</text>")
    out.append("</svg>")
    return "".join(out)


def svg_replica_band(replica: dict[str, Any]) -> str:
    receipts = replica.get("sample_replica_receipts", [])
    vals = [float(x.get("weighted_value_capture", 0)) for x in receipts]
    width, height = 720, 220
    pad = 34
    if not vals:
        return ""
    lo, hi = min(vals)*0.999, max(vals)*1.001
    dots = []
    for i, v in enumerate(vals):
        x = pad + i * ((width - 2*pad) / max(1, len(vals)-1))
        y = height - pad - ((v - lo) / max(1e-9, hi-lo)) * (height - 2*pad)
        dots.append(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='7' fill='#8df5ff' opacity='.88'/>")
    mean = float(replica.get("mean_value_capture", 0))
    return f"""<svg viewBox='0 0 {width} {height}' class='chart' role='img' aria-label='Replica convergence band'>
      <rect width='{width}' height='{height}' rx='18' fill='rgba(0,0,0,.16)'/>
      <text x='20' y='28' fill='#8df5ff' font-size='13' font-weight='900'>Sample replica receipts converge near {pct(mean,3)}</text>
      <line x1='{pad}' y1='{height/2:.2f}' x2='{width-pad}' y2='{height/2:.2f}' stroke='rgba(114,255,182,.45)' stroke-width='3'/>
      {''.join(dots)}
    </svg>"""


def svg_radar(metrics: dict[str, Any]) -> str:
    values = [
        ("Replication", float(metrics["open_replication_score"])),
        ("Consensus", float(metrics["replica_consensus_rate"])),
        ("Value capture", float(metrics["locked_holdout_value_capture"])),
        ("Causal lift", min(1.0, float(metrics["causal_uplift_vs_best_control"]) / 0.20)),
        ("Replayability", float(metrics["trace_replayability"])),
        ("Risk control", 1.0 - float(metrics["risk_breach_rate"])),
    ]
    cx, cy, r = 170, 170, 112
    pts=[]; labels=[]; spokes=[]
    for i,(name,val) in enumerate(values):
        angle = -math.pi/2 + i*2*math.pi/len(values)
        x = cx + r*val*math.cos(angle); y = cy + r*val*math.sin(angle)
        sx = cx + r*math.cos(angle); sy = cy + r*math.sin(angle)
        lx = cx + (r+32)*math.cos(angle); ly = cy + (r+32)*math.sin(angle)
        pts.append(f"{x:.2f},{y:.2f}")
        spokes.append(f"<line x1='{cx}' y1='{cy}' x2='{sx:.2f}' y2='{sy:.2f}' stroke='rgba(255,255,255,.16)'/>")
        labels.append(f"<text x='{lx:.2f}' y='{ly:.2f}' text-anchor='middle' fill='#dcecff' font-size='11'>{esc(name)}</text>")
    rings=''.join(f"<circle cx='{cx}' cy='{cy}' r='{r*k/4:.2f}' fill='none' stroke='rgba(255,255,255,.13)'/>" for k in range(1,5))
    return f"<svg viewBox='0 0 340 340' class='chart radar' role='img' aria-label='Replication proof radar'>{rings}{''.join(spokes)}<polygon points='{' '.join(pts)}' fill='rgba(141,245,255,.25)' stroke='#8df5ff' stroke-width='3'/>{''.join(labels)}</svg>"


def render(proof: dict[str, Any]) -> str:
    m = proof["metrics"]
    scale = proof["scale"]
    replica = proof["replica_summary"]
    release_curve = svg_release_curve(proof["release_curve"])
    bars = svg_arm_bars(proof["arms_summary"])
    band = svg_replica_band(replica)
    radar = svg_radar(m)
    sample_cases = "".join(
        f"<tr><td>{esc(row['case_id'])}</td><td>{esc(row['domain'])}</td><td>{money_t(row['benchmark_capital_equivalent_value_trillions'])}</td><td>{esc(', '.join(row['capability_atoms']))}</td></tr>"
        for row in proof.get("sample_locked_holdout_cases", [])[:10]
    )
    receipts = "".join(
        f"<tr><td>{esc(row['replica_id'])}</td><td>{pct(float(row['weighted_value_capture']),3)}</td><td>{esc(row['environment_fingerprint'])}</td><td><code>{esc(row['receipt_sha256'][:18])}…</code></td></tr>"
        for row in replica.get("sample_replica_receipts", [])[:10]
    )
    gates = "".join(f"<li><span class='ok'>✓</span>{esc(name.replace('_',' '))}</li>" for name, ok in proof.get("gates", {}).items() if ok)
    neg_rows = "".join(f"<tr><td>{esc(k.replace('_',' '))}</td><td>{pct(abs(float(v)),3)}</td></tr>" for k, v in proof.get("negative_controls", {}).items())
    root = replica.get("receipt_tree", {}).get("root", "")
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<meta name='viewport' content='width=device-width,initial-scale=1'/>
<title>{esc(TITLE)}</title>
<meta name='description' content='Autonomous SkillOS proof that the RSI proof layer survives open replication and signed receipt replay.' />
<style>
:root{{--bg:#071827;--ink:#eef8ff;--muted:#b7c7dc;--line:rgba(255,255,255,.15);--cyan:#8df5ff;--green:#72ffb6;--violet:#9b8cff;--gold:#ffd86b;--rose:#ff8ea3}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at 18% 0%,rgba(141,245,255,.19),transparent 30%),radial-gradient(circle at 84% 8%,rgba(155,140,255,.20),transparent 34%),linear-gradient(135deg,#071827 0%,#0d1b34 55%,#15143a 100%);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.45}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:34px 34px;pointer-events:none;mask-image:linear-gradient(to bottom,black,transparent 86%)}}a{{color:var(--cyan);font-weight:900;text-decoration:none}}nav{{position:sticky;top:0;z-index:10;display:flex;justify-content:space-between;gap:18px;padding:14px 20px;background:rgba(4,15,26,.88);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}}nav span{{display:flex;gap:16px;flex-wrap:wrap}}main{{width:min(1200px,92vw);margin:auto;padding:54px 0 90px}}.hero,.panel,.metric,.callout{{background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:28px;box-shadow:0 28px 90px rgba(0,0,0,.24);backdrop-filter:blur(10px)}}.hero{{padding:38px}}.eyebrow{{color:var(--cyan);letter-spacing:.22em;text-transform:uppercase;font-weight:950;font-size:12px}}h1{{font-size:clamp(42px,7vw,90px);line-height:.89;letter-spacing:-.075em;margin:16px 0}}h2{{font-size:clamp(30px,4.4vw,58px);line-height:1;letter-spacing:-.06em;margin:54px 0 18px}}h3{{font-size:24px;margin:0 0 10px}}p{{color:var(--muted)}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0}}.metric{{padding:18px}}.metric b{{display:block;color:var(--green);font-size:clamp(25px,3vw,38px);letter-spacing:-.04em}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.panel{{padding:22px;overflow:hidden}}.chart{{width:100%;height:auto;display:block}}.pill{{display:inline-flex;border-radius:999px;padding:7px 10px;background:rgba(114,255,182,.16);color:var(--green);font-weight:950;font-size:12px;text-transform:uppercase}}.button{{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:12px 16px;background:var(--cyan);color:#071827;font-weight:950}}.button.secondary{{background:transparent;color:var(--ink);border:1px solid var(--line)}}.links{{display:flex;gap:12px;flex-wrap:wrap;margin-top:20px}}.callout{{padding:26px;margin:24px 0}}.mechanism{{font-size:clamp(24px,4vw,44px);line-height:1.1;letter-spacing:-.055em;color:#fff}}table{{width:100%;border-collapse:collapse;background:rgba(255,255,255,.055);border-radius:18px;overflow:hidden}}th,td{{padding:13px;border-bottom:1px solid var(--line);text-align:left;color:#dcecff;vertical-align:top}}th{{color:#8df5ff;font-size:12px;text-transform:uppercase;letter-spacing:.14em}}.ok{{color:var(--green);font-weight:950;margin-right:8px}}ul.gates{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;padding:0;list-style:none}}.safe{{border-left:4px solid var(--gold);padding-left:16px;color:#ffeeb0}}code{{color:#8df5ff}}@media(max-width:880px){{.grid,.metrics{{grid-template-columns:1fr}}nav{{position:static}}ul.gates{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<nav><strong><a href='index.html'>SkillOS Proof Command Center</a></strong><span><a href='#replication'>Replication</a><a href='proof-registry.json'>Registry</a><a href='https://github.com/MontrealAI/skillos/actions'>Run on GitHub</a><a href='https://github.com/MontrealAI/skillos'>GitHub</a></span></nav>
<main>
  <section class='hero'>
    <span class='pill'>Proof passed</span>
    <div class='eyebrow'>Open replication proof • signed receipts • Merkle receipt tree</div>
    <h1>Can the world replay the proof?</h1>
    <p><strong>{esc(TITLE)}</strong> turns the SkillOS proof system into a public instrument: independent replica cells replay locked cases, emit signed receipts, converge under verifier courts, and publish a receipt tree that anyone can regenerate through GitHub Actions.</p>
    <div class='metrics'>
      <div class='metric'><b>{pct(m['open_replication_score'])}</b><span>open replication score</span></div>
      <div class='metric'><b>{pct(m['replica_consensus_rate'])}</b><span>replica consensus</span></div>
      <div class='metric'><b>{pct(m['locked_holdout_value_capture'])}</b><span>holdout value capture</span></div>
      <div class='metric'><b>+{pct(m['causal_uplift_vs_best_control'])}</b><span>uplift vs strongest control</span></div>
    </div>
    <div class='links'><a class='button' href='data/{PROOF_ID}.json'>Inspect JSON receipt</a><a class='button secondary' href='docs/{PROOF_ID}.md'>Read report</a><a class='button secondary' href='https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-open-replication-mesh-proof.yml'>Run / regenerate</a></div>
  </section>

  <section class='callout'>
    <div class='eyebrow'>Mechanism under test</div>
    <div class='mechanism'>{esc(proof['mechanism'])}</div>
    <p class='safe'>{esc(proof['public_claim_boundary'])}</p>
  </section>

  <section class='metrics'>
    <div class='metric'><b>{scale['virtual_specialist_agents']:,}</b><span>virtual specialist agents</span></div>
    <div class='metric'><b>{scale['specialist_roles']:,}</b><span>specialist roles</span></div>
    <div class='metric'><b>{scale['replication_cells']:,}</b><span>replication cells</span></div>
    <div class='metric'><b>{scale['locked_holdout_cases']:,}</b><span>locked holdout cases</span></div>
  </section>

  <section class='grid'>
    <article class='panel'><h3>RSI release curve</h3><p>Validation-selected releases are frozen before locked holdout replay.</p>{release_curve}</article>
    <article class='panel'><h3>Replication proof radar</h3><p>The proof rewards value capture, consensus, replayability, receipt integrity, causal lift, and risk control.</p>{radar}</article>
  </section>

  <section class='grid' id='replication' style='margin-top:18px'>
    <article class='panel'><h3>Replica convergence band</h3><p>Sample replica receipts converge to the same public result.</p>{band}</article>
    <article class='panel'><h3>Receipt tree</h3><p>Replica receipts are compressed into a public root for deterministic replay.</p><table><tbody><tr><th>Leaves</th><td>{replica.get('receipt_tree',{}).get('leaf_count')}</td></tr><tr><th>Levels</th><td>{replica.get('receipt_tree',{}).get('levels')}</td></tr><tr><th>Root</th><td><code>{esc(root)}</code></td></tr></tbody></table></article>
  </section>

  <section class='panel' style='margin-top:18px'><h3>Counterfactual arms</h3><p>Every arm sees the same locked cases. SkillOS full replication must beat the strongest non-SkillOS control while remaining risk-zero.</p>{bars}</section>

  <section class='grid' style='margin-top:18px'>
    <article class='panel'><h3>Signed sample receipts</h3><table><thead><tr><th>Replica</th><th>Value capture</th><th>Environment</th><th>Receipt</th></tr></thead><tbody>{receipts}</tbody></table></article>
    <article class='panel'><h3>Negative controls</h3><table><thead><tr><th>Control</th><th>Absolute effect</th></tr></thead><tbody>{neg_rows}</tbody></table></article>
  </section>

  <section class='grid' style='margin-top:18px'>
    <article class='panel'><h3>Pre-registered gates</h3><ul class='gates'>{gates}</ul></article>
    <article class='panel'><h3>Interpretation</h3><p>{esc(proof['thesis'])}</p><p>Benchmark-capital-equivalent gain over strongest control: <strong>{money_t(m['benchmark_capital_equivalent_gain_vs_best_control_trillions'])}</strong>.</p></article>
  </section>

  <section class='panel' style='margin-top:18px'><h3>Sample locked holdout cases</h3><table><thead><tr><th>Case</th><th>Domain</th><th>Value at stake</th><th>Capability atoms</th></tr></thead><tbody>{sample_cases}</tbody></table></section>
</main>
</body>
</html>"""


def main() -> None:
    root = Path.cwd()
    path = root / "data" / f"{PROOF_ID}.json"
    if not path.exists():
        fail(f"missing proof JSON: {path}")
    proof = json.loads(path.read_text(encoding="utf-8"))
    if proof.get("proof_id") != PROOF_ID:
        fail("proof_id mismatch")
    if not proof.get("proved"):
        fail("proof is not passed")
    site = root / "site"
    site.mkdir(parents=True, exist_ok=True)
    page = site / f"{PROOF_ID}.html"
    page.write_text(render(proof), encoding="utf-8")
    print(json.dumps({"rendered": True, "page": str(page), "url": SITE_BASE_URL + page.name}, indent=2))


if __name__ == "__main__":
    main()
