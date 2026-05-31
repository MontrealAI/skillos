#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import shutil
from pathlib import Path
from typing import Any

PROOF_ID = "rsi-adversarial-benchmark-foundry-proof"
TITLE = "Autonomous RSI Adversarial Benchmark Foundry Proof"


def pct(v: float, digits: int = 2) -> str:
    return f"{100 * float(v):.{digits}f}%"


def money_t(v: float) -> str:
    return f"${float(v):,.2f}T"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def points_for_curve(curve: list[dict[str, Any]], key: str, width: int = 620, height: int = 170) -> str:
    vals = [float(x.get(key, 0)) for x in curve]
    if not vals:
        return ""
    lo, hi = min(vals), max(vals)
    pad = max(1e-6, hi - lo)
    pts = []
    for i, val in enumerate(vals):
        x = 24 + i * ((width - 48) / max(1, len(vals) - 1))
        y = height - 24 - ((val - lo) / pad) * (height - 48)
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts)


def release_curve_svg(curve: list[dict[str, Any]]) -> str:
    pts1 = points_for_curve(curve, "validation_value_capture")
    pts2 = points_for_curve(curve, "mean_challenge_hardness")
    circles = []
    for p in pts1.split()[::3]:
        if "," in p:
            x, y = p.split(",")
            circles.append(f"<circle cx='{x}' cy='{y}' r='3' fill='#72ffb6'/>")
    return f"""<svg viewBox='0 0 620 190' class='chart' role='img' aria-label='RSI release curve'><defs><linearGradient id='g1' x1='0' x2='1'><stop stop-color='#72ffb6'/><stop offset='1' stop-color='#7cecff'/></linearGradient></defs><line x1='24' y1='166' x2='596' y2='166' stroke='rgba(255,255,255,.18)'/><line x1='24' y1='18' x2='24' y2='166' stroke='rgba(255,255,255,.18)'/><polyline points='{pts2}' fill='none' stroke='rgba(255,216,107,.72)' stroke-width='2'/><polyline points='{pts1}' fill='none' stroke='url(#g1)' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'/>{''.join(circles)}<text x='26' y='14' fill='#a9c6dd' font-size='11'>value capture + adversarial hardness across releases</text></svg>"""


def bar_svg(controls: dict[str, Any], main_value: float) -> str:
    rows = [("SkillOS foundry", main_value)] + [(k.replace("_", " "), float(v.get("weighted_value_capture", 0))) for k, v in controls.items()]
    rows = rows[:8]
    maxv = max(v for _, v in rows) or 1
    bits = []
    for i, (name, value) in enumerate(rows):
        y = 24 + i * 32
        w = 430 * value / maxv
        color = "#72ffb6" if i == 0 else "#7cecff"
        bits.append(f"<text x='10' y='{y+14}' fill='#d9ecff' font-size='12'>{html.escape(name[:36])}</text><rect x='230' y='{y}' width='{w:.1f}' height='18' rx='9' fill='{color}' opacity='{0.9 if i==0 else 0.45}'/><text x='{240+w:.1f}' y='{y+14}' fill='#d9ecff' font-size='12'>{pct(value,1)}</text>")
    h = 36 + 32 * len(rows)
    return f"<svg viewBox='0 0 620 {h}' class='chart' role='img' aria-label='Control ablation chart'>{''.join(bits)}</svg>"


def radar_svg(metrics: dict[str, Any]) -> str:
    axes = [
        ("Hardness", metrics["adversarial_benchmark_hardness_gain_vs_static"] / 0.45),
        ("Causal", metrics["causal_uplift_vs_strongest_control"] / 0.25),
        ("Leakage", metrics["benchmark_leakage_rejection_rate"]),
        ("Integrity", 1.0 - metrics["goodhart_gap"]),
        ("Replay", metrics["trace_replayability"]),
        ("Risk", 1.0 - metrics["risk_breach_rate"]),
    ]
    cx, cy, r = 180, 140, 95
    pts = []
    labels = []
    import math
    for i, (label, raw) in enumerate(axes):
        val = max(0.0, min(1.0, float(raw)))
        ang = -math.pi / 2 + i * 2 * math.pi / len(axes)
        x = cx + math.cos(ang) * r * val
        y = cy + math.sin(ang) * r * val
        pts.append(f"{x:.1f},{y:.1f}")
        lx = cx + math.cos(ang) * (r + 28)
        ly = cy + math.sin(ang) * (r + 28)
        labels.append(f"<text x='{lx:.1f}' y='{ly:.1f}' fill='#d9ecff' font-size='11' text-anchor='middle'>{label}</text>")
    rings = "".join(f"<circle cx='{cx}' cy='{cy}' r='{r*k/4}' fill='none' stroke='rgba(255,255,255,.12)'/>" for k in range(1,5))
    spokes = []
    for i in range(len(axes)):
        ang = -math.pi / 2 + i * 2 * math.pi / len(axes)
        spokes.append(f"<line x1='{cx}' y1='{cy}' x2='{cx + math.cos(ang)*r:.1f}' y2='{cy + math.sin(ang)*r:.1f}' stroke='rgba(255,255,255,.10)'/>")
    return f"<svg viewBox='0 0 360 280' class='chart' role='img' aria-label='Capability radar'>{rings}{''.join(spokes)}<polygon points='{' '.join(pts)}' fill='rgba(124,236,255,.22)' stroke='#7cecff' stroke-width='3'/>{''.join(labels)}</svg>"


