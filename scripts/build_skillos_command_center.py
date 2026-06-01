#!/usr/bin/env python3
"""Autonomous SkillOS Public Command Center builder.

This script scans the repository and regenerates the public SkillOS command
center from proof receipts, workflows, badges, docs, and generated proof pages.

It is intentionally dependency-free and safe for GitHub Actions.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
DOCS = ROOT / "docs"
BADGES = ROOT / "badges"
WORKFLOWS = ROOT / ".github" / "workflows"
MANIFEST = SITE / "data" / "command-center-manifest.json"

REPO = os.environ.get("GITHUB_REPOSITORY", "MontrealAI/skillos")
LIVE_URL = os.environ.get("SKILLOS_LIVE_URL", "https://montrealai.github.io/skillos/")
REPO_URL = f"https://github.com/{REPO}"
ACTIONS_URL = f"{REPO_URL}/actions"

BAD_WORDS = [
    "guaranteed wealth",
    "independent financial-performance claims",
    "investment advice",
    "real results",
    "guaranteed returns",
]

SAFE_BOUNDARY = (
    "SkillOS publishes deterministic benchmark proofs and reference workflows. "
    "The public command center is not a claim of live customer revenue, independent financial-performance claims, "
    "financial advice, legal advice, medical advice, policy advice, token advice, "
    "or achieved superintelligence."
)

def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(path.parent)) as tmp:
        tmp.write(text)
        tmp_path = tmp.name
    os.replace(tmp_path, path)

def read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return value or "proof"

def title_from_slug(slug: str) -> str:
    words = slug.replace("rsi-", "").replace("-proof", "").split("-")
    return " ".join(w.capitalize() if w.upper() != "RSI" else "RSI" for w in words)

def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))

def money(value: Any) -> str:
    try:
        value = float(value)
    except Exception:
        return "—"
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000_000_000:
        return f"{sign}${value/1_000_000_000_000:,.2f}T"
    if value >= 1_000_000_000:
        return f"{sign}${value/1_000_000_000:,.2f}B"
    if value >= 1_000_000:
        return f"{sign}${value/1_000_000:,.2f}M"
    return f"{sign}${value:,.0f}"

def pct(value: Any) -> str:
    try:
        return f"{float(value):.4f}%".rstrip("0").rstrip(".") + "%"
    except Exception:
        return "—"

def proof_id_from_path(path: Path) -> str:
    stem = path.stem
    if stem.endswith("_proof"):
        stem = stem.replace("_", "-")
    return stem

def proof_page_for(proof_id: str) -> str:
    candidates = [
        SITE / f"{proof_id}.html",
        SITE / f"{proof_id.replace('_','-')}.html",
        SITE / f"{proof_id.replace('-','_')}.html",
    ]
    for c in candidates:
        if c.exists():
            return c.name
    return f"{proof_id}.html"

def find_report(proof_id: str) -> str:
    candidates = [
        DOCS / f"{proof_id}.md",
        DOCS / f"{proof_id.replace('-','_')}.md",
        DOCS / f"{proof_id.replace('_','-')}.md",
    ]
    for c in candidates:
        if c.exists():
            return f"docs/{c.name}"
    return ""

def find_badge(proof_id: str) -> str:
    candidates = [
        BADGES / f"{proof_id}.svg",
        BADGES / f"{proof_id.replace('-','_')}.svg",
        SITE / "badges" / f"{proof_id}.svg",
    ]
    for c in candidates:
        if c.exists():
            return f"badges/{c.name}"
    return ""

def normalize_proof(path: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    proof_id = receipt.get("id") or proof_id_from_path(path)
    proof_id = str(proof_id).replace("_", "-")
    final = receipt.get("final") or {}
    agent_system = receipt.get("agent_system") or {}
    benchmark = receipt.get("benchmark_public") or {}
    comparisons = receipt.get("comparisons") or {}
    bootstrap = receipt.get("bootstrap_confidence_intervals") or {}

    title = (
        receipt.get("proof_type")
        or receipt.get("workflow")
        or receipt.get("title")
        or title_from_slug(proof_id)
    )

    skills = receipt.get("skills_used") or []
    skill_preview = []
    if isinstance(skills, list):
        for item in skills[:8]:
            if isinstance(item, dict):
                skill_preview.append({
                    "name": item.get("name", ""),
                    "layer": item.get("layer", ""),
                    "purpose": item.get("purpose", ""),
                    "verifier": item.get("verifier", ""),
                })

    all_skill_names = []
    if isinstance(skills, list):
        for item in skills:
            if isinstance(item, dict) and item.get("name"):
                all_skill_names.append(str(item.get("name")))

    href = proof_page_for(proof_id)
    json_href = f"data/{path.name}" if path.parent.name == "data" else f"data/{path.name}"
    report_href = find_report(proof_id)
    badge_href = find_badge(proof_id)

    return {
        "id": proof_id,
        "title": str(title),
        "href": href,
        "json": json_href,
        "doc": report_href,
        "badge": badge_href,
        "proved": bool(receipt.get("proved")),
        "status": receipt.get("status", ""),
        "generated_at_utc": receipt.get("generated_at_utc", ""),
        "protocol_fingerprint_sha256": receipt.get("protocol_fingerprint_sha256", ""),
        "safe_interpretation": receipt.get("safe_interpretation", ""),
        "public_boundary": receipt.get("public_boundary", ""),
        "value_capture_rate_percent": final.get("value_capture_rate_percent") or final.get("benchmark_value_capture_rate_percent"),
        "minimum_domain_value_capture_percent": final.get("minimum_domain_value_capture_percent") or final.get("minimum_regime_value_capture_percent"),
        "risk_breach_rate_percent": final.get("risk_breach_rate_percent"),
        "unauthorized_action_rate_percent": final.get("unauthorized_action_rate_percent"),
        "sla_breach_rate_percent": final.get("sla_breach_rate_percent"),
        "policy_violation_rate_percent": final.get("policy_violation_rate_percent"),
        "assurance_gap_rate_percent": final.get("assurance_gap_rate_percent"),
        "benchmark_value_at_stake_usd": final.get("total_benchmark_value_at_stake_usd"),
        "benchmark_value_captured_usd": final.get("total_benchmark_value_captured_usd"),
        "gain_over_strongest_safe_control_usd": final.get("benchmark_implied_value_captured_over_strongest_safe_control_usd") or final.get("benchmark_implied_value_captured_over_strongest_control_usd"),
        "strongest_control": final.get("strongest_safe_control") or final.get("strongest_control"),
        "virtual_specialist_agents": agent_system.get("virtual_specialist_agents"),
        "specialist_roles": agent_system.get("specialist_roles"),
        "role_families": agent_system.get("role_families"),
        "rsi_release_count": receipt.get("rsi_release_count"),
        "locked_holdout_count": benchmark.get("locked_holdout_count"),
        "candidate_actions_per_case": benchmark.get("candidate_actions_per_case"),
        "domains_count": len(benchmark.get("domains") or benchmark.get("regimes") or []),
        "skills_used_count": len(skills) if isinstance(skills, list) else 0,
        "skill_preview": skill_preview,
        "skill_names": all_skill_names,
        "comparison_count": len(comparisons) if isinstance(comparisons, dict) else 0,
        "bootstrap_keys": list(bootstrap.keys()) if isinstance(bootstrap, dict) else [],
    }

def collect_proofs() -> list[dict[str, Any]]:
    proof_by_id: dict[str, dict[str, Any]] = {}
    for folder in [DATA, SITE / "data"]:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.json")):
            if path.name in {"proof-registry.json", "command-center-manifest.json"}:
                continue
            raw = read_json(path)
            if not isinstance(raw, dict):
                continue
            if not any(k in raw for k in ["proved", "final", "agent_system", "proof_type", "workflow"]):
                continue
            item = normalize_proof(path, raw)
            existing = proof_by_id.get(item["id"])
            if existing is None or (not existing.get("generated_at_utc") and item.get("generated_at_utc")):
                proof_by_id[item["id"]] = item
    proofs = list(proof_by_id.values())
    proofs.sort(key=lambda p: (str(p.get("generated_at_utc") or ""), p.get("title","")), reverse=True)
    return proofs

def parse_workflow_name(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return title_from_slug(path.stem)
    for line in text.splitlines():
        m = re.match(r"\s*name\s*:\s*(.+?)\s*$", line)
        if m:
            return m.group(1).strip().strip('"').strip("'")
    return title_from_slug(path.stem)

def collect_workflows() -> list[dict[str, Any]]:
    workflows = []
    if not WORKFLOWS.exists():
        return workflows
    for path in sorted(list(WORKFLOWS.glob("*.yml")) + list(WORKFLOWS.glob("*.yaml"))):
        name = parse_workflow_name(path)
        workflows.append({
            "name": name,
            "file": path.name,
            "href": f"{ACTIONS_URL}/workflows/{path.name}",
            "is_proof": "proof" in name.lower() or "proof" in path.name.lower(),
            "is_command_center": "command" in name.lower() or "command-center" in path.name.lower(),
        })
    workflows.sort(key=lambda w: (not w["is_command_center"], not w["is_proof"], w["name"].lower()))
    return workflows

def fetch_recent_runs() -> dict[str, dict[str, str]]:
    token = os.environ.get("GITHUB_TOKEN")
    if not token or not REPO or "/" not in REPO:
        return {}
    url = f"https://api.github.com/repos/{REPO}/actions/runs?per_page=100"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "SkillOS-Command-Center",
    })
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception:
        return {}
    by_name: dict[str, dict[str, str]] = {}
    for run in data.get("workflow_runs", []):
        name = run.get("name") or ""
        if name and name not in by_name:
            by_name[name] = {
                "status": run.get("status", ""),
                "conclusion": run.get("conclusion", ""),
                "html_url": run.get("html_url", ""),
                "updated_at": run.get("updated_at", ""),
            }
    return by_name

def merge_registry(proofs: list[dict[str, Any]]) -> dict[str, Any]:
    path = SITE / "proof-registry.json"
    old = read_json(path)
    old_items = []
    if isinstance(old, list):
        old_items = [x for x in old if isinstance(x, dict)]
    elif isinstance(old, dict):
        old_items = [x for x in old.get("proofs", []) if isinstance(x, dict)]

    merged: dict[str, dict[str, Any]] = {}
    for item in old_items:
        key = item.get("id") or item.get("href") or item.get("title")
        if key:
            merged[str(key)] = item
    for p in proofs:
        merged[p["id"]] = {
            **merged.get(p["id"], {}),
            **{
                "id": p["id"],
                "title": p["title"],
                "href": p["href"],
                "json": p["json"],
                "doc": p["doc"],
                "badge": p["badge"],
                "proved": p["proved"],
                "status": p["status"],
                "generated_at_utc": p["generated_at_utc"],
                "value_capture_rate_percent": p["value_capture_rate_percent"],
                "risk_breach_rate_percent": p["risk_breach_rate_percent"],
                "skills_used_count": p["skills_used_count"],
                "virtual_specialist_agents": p["virtual_specialist_agents"],
                "specialist_roles": p["specialist_roles"],
                "rsi_release_count": p["rsi_release_count"],
            },
        }
    items = list(merged.values())
    items.sort(key=lambda x: (str(x.get("generated_at_utc") or ""), str(x.get("title") or "")), reverse=True)
    return {"updated_at_utc": utc_now(), "proofs": items}

def total_agents(proofs: list[dict[str, Any]]) -> int:
    values = [p.get("virtual_specialist_agents") for p in proofs if isinstance(p.get("virtual_specialist_agents"), int)]
    return max(values) if values else 0

def proof_family(title: str) -> str:
    t = title.lower()
    if any(x in t for x in ["governance", "assurance", "sla", "reliability"]):
        return "Reliability, assurance, and governance"
    if any(x in t for x in ["market", "economy", "clearinghouse", "treasury", "moat", "fork", "incentive"]):
        return "Skill markets and compounding moat"
    if any(x in t for x in ["causal", "objective", "replication", "benchmark", "continual", "transfer"]):
        return "RSI evidence and robustness"
    return "Core capability proof"

def render_badge() -> None:
    BADGES.mkdir(parents=True, exist_ok=True)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="282" height="20">'
        '<rect width="282" height="20" rx="10" fill="#14233a"/>'
        '<rect x="172" width="110" height="20" rx="10" fill="#2bb673"/>'
        '<text x="10" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">SkillOS command center</text>'
        '<text x="192" y="14" fill="#fff" font-family="Verdana" font-size="11">fresh</text>'
        '</svg>'
    )
    atomic_write(BADGES / "command-center-fresh.svg", svg)
    (SITE / "badges").mkdir(parents=True, exist_ok=True)
    atomic_write(SITE / "badges" / "command-center-fresh.svg", svg)

def css() -> str:
    return """
