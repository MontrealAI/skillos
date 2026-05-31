#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SITE = ROOT / "site"
DOCS = ROOT / "docs"
PROOF = DATA / "rsi_corporate_capability_frontier_proof.json"
PAGE = SITE / "rsi-corporate-capability-frontier-proof.html"
START = "<!-- SKILLOS_CORPORATE_CAPABILITY_FRONTIER_START -->"
END = "<!-- SKILLOS_CORPORATE_CAPABILITY_FRONTIER_END -->"

SITE.mkdir(parents=True, exist_ok=True)


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


def block(proof: dict) -> str:
    f = proof["final"]
    c = proof["comparisons"]
    return f'''{START}
<style>
.skillos-frontier-wrap{{margin:32px auto;max-width:1240px;padding:0 20px;color:#f5fbff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif}}
.skillos-frontier-card{{position:relative;overflow:hidden;border:1px solid rgba(255,255,255,.18);border-radius:30px;padding:26px;background:radial-gradient(circle at 90% 0,rgba(150,115,255,.32),transparent 35%),linear-gradient(135deg,rgba(8,92,104,.52),rgba(38,41,96,.72));box-shadow:0 24px 80px rgba(0,0,0,.28)}}
.skillos-frontier-grid{{display:grid;grid-template-columns:1.15fr .85fr;gap:20px;align-items:center}}.skillos-frontier-eyebrow{{color:#83f7ff;text-transform:uppercase;letter-spacing:.18em;font-weight:950;font-size:12px}}
.skillos-frontier-title{{font-size:clamp(36px,5vw,74px);line-height:.92;letter-spacing:-.065em;margin:12px 0;color:#f5fbff}}.skillos-frontier-card p{{color:#bfd0e0;line-height:1.55;font-size:17px}}
.skillos-frontier-metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:18px}}.skillos-frontier-metric{{border:1px solid rgba(255,255,255,.16);border-radius:18px;padding:14px;background:rgba(255,255,255,.07)}}.skillos-frontier-metric strong{{display:block;color:#82ffb4;font-size:27px;letter-spacing:-.04em}}.skillos-frontier-metric span{{color:#bfd0e0;font-size:13px}}
.skillos-frontier-btns{{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}}.skillos-frontier-btn{{display:inline-flex;padding:12px 17px;border-radius:999px;background:#83f7ff;color:#061521;font-weight:950;text-decoration:none}}.skillos-frontier-btn.secondary{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);color:#f5fbff}}
@media(max-width:900px){{.skillos-frontier-grid,.skillos-frontier-metrics{{grid-template-columns:1fr}}}}
</style>
<section class="skillos-frontier-wrap" id="corporate-capability-frontier-proof">
  <div class="skillos-frontier-card">
    <div class="skillos-frontier-grid">
      <div>
        <div class="skillos-frontier-eyebrow">Featured autonomous proof · edge of corporate capability</div>
        <h2 class="skillos-frontier-title">Corporate Capability Frontier Proof</h2>
        <p>SkillOS now publishes a 100% autonomous RSI proof showing a large specialist-agent superorganization recursively improving the coordination layer that turns capital, compute, energy, data, trust, talent, product, distribution, validation, risk control, and reinvestment into compounding productive capability.</p>
        <div class="skillos-frontier-btns">
          <a class="skillos-frontier-btn" href="rsi-corporate-capability-frontier-proof.html">View proof</a>
          <a class="skillos-frontier-btn secondary" href="https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-corporate-capability-frontier-proof.yml">Run on GitHub</a>
          <a class="skillos-frontier-btn secondary" href="../data/rsi_corporate_capability_frontier_proof.json">JSON receipt</a>
        </div>
      </div>
      <div class="skillos-frontier-metrics">
        <div class="skillos-frontier-metric"><strong>{proof['agent_system']['agent_count']:,}</strong><span>deterministic virtual agents</span></div>
        <div class="skillos-frontier-metric"><strong>{proof['agent_system']['role_count']:,}</strong><span>specialist roles</span></div>
        <div class="skillos-frontier-metric"><strong>{f['benchmark_value_capture_rate_percent']}%</strong><span>benchmark value capture</span></div>
        <div class="skillos-frontier-metric"><strong>{money(c['vs_single_corporate_generalist']['benchmark_value_captured_gain_usd'])}</strong><span>over single generalist</span></div>
      </div>
    </div>
  </div>
</section>
{END}'''


