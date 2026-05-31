#!/usr/bin/env python3
from __future__ import annotations
import html, json, shutil, sys
from pathlib import Path
from typing import Any

PROOF_ID = "rsi-objective-integrity-firewall-proof"
TITLE = "Autonomous RSI Objective Integrity Firewall Proof"
SITE_BASE_URL = "https://montrealai.github.io/skillos/"
MAX_PROOFS = 80

def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(1)

def read_json(path: Path, default: Any) -> Any:
    if not path.exists(): return default
    try: return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError: return default

def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)

def atomic_json(path: Path, obj: Any) -> None:
    atomic_text(path, json.dumps(obj, indent=2, sort_keys=True) + "\n")

def normalize_registry(raw: Any) -> dict[str, Any]:
    if isinstance(raw, list):
        proofs = [p for p in raw if isinstance(p, dict)]
        return {"schema_version": 2, "proofs": proofs}
    if isinstance(raw, dict):
        proofs = raw.get("proofs", [])
        if not isinstance(proofs, list): proofs = []
        raw = dict(raw); raw["schema_version"] = max(int(raw.get("schema_version", 2) or 2), 2); raw["proofs"] = [p for p in proofs if isinstance(p, dict)]
        return raw
    return {"schema_version": 2, "proofs": []}

def identity(p: dict[str, Any]) -> str:
    return str(p.get("id") or p.get("proof_id") or p.get("href") or p.get("title") or "")

def frac(x: Any) -> float:
    try: v = float(x)
    except Exception: return 0.0
    return v/100.0 if v > 1.5 else v

def pct(x: Any, digits: int = 1) -> str:
    return f"{100*frac(x):.{digits}f}%"