:root{--bg:#06131f;--panel:rgba(255,255,255,.075);--panel2:rgba(255,255,255,.108);--line:rgba(255,255,255,.16);--text:#f5fbff;--muted:#b8c8d8;--cyan:#86f8ff;--green:#7dffb0;--gold:#ffd66b;--pink:#ff9ef8}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;background:radial-gradient(circle at 82% 0,#3d4381 0,transparent 34%),radial-gradient(circle at 0 18%,#095e70 0,transparent 26%),linear-gradient(135deg,#06131f,#13243d 60%,#282a5d);color:var(--text)}
body:before{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:42px 42px;pointer-events:none;mask-image:linear-gradient(to bottom,rgba(0,0,0,.9),rgba(0,0,0,.05))}
a{color:var(--cyan)}main{max-width:1240px;margin:0 auto;padding:44px 20px 84px;position:relative}nav{position:sticky;top:0;z-index:10;background:rgba(6,19,31,.91);border-bottom:1px solid var(--line);backdrop-filter:blur(14px);display:flex;justify-content:space-between;align-items:center;padding:14px 22px}nav a{color:var(--muted);text-decoration:none;font-weight:850;margin-left:14px}
h1{font-size:clamp(44px,7.2vw,104px);line-height:.84;letter-spacing:-.08em;margin:12px 0}h2{font-size:clamp(30px,4.5vw,58px);letter-spacing:-.05em;margin:36px 0 14px}h3{letter-spacing:-.025em}p{color:var(--muted);font-size:18px;line-height:1.55}.hero{display:grid;grid-template-columns:1.05fr .95fr;gap:22px;align-items:center}.card,.metric,.proof-card,.workflow-card{background:var(--panel);border:1px solid var(--line);border-radius:28px;padding:22px;box-shadow:0 22px 80px rgba(0,0,0,.25)}.card.feature{background:linear-gradient(180deg,var(--panel2),var(--panel))}
.eyebrow{color:var(--cyan);text-transform:uppercase;letter-spacing:.18em;font-weight:950;font-size:12px}.quote{font-size:clamp(24px,3.2vw,42px);line-height:1.08;letter-spacing:-.04em;color:var(--text)}.pill{display:inline-block;border:1px solid rgba(134,248,255,.35);border-radius:999px;padding:7px 10px;margin:4px 6px 4px 0;color:var(--cyan);font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:.06em}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}.metric strong{display:block;color:var(--green);font-size:32px}.metric span{color:var(--muted)}.proof-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.proof-card h3{font-size:22px;margin:8px 0}.proof-card p{font-size:15px}.proof-card .links a,.workflow-card a.button,.button{display:inline-block;background:var(--cyan);color:#06131f;text-decoration:none;border-radius:999px;padding:10px 14px;font-weight:950;margin:4px 6px 4px 0}.secondary{background:rgba(255,255,255,.09)!important;color:var(--text)!important;border:1px solid var(--line)}
.skill-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.skill-card{background:rgba(255,255,255,.07);border:1px solid var(--line);border-radius:22px;padding:16px;min-height:166px}.skill-card h3{font-size:18px;margin:8px 0}.skill-card p{font-size:14px;margin:0}.family{color:var(--gold);font-size:12px;font-weight:950;text-transform:uppercase;letter-spacing:.1em}.bar{display:grid;grid-template-columns:240px 1fr 120px;gap:12px;align-items:center;margin:12px 0}.bar span,.bar b{color:var(--muted)}.bar div{height:20px;background:rgba(255,255,255,.08);border-radius:999px;overflow:hidden}.bar i{display:block;height:100%;background:linear-gradient(90deg,var(--green),var(--cyan));border-radius:999px}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:18px;overflow:hidden;margin:16px 0}td,th{padding:12px;border-bottom:1px solid var(--line);text-align:left}th{color:var(--muted);text-transform:uppercase;font-size:12px;letter-spacing:.08em}.notice{border-left:4px solid var(--gold);background:rgba(255,214,107,.08);border-radius:16px;padding:16px 18px;color:var(--muted)}.workflow-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}.status-ok{color:var(--green);font-weight:950}.status-warn{color:var(--gold);font-weight:950}.small{font-size:14px;color:var(--muted)}code{background:rgba(255,255,255,.08);padding:2px 6px;border-radius:8px}
@media(max-width:1000px){.proof-grid{grid-template-columns:repeat(2,1fr)}.skill-grid{grid-template-columns:repeat(2,1fr)}.workflow-grid{grid-template-columns:1fr}}@media(max-width:760px){.hero,.grid,.proof-grid,.skill-grid,.bar{grid-template-columns:1fr}nav{display:block}nav a{display:inline-block;margin:8px 10px 0 0}}
"""

def render_head(title: str) -> str:
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title><style>{css()}</style></head><body><nav><strong>SkillOS Command Center</strong><div><a href="index.html">Home</a><a href="proofs.html">Proofs</a><a href="actions.html">Run Proofs</a><a href="data/command-center-manifest.json">Manifest</a></div></nav><main>"""

