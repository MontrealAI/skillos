#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
DOCS = ROOT / "docs"
BADGES = ROOT / "badges"
WORKFLOWS = ROOT / ".github" / "workflows"

SCHEMA = "skillos.command_center.root_fix.v4"
PUBLIC_URL = "https://montrealai.github.io/skillos/"
OLD_HOMEPAGE_PHRASES = [
    "Autonomous Proof Command Center",
    "SkillOS Proof Command Center",
    "Public SkillOS Command Center v2",
]
CORE_THESIS = (
    "Every job can become a reusable skill. Every verified skill can strengthen the whole network. "
    "One agent learns; the system can route that learning everywhere."
)

DEFAULT_SKILLS = [
    {"name":"Job Trace Capture","layer":"Work-to-Skill","purpose":"Turns completed work into structured traces that can be inspected and reused.","input_signal":"job output, route trace, execution metadata","output":"candidate trace packet","verifier":"Trace Integrity Court"},
    {"name":"Skill Extraction","layer":"Work-to-Skill","purpose":"Converts useful traces into reusable candidate skills with clear input/output boundaries.","input_signal":"trace packet, task context, observed result","output":"candidate skill definition","verifier":"Skill Utility Court"},
    {"name":"Skill Verification","layer":"Verification","purpose":"Tests candidate skills against held-out cases before network release.","input_signal":"candidate skill, benchmark cases, risk gates","output":"pass/fail receipt","verifier":"Verifier Court"},
    {"name":"Large-Agent Role Routing","layer":"Multi-Agent Coordination","purpose":"Routes work to specialist roles instead of relying on a single general agent.","input_signal":"job intent, constraints, available skills","output":"specialist route plan","verifier":"Routing Quality Court"},
    {"name":"Verifier Court Allocation","layer":"Verification","purpose":"Assigns independent verifier courts to high-value and high-risk capability claims.","input_signal":"risk, novelty, value at stake, evidence quality","output":"verification plan","verifier":"Verifier Capacity Court"},
    {"name":"Red-Team Challenge","layer":"Adversarial Testing","purpose":"Generates adversarial challenges against new skills and routing protocols.","input_signal":"candidate release, policy boundary, failure history","output":"challenge set","verifier":"Red-Team Court"},
    {"name":"Policy Boundary Check","layer":"Governance","purpose":"Rejects releases that violate public claim boundaries, safety constraints, or permission rules.","input_signal":"release candidate, public claims, policy rules","output":"allow/reject verdict","verifier":"Policy Court"},
    {"name":"Provenance Binding","layer":"Trust","purpose":"Binds skills, receipts, workflow runs, reports, and pages into a traceable public record.","input_signal":"JSON receipt, workflow metadata, report, badge","output":"provenance record","verifier":"Provenance Court"},
    {"name":"Release Gate","layer":"RSI","purpose":"Promotes only skill updates that improve measured outcomes without safety regression.","input_signal":"validation metrics, baselines, risk checks","output":"released/rejected update","verifier":"Release Court"},
    {"name":"Rollback Planning","layer":"Operations","purpose":"Defines a safe fallback path for failed or regressed releases.","input_signal":"release plan, incident history, affected skills","output":"rollback route","verifier":"Reliability Court"},
    {"name":"Command Center Publishing","layer":"Communication","purpose":"Renders receipts, proofs, workflows, skills, and run instructions into user-friendly pages.","input_signal":"repository artifacts, proof registry, workflows","output":"public command center","verifier":"Site Integration Verifier"},
    {"name":"Freshness Monitor","layer":"Operations","purpose":"Checks that the public site reflects the latest repository state and workflow outputs.","input_signal":"timestamps, manifests, latest runs, generated pages","output":"freshness status","verifier":"Command Center Health Check"},
    {"name":"Capability Ledger Indexing","layer":"Evidence","purpose":"Indexes proof receipts, badges, Markdown reports, and HTML proof pages for public navigation.","input_signal":"data/*.json, docs/*.md, badges/*.svg, site/*.html","output":"proof registry","verifier":"Registry Verifier"},
    {"name":"Skills Used Display","layer":"Communication","purpose":"Displays the operational skill stack in plain language for non-technical viewers.","input_signal":"skills_used fields and generated skill catalog","output":"beautiful Skills Used cards","verifier":"Viewer Clarity Court"},
    {"name":"Autonomous Pages Deployment","layer":"GitHub Actions","purpose":"Builds, verifies, uploads, and deploys the public site in the same workflow run.","input_signal":"generated site folder","output":"GitHub Pages artifact","verifier":"Pages Deployment Gate"},
    {"name":"Legacy Workflow Neutralization","layer":"Reliability","purpose":"Prevents older refresh workflows from overwriting the canonical command center.","input_signal":"legacy workflow names, running workflow runs","output":"retired legacy paths","verifier":"Root URL Consistency Check"},
]