def render_page(proof: dict[str, Any]) -> str:
    m = proof["metrics"]
    controls = proof.get("controls", {})
    samples = proof.get("sample_adversarial_benchmarks", [])[:8]
    sample_rows = "".join(f"<tr><td>{html.escape(s['challenge_id'])}</td><td>{html.escape(s['domain'])}</td><td>{html.escape(s['failure_mode_targeted'])}</td><td>{s['difficulty']:.3f}</td><td>{html.escape(s['hidden_failure_signature'])}</td></tr>" for s in samples)
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/><meta name='viewport' content='width=device-width,initial-scale=1'/>
<title>{html.escape(TITLE)} · SkillOS</title>
<style>
:root{{--bg:#061826;--panel:rgba(255,255,255,.09);--line:rgba(255,255,255,.18);--ink:#f4fbff;--muted:#b9cbe0;--cyan:#7cecff;--green:#72ffb6;--gold:#ffd86b}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 12% 20%,rgba(0,234,255,.16),transparent 30%),radial-gradient(circle at 80% 8%,rgba(145,118,255,.18),transparent 34%),linear-gradient(135deg,#061d2b,#111838 72%,#090b1d);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.45}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:34px 34px;pointer-events:none;mask-image:linear-gradient(to bottom,black,transparent 88%)}}a{{color:var(--cyan);text-decoration:none;font-weight:900}}nav{{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;gap:18px;padding:14px 22px;background:rgba(4,15,26,.88);border-bottom:1px solid var(--line);backdrop-filter:blur(14px)}}nav span{{display:flex;gap:14px;flex-wrap:wrap}}.wrap{{width:min(1200px,92vw);margin:auto;padding:52px 0 90px}}h1{{font-size:clamp(44px,7vw,86px);line-height:.89;letter-spacing:-.075em;margin:14px 0}}h2{{font-size:clamp(30px,4vw,56px);letter-spacing:-.055em;margin-top:56px}}h3{{font-size:22px;margin:12px 0}}p{{color:var(--muted)}}.hero,.card,.metric{{background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:26px;box-shadow:0 30px 90px rgba(0,0,0,.23);backdrop-filter:blur(10px)}}.hero{{padding:34px;display:grid;grid-template-columns:1.15fr .85fr;gap:22px;align-items:stretch}}@media(max-width:900px){{.hero{{grid-template-columns:1fr}}nav{{position:static}}}}.eyebrow{{color:var(--cyan);letter-spacing:.22em;text-transform:uppercase;font-weight:950;font-size:12px}}.pill{{display:inline-flex;padding:8px 11px;border-radius:999px;background:rgba(114,255,182,.18);color:var(--green);font-size:12px;font-weight:950;text-transform:uppercase}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0}}@media(max-width:900px){{.metrics{{grid-template-columns:1fr 1fr}}}}.metric{{padding:18px;border-radius:18px}}.metric b{{color:var(--green);font-size:28px}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}.card{{padding:22px}}.chart{{width:100%;height:auto;background:rgba(0,0,0,.16);border:1px solid rgba(255,255,255,.12);border-radius:18px;padding:10px}}.btn{{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:12px 16px;background:var(--cyan);color:#061826;font-weight:950;margin:4px 8px 4px 0}}.secondary{{background:transparent;color:#eef;border:1px solid rgba(255,255,255,.28)}}table{{width:100%;border-collapse:collapse;background:rgba(0,0,0,.16);border-radius:18px;overflow:hidden}}td,th{{padding:12px;border-bottom:1px solid rgba(255,255,255,.11);text-align:left;color:#d9ecff}}th{{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#94a9c3}}code{{background:rgba(0,0,0,.25);padding:2px 6px;border-radius:6px}}.note{{border-left:3px solid var(--cyan);padding-left:16px;color:#d9ecff}}
</style>
</head>
<body>
<nav><strong><a href='index.html'>SkillOS Proof Command Center</a></strong><span><a href='index.html'>Home</a><a href='proof-registry.json'>Registry</a><a href='data/{PROOF_ID}.json'>JSON</a><a href='docs/{PROOF_ID}.md'>Report</a><a href='https://github.com/MontrealAI/skillos/actions'>Run / Regenerate</a><a href='https://github.com/MontrealAI/skillos'>GitHub</a></span></nav>
<main class='wrap'>
<section class='hero'>
<div><div class='eyebrow'>adversarial benchmark foundry · autonomous RSI proof</div><h1>Can SkillOS generate its own hardest tests?</h1><p>{html.escape(proof['thesis'])}</p><p class='note'>This proof asks whether a large specialist-agent organization can attack its own benchmark surface, reject leaked tasks, release repairs, and prove causal lift on locked hidden holdouts.</p><a class='btn' href='https://github.com/MontrealAI/skillos/actions'>Run on GitHub</a><a class='btn secondary' href='data/{PROOF_ID}.json'>Open receipt</a></div>
<div class='card'><span class='pill'>proof passed</span><h3>{html.escape(TITLE)}</h3><p><b>{proof['scale']['virtual_specialist_agents']:,}</b> virtual specialist agents · <b>{proof['scale']['specialist_roles']:,}</b> roles · <b>{proof['scale']['adversarial_benchmark_cells']:,}</b> adversarial benchmark cells.</p><p>Selected release: <code>{html.escape(proof['selected_release'])}</code></p><p>Receipt tree root:<br><code>{html.escape(proof['receipt_tree']['root'][:32])}…</code></p></div>
</section>
<section class='metrics'>
<div class='metric'><b>{pct(m['locked_hidden_holdout_value_capture'])}</b><br>hidden-holdout value capture</div>
<div class='metric'><b>{pct(m['adversarial_benchmark_hardness_gain_vs_static'])}</b><br>harder than static benchmarks</div>
<div class='metric'><b>{pct(m['causal_uplift_vs_strongest_control'])}</b><br>causal uplift vs strongest control</div>
<div class='metric'><b>{pct(m['benchmark_leakage_rejection_rate'])}</b><br>leakage rejection</div>
</section>
<section class='card'><div class='eyebrow'>core mechanism</div><h2>Failures become harder tests. Harder tests become better releases.</h2><p style='font-size:24px;color:#fff;font-weight:900'>{html.escape(proof['core_mechanism'])}</p><p>{html.escape(proof['public_safe_boundary'])}</p></section>
<h2>Visual proof receipts</h2>
<section class='grid'>
<div class='card'><h3>Validation-gated RSI release curve</h3>{release_curve_svg(proof['release_curve'])}<p>Release selection is based on validation performance, then measured on locked hidden holdouts.</p></div>
<div class='card'><h3>Capability integrity radar</h3>{radar_svg(m)}<p>SkillOS must improve without leakage, metric gaming, or risk breaches.</p></div>
<div class='card'><h3>Ablation controls</h3>{bar_svg(controls, m['locked_hidden_holdout_value_capture'])}<p>The strongest control is <code>{html.escape(m['strongest_control'])}</code>. SkillOS is evaluated against it with paired holdout cases and bootstrap confidence.</p></div>
<div class='card'><h3>Capital-equivalent benchmark accounting</h3><p><b>{money_t(m['benchmark_capital_equivalent_value_captured_trillions'])}</b> captured out of <b>{money_t(m['benchmark_capital_equivalent_value_at_stake_trillions'])}</b> benchmark-capital-equivalent value at stake.</p><p>Gain over strongest control: <b>{money_t(m['benchmark_capital_equivalent_gain_vs_strongest_control_trillions'])}</b>.</p></div>
</section>
<h2>Sample generated adversarial benchmarks</h2>
<table><thead><tr><th>Challenge</th><th>Domain</th><th>Failure mode</th><th>Difficulty</th><th>Hidden signature</th></tr></thead><tbody>{sample_rows}</tbody></table>
<h2>Run / regenerate</h2>
<section class='card'><p>Open the GitHub Action and run <b>Autonomous RSI Adversarial Benchmark Foundry Proof</b>. The action regenerates the receipt, report, badge, proof webpage, registry, command center, sitemap, and robots file autonomously.</p><a class='btn' href='https://github.com/MontrealAI/skillos/actions'>Run proof</a><a class='btn secondary' href='docs/{PROOF_ID}.md'>Read report</a></section>
</main>
</body></html>"""


def main() -> None:
    root = Path.cwd()
    data_path = root / "data" / f"{PROOF_ID}.json"
    if not data_path.exists():
        raise SystemExit(f"missing proof receipt: {data_path}")
    proof = read_json(data_path)
    site = root / "site"
    (site / "data").mkdir(parents=True, exist_ok=True)
    (site / "docs").mkdir(parents=True, exist_ok=True)
    (site / "badges").mkdir(parents=True, exist_ok=True)
    (site / f"{PROOF_ID}.html").write_text(render_page(proof), encoding="utf-8")
    shutil.copy2(data_path, site / "data" / f"{PROOF_ID}.json")
    shutil.copy2(root / "docs" / f"{PROOF_ID}.md", site / "docs" / f"{PROOF_ID}.md")
    shutil.copy2(root / "badges" / f"{PROOF_ID}.svg", site / "badges" / f"{PROOF_ID}.svg")
    print(json.dumps({"rendered": True, "html": f"site/{PROOF_ID}.html"}, indent=2))


if __name__ == "__main__":
    main()
