#!/usr/bin/env python3
"""SkillOS Public Proof Command Center v3.

World-class, dependency-free generator for the live SkillOS public proof site.

It refreshes https://montrealai.github.io/skillos/ from:
- GitHub Actions workflows
- latest GitHub Actions runs
- generated proof HTML pages
- generated proof Markdown reports
- generated proof JSON receipts
- badges and public site assets

It generates dynamic, client-side SVG charts from public_site_status.json:
- proof status chart
- workflow status chart
- RSI release curve
- multi-agent ablation bars
- capability lever radar
- agent-role constellation
- proof timeline / status tables

Safe boundary:
The site presents deterministic, public market-readiness proofs using
synthetic/redacted-style benchmark data and benchmark assumptions. It does not
claim audited customer ROI, live customer adoption, financial advice,
investment advice, superintelligence, Kardashev Type II achievement, or
guarantees.
"""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
ASSETS = SITE / "assets"
DATA = ROOT / "data"
DOCS = ROOT / "docs"
WORKFLOWS = ROOT / ".github" / "workflows"

for folder in [SITE, ASSETS, DATA, DOCS]:
    folder.mkdir(parents=True, exist_ok=True)

REPO = os.environ.get("GITHUB_REPOSITORY", "MontrealAI/skillos")
SERVER_URL = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
RUN_URL = f"{SERVER_URL}/{REPO}/actions/runs/{RUN_ID}" if RUN_ID else ""
SHA = os.environ.get("GITHUB_SHA", "")
REF_NAME = os.environ.get("GITHUB_REF_NAME", "main")
SITE_URL = "https://montrealai.github.io/skillos/"

META_WORKFLOW_PATTERNS = [
    "public proof command center",
    "public site command center",
    "run all public proofs",
    "refresh reusable",
]
PROOF_HINTS = [
    "proof", "rsi", "capability", "capital", "command", "market", "multi-agent",
    "flywheel", "experiment", "unit", "shadow", "wealth", "skillos",
]


def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_url(path: str = "") -> str:
    return f"{SERVER_URL}/{REPO}{('/' + path.lstrip('/')) if path else ''}"


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
    with urllib.request.urlopen(req, timeout=25) as resp:
        return json.loads(resp.read().decode("utf-8"))


def parse_workflow_name(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return path.stem
    for line in text.splitlines():
        m = re.match(r"^\s*name:\s*(.+?)\s*$", line)
        if m:
            return m.group(1).strip().strip('"').strip("'") or path.stem
    return path.stem


def local_workflows() -> list[dict[str, Any]]:
    rows = []
    if WORKFLOWS.exists():
        for path in sorted(WORKFLOWS.glob("*.y*ml")):
            rows.append({
                "id": path.name,
                "name": parse_workflow_name(path),
                "path": f".github/workflows/{path.name}",
                "html_url": repo_url(f"actions/workflows/{path.name}"),
                "state": "active",
                "source": "local",
            })
    return rows


def github_workflows() -> list[dict[str, Any]]:
    try:
        data = api_json(f"/repos/{REPO}/actions/workflows?per_page=100")
        workflows = data.get("workflows", [])
        if workflows:
            return [{
                "id": w.get("id"),
                "name": w.get("name") or Path(w.get("path", "")).stem,
                "path": w.get("path"),
                "html_url": w.get("html_url") or repo_url(f"actions/workflows/{Path(w.get('path','')).name}"),
                "state": w.get("state"),
                "source": "api",
            } for w in workflows]
    except Exception as exc:
        print(f"Workflow API unavailable; using local workflow scan: {exc}")
    return local_workflows()


def github_runs() -> list[dict[str, Any]]:
    try:
        data = api_json(f"/repos/{REPO}/actions/runs?per_page=100")
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
        } for r in data.get("workflow_runs", [])]
    except Exception as exc:
        print(f"Runs API unavailable; continuing without live run data: {exc}")
        return []