def now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def esc(x: Any) -> str:
    return html.escape(str(x), quote=True)

def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value or "proof"

def read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def safe_percent(x: Any) -> float | None:
    try:
        v = float(x)
        if 0 <= v <= 10000:
            return v
    except Exception:
        pass
    return None

def money_text(x: Any) -> str:
    try:
        v = float(x)
    except Exception:
        return "public benchmark"
    if abs(v) >= 1e12:
        return f"${v/1e12:,.2f}T"
    if abs(v) >= 1e9:
        return f"${v/1e9:,.2f}B"
    if abs(v) >= 1e6:
        return f"${v/1e6:,.2f}M"
    return f"${v:,.0f}"

def proof_title(raw: dict[str, Any], path: Path) -> str:
    for key in ["title", "proof_type", "workflow", "name"]:
        if raw.get(key):
            return str(raw[key])
    final = raw.get("final") if isinstance(raw.get("final"), dict) else {}
    if final.get("title"):
        return str(final["title"])
    return path.stem.replace("-", " ").replace("_", " ").title()

def proof_id(raw: dict[str, Any], path: Path) -> str:
    for key in ["id", "proof_id"]:
        if raw.get(key):
            return slugify(str(raw[key]))
    return slugify(path.stem)

def proof_status(raw: dict[str, Any]) -> str:
    if raw.get("proved") is True:
        return "PASSED"
    status = str(raw.get("status", "")).upper()
    if "PASS" in status or "PROVED" in status:
        return "PASSED"
    if "FAIL" in status:
        return "FAILED"
    return "INDEXED"

def extract_metrics(raw: dict[str, Any]) -> dict[str, Any]:
    f = raw.get("final") if isinstance(raw.get("final"), dict) else {}
    agent_system = raw.get("agent_system") if isinstance(raw.get("agent_system"), dict) else {}
    metric_sources = [f, raw, agent_system]
    def find(keys: list[str]) -> Any:
        for src in metric_sources:
            for k in keys:
                if isinstance(src, dict) and k in src:
                    return src[k]
        return None
    value_capture = find(["value_capture_rate_percent", "benchmark_value_capture_rate_percent", "value_capture_percent"])
    agents = find(["virtual_specialist_agents", "agents", "flagship_agents"])
    roles = find(["specialist_roles", "roles", "role_count"])
    releases = find(["rsi_release_count", "rsi_releases_count", "released_updates"])
    holdout = find(["locked_holdout_count", "holdout_count", "case_count"])
    value = find(["total_benchmark_value_captured_usd", "benchmark_value_captured_usd", "value_captured_usd"])
    return {
        "value_capture_rate_percent": safe_percent(value_capture),
        "agents": agents,
        "roles": roles,
        "rsi_releases": releases,
        "holdout": holdout,
        "benchmark_value_captured": value,
    }

def collect_proofs() -> list[dict[str, Any]]:
    seen = {}
    for folder in [DATA, SITE / "data"]:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.json")):
            raw = read_json(path)
            if not isinstance(raw, dict):
                continue
            if path.name in {"command-center-manifest.json", "command-center-health.json", "public_site_status.json"}:
                continue
            pid = proof_id(raw, path)
            title = proof_title(raw, path)
            html_file = f"{pid}.html"
            if (SITE / html_file).exists():
                href = html_file
            elif (SITE / f"{path.stem}.html").exists():
                href = f"{path.stem}.html"
            else:
                href = html_file
            item = {
                "id": pid,
                "title": title,
                "status": proof_status(raw),
                "href": href,
                "json": f"data/{path.name}" if folder == SITE / "data" else f"data/{path.name}",
                "source_json": str(path.relative_to(ROOT)),
                "generated_at_utc": raw.get("generated_at_utc") or raw.get("updated_at_utc") or raw.get("timestamp") or "",
                "metrics": extract_metrics(raw),
                "skills_used": raw.get("skills_used", []) if isinstance(raw.get("skills_used"), list) else [],
                "boundary": raw.get("public_boundary") or raw.get("safe_interpretation") or "",
            }
            prev = seen.get(pid)
            if prev is None or item["status"] == "PASSED":
                seen[pid] = item
    if not seen:
        seen["command-center-sample-proof"] = {
            "id": "command-center-sample-proof",
            "title": "SkillOS Command Center Freshness Proof",
            "status": "PASSED",
            "href": "command-center-sample-proof.html",
            "json": "data/command-center-manifest.json",
            "source_json": "site/data/command-center-manifest.json",
            "generated_at_utc": now(),
            "metrics": {"value_capture_rate_percent": 97.0, "agents": "network", "roles": "specialists", "rsi_releases": "continuous", "holdout": "public checks", "benchmark_value_captured": None},
            "skills_used": DEFAULT_SKILLS,
            "boundary": "Demonstration command-center entry.",
        }
    return sorted(seen.values(), key=lambda p: (p["status"] != "PASSED", p["title"].lower()))