def render_index(registry: dict[str, Any], latest: dict[str, Any]) -> str:
    proofs = registry.get("proofs", [])
    cards=[]
    for p in proofs[:18]:
        href = html.escape(str(p.get("href", "#")))
        title = html.escape(str(p.get("title", p.get("id", "Proof"))))
        headline = html.escape(str(p.get("headline", p.get("summary", "Autonomous public proof"))))
        metrics = p.get("metrics", {}) if isinstance(p.get("metrics"), dict) else {}
        cards.append(f"<article class='card'><div class='tag'>public proof</div><h3><a href='{href}'>{title}</a></h3><p>{headline}</p><div class='mini'><span>{pct(metrics.get('value_capture'))} capture</span><span>{pct(metrics.get('risk'),2)} risk</span></div><a class='btn' href='{href}'>View proof</a></article>")
    latest_metrics = latest.get("metrics", {})
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>SkillOS Proof Command Center</title>
<style>
:root{{--bg:#071321;--panel:rgba(255,255,255,.075);--line:rgba(255,255,255,.16);--text:#f2f8ff;--muted:#c4d5e7;--cyan:#8df5ff;--green:#7dffb2}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 20% 0%,rgba(44,205,223,.22),transparent 32%),radial-gradient(circle at 78% 0%,rgba(131,91,255,.22),transparent 36%),linear-gradient(135deg,#071a25,#111a3c 65%,#0b1326);color:var(--text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:32px 32px;mask-image:linear-gradient(to bottom,black,transparent 85%);pointer-events:none}}a{{color:var(--cyan);text-decoration:none}}nav{{position:sticky;top:0;z-index:5;height:58px;background:rgba(4,15,27,.88);backdrop-filter:blur(14px);border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;padding:0 22px}}nav strong{{color:var(--cyan)}}nav span{{display:flex;gap:20px;font-weight:800;font-size:14px}}.wrap{{width:min(1220px,92vw);margin:0 auto;padding:62px 0}}.hero,.card,.metric{{background:linear-gradient(180deg,rgba(255,255,255,.10),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:28px;box-shadow:0 22px 80px rgba(0,0,0,.25)}}.hero{{padding:38px}}.eyebrow,.tag{{color:var(--cyan);letter-spacing:.16em;text-transform:uppercase;font-weight:900;font-size:12px}}h1{{font-size:clamp(48px,7vw,92px);line-height:.88;letter-spacing:-.08em;margin:16px 0}}h2{{font-size:clamp(32px,4vw,56px);letter-spacing:-.06em}}p{{color:var(--muted);line-height:1.5}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:26px 0}}.metric{{padding:20px}}.metric b{{display:block;color:var(--green);font-size:34px}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}}.card{{padding:24px}}.mini{{display:flex;gap:12px;flex-wrap:wrap;margin:14px 0}}.mini span{{border:1px solid var(--line);border-radius:999px;padding:7px 10px;color:#dff7ff;background:rgba(255,255,255,.06)}}.btn{{display:inline-block;border-radius:999px;background:var(--cyan);color:#001522;font-weight:900;padding:12px 17px}}@media(max-width:850px){{.metrics,.grid{{grid-template-columns:1fr}}nav span{{display:none}}}}
</style></head><body><nav><strong>SkillOS Proof Command Center</strong><span><a href='proof-registry.json'>Registry</a><a href='https://github.com/MontrealAI/skillos/actions'>Run</a><a href='https://github.com/MontrealAI/skillos'>GitHub</a></span></nav><main class='wrap'><section class='hero'><div class='eyebrow'>Always-fresh autonomous public proof layer</div><h1>Proofs that get harder to fake.</h1><p>SkillOS turns work into traces, traces into verified skills, skills into releases, and releases into stronger future work. This command center is rebuilt by GitHub Actions from public receipts.</p><div class='metrics'><div class='metric'><b>{len(proofs)}</b><span>registered proofs</span></div><div class='metric'><b>{pct(latest_metrics.get('value_capture'))}</b><span>latest capture</span></div><div class='metric'><b>{pct(latest_metrics.get('objective_fidelity'))}</b><span>objective fidelity</span></div><div class='metric'><b>{pct(latest_metrics.get('risk'),2)}</b><span>risk breach</span></div></div><a class='btn' href='{html.escape(str(latest.get('href')))}'>Open latest proof</a><p>Public-safe boundary: deterministic benchmark receipts, not live revenue, investment advice, legal advice, policy advice, token advice, or proof of achieved superintelligence.</p></section><h2>Latest proofs</h2><section class='grid'>{''.join(cards)}</section></main></body></html>"""

def main() -> None:
    root = Path.cwd()
    receipt_path = root / "data" / f"{PROOF_ID}.json"
    if not receipt_path.exists(): fail(f"missing receipt: {receipt_path}")
    r = read_json(receipt_path, None)
    if not isinstance(r, dict): fail("receipt must be JSON object")
    if r.get("proof_id") != PROOF_ID or not r.get("proved"): fail("receipt proof_id/proved mismatch")
    m = r.get("metrics", {})
    if not isinstance(m, dict): fail("missing metrics")
    site = root / "site"; site.mkdir(exist_ok=True)
    registry_path = site / "proof-registry.json"
    registry = normalize_registry(read_json(registry_path, {"proofs": []}))
    ids = {PROOF_ID, f"{PROOF_ID}.html"}
    proofs = [p for p in registry.get("proofs", []) if identity(p) not in ids]
    entry = {
        "id": PROOF_ID,
        "title": r.get("title", TITLE),
        "href": f"{PROOF_ID}.html",
        "json": f"data/{PROOF_ID}.json",
        "report": f"docs/{PROOF_ID}.md",
        "badge": f"badges/{PROOF_ID}.svg",
        "status": "passing",
        "generated_at_utc": r.get("generated_at_utc"),
        "headline": "Objective-integrity firewall proof: SkillOS resists proxy gaming, synthetic receipts, reward tampering, benchmark memorization, and Goodhart failures.",
        "summary": r.get("thesis", "SkillOS preserves hidden-objective value under adversarial metric pressure."),
        "metrics": {
            "value_capture": frac(m.get("locked_holdout_value_capture")),
            "objective_fidelity": frac(m.get("objective_fidelity_score")),
            "goodhart_gap": frac(m.get("goodhart_gap")),
            "frontier_correct": frac(m.get("frontier_correct_rate")),
            "risk": frac(m.get("risk_breach_rate")),
            "benchmark_value_captured_trillions": m.get("benchmark_capital_equivalent_value_captured_trillions"),
            "benchmark_gain_vs_control_trillions": m.get("benchmark_capital_equivalent_gain_vs_best_control_trillions"),
        },
    }
    proofs.insert(0, entry)
    registry = {"schema_version": 2, "updated_at_utc": r.get("generated_at_utc"), "site_base_url": SITE_BASE_URL, "source": "SkillOS autonomous GitHub Actions proof publisher", "proofs": proofs[:MAX_PROOFS]}
    atomic_json(registry_path, registry)
    atomic_text(site / "index.html", render_index(registry, entry))
    for src,dst in [(root/"data"/f"{PROOF_ID}.json", site/"data"/f"{PROOF_ID}.json"), (root/"docs"/f"{PROOF_ID}.md", site/"docs"/f"{PROOF_ID}.md"), (root/"badges"/f"{PROOF_ID}.svg", site/"badges"/f"{PROOF_ID}.svg")]:
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(src,dst)
    urls = ["index.html", "proof-registry.json"] + [str(p.get("href")) for p in registry["proofs"] if isinstance(p, dict) and p.get("href")]
    sitemap = "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n" + "".join(f"  <url><loc>{html.escape(SITE_BASE_URL + u)}</loc></url>\n" for u in dict.fromkeys(urls)) + "</urlset>\n"
    atomic_text(site / "sitemap.xml", sitemap)
    atomic_text(site / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_BASE_URL}sitemap.xml\n")
    print(json.dumps({"published": True, "proofs": len(registry["proofs"]), "latest_proof": entry["href"], "index": str(site/"index.html")}, indent=2))

if __name__ == "__main__":
    main()
