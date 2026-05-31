#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
from pathlib import Path

PROOF_ID = "rsi-capability-liquidity-engine-proof"
PROOF_PAGE = f"{PROOF_ID}.html"
BASE_URL = "https://montrealai.github.io/skillos/"
REPO_URL = "https://github.com/MontrealAI/skillos"
WORKFLOW = ".github/workflows/autonomous-rsi-capability-liquidity-engine-proof.yml"
WORKFLOW_URL = f"{REPO_URL}/actions/workflows/autonomous-rsi-capability-liquidity-engine-proof.yml"


def money(x: float) -> str:
    ax = abs(x)
    if ax >= 1e12:
        return f"${x/1e12:,.2f}T"
    if ax >= 1e9:
        return f"${x/1e9:,.2f}B"
    if ax >= 1e6:
        return f"${x/1e6:,.2f}M"
    return f"${x:,.0f}"


def pct(x: float, places: int = 3) -> str:
    return f"{100*x:.{places}f}%"


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            if src.resolve() == dst.resolve():
                return
        except FileNotFoundError:
            pass
        shutil.copy2(src, dst)


def load_registry(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("proofs"), list):
            return data["proofs"]
        if isinstance(data, list):
            return data
    except Exception:
        return []
    return []


def save_registry(path: Path, proofs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"updated_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"), "proofs": proofs}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def proof_cards(proofs: list[dict]) -> str:
    cards = []
    for p in proofs[:12]:
        status = "PROOF PASSED" if p.get("proved") else "NOT RUN YET"
        cards.append(f'''<article class="proof-card"><div class="pill">{status}</div><h3>{p.get('short_title', p.get('title','Proof'))}</h3><p>{p.get('description','Autonomous public proof.')}</p><div class="mini"><span>{p.get('agents','')}</span><span>{p.get('capture','')}</span><span>{p.get('risk','')}</span></div><div class="btns"><a class="btn primary" href="{p.get('path','#')}">View proof</a><a class="btn" href="{p.get('workflow_url', WORKFLOW_URL)}">Run on GitHub</a></div></article>''')
    return "".join(cards)


def status_rows(proofs: list[dict]) -> str:
    rows = []
    for p in proofs[:14]:
        status = "PASSING" if p.get("proved") else "NOT RUN YET"
        cls = "pass" if p.get("proved") else "pending"
        rows.append(f'''<tr><td><a href="{p.get('path','#')}">{p.get('title','Proof')}</a><br><span>{p.get('workflow','')}</span></td><td><b class="{cls}">{status}</b></td><td>{p.get('updated_at','')}</td><td>{p.get('capture','')}</td></tr>''')
    return "".join(rows)


def render_index(proofs: list[dict]) -> str:
    latest = proofs[0] if proofs else {}
    cards = proof_cards(proofs)
    rows = status_rows(proofs)
    updated = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>SkillOS Proof Command Center</title><meta name="description" content="Always-fresh public command center for autonomous SkillOS RSI proofs."/>