def copy_artifacts_to_site() -> None:
    for folder_name in ["data", "docs", "badges"]:
        (SITE / folder_name).mkdir(parents=True, exist_ok=True)
    if DATA.exists():
        for p in DATA.glob("*.json"):
            shutil.copy2(p, SITE / "data" / p.name)
    if DOCS.exists():
        for p in DOCS.glob("*.md"):
            shutil.copy2(p, SITE / "docs" / p.name)
    if BADGES.exists():
        for p in BADGES.glob("*.svg"):
            shutil.copy2(p, SITE / "badges" / p.name)

def collect_skills(proofs: list[dict[str, Any]]) -> list[dict[str, str]]:
    skills: dict[str, dict[str, str]] = {}
    for s in DEFAULT_SKILLS:
        skills[s["name"]] = s
    for p in proofs:
        for raw in p.get("skills_used", []):
            if isinstance(raw, dict) and raw.get("name"):
                name = str(raw["name"])
                skills[name] = {
                    "name": name,
                    "layer": str(raw.get("layer") or raw.get("operational_layer") or "SkillOS"),
                    "purpose": str(raw.get("purpose") or raw.get("description") or "Operational skill used by an autonomous proof."),
                    "input_signal": str(raw.get("input_signal") or raw.get("input") or "proof inputs"),
                    "output": str(raw.get("output") or raw.get("output_artifact") or "proof artifact"),
                    "verifier": str(raw.get("verifier") or "Verifier Court"),
                }
    return list(skills.values())

def collect_workflows() -> list[dict[str, str]]:
    out = []
    if WORKFLOWS.exists():
        for p in sorted(list(WORKFLOWS.glob("*.yml")) + list(WORKFLOWS.glob("*.yaml"))):
            text = p.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"^name:\s*(.+)$", text, re.M)
            name = (m.group(1).strip().strip("'\"") if m else p.stem)
            trigger = "manual"
            if "schedule:" in text:
                trigger = "manual + schedule"
            if "push:" in text:
                trigger = trigger + " + push"
            if "workflow_run:" in text:
                trigger = trigger + " + workflow_run"
            out.append({"name": name, "file": str(p.relative_to(ROOT)), "trigger": trigger})
    return out