def render_foot() -> str:
    return f"""<section class="notice"><strong>Public boundary:</strong> {esc(SAFE_BOUNDARY)}</section></main></body></html>"""

def proof_card(p: dict[str, Any]) -> str:
    proved = "PASSED" if p.get("proved") else "CHECK"
    status_cls = "status-ok" if p.get("proved") else "status-warn"
    skills = p.get("skill_preview") or []
    skills_text = "".join(f'<span class="pill">{esc(s.get("name"))}</span>' for s in skills[:3])
    value = pct(p.get("value_capture_rate_percent"))
    risk = pct(p.get("risk_breach_rate_percent"))
    href = p.get("href") or "#"
    json_href = p.get("json") or "#"
    doc_href = p.get("doc") or "#"
    badge = p.get("badge")
    badge_html = f'<img alt="proof badge" src="{esc(badge)}" style="max-width:240px;height:20px">' if badge else ""
    return f"""<article class="proof-card">
<div class="family">{esc(proof_family(p.get('title','')))}</div>
<h3>{esc(p.get('title'))}</h3>
<p><span class="{status_cls}">{proved}</span> · value capture {esc(value)} · risk breach {esc(risk)}</p>
<p class="small">{esc(p.get('virtual_specialist_agents') or '—')} agents · {esc(p.get('specialist_roles') or '—')} roles · {esc(p.get('skills_used_count') or 0)} skills · {esc(p.get('rsi_release_count') or '—')} releases</p>
<div>{skills_text}</div>
<p class="links"><a href="{esc(href)}">Open proof page</a><a class="secondary" href="{esc(json_href)}">JSON receipt</a>{f'<a class="secondary" href="{esc(doc_href)}">Report</a>' if doc_href else ''}</p>
{badge_html}
</article>"""

