#!/usr/bin/env python3
"""Refresh the SkillOS public site into a live proof command center.

This script is intentionally dependency-free and safe for GitHub Actions.

It generates:
- site/index.html
- site/proofs.html
- site/actions.html
- site/runbook.html
- site/public_site_status.json
- data/public_site_status.json
- docs/SKILLOS_PUBLIC_SITE_STATUS.md

Design goal:
Make https://montrealai.github.io/skillos/ fresh, complete, useful, beautiful,
and easy for non-technical viewers to understand and for maintainers to rerun.

Boundary:
The generated site presents deterministic public proof/benchmark outputs. It
does not claim audited customer ROI, live customer adoption, financial advice,
investment advice, superintelligence, or Kardashev Type II achievement.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import shutil
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
DOCS = ROOT / "docs"
WORKFLOWS = ROOT / ".github" / "workflows"

for folder in [SITE, DATA, DOCS]:
    folder.mkdir(parents=True, exist_ok=True)

REPO = os.environ.get("GITHUB_REPOSITORY", "MontrealAI/skillos")
OWNER, REPO_NAME = REPO.split("/", 1)
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
SERVER_URL = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
RUN_URL = f"{SERVER_URL}/{REPO}/actions/runs/{RUN_ID}" if RUN_ID else ""
REF_NAME = os.environ.get("GITHUB_REF_NAME", "main")
SHA = os.environ.get("GITHUB_SHA", "")

EXCLUDE_WORKFLOW_NAME_PATTERNS = [
    "public site command center refresh",
    "run all public proofs",
    "public site refresh reusable",
]

PROOF_KEYWORDS = [
    "proof", "rsi", "market", "command", "capability", "capital", "flywheel",
    "experiment", "shadow", "wealth", "skillos"
]


def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def api_json(path: str) -> dict[str, Any]:
    if not TOKEN:
        raise RuntimeError("No GITHUB_TOKEN available.")
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_workflow_name(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return path.stem
    for line in text.splitlines():
        m = re.match(r"^\s*name:\s*(.+?)\s*$", line)
        if m:
            raw = m.group(1).strip().strip('"').strip("'")
            return raw or path.stem
    return path.stem


def local_workflows() -> list[dict[str, Any]]:
    rows = []
    if WORKFLOWS.exists():
        for path in sorted(WORKFLOWS.glob("*.y*ml")):
            rows.append({
                "id": path.name,
                "name": parse_workflow_name(path),
                "path": f".github/workflows/{path.name}",
                "html_url": f"{SERVER_URL}/{REPO}/actions/workflows/{path.name}",
                "state": "active",
                "source": "local",
            })
    return rows


def github_workflows() -> list[dict[str, Any]]:
    try:
        data = api_json(f"/repos/{REPO}/actions/workflows?per_page=100")
        rows = data.get("workflows", [])
        if rows:
            return [{
                "id": w.get("id"),
                "name": w.get("name") or Path(w.get("path", "")).stem,
                "path": w.get("path"),
                "html_url": w.get("html_url") or f"{SERVER_URL}/{REPO}/actions/workflows/{Path(w.get('path','')).name}",
                "state": w.get("state"),
                "source": "api",
            } for w in rows]
    except Exception as exc:
        print(f"Workflow API unavailable; using local workflow scan: {exc}")
    return local_workflows()


def github_runs() -> list[dict[str, Any]]:
    try:
        data = api_json(f"/repos/{REPO}/actions/runs?per_page=100")
        rows = data.get("workflow_runs", [])
        return [{
            "id": r.get("id"),
            "name": r.get("name") or "",
            "workflow_id": r.get("workflow_id"),
            "event": r.get("event"),
            "status": r.get("status"),
            "conclusion": r.get("conclusion"),
            "html_url": r.get("html_url"),
            "created_at": r.get("created_at"),
            "updated_at": r.get("updated_at"),
            "head_sha": r.get("head_sha"),
            "head_branch": r.get("head_branch"),
            "actor": (r.get("actor") or {}).get("login"),
        } for r in rows]
    except Exception as exc:
        print(f"Runs API unavailable; continuing without live run data: {exc}")
        return []


def latest_run_by_workflow(runs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for r in runs:
        key = str(r.get("name") or "").lower()
        if key and key not in out:
            out[key] = r
    return out


def is_meta_workflow(name: str, path: str = "") -> bool:
    text = f"{name} {path}".lower()
    return any(p in text for p in EXCLUDE_WORKFLOW_NAME_PATTERNS)


def is_proof_workflow(name: str, path: str = "") -> bool:
    text = f"{name} {path}".lower()
    if is_meta_workflow(name, path):
        return False
    return any(k in text for k in PROOF_KEYWORDS)


def read_json_file(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def human_name_from_slug(slug: str) -> str:
    slug = re.sub(r"^rsi[_-]?", "", slug)
    slug = slug.replace("_", " ").replace("-", " ")
    words = [w for w in slug.split() if w not in {"proof", "market", "benchmark"}]
    title = " ".join(words).strip().title()
    return title or slug.title()


def proof_jsons() -> list[dict[str, Any]]:
    rows = []
    seen = set()
    for path in sorted(DATA.glob("*.json")):
        name = path.name.lower()
        if "proof" not in name and "command_center" not in name and "wealth" not in name:
            continue
        if "benchmark" in name or "preregistered" in name:
            continue
        obj = read_json_file(path)
        if not isinstance(obj, dict):
            continue
        key = path.name
        if key in seen:
            continue
        seen.add(key)
        slug = path.stem
        status = obj.get("status") or ("PASSED" if obj.get("proved") else "PENDING")
        workflow = obj.get("workflow") or obj.get("proof_type") or human_name_from_slug(slug)
        final = obj.get("final") or {}
        agent_system = obj.get("agent_system") or {}
        metrics = {}
        for k in [
            "fully_correct_percent", "value_capture_rate_percent", "coordination_protocol_accuracy_percent",
            "risk_control_accuracy_percent", "capability_lever_accuracy_percent", "avg_compounding_index",
            "avg_productive_capacity_index", "risk_breach_rate_percent", "avg_consensus_score"
        ]:
            if k in final:
                metrics[k] = final[k]
        rows.append({
            "title": human_name_from_slug(slug),
            "slug": slug,
            "status": status,
            "proved": bool(obj.get("proved", "PASSED" in str(status))),
            "workflow": workflow,
            "json_path": f"data/{path.name}",
            "json_url": f"{SERVER_URL}/{REPO}/blob/main/data/{path.name}",
            "generated_at": obj.get("generated_at_utc") or obj.get("generated_at"),
            "safe_interpretation": obj.get("safe_interpretation", ""),
            "agent_count": agent_system.get("agent_count"),
            "role_count": agent_system.get("role_count"),
            "holdout_count": obj.get("holdout_count"),
            "rsi_releases": len([r for r in obj.get("rsi_releases", []) if r.get("released")]),
            "metrics": metrics,
            "raw": obj,
        })
    return rows


def proof_pages() -> list[dict[str, str]]:
    rows = []
    for path in sorted(SITE.glob("*proof*.html")):
        rows.append({
            "title": human_name_from_slug(path.stem),
            "path": f"site/{path.name}",
            "url": f"https://montrealai.github.io/skillos/{path.name}",
            "name": path.name,
        })
    return rows


def proof_docs() -> list[dict[str, str]]:
    rows = []
    for path in sorted(DOCS.glob("*PROOF*.md")) + sorted(DOCS.glob("*proof*.md")):
        if path.name == "SKILLOS_PUBLIC_SITE_STATUS.md":
            continue
        rows.append({
            "title": human_name_from_slug(path.stem),
            "path": f"docs/{path.name}",
            "url": f"{SERVER_URL}/{REPO}/blob/main/docs/{path.name}",
            "name": path.name,
        })
    return rows


def merge_proofs(workflows: list[dict[str, Any]], runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_run_name = latest_run_by_workflow(runs)
    pages = proof_pages()
    docs = proof_docs()
    json_rows = proof_jsons()

    entries: dict[str, dict[str, Any]] = {}

    def add_entry(key: str, data: dict[str, Any]) -> None:
        if key not in entries:
            entries[key] = {"title": data.get("title") or key, "sources": []}
        for k, v in data.items():
            if v not in (None, "", [], {}):
                entries[key][k] = v
        entries[key]["sources"].append(data.get("source", "unknown"))

    for j in json_rows:
        add_entry(j["slug"], {**j, "source": "json"})

    for p in pages:
        key = p["name"].replace(".html", "")
        add_entry(key, {"title": p["title"], "page_url": p["url"], "page_path": p["path"], "source": "page"})

    for d in docs:
        key = d["name"].replace(".md", "").lower()
        add_entry(key, {"title": d["title"], "doc_url": d["url"], "doc_path": d["path"], "source": "doc"})

    for w in workflows:
        if is_proof_workflow(str(w.get("name", "")), str(w.get("path", ""))):
            name = str(w.get("name") or "")
            key = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
            run = by_run_name.get(name.lower(), {})
            add_entry(key, {
                "title": name,
                "workflow_name": name,
                "workflow_path": w.get("path"),
                "workflow_url": w.get("html_url"),
                "latest_run_url": run.get("html_url"),
                "latest_run_status": run.get("status"),
                "latest_run_conclusion": run.get("conclusion"),
                "latest_run_updated_at": run.get("updated_at"),
                "source": "workflow",
            })

    proof_list = list(entries.values())

    def rank(item: dict[str, Any]) -> tuple[int, str]:
        title = str(item.get("title", "")).lower()
        score = 100
        if "v17" in title or "capital-to-capability" in title or "capability command center" in title:
            score -= 50
        if "multi-agent" in title or "command center" in title:
            score -= 25
        if item.get("proved"):
            score -= 10
        if item.get("page_url"):
            score -= 5
        return (score, title)

    return sorted(proof_list, key=rank)


def status_badge(conclusion: str | None, status: str | None = None) -> str:
    c = (conclusion or "").lower()
    s = (status or "").lower()
    if c == "success":
        return "passing"
    if c in {"failure", "cancelled", "timed_out"}:
        return c
    if s in {"queued", "in_progress", "requested", "waiting"}:
        return "running"
    return "not run yet"


def badge_class(label: str) -> str:
    if label in {"success", "passing", "passed"} or "passed" in label:
        return "ok"
    if label in {"running", "queued", "in_progress"}:
        return "warn"
    if label in {"failure", "failed", "cancelled", "timed_out"}:
        return "bad"
    return "neutral"


def latest_status_rows(workflows: list[dict[str, Any]], runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_name = latest_run_by_workflow(runs)
    rows = []
    for w in workflows:
        run = by_name.get(str(w.get("name") or "").lower(), {})
        rows.append({
            "name": w.get("name"),
            "path": w.get("path"),
            "workflow_url": w.get("html_url"),
            "state": w.get("state"),
            "run_url": run.get("html_url"),
            "status": run.get("status") or "not_run",
            "conclusion": run.get("conclusion"),
            "updated_at": run.get("updated_at"),
            "event": run.get("event"),
        })
    return sorted(rows, key=lambda r: (r.get("updated_at") or ""), reverse=True)


def public_status(workflows: list[dict[str, Any]], runs: list[dict[str, Any]], proofs: list[dict[str, Any]]) -> dict[str, Any]:
    success = sum(1 for r in runs[:50] if r.get("conclusion") == "success")
    failed = sum(1 for r in runs[:50] if r.get("conclusion") == "failure")
    running = sum(1 for r in runs[:50] if r.get("status") in {"in_progress", "queued", "requested", "waiting"})
    proven = sum(1 for p in proofs if p.get("proved") or "PASSED" in str(p.get("status")))
    return {
        "generated_at_utc": now_iso(),
        "repository": REPO,
        "branch": REF_NAME,
        "commit": SHA,
        "refresh_run_url": RUN_URL,
        "site_url": "https://montrealai.github.io/skillos/",
        "workflow_count": len(workflows),
        "proof_count": len(proofs),
        "proved_or_passed_proof_count": proven,
        "recent_successful_runs": success,
        "recent_failed_runs": failed,
        "recent_running_runs": running,
        "workflows": latest_status_rows(workflows, runs),
        "proofs": proofs,
    }


CSS = """
:root{color-scheme:dark;--bg:#071421;--panel:rgba(255,255,255,.065);--line:rgba(255,255,255,.14);--text:#eff8ff;--muted:#aebdca;--cyan:#82f7ff;--green:#7dffb0;--gold:#ffd66b;--red:#ff7b7b}
*{box-sizing:border-box} body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;background:radial-gradient(circle at 80% 0,#3a3b72 0,transparent 36%),linear-gradient(135deg,#06131e,#13243d 60%,#252958);color:var(--text)}
a{color:var(--cyan);text-decoration:none} a:hover{text-decoration:underline}
main{max-width:1240px;margin:0 auto;padding:42px 22px 80px}
nav{display:flex;align-items:center;justify-content:space-between;gap:16px;position:sticky;top:0;z-index:10;background:rgba(7,20,33,.86);backdrop-filter:blur(14px);border-bottom:1px solid var(--line);padding:13px 22px}
.brand{font-weight:900;letter-spacing:-.02em}.navlinks{display:flex;gap:14px;flex-wrap:wrap}.navlinks a{color:var(--muted);font-weight:800;font-size:14px}
.hero{display:grid;grid-template-columns:1.05fr .95fr;gap:24px;align-items:center;padding:48px 0 28px}.eyebrow{color:var(--cyan);font-size:12px;text-transform:uppercase;letter-spacing:.16em;font-weight:950}.hero h1{font-size:clamp(42px,7vw,92px);line-height:.88;letter-spacing:-.075em;margin:10px 0}.hero p,.lead{font-size:20px;color:var(--muted);line-height:1.55}.card{background:var(--panel);border:1px solid var(--line);border-radius:26px;padding:24px;box-shadow:0 20px 80px rgba(0,0,0,.24)}.status{font-size:28px;font-weight:950;color:var(--green);overflow-wrap:anywhere}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:22px 0}.metric{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:20px}.metric strong{display:block;color:var(--green);font-size:34px}.metric span{color:var(--muted)}
.section{margin:26px 0}.section h2{font-size:clamp(28px,4vw,54px);letter-spacing:-.045em;margin:0 0 14px}.proof-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}.proof-card{background:var(--panel);border:1px solid var(--line);border-radius:24px;padding:22px}.proof-card h3{font-size:24px;line-height:1.05;letter-spacing:-.035em;margin:8px 0}.proof-card p{color:var(--muted);line-height:1.45}.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}.button{display:inline-block;padding:11px 15px;border-radius:999px;font-weight:900;background:var(--cyan);color:#061421}.button.secondary{background:transparent;color:var(--text);border:1px solid var(--line)}
.badge{display:inline-flex;align-items:center;border-radius:999px;padding:6px 10px;font-size:12px;font-weight:950;text-transform:uppercase;letter-spacing:.04em}.badge.ok{background:rgba(125,255,176,.16);color:var(--green)}.badge.warn{background:rgba(255,214,107,.16);color:var(--gold)}.badge.bad{background:rgba(255,123,123,.16);color:var(--red)}.badge.neutral{background:rgba(255,255,255,.08);color:var(--muted)}
table{width:100%;border-collapse:collapse;background:var(--panel);border-radius:18px;overflow:hidden;border:1px solid var(--line)}th,td{padding:13px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--muted);font-size:13px;text-transform:uppercase;letter-spacing:.07em}td{color:var(--text)}tr:last-child td{border-bottom:0}
.notice{border-left:4px solid var(--gold);background:rgba(255,214,107,.08);border-radius:16px;padding:16px 18px;color:var(--muted);line-height:1.5}.small{font-size:13px;color:var(--muted)}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.step{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:20px}.step strong{display:block;color:var(--cyan);font-size:15px;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px}
@media(max-width:900px){.hero,.grid,.proof-grid,.steps{grid-template-columns:1fr}nav{align-items:flex-start;flex-direction:column}.navlinks{gap:10px}}
""".strip()


def page_shell(title: str, body: str, active: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<nav>
  <a class="brand" href="index.html">SkillOS Public Proof Command Center</a>
  <div class="navlinks">
    <a href="index.html">Home</a>
    <a href="proofs.html">Proofs</a>
    <a href="actions.html">Actions</a>
    <a href="runbook.html">Run / Regenerate</a>
    <a href="https://github.com/{html.escape(REPO)}">GitHub</a>
  </div>
</nav>
<main>{body}</main>
</body>
</html>
"""


