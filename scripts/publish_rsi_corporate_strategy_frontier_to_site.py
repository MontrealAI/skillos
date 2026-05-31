#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
SLUG = "rsi-corporate-strategy-frontier-proof"
PROOF = ROOT / "data" / f"{SLUG}.json"
PAGE = SITE / f"{SLUG}.html"
INDEX = SITE / "index.html"
REGISTRY = SITE / "proof-registry.json"
BASE_URL = "https://montrealai.github.io/skillos/"
ACTION_URL = "https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-corporate-strategy-frontier-proof.yml"
START = "<!-- SKILLOS_CORPORATE_STRATEGY_FRONTIER_START -->"
END = "<!-- SKILLOS_CORPORATE_STRATEGY_FRONTIER_END -->"


def dollars(x: float) -> str:
    if abs(x) >= 1e12: return f"${x/1e12:.2f}T"
    if abs(x) >= 1e9: return f"${x/1e9:.2f}B"
    if abs(x) >= 1e6: return f"${x/1e6:.2f}M"
    return f"${x:.0f}"

def pct(x: float) -> str: return f"{x:.3f}%"


def proof_section(proof: dict) -> str:
    s = proof["summary"]
    return f'''{START}
<style>
.skillos-frontier-proof{{margin:48px auto;padding:0;width:min(1180px,calc(100% - 32px));font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;color:#effaff}}
.skillos-frontier-proof *{{box-sizing:border-box}}.skillos-frontier-card{{position:relative;overflow:hidden;border:1px solid rgba(255,255,255,.20);border-radius:30px;background:linear-gradient(135deg,rgba(125,247,255,.16),rgba(124,255,178,.09) 38%,rgba(255,255,255,.07));box-shadow:0 24px 90px rgba(0,0,0,.25);padding:30px}}
.skillos-frontier-card:before{{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:28px 28px;mask-image:linear-gradient(#000,transparent);pointer-events:none}}
.skillos-frontier-kicker{{position:relative;color:#7df7ff;font-weight:950;letter-spacing:.22em;text-transform:uppercase;font-size:12px}}.skillos-frontier-proof h2{{position:relative;margin:12px 0;font-size:clamp(34px,5vw,68px);line-height:.94;letter-spacing:-.07em;color:#f6fbff}}
.skillos-frontier-proof p{{position:relative;color:#c7d7ea;max-width:850px}}.skillos-frontier-metrics{{position:relative;display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0}}@media(max-width:800px){{.skillos-frontier-metrics{{grid-template-columns:repeat(2,1fr)}}}}
.skillos-frontier-metric{{border:1px solid rgba(255,255,255,.18);border-radius:18px;padding:16px;background:rgba(255,255,255,.08)}}.skillos-frontier-metric b{{display:block;color:#7cffb2;font-size:28px;line-height:1}}.skillos-frontier-metric span{{color:#c6d4e7;font-size:13px}}
.skillos-frontier-chain{{position:relative;margin:18px 0;padding:18px;border-radius:20px;border:1px solid rgba(255,255,255,.18);background:rgba(0,0,0,.14);font-weight:950;font-size:clamp(18px,2.8vw,34px);letter-spacing:-.04em;line-height:1.08}}
.skillos-frontier-actions{{position:relative;display:flex;gap:12px;flex-wrap:wrap;margin-top:20px}}.skillos-frontier-actions a{{display:inline-flex;border-radius:999px;padding:12px 16px;font-weight:950;text-decoration:none}}.skillos-frontier-actions a:first-child{{background:#7df7ff;color:#05111a}}.skillos-frontier-actions a:not(:first-child){{border:1px solid rgba(255,255,255,.22);color:#effaff;background:rgba(255,255,255,.08)}}
</style>
<section id="corporate-strategy-frontier-proof" class="skillos-frontier-proof">
  <div class="skillos-frontier-card">
    <div class="skillos-frontier-kicker">Newest autonomous public proof · corporate strategy RSI</div>
    <h2>Corporate Strategy Frontier Proof</h2>
    <p>A reproducible GitHub Action proof that a large specialist-agent organization recursively improves its coordination protocol for corporate strategy: capital, compute, energy, data, trust, talent, product, distribution, validation, risk control, and reinvestment become compounding productive capability.</p>
    <div class="skillos-frontier-metrics">
      <div class="skillos-frontier-metric"><b>{s['agents']:,}</b><span>virtual specialist agents</span></div>
      <div class="skillos-frontier-metric"><b>{pct(s['value_capture_percent'])}</b><span>benchmark value capture</span></div>
      <div class="skillos-frontier-metric"><b>{pct(s['frontier_equivalent_percent'])}</b><span>frontier-equivalent strategy decisions</span></div>
      <div class="skillos-frontier-metric"><b>{dollars(s['value_over_static_committee'])}</b><span>over static committee baseline</span></div>
    </div>
    <div class="skillos-frontier-chain">capital → compute → energy → data → trust → talent → product → distribution → validation → risk control → reinvestment → compounding productive capability</div>
    <p>This does not claim achieved superintelligence, audited revenue, investment advice, or Kardashev Type II civilization. It makes the corporate strategy mechanism underneath that thesis publicly testable and rerunnable.</p>
    <div class="skillos-frontier-actions">
      <a href="{SLUG}.html">View proof webpage</a>
      <a href="data/{SLUG}.json">JSON receipt</a>
      <a href="docs/{SLUG}.md">Report</a>
      <a href="{ACTION_URL}">Run on GitHub</a>
    </div>
  </div>
</section>
{END}'''


