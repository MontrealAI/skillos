#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

PROOF_ID = "rsi-causal-attribution-engine-proof"
TITLE = "Autonomous RSI Causal Attribution Engine Proof"
SITE_BASE_URL = "https://montrealai.github.io/skillos/"


def fail(message: str) -> None:
    raise SystemExit(f"render failed: {message}")


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def pct(value: float, digits: int = 1) -> str:
    return f"{100 * float(value):.{digits}f}%"


def money_t(value: float) -> str:
    return f"${float(value):,.2f}T"


def svg_release_curve(curve: list[dict[str, Any]]) -> str:
    width, height = 720, 260
    pad_l, pad_r, pad_t, pad_b = 48, 24, 24, 42
    vals = [float(x["validation_value_capture"]) for x in curve]
    lo = min(vals) * 0.995
    hi = max(vals) * 1.002
    if hi <= lo:
        hi = lo + 1
    points = []
    for i, val in enumerate(vals):
        x = pad_l + i * (width - pad_l - pad_r) / max(1, len(vals) - 1)
        y = pad_t + (hi - val) * (height - pad_t - pad_b) / (hi - lo)
        points.append((x, y))
    line = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    area = f"{pad_l},{height-pad_b} " + line + f" {width-pad_r},{height-pad_b}"
    dots = "".join(f"<circle cx='{x:.2f}' cy='{y:.2f}' r='4'/>" for x, y in points)
    labels = "".join(f"<text x='{x:.2f}' y='{height-14}'>{i}</text>" for i, (x, _) in enumerate(points) if i % 4 == 0 or i == len(points)-1)
    return f"""<svg viewBox='0 0 {width} {height}' class='chart' role='img' aria-label='RSI validation release curve'>
      <defs><linearGradient id='area' x1='0' y1='0' x2='0' y2='1'><stop offset='0' stop-color='#72ffb6' stop-opacity='.36'/><stop offset='1' stop-color='#72ffb6' stop-opacity='0'/></linearGradient></defs>
      <path d='M {area} Z' fill='url(#area)'/>
      <polyline points='{line}' fill='none' stroke='#72ffb6' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>
      <g fill='#8df5ff'>{dots}</g>
      <line x1='{pad_l}' y1='{pad_t}' x2='{pad_l}' y2='{height-pad_b}' stroke='rgba(255,255,255,.18)'/>
      <line x1='{pad_l}' y1='{height-pad_b}' x2='{width-pad_r}' y2='{height-pad_b}' stroke='rgba(255,255,255,.18)'/>
      <text x='{pad_l}' y='18' fill='#b7c7dc'>{pct(hi,3)}</text>
      <text x='{pad_l}' y='{height-48}' fill='#b7c7dc'>{pct(lo,3)}</text>
      <g fill='#b7c7dc' font-size='12' text-anchor='middle'>{labels}</g>
    </svg>"""


def svg_arm_bars(arms: dict[str, Any]) -> str:
    width, height = 760, 340
    rows = sorted(arms.items(), key=lambda kv: kv[1]["weighted_value_capture"], reverse=True)
    maxv = max(float(v["weighted_value_capture"]) for _, v in rows)
    minv = min(float(v["weighted_value_capture"]) for _, v in rows)
    span = maxv - minv or 1
    y = 24
    chunks = []
    for name, data in rows:
        val = float(data["weighted_value_capture"])
        bar = 130 + (val - minv) / span * 520
        color = "#72ffb6" if name == "skillos_full_rsi" else "#8df5ff"
        chunks.append(f"<text x='18' y='{y+18}' fill='#eef8ff' font-size='14' font-weight='800'>{esc(name.replace('_',' '))}</text>")
        chunks.append(f"<rect x='270' y='{y}' width='{bar:.2f}' height='24' rx='12' fill='{color}' opacity='.80'/>")
        chunks.append(f"<text x='{bar+284:.2f}' y='{y+18}' fill='#dcecff' font-size='13'>{pct(val,2)}</text>")
        y += 38
    return f"<svg viewBox='0 0 {width} {height}' class='chart' role='img' aria-label='Counterfactual arm comparison'>{''.join(chunks)}</svg>"