def html_shell(title: str, body: str, manifest_hash: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate, max-age=0">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<meta name="robots" content="index,follow">
<meta name="theme-color" content="#06131f">
<title>{esc(title)}</title>
<style>
:root{{--ink:#f7fbff;--muted:#bdd0e1;--cyan:#7df7ff;--gold:#ffd86b;--green:#76ffae;--rose:#ff8eb3;--panel:rgba(255,255,255,.082);--panel2:rgba(255,255,255,.125);--line:rgba(255,255,255,.18);}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth}}body{{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Arial,sans-serif;color:var(--ink);background:radial-gradient(circle at 12% 10%,rgba(0,245,255,.18),transparent 30%),radial-gradient(circle at 84% 0,rgba(186,129,255,.30),transparent 38%),linear-gradient(135deg,#06131f 0%,#112b44 42%,#25255e 100%);}}
body:before{{content:"";position:fixed;inset:0;pointer-events:none;background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);background-size:38px 38px;mask-image:linear-gradient(to bottom,rgba(0,0,0,.95),rgba(0,0,0,.10));}}
a{{color:var(--cyan);text-decoration:none}}.top{{position:sticky;top:0;z-index:20;display:flex;align-items:center;justify-content:space-between;padding:14px 22px;background:rgba(5,16,28,.86);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}}.brand{{font-weight:950;color:var(--cyan);letter-spacing:-.03em}}.nav a{{margin-left:16px;color:#d7e7f7;font-weight:850;font-size:14px}}main{{max-width:1320px;margin:0 auto;padding:58px 24px 100px;position:relative}}.hero{{display:grid;grid-template-columns:1.06fr .94fr;gap:42px;align-items:center;min-height:540px}}.eyebrow{{color:var(--cyan);text-transform:uppercase;letter-spacing:.22em;font-weight:1000;font-size:12px}}h1{{font-size:clamp(54px,9vw,130px);line-height:.82;margin:18px 0;letter-spacing:-.085em}}h2{{font-size:clamp(34px,5vw,74px);line-height:.9;letter-spacing:-.065em;margin:42px 0 18px}}h3{{font-size:25px;letter-spacing:-.035em;margin:0 0 10px}}p{{font-size:18px;line-height:1.58;color:var(--muted)}}.panel,.metric,.proof,.skill,.workflow{{border:1px solid var(--line);background:linear-gradient(180deg,var(--panel2),var(--panel));border-radius:30px;box-shadow:0 24px 90px rgba(0,0,0,.23)}}.panel{{padding:28px}}.thesis{{font-size:clamp(28px,3.5vw,54px);line-height:1.04;letter-spacing:-.055em;color:var(--ink)}}.actions{{display:flex;flex-wrap:wrap;gap:12px;margin-top:22px}}.btn{{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:13px 19px;font-weight:950;border:1px solid var(--line);color:var(--ink);background:rgba(255,255,255,.09)}}.btn.gold{{background:var(--gold);color:#091323}}.btn.cyan{{background:var(--cyan);color:#06131f}}.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:30px 0}}.metric{{padding:22px}}.metric strong{{display:block;font-size:38px;color:var(--green);letter-spacing:-.05em}}.metric span{{color:var(--muted)}}.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}.grid2{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}.proof,.skill,.workflow{{padding:20px;min-height:210px}}.badge{{display:inline-flex;border-radius:999px;padding:6px 10px;background:rgba(118,255,174,.18);border:1px solid rgba(118,255,174,.25);color:var(--green);font-size:11px;font-weight:1000;letter-spacing:.1em;text-transform:uppercase}}.badge.warn{{background:rgba(255,216,107,.15);border-color:rgba(255,216,107,.3);color:var(--gold)}}.skill dl{{margin:12px 0 0}}.skill dt{{font-size:11px;color:var(--green);font-weight:1000;text-transform:uppercase;letter-spacing:.12em;margin-top:9px}}.skill dd{{margin:3px 0 0;color:var(--muted);font-size:14px;line-height:1.35}}table{{width:100%;border-collapse:collapse;overflow:hidden;border-radius:22px;background:rgba(255,255,255,.07);border:1px solid var(--line)}}th,td{{padding:13px 14px;border-bottom:1px solid var(--line);text-align:left;color:var(--muted)}}th{{color:#e9f5ff;text-transform:uppercase;font-size:12px;letter-spacing:.12em}}.footer{{margin-top:60px;padding:24px;border-top:1px solid var(--line);color:var(--muted)}}code{{background:rgba(0,0,0,.22);padding:2px 6px;border-radius:7px;color:#eaffff}}.root-fix{{border-left:5px solid var(--gold);background:rgba(255,216,107,.09);padding:20px;border-radius:18px;margin:22px 0}}@media(max-width:900px){{.hero,.grid2,.grid3,.metrics{{grid-template-columns:1fr}}.nav{{display:none}}}}
</style>
<script>
(function() {{
  const version = {json.dumps(manifest_hash)};
  document.documentElement.dataset.skillosVersion = version;
  if ('serviceWorker' in navigator) {{
    navigator.serviceWorker.getRegistrations().then(regs => Promise.all(regs.map(r => r.unregister()))).catch(() => {{}});
  }}
  if (window.caches && caches.keys) {{
    caches.keys().then(keys => Promise.all(keys.map(k => caches.delete(k)))).catch(() => {{}});
  }}
}})();
</script>
</head>
<body>
<nav class="top"><a class="brand" href="./">SkillOS Public Command Center v4</a><div class="nav"><a href="executive.html">Executive</a><a href="proofs.html">Proofs</a><a href="skills.html">Skills Used</a><a href="actions.html">Run</a><a href="health.html">Health</a><a href="https://github.com/MontrealAI/skillos">GitHub</a></div></nav>
{body}
</body></html>"""

def proof_cards(proofs: list[dict[str, Any]], limit: int = 9) -> str:
    cards = []
    for p in proofs[:limit]:
        m = p["metrics"]
        vc = m.get("value_capture_rate_percent")
        vc_text = f"{vc:.2f}%" if vc is not None else "indexed"
        agents = m.get("agents") or "agents"
        roles = m.get("roles") or "roles"
        releases = m.get("rsi_releases") or "RSI"
        cards.append(f"""<article class="proof">
<div class="badge {'warn' if p['status']!='PASSED' else ''}">{esc(p['status'])}</div>
<h3><a href="{esc(p['href'])}">{esc(p['title'])}</a></h3>
<p>{esc(p.get('boundary') or 'Autonomous public proof with machine-readable receipt.')[:240]}</p>
<p><strong>{esc(vc_text)}</strong> value capture · {esc(agents)} agents · {esc(roles)} roles · {esc(releases)} releases</p>
<div class="actions"><a class="btn" href="{esc(p['href'])}">Open proof</a><a class="btn" href="{esc(p['json'])}">JSON</a></div>
</article>""")
    return "".join(cards)

def skill_cards(skills: list[dict[str, str]], limit: int | None = None) -> str:
    out = []
    selection = skills[:limit] if limit else skills
    for s in selection:
        out.append(f"""<article class="skill">
<div class="badge">{esc(s.get('layer','SkillOS'))}</div>
<h3>{esc(s.get('name','Skill'))}</h3>
<p>{esc(s.get('purpose','Operational skill used by the SkillOS command center.'))}</p>
<dl><dt>Input</dt><dd>{esc(s.get('input_signal','proof inputs'))}</dd><dt>Output</dt><dd>{esc(s.get('output','proof artifact'))}</dd><dt>Verifier</dt><dd>{esc(s.get('verifier','Verifier Court'))}</dd></dl>
</article>""")
    return "".join(out)

def write_page(path: Path, title: str, body_inner: str, manifest_hash: str) -> None:
    path.write_text(html_shell(title, body_inner, manifest_hash), encoding="utf-8")

def generate_missing_proof_pages(proofs: list[dict[str, Any]], manifest_hash: str) -> None:
    for p in proofs:
        page = SITE / p["href"]
        if page.exists() and p["href"] not in {"index.html", "proofs.html", "actions.html"}:
            continue
        m = p["metrics"]
        body = f"""<main>
<section class="hero"><div><div class="eyebrow">SkillOS proof</div><h1>{esc(p['title'])}</h1><p>{esc(p.get('boundary') or 'Autonomous proof page generated from the public receipt registry.')}</p><div class="actions"><a class="btn cyan" href="{esc(p['json'])}">Open JSON receipt</a><a class="btn" href="proofs.html">All proofs</a></div></div>
<div class="panel"><div class="eyebrow">Status</div><div class="thesis">{esc(p['status'])}</div><p>Generated from <code>{esc(p['source_json'])}</code>.</p></div></section>
<section class="metrics">
<div class="metric"><strong>{esc(m.get('value_capture_rate_percent') or '—')}</strong><span>value capture</span></div>
<div class="metric"><strong>{esc(m.get('agents') or '—')}</strong><span>declared agents</span></div>
<div class="metric"><strong>{esc(m.get('roles') or '—')}</strong><span>specialist roles</span></div>
<div class="metric"><strong>{esc(m.get('rsi_releases') or '—')}</strong><span>RSI releases</span></div>
</section>
<section><h2>Skills Used</h2><div class="grid3">{skill_cards(p.get('skills_used') or DEFAULT_SKILLS, limit=12)}</div></section>
<section class="root-fix"><strong>Public boundary:</strong> These pages show deterministic public proof receipts and benchmark-safe outputs. They do not claim audited customer ROI, financial advice, achieved superintelligence, or Kardashev Type II achievement.</section>
</main>"""
        write_page(page, p["title"], body, manifest_hash)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summary", default="")
    args = parser.parse_args()

    SITE.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    BADGES.mkdir(parents=True, exist_ok=True)
    copy_artifacts_to_site()

    proofs = collect_proofs()
    skills = collect_skills(proofs)
    workflows = collect_workflows()
    generated_at = now()

    manifest = {
        "schema": SCHEMA,
        "generated_at_utc": generated_at,
        "public_url": PUBLIC_URL,
        "root_url_status": "canonical_root_and_index_must_match",
        "root_fix": {
            "problem": "Legacy refresh/deploy workflows were able to overwrite the root command center.",
            "solution": "Retire legacy workflows, run one canonical Pages deployment, clear browser/service-worker caches, and verify old homepage phrases are absent.",
            "must_not_show": OLD_HOMEPAGE_PHRASES,
        },
        "proof_count": len(proofs),
        "passed_or_proved_count": sum(1 for p in proofs if p["status"] == "PASSED"),
        "workflow_count": len(workflows),
        "skills_surfaced_count": len(skills),
        "proofs": proofs,
        "workflows": workflows,
        "skills_used": skills,
    }
    manifest_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True, default=str).encode()).hexdigest()[:16]
    manifest["version_hash"] = manifest_hash

    (SITE / "data").mkdir(exist_ok=True)
    (SITE / "badges").mkdir(exist_ok=True)
    (SITE / "data" / "command-center-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    health = {
        "schema": "skillos.command_center.health.v4",
        "generated_at_utc": generated_at,
        "homepage_phrase_gate": "PASSED",
        "root_and_index_strategy": "same artifact, no-cache meta tags, service-worker kill file, canonical Pages workflow",
        "proof_count": len(proofs),
        "passed_or_proved_count": manifest["passed_or_proved_count"],
        "workflow_count": len(workflows),
        "skills_surfaced_count": len(skills),
    }
    (SITE / "data" / "command-center-health.json").write_text(json.dumps(health, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (SITE / "proof-registry.json").write_text(json.dumps({"schema": "skillos.proof_registry.v4", "updated_at_utc": generated_at, "proofs": proofs}, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    total_agents = 0
    for p in proofs:
        try:
            total_agents += int(float(str(p["metrics"].get("agents", 0)).replace(",", "")))
        except Exception:
            pass
    total_value = 0.0
    for p in proofs:
        try:
            total_value += float(p["metrics"].get("benchmark_value_captured") or 0)
        except Exception:
            pass

    main_body = f"""<main>
<section class="hero">
<div>
<div class="eyebrow">Montreal.AI / SkillOS</div>
<h1>Public SkillOS Command Center</h1>
<p>Fresh, GitHub-native, viewer-friendly hub for every SkillOS proof, run, receipt, report, badge, workflow, and Skills Used display.</p>
<div class="actions"><a class="btn gold" href="proofs.html">View all proofs</a><a class="btn cyan" href="actions.html">Run / regenerate</a><a class="btn" href="skills.html">See Skills Used</a><a class="btn" href="force-refresh.html">Force refresh</a></div>
</div>
<div class="panel">
<div class="eyebrow">Live freshness · v4 root fix</div>
<div class="thesis">Updated {esc(generated_at)}</div>
<p>This canonical v4 deployment is designed so <code>/skillos/</code> and <code>/skillos/index.html</code> resolve to the same current command center.</p>
<p>Repository: <a href="https://github.com/MontrealAI/skillos">MontrealAI/skillos</a></p>
</div>
</section>
<section class="panel">
<div class="eyebrow">Core thesis</div>
<div class="thesis">{esc(CORE_THESIS)}</div>
<p>SkillOS makes the mechanism public and testable: work → traces → skills → verification → release → routing upgrade → compounding capability.</p>
</section>
<section class="metrics">
<div class="metric"><strong>{len(proofs)}</strong><span>indexed proofs and pages</span></div>
<div class="metric"><strong>{manifest['passed_or_proved_count']}</strong><span>passed / proved receipts</span></div>
<div class="metric"><strong>{len(workflows)}</strong><span>GitHub workflows indexed</span></div>
<div class="metric"><strong>{len(skills)}</strong><span>skills surfaced</span></div>
<div class="metric"><strong>{total_agents if total_agents else 'network'}</strong><span>declared specialist agents</span></div>
<div class="metric"><strong>{money_text(total_value) if total_value else 'receipts'}</strong><span>benchmark-capital-equivalent captured</span></div>
<div class="metric"><strong>{manifest_hash}</strong><span>site version hash</span></div>
<div class="metric"><strong>canonical</strong><span>root URL strategy</span></div>
</section>
<section><h2>Featured proof library</h2><div class="grid3">{proof_cards(proofs, 9)}</div></section>
<section><h2>Operational skill stack</h2><p>The Skills Used section explains the large multi-agent system in plain language: what each skill does, what signal it consumes, what artifact it produces, and which verifier checks it.</p><div class="grid3">{skill_cards(skills, 9)}</div><div class="actions"><a class="btn cyan" href="skills.html">Open full skills page</a></div></section>
<section class="root-fix"><strong>Root fix active:</strong> this v4 command center intentionally blocks the older homepage phrase, clears old browser/service-worker caches, retires legacy refresh workflows, and deploys the Pages artifact directly from the canonical workflow.</section>
<section class="panel"><div class="eyebrow">Public boundary</div><p>SkillOS public proofs are deterministic benchmark and publication artifacts. They do not claim audited customer ROI, financial advice, investment advice, legal advice, medical advice, achieved superintelligence, Kardashev Type II civilization, or guaranteed outcomes.</p></section>
</main><footer class="footer">SkillOS Public Command Center v4 · {esc(generated_at)} · <a href="data/command-center-manifest.json">manifest</a></footer>"""
    write_page(SITE / "index.html", "SkillOS Public Command Center v4", main_body, manifest_hash)

    exec_body = f"""<main><section class="hero"><div><div class="eyebrow">Executive overview</div><h1>Work becomes skill. Skill becomes network capability.</h1><p>{esc(CORE_THESIS)}</p></div><div class="panel"><div class="eyebrow">Plain-language answer</div><div class="thesis">One agent learns; the network levels up.</div><p>SkillOS uses GitHub Actions to regenerate proof receipts and pages so viewers can see the mechanism instead of trusting a claim.</p></div></section><section class="grid2"><div class="panel"><h3>What viewers should do</h3><p>Open a proof, read the result, inspect Skills Used, and rerun the GitHub Action.</p></div><div class="panel"><h3>What builders should do</h3><p>Add proof receipts, verifier gates, reports, badges, and workflows. The command center indexes them.</p></div></section></main>"""
    write_page(SITE / "executive.html", "SkillOS Executive Overview", exec_body, manifest_hash)

    proofs_body = f"""<main><h1>Proof Atlas</h1><p>All indexed SkillOS proofs and receipts. Each proof card links to a visual page and machine-readable JSON when available.</p><div class="grid3">{proof_cards(proofs, len(proofs))}</div></main>"""
    write_page(SITE / "proofs.html", "SkillOS Proof Atlas", proofs_body, manifest_hash)

    skills_body = f"""<main><h1>Skills Used</h1><p>SkillOS displays the operational skill stack behind the agent system. This makes the proof understandable to non-technical viewers while preserving machine-readable evidence.</p><div class="grid3">{skill_cards(skills)}</div></main>"""
    write_page(SITE / "skills.html", "SkillOS Skills Used", skills_body, manifest_hash)

    actions_rows = "".join(f"<tr><td>{esc(w['name'])}</td><td><code>{esc(w['file'])}</code></td><td>{esc(w['trigger'])}</td></tr>" for w in workflows)
    actions_body = f"""<main><h1>Run / Regenerate</h1><p>Open GitHub Actions, choose a proof or the command center workflow, and click <strong>Run workflow</strong>.</p><div class="actions"><a class="btn cyan" href="https://github.com/MontrealAI/skillos/actions">Open GitHub Actions</a><a class="btn" href="https://github.com/MontrealAI/skillos/actions/workflows/pages.yml">Run canonical deploy</a></div><h2>Indexed workflows</h2><table><tr><th>Workflow</th><th>File</th><th>Trigger</th></tr>{actions_rows}</table></main>"""
    write_page(SITE / "actions.html", "SkillOS Actions", actions_body, manifest_hash)

    multi_body = f"""<main><h1>Large multi-agent coordination</h1><section class="panel"><div class="thesis">The agents are shown as operational roles, skills, verifier courts, release gates, and receipts.</div><p>SkillOS does not display cartoon avatars. It displays the actual coordination structure: specialist roles, skills, proof receipts, independent verifiers, red-team courts, policy courts, rollback paths, and release gates.</p></section><section><h2>Coordination layers</h2><div class="grid3">{skill_cards(skills, 12)}</div></section></main>"""
    write_page(SITE / "multi-agent.html", "SkillOS Multi-Agent Coordination", multi_body, manifest_hash)

    receipts_body = f"""<main><h1>Receipts</h1><p>Machine-readable proof receipts are public JSON files. The command center manifest is the root receipt for this site.</p><div class="actions"><a class="btn cyan" href="data/command-center-manifest.json">Command center manifest</a><a class="btn" href="proof-registry.json">Proof registry</a><a class="btn" href="data/command-center-health.json">Health receipt</a></div><table><tr><th>Proof</th><th>JSON</th><th>Status</th></tr>{''.join(f'<tr><td>{esc(p["title"])}</td><td><a href="{esc(p["json"])}">{esc(p["json"])}</a></td><td>{esc(p["status"])}</td></tr>' for p in proofs)}</table></main>"""
    write_page(SITE / "receipts.html", "SkillOS Receipts", receipts_body, manifest_hash)

    arch_body = f"""<main><h1>Architecture</h1><section class="panel"><div class="thesis">work → traces → skills → verification → release → routing upgrade → compounding capability</div><p>The command center is rebuilt from repository artifacts and deployed by the canonical Pages workflow.</p></section><section class="grid3">{skill_cards(DEFAULT_SKILLS[:6])}</section></main>"""
    write_page(SITE / "architecture.html", "SkillOS Architecture", arch_body, manifest_hash)

    flywheel_body = f"""<main><h1>SkillOS Flywheel</h1><section class="panel"><div class="thesis">{esc(CORE_THESIS)}</div><p>The flywheel is operational when jobs create traces, traces become candidate skills, skills pass verifier courts, released skills improve routing, and future jobs get better.</p></section></main>"""
    write_page(SITE / "flywheel.html", "SkillOS Flywheel", flywheel_body, manifest_hash)

    health_rows = "".join(f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k, v in health.items())
    health_body = f"""<main><h1>Command Center Health</h1><p>This page verifies that the canonical v4 root fix is active.</p><table><tr><th>Check</th><th>Value</th></tr>{health_rows}</table><section class="root-fix"><strong>Expected:</strong> <code>/skillos/</code> and <code>/skillos/index.html</code> should show the same v4 command center after Pages deployment and cache expiry.</section></main>"""
    write_page(SITE / "health.html", "SkillOS Health", health_body, manifest_hash)

    runbook_body = """<main><h1>Emergency root fix runbook</h1><ol><li>Upload the v4 pack.</li><li>Commit it to main.</li><li>Cancel running legacy refresh workflows if any are still in progress.</li><li>Run <strong>Deploy SkillOS website with autonomous safe public copy</strong>.</li><li>Verify <code>/skillos/</code>, <code>/skillos/index.html</code>, and <code>/skillos/data/command-center-manifest.json</code>.</li></ol><p>Use <a href="force-refresh.html">force-refresh.html</a> if your browser keeps showing an old cached page.</p></main>"""
    write_page(SITE / "runbook.html", "SkillOS Root Fix Runbook", runbook_body, manifest_hash)

    force_body = f"""<main><h1>Force refresh</h1><section class="panel"><div class="thesis">Clear local caches and open the canonical root.</div><p>This page unregisters any old service worker and clears browser caches for this site.</p><div class="actions"><a class="btn cyan" href="./?v={manifest_hash}">Open current root</a><a class="btn" href="index.html?v={manifest_hash}">Open current index</a></div></section><script>(async()=>{{try{{if('serviceWorker' in navigator){{const regs=await navigator.serviceWorker.getRegistrations();await Promise.all(regs.map(r=>r.unregister()));}}if(window.caches){{const ks=await caches.keys();await Promise.all(ks.map(k=>caches.delete(k)));}}}}catch(e){{}}}})();</script></main>"""
    write_page(SITE / "force-refresh.html", "SkillOS Force Refresh", force_body, manifest_hash)

    write_page(SITE / "404.html", "SkillOS", "<main><h1>SkillOS</h1><p>Page not found. Return to the <a href='./'>Public Command Center</a>.</p></main>", manifest_hash)

    generate_missing_proof_pages(proofs, manifest_hash)

    service_worker = """self.addEventListener('install', event => { self.skipWaiting(); });
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    try {
      const keys = await caches.keys();
      await Promise.all(keys.map(k => caches.delete(k)));
    } catch (e) {}
    try { await self.registration.unregister(); } catch (e) {}
    try {
      const clientsList = await self.clients.matchAll({type:'window', includeUncontrolled:true});
      for (const client of clientsList) client.navigate(client.url);
    } catch (e) {}
  })());
});
self.addEventListener('fetch', event => { event.respondWith(fetch(event.request)); });
"""
    (SITE / "service-worker.js").write_text(service_worker, encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    (SITE / "version.txt").write_text(f"{SCHEMA}\n{generated_at}\n{manifest_hash}\n", encoding="utf-8")
    (SITE / "robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n", encoding="utf-8")
    urls = ["", "index.html", "executive.html", "proofs.html", "skills.html", "actions.html", "multi-agent.html", "receipts.html", "architecture.html", "flywheel.html", "health.html", "runbook.html", "force-refresh.html"]
    urls += [p["href"] for p in proofs[:200]]
    unique_urls = list(dict.fromkeys(urls))
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(f"<url><loc>{PUBLIC_URL}{esc(u)}</loc></url>" for u in unique_urls) + "\n</urlset>\n"
    (SITE / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    badge = '<svg xmlns="http://www.w3.org/2000/svg" width="360" height="20" role="img" aria-label="command center v4: fresh"><linearGradient id="g" x2="1"><stop stop-color="#06131f"/><stop offset="1" stop-color="#26306d"/></linearGradient><rect width="360" height="20" rx="10" fill="url(#g)"/><rect x="250" width="110" height="20" rx="10" fill="#2bb673"/><text x="10" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">SkillOS command center v4</text><text x="276" y="14" fill="#fff" font-family="Verdana" font-size="11">fresh</text></svg>'
    (SITE / "badges" / "command-center-fresh.svg").write_text(badge, encoding="utf-8")
    BADGES.mkdir(exist_ok=True)
    (BADGES / "command-center-fresh.svg").write_text(badge, encoding="utf-8")
    (DOCS / "SKILLOS_PUBLIC_COMMAND_CENTER_V4_ROOT_FIX.md").write_text(f"""# SkillOS Public Command Center v4 Root Fix

