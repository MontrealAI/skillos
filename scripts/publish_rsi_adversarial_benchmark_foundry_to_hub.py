#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import tempfile
from pathlib import Path
from typing import Any

PROOF_ID = "rsi-adversarial-benchmark-foundry-proof"
TITLE = "Autonomous RSI Adversarial Benchmark Foundry Proof"
SITE_BASE_URL = "https://montrealai.github.io/skillos/"
MAX_REGISTRY_PROOFS = 80


def fail(message: str) -> None:
    raise SystemExit(f"publisher failed: {message}")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(path.parent), delete=False) as f:
        f.write(text)
        tmp = Path(f.name)
    os.replace(tmp, path)


def atomic_write_json(path: Path, obj: Any) -> None:
    atomic_write_text(path, json.dumps(obj, indent=2, sort_keys=True))


def normalize_registry(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict):
        proofs = raw.get("proofs", [])
        if isinstance(proofs, dict):
            proofs = list(proofs.values())
        elif not isinstance(proofs, list):
            proofs = []
        meta = {k: v for k, v in raw.items() if k != "proofs"}
    elif isinstance(raw, list):
        proofs = raw
        meta = {}
    else:
        proofs = []
        meta = {}
    clean = []
    seen = set()
    for p in proofs:
        if not isinstance(p, dict):
            continue
        ident = str(p.get("id") or p.get("proof_id") or p.get("href") or p.get("title") or "").strip()
        if not ident or ident in seen:
            continue
        seen.add(ident)
        clean.append(p)
    meta["proofs"] = clean
    return meta


def as_fraction(value: Any) -> float | None:
    try:
        v = float(value)
        return v if v <= 1.0 else v / 100.0
    except Exception:
        return None


def proof_identity(p: dict[str, Any]) -> str:
    return str(p.get("id") or p.get("proof_id") or p.get("href") or p.get("title") or "")


def pct(v: Any) -> str:
    try:
        return f"{100*float(v):.2f}%"
    except Exception:
        return "—"


def metric(entry: dict[str, Any], key: str) -> Any:
    m = entry.get("metrics")
    return m.get(key) if isinstance(m, dict) else None


def render_cards(proofs: list[dict[str, Any]]) -> str:
    cards = []
    for p in proofs[:12]:
        href = html.escape(str(p.get("href") or "#"))
        title = html.escape(str(p.get("title") or p.get("id") or "Proof"))
        status = html.escape(str(p.get("status") or "unknown"))
        summary = html.escape(str(p.get("summary") or p.get("headline") or "Autonomous public proof"))
        vc = pct(metric(p, "value_capture"))
        cards.append(f"<article class='card'><span class='pill'>{status}</span><h3><a href='{href}'>{title}</a></h3><p>{summary}</p><p><b>{vc}</b> value capture</p><a class='btn secondary' href='{href}'>Open proof</a></article>")
    return "\n".join(cards)


def render_index(registry: dict[str, Any], latest: dict[str, Any]) -> str:
    proofs = [p for p in registry.get("proofs", []) if isinstance(p, dict)]
    cards = render_cards(proofs)
    lm = latest.get("metrics", {}) if isinstance(latest.get("metrics"), dict) else {}
    return f"""<!doctype html><html lang='en'><head><meta charset='utf-8'/><meta name='viewport' content='width=device-width,initial-scale=1'/><title>SkillOS Proof Command Center</title><style>
:root{{--bg:#061826;--line:rgba(255,255,255,.18);--ink:#f4fbff;--muted:#b9cbe0;--cyan:#7cecff;--green:#72ffb6;--gold:#ffd86b}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 15% 10%,rgba(0,234,255,.16),transparent 32%),linear-gradient(135deg,#061d2b,#111838 72%,#090b1d);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.45}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:32px 32px;pointer-events:none;mask-image:linear-gradient(to bottom,black,transparent 90%)}}a{{color:var(--cyan);text-decoration:none;font-weight:900}}nav{{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;gap:20px;padding:14px 22px;background:rgba(4,15,26,.86);border-bottom:1px solid var(--line);backdrop-filter:blur(14px)}}nav span{{display:flex;gap:14px;flex-wrap:wrap}}.wrap{{width:min(1180px,92vw);margin:auto;padding:48px 0 90px}}h1{{font-size:clamp(44px,7vw,88px);line-height:.88;letter-spacing:-.075em;margin:18px 0}}h2{{font-size:clamp(30px,4vw,56px);letter-spacing:-.05em;margin-top:54px}}h3{{font-size:22px;margin:14px 0 8px}}p{{color:var(--muted)}}.hero,.card,.metric{{background:linear-gradient(135deg,rgba(255,255,255,.11),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:26px;box-shadow:0 30px 90px rgba(0,0,0,.23);backdrop-filter:blur(10px)}}.hero{{padding:34px}}.eyebrow{{color:var(--cyan);letter-spacing:.22em;text-transform:uppercase;font-weight:950;font-size:12px}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}@media(max-width:850px){{.grid{{grid-template-columns:1fr}}nav{{position:static}}}}.card{{padding:22px}}.pill{{display:inline-flex;padding:7px 10px;border-radius:999px;background:rgba(114,255,182,.17);color:var(--green);font-size:12px;font-weight:950;text-transform:uppercase}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0}}@media(max-width:850px){{.metrics{{grid-template-columns:1fr 1fr}}}}.metric{{padding:18px;border-radius:18px}}.metric b,.card b{{color:var(--green);font-size:26px}}.btn{{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:12px 16px;background:var(--cyan);color:#071827;font-weight:950}}.secondary{{background:transparent;color:#eef;border:1px solid rgba(255,255,255,.3)}}.note{{border-left:3px solid var(--cyan);padding-left:16px;margin-top:20px;color:#d9ecff}}</style></head><body>
<nav><strong><a href='index.html'>SkillOS Proof Command Center</a></strong><span><a href='proof-registry.json'>Registry</a><a href='https://github.com/MontrealAI/skillos/actions'>Actions</a><a href='https://github.com/MontrealAI/skillos'>GitHub</a></span></nav>
<main class='wrap'><section class='hero'><div class='eyebrow'>Autonomous public proof system</div><h1>Verified skills, harder tests, stronger releases.</h1><p>SkillOS turns work into traces, traces into verified skills, skills into releases, and releases into stronger future work. This command center is regenerated by GitHub Actions from public receipts.</p><div class='metrics'><div class='metric'><b>{len(proofs)}</b><br>registered proofs</div><div class='metric'><b>{pct(lm.get('value_capture'))}</b><br>latest value capture</div><div class='metric'><b>{pct(lm.get('hardness_gain'))}</b><br>latest benchmark hardness gain</div><div class='metric'><b>{pct(lm.get('risk'))}</b><br>latest risk breach</div></div><a class='btn' href='{html.escape(str(latest.get('href')))}'>Open latest proof</a><p class='note'>Public-safe boundary: these are deterministic benchmark receipts, not live revenue, investment advice, legal advice, policy advice, token advice, or proof of achieved superintelligence.</p></section><h2>Latest proofs</h2><section class='grid'>{cards}</section></main></body></html>"""