def proof_card(p: dict[str, Any]) -> str:
    title = html.escape(str(p.get("title") or "SkillOS proof"))
    status = str(p.get("status") or status_badge(p.get("latest_run_conclusion"), p.get("latest_run_status")))
    status_clean = status.lower().replace("_", " ")
    klass = badge_class(status_clean)
    workflow = html.escape(str(p.get("workflow") or p.get("workflow_name") or "Autonomous public proof"))
    page_url = p.get("page_url") or ""
    workflow_url = p.get("workflow_url") or p.get("latest_run_url") or ""
    doc_url = p.get("doc_url") or ""
    json_url = p.get("json_url") or ""
    agent = p.get("agent_count")
    roles = p.get("role_count")
    releases = p.get("rsi_releases")
    meta = []
    if agent:
        meta.append(f"{agent} agents")
    if roles:
        meta.append(f"{roles} roles")
    if releases:
        meta.append(f"{releases} RSI releases")
    if p.get("holdout_count"):
        meta.append(f"{p.get('holdout_count')} holdout cases")
    meta_html = " · ".join(html.escape(str(x)) for x in meta) or "public, reproducible GitHub proof"
    actions = []
    if page_url:
        actions.append(f'<a class="button" href="{html.escape(page_url)}">View proof</a>')
    if workflow_url:
        actions.append(f'<a class="button secondary" href="{html.escape(workflow_url)}">Run on GitHub</a>')
    if doc_url:
        actions.append(f'<a class="button secondary" href="{html.escape(doc_url)}">Read doc</a>')
    if json_url:
        actions.append(f'<a class="button secondary" href="{html.escape(json_url)}">Inspect JSON</a>')
    if not actions:
        actions.append(f'<a class="button secondary" href="https://github.com/{html.escape(REPO)}/actions">Open Actions</a>')
    metrics = p.get("metrics") or {}
    metric_html = ""
    if metrics:
        items = []
        labels = {
            "fully_correct_percent": "fully correct",
            "value_capture_rate_percent": "value capture",
            "coordination_protocol_accuracy_percent": "coordination",
            "risk_control_accuracy_percent": "risk control",
            "capability_lever_accuracy_percent": "capability lever",
            "avg_compounding_index": "compounding",
            "risk_breach_rate_percent": "risk breach",
        }
        for k, v in list(metrics.items())[:4]:
            suffix = "%" if "percent" in k else ""
            items.append(f"<span class='badge neutral'>{html.escape(labels.get(k,k))}: {html.escape(str(v))}{suffix}</span>")
        metric_html = "<div class='actions'>" + "".join(items) + "</div>"
    return f"""
<div class="proof-card">
  <span class="badge {klass}">{html.escape(status_clean[:80])}</span>
  <h3>{title}</h3>
  <p>{workflow}</p>
  <p class="small">{meta_html}</p>
  {metric_html}
  <div class="actions">{''.join(actions)}</div>
</div>
"""