def render_skill_mosaic(proofs: list[dict[str, Any]]) -> str:
    seen = {}
    for p in proofs:
        for s in p.get("skill_preview") or []:
            name = s.get("name")
            if name and name not in seen:
                seen[name] = s
    if not seen:
        return '<div class="card"><p>No skills catalog found yet. Future proof receipts with <code>skills_used</code> will appear here automatically.</p></div>'
    cards = []
    for s in list(seen.values())[:24]:
        cards.append(f"""<article class="skill-card"><div class="family">{esc(s.get('layer') or 'Skill')}</div><h3>{esc(s.get('name'))}</h3><p>{esc(s.get('purpose') or 'Operational skill used by a proof workflow.')}</p><p class="small">Verifier: {esc(s.get('verifier') or 'Verifier court')}</p></article>""")
    return f'<div class="skill-grid">{"".join(cards)}</div>'

def render_index(proofs: list[dict[str, Any]], workflows: list[dict[str, Any]], runs: dict[str, dict[str, str]], generated_at: str) -> str:
    latest = proofs[:9]
    proof_count = len(proofs)
    proved_count = sum(1 for p in proofs if p.get("proved"))
    workflow_count = len(workflows)
    skills_count = len({n for p in proofs for n in p.get("skill_names", [])})
    agent_count = total_agents(proofs)
    run_updates = [r for r in runs.values() if r.get("updated_at")]
    latest_run = max([r["updated_at"] for r in run_updates], default="best effort")

    html = render_head("SkillOS Public Command Center")
    html += f"""<section class="hero"><div><div class="eyebrow">Public SkillOS Command Center</div><h1>Autonomous proof, always refreshed.</h1><p>The SkillOS website is regenerated from the repository itself: proof receipts, workflow files, badges, Markdown reports, skills catalogs, and GitHub Actions outputs.</p><p><a class="button" href="proofs.html">Explore proofs</a><a class="button secondary" href="actions.html">Run proofs</a><a class="button secondary" href="{esc(REPO_URL)}">Open GitHub</a></p></div><div class="card feature"><div class="eyebrow">What this page guarantees</div><div class="quote">No manual homepage curation required. Every refresh scans the repo, rebuilds the command center, verifies the Skills Used displays, and republishes the proof registry.</div><p class="small">Generated at {esc(generated_at)}. Latest GitHub run status is fetched best-effort when the GitHub token is available.</p></div></section>
<section class="grid"><div class="metric"><strong>{proof_count}</strong><span>proof receipts found</span></div><div class="metric"><strong>{proved_count}</strong><span>passed proof receipts</span></div><div class="metric"><strong>{workflow_count}</strong><span>workflow files found</span></div><div class="metric"><strong>{skills_count}</strong><span>unique skills displayed</span></div></section>
<section class="card"><div class="eyebrow">Core public explanation</div><div class="quote">work → traces → skills → verification → releases → routing upgrades → compounding capability</div><p>SkillOS makes this loop visible. The public site shows the proof visually; GitHub Actions shows the proof regenerating; JSON receipts show machine-readable evidence; Skills Used cards show what the agent system actually did.</p></section>
<section><h2>Latest proof pages</h2><div class="proof-grid">{''.join(proof_card(p) for p in latest) or '<div class="card"><p>No proof receipts found yet.</p></div>'}</div><p><a class="button" href="proofs.html">View all proofs</a></p></section>
<section id="skills-used"><h2>Skills Used across the network</h2><p>The command center automatically extracts skills from proof receipts and renders them as user-friendly cards. This gives non-technical viewers a concrete way to understand the multi-agent system.</p>{render_skill_mosaic(proofs)}</section>
<section><h2>How to see the proof</h2><div class="grid"><div class="card"><div class="eyebrow">1</div><h3>Open a proof page</h3><p>Click a proof card to see the visual evidence, metrics, controls, release history, and Skills Used.</p></div><div class="card"><div class="eyebrow">2</div><h3>Open the JSON receipt</h3><p>The JSON receipt is the machine-readable proof artifact generated by the workflow.</p></div><div class="card"><div class="eyebrow">3</div><h3>Rerun in GitHub Actions</h3><p>Open the Actions page, choose a workflow, and click Run workflow. A green run regenerates the proof autonomously.</p></div><div class="card"><div class="eyebrow">4</div><h3>Return here</h3><p>This command center refreshes from committed proof outputs so viewers always have a single current hub.</p></div></div></section>
<section><h2>Workflow status</h2><div class="workflow-grid">{''.join(workflow_card(w, runs.get(w['name'])) for w in workflows[:10])}</div><p><a class="button" href="actions.html">Open all workflows</a></p></section>"""
    html += render_foot()
    return html