def main() -> None:
    root = Path.cwd()
    data_path = root / "data" / f"{PROOF_ID}.json"
    if not data_path.exists():
        fail(f"missing proof receipt: {data_path}")
    proof = read_json(data_path, None)
    if not isinstance(proof, dict) or proof.get("proof_id") != PROOF_ID or not proof.get("proved"):
        fail("proof receipt is missing or not passing")
    metrics = proof.get("metrics")
    if not isinstance(metrics, dict):
        fail("proof receipt missing metrics")
    site = root / "site"
    site.mkdir(parents=True, exist_ok=True)
    registry_path = site / "proof-registry.json"
    registry = normalize_registry(read_json(registry_path, {"proofs": []}))
    existing = [p for p in registry.get("proofs", []) if isinstance(p, dict)]
    proofs = [p for p in existing if proof_identity(p) not in {PROOF_ID, f"{PROOF_ID}.html"}]
    entry = {
        "id": PROOF_ID,
        "title": proof.get("title", TITLE),
        "href": f"{PROOF_ID}.html",
        "json": f"data/{PROOF_ID}.json",
        "report": f"docs/{PROOF_ID}.md",
        "badge": f"badges/{PROOF_ID}.svg",
        "status": "passing",
        "generated_at_utc": proof.get("generated_at_utc"),
        "headline": "SkillOS generates its own harder, leak-resistant adversarial benchmarks and proves causal lift on locked hidden holdouts.",
        "summary": proof.get("thesis"),
        "metrics": {
            "value_capture": as_fraction(metrics.get("locked_hidden_holdout_value_capture")),
            "hardness_gain": as_fraction(metrics.get("adversarial_benchmark_hardness_gain_vs_static")),
            "causal_uplift": as_fraction(metrics.get("causal_uplift_vs_strongest_control")),
            "leakage_rejection": as_fraction(metrics.get("benchmark_leakage_rejection_rate")),
            "goodhart_gap": as_fraction(metrics.get("goodhart_gap")),
            "risk": as_fraction(metrics.get("risk_breach_rate")),
            "benchmark_value_captured_trillions": metrics.get("benchmark_capital_equivalent_value_captured_trillions"),
            "benchmark_gain_vs_best_control_trillions": metrics.get("benchmark_capital_equivalent_gain_vs_strongest_control_trillions"),
        },
    }
    proofs.insert(0, entry)
    registry = {"schema_version": 2, "updated_at_utc": proof.get("generated_at_utc"), "source": "SkillOS autonomous GitHub Actions proof publisher", "site_base_url": SITE_BASE_URL, "proofs": proofs[:MAX_REGISTRY_PROOFS]}
    atomic_write_json(registry_path, registry)
    atomic_write_text(site / "index.html", render_index(registry, entry))
    sitemap_urls = [SITE_BASE_URL, SITE_BASE_URL + f"{PROOF_ID}.html"]
    for p in registry.get("proofs", [])[:MAX_REGISTRY_PROOFS]:
        href = str(p.get("href", ""))
        if href and not href.startswith("http"):
            url = SITE_BASE_URL + href
            if url not in sitemap_urls:
                sitemap_urls.append(url)
    sitemap = "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n" + "\n".join(f"  <url><loc>{html.escape(u)}</loc></url>" for u in sitemap_urls) + "\n</urlset>\n"
    atomic_write_text(site / "sitemap.xml", sitemap)
    atomic_write_text(site / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_BASE_URL}sitemap.xml\n")
    print(json.dumps({"published": True, "proof_id": PROOF_ID, "registry_entries": len(registry["proofs"]), "index": "site/index.html"}, indent=2))


if __name__ == "__main__":
    main()