def workflow_table(rows: list[dict[str, Any]], limit: int | None = None) -> str:
    subset = rows if limit is None else rows[:limit]
    tr = []
    for r in subset:
        label = status_badge(r.get("conclusion"), r.get("status"))
        klass = badge_class(label)
        name = html.escape(str(r.get("name") or "Workflow"))
        wf_url = html.escape(str(r.get("workflow_url") or "#"))
        run_url = html.escape(str(r.get("run_url") or wf_url))
        updated = html.escape(str(r.get("updated_at") or "not run yet"))
        event = html.escape(str(r.get("event") or ""))
        path = html.escape(str(r.get("path") or ""))
        tr.append(f"""<tr>
<td><a href="{wf_url}"><strong>{name}</strong></a><br><span class="small mono">{path}</span></td>
<td><span class="badge {klass}">{html.escape(label)}</span></td>
<td>{event}</td>
<td><a href="{run_url}">{updated}</a></td>
</tr>""")
    return "<table><tr><th>Workflow</th><th>Status</th><th>Event</th><th>Latest run</th></tr>" + "\n".join(tr) + "</table>"


def build_pages(status: dict[str, Any]) -> None:
    proofs = status["proofs"]
    workflows = status["workflows"]
    generated = html.escape(status["generated_at_utc"])
    run_all_url = f"{SERVER_URL}/{REPO}/actions/workflows/skillos-run-all-public-proofs.yml"
    refresh_url = f"{SERVER_URL}/{REPO}/actions/workflows/skillos-public-site-refresh.yml"
    github_url = f"{SERVER_URL}/{REPO}"

    hero = f"""
<section class="hero">
  <div>
    <div class="eyebrow">MONTREAL.AI / SKILLOS</div>
    <h1>Public Proof Command Center</h1>
    <p>Fresh public proof hub for every SkillOS GitHub Action run: proofs, dashboards, reports, JSON receipts, workflow status, and one-click regeneration instructions.</p>
    <div class="actions">
      <a class="button" href="proofs.html">View proofs</a>
      <a class="button secondary" href="{html.escape(run_all_url)}">Run all public proofs</a>
      <a class="button secondary" href="{html.escape(refresh_url)}">Refresh site</a>
    </div>
  </div>
  <div class="card">
    <div class="eyebrow">Live site freshness</div>
    <div class="status">Updated {generated}</div>
    <p>Generated autonomously from repository files, proof JSON, GitHub Actions workflows, and latest run metadata.</p>
    <p class="small">Repository: <a href="{html.escape(github_url)}">{html.escape(REPO)}</a></p>
  </div>
</section>
<section class="grid">
  <div class="metric"><strong>{status['proof_count']}</strong><span>proof entries</span></div>
  <div class="metric"><strong>{status['workflow_count']}</strong><span>workflows tracked</span></div>
  <div class="metric"><strong>{status['recent_successful_runs']}</strong><span>recent successful runs</span></div>
  <div class="metric"><strong>{status['recent_running_runs']}</strong><span>recent running runs</span></div>
</section>
<section class="section">
  <h2>Flagship public proofs</h2>
  <div class="proof-grid">{''.join(proof_card(p) for p in proofs[:6])}</div>
</section>
<section class="section">
  <h2>Run or regenerate</h2>
  <div class="steps">
    <div class="step"><strong>1. Open Actions</strong><p>Click a proof card or the Run All button. GitHub opens the workflow page.</p></div>
    <div class="step"><strong>2. Run workflow</strong><p>Use the green <span class="mono">Run workflow</span> button. No API keys, no private data, no customers.</p></div>
    <div class="step"><strong>3. Watch receipts</strong><p>The Action regenerates proof HTML, Markdown, JSON, badges, and updates this hub.</p></div>
  </div>
</section>
<section class="notice">
  <strong>Public boundary:</strong> These are autonomous, deterministic market-readiness proofs using synthetic/redacted-style benchmark data. They are not audited customer ROI, live customer adoption, financial advice, investment advice, superintelligence, Kardashev Type II achievement, or guarantees of future outcomes.
</section>
<section class="section">
  <h2>Latest workflow status</h2>
  {workflow_table(workflows, limit=12)}
</section>
"""
    (SITE / "index.html").write_text(page_shell("SkillOS Public Proof Command Center", hero), encoding="utf-8")

    proofs_body = f"""
<section class="section">
  <div class="eyebrow">Proof library</div>
  <h2>All public SkillOS proofs</h2>
  <p class="lead">Every proof card links to the visual page when available, the workflow that reruns it, the documentation, and machine-readable JSON receipts.</p>
  <div class="proof-grid">{''.join(proof_card(p) for p in proofs)}</div>
</section>
"""
    (SITE / "proofs.html").write_text(page_shell("SkillOS Proof Library", proofs_body), encoding="utf-8")

    actions_body = f"""
<section class="section">
  <div class="eyebrow">GitHub Actions</div>
  <h2>Workflow status command board</h2>
  <p class="lead">Latest visible workflow status from the repository. This page is regenerated by the autonomous site refresh workflow.</p>
  <div class="actions">
    <a class="button" href="{html.escape(run_all_url)}">Run all public proofs</a>
    <a class="button secondary" href="{html.escape(refresh_url)}">Refresh this site</a>
    <a class="button secondary" href="{html.escape(github_url + '/actions')}">Open all Actions</a>
  </div>
  {workflow_table(workflows)}
</section>
"""
    (SITE / "actions.html").write_text(page_shell("SkillOS Actions Status", actions_body), encoding="utf-8")

    runbook_body = f"""
<section class="section">
  <div class="eyebrow">For viewers, users, maintainers</div>
  <h2>Run and regenerate the proofs</h2>
  <p class="lead">This site is designed so a non-technical viewer can understand the proof and a maintainer can rerun the full proof suite from GitHub Actions.</p>
  <div class="steps">
    <div class="step"><strong>Run one proof</strong><p>Open a proof card, click <span class="mono">Run on GitHub</span>, then click <span class="mono">Run workflow</span>.</p></div>
    <div class="step"><strong>Run all proofs</strong><p>Use the orchestrator workflow to dispatch public proof workflows from one place.</p><p><a class="button" href="{html.escape(run_all_url)}">Run all public proofs</a></p></div>
    <div class="step"><strong>Refresh the hub</strong><p>Use the refresh workflow to rebuild the site from latest workflows, JSON receipts, docs, and proof pages.</p><p><a class="button secondary" href="{html.escape(refresh_url)}">Refresh site</a></p></div>
  </div>
</section>
<section class="section card">
  <h2>What the automation guarantees</h2>
  <ul>
    <li>Scans GitHub workflow files and latest workflow runs.</li>
    <li>Scans generated proof JSON, proof pages, proof docs, and badges.</li>
    <li>Regenerates a fresh, public, user-friendly proof hub.</li>
    <li>Commits generated site/status files back to the repository.</li>
    <li>Deploys the static site to GitHub Pages.</li>
  </ul>
</section>
<section class="section card">
  <h2>Future-proofing rule</h2>
  <p>For any future proof workflow, include the word <span class="mono">Proof</span> or <span class="mono">RSI</span> in the workflow name, generate proof JSON into <span class="mono">data/</span>, and a visual proof page into <span class="mono">site/</span>. The command center will discover it automatically.</p>
</section>
<section class="notice">
  <strong>Safe claim boundary:</strong> The hub makes proof outputs visible and reproducible. It does not convert benchmark results into audited customer results or guarantees.
</section>
"""
    (SITE / "runbook.html").write_text(page_shell("SkillOS Runbook", runbook_body), encoding="utf-8")