def latest_run_by_name(runs: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for r in runs:
        name = str(r.get("name") or "").lower()
        if name and name not in out:
            out[name] = r
    return out


def is_meta_workflow(name: str, path: str = "") -> bool:
    text = f"{name} {path}".lower()
    return any(p in text for p in META_WORKFLOW_PATTERNS)


def is_proof_workflow(name: str, path: str = "") -> bool:
    text = f"{name} {path}".lower()
    if is_meta_workflow(name, path):
        return False
    return any(h in text for h in PROOF_HINTS)


def titleize(slug: str) -> str:
    cleaned = re.sub(r"^(rsi|autonomous)[_-]*", "", slug, flags=re.I)
    cleaned = cleaned.replace("_", " ").replace("-", " ")
    cleaned = re.sub(r"\b(proof|market|benchmark|json|html|receipt)\b", "", cleaned, flags=re.I)
    return re.sub(r"\s+", " ", cleaned).strip().title() or slug.title()


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def collect_proof_jsons() -> list[dict[str, Any]]:
    rows = []
    for path in sorted(DATA.glob("*.json")):
        name = path.name.lower()
        if "benchmark" in name or "preregistered" in name or "status" in name:
            continue
        if not any(k in name for k in ["proof", "command", "capability", "wealth", "shadow"]):
            continue
        obj = read_json(path)
        if not obj:
            continue
        slug = path.stem
        final = obj.get("final") or {}
        agent_system = obj.get("agent_system") or {}
        metrics = {}
        for k, v in final.items():
            if isinstance(v, (int, float)) and any(h in k for h in ["percent", "index", "score", "accuracy", "rate"]):
                metrics[k] = v
        status = obj.get("status") or ("PASSED" if obj.get("proved") else "PENDING")
        benchmark = obj.get("benchmark_public") or {}
        rows.append({
            "key": slug,
            "title": titleize(slug),
            "status": status,
            "proved": bool(obj.get("proved")) or "PASSED" in str(status),
            "workflow": obj.get("workflow") or obj.get("proof_type") or titleize(slug),
            "json_path": f"data/{path.name}",
            "json_url": repo_url(f"blob/main/data/{path.name}"),
            "generated_at": obj.get("generated_at_utc") or obj.get("generated_at"),
            "safe_interpretation": obj.get("safe_interpretation", ""),
            "agent_count": agent_system.get("agent_count"),
            "role_count": agent_system.get("role_count"),
            "agents_per_role": agent_system.get("agents_per_role"),
            "coordination_style": agent_system.get("coordination_style"),
            "roles": agent_system.get("roles") or [],
            "holdout_count": obj.get("holdout_count") or benchmark.get("holdout_count"),
            "train_count": obj.get("train_count") or benchmark.get("train_count"),
            "validation_count": obj.get("validation_count") or benchmark.get("validation_count"),
            "rsi_releases": len([r for r in obj.get("rsi_releases", []) if isinstance(r, dict) and r.get("released")]),
            "proof_type": obj.get("proof_type"),
            "benchmark_public": benchmark,
            "metrics": metrics,
            "raw": obj,
            "source": "json",
        })
    return rows


def collect_pages_docs() -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    pages = [{
        "key": p.stem,
        "title": titleize(p.stem),
        "page_path": f"site/{p.name}",
        "page_url": f"{SITE_URL}{p.name}",
        "source": "page",
    } for p in sorted(SITE.glob("*proof*.html"))]
    docs = []
    for p in sorted(DOCS.glob("*PROOF*.md")) + sorted(DOCS.glob("*proof*.md")):
        if p.name in {"SKILLOS_PUBLIC_SITE_STATUS.md"}:
            continue
        docs.append({
            "key": p.stem.lower(),
            "title": titleize(p.stem),
            "doc_path": f"docs/{p.name}",
            "doc_url": repo_url(f"blob/main/docs/{p.name}"),
            "source": "doc",
        })
    return pages, docs


def collect_proofs(workflows: list[dict[str, Any]], runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    latest = latest_run_by_name(runs)

    def add(key: str, item: dict[str, Any]) -> None:
        if key not in entries:
            entries[key] = {"key": key, "title": item.get("title") or titleize(key), "sources": []}
        entries[key].update({k: v for k, v in item.items() if v not in (None, "", [], {})})
        entries[key]["sources"].append(item.get("source", "unknown"))

    for p in collect_proof_jsons():
        add(p["key"], p)
    pages, docs = collect_pages_docs()
    for p in pages:
        add(p["key"], p)
    for d in docs:
        add(d["key"], d)

    for w in workflows:
        name = str(w.get("name") or "")
        path = str(w.get("path") or "")
        if not is_proof_workflow(name, path):
            continue
        key = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        run = latest.get(name.lower(), {})
        add(key, {
            "title": name,
            "workflow_name": name,
            "workflow_path": path,
            "workflow_url": w.get("html_url"),
            "latest_run_url": run.get("html_url"),
            "latest_run_status": run.get("status"),
            "latest_run_conclusion": run.get("conclusion"),
            "latest_run_updated_at": run.get("updated_at"),
            "source": "workflow",
        })

    rows = list(entries.values())

    def score(item: dict[str, Any]) -> tuple[int, str]:
        text = f"{item.get('title','')} {item.get('key','')} {item.get('workflow','')}".lower()
        s = 1000
        if any(h in text for h in ["capital-to-capability", "capability command", "v17", "v16"]):
            s -= 500
        if "multi-agent" in text or "command center" in text:
            s -= 250
        if "adversarial" in text:
            s -= 120
        if item.get("agent_count"):
            s -= min(120, int(item.get("agent_count") or 0) // 4)
        if item.get("proved"):
            s -= 50
        if item.get("page_url"):
            s -= 30
        if item.get("workflow_url"):
            s -= 10
        return (s, text)

    return sorted(rows, key=score)


def pick_flagship(proofs: list[dict[str, Any]]) -> dict[str, Any]:
    if proofs:
        return proofs[0]
    return {
        "title": "Autonomous RSI Capital-to-Capability Command Center",
        "status": "READY_TO_RUN",
        "workflow": "Large-scale multi-agent capital-to-capability coordination proof",
        "agent_count": 512,
        "role_count": 64,
        "holdout_count": 0,
        "rsi_releases": 0,
        "page_url": "rsi-capability-command-center-v17-proof.html",
        "workflow_url": repo_url("actions"),
        "safe_interpretation": "Pending generated proof receipt. Run the GitHub Action to generate the latest public proof.",
        "roles": [
            "capital allocator", "compute allocator", "energy strategist", "data moat architect",
            "trust engineer", "talent allocator", "product strategist", "distribution lead",
            "validation scientist", "risk governor", "regulatory boundary", "coordination chair"
        ],
        "raw": {
            "final": {},
            "single_agent_baseline": {},
            "uncoordinated_pool": {},
            "static_coordination": {},
            "agent_system": {"agent_count": 512, "role_count": 64, "roles": []},
        },
    }


def status_label(conclusion: str | None, status: str | None = None) -> str:
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
    t = label.lower()
    if "pass" in t or t == "success" or t == "passing":
        return "ok"
    if "run" in t or "ready" in t or "pending" in t or "not run" in t:
        return "warn"
    if "fail" in t or "cancel" in t or "timed" in t:
        return "bad"
    return "neutral"


def workflow_statuses(workflows: list[dict[str, Any]], runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    latest = latest_run_by_name(runs)
    rows = []
    for w in workflows:
        name = str(w.get("name") or "")
        run = latest.get(name.lower(), {})
        rows.append({
            "name": name,
            "path": w.get("path"),
            "workflow_url": w.get("html_url"),
            "run_url": run.get("html_url"),
            "status": run.get("status") or "not_run",
            "conclusion": run.get("conclusion"),
            "event": run.get("event"),
            "updated_at": run.get("updated_at") or "",
        })
    return sorted(rows, key=lambda r: r.get("updated_at") or "", reverse=True)


def status_object(workflows: list[dict[str, Any]], runs: list[dict[str, Any]], proofs: list[dict[str, Any]], flagship: dict[str, Any]) -> dict[str, Any]:
    recent = runs[:50]
    return {
        "generated_at_utc": now_iso(),
        "repository": REPO,
        "site_url": SITE_URL,
        "branch": REF_NAME,
        "commit": SHA,
        "refresh_run_url": RUN_URL,
        "workflow_count": len(workflows),
        "proof_count": len(proofs),
        "proved_or_passed_proof_count": sum(1 for p in proofs if p.get("proved") or "PASSED" in str(p.get("status"))),
        "recent_successful_runs": sum(1 for r in recent if r.get("conclusion") == "success"),
        "recent_failed_runs": sum(1 for r in recent if r.get("conclusion") == "failure"),
        "recent_running_runs": sum(1 for r in recent if r.get("status") in {"in_progress", "queued", "requested", "waiting"}),
        "flagship": {k: v for k, v in flagship.items() if k != "raw"},
        "flagship_raw": flagship.get("raw") or {},
        "workflows": workflow_statuses(workflows, runs),
        "proofs": [{k: v for k, v in p.items() if k != "raw"} for p in proofs],
        "safe_boundary": "Autonomous deterministic market-readiness proofs using synthetic/redacted-style benchmark data and benchmark assumptions. Not audited customer ROI, live customer adoption, financial advice, investment advice, superintelligence, Kardashev Type II achievement, or guarantees.",
    }


CSS = r"""
:root{color-scheme:dark;--text:#f4fbff;--muted:#adbfcc;--line:rgba(255,255,255,.14);--panel:rgba(255,255,255,.064);--panel2:rgba(255,255,255,.095);--cyan:#86f8ff;--green:#7dffb0;--gold:#ffd66b;--red:#ff7979;--blue:#9da8ff;--purple:#d8a7ff}
*{box-sizing:border-box}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;background:radial-gradient(circle at 83% 0,#3b407c 0,transparent 34%),radial-gradient(circle at 6% 18%,#13576b 0,transparent 25%),linear-gradient(135deg,#06131f,#13243d 60%,#26295a);color:var(--text)}
body:before{content:"";position:fixed;inset:0;pointer-events:none;background-image:linear-gradient(rgba(255,255,255,.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.03) 1px,transparent 1px);background-size:40px 40px;mask-image:linear-gradient(to bottom,rgba(0,0,0,.8),rgba(0,0,0,.05))}
a{color:var(--cyan);text-decoration:none}a:hover{text-decoration:underline}nav{display:flex;align-items:center;justify-content:space-between;gap:18px;position:sticky;top:0;z-index:20;background:rgba(6,19,31,.86);backdrop-filter:blur(16px);border-bottom:1px solid var(--line);padding:14px 22px}.brand{font-weight:950;letter-spacing:-.03em}.navlinks{display:flex;gap:14px;flex-wrap:wrap}.navlinks a{color:var(--muted);font-weight:850;font-size:14px}
main{max-width:1280px;margin:0 auto;padding:44px 22px 86px}.hero{display:grid;grid-template-columns:1.08fr .92fr;gap:28px;align-items:center;padding:42px 0 24px}.eyebrow{color:var(--cyan);text-transform:uppercase;letter-spacing:.18em;font-weight:950;font-size:12px}.hero h1{font-size:clamp(44px,7vw,100px);line-height:.86;letter-spacing:-.08em;margin:10px 0}.hero p,.lead{color:var(--muted);font-size:20px;line-height:1.55}.card{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:28px;padding:24px;box-shadow:0 24px 90px rgba(0,0,0,.26)}.status{font-size:28px;font-weight:950;color:var(--green);overflow-wrap:anywhere}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}.metric{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:20px}.metric strong{display:block;color:var(--green);font-size:34px;letter-spacing:-.04em}.metric span{color:var(--muted)}.section{margin:30px 0}.section h2{font-size:clamp(30px,4.8vw,60px);letter-spacing:-.055em;line-height:.95;margin:0 0 16px}.proof-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}.proof-card{background:var(--panel);border:1px solid var(--line);border-radius:24px;padding:22px}.proof-card h3{font-size:24px;line-height:1.05;letter-spacing:-.035em;margin:10px 0}.proof-card p{color:var(--muted);line-height:1.45}.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:16px}.button{display:inline-block;border-radius:999px;padding:11px 16px;background:var(--cyan);color:#071521;font-weight:950}.button.secondary{background:transparent;border:1px solid var(--line);color:var(--text)}.button.gold{background:var(--gold);color:#15110a}
.badge{display:inline-flex;border-radius:999px;padding:6px 10px;font-size:12px;font-weight:950;text-transform:uppercase;letter-spacing:.04em}.badge.ok{background:rgba(125,255,176,.16);color:var(--green)}.badge.warn{background:rgba(255,214,107,.16);color:var(--gold)}.badge.bad{background:rgba(255,121,121,.16);color:var(--red)}.badge.neutral{background:rgba(255,255,255,.08);color:var(--muted)}
table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:18px;overflow:hidden}th,td{padding:13px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.08em}tr:last-child td{border-bottom:0}.small{font-size:13px;color:var(--muted)}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}.notice{border-left:4px solid var(--gold);background:rgba(255,214,107,.08);border-radius:16px;padding:16px 18px;color:var(--muted);line-height:1.55}.roles{display:flex;flex-wrap:wrap;gap:8px}.roles span{border:1px solid var(--line);border-radius:999px;padding:8px 10px;color:var(--muted);background:rgba(255,255,255,.05);font-size:13px}.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.step{background:var(--panel);border:1px solid var(--line);border-radius:22px;padding:20px}.step strong{display:block;color:var(--cyan);font-size:13px;text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px}.quote{font-size:clamp(24px,3.6vw,46px);line-height:1.05;letter-spacing:-.04em;color:var(--text);margin:8px 0 12px}.divider{height:1px;background:var(--line);margin:24px 0}.chart{min-height:260px;background:rgba(0,0,0,.16);border:1px solid var(--line);border-radius:22px;padding:16px;margin:12px 0;overflow:hidden}.chart svg{width:100%;height:auto;display:block}.chart-title{font-weight:950;margin:0 0 8px}.chart-note{color:var(--muted);font-size:13px;margin:6px 0 0}.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media(max-width:900px){.hero,.grid,.proof-grid,.steps,.two{grid-template-columns:1fr}nav{align-items:flex-start;flex-direction:column}.navlinks{gap:10px}}
""".strip()


JS = r"""
(function(){
  const fmt = new Intl.NumberFormat("en-US");
  const money = v => {
    const n = Number(v || 0);
    if (!Number.isFinite(n) || n === 0) return "—";
    if (Math.abs(n) >= 1e12) return "$" + (n/1e12).toFixed(2) + "T";
    if (Math.abs(n) >= 1e9) return "$" + (n/1e9).toFixed(2) + "B";
    if (Math.abs(n) >= 1e6) return "$" + (n/1e6).toFixed(2) + "M";
    return "$" + fmt.format(Math.round(n));
  };
  const pct = v => (v === undefined || v === null || v === "") ? "—" : Number(v).toFixed(1).replace(".0","") + "%";
  const safe = s => String(s ?? "").replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
  const color = i => ["#7dffb0","#86f8ff","#ffd66b","#d8a7ff","#9da8ff","#ffb86c"][i%6];

  async function loadStatus(){
    try{
      const res = await fetch("public_site_status.json?ts=" + Date.now());
      if(!res.ok) throw new Error("status fetch failed");
      return await res.json();
    }catch(e){
      console.warn(e);
      return null;
    }
  }

  function chartShell(el, title, note, svg){
    el.innerHTML = `<div class="chart-title">${safe(title)}</div>${svg}<div class="chart-note">${safe(note || "")}</div>`;
  }

  function barChart(el, title, rows, note){
    const w=760, h=Math.max(220, 58*rows.length+50), left=220, right=40;
    const max=Math.max(1, ...rows.map(r=>Number(r.value)||0));
    const bars=rows.map((r,i)=>{
      const y=42+i*52, bw=(w-left-right)*(Number(r.value)||0)/max;
      return `<text x="14" y="${y+24}" fill="#b3c0cd" font-size="14">${safe(r.label)}</text>
      <rect x="${left}" y="${y+6}" width="${w-left-right}" height="28" fill="rgba(255,255,255,.06)" rx="8"/>
      <rect x="${left}" y="${y+6}" width="${bw}" height="28" fill="${color(i)}" rx="8"/>
      <text x="${left+bw+10}" y="${y+25}" fill="#f4fbff" font-size="13" font-weight="700">${safe(r.display ?? r.value)}</text>`;
    }).join("");
    chartShell(el,title,note,`<svg viewBox="0 0 ${w} ${h}" role="img"><rect width="${w}" height="${h}" fill="transparent"/>${bars}</svg>`);
  }

  function donutChart(el, title, rows, note){
    const total = rows.reduce((a,r)=>a+(Number(r.value)||0),0) || 1;
    let start=0;
    const cx=160, cy=142, r=90, sw=28;
    const arcs=rows.map((row,i)=>{
      const val=(Number(row.value)||0)/total;
      const end=start+val*360;
      const large=end-start>180?1:0;
      const p1=polar(cx,cy,r,start), p2=polar(cx,cy,r,end);
      const dash=`<path d="M ${p1.x} ${p1.y} A ${r} ${r} 0 ${large} 1 ${p2.x} ${p2.y}" fill="none" stroke="${color(i)}" stroke-width="${sw}" stroke-linecap="round"/>`;
      start=end;
      return dash;
    }).join("");
    const legend=rows.map((row,i)=>`<g transform="translate(320 ${70+i*30})"><rect width="12" height="12" rx="3" fill="${color(i)}"/><text x="20" y="11" fill="#b3c0cd" font-size="13">${safe(row.label)}: ${safe(row.display ?? row.value)}</text></g>`).join("");
    chartShell(el,title,note,`<svg viewBox="0 0 760 300" role="img"><circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="rgba(255,255,255,.06)" stroke-width="${sw}"/>${arcs}<text x="${cx}" y="${cy-2}" text-anchor="middle" fill="#f4fbff" font-size="28" font-weight="900">${total}</text><text x="${cx}" y="${cy+24}" text-anchor="middle" fill="#b3c0cd" font-size="12">total</text>${legend}</svg>`);
  }

  function polar(cx,cy,r,deg){
    const a=(deg-90)*Math.PI/180;
    return {x:cx+r*Math.cos(a), y:cy+r*Math.sin(a)};
  }

  function lineChart(el, title, vals, note){
    const w=760,h=300,left=48,bottom=250,top=36,right=28;
    const max=Math.max(100,...vals), min=0;
    const pts=vals.map((v,i)=>{
      const x=left+i*((w-left-right)/Math.max(1,vals.length-1));
      const y=bottom-((v-min)/(max-min))*(bottom-top);
      return {x,y,v};
    });
    const poly=pts.map(p=>`${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
    const circles=pts.map((p,i)=>`<circle cx="${p.x}" cy="${p.y}" r="5" fill="#7dffb0"/><text x="${p.x}" y="276" text-anchor="middle" fill="#b3c0cd" font-size="11">v${i}</text>`).join("");
    chartShell(el,title,note,`<svg viewBox="0 0 ${w} ${h}" role="img"><line x1="${left}" y1="${bottom}" x2="${w-right}" y2="${bottom}" stroke="rgba(255,255,255,.18)"/><line x1="${left}" y1="${top}" x2="${left}" y2="${bottom}" stroke="rgba(255,255,255,.18)"/><polyline points="${poly}" fill="none" stroke="#7dffb0" stroke-width="4"/><path d="M ${poly.replaceAll(" "," L ")} L ${pts[pts.length-1]?.x||left} ${bottom} L ${left} ${bottom} Z" fill="rgba(125,255,176,.08)"/>${circles}</svg>`);
  }

  function radarChart(el, title, rows, note){
    const cx=380,cy=170,r=120,n=rows.length||1;
    const points=rows.map((row,i)=>{
      const a=-Math.PI/2+i*2*Math.PI/n;
      const val=Math.max(0,Math.min(100,Number(row.value)||0))/100;
      return {x:cx+r*val*Math.cos(a),y:cy+r*val*Math.sin(a), lx:cx+(r+32)*Math.cos(a), ly:cy+(r+32)*Math.sin(a), label:row.label, value:row.value};
    });
    const rings=[.25,.5,.75,1].map(fr=>{
      const p=rows.map((_,i)=>{const a=-Math.PI/2+i*2*Math.PI/n;return `${cx+r*fr*Math.cos(a)},${cy+r*fr*Math.sin(a)}`}).join(" ");
      return `<polygon points="${p}" fill="none" stroke="rgba(255,255,255,.11)"/>`;
    }).join("");
    const poly=points.map(p=>`${p.x},${p.y}`).join(" ");
    const axes=points.map(p=>`<line x1="${cx}" y1="${cy}" x2="${p.lx}" y2="${p.ly}" stroke="rgba(255,255,255,.08)"/><text x="${p.lx}" y="${p.ly}" text-anchor="middle" fill="#b3c0cd" font-size="11">${safe(p.label)}</text>`).join("");
    chartShell(el,title,note,`<svg viewBox="0 0 760 360" role="img">${rings}${axes}<polygon points="${poly}" fill="rgba(134,248,255,.18)" stroke="#86f8ff" stroke-width="3"/><circle cx="${cx}" cy="${cy}" r="3" fill="#fff"/></svg>`);
  }

  function constellation(el, title, roles, note){
    const w=760,h=520,cx=380,cy=260;
    const list=(roles&&roles.length?roles:["capital allocator","compute allocator","energy strategist","data moat","trust","talent","product","distribution","validation","risk","reinvestment","coordination"]);
    const nodes=list.slice(0,64).map((role,i)=>{
      const ring=i<20?120:i<44?175:225;
      const idx=i<20?i:i<44?i-20:i-44;
      const count=i<20?20:i<44?24:20;
      const a=-Math.PI/2+idx*2*Math.PI/count+(i<20?0:i<44?.13:.27);
      const x=cx+ring*Math.cos(a), y=cy+ring*Math.sin(a);
      return `<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" stroke="rgba(134,248,255,.08)"/><circle cx="${x}" cy="${y}" r="${i<20?6:5}" fill="${color(i)}"/><title>${safe(role)}</title>`;
    }).join("");
    chartShell(el,title,note,`<svg viewBox="0 0 ${w} ${h}" role="img"><circle cx="${cx}" cy="${cy}" r="70" fill="rgba(125,255,176,.11)" stroke="#7dffb0"/><text x="${cx}" y="${cy-6}" text-anchor="middle" fill="#f4fbff" font-size="18" font-weight="900">SkillOS</text><text x="${cx}" y="${cy+18}" text-anchor="middle" fill="#b3c0cd" font-size="12">coordination core</text>${nodes}</svg>`);
  }

  function render(status){
    const flagship=status.flagship_raw||{};
    const final=flagship.final||{};
    const single=flagship.single_agent_baseline||{};
    const uncoord=flagship.uncoordinated_pool||{};
    const stat=flagship.static_coordination||{};
    const agentSystem=flagship.agent_system||status.flagship||{};
    const releases=(flagship.rsi_releases||[]).filter(r=>r.released || r.generation===0);
    document.querySelectorAll("[data-live-count]").forEach(el=>{
      const key=el.getAttribute("data-live-count");
      el.textContent = status[key] ?? "—";
    });
    const charts=document.querySelectorAll("[data-chart]");
    charts.forEach(el=>{
      const type=el.getAttribute("data-chart");
      if(type==="proof-status"){
        const passed=(status.proved_or_passed_proof_count||0), total=(status.proof_count||0);
        donutChart(el,"Proof status",[{"label":"passed or ready","value":passed},{"label":"other entries","value":Math.max(0,total-passed)}],"Autonomously rebuilt from proof JSON, pages, reports, and workflow metadata.");
      }
      if(type==="workflow-status"){
        const rows=status.workflows||[];
        const counts={passing:0,running:0,failed:0,other:0};
        rows.forEach(w=>{const l=(w.conclusion==="success")?"passing":(["queued","in_progress","requested","waiting"].includes(w.status)?"running":(w.conclusion==="failure"?"failed":"other"));counts[l]++;});
        donutChart(el,"Workflow status",Object.entries(counts).map(([k,v])=>({label:k,value:v})),"Latest visible GitHub Actions state.");
      }
      if(type==="rsi-curve"){
        const vals=releases.map(r=>(r.validation||{}).fully_correct_percent ?? 0);
        lineChart(el,"Recursive self-improvement curve", vals.length?vals:[0,25,50,75,100],"Validation fully-correct rate across released protocol versions.");
      }
      if(type==="ablation-bars"){
        barChart(el,"Ablation: single agent vs pool vs coordination vs RSI",[
          {label:"Single agent", value:single.fully_correct_percent||0, display:pct(single.fully_correct_percent)},
          {label:"Uncoordinated pool", value:uncoord.fully_correct_percent||0, display:pct(uncoord.fully_correct_percent)},
          {label:"Static coordination", value:stat.fully_correct_percent||0, display:pct(stat.fully_correct_percent)},
          {label:"SkillOS RSI", value:final.fully_correct_percent||0, display:pct(final.fully_correct_percent)},
        ],"Shows whether recursive coordination beats both single-agent and uncoordinated multi-agent baselines.");
      }
      if(type==="capability-radar"){
        radarChart(el,"Capability coordination radar",[
          {label:"Coordination", value:final.coordination_protocol_accuracy_percent||0},
          {label:"Risk control", value:final.risk_control_accuracy_percent||0},
          {label:"Role quorum", value:final.role_quorum_accuracy_percent||0},
          {label:"Capability lever", value:final.capability_lever_accuracy_percent||0},
          {label:"Value capture", value:final.value_capture_rate_percent||0},
          {label:"Compounding", value:final.avg_compounding_index||0},
          {label:"Capacity", value:final.avg_productive_capacity_index||0},
        ],"The flagship proof measures coordination quality, risk discipline, compounding, and productive capacity.");
      }
      if(type==="agent-constellation"){
        constellation(el,"Specialist agent organization", (agentSystem.roles||status.flagship.roles||[]), "Visualizes the specialist roles coordinated by the flagship proof.");
      }
      if(type==="value-bars"){
        barChart(el,"Business effect metrics",[
          {label:"Value capture", value:final.value_capture_rate_percent||0, display:pct(final.value_capture_rate_percent)},
          {label:"Compounding index", value:final.avg_compounding_index||0},
          {label:"Productive capacity", value:final.avg_productive_capacity_index||0},
          {label:"Consensus", value:final.avg_consensus_score||0},
          {label:"Risk breach", value:final.risk_breach_rate_percent||0, display:pct(final.risk_breach_rate_percent)},
        ],"Benchmark values, not audited customer revenue.");
      }
    });
  }

  loadStatus().then(status=>{ if(status) render(status); });
})();
"""


def shell(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="assets/command-center.css">
<script defer src="assets/command-center.js"></script>
</head>
<body>
<nav>
  <a class="brand" href="index.html">SkillOS Proof Command Center</a>
  <div class="navlinks">
    <a href="index.html">Home</a>
    <a href="proofs.html">Proofs</a>
    <a href="actions.html">Actions</a>
    <a href="multi-agent.html">Multi-Agent</a>
    <a href="runbook.html">Run / Regenerate</a>
    <a href="{html.escape(repo_url())}">GitHub</a>
  </div>
</nav>
<main>{body}</main>
</body>
</html>
"""


def metric_value(p: dict[str, Any], key: str, default: str = "—") -> str:
    raw = p.get("raw") or {}
    if key in raw:
        return str(raw[key])
    final = raw.get("final") or {}
    if key in final:
        return str(final[key])
    if key in p:
        return str(p[key])
    return default


def proof_badge(p: dict[str, Any]) -> str:
    label = str(p.get("status") or status_label(p.get("latest_run_conclusion"), p.get("latest_run_status"))).lower().replace("_", " ")[:90]
    return f'<span class="badge {badge_class(label)}">{html.escape(label)}</span>'


def proof_card(p: dict[str, Any]) -> str:
    title = html.escape(str(p.get("title") or "SkillOS proof"))
    workflow = html.escape(str(p.get("workflow") or p.get("workflow_name") or "Autonomous public proof"))
    page_url = p.get("page_url")
    workflow_url = p.get("workflow_url") or p.get("latest_run_url")
    doc_url = p.get("doc_url")
    json_url = p.get("json_url")
    facts = []
    for label, key in [("agents", "agent_count"), ("roles", "role_count"), ("holdout", "holdout_count"), ("RSI releases", "rsi_releases")]:
        val = p.get(key)
        if val:
            facts.append(f"{val} {label}")
    fact_line = " · ".join(facts) or "public, reproducible proof"
    actions = []
    if page_url:
        actions.append(f'<a class="button" href="{html.escape(str(page_url))}">View proof</a>')
    if workflow_url:
        actions.append(f'<a class="button secondary" href="{html.escape(str(workflow_url))}">Run on GitHub</a>')
    if json_url:
        actions.append(f'<a class="button secondary" href="{html.escape(str(json_url))}">JSON</a>')
    if doc_url:
        actions.append(f'<a class="button secondary" href="{html.escape(str(doc_url))}">Docs</a>')
    if not actions:
        actions.append(f'<a class="button secondary" href="{html.escape(repo_url("actions"))}">Open Actions</a>')
    return f"""
<div class="proof-card">
  {proof_badge(p)}
  <h3>{title}</h3>
  <p>{workflow}</p>
  <p class="small">{html.escape(fact_line)}</p>
  <div class="actions">{''.join(actions)}</div>
</div>
"""


def workflows_table(workflows: list[dict[str, Any]], limit: int | None = None) -> str:
    rows = workflows if limit is None else workflows[:limit]
    body = []
    for w in rows:
        label = status_label(w.get("conclusion"), w.get("status"))
        wf_url = html.escape(str(w.get("workflow_url") or "#"))
        run_url = html.escape(str(w.get("run_url") or wf_url))
        body.append(f"""<tr>
<td><a href="{wf_url}"><strong>{html.escape(str(w.get("name") or "Workflow"))}</strong></a><br><span class="small mono">{html.escape(str(w.get("path") or ""))}</span></td>
<td><span class="badge {badge_class(label)}">{html.escape(label)}</span></td>
<td>{html.escape(str(w.get("event") or ""))}</td>
<td><a href="{run_url}">{html.escape(str(w.get("updated_at") or "not run yet"))}</a></td>
</tr>""")
    return "<table><tr><th>Workflow</th><th>Status</th><th>Event</th><th>Latest run</th></tr>" + "\n".join(body) + "</table>"


def role_chips(roles: list[str]) -> str:
    return "".join(f"<span>{html.escape(str(r).replace('_',' '))}</span>" for r in roles[:96])


def build_pages(status: dict[str, Any]) -> None:
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "command-center.css").write_text(CSS, encoding="utf-8")
    (ASSETS / "command-center.js").write_text(JS, encoding="utf-8")

    proofs = status["proofs"]
    workflows = status["workflows"]
    flagship = status["flagship"]
    raw = status.get("flagship_raw") or flagship.get("raw") or {}
    final = raw.get("final") or {}
    single = raw.get("single_agent_baseline") or {}
    uncoord = raw.get("uncoordinated_pool") or {}
    static = raw.get("static_coordination") or {}
    agent_system = raw.get("agent_system") or {}
    roles = agent_system.get("roles") or flagship.get("roles") or []
    run_all_url = repo_url("actions/workflows/skillos-run-all-public-proofs.yml")
    refresh_url = repo_url("actions/workflows/skillos-public-proof-command-center-refresh.yml")
    flagship_workflow = flagship.get("workflow_url") or repo_url("actions")
    flagship_page = flagship.get("page_url") or "rsi-capability-command-center-v17-proof.html"

    hero = f"""
<section class="hero">
  <div>
    <div class="eyebrow">MONTREAL.AI / SKILLOS</div>
    <h1>Autonomous Proof Command Center</h1>
    <p>Fresh, beautiful, GitHub-native hub for every SkillOS proof, run, receipt, report, chart, and visual dashboard.</p>
    <div class="actions">
      <a class="button gold" href="{html.escape(str(flagship_page))}">View flagship proof</a>
      <a class="button" href="{html.escape(str(flagship_workflow))}">Run flagship Action</a>
      <a class="button secondary" href="{html.escape(run_all_url)}">Run all proofs</a>
    </div>
  </div>
  <div class="card">
    <div class="eyebrow">Live freshness</div>
    <div class="status">Updated {html.escape(status['generated_at_utc'])}</div>
    <p>Autonomously regenerated from GitHub Actions workflows, latest runs, proof JSON receipts, proof reports, badges, and visual pages.</p>
    <p class="small">Repository: <a href="{html.escape(repo_url())}">{html.escape(REPO)}</a></p>
  </div>
</section>

<section class="section card">
  <div class="eyebrow">Capital-to-capability thesis</div>
  <div class="quote">Can autonomous coordination turn capital, compute, energy, data, trust, talent, product, distribution, validation, risk control, and reinvestment into compounding productive capability?</div>
  <p>This site does not claim superintelligence or Kardashev Type II achievement. It makes the mechanism publicly testable: a large specialist-agent organization improves its coordination layer through validation-gated Recursive Self-Improvement.</p>
</section>

<section class="grid">
  <div class="metric"><strong>{html.escape(str(flagship.get('agent_count') or agent_system.get('agent_count') or '—'))}</strong><span>flagship agents</span></div>
  <div class="metric"><strong>{html.escape(str(flagship.get('role_count') or agent_system.get('role_count') or '—'))}</strong><span>specialist roles</span></div>
  <div class="metric"><strong data-live-count="proof_count">{html.escape(str(status['proof_count']))}</strong><span>proof entries</span></div>
  <div class="metric"><strong data-live-count="recent_successful_runs">{html.escape(str(status['recent_successful_runs']))}</strong><span>recent successful runs</span></div>
</section>

<section class="two">
  <div class="chart" data-chart="rsi-curve"></div>
  <div class="chart" data-chart="capability-radar"></div>
</section>

<section class="section">
  <h2>Flagship multi-agent proof</h2>
  <div class="proof-grid">
    {proof_card(flagship)}
    <div class="proof-card">
      <span class="badge ok">large-scale coordination</span>
      <h3>Single agent vs uncoordinated pool vs static coordination vs SkillOS RSI</h3>
      <p>Many agents alone are not the moat. Recursive improvement of the coordination layer is the moat.</p>
      <div class="actions">
        <a class="button" href="multi-agent.html">See comparison</a>
        <a class="button secondary" href="{html.escape(str(flagship_workflow))}">Run proof</a>
      </div>
    </div>
  </div>
</section>

<section class="two">
  <div class="chart" data-chart="proof-status"></div>
  <div class="chart" data-chart="workflow-status"></div>
</section>

<section class="section">
  <h2>Proof library</h2>
  <div class="proof-grid">{''.join(proof_card(p) for p in proofs[:8])}</div>
  <div class="actions"><a class="button secondary" href="proofs.html">View all proofs</a></div>
</section>

<section class="section">
  <h2>Run or regenerate</h2>
  <div class="steps">
    <div class="step"><strong>Run one proof</strong><p>Open a proof card, click <span class="mono">Run on GitHub</span>, then click <span class="mono">Run workflow</span>.</p></div>
    <div class="step"><strong>Run all proofs</strong><p>Use the orchestrator workflow to dispatch public proof workflows from one place.</p><p><a class="button" href="{html.escape(run_all_url)}">Run all public proofs</a></p></div>
    <div class="step"><strong>Refresh hub</strong><p>The refresh workflow rebuilds the public site from proof receipts and latest run metadata.</p><p><a class="button secondary" href="{html.escape(refresh_url)}">Refresh site</a></p></div>
  </div>
</section>

<section class="section">
  <h2>Latest Actions status</h2>
  {workflows_table(workflows, limit=12)}
</section>

<section class="notice">
  <strong>Public boundary:</strong> These are autonomous deterministic market-readiness proofs using synthetic/redacted-style benchmark data and benchmark assumptions. They are not audited customer ROI, live customer adoption, financial advice, investment advice, superintelligence, Kardashev Type II achievement, or guarantees.
</section>
"""
    (SITE / "index.html").write_text(shell("SkillOS Public Proof Command Center", hero), encoding="utf-8")

    proofs_body = f"""
<section class="section">
  <div class="eyebrow">All public proof entries</div>
  <h2>Proof Library</h2>
  <p class="lead">Every proof card links to the visual page when available, the GitHub Action that regenerates it, the Markdown report, and the machine-readable JSON receipt.</p>
  <div class="two">
    <div class="chart" data-chart="proof-status"></div>
    <div class="chart" data-chart="value-bars"></div>
  </div>
  <div class="proof-grid">{''.join(proof_card(p) for p in proofs)}</div>
</section>
"""
    (SITE / "proofs.html").write_text(shell("SkillOS Proof Library", proofs_body), encoding="utf-8")

    actions_body = f"""
<section class="section">
  <div class="eyebrow">Workflow command board</div>
  <h2>GitHub Actions Status</h2>
  <p class="lead">The public website refreshes from workflow files and latest workflow runs. Use this page to see what can be rerun.</p>
  <div class="actions">
    <a class="button" href="{html.escape(run_all_url)}">Run all public proofs</a>
    <a class="button secondary" href="{html.escape(refresh_url)}">Refresh site</a>
    <a class="button secondary" href="{html.escape(repo_url('actions'))}">Open all Actions</a>
  </div>
  <div class="chart" data-chart="workflow-status"></div>
  {workflows_table(workflows)}
</section>
"""
    (SITE / "actions.html").write_text(shell("SkillOS Actions Status", actions_body), encoding="utf-8")

    multi_body = f"""
<section class="section">
  <div class="eyebrow">Large-scale agentic coordination</div>
  <h2>Multi-Agent Command Center</h2>
  <p class="lead">The flagship proof shows a large specialist-agent system coordinating to maximum effect through validation-gated Recursive Self-Improvement.</p>
</section>
<section class="grid">
  <div class="metric"><strong>{html.escape(str(agent_system.get('agent_count') or flagship.get('agent_count') or '—'))}</strong><span>specialist agents</span></div>
  <div class="metric"><strong>{html.escape(str(agent_system.get('role_count') or flagship.get('role_count') or '—'))}</strong><span>roles</span></div>
  <div class="metric"><strong>{html.escape(str(metric_value(flagship,'fully_correct_gain_vs_single_agent_points')))}</strong><span>gain vs single agent</span></div>
  <div class="metric"><strong>{html.escape(str(metric_value(flagship,'synthetic_value_captured_over_single_agent_usd')))}</strong><span>benchmark value over baseline</span></div>
</section>
<section class="two">
  <div class="chart" data-chart="agent-constellation"></div>
  <div class="chart" data-chart="ablation-bars"></div>
</section>
<section class="two">
  <div class="chart" data-chart="capability-radar"></div>
  <div class="chart" data-chart="value-bars"></div>
</section>
<section class="section card">
  <h2>Specialist roles</h2>
  <div class="roles">{role_chips(roles)}</div>
</section>
<section class="section">
  <h2>Ablation comparison</h2>
  <table>
    <tr><th>Metric</th><th>Single agent</th><th>Uncoordinated pool</th><th>Static coordination</th><th>SkillOS RSI</th></tr>
    <tr><td>Fully correct</td><td>{single.get('fully_correct_percent','—')}%</td><td>{uncoord.get('fully_correct_percent','—')}%</td><td>{static.get('fully_correct_percent','—')}%</td><td>{final.get('fully_correct_percent','—')}%</td></tr>
    <tr><td>Coordination accuracy</td><td>{single.get('coordination_protocol_accuracy_percent','—')}%</td><td>{uncoord.get('coordination_protocol_accuracy_percent','—')}%</td><td>{static.get('coordination_protocol_accuracy_percent','—')}%</td><td>{final.get('coordination_protocol_accuracy_percent','—')}%</td></tr>
    <tr><td>Risk control</td><td>{single.get('risk_control_accuracy_percent','—')}%</td><td>{uncoord.get('risk_control_accuracy_percent','—')}%</td><td>{static.get('risk_control_accuracy_percent','—')}%</td><td>{final.get('risk_control_accuracy_percent','—')}%</td></tr>
    <tr><td>Value capture</td><td>{single.get('value_capture_rate_percent','—')}%</td><td>{uncoord.get('value_capture_rate_percent','—')}%</td><td>{static.get('value_capture_rate_percent','—')}%</td><td>{final.get('value_capture_rate_percent','—')}%</td></tr>
    <tr><td>Risk breach</td><td>{single.get('risk_breach_rate_percent','—')}%</td><td>{uncoord.get('risk_breach_rate_percent','—')}%</td><td>{static.get('risk_breach_rate_percent','—')}%</td><td>{final.get('risk_breach_rate_percent','—')}%</td></tr>
  </table>
</section>
<section class="section card">
  <h2>What it proves</h2>
  <p>Many agents alone are not enough. Uncoordinated agents are not enough. Static coordination is not enough. SkillOS tests whether the coordination layer can recursively improve through validation-gated protocol releases and then generalize to adversarial holdout market states.</p>
  <div class="actions">
    <a class="button" href="{html.escape(str(flagship_page))}">View flagship proof</a>
    <a class="button secondary" href="{html.escape(str(flagship_workflow))}">Run flagship Action</a>
  </div>
</section>
<section class="notice"><strong>Boundary:</strong> This is a benchmark proof of coordination mechanics, not a claim of superintelligence, audited customer ROI, or Kardashev Type II achievement.</section>
"""
    (SITE / "multi-agent.html").write_text(shell("SkillOS Multi-Agent Command Center", multi_body), encoding="utf-8")

    runbook_body = f"""
<section class="section">
  <div class="eyebrow">Friendly runbook</div>
  <h2>Run and regenerate everything</h2>
  <p class="lead">Designed for non-technical viewers and maintainers. Every proof can be rerun from GitHub Actions, and this site can be refreshed on demand.</p>
  <div class="steps">
    <div class="step"><strong>1. Run flagship proof</strong><p>Open the flagship workflow and press <span class="mono">Run workflow</span>.</p><p><a class="button" href="{html.escape(str(flagship_workflow))}">Run flagship</a></p></div>
    <div class="step"><strong>2. Run all proofs</strong><p>Dispatch all public proof workflows from one place.</p><p><a class="button secondary" href="{html.escape(run_all_url)}">Run all proofs</a></p></div>
    <div class="step"><strong>3. Refresh public site</strong><p>Regenerate the command center from latest proof receipts and workflow metadata.</p><p><a class="button secondary" href="{html.escape(refresh_url)}">Refresh site</a></p></div>
  </div>
</section>
<section class="section card">
  <h2>Future-proofing rule</h2>
  <p>For new proofs: include <span class="mono">Proof</span> or <span class="mono">RSI</span> in the workflow name, generate JSON into <span class="mono">data/</span>, Markdown into <span class="mono">docs/</span>, and visual HTML into <span class="mono">site/</span>. The command center discovers them automatically.</p>
</section>
<section class="notice"><strong>Safe boundary:</strong> This site makes proof outputs easy to inspect and rerun. It does not convert benchmark results into audited customer results or guarantees.</section>
"""
    (SITE / "runbook.html").write_text(shell("SkillOS Runbook", runbook_body), encoding="utf-8")


def markdown_status(status: dict[str, Any]) -> str:
    lines = [
        "# SkillOS Public Proof Command Center Status",
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
        "## Flagship",
        "",
        f"- Title: {status['flagship'].get('title')}",
        f"- Status: {status['flagship'].get('status')}",
        f"- Agents: {status['flagship'].get('agent_count')}",
        f"- Roles: {status['flagship'].get('role_count')}",
        "",
        "## Proof entries",
        "",
    ]
    for p in status["proofs"]:
        lines.append(f"- **{p.get('title')}**")
        if p.get("page_url"):
            lines.append(f"  - Page: {p.get('page_url')}")
        if p.get("workflow_url"):
            lines.append(f"  - Workflow: {p.get('workflow_url')}")
        if p.get("json_url"):
            lines.append(f"  - JSON: {p.get('json_url')}")
    lines += [
        "",
        "## Safe boundary",
        "",
        status["safe_boundary"],
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    workflows = github_workflows()
    runs = github_runs()
    proofs = collect_proofs(workflows, runs)
    flagship = pick_flagship(proofs)
    status = status_object(workflows, runs, proofs, flagship)

    build_pages(status)

    status_json = json.dumps(status, indent=2, sort_keys=True) + "\n"
    (SITE / "public_site_status.json").write_text(status_json, encoding="utf-8")
    (DATA / "public_site_status.json").write_text(status_json, encoding="utf-8")
    (DOCS / "SKILLOS_PUBLIC_SITE_STATUS.md").write_text(markdown_status(status), encoding="utf-8")

    print(json.dumps({
        "status": "PUBLIC_PROOF_COMMAND_CENTER_REFRESHED",
        "site_url": SITE_URL,
        "generated_at_utc": status["generated_at_utc"],
        "proof_count": status["proof_count"],
        "workflow_count": status["workflow_count"],
        "flagship": status["flagship"].get("title"),
        "outputs": [
            "site/index.html",
            "site/proofs.html",
            "site/actions.html",
            "site/multi-agent.html",
            "site/runbook.html",
            "site/assets/command-center.css",
            "site/assets/command-center.js",
            "site/public_site_status.json",
            "data/public_site_status.json",
            "docs/SKILLOS_PUBLIC_SITE_STATUS.md",
        ],
    }, indent=2))

if __name__ == "__main__":
    main()