def svg_radar(metrics: dict[str, float]) -> str:
    axes = [
        ("Value capture", metrics["locked_holdout_value_capture"]),
        ("Causal uplift", min(1.0, metrics["causal_uplift_vs_best_control"] / 0.20)),
        ("Verifier agreement", metrics["verifier_agreement"]),
        ("RSI integrity", metrics["rsi_integrity"]),
        ("Trace replay", metrics["trace_replayability"]),
        ("Risk control", 1.0 - metrics["risk_breach_rate"]),
        ("Negative control", 1.0 - min(1.0, metrics["negative_control_max_abs_gain"] / 0.02)),
    ]
    cx = cy = 170
    r = 118
    pts = []
    labels = []
    spokes = []
    n = len(axes)
    for i, (name, val) in enumerate(axes):
        angle = -3.14159265/2 + 2*3.14159265*i/n
        x = cx + r * val * __import__('math').cos(angle)
        y = cy + r * val * __import__('math').sin(angle)
        lx = cx + (r+34) * __import__('math').cos(angle)
        ly = cy + (r+34) * __import__('math').sin(angle)
        sx = cx + r * __import__('math').cos(angle)
        sy = cy + r * __import__('math').sin(angle)
        pts.append(f"{x:.2f},{y:.2f}")
        labels.append(f"<text x='{lx:.2f}' y='{ly:.2f}' text-anchor='middle' fill='#d9ecff' font-size='11'>{esc(name)}</text>")
        spokes.append(f"<line x1='{cx}' y1='{cy}' x2='{sx:.2f}' y2='{sy:.2f}' stroke='rgba(255,255,255,.14)'/>")
    rings = "".join(f"<circle cx='{cx}' cy='{cy}' r='{r*k/4:.2f}' fill='none' stroke='rgba(255,255,255,.12)'/>" for k in range(1,5))
    return f"""<svg viewBox='0 0 340 340' class='chart radar' role='img' aria-label='Causal attribution radar'>
      {rings}{''.join(spokes)}<polygon points='{' '.join(pts)}' fill='rgba(141,245,255,.25)' stroke='#8df5ff' stroke-width='3'/>
      <g>{''.join(labels)}</g>
    </svg>"""