def build_markdown_status(status: dict[str, Any]) -> str:
    lines = [
        "# SkillOS Public Site Command Center Status",
        "",
        f"Generated: `{status['generated_at_utc']}`",
        f"Repository: `{status['repository']}`",
        f"Site: {status['site_url']}",
        "",
        "## Summary",
        "",
        f"- Proof entries: {status['proof_count']}",
        f"- Workflows tracked: {status['workflow_count']}",
        f"- Recent successful runs: {status['recent_successful_runs']}",
        f"- Recent failed runs: {status['recent_failed_runs']}",
        f"- Recent running runs: {status['recent_running_runs']}",
        "",
        "## Public proof entries",
        "",
    ]
    for p in status["proofs"]:
        title = p.get("title", "Proof")
        page = p.get("page_url", "")
        workflow = p.get("workflow_url", "")
        lines.append(f"- **{title}**")
        if page:
            lines.append(f"  - Visual page: {page}")
        if workflow:
            lines.append(f"  - Workflow: {workflow}")
        if p.get("json_url"):
            lines.append(f"  - JSON receipt: {p['json_url']}")
    lines += [
        "",
        "## Safe boundary",
        "",
        "This command center presents autonomous, deterministic market-readiness proofs using synthetic/redacted-style benchmark data. It is not audited customer ROI, live customer adoption, financial advice, investment advice, superintelligence, Kardashev Type II achievement, or a guarantee of future outcomes.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    workflows = github_workflows()
    runs = github_runs()
    proofs = merge_proofs(workflows, runs)
    status = public_status(workflows, runs, proofs)

    build_pages(status)
    status_json = json.dumps(status, indent=2, sort_keys=True) + "\n"
    (SITE / "public_site_status.json").write_text(status_json, encoding="utf-8")
    (DATA / "public_site_status.json").write_text(status_json, encoding="utf-8")
    (DOCS / "SKILLOS_PUBLIC_SITE_STATUS.md").write_text(build_markdown_status(status), encoding="utf-8")

    print(json.dumps({
        "status": "PUBLIC_SITE_COMMAND_CENTER_REFRESHED",
        "site_url": status["site_url"],
        "generated_at_utc": status["generated_at_utc"],
        "proof_count": status["proof_count"],
        "workflow_count": status["workflow_count"],
        "recent_successful_runs": status["recent_successful_runs"],
        "recent_failed_runs": status["recent_failed_runs"],
        "outputs": [
            "site/index.html",
            "site/proofs.html",
            "site/actions.html",
            "site/runbook.html",
            "site/public_site_status.json",
            "data/public_site_status.json",
            "docs/SKILLOS_PUBLIC_SITE_STATUS.md",
        ],
    }, indent=2))

if __name__ == "__main__":
    main()