def workflow_card(w: dict[str, Any], run: dict[str, str] | None = None) -> str:
    run = run or {}
    status = run.get("conclusion") or run.get("status") or "available"
    status_cls = "status-ok" if status in {"success", "completed", "available"} else "status-warn"
    run_link = run.get("html_url")
    return f"""<article class="workflow-card"><div class="family">{'Proof workflow' if w.get('is_proof') else 'Repository workflow'}</div><h3>{esc(w.get('name'))}</h3><p><span class="{status_cls}">{esc(status)}</span> · {esc(w.get('file'))}</p><p><a class="button" href="{esc(w.get('href'))}">Open workflow</a>{f'<a class="button secondary" href="{esc(run_link)}">Latest run</a>' if run_link else ''}</p></article>"""

def render_proofs(proofs: list[dict[str, Any]], generated_at: str) -> str:
    groups: dict[str, list[dict[str, Any]]] = {}
    for p in proofs:
        groups.setdefault(proof_family(p.get("title","")), []).append(p)
    html = render_head("SkillOS Proof Registry")
    html += f"""<section class="hero"><div><div class="eyebrow">Proof registry</div><h1>All public proofs.</h1><p>Automatically generated from proof receipts in <code>data/</code> and <code>site/data/</code>. Generated at {esc(generated_at)}.</p></div><div class="card feature"><div class="quote">{len(proofs)} proof receipts indexed. {sum(1 for p in proofs if p.get('proved'))} passed receipts.</div><p>Each card links to the visual page, JSON receipt, and Markdown report when available.</p></div></section>"""
    for name, items in groups.items():
        html += f"<section><h2>{esc(name)}</h2><div class=\"proof-grid\">{''.join(proof_card(p) for p in items)}</div></section>"
    html += render_foot()
    return html