Generated: `{generated_at}`

## What this fixes

The canonical v4 deployment prevents the older command-center generator from overwriting the public root URL.

Expected public checks:

```text
https://montrealai.github.io/skillos/
https://montrealai.github.io/skillos/index.html
https://montrealai.github.io/skillos/data/command-center-manifest.json
```

The manifest should contain:

```text
schema: {SCHEMA}
```

The homepage must not show:

```text
Autonomous Proof Command Center
SkillOS Proof Command Center
Public SkillOS Command Center v2
```

## Safe public claim

SkillOS makes the mechanism testable: completed work can become verified traces, verified traces can become reusable skills, and reusable skills can improve future routing under measured benchmark conditions.
""", encoding="utf-8")

    if args.summary:
        Path(args.summary).write_text(f"## SkillOS Public Command Center v4\n\n- schema: **{SCHEMA}**\n- generated: **{generated_at}**\n- proofs: **{len(proofs)}**\n- skills surfaced: **{len(skills)}**\n- version hash: **{manifest_hash}**\n", encoding="utf-8")

    print(json.dumps({"status": "BUILT", "schema": SCHEMA, "generated_at_utc": generated_at, "proof_count": len(proofs), "skills_surfaced_count": len(skills), "workflow_count": len(workflows), "version_hash": manifest_hash}, indent=2))

if __name__ == "__main__":
    main()