<style>:root{{--bg:#071827;--line:rgba(218,242,255,.18);--text:#eef8ff;--muted:#b8d0df;--cyan:#7ef7ff;--green:#78ffb0;--gold:#f6d76a}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 10% 18%,#0b6070 0,#092b44 32%,#151b3e 76%,#090d1a 100%);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.45}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:34px 34px;pointer-events:none;opacity:.75}}a{{color:var(--cyan);text-decoration:none}}a:hover{{text-decoration:underline}}.nav{{position:sticky;top:0;z-index:10;background:rgba(4,16,28,.86);backdrop-filter:blur(18px);border-bottom:1px solid var(--line);height:56px;display:flex;justify-content:space-between;align-items:center;padding:0 22px}}.brand{{font-weight:1000;color:var(--cyan)}}.navlinks{{display:flex;gap:18px;font-size:14px;font-weight:800}}.wrap{{width:min(1180px,calc(100% - 40px));margin:auto;position:relative}}.hero{{padding:70px 0 40px;display:grid;grid-template-columns:1.1fr .9fr;gap:28px;align-items:stretch}}h1{{font-size:clamp(54px,7.5vw,112px);line-height:.88;letter-spacing:-.08em;margin:12px 0 20px}}.eyebrow{{font-size:12px;letter-spacing:.32em;text-transform:uppercase;color:var(--cyan);font-weight:1000}}.lead{{font-size:18px;color:#d4eaf7;max-width:780px}}.panel,.proof-card,.stat,.run-card,table{{border:1px solid var(--line);background:linear-gradient(135deg,rgba(255,255,255,.14),rgba(255,255,255,.055));border-radius:26px;box-shadow:0 24px 80px rgba(0,0,0,.18)}}.panel{{padding:28px}}.big{{font-size:36px;line-height:1.02;font-weight:1000;letter-spacing:-.05em}}.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:14px 0 38px}}.stat{{padding:20px}}.stat strong{{display:block;color:var(--green);font-size:30px;letter-spacing:-.04em}}.stat span{{color:var(--muted);font-size:14px}}.section-title{{font-size:clamp(38px,5vw,64px);line-height:.92;letter-spacing:-.06em;margin:45px 0 22px}}.proof-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}.proof-card{{padding:22px}}.pill{{display:inline-flex;border-radius:999px;background:rgba(120,255,176,.18);color:var(--green);padding:7px 10px;font-size:11px;font-weight:1000;letter-spacing:.15em}}.proof-card h3{{font-size:27px;line-height:1;margin:14px 0 9px;letter-spacing:-.04em}}.proof-card p{{color:var(--muted)}}.mini{{display:flex;gap:10px;flex-wrap:wrap;color:#cfe5f2;font-size:13px}}.mini span{{border:1px solid var(--line);border-radius:999px;padding:6px 10px}}.btns,.run-grid{{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}}.btn{{display:inline-flex;border-radius:999px;padding:12px 16px;border:1px solid var(--line);font-weight:1000;color:var(--text)}}.btn.primary{{background:var(--cyan);color:#06131f;border-color:transparent}}.run-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}.run-card{{padding:22px}}.smallcap{{font-size:12px;letter-spacing:.26em;text-transform:uppercase;color:var(--cyan);font-weight:1000}}table{{width:100%;border-collapse:separate;border-spacing:0;overflow:hidden}}th,td{{padding:14px 16px;text-align:left;border-bottom:1px solid var(--line)}}th{{font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:#a7bed0}}td span{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;color:#9fb8c9;font-size:12px}}tr:last-child td{{border-bottom:0}}.pass{{background:rgba(120,255,176,.18);color:var(--green);padding:6px 10px;border-radius:999px;font-size:12px}}.pending{{background:rgba(246,215,106,.18);color:var(--gold);padding:6px 10px;border-radius:999px;font-size:12px}}footer{{padding:50px 0 80px;color:var(--muted)}}@media(max-width:900px){{.hero,.proof-grid,.stats,.run-grid{{grid-template-columns:1fr}}.navlinks{{display:none}}}}</style></head>
<body><nav class="nav"><div class="brand">SkillOS Proof Command Center</div><div class="navlinks"><a href="#proofs">Proofs</a><a href="#run">Run / Regenerate</a><a href="proof-registry.json">Registry</a><a href="{REPO_URL}">GitHub</a></div></nav><main class="wrap">
<section class="hero"><div><div class="eyebrow">Always-fresh autonomous public proof hub</div><h1>Capabilities, proved in public.</h1><p class="lead">SkillOS turns GitHub Actions into a public proof system: benchmarks run, gates verify, receipts publish, proof pages render, and this command center refreshes automatically.</p><div class="btns"><a class="btn primary" href="{WORKFLOW_URL}">Run latest proof</a><a class="btn" href="proof-registry.json">Open proof registry</a></div></div><aside class="panel"><div class="smallcap">Latest flagship proof</div><div class="big">{latest.get('short_title','SkillOS Proof')}</div><p class="lead">{latest.get('description','Autonomous public proof.')}</p><p>Updated: <strong>{updated}</strong></p></aside></section>
<section class="stats"><div class="stat"><strong>{latest.get('agents','—')}</strong><span>virtual specialist agents</span></div><div class="stat"><strong>{latest.get('roles','—')}</strong><span>specialist roles</span></div><div class="stat"><strong>{latest.get('capture','—')}</strong><span>holdout capture</span></div><div class="stat"><strong>{latest.get('risk','—')}</strong><span>risk breach</span></div></section>
<section id="proofs"><h2 class="section-title">Public proofs.</h2><div class="proof-grid">{cards}</div></section>
<section id="run"><h2 class="section-title">Run or regenerate.</h2><div class="run-grid"><div class="run-card"><div class="smallcap">Run one proof</div><p>Open a proof card, click <b>Run on GitHub</b>, then click <b>Run workflow</b>.</p></div><div class="run-card"><div class="smallcap">Refresh hub</div><p>Generated outputs update this site, registry, report, badge, JSON receipt, and sitemap.</p></div><div class="run-card"><div class="smallcap">No human review</div><p>The workflow runs, verifies, commits generated outputs, and can deploy GitHub Pages autonomously.</p></div></div></section>
<section><h2 class="section-title">Latest proof status.</h2><table><thead><tr><th>Workflow</th><th>Status</th><th>Updated</th><th>Capture</th></tr></thead><tbody>{rows}</tbody></table></section></main><footer class="wrap">Public benchmark hub. No claim of achieved superintelligence, live revenue, legal advice, policy advice, investment advice, customer results, guaranteed profit, or Kardashev Type II achievement.</footer></body></html>'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default=f"data/{PROOF_ID}.json")
    parser.add_argument("--site", default="site")
    args = parser.parse_args()
    proof_path = Path(args.json)
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    site = Path(args.site)
    site.mkdir(parents=True, exist_ok=True)
    copy_if_exists(Path(f"site/{PROOF_PAGE}"), site / PROOF_PAGE)
    copy_if_exists(proof_path, site / "data" / f"{PROOF_ID}.json")
    copy_if_exists(Path(f"docs/{PROOF_ID}.md"), site / "docs" / f"{PROOF_ID}.md")
    copy_if_exists(Path(f"badges/{PROOF_ID}.svg"), site / "badges" / f"{PROOF_ID}.svg")
    registry_path = site / "proof-registry.json"
    proofs = load_registry(registry_path)
    proofs = [p for p in proofs if p.get("id") != PROOF_ID]
    m = proof["metrics"]
    proofs.insert(0, {
        "id": PROOF_ID,
        "title": proof["proof_title"],
        "short_title": "RSI Capability Liquidity Engine",
        "description": "Large autonomous specialist-agent capability marketplace with validation-gated RSI, skill release lanes, verifier courts, locked holdout tasks, negative controls, and public receipts.",
        "path": PROOF_PAGE,
        "json": f"data/{PROOF_ID}.json",
        "report": f"docs/{PROOF_ID}.md",
        "badge": f"badges/{PROOF_ID}.svg",
        "workflow": WORKFLOW,
        "workflow_url": WORKFLOW_URL,
        "proved": bool(m["proved"]),
        "agents": f"{m['virtual_specialist_agents']:,}",
        "roles": f"{m['specialist_roles']:,}",
        "capture": pct(m["locked_holdout_value_capture_rate"]),
        "risk": pct(m["risk_breach_rate"]),
        "value_captured": money(m["benchmark_capital_equivalent_value_captured"]),
        "updated_at": proof.get("generated_at", ""),
    })
    save_registry(registry_path, proofs)
    (site / "index.html").write_text(render_index(proofs), encoding="utf-8")
    (site / "sitemap.xml").write_text("\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{BASE_URL}</loc></url>',
        *[f'  <url><loc>{BASE_URL}{p.get("path")}</loc></url>' for p in proofs if p.get("path")],
        '</urlset>',
    ]), encoding="utf-8")
    (site / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")
    print(json.dumps({"published": True, "site": str(site), "index": str(site/'index.html'), "proof": str(site/PROOF_PAGE), "registry": str(registry_path)}, indent=2))


if __name__ == "__main__":
    main()