def render_actions(workflows: list[dict[str, Any]], runs: dict[str, dict[str, str]], generated_at: str) -> str:
    html = render_head("SkillOS GitHub Actions")
    html += f"""<section class="hero"><div><div class="eyebrow">Run proofs</div><h1>Regenerate the evidence.</h1><p>Open a workflow and press <strong>Run workflow</strong>. The workflow regenerates receipts, reports, visual pages, badges, and the command center.</p><p><a class="button" href="{esc(ACTIONS_URL)}">Open GitHub Actions</a></p></div><div class="card feature"><div class="quote">The command center is designed for non-technical viewers: one page to view proofs, one page to run them, one manifest to verify them.</div><p>Generated at {esc(generated_at)}.</p></div></section>
<section><h2>Available workflows</h2><div class="workflow-grid">{''.join(workflow_card(w, runs.get(w['name'])) for w in workflows)}</div></section>"""
    html += render_foot()
    return html

def render_docs(proofs: list[dict[str, Any]], workflows: list[dict[str, Any]], generated_at: str) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    text = f"""# SkillOS Public Command Center

Generated: `{generated_at}`

The public command center is regenerated autonomously from repository state.

## What it scans

```text
data/*.json
site/data/*.json
docs/*.md
badges/*.svg
site/*.html
.github/workflows/*.yml
.github/workflows/*.yaml
```

## What it writes

```text
site/index.html
site/proofs.html
site/actions.html
site/data/command-center-manifest.json
site/proof-registry.json
site/sitemap.xml
site/robots.txt
badges/command-center-fresh.svg
site/badges/command-center-fresh.svg
docs/SKILLOS_PUBLIC_COMMAND_CENTER.md
```

## Current inventory

```text
proof receipts indexed: {len(proofs)}
passed proof receipts: {sum(1 for p in proofs if p.get("proved"))}
workflow files indexed: {len(workflows)}
```

## Viewer instructions

1. Open `https://montrealai.github.io/skillos/`.
2. Click a proof card.
3. Read the visual proof page and Skills Used section.
4. Open the JSON receipt for machine-readable evidence.
5. Rerun the workflow from GitHub Actions when needed.

## Boundary

{SAFE_BOUNDARY}
"""
    atomic_write(DOCS / "SKILLOS_PUBLIC_COMMAND_CENTER.md", text)

