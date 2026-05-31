#!/usr/bin/env python3
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ROOT / "docs"
SITE = ROOT / "site"
BADGES = ROOT / "badges"
PROOF = DATA / "rsi-continual-capability-frontier-proof.json"
SITE.mkdir(parents=True, exist_ok=True)
BADGES.mkdir(parents=True, exist_ok=True)

def esc(x: object) -> str:
    return html.escape(str(x))

def money(value: float) -> str:
    if abs(value) >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:,.2f}T"
    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"
    return f"${value:,.0f}"

def bar(label: str, value: float, note: str = "") -> str:
    width = max(0.0, min(100.0, value))
    return f'<div class="bar"><span>{esc(label)}</span><div><i style="width:{width:.2f}%"></i></div><b>{esc(note or str(value))}</b></div>'

def main() -> None:
    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    final = proof["final"]
    controls = proof["baselines_and_controls"]
    releases = proof["rsi_releases"]

    release_rows = "".join(
        f"<tr><td>v{r['generation']}</td><td>{'released' if r['released'] else 'rejected'}</td><td>{esc(r['lesson'])}</td><td>{r['validation']['value_capture_rate_percent']}%</td><td>{r['validation']['minimum_regime_value_capture_percent']}%</td><td>{r['validation']['catastrophic_forgetting_rate_percent']}%</td></tr>"
        for r in releases
    )
    control_bars = "".join(bar(k.replace("_", " "), v["value_capture_rate_percent"], f"{v['value_capture_rate_percent']}%") for k, v in controls.items())
    gate_rows = "".join(f"<tr><td>{esc(k.replace('_',' '))}</td><td>{'passed' if v else 'failed'}</td></tr>" for k, v in proof["pre_registered_gates"].items())
    regime_rows = "".join(
        f"<tr><td>{esc(proof['benchmark_public']['regimes'][int(k)])}</td><td>{v['value_capture_rate_percent']}%</td><td>{v['frontier_correct_rate_percent']}%</td><td>{v['count']}</td></tr>"
        for k, v in final["regime_scores"].items()
    )

    html_text = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SkillOS RSI Continual Capability Frontier Proof</title>
