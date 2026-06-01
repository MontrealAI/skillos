#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import math
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
DOCS = ROOT / "docs"
BADGES = ROOT / "badges"
WORKFLOWS = ROOT / ".github" / "workflows"

SCHEMA = "skillos.command_center.sovereign.v5"
MARKER = "SKILLOS_COMMAND_CENTER_V5_CANONICAL_ROOT"
OLD_PHRASES = [
    "Autonomous Proof Command Center",
    "SkillOS Public Command Center v2",
    "SkillOS Public Command Center v3",
    "Public SkillOS Command Center v2",
]

def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def safe_slug(text: str) -> str:
    out = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return out or "proof"

def money(v: Any) -> str:
    try:
        v = float(v)
    except Exception:
        return "—"
    if abs(v) >= 1e12:
        return f"${v/1e12:,.2f}T"
    if abs(v) >= 1e9:
        return f"${v/1e9:,.2f}B"
    if abs(v) >= 1e6:
        return f"${v/1e6:,.2f}M"
    return f"${v:,.0f}"

def pct(v: Any) -> str:
    try:
        return f"{float(v):,.2f}%"
    except Exception:
        return "—"

def esc(x: Any) -> str:
    return html.escape("" if x is None else str(x), quote=True)

def normalize_proof(path: Path, raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    title = raw.get("proof_type") or raw.get("workflow") or raw.get("title") or raw.get("name")
    proof_id = raw.get("id") or raw.get("proof_id") or safe_slug(title or path.stem)
    final = raw.get("final") if isinstance(raw.get("final"), dict) else {}
    agent_system = raw.get("agent_system") if isinstance(raw.get("agent_system"), dict) else {}
    benchmark = raw.get("benchmark_public") if isinstance(raw.get("benchmark_public"), dict) else {}
    status = raw.get("status") or ("PASSED" if raw.get("proved") else "UNKNOWN")
    proved = bool(raw.get("proved") or str(status).upper().startswith("PASSED"))
    skills = raw.get("skills_used") if isinstance(raw.get("skills_used"), list) else []
    href = raw.get("href") or f"{proof_id}.html"
    json_href = f"data/{path.name}"
    value_capture = (
        final.get("value_capture_rate_percent")
        or final.get("benchmark_value_capture_rate_percent")
        or raw.get("value_capture_rate_percent")
        or raw.get("benchmark_value_capture_rate_percent")
    )
    agents = (
        agent_system.get("virtual_specialist_agents")
        or agent_system.get("agents")
        or raw.get("virtual_specialist_agents")
        or raw.get("agents")
        or final.get("virtual_specialist_agents")
    )
    roles = (
        agent_system.get("specialist_roles")
        or agent_system.get("roles")
        or raw.get("specialist_roles")
        or raw.get("roles")
    )
    releases = raw.get("rsi_release_count") or len([r for r in raw.get("rsi_releases", []) if isinstance(r, dict) and r.get("released")])
    holdout = benchmark.get("locked_holdout_count") or benchmark.get("holdout_count") or raw.get("locked_holdout_count") or final.get("locked_holdout_count")
    value_captured = (
        final.get("total_benchmark_value_captured_usd")
        or final.get("benchmark_value_captured_usd")
        or raw.get("benchmark_value_captured_usd")
        or raw.get("total_benchmark_value_captured_usd")
    )
    generated = raw.get("generated_at_utc") or raw.get("updated_at_utc") or raw.get("timestamp") or ""
    desc = (
        raw.get("description")
        or raw.get("safe_interpretation")
        or raw.get("summary")
        or "Autonomous SkillOS public proof with deterministic receipt, verification gates, and visual evidence."
    )
    return {
        "id": proof_id,
        "title": str(title or proof_id.replace("-", " ").title()),
        "status": str(status),
        "proved": proved,
        "href": href,
        "json": json_href,
        "doc": f"docs/{proof_id}.md",
        "badge": f"badges/{proof_id}.svg",
        "source_json": str(path.relative_to(ROOT)),
        "generated_at_utc": generated,
        "value_capture_rate_percent": value_capture,
        "benchmark_value_captured_usd": value_captured,
        "virtual_specialist_agents": agents,
        "specialist_roles": roles,
        "rsi_release_count": releases,
        "holdout_count": holdout,
        "skills_used_count": len(skills),
        "description": str(desc)[:500],
        "skills_used": skills,
        "raw": raw,
    }

def collect_proofs() -> list[dict[str, Any]]:
    seen: set[str] = set()
    proofs: list[dict[str, Any]] = []
    for folder in [DATA, SITE / "data"]:
        if not folder.exists():
            continue
        for path in sorted(folder.glob("*.json")):
            if path.name.startswith("command-center"):
                continue
            raw = read_json(path)
            if isinstance(raw, dict) and isinstance(raw.get("proofs"), list):
                continue
            proof = normalize_proof(path, raw)
            if proof and proof["id"] not in seen:
                proofs.append(proof)
                seen.add(proof["id"])
    for registry_path in [SITE / "proof-registry.json"]:
        raw = read_json(registry_path)
        entries = raw.get("proofs", []) if isinstance(raw, dict) else raw if isinstance(raw, list) else []
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            pid = entry.get("id") or safe_slug(entry.get("title", "proof"))
            if pid in seen:
                continue
            proofs.append({
                "id": pid,
                "title": entry.get("title") or pid.replace("-", " ").title(),
                "status": entry.get("status", "INDEXED"),
                "proved": bool(entry.get("proved")),
                "href": entry.get("href") or f"{pid}.html",
                "json": entry.get("json") or "",
                "doc": entry.get("doc") or "",
                "badge": entry.get("badge") or "",
                "source_json": str(registry_path.relative_to(ROOT)),
                "generated_at_utc": entry.get("generated_at_utc", ""),
                "value_capture_rate_percent": entry.get("value_capture_rate_percent"),
                "benchmark_value_captured_usd": entry.get("benchmark_value_captured_usd"),
                "virtual_specialist_agents": entry.get("virtual_specialist_agents"),
                "specialist_roles": entry.get("specialist_roles"),
                "rsi_release_count": entry.get("rsi_release_count"),
                "holdout_count": entry.get("holdout_count"),
                "skills_used_count": entry.get("skills_used_count", 0),
                "description": entry.get("description", "Indexed public proof."),
                "skills_used": [],
                "raw": entry,
            })
            seen.add(pid)
    proofs.sort(key=lambda p: (not p["proved"], -(float(p["value_capture_rate_percent"] or 0)), p["title"].lower()))
    return proofs

def collect_workflows() -> list[dict[str, Any]]:
    rows = []
    if not WORKFLOWS.exists():
        return rows
    for path in sorted(list(WORKFLOWS.glob("*.yml")) + list(WORKFLOWS.glob("*.yaml"))):
        txt = path.read_text(encoding="utf-8", errors="ignore")
        m = re.findall(r"(?m)^name:\s*(.+)$", txt)
        name = m[0] if m else path.stem.replace("-", " ").title()
        retired = "Retired legacy SkillOS site refresh" in txt or "v5 canonical deploy is the single publisher" in txt
        rows.append({
            "name": name.strip().strip('"\''),
            "path": str(path.relative_to(ROOT)),
            "retired": retired,
            "dispatch": "workflow_dispatch" in txt,
            "schedule": "schedule:" in txt,
            "push": re.search(r"(?m)^\s*push\s*:", txt) is not None or "\n  push:" in txt,
            "workflow_run": "workflow_run:" in txt,
        })
    return rows

def aggregate_skills(proofs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for proof in proofs:
        for skill in proof.get("skills_used", []):
            if not isinstance(skill, dict):
                continue
            name = str(skill.get("name") or "").strip()
            if not name:
                continue
            rec = index.setdefault(name, {
                "name": name,
                "layer": skill.get("layer") or "Skill",
                "purpose": skill.get("purpose") or "",
                "input_signal": skill.get("input_signal") or skill.get("input") or "",
                "output": skill.get("output") or skill.get("output_artifact") or "",
                "verifier": skill.get("verifier") or "",
                "proofs": set(),
            })
            rec["proofs"].add(proof["id"])
            for key in ["purpose", "input_signal", "output", "verifier"]:
                if not rec.get(key) and skill.get(key):
                    rec[key] = skill.get(key)
    if not index:
        fallback = [
            ("Trace Capture", "Work", "Captures completed jobs as reusable evidence traces."),
            ("Skill Distillation", "Learning", "Turns repeatable execution traces into candidate skills."),
            ("Verifier Court", "Verification", "Checks whether candidate skills improve outcomes without breaking boundaries."),
            ("Policy Gate", "Governance", "Applies safe claim, permission, and publication boundaries."),
            ("Risk Veto", "Safety", "Blocks releases that regress risk, reliability, or policy gates."),
            ("Release Signing", "RSI", "Publishes only validation-gated upgrades."),
            ("Routing Upgrade", "Coordination", "Routes future work through verified skill improvements."),
            ("Command Center Publishing", "Communication", "Regenerates public pages, receipts, badges, and runbooks."),
        ]
        for name, layer, purpose in fallback:
            index[name] = {"name": name, "layer": layer, "purpose": purpose, "input_signal": "proof receipt", "output": "public skill card", "verifier": "site verifier", "proofs": set()}
    skills = []
    for rec in index.values():
        rec = dict(rec)
        rec["proof_count"] = len(rec.pop("proofs"))
        skills.append(rec)
    skills.sort(key=lambda s: (-s["proof_count"], s["layer"], s["name"]))
    return skills

CSS = r'''
:root{
  --ink:#f8fbff; --muted:#bdcce0; --dim:#7d8ca1; --cyan:#7df8ff; --mint:#7dffb1;
  --gold:#ffd86f; --rose:#ff8cb2; --panel:rgba(255,255,255,.085); --panel2:rgba(255,255,255,.13);
  --line:rgba(255,255,255,.18); --night:#07101f; --royal:#1d2558; --deep:#0b1c35;
}
*{box-sizing:border-box} html{scroll-behavior:smooth} body{margin:0;font-family:Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:linear-gradient(135deg,#07101f 0%,#0d3041 38%,#232b5d 74%,#090d1a 100%);color:var(--ink);overflow-x:hidden}
body:before{content:"";position:fixed;inset:0;background:radial-gradient(circle at 15% 5%,rgba(125,248,255,.22),transparent 30%),radial-gradient(circle at 85% 0%,rgba(255,216,111,.15),transparent 25%),radial-gradient(circle at 70% 75%,rgba(125,255,177,.12),transparent 35%),linear-gradient(rgba(255,255,255,.028) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.028) 1px,transparent 1px);background-size:auto,auto,auto,44px 44px,44px 44px;pointer-events:none;z-index:-3}
body:after{content:"";position:fixed;inset:0;background:radial-gradient(ellipse at center,transparent 20%,rgba(0,0,0,.26) 100%);pointer-events:none;z-index:-2}
a{color:var(--cyan);text-decoration:none} a:hover{text-decoration:underline}.topbar{position:sticky;top:0;z-index:20;background:rgba(5,13,25,.83);backdrop-filter:blur(22px);border-bottom:1px solid rgba(255,255,255,.12);display:flex;justify-content:space-between;gap:18px;align-items:center;padding:13px 24px}.brand{font-weight:1000;letter-spacing:-.03em;color:var(--cyan);text-shadow:0 0 20px rgba(125,248,255,.5)}.nav{display:flex;gap:16px;flex-wrap:wrap}.nav a{font-weight:850;color:#d9e5f2;font-size:14px}.wrap{max-width:1320px;margin:0 auto;padding:54px 22px 96px;position:relative}.hero{display:grid;grid-template-columns:1.05fr .95fr;gap:28px;align-items:center;min-height:620px}.kicker{color:var(--cyan);text-transform:uppercase;letter-spacing:.22em;font-weight:1000;font-size:12px}.title{font-size:clamp(58px,8.8vw,132px);line-height:.78;letter-spacing:-.105em;margin:20px 0 22px;text-wrap:balance}.subtitle{max-width:770px;color:#d5e2ef;font-size:clamp(18px,2.05vw,27px);line-height:1.32}.glass{background:linear-gradient(145deg,rgba(255,255,255,.14),rgba(255,255,255,.06));border:1px solid var(--line);border-radius:34px;box-shadow:0 35px 110px rgba(0,0,0,.34), inset 0 1px 0 rgba(255,255,255,.14);backdrop-filter:blur(18px)}.card{padding:28px}.crown{position:relative;overflow:hidden}.crown:before{content:"";position:absolute;inset:-1px;background:linear-gradient(120deg,transparent,rgba(255,216,111,.28),transparent 55%,rgba(125,248,255,.20));opacity:.9;pointer-events:none}.hero-card{min-height:390px;display:flex;flex-direction:column;justify-content:space-between}.hero-card .giant,.giant{font-size:clamp(32px,4.2vw,62px);letter-spacing:-.06em;line-height:.94;font-weight:1000}.pillrow{display:flex;gap:12px;flex-wrap:wrap;margin-top:24px}.btn{display:inline-flex;align-items:center;gap:9px;border-radius:999px;padding:13px 18px;font-weight:1000;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.1);color:var(--ink)}.btn.primary{background:linear-gradient(90deg,var(--gold),#ffef9a);color:#07101f}.btn.cyan{background:linear-gradient(90deg,var(--cyan),#9bfff4);color:#07101f}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:28px 0}.stat{padding:22px;border-radius:25px;background:rgba(255,255,255,.08);border:1px solid var(--line)}.stat b{display:block;color:var(--mint);font-size:clamp(32px,3.4vw,48px);letter-spacing:-.06em;line-height:.9}.stat span{color:#c9d8e8}.section{margin:72px 0}.section h2{font-size:clamp(38px,5vw,78px);line-height:.84;letter-spacing:-.08em;margin:0 0 20px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.grid.two{grid-template-columns:repeat(2,1fr)}.proof-card,.skill-card,.workflow-card{padding:23px;border-radius:27px;background:rgba(255,255,255,.08);border:1px solid var(--line);min-height:220px}.badge{display:inline-block;border-radius:999px;padding:7px 10px;font-size:11px;font-weight:1000;letter-spacing:.12em;text-transform:uppercase;background:rgba(125,255,177,.18);color:var(--mint);border:1px solid rgba(125,255,177,.25)}.badge.warn{background:rgba(255,216,111,.14);color:var(--gold);border-color:rgba(255,216,111,.28)}.proof-card h3,.skill-card h3{font-size:24px;letter-spacing:-.04em;line-height:1.02;margin:14px 0 10px}.meta{display:flex;gap:10px;flex-wrap:wrap;color:#aebfd3;font-size:13px;margin-top:14px}.meta span{border:1px solid rgba(255,255,255,.12);background:rgba(0,0,0,.16);border-radius:999px;padding:6px 9px}.bar{display:grid;grid-template-columns:220px 1fr 95px;gap:14px;align-items:center;margin:12px 0;color:#c5d3e4}.bar i{height:18px;display:block;background:rgba(255,255,255,.09);border-radius:999px;overflow:hidden}.bar i:before{content:"";display:block;height:100%;width:var(--w);background:linear-gradient(90deg,var(--mint),var(--cyan),var(--gold));border-radius:999px}.table{width:100%;border-collapse:collapse;overflow:hidden;border-radius:24px;background:rgba(255,255,255,.07);border:1px solid var(--line)}.table th,.table td{padding:14px;border-bottom:1px solid rgba(255,255,255,.11);text-align:left;vertical-align:top}.table th{color:#aebfd3;font-size:12px;text-transform:uppercase;letter-spacing:.13em}.notice{border-left:4px solid var(--gold);background:rgba(255,216,111,.08);padding:18px 20px;border-radius:18px;color:#d8e4f0}.constellation{height:420px;position:relative;overflow:hidden}.node{position:absolute;border-radius:999px;background:radial-gradient(circle,#fff,var(--cyan) 28%,rgba(125,248,255,.2) 70%,transparent);box-shadow:0 0 28px rgba(125,248,255,.65)}.line{position:absolute;height:1px;background:linear-gradient(90deg,transparent,rgba(125,248,255,.55),transparent);transform-origin:left center}.timeline{display:grid;gap:14px}.step{display:grid;grid-template-columns:70px 1fr;gap:18px;align-items:start}.step b{width:54px;height:54px;border-radius:18px;display:grid;place-items:center;background:linear-gradient(135deg,var(--gold),var(--cyan));color:#07101f}.foot{color:#95a8bc;margin-top:80px;font-size:14px}.quote{font-size:clamp(28px,4vw,58px);line-height:.98;letter-spacing:-.06em;font-weight:1000}.gold{color:var(--gold)}.mint{color:var(--mint)}.cyan{color:var(--cyan)}code{background:rgba(0,0,0,.22);border:1px solid rgba(255,255,255,.1);border-radius:8px;padding:2px 5px}@media(max-width:900px){.hero,.grid,.grid.two,.stats{grid-template-columns:1fr}.title{font-size:64px}.bar{grid-template-columns:1fr}.topbar{align-items:flex-start;flex-direction:column}.nav{gap:10px}.constellation{height:280px}}
'''

JS = r'''
(function(){
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.getRegistrations().then(function(regs){ regs.forEach(function(r){ r.unregister(); }); }).catch(function(){});
  }
  if (window.caches && caches.keys) {
    caches.keys().then(function(keys){ keys.forEach(function(k){ caches.delete(k); }); }).catch(function(){});
  }
})();
'''

def base_head(title: str, desc: str) -> str:
    return f'''<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="pragma" content="no-cache"><meta http-equiv="expires" content="0">
<meta name="description" content="{esc(desc)}"><meta name="theme-color" content="#07101f">
<title>{esc(title)}</title>
<style>{CSS}</style><script>{JS}</script>
</head><body><!-- {MARKER} --><div class="topbar"><a class="brand" href="index.html">SkillOS Sovereign Command Center v5</a><div class="nav">
<a href="index.html">Home</a><a href="executive.html">Executive</a><a href="proofs.html">Proofs</a><a href="skills.html">Skills Used</a><a href="multi-agent.html">Multi-Agent</a><a href="receipts.html">Receipts</a><a href="health.html">Health</a><a href="runbook.html">Run</a><a href="https://github.com/MontrealAI/skillos">GitHub</a>
</div></div><main class="wrap">'''

def end() -> str:
    return f'''<div class="foot">Public boundary: deterministic public proof and publication system. Not audited customer ROI, financial advice, investment advice, legal advice, medical advice, policy advice, token advice, achieved superintelligence, Kardashev Type II achievement, or guarantees. <span class="cyan">{MARKER}</span></div></main></body></html>'''

def constellation() -> str:
    nodes = []
    coords = [(12,25,12),(24,42,7),(31,20,11),(42,36,16),(55,22,8),(64,45,18),(77,32,10),(83,60,14),(65,68,7),(48,62,11),(33,72,8),(20,61,13),(52,52,6),(72,18,6),(90,38,8),(8,55,7)]
    for x,y,s in coords:
        nodes.append(f'<span class="node" style="left:{x}%;top:{y}%;width:{s*2}px;height:{s*2}px"></span>')
    for i,(x1,y1,s1) in enumerate(coords[:-1]):
        x2,y2,_=coords[i+1]
        dx=x2-x1; dy=y2-y1; length=(dx*dx+dy*dy)**0.5
        angle=math.degrees(math.atan2(dy,dx))
        nodes.append(f'<span class="line" style="left:{x1}%;top:{y1}%;width:{length}%;transform:rotate({angle}deg)"></span>')
    return "".join(nodes)

def timeline() -> str:
    steps = [("01","Job produces trace"),("02","Trace becomes candidate skill"),("03","Verifier courts test improvement"),("04","Policy and risk gates veto regressions"),("05","Release upgrades routing"),("06","The network levels up")]
    return "".join(f'<div class="step"><b>{n}</b><p>{esc(t)}</p></div>' for n,t in steps)

def proof_card(p: dict[str, Any]) -> str:
    status = "PASSED" if p["proved"] else "INDEXED"
    badge_class = "" if p["proved"] else "warn"
    bits = []
    if p.get("virtual_specialist_agents"):
        try: bits.append(f"{int(float(p['virtual_specialist_agents'])):,} agents")
        except Exception: pass
    if p.get("specialist_roles"):
        try: bits.append(f"{int(float(p['specialist_roles'])):,} roles")
        except Exception: pass
    if p.get("rsi_release_count"): bits.append(f"{p['rsi_release_count']} RSI releases")
    if p.get("skills_used_count"): bits.append(f"{p['skills_used_count']} skills")
    if p.get("value_capture_rate_percent"): bits.append(pct(p["value_capture_rate_percent"]))
    href = p.get("href") or f"{p['id']}.html"
    return f'''<article class="proof-card glass">
<span class="badge {badge_class}">{esc(status)}</span>
<h3><a href="{esc(href)}">{esc(p["title"])}</a></h3>
<p>{esc(p.get("description",""))}</p>
<div class="meta">{''.join(f"<span>{esc(x)}</span>" for x in bits)}</div>
<div class="pillrow"><a class="btn cyan" href="{esc(href)}">Open proof</a>{f'<a class="btn" href="{esc(p["json"])}">JSON</a>' if p.get("json") else ''}</div>
</article>'''

def ensure_proof_pages(proofs: list[dict[str, Any]]) -> None:
    for p in proofs:
        href = p.get("href") or f"{p['id']}.html"
        out = SITE / href
        if out.exists() and MARKER in out.read_text(encoding="utf-8", errors="ignore"):
            continue
        skills = p.get("skills_used") or []
        skill_html = "".join(
            f'''<article class="skill-card"><span class="badge">{esc(s.get("layer","Skill"))}</span><h3>{esc(s.get("name","Skill"))}</h3><p>{esc(s.get("purpose",""))}</p><div class="meta"><span>Verifier: {esc(s.get("verifier","site verifier"))}</span></div></article>'''
            for s in skills if isinstance(s, dict)
        ) or '<p>No explicit Skills Used array found in this receipt yet. The Command Center still indexes the proof receipt and source files.</p>'
        raw = p.get("raw", {})
        final = raw.get("final", {}) if isinstance(raw, dict) else {}
        bars = ""
        for label, key in [("Value capture", "value_capture_rate_percent"), ("Minimum domain capture", "minimum_domain_value_capture_percent"), ("Policy violation", "policy_violation_rate_percent"), ("Risk breach", "risk_breach_rate_percent")]:
            v = final.get(key) or p.get(key)
            try:
                width = float(v)
            except Exception:
                width = 0
            bars += f'<div class="bar"><span>{esc(label)}</span><i style="--w:{max(0,min(100,width))}%"></i><b>{pct(v)}</b></div>'
        text = base_head(p["title"], p.get("description","SkillOS proof")) + f'''
<section class="hero" style="min-height:420px"><div><div class="kicker">MONTREAL.AI / SKILLOS / PROOF</div><h1 class="title">{esc(p["title"])}</h1><p class="subtitle">{esc(p.get("description",""))}</p><div class="pillrow"><a class="btn primary" href="index.html">Command Center</a>{f'<a class="btn cyan" href="{esc(p.get("json",""))}">Open JSON receipt</a>' if p.get("json") else ""}</div></div><div class="glass card crown"><div class="kicker">Proof receipt</div><div class="giant">{esc(p.get("status","INDEXED"))}</div><p>Generated: {esc(p.get("generated_at_utc") or "indexed from repository")}</p><div class="stats" style="grid-template-columns:repeat(2,1fr)"><div class="stat"><b>{esc(p.get("rsi_release_count") or "—")}</b><span>RSI releases</span></div><div class="stat"><b>{esc(p.get("skills_used_count") or "—")}</b><span>skills displayed</span></div></div></div></section>
<section class="section glass card"><h2>Measured signals</h2>{bars}</section>
<section class="section"><h2>Skills Used</h2><div class="grid">{skill_html}</div></section>
<section class="section notice">Boundary: this page is a public deterministic proof receipt presentation, not audited ROI, financial advice, investment advice, legal advice, medical advice, or proof of achieved superintelligence.</section>
''' + end()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")

def homepage(proofs, workflows, skills, ts):
    passed = sum(1 for p in proofs if p["proved"])
    total_agents = 0
    for p in proofs:
        try: total_agents += int(float(p.get("virtual_specialist_agents") or 0))
        except Exception: pass
    receipts = len(list(DATA.glob("*.json"))) if DATA.exists() else 0
    if (SITE/"data").exists():
        receipts += len(list((SITE/"data").glob("*.json")))
    badges = len(list(BADGES.glob("*.svg"))) if BADGES.exists() else 0
    if (SITE/"badges").exists():
        badges += len(list((SITE/"badges").glob("*.svg")))
    featured = "".join(proof_card(p) for p in proofs[:6])
    top_workflows = "".join(f'''<article class="workflow-card"><span class="badge {'warn' if w['retired'] else ''}">{'retired' if w['retired'] else 'active'}</span><h3>{esc(w['name'])}</h3><p>{esc(w['path'])}</p><div class="meta"><span>dispatch {w['dispatch']}</span><span>push {w['push']}</span><span>schedule {w['schedule']}</span></div></article>''' for w in workflows[:6])
    return base_head("SkillOS Sovereign Command Center v5", "Canonical public SkillOS proof hub") + f'''
<section class="hero"><div><div class="kicker">MONTREAL.AI / SKILLOS</div><h1 class="title">Sovereign SkillOS Command Center.</h1><p class="subtitle">The canonical, self-deploying public proof atlas for SkillOS: every proof, receipt, workflow, badge, Skills Used display, and multi-agent coordination signal is indexed, verified, rendered, and published through one autonomous GitHub Action.</p><div class="pillrow"><a class="btn primary" href="proofs.html">View proof atlas</a><a class="btn cyan" href="runbook.html">Run / regenerate</a><a class="btn" href="skills.html">Inspect Skills Used</a></div></div><div class="hero-card glass card crown"><div><div class="kicker">Canonical live root</div><div class="giant">Root and index are one artifact.</div></div><p>Updated <b class="mint">{esc(ts)}</b>. This v5 publisher blocks legacy overwrite loops and deploys the exact generated <code>site/index.html</code> artifact to GitHub Pages.</p><div class="notice">The old homepage phrase is intentionally forbidden by verification.</div></div></section>
<section class="glass card"><div class="kicker">Core thesis</div><div class="quote">Every job can become a reusable skill. Every verified skill can strengthen the whole network. One agent learns; the system can route that learning everywhere.</div><p>SkillOS makes the mechanism public and testable: work → traces → skills → verification → release → routing upgrade → compounding capability.</p></section>
<section class="stats"><div class="stat"><b>{len(proofs):,}</b><span>indexed proofs and pages</span></div><div class="stat"><b>{passed:,}</b><span>passed / proved receipts</span></div><div class="stat"><b>{len(workflows):,}</b><span>GitHub workflows scanned</span></div><div class="stat"><b>{len(skills):,}</b><span>Skills Used surfaced</span></div><div class="stat"><b>{total_agents/1e9:,.2f}B</b><span>declared specialist agents across receipts</span></div><div class="stat"><b>{receipts:,}</b><span>JSON receipt files</span></div><div class="stat"><b>{len(list(DOCS.glob("*.md"))) if DOCS.exists() else 0:,}</b><span>Markdown reports</span></div><div class="stat"><b>{badges:,}</b><span>badges</span></div></section>
<section class="section"><h2>Featured proof atlas</h2><div class="grid">{featured or '<p>No proof receipts found yet. Run the Action to scan the repository.</p>'}</div><div class="pillrow"><a class="btn cyan" href="proofs.html">Open all proofs</a></div></section>
<section class="section glass card"><h2>Large multi-agent coordination</h2><div class="grid two"><div class="constellation">{constellation()}</div><div><p class="subtitle">The agents are represented as operational roles, verifier courts, skills, release gates, routing upgrades, and public receipts — not avatars. The command center exposes how the system coordinates to maximum effect.</p><div class="timeline">{timeline()}</div></div></div></section>
<section class="section"><h2>Autonomous workflows</h2><div class="grid">{top_workflows}</div></section>
''' + end()

def proofs_page(proofs, ts):
    rows = "".join(proof_card(p) for p in proofs)
    return base_head("SkillOS Proof Atlas", "All indexed SkillOS proof pages") + f'''
<section class="section"><div class="kicker">Proof atlas</div><h1 class="title">Every proof, indexed.</h1><p class="subtitle">Generated at {esc(ts)} from JSON receipts, reports, badges, and site pages. Each card opens a proof page; each receipt remains machine-readable.</p></section>
<section class="grid">{rows or '<p>No proofs found yet.</p>'}</section>
''' + end()

def skills_page(skills, ts):
    grouped = {}
    for s in skills:
        grouped.setdefault(s.get("layer") or "Skill", []).append(s)
    sections = []
    for layer in sorted(grouped):
        cards = "".join(f'''<article class="skill-card glass"><span class="badge">{esc(layer)}</span><h3>{esc(s["name"])}</h3><p>{esc(s.get("purpose",""))}</p><div class="meta"><span>Input: {esc(s.get("input_signal","proof receipt"))}</span><span>Output: {esc(s.get("output","skill card"))}</span><span>Verifier: {esc(s.get("verifier","site verifier"))}</span><span>{s.get("proof_count",0)} proofs</span></div></article>''' for s in grouped[layer])
        sections.append(f'<section class="section"><div class="kicker">{esc(layer)}</div><div class="grid">{cards}</div></section>')
    return base_head("SkillOS Skills Used", "Operational skill stack") + f'''
<section class="hero" style="min-height:460px"><div><div class="kicker">Operational skill stack</div><h1 class="title">Skills Used, beautifully exposed.</h1><p class="subtitle">The agent system becomes understandable through skills: what each operational skill does, what signal it consumes, what artifact it emits, and which verifier checks it.</p></div><div class="glass card crown"><div class="giant">{len(skills):,} skills surfaced.</div><p>Updated {esc(ts)}. Generated directly from proof receipts when available, with a fallback operating stack when receipts are incomplete.</p></div></section>{''.join(sections)}
''' + end()

def actions_page(workflows, ts):
    rows = "".join(f'<tr><td>{esc(w["name"])}</td><td><code>{esc(w["path"])}</code></td><td>{"retired" if w["retired"] else "active"}</td><td>{w["dispatch"]}</td><td>{w["push"]}</td><td>{w["schedule"]}</td><td>{w["workflow_run"]}</td></tr>' for w in workflows)
    return base_head("SkillOS Actions", "Workflows and run instructions") + f'''
<section class="section"><div class="kicker">Run / regenerate</div><h1 class="title">One canonical deploy path.</h1><p class="subtitle">Run <b>SkillOS Sovereign Command Center v5 Canonical Deploy</b>. It builds, verifies, commits, uploads the Pages artifact, deploys, and verifies the live root.</p><div class="pillrow"><a class="btn primary" href="https://github.com/MontrealAI/skillos/actions">Open GitHub Actions</a></div></section>
<table class="table"><tr><th>Workflow</th><th>Path</th><th>Status</th><th>Dispatch</th><th>Push</th><th>Schedule</th><th>Workflow run</th></tr>{rows}</table>
''' + end()

def receipts_page(proofs, ts):
    rows = "".join(f'<tr><td>{esc(p["title"])}</td><td><a href="{esc(p.get("json",""))}">{esc(p.get("json",""))}</a></td><td>{esc(p.get("source_json",""))}</td><td>{esc(p.get("generated_at_utc",""))}</td></tr>' for p in proofs)
    return base_head("SkillOS Receipts", "Machine-readable proof receipts") + f'''
<section class="section"><div class="kicker">Receipts</div><h1 class="title">Machine-readable evidence.</h1><p class="subtitle">Every proof should have a JSON receipt, a Markdown report, a badge, and a public page. This page indexes the available receipts.</p></section>
<table class="table"><tr><th>Proof</th><th>Public JSON</th><th>Source</th><th>Generated</th></tr>{rows}</table>
''' + end()

def simple_page(title, subtitle, body):
    return base_head(title, subtitle) + f'<section class="section"><div class="kicker">SkillOS</div><h1 class="title">{esc(title)}</h1><p class="subtitle">{esc(subtitle)}</p></section>{body}' + end()

def manifest(proofs, workflows, skills, ts):
    h = hashlib.sha256(json.dumps({
        "proofs":[{k:p.get(k) for k in ["id","title","status","href","json","generated_at_utc"]} for p in proofs],
        "workflows":workflows,
        "skills":[s["name"] for s in skills],
        "ts":ts,
    }, sort_keys=True).encode()).hexdigest()
    return {
        "schema": SCHEMA,
        "marker": MARKER,
        "generated_at_utc": ts,
        "repository": "MontrealAI/skillos",
        "canonical_root": "index.html",
        "old_phrases_forbidden": OLD_PHRASES,
        "proof_count": len(proofs),
        "proved_count": sum(1 for p in proofs if p["proved"]),
        "workflow_count": len(workflows),
        "skills_used_count": len(skills),
        "site_fingerprint_sha256": h,
        "root_fix": {
            "deploys_pages_artifact": True,
            "retires_legacy_refresh_workflows": True,
            "verifies_root_and_index": True,
            "no_cache_meta_tags": True,
            "service_worker_kill_switch": True,
        },
    }

def write_pages(proofs, workflows, skills, ts):
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE/"data").mkdir(exist_ok=True)
    (SITE/"badges").mkdir(exist_ok=True)
    (SITE/"docs").mkdir(exist_ok=True)
    ensure_proof_pages(proofs)
    pages = {
        "index.html": homepage(proofs, workflows, skills, ts),
        "proofs.html": proofs_page(proofs, ts),
        "skills.html": skills_page(skills, ts),
        "actions.html": actions_page(workflows, ts),
        "receipts.html": receipts_page(proofs, ts),
        "executive.html": simple_page("Executive Briefing", "SkillOS turns work into compounding capability through verified skills, public receipts, and autonomous proof publication.", '<section class="glass card"><div class="quote">One agent learns. The network levels up.</div><p>SkillOS is the public proof layer for reusable skill compounding. It is intentionally bounded: powerful, beautiful, reproducible, and safe to inspect.</p></section>'),
        "multi-agent.html": simple_page("Large Multi-Agent Coordination", "Specialist roles, verifier courts, policy gates, routing upgrades, and release lanes coordinate as one proof-producing organization.", f'<section class="glass card constellation">{constellation()}</section><section class="section"><div class="timeline">{timeline()}</div></section>'),
        "architecture.html": simple_page("Architecture", "The public operating model for the SkillOS compounding flywheel.", '<section class="glass card"><div class="quote">work → trace → skill → verification → release → routing upgrade → compounding capability</div></section>'),
        "flywheel.html": simple_page("The SkillOS Flywheel", "Every verified job can become a reusable skill; every reusable skill can improve future routing.", '<section class="grid">' + "".join(f'<article class="skill-card"><span class="badge">{i}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></article>' for i,(t,d) in enumerate([("Work","A job completes and leaves a trace."),("Trace","The trace becomes evidence."),("Skill","Reusable capability is distilled."),("Verify","Courts test improvement."),("Release","Safe upgrades ship."),("Route","Future jobs use better skills.")],1)) + '</section>'),
        "health.html": simple_page("Command Center Health", "Freshness, root canonicalization, proof registry integrity, and live deployment checks.", '<section class="glass card"><h2>Health contract</h2><p>The verifier blocks old homepage phrases, requires the v5 marker, validates all core pages, checks proof registry JSON, and can verify live / and /index.html after deployment.</p><p><a class="btn cyan" href="data/command-center-health.json">Open health JSON</a></p></section>'),
        "runbook.html": simple_page("Run or Regenerate", "A non-technical runbook for refreshing the public command center.", '<section class="glass card"><h2>Run this Action</h2><p>GitHub → Actions → <b>SkillOS Sovereign Command Center v5 Canonical Deploy</b> → Run workflow.</p><p>Use: publish_to_repo=true, deploy_pages=true, verify_live=true.</p></section>'),
        "force-refresh.html": simple_page("Force Refresh", "Clears local browser caches and points viewers back to the canonical root.", '<section class="glass card"><h2>Refresh complete</h2><p>This page unregisters service workers and clears browser caches. Now open the home page.</p><p><a class="btn primary" href="index.html?v=sovereign-v5">Open Command Center</a></p></section>'),
        "404.html": simple_page("SkillOS Page Not Found", "Return to the canonical public command center.", '<p><a class="btn primary" href="index.html">Return home</a></p>'),
    }
    for name, content in pages.items():
        (SITE/name).write_text(content, encoding="utf-8")
    (SITE/"service-worker.js").write_text("self.addEventListener('install',e=>self.skipWaiting());self.addEventListener('activate',e=>{e.waitUntil(self.registration.unregister())});", encoding="utf-8")
    (SITE/".nojekyll").write_text("", encoding="utf-8")
    (SITE/"version.txt").write_text(f"{SCHEMA}\n{MARKER}\n{ts}\n", encoding="utf-8")
    m = manifest(proofs, workflows, skills, ts)
    (SITE/"data"/"command-center-manifest.json").write_text(json.dumps(m, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    health = {"schema": "skillos.command_center.health.v5", "generated_at_utc": ts, "root_marker": MARKER, "required_pages": sorted(pages), "proof_count": len(proofs), "proved_count": sum(1 for p in proofs if p["proved"]), "workflow_count": len(workflows), "skills_used_count": len(skills), "status": "ready"}
    (SITE/"data"/"command-center-health.json").write_text(json.dumps(health, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    registry = {"schema": "skillos.proof_registry.v5", "updated_at_utc": ts, "proofs": [{k:v for k,v in p.items() if k not in {"raw","skills_used"}} for p in proofs]}
    (SITE/"proof-registry.json").write_text(json.dumps(registry, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    (SITE/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>https://montrealai.github.io/skillos/{name}</loc></url>\n" for name in pages) + "</urlset>\n", encoding="utf-8")
    (SITE/"robots.txt").write_text("User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n", encoding="utf-8")
    badge = '<svg xmlns="http://www.w3.org/2000/svg" width="410" height="22" role="img" aria-label="SkillOS sovereign command center v5: fresh"><linearGradient id="g" x2="1"><stop offset="0" stop-color="#07101f"/><stop offset=".55" stop-color="#243064"/><stop offset="1" stop-color="#0d3041"/></linearGradient><rect width="410" height="22" rx="11" fill="url(#g)"/><rect x="294" width="116" height="22" rx="11" fill="#7dffb1"/><text x="12" y="15" fill="#dff7ff" font-family="Verdana" font-size="11">SkillOS sovereign command center v5</text><text x="317" y="15" fill="#06131f" font-family="Verdana" font-size="11" font-weight="700">fresh</text></svg>'
    BADGES.mkdir(exist_ok=True)
    (BADGES/"command-center-sovereign-v5.svg").write_text(badge, encoding="utf-8")
    (SITE/"badges"/"command-center-sovereign-v5.svg").write_text(badge, encoding="utf-8")
    DOCS.mkdir(exist_ok=True)
    (DOCS/"SKILLOS_SOVEREIGN_COMMAND_CENTER_V5.md").write_text(f'''# SkillOS Sovereign Command Center v5

Generated: `{ts}`

This is the canonical public SkillOS Command Center publisher.

It scans proof receipts, workflows, reports, badges, and Skills Used metadata; renders a prestigious public proof atlas; verifies the output; commits the generated site; deploys the exact `site/` artifact to GitHub Pages; and optionally verifies that both `/skillos/` and `/skillos/index.html` are serving the v5 root.

## Canonical marker

`{MARKER}`

## Public thesis

Every job can become a reusable skill. Every verified skill can strengthen the whole network. One agent learns; the system can route that learning everywhere.

## Boundary

This is deterministic public proof and publication infrastructure. It is not audited customer ROI, financial advice, investment advice, legal advice, medical advice, policy advice, token advice, achieved superintelligence, Kardashev Type II achievement, or a guarantee.
''', encoding="utf-8")
    (DOCS/"SKILLOS_COMMAND_CENTER_ROOT_FIX_V5_RUNBOOK.md").write_text(f'''# Root Fix v5 Runbook

Run:

`GitHub → Actions → SkillOS Sovereign Command Center v5 Canonical Deploy → Run workflow`

Inputs:

- `publish_to_repo: true`
- `deploy_pages: true`
- `verify_live: true`
- `cancel_legacy_runs: true`

Verify:

- `https://montrealai.github.io/skillos/data/command-center-manifest.json` contains `{SCHEMA}`
- `https://montrealai.github.io/skillos/?v=sovereign-v5` contains `{MARKER}`
- `https://montrealai.github.io/skillos/index.html?v=sovereign-v5` contains `{MARKER}`
- Neither page contains `Autonomous Proof Command Center`.
''', encoding="utf-8")

def main():
    ts = now_iso()
    proofs = collect_proofs()
    workflows = collect_workflows()
    skills = aggregate_skills(proofs)
    write_pages(proofs, workflows, skills, ts)
    print(json.dumps({"schema": SCHEMA, "marker": MARKER, "generated_at_utc": ts, "proofs": len(proofs), "workflows": len(workflows), "skills": len(skills), "site": str(SITE)}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