def render_sitemap(proofs: list[dict[str, Any]]) -> None:
    urls = [LIVE_URL.rstrip("/") + "/", LIVE_URL.rstrip("/") + "/proofs.html", LIVE_URL.rstrip("/") + "/actions.html"]
    for p in proofs:
        href = p.get("href")
        if href:
            urls.append(LIVE_URL.rstrip("/") + "/" + href.lstrip("/"))
    seen = []
    for u in urls:
        if u not in seen:
            seen.append(u)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{esc(u)}</loc></url>\n" for u in seen) + "</urlset>\n"
    atomic_write(SITE / "sitemap.xml", xml)
    atomic_write(SITE / "robots.txt", "User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n")

def main() -> None:
    generated_at = utc_now()
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data").mkdir(parents=True, exist_ok=True)
    (SITE / "badges").mkdir(parents=True, exist_ok=True)
    (SITE / "docs").mkdir(parents=True, exist_ok=True)

    proofs = collect_proofs()
    workflows = collect_workflows()
    runs = fetch_recent_runs()

    registry = merge_registry(proofs)
    manifest = {
        "generated_at_utc": generated_at,
        "repository": REPO,
        "live_url": LIVE_URL,
        "proof_count": len(proofs),
        "proved_count": sum(1 for p in proofs if p.get("proved")),
        "workflow_count": len(workflows),
        "unique_skills_count": len({n for p in proofs for n in p.get("skill_names", [])}),
        "max_virtual_specialist_agents": total_agents(proofs),
        "proofs": proofs,
        "workflows": workflows,
        "recent_workflow_runs_available": bool(runs),
        "safe_boundary": SAFE_BOUNDARY,
    }

    render_badge()
    atomic_write(MANIFEST, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    atomic_write(SITE / "proof-registry.json", json.dumps(registry, indent=2, sort_keys=True) + "\n")
    atomic_write(SITE / "index.html", render_index(proofs, workflows, runs, generated_at))
    atomic_write(SITE / "proofs.html", render_proofs(proofs, generated_at))
    atomic_write(SITE / "actions.html", render_actions(workflows, runs, generated_at))
    render_docs(proofs, workflows, generated_at)
    render_sitemap(proofs)

    # Keep public copies close to the deployed site.
    for name in ["SKILLOS_PUBLIC_COMMAND_CENTER.md"]:
        src = DOCS / name
        if src.exists():
            atomic_write(SITE / "docs" / name, src.read_text(encoding="utf-8"))

    print(json.dumps({
        "status": "COMMAND_CENTER_REFRESHED",
        "generated_at_utc": generated_at,
        "proof_count": len(proofs),
        "proved_count": sum(1 for p in proofs if p.get("proved")),
        "workflow_count": len(workflows),
        "unique_skills_count": manifest["unique_skills_count"],
        "outputs": [
            "site/index.html",
            "site/proofs.html",
            "site/actions.html",
            "site/data/command-center-manifest.json",
            "site/proof-registry.json",
            "site/sitemap.xml",
            "site/robots.txt",
            "badges/command-center-fresh.svg",
            "docs/SKILLOS_PUBLIC_COMMAND_CENTER.md",
        ],
    }, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
