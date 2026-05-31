#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
DOCS = ROOT / "docs"
BADGES = ROOT / "badges"
SLUG = "rsi-skill-provenance-ledger-proof"
TITLE = "Autonomous RSI Skill Provenance Ledger Proof"
PAGE = "rsi-skill-provenance-ledger-proof.html"

def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    proof_path = DATA / f"{SLUG}.json"
    if not proof_path.exists():
        raise SystemExit(f"Missing proof JSON: {proof_path}")
    proof = json.loads(proof_path.read_text(encoding="utf-8"))
    final = proof["final"]
    registry_path = SITE / "proof-registry.json"
    registry = []
    if registry_path.exists():
        try:
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            if not isinstance(registry, list):
                registry = []
        except Exception:
            registry = []
    entry = {
        "title": TITLE,
        "slug": SLUG,
        "page": PAGE,
        "json": f"data/{SLUG}.json",
        "docs": f"docs/{SLUG}.md",
        "badge": f"badges/{SLUG}.svg",
        "status": proof["status"],
        "generated_at_utc": proof["generated_at_utc"],
        "value_capture_percent": final["benchmark_value_capture_rate_percent"],
        "frontier_correct_percent": final["frontier_correct_rate_percent"],
        "provenance_integrity_percent": final["provenance_integrity_score"],
        "virtual_specialist_agents": proof["agent_system"]["virtual_specialist_agents"],
        "specialist_roles": proof["agent_system"]["specialist_roles"],
    }
    registry = [item for item in registry if item.get("slug") != SLUG]
    registry.insert(0, entry)
    registry_path.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # Copy public receipt/report/badge into site for direct public access.
    for src, dst in [
        (proof_path, SITE / "data" / f"{SLUG}.json"),
        (DOCS / f"{SLUG}.md", SITE / "docs" / f"{SLUG}.md"),
        (BADGES / f"{SLUG}.svg", SITE / "badges" / f"{SLUG}.svg"),
    ]:
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(src.read_bytes())

    card = f"""
<section id="{SLUG}" class="proof-card featured-proof">
  <p class="eyebrow">Newest SkillOS proof</p>
  <h2>{TITLE}</h2>
  <p>Verified traces become replayable, transferable, safe, reusable skills through validation-gated Recursive Self-Improvement.</p>
  <div class="metric-row">
    <span>{final['benchmark_value_capture_rate_percent']}% value capture</span>
    <span>{final['provenance_integrity_score']}% provenance integrity</span>
    <span>{proof['agent_system']['virtual_specialist_agents']:,} virtual agents</span>
  </div>
  <p><a class="button" href="{PAGE}">View proof</a> <a class="button secondary" href="data/{SLUG}.json">Inspect JSON</a></p>
</section>
""".strip()

    index = SITE / "index.html"
    if index.exists():
        text = index.read_text(encoding="utf-8")
        if SLUG not in text:
            if "</main>" in text:
                text = text.replace("</main>", card + "\n</main>", 1)
            elif "</body>" in text:
                text = text.replace("</body>", card + "\n</body>", 1)
            else:
                text += "\n" + card
            index.write_text(text, encoding="utf-8")
    else:
        index.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><title>SkillOS Proofs</title><style>body{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;background:#071421;color:#eef;padding:40px}}a{{color:#86f8ff}}.proof-card{{border:1px solid rgba(255,255,255,.2);border-radius:24px;padding:24px;max-width:960px}}.button{{display:inline-block;padding:10px 14px;border-radius:999px;background:#86f8ff;color:#071421;text-decoration:none;font-weight:800}}.secondary{{background:transparent;color:#eef;border:1px solid rgba(255,255,255,.3)}}.metric-row{{display:flex;gap:12px;flex-wrap:wrap}}.metric-row span{{padding:8px 10px;border-radius:999px;background:rgba(255,255,255,.08)}}.eyebrow{{color:#86f8ff;text-transform:uppercase;letter-spacing:.15em}}</style></head><body><main>{card}</main></body></html>""", encoding="utf-8")

    pages = ["index.html", PAGE]
    sitemap = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n" + "\n".join(f"  <url><loc>https://montrealai.github.io/skillos/{p}</loc></url>" for p in pages) + "\n</urlset>\n"
    (SITE / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (SITE / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n", encoding="utf-8")
    print(json.dumps({"status": "PUBLISHED_TO_HUB", "page": f"site/{PAGE}", "registry": "site/proof-registry.json"}, indent=2))

if __name__ == "__main__":
    main()
