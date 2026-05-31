#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

PROOF_ID = "rsi-open-replication-mesh-proof"
TITLE = "Autonomous RSI Open Replication Mesh Proof"
SITE_BASE_URL = "https://montrealai.github.io/skillos/"
MAX_REGISTRY_PROOFS = 200


def fail(message: str) -> None:
    raise SystemExit(f"publish failed: {message}")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"warning: could not parse {path}: {exc}; rebuilding")
        return default


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def atomic_write_json(path: Path, payload: Any) -> None:
    atomic_write_text(path, json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def as_fraction(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, str):
        raw = value.strip().replace(",", "")
        try:
            if raw.endswith("%"):
                return max(0.0, min(1.0, float(raw[:-1]) / 100.0))
            value = float(raw)
        except ValueError:
            return default
    if isinstance(value, (int, float)):
        val = float(value)
        if val > 1.0 and val <= 100.0:
            val /= 100.0
        return max(0.0, min(1.0, val))
    return default


def pct(value: Any, digits: int = 1) -> str:
    return f"{100.0 * as_fraction(value):.{digits}f}%"


def normalize_registry(raw: Any) -> dict[str, Any]:
    meta: dict[str, Any] = {}
    if isinstance(raw, dict):
        meta = {k: v for k, v in raw.items() if k != "proofs"}
        proofs = raw.get("proofs", [])
    elif isinstance(raw, list):
        proofs = raw
    else:
        proofs = []
    if isinstance(proofs, dict):
        proofs = list(proofs.values())
    if not isinstance(proofs, list):
        proofs = []
    clean: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in proofs:
        if not isinstance(item, dict):
            continue
        identity = str(item.get("id") or item.get("proof_id") or item.get("href") or item.get("slug") or item.get("title") or "").strip()
        if not identity or identity in seen:
            continue
        seen.add(identity)
        clean.append(item)
    meta["proofs"] = clean
    return meta


def proof_identity(item: dict[str, Any]) -> str:
    return str(item.get("id") or item.get("proof_id") or item.get("href") or item.get("slug") or item.get("title") or "")


def card_html(item: dict[str, Any]) -> str:
    metrics = item.get("metrics", {}) if isinstance(item.get("metrics", {}), dict) else {}
    status = html.escape(str(item.get("status", "unknown")))
    title = html.escape(str(item.get("title", "Autonomous public proof")))
    headline = html.escape(str(item.get("headline", "Autonomous, reproducible SkillOS proof.")))
    href = html.escape(str(item.get("href", "#")))
    json_href = html.escape(str(item.get("json", "#")))
    report_href = html.escape(str(item.get("report", "#")))
    value_capture = metrics.get("value_capture", metrics.get("locked_holdout_value_capture", 0))
    lift = metrics.get("replication", metrics.get("causal_uplift", metrics.get("transfer", 0)))
    risk = metrics.get("risk", metrics.get("risk_breach_rate", 0))
    return f"""<article class='card'>
      <span class='pill {'pass' if status == 'passing' else ''}'>{status}</span>
      <h3><a href='{href}'>{title}</a></h3>
      <p>{headline}</p>
      <div class='mini'>
        <b>{pct(value_capture)}</b><span>value capture</span>
        <b>{pct(lift)}</b><span>replication / causal lift</span>
        <b>{pct(risk)}</b><span>risk breach</span>
      </div>
      <div class='links'><a href='{href}'>View proof</a><a href='{json_href}'>JSON</a><a href='{report_href}'>Report</a></div>
    </article>"""


def render_index(registry: dict[str, Any], latest_entry: dict[str, Any]) -> str:
    proofs = registry.get("proofs", [])
    cards = "".join(card_html(item) for item in proofs[:36] if isinstance(item, dict))
    lm = latest_entry["metrics"]
    return f"""<!doctype html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<meta name='viewport' content='width=device-width,initial-scale=1'/>
<title>SkillOS Proof Command Center</title>
<meta name='description' content='Autonomously refreshed SkillOS proof command center with public receipts and reproducible GitHub Actions.' />
<style>
:root{{--bg:#071827;--ink:#eef8ff;--muted:#b7c7dc;--line:rgba(255,255,255,.15);--cyan:#8df5ff;--green:#72ffb6;--violet:#9b8cff;--gold:#ffd86b}}
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 15% 8%,rgba(141,245,255,.20),transparent 32%),radial-gradient(circle at 76% 0%,rgba(155,140,255,.18),transparent 32%),linear-gradient(135deg,#061d2b,#111838 70%,#090b1d);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Arial,sans-serif;line-height:1.45}}body:before{{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.04) 1px,transparent 1px);background-size:32px 32px;pointer-events:none;mask-image:linear-gradient(to bottom,black,transparent 90%)}}a{{color:var(--cyan);text-decoration:none;font-weight:900}}nav{{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;gap:20px;padding:14px 22px;background:rgba(4,15,26,.86);border-bottom:1px solid var(--line);backdrop-filter:blur(14px)}}nav span{{display:flex;gap:14px;flex-wrap:wrap}}.wrap{{width:min(1180px,92vw);margin:auto;padding:48px 0 90px}}h1{{font-size:clamp(44px,7vw,88px);line-height:.88;letter-spacing:-.075em;margin:18px 0}}h2{{font-size:clamp(30px,4vw,56px);letter-spacing:-.05em;margin-top:54px}}h3{{font-size:22px;margin:14px 0 8px}}p{{color:var(--muted)}}.hero,.card{{background:linear-gradient(135deg,rgba(255,255,255,.11),rgba(255,255,255,.055));border:1px solid var(--line);border-radius:26px;box-shadow:0 30px 90px rgba(0,0,0,.23);backdrop-filter:blur(10px)}}.hero{{padding:34px}}.eyebrow{{color:var(--cyan);letter-spacing:.22em;text-transform:uppercase;font-weight:950;font-size:12px}}.grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}@media(max-width:850px){{.grid{{grid-template-columns:1fr}}nav{{position:static}}}}.card{{padding:22px}}.pill{{display:inline-flex;padding:7px 10px;border-radius:999px;background:rgba(255,216,107,.16);color:var(--gold);font-size:12px;font-weight:950;text-transform:uppercase}}.pill.pass{{background:rgba(114,255,182,.17);color:var(--green)}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:20px 0}}@media(max-width:850px){{.metrics{{grid-template-columns:1fr 1fr}}}}.metric{{padding:18px;border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.07)}}.metric b,.mini b{{color:var(--green);font-size:26px}}.mini{{display:grid;grid-template-columns:auto 1fr;gap:7px 10px;align-items:baseline;margin-top:12px}}.links{{display:flex;gap:12px;flex-wrap:wrap;margin-top:15px}}.btn{{display:inline-flex;border:1px solid var(--line);border-radius:999px;padding:12px 16px;background:var(--cyan);color:#071827;font-weight:950}}.secondary{{background:transparent;color:#eef;border:1px solid rgba(255,255,255,.3)}}.note{{border-left:3px solid var(--cyan);padding-left:16px;margin-top:20px;color:#d9ecff}}
</style>
</head>
<body>
<nav><strong><a href='index.html'>SkillOS Proof Command Center</a></strong><span><a href='proof-registry.json'>Registry</a><a href='https://github.com/MontrealAI/skillos/actions'>Actions</a><a href='https://github.com/MontrealAI/skillos'>GitHub</a></span></nav>
<main class='wrap'>
  <section class='hero'>
    <div class='eyebrow'>AUTONOMOUS RSI PUBLIC PROOF SYSTEM</div>
    <h1>Proofs that can be replayed by the world.</h1>
    <p>SkillOS turns work into traces, traces into verified skills, skills into releases, and releases into stronger future work. This command center is regenerated by GitHub Actions from public receipts.</p>
    <div class='metrics'>
      <div class='metric'><b>{len(proofs)}</b><br>registered proofs</div>
      <div class='metric'><b>{pct(lm.get('value_capture'))}</b><br>latest value capture</div>
      <div class='metric'><b>{pct(lm.get('replication'))}</b><br>latest replication score</div>
      <div class='metric'><b>{pct(lm.get('risk'))}</b><br>latest risk breach</div>
    </div>
    <a class='btn' href='{html.escape(latest_entry['href'])}'>Open latest proof</a>
    <p class='note'>Public-safe boundary: these are deterministic benchmark receipts, not live revenue, investment advice, legal advice, policy advice, token advice, or proof of achieved superintelligence.</p>
  </section>
  <h2>Latest proofs</h2>
  <section class='grid'>{cards}</section>
</main>
</body>
</html>"""


def main() -> None:
    root = Path.cwd()
    data_path = root / "data" / f"{PROOF_ID}.json"
    if not data_path.exists():
        fail(f"missing proof receipt: {data_path}")
    proof = read_json(data_path, None)
    if not isinstance(proof, dict):
        fail("proof receipt must be a JSON object")
    if proof.get("proof_id") != PROOF_ID:
        fail("proof_id mismatch")
    if not proof.get("proved"):
        fail("proof has not passed")
    metrics = proof.get("metrics")
    if not isinstance(metrics, dict):
        fail("missing metrics")

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
        "status": "passing" if proof.get("proved") else "failing",
        "generated_at_utc": proof.get("generated_at_utc"),
        "headline": "Open replication for SkillOS RSI: signed replica receipts, Merkle-style receipt tree, locked holdout replay, and GitHub-runnable verification.",
        "summary": proof.get("thesis", "SkillOS public proofs survive open replication."),
        "metrics": {
            "value_capture": as_fraction(metrics.get("locked_holdout_value_capture")),
            "replication": as_fraction(metrics.get("open_replication_score")),
            "consensus": as_fraction(metrics.get("replica_consensus_rate")),
            "causal_uplift": as_fraction(metrics.get("causal_uplift_vs_best_control")),
            "causal_uplift_p05": as_fraction(metrics.get("causal_uplift_vs_best_control_p05")),
            "risk": as_fraction(metrics.get("risk_breach_rate")),
            "negative_control_max_abs_gain": as_fraction(metrics.get("negative_control_max_abs_gain")),
            "benchmark_value_captured_trillions": metrics.get("benchmark_capital_equivalent_value_captured_trillions"),
            "benchmark_gain_vs_best_control_trillions": metrics.get("benchmark_capital_equivalent_gain_vs_best_control_trillions"),
        },
    }
    proofs.insert(0, entry)
    registry = {
        "schema_version": 2,
        "updated_at_utc": proof.get("generated_at_utc"),
        "source": "SkillOS autonomous GitHub Actions proof publisher",
        "site_base_url": SITE_BASE_URL,
        "proofs": proofs[:MAX_REGISTRY_PROOFS],
    }
    atomic_write_json(registry_path, registry)
    atomic_write_text(site / "index.html", render_index(registry, entry))

    for src, dst in [
        (root / "data" / f"{PROOF_ID}.json", site / "data" / f"{PROOF_ID}.json"),
        (root / "docs" / f"{PROOF_ID}.md", site / "docs" / f"{PROOF_ID}.md"),
        (root / "badges" / f"{PROOF_ID}.svg", site / "badges" / f"{PROOF_ID}.svg"),
    ]:
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)

    urls = ["index.html", "proof-registry.json"] + [str(p.get("href")) for p in registry["proofs"] if isinstance(p, dict) and p.get("href")]
    sitemap = "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n"
    for url in dict.fromkeys(urls):
        sitemap += f"  <url><loc>{html.escape(SITE_BASE_URL + url)}</loc></url>\n"
    sitemap += "</urlset>\n"
    atomic_write_text(site / "sitemap.xml", sitemap)
    atomic_write_text(site / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_BASE_URL}sitemap.xml\n")

    print(json.dumps({
        "published": True,
        "registered_proofs": len(registry["proofs"]),
        "index": str(site / "index.html"),
        "registry": str(registry_path),
        "latest_proof": entry["href"],
    }, indent=2))


if __name__ == "__main__":
    main()