def blank_page(title: str, body: str) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{esc(title)}</title><style>body{{margin:0;background:linear-gradient(135deg,#061521,#172743 55%,#25245f);color:#f5fbff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif}}nav{{padding:14px 22px;background:rgba(5,16,28,.92);border-bottom:1px solid rgba(255,255,255,.16);display:flex;gap:16px;flex-wrap:wrap}}nav a{{color:#83f7ff;text-decoration:none;font-weight:850}}main{{max-width:1240px;margin:auto;padding:28px 0 70px}}h1{{padding:0 20px;font-size:clamp(38px,6vw,80px);letter-spacing:-.065em}}</style></head><body><nav><a href="index.html">Command Center</a><a href="proofs.html">Proofs</a><a href="multi-agent.html">Multi-Agent</a><a href="runbook.html">Run</a><a href="https://github.com/MontrealAI/skillos">GitHub</a></nav><main><h1>{esc(title)}</h1>{body}</main></body></html>'''


def patch_html(path: Path, title: str, insert: str) -> None:
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = blank_page(title, "")

    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
    if pattern.search(text):
        text = pattern.sub(insert, text)
    elif "</main>" in text:
        text = text.replace("</main>", insert + "\n</main>", 1)
    elif "<body" in text:
        text = re.sub(r"(<body[^>]*>)", r"\1\n" + insert, text, count=1, flags=re.I)
    else:
        text = insert + "\n" + text

    path.write_text(text, encoding="utf-8")


def write_registry(proof: dict) -> None:
    registry_path = SITE / "proof-index.json"
    if registry_path.exists():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            registry = {"proofs": []}
    else:
        registry = {"proofs": []}

    entry = {
        "id": "rsi-corporate-capability-frontier-proof",
        "title": "Autonomous RSI Corporate Capability Frontier Proof",
        "status": "passing" if proof["proved"] else "failing",
        "page_url": "rsi-corporate-capability-frontier-proof.html",
        "workflow": ".github/workflows/autonomous-rsi-corporate-capability-frontier-proof.yml",
        "json": "../data/rsi_corporate_capability_frontier_proof.json",
        "markdown": "../docs/rsi_corporate_capability_frontier_proof.md",
        "agents": proof["agent_system"]["agent_count"],
        "roles": proof["agent_system"]["role_count"],
        "rsi_releases": proof["rsi_release_count"],
        "value_capture_percent": proof["final"]["benchmark_value_capture_rate_percent"],
        "updated_at": proof["generated_at_utc"],
    }

    proofs = [p for p in registry.get("proofs", []) if p.get("id") != entry["id"]]
    proofs.insert(0, entry)
    registry["proofs"] = proofs
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_sitemap() -> None:
    urls = [
        "https://montrealai.github.io/skillos/",
        "https://montrealai.github.io/skillos/proofs.html",
        "https://montrealai.github.io/skillos/multi-agent.html",
        "https://montrealai.github.io/skillos/runbook.html",
        "https://montrealai.github.io/skillos/rsi-corporate-capability-frontier-proof.html",
    ]
    body = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    (SITE / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{body}\n</urlset>\n', encoding="utf-8")
    (SITE / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n", encoding="utf-8")


def write_runbook(proof: dict) -> None:
    body = f'''<section class="skillos-frontier-wrap"><div class="skillos-frontier-card"><div class="skillos-frontier-eyebrow">Run / regenerate</div><h2 class="skillos-frontier-title">Run the Corporate Capability Frontier proof.</h2><p>Open GitHub Actions, choose <strong>Autonomous RSI Corporate Capability Frontier Proof</strong>, click <strong>Run workflow</strong>, and keep <code>deploy_pages</code> enabled. The Action regenerates the receipt, report, visual page, homepage integration, sitemap, and badge without human review.</p><p><a class="skillos-frontier-btn" href="https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-corporate-capability-frontier-proof.yml">Run on GitHub</a></p></div></section>'''
    patch_html(SITE / "runbook.html", "Run SkillOS Proofs", body)


def main() -> None:
    if not PROOF.exists():
        raise SystemExit(f"Missing proof receipt: {PROOF}")
    if not PAGE.exists():
        raise SystemExit(f"Missing specific proof page: {PAGE}")
    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    featured = block(proof)

    patch_html(SITE / "index.html", "SkillOS Proof Command Center", featured)
    patch_html(SITE / "proofs.html", "SkillOS Proofs", featured)
    patch_html(SITE / "multi-agent.html", "SkillOS Multi-Agent Proofs", featured)
    patch_html(SITE / "actions.html", "SkillOS Actions", featured)
    patch_html(SITE / "receipts.html", "SkillOS Receipts", featured)
    write_runbook(proof)
    write_registry(proof)
    write_sitemap()

    print(json.dumps({
        "status": "PUBLIC_SITE_UPDATED",
        "page": "site/rsi-corporate-capability-frontier-proof.html",
        "index": "site/index.html",
        "proofs": "site/proofs.html",
        "registry": "site/proof-index.json",
        "sitemap": "site/sitemap.xml",
    }, indent=2))


if __name__ == "__main__":
    main()