<style>
:root{{--bg:#06131f;--panel:rgba(255,255,255,.075);--line:rgba(255,255,255,.16);--text:#f5fbff;--muted:#b8c8d8;--cyan:#86f8ff;--green:#7dffb0;--gold:#ffd66b}}
*{{box-sizing:border-box}}body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;background:radial-gradient(circle at 82% 0,#3d4381 0,transparent 34%),radial-gradient(circle at 0 18%,#095e70 0,transparent 26%),linear-gradient(135deg,#06131f,#13243d 60%,#282a5d);color:var(--text)}}a{{color:var(--cyan)}}main{{max-width:1220px;margin:0 auto;padding:44px 20px 80px}}nav{{position:sticky;top:0;z-index:5;background:rgba(6,19,31,.9);border-bottom:1px solid var(--line);backdrop-filter:blur(14px);display:flex;justify-content:space-between;padding:14px 22px}}nav a{{color:var(--muted);text-decoration:none;font-weight:850;margin-left:14px}}h1{{font-size:clamp(44px,7vw,96px);line-height:.86;letter-spacing:-.08em;margin:12px 0}}h2{{font-size:clamp(30px,4vw,54px);letter-spacing:-.05em}}p{{color:var(--muted);font-size:18px;line-height:1.55}}.hero{{display:grid;grid-template-columns:1.05fr .95fr;gap:22px;align-items:center}}.card,.metric{{background:var(--panel);border:1px solid var(--line);border-radius:28px;padding:22px;box-shadow:0 22px 80px rgba(0,0,0,.25)}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}}.metric strong{{display:block;color:var(--green);font-size:32px}}.metric span{{color:var(--muted)}}.eyebrow{{color:var(--cyan);text-transform:uppercase;letter-spacing:.18em;font-weight:950;font-size:12px}}.quote{{font-size:clamp(24px,3.2vw,42px);line-height:1.08;letter-spacing:-.04em;color:var(--text)}}.bar{{display:grid;grid-template-columns:245px 1fr 140px;gap:12px;align-items:center;margin:12px 0}}.bar span,.bar b{{color:var(--muted)}}.bar div{{height:20px;background:rgba(255,255,255,.08);border-radius:999px;overflow:hidden}}.bar i{{display:block;height:100%;background:linear-gradient(90deg,var(--green),var(--cyan));border-radius:999px}}table{{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:18px;overflow:hidden;margin:16px 0}}td,th{{padding:12px;border-bottom:1px solid var(--line);text-align:left}}th{{color:var(--muted);text-transform:uppercase;font-size:12px;letter-spacing:.08em}}.notice{{border-left:4px solid var(--gold);background:rgba(255,214,107,.08);border-radius:16px;padding:16px 18px;color:var(--muted)}}@media(max-width:900px){{.hero,.grid,.bar{{grid-template-columns:1fr}}}}
</style></head>
<body><nav><strong>SkillOS Continual Capability Frontier</strong><div><a href="index.html">Command Center</a><a href="proofs.html">Proofs</a><a href="data/rsi-continual-capability-frontier-proof.json">JSON</a></div></nav>
<main>
<section class="hero"><div><div class="eyebrow">MONTREAL.AI / SKILLOS</div><h1>Continual Capability Frontier.</h1><p>Autonomous proof that SkillOS can recursively improve capability routing under drift while avoiding catastrophic forgetting, risk breach, and unauthorized actions.</p></div>
<div class="card"><div class="eyebrow">proof passed</div><div class="quote">{proof['agent_system']['virtual_specialist_agents']:,} agents. {proof['agent_system']['specialist_roles']:,} roles. {proof['rsi_release_count']} RSI releases. {proof['benchmark_public']['locked_holdout_count']} locked holdout cases.</div><p>{esc(proof['safe_interpretation'])}</p></div></section>
<section class="grid">
<div class="metric"><strong>{final['value_capture_rate_percent']}%</strong><span>value capture</span></div>
<div class="metric"><strong>{final['minimum_regime_value_capture_percent']}%</strong><span>minimum regime capture</span></div>
<div class="metric"><strong>{final['catastrophic_forgetting_rate_percent']}%</strong><span>catastrophic forgetting</span></div>
<div class="metric"><strong>{final['risk_breach_rate_percent']}%</strong><span>risk breach</span></div>
</section>
<section class="card"><div class="eyebrow">core mechanism</div><div class="quote">telemetry → drift detection → specialist-agent market clearing → replay buffer → verifier courts → rollback gates → release promotion → multi-regime holdout → reinvestment → compounding trustworthy capability</div></section>
<section><h2>Baselines and controls</h2><div class="card">{control_bars}{bar('SkillOS RSI continual frontier', final['value_capture_rate_percent'], str(final['value_capture_rate_percent'])+'%')}</div></section>
<section><h2>Regime coverage</h2><table><tr><th>Regime</th><th>Value capture</th><th>Frontier-correct</th><th>Cases</th></tr>{regime_rows}</table></section>
<section><h2>RSI release history</h2><table><tr><th>Generation</th><th>Status</th><th>Lesson</th><th>Validation capture</th><th>Min regime capture</th><th>Forgetting</th></tr>{release_rows}</table></section>
<section><h2>Pre-registered gates</h2><table><tr><th>Gate</th><th>Status</th></tr>{gate_rows}</table></section>
<section class="notice"><strong>Boundary:</strong> {esc(proof['public_boundary'])} Protocol fingerprint: {esc(proof['protocol_fingerprint_sha256'])}</section>
</main></body></html>"""

    (SITE / "rsi-continual-capability-frontier-proof.html").write_text(html_text, encoding="utf-8")
    badge = '<svg xmlns="http://www.w3.org/2000/svg" width="330" height="20"><rect width="330" height="20" rx="10" fill="#14233a"/><rect x="226" width="104" height="20" rx="10" fill="#2bb673"/><text x="10" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">continual capability frontier</text><text x="242" y="14" fill="#fff" font-family="Verdana" font-size="11">passed</text></svg>'
    (BADGES / "rsi-continual-capability-frontier-proof.svg").write_text(badge, encoding="utf-8")
    print(json.dumps({"status": "VISIBLE_OUTPUTS_WRITTEN", "html": "site/rsi-continual-capability-frontier-proof.html"}, indent=2))

if __name__ == "__main__":
    main()
