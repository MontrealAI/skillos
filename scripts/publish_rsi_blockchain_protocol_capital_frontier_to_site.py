from __future__ import annotations
import json, re, html
from pathlib import Path

SLUG = "rsi-blockchain-protocol-capital-frontier-proof"
PROOF_JSON = Path(f"data/{SLUG}.json")
INDEX = Path("site/index.html")
REGISTRY = Path("site/proof-registry.json")
SITEMAP = Path("site/sitemap.xml")
ROBOTS = Path("site/robots.txt")
FEATURE_ID = "rsi-blockchain-protocol-capital-frontier-feature"


def base_home(proof: dict) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SkillOS Proof Command Center</title><style>
body{{margin:0;background:linear-gradient(135deg,#061727,#152049 70%,#0b4c59);color:#ecf7ff;font-family:Inter,system-ui,sans-serif}}a{{color:#7df9ff;text-decoration:none}}.wrap{{max-width:1180px;margin:0 auto;padding:40px 24px}}.nav{{padding:12px 22px;background:#061422;position:sticky;top:0;display:flex;justify-content:space-between;font-weight:900}}.hero{{padding:42px;border:1px solid rgba(255,255,255,.18);border-radius:28px;background:rgba(255,255,255,.08);margin:40px 0}}h1{{font-size:72px;line-height:.9;letter-spacing:-.07em;margin:0 0 18px}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}.card{{padding:24px;border:1px solid rgba(255,255,255,.18);border-radius:24px;background:rgba(255,255,255,.08)}}.big{{color:#6dffac;font-size:34px;font-weight:900}}@media(max-width:800px){{.grid{{grid-template-columns:1fr}}h1{{font-size:48px}}}}</style></head><body><div class="nav"><a href="index.html">SkillOS Proof Command Center</a><a href="https://github.com/MontrealAI/skillos/actions">Run proofs on GitHub</a></div><main class="wrap"><section class="hero"><h1>Autonomous public proofs.</h1><p>Every proof is generated, verified, published, and refreshed by GitHub Actions.</p></section>{feature_block(proof)}</main></body></html>'''


def feature_block(proof: dict) -> str:
    hr = proof["human_readable_metrics"]
    scale = proof["system_scale"]
    return f'''
<section id="{FEATURE_ID}" class="hero" data-proof-slug="{SLUG}">
  <div style="letter-spacing:.24em;color:#7df9ff;text-transform:uppercase;font-weight:900;font-size:12px">Featured autonomous blockchain RSI proof</div>
  <h1 style="font-size:56px">Blockchain Protocol Capital Frontier.</h1>
  <p style="font-size:18px;line-height:1.55;max-width:850px">A validation-gated autonomous protocol superorganization: many specialist councils, one measured decision market, recursive release control, locked holdout discipline, and capital-to-capability compounding under risk courts.</p>
  <div class="grid">
    <div class="card"><div class="big">{hr['value_capture_percent']}</div><div>holdout value capture</div></div>
    <div class="card"><div class="big">{scale['virtual_specialist_agents']:,}</div><div>virtual specialist agents</div></div>
    <div class="card"><div class="big">{hr['value_over_static_dao_committee']}</div><div>over static DAO committee</div></div>
  </div>
  <p style="margin-top:24px"><a class="card" style="display:inline-block;font-weight:900" href="{SLUG}.html">Open the proof webpage →</a> <a class="card" style="display:inline-block;font-weight:900" href="https://github.com/MontrealAI/skillos/actions/workflows/autonomous-rsi-blockchain-protocol-capital-frontier-proof.yml">Run / regenerate on GitHub →</a></p>
</section>'''


def inject_feature(index_html: str, proof: dict) -> str:
    block = feature_block(proof)
    index_html = re.sub(rf"\n?<section id=[\"']{FEATURE_ID}[\"'][\s\S]*?</section>", "", index_html)
    if "</main>" in index_html:
        return index_html.replace("</main>", block + "\n</main>")
    if "</body>" in index_html:
        return index_html.replace("</body>", block + "\n</body>")
    return index_html + block


def update_registry(proof: dict) -> None:
    REGISTRY.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if REGISTRY.exists():
        try:
            raw = json.loads(REGISTRY.read_text(encoding="utf-8"))
            existing = raw if isinstance(raw, list) else raw.get("proofs", [])
        except Exception:
            existing = []
    row = {
        "title": proof["proof_name"],
        "slug": SLUG,
        "page_url": f"{SLUG}.html",
        "json_url": f"data/{SLUG}.json",
        "report_url": f"docs/{SLUG}.md",
        "badge_url": f"badges/{SLUG}.svg",
        "status": "passing" if proof["proved"] else "failed",
        "generated_at": proof["generated_at"],
        "summary": "Autonomous blockchain protocol RSI proof with locked holdout evaluation and multi-agent coordination.",
        "metrics": proof["human_readable_metrics"],
    }
    existing = [x for x in existing if x.get("slug") != SLUG]
    existing.insert(0, row)
    REGISTRY.write_text(json.dumps({"proofs": existing}, indent=2, sort_keys=True), encoding="utf-8")


def write_sitemap() -> None:
    pages = ["index.html", f"{SLUG}.html"]
    if REGISTRY.exists():
        try:
            for p in json.loads(REGISTRY.read_text(encoding="utf-8")).get("proofs", []):
                if p.get("page_url") and p["page_url"] not in pages:
                    pages.append(p["page_url"])
        except Exception:
            pass
    urls = "\n".join(f"  <url><loc>https://montrealai.github.io/skillos/{html.escape(p)}</loc></url>" for p in pages)
    SITEMAP.write_text(f"<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n{urls}\n</urlset>\n", encoding="utf-8")
    ROBOTS.write_text("User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n", encoding="utf-8")


def main() -> None:
    proof = json.loads(PROOF_JSON.read_text(encoding="utf-8"))
    INDEX.parent.mkdir(parents=True, exist_ok=True)
    if INDEX.exists():
        INDEX.write_text(inject_feature(INDEX.read_text(encoding="utf-8"), proof), encoding="utf-8")
    else:
        INDEX.write_text(base_home(proof), encoding="utf-8")
    update_registry(proof)
    write_sitemap()
    print("Updated site/index.html, site/proof-registry.json, sitemap.xml, and robots.txt")


if __name__ == "__main__":
    main()