def render(proof: dict[str, Any]) -> str:
    m = proof["metrics"]
    scale = proof["scale"]
    page_title = esc(TITLE)
    release_curve = svg_release_curve(proof["release_curve"])
    bars = svg_arm_bars(proof["arms_summary"])
    radar = svg_radar(m)
    samples = "".join(
        f"<tr><td>{esc(row['case_id'])}</td><td>{esc(row['domain'])}</td><td>{money_t(row['benchmark_capital_equivalent_value_trillions'])}</td><td>{esc(', '.join(row['capability_atoms']))}</td></tr>"
        for row in proof.get("sample_locked_holdout_cases", [])[:10]
    )
    gates = "".join(f"<li><span class='ok'>✓</span>{esc(name.replace('_',' '))}</li>" for name, ok in proof["gates"].items() if ok)
    neg = proof["negative_controls"]
    neg_rows = "".join(f"<tr><td>{esc(k)}</td><td>{pct(float(v),3)}</td></tr>" for k, v in neg.items())
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<meta name='viewport' content='width=device-width,initial-scale=1'/>
<title>{page_title}</title>
<meta name='description' content='Autonomous SkillOS proof for causal attribution of validation-gated Recursive Self-Improvement.' />
<style>
:root {{--bg:#071827;--ink:#eef8ff;--muted:#b7c7dc;--line:rgba(255,255,255,.15);--cyan:#8df5ff;--green:#72ffb6;--violet:#9b8cff;--gold:#ffd86b;--rose:#ff8ea3}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;background:radial-gradient(circle at 18% 0%,rgba(141,245,255,.18),transparent 30%),radial-gradient(circle at 84% 8%,rgba(155,140,255,.18),transparent 34%),linear-gradient(135deg,#071827 0%,#0d1b34 55%,#15143a 100%);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.45}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:34px 34px;pointer-events:none;mask-image:linear-gradient(to bottom,black,transparent 86%)}}a{{color:var(--cyan);font-weight:900;text-decoration:none}}nav{{position:sticky;top:0;z-index:10;display:flex;justify-content:space-between;gap:18px;padding:14px 20px;background:rgba(4,15,26,.88);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}}nav span{{display:flex;gap:16px;flex-wrap:wrap}}main{{width:min(1180px,92vw);margin:auto;padding:54px 0 90px}}.hero,.panel,.metric,.callout{{background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:28px;box-shadow:0 28px 90px rgba(0,0,0,.24);backdrop-filter:blur(10px)}}.hero{{padding:38px}}.eyebrow{{color:var(--cyan);letter-spacing:.22em;text-transform:uppercase;font-weight:950;font-size:12px}}h1{{font-size:clamp(42px,7vw,88px);line-height:.89;letter-spacing:-.075em;margin:16px 0}}h2{{font-size:clamp(30px,4.4vw,58px);line-height:1;letter-spacing:-.06em;margin:54px 0 18px}}h3{{font-size:24px;margin:0 0 10px}}p{{color:var(--muted)}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0}}.metric{{padding:18px}}.metric b{{display:block;color:var(--green);font-size:clamp(26px,3vw,38px);letter-spacing:-.04em}}.grid{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.panel{{padding:22px;overflow:hidden}}.chart{{width:100%;height:auto;display:block}}.pill{{display:inline-flex;border-radius:999px;padding:7px 10px;background:rgba(114,255,182,.16);color:var(--green);font-weight:950;font-size:12px;text-transform:uppercase}}.button{{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:12px 16px;background:var(--cyan);color:#071827;font-weight:950}}.button.secondary{{background:transparent;color:var(--ink);border:1px solid var(--line)}}.links{{display:flex;gap:12px;flex-wrap:wrap;margin-top:20px}}.callout{{padding:26px;margin:24px 0}}.mechanism{{font-size:clamp(24px,4vw,44px);line-height:1.1;letter-spacing:-.055em;color:#fff}}table{{width:100%;border-collapse:collapse;background:rgba(255,255,255,.055);border-radius:18px;overflow:hidden}}th,td{{padding:13px;border-bottom:1px solid var(--line);text-align:left;color:#dcecff}}th{{color:#8df5ff;font-size:12px;text-transform:uppercase;letter-spacing:.14em}}.ok{{color:var(--green);font-weight:950;margin-right:8px}}ul.gates{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;padding:0;list-style:none}}.safe{{border-left:4px solid var(--gold);padding-left:16px;color:#ffeeb0}}@media(max-width:880px){{.grid,.metrics{{grid-template-columns:1fr}}nav{{position:static}}ul.gates{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<nav><strong><a href='index.html'>SkillOS Proof Command Center</a></strong><span><a href='#method'>Method</a><a href='proof-registry.json'>Registry</a><a href='https://github.com/MontrealAI/skillos/actions'>Run on GitHub</a><a href='https://github.com/MontrealAI/skillos'>GitHub</a></span></nav>
<main>
  <section class='hero'>
    <div class='eyebrow'>Causal attribution proof • validation-gated RSI • counterfactual replay</div>
    <h1>Did SkillOS cause the improvement?</h1>
    <p><strong>{page_title}</strong> isolates the contribution of a large specialist-agent coordination lattice through paired counterfactual worlds, baselines, ablations, placebo controls, shuffled-label controls, locked holdout cases, and public receipts.</p>
    <div class='metrics'>
      <div class='metric'><b>{pct(m['locked_holdout_value_capture'])}</b><span>locked-holdout value capture</span></div>
      <div class='metric'><b>+{pct(m['causal_uplift_vs_best_control'])}</b><span>causal uplift vs strongest control</span></div>
      <div class='metric'><b>{pct(m['frontier_correct_rate'])}</b><span>frontier-correct rate</span></div>
      <div class='metric'><b>{pct(m['risk_breach_rate'])}</b><span>risk breach rate</span></div>
    </div>
    <div class='links'><a class='button' href='data/{PROOF_ID}.json'>Inspect JSON receipt</a><a class='button secondary' href='docs/{PROOF_ID}.md'>Read report</a><a class='button secondary' href='https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-causal-attribution-engine-proof.yml'>Run / regenerate</a></div>
  </section>

  <section class='callout'>
    <div class='eyebrow'>Mechanism under test</div>
    <div class='mechanism'>{esc(proof['mechanism'])}</div>
    <p class='safe'>{esc(proof['public_claim_boundary'])}</p>
  </section>

  <section class='metrics'>
    <div class='metric'><b>{scale['virtual_specialist_agents']:,}</b><span>virtual specialist agents</span></div>
    <div class='metric'><b>{scale['specialist_roles']:,}</b><span>specialist roles</span></div>
    <div class='metric'><b>{scale['counterfactual_cells']:,}</b><span>counterfactual cells</span></div>
    <div class='metric'><b>{scale['locked_holdout_cases']:,}</b><span>locked holdout cases</span></div>
  </section>

  <section class='grid'>
    <article class='panel'><h3>RSI release curve</h3><p>Validation-selected releases improve until the selected protocol is frozen for holdout evaluation.</p>{release_curve}</article>
    <article class='panel'><h3>Causal attribution radar</h3><p>The proof rewards value capture, causal identifiability, verifier agreement, trace replayability, RSI integrity, and risk control.</p>{radar}</article>
  </section>

  <section class='panel' id='method' style='margin-top:18px'><h3>Paired counterfactual arms</h3><p>Every arm sees the same locked holdout cases. SkillOS full RSI must beat the strongest non-SkillOS control and the falsification tests.</p>{bars}</section>

  <section class='grid' style='margin-top:18px'>
    <article class='panel'><h3>Negative controls</h3><table><thead><tr><th>Control</th><th>Effect</th></tr></thead><tbody>{neg_rows}</tbody></table></article>
    <article class='panel'><h3>Pre-registered gates</h3><ul class='gates'>{gates}</ul></article>
  </section>

  <section class='panel' style='margin-top:18px'><h3>Sample locked holdout cases</h3><table><thead><tr><th>Case</th><th>Domain</th><th>Value at stake</th><th>Capability atoms</th></tr></thead><tbody>{samples}</tbody></table></section>

  <section class='callout'>
    <div class='eyebrow'>Interpretation</div>
    <p>{esc(proof['thesis'])}</p>
    <p>Best non-SkillOS control: <strong>{esc(proof['best_control']['arm'].replace('_',' '))}</strong>. Benchmark-capital-equivalent gain over that control: <strong>{money_t(m['benchmark_capital_equivalent_gain_vs_best_control_trillions'])}</strong>.</p>
    <p>Receipt SHA-256: <code>{esc(proof['receipt_sha256'])}</code></p>
  </section>
</main>
</body>
</html>
"""


def main() -> None:
    root = Path.cwd()
    data_path = root / "data" / f"{PROOF_ID}.json"
    if not data_path.exists():
        fail(f"missing proof JSON: {data_path}")
    proof = json.loads(data_path.read_text(encoding="utf-8"))
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
