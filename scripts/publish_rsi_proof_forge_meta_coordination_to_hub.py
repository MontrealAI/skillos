#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
from pathlib import Path

PROOF_ID = "rsi-proof-forge-meta-coordination-proof"
TITLE = "Autonomous RSI Proof Forge Meta-Coordination Proof"
HREF = f"{PROOF_ID}.html"
BASE_URL = "https://montrealai.github.io/skillos/"

CSS = """
<style id="rsi-proof-forge-hub-css">
.rsi-proof-forge-feature{max-width:1180px;margin:32px auto;padding:32px;border:1px solid rgba(255,255,255,.16);border-radius:28px;background:linear-gradient(135deg,rgba(116,245,255,.12),rgba(127,255,176,.08));box-shadow:0 20px 80px rgba(0,0,0,.24)}
.rsi-proof-forge-feature h2{font-size:clamp(32px,4vw,58px);letter-spacing:-.06em;margin:0 0 12px;color:#eff8ff}.rsi-proof-forge-feature p{color:#bdd0e9;max-width:880px;font-size:18px}.rsi-proof-forge-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:22px 0}.rsi-proof-forge-kpis div{border:1px solid rgba(255,255,255,.14);border-radius:18px;padding:16px;background:rgba(255,255,255,.06)}.rsi-proof-forge-kpis strong{display:block;color:#7fffb0;font-size:28px}.rsi-proof-forge-feature a{display:inline-flex;align-items:center;margin-right:10px;margin-top:8px;padding:12px 16px;border-radius:999px;text-decoration:none;font-weight:900}.rsi-proof-forge-primary{background:#74f5ff;color:#061727}.rsi-proof-forge-secondary{border:1px solid rgba(255,255,255,.18);color:#eff8ff}.rsi-proof-forge-badge{display:inline-flex;padding:7px 12px;border-radius:999px;background:rgba(127,255,176,.16);color:#7fffb0;font-size:12px;font-weight:900;letter-spacing:.1em;text-transform:uppercase}@media(max-width:800px){.rsi-proof-forge-kpis{grid-template-columns:1fr}}
</style>
"""


def pct(x: float) -> str:
    return f"{100*x:.2f}%"


def money(x: float) -> str:
    if abs(x) >= 1e12: return f"${x/1e12:,.2f}T"
    if abs(x) >= 1e9: return f"${x/1e9:,.2f}B"
    return f"${x:,.0f}"


def ensure_index(site: Path) -> Path:
    index = site / "index.html"
    if index.exists(): return index
    index.write_text("""<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>SkillOS Proof Command Center</title><style>body{margin:0;background:#071827;color:#eff8ff;font-family:Inter,system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:40px 24px}a{color:#74f5ff}</style></head><body><main><h1>SkillOS Proof Command Center</h1></main></body></html>""", encoding="utf-8")
    return index


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = Path(args.root)
    site = root / "site"
    site.mkdir(parents=True, exist_ok=True)
    result = json.loads((root / "data" / f"{PROOF_ID}.json").read_text(encoding="utf-8"))
    s = result["selected_release_summary"]
    index = ensure_index(site)
    doc = index.read_text(encoding="utf-8")
    if "rsi-proof-forge-hub-css" not in doc:
        doc = doc.replace("</head>", CSS + "\n</head>") if "</head>" in doc else CSS + doc
    card = f"""
<section id="rsi-proof-forge-meta-coordination" class="rsi-proof-forge-feature">
  <span class="rsi-proof-forge-badge">New autonomous RSI meta-proof</span>
  <h2>Proof Forge Meta-Coordination</h2>
  <p>SkillOS now tests the proof system itself: a large specialist-agent proof market recursively improves how hypotheses become verified receipts, public reports, executive webpages, and reusable future proof machinery.</p>
  <div class="rsi-proof-forge-kpis">
    <div><strong>{result['scale']['virtual_specialist_agents']:,}</strong><span>virtual specialist agents</span></div>
    <div><strong>{result['scale']['verifier_courts']}</strong><span>verifier courts</span></div>
    <div><strong>{pct(s['value_capture_rate'])}</strong><span>holdout value capture</span></div>
    <div><strong>{money(s['captured_value'])}</strong><span>benchmark value captured</span></div>
  </div>
  <a class="rsi-proof-forge-primary" href="{HREF}">View proof</a>
  <a class="rsi-proof-forge-secondary" href="data/{PROOF_ID}.json">JSON receipt</a>
  <a class="rsi-proof-forge-secondary" href="docs/{PROOF_ID}.md">Report</a>
</section>
"""
    if "id=\"rsi-proof-forge-meta-coordination\"" not in doc and "id='rsi-proof-forge-meta-coordination'" not in doc:
        if "</main>" in doc:
            doc = doc.replace("</main>", card + "\n</main>", 1)
        elif "</body>" in doc:
            doc = doc.replace("</body>", card + "\n</body>", 1)
        else:
            doc += card
    index.write_text(doc, encoding="utf-8")

    registry_path = site / "proof-registry.json"
    registry = []
    if registry_path.exists():
        try:
            loaded = json.loads(registry_path.read_text(encoding="utf-8"))
            registry = loaded if isinstance(loaded, list) else loaded.get("proofs", [])
        except Exception:
            registry = []
    entry = {
        "id": PROOF_ID,
        "title": TITLE,
        "href": HREF,
        "status": "passing" if result.get("proved") else "failing",
        "proof_version": result.get("proof_version"),
        "generated_at_utc": result.get("generated_at_utc"),
        "value_capture_rate": s.get("value_capture_rate"),
        "proof_credibility": s.get("mean_proof_credibility"),
        "coordination_quality": s.get("mean_coordination_quality"),
        "fingerprint": result.get("proof_fingerprint"),
        "workflow_url": result.get("workflow_url"),
    }
    registry = [p for p in registry if p.get("id") != PROOF_ID]
    registry.insert(0, entry)
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True), encoding="utf-8")

    sitemap = site / "sitemap.xml"
    urls = [BASE_URL, BASE_URL + HREF]
    if registry:
        for p in registry:
            h = p.get("href")
            if h and (BASE_URL + h) not in urls:
                urls.append(BASE_URL + h)
    now = dt.datetime.now(dt.timezone.utc).date().isoformat()
    sitemap.write_text("<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n" + "\n".join(f"  <url><loc>{html.escape(u)}</loc><lastmod>{now}</lastmod></url>" for u in urls) + "\n</urlset>\n", encoding="utf-8")
    (site / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}sitemap.xml\n", encoding="utf-8")
    print(f"Updated {index} and registry with {PROOF_ID}")


if __name__ == "__main__":
    main()