def standalone_index(section: str) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>SkillOS Proof Command Center</title><style>body{{margin:0;background:radial-gradient(circle at 20% 0,#155f68,#111b3d 45%,#071421);color:#effaff;font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif}}.top{{position:sticky;top:0;padding:14px 22px;background:rgba(5,16,25,.88);border-bottom:1px solid rgba(255,255,255,.16);display:flex;justify-content:space-between}}a{{color:#7df7ff}}.hero{{width:min(1180px,calc(100% - 32px));margin:0 auto;padding:60px 0 10px}}h1{{font-size:clamp(46px,7vw,96px);line-height:.9;letter-spacing:-.08em;margin:0 0 14px}}</style></head><body><div class="top"><b>SkillOS Proof Command Center</b><a href="https://github.com/MontrealAI/skillos">GitHub</a></div><main><section class="hero"><h1>Autonomous public proofs.</h1><p>Fresh, rerunnable proof pages generated by GitHub Actions.</p></section>{section}</main></body></html>'''


def update_registry(proof: dict) -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    if REGISTRY.exists():
        try: registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        except json.JSONDecodeError: registry = {"proofs": []}
    else:
        registry = {"proofs": []}
    proofs = [p for p in registry.get("proofs", []) if p.get("slug") != SLUG]
    s = proof["summary"]
    proofs.insert(0, {
        "slug": SLUG,
        "title": proof["proof_name"],
        "page": f"{SLUG}.html",
        "json": f"data/{SLUG}.json",
        "report": f"docs/{SLUG}.md",
        "badge": f"badges/{SLUG}.svg",
        "status": "passing" if proof.get("proved") else "failing",
        "agents": s["agents"],
        "specialist_roles": s["specialist_roles"],
        "value_capture_percent": s["value_capture_percent"],
        "frontier_equivalent_percent": s["frontier_equivalent_percent"],
        "risk_breach_rate_percent": s["risk_breach_rate_percent"],
        "protocol_fingerprint": s["protocol_fingerprint"],
    })
    registry["proofs"] = proofs[:80]
    REGISTRY.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_sitemap() -> None:
    urls = [BASE_URL, BASE_URL + f"{SLUG}.html"]
    for p in sorted(SITE.glob("*.html")):
        u = BASE_URL + p.name
        if u not in urls: urls.append(u)
    sitemap = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n" + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    (SITE / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")


def main() -> None:
    proof = json.loads(PROOF.read_text(encoding="utf-8"))
    SITE.mkdir(parents=True, exist_ok=True)
    section = proof_section(proof)
    if INDEX.exists():
        text = INDEX.read_text(encoding="utf-8")
        if START in text and END in text:
            text = re.sub(re.escape(START) + r".*?" + re.escape(END), section, text, flags=re.S)
        elif "</main>" in text:
            text = text.replace("</main>", section + "\n</main>", 1)
        elif "</body>" in text:
            text = text.replace("</body>", section + "\n</body>", 1)
        else:
            text += "\n" + section
    else:
        text = standalone_index(section)
    INDEX.write_text(text, encoding="utf-8")
    update_registry(proof)
    update_sitemap()
    print(json.dumps({"published": True, "index": str(INDEX), "proof_page": str(PAGE), "registry": str(REGISTRY)}, indent=2))

if __name__ == "__main__":
    main()
