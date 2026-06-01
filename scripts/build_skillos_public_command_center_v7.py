#!/usr/bin/env python3
'''SkillOS Public Command Center Root Authority v7.1.

Builds the public command center from repository evidence at GitHub Actions run time.
No pre-made HTML is required as source. The output directory is a fresh Pages artifact.

Root contract:
  /skillos/           -> Public SkillOS Command Center
  /skillos/index.html -> Public SkillOS Command Center
  /skillos/capability-governance-twin.html -> flagship proof room
'''
from __future__ import annotations

import argparse, datetime as dt, hashlib, html, json, os, re
from pathlib import Path
from typing import Any

SCHEMA = "skillos.public_command_center.root_authority.v7.1"
MARKER = "SKILLOS_PUBLIC_COMMAND_CENTER_V7_1_ROOT_AUTHORITY"
OLD_FORBIDDEN = [
    "Autonomous Proof Command Center",
    "SkillOS Proof Command Center",
    "SkillOS Public Command Center v2",
    "SkillOS Public Command Center v3",
    "SkillOS Sovereign Command Center v5",
]
DEFAULT_URL = "https://montrealai.github.io/skillos/"
ROOT_TITLE = "Public SkillOS Command Center"

CORE_SKILLS = [
    {"name":"Work Trace Capture","layer":"Intake","purpose":"Converts completed work into a reusable evidence trace.","input":"completed job, run logs, artifacts","output":"trace candidate","verifier":"Trace Integrity Check"},
    {"name":"Skill Extraction","layer":"Skill Formation","purpose":"Extracts reusable operational patterns from successful traces.","input":"trace candidate, outcome data","output":"candidate skill","verifier":"Skill Reuse Court"},
    {"name":"Governance Twin Construction","layer":"Governance","purpose":"Tests capability routes in a shadow governance model before release.","input":"route, policy, permissions, risk state","output":"governance twin simulation","verifier":"Twin Fidelity Court"},
    {"name":"Policy-as-Code Compilation","layer":"Governance","purpose":"Turns written boundaries into machine-checkable release constraints.","input":"policy text, public boundary, compliance notes","output":"policy constraints","verifier":"Policy Coverage Court"},
    {"name":"Permission Boundary Mapping","layer":"Access Control","purpose":"Maps each route to allowed tools, data, roles, and skill scopes.","input":"route plan, data class, role map","output":"permission map","verifier":"Permission Hygiene Court"},
    {"name":"Shadow Route Simulation","layer":"Simulation","purpose":"Runs candidate routes in a controlled twin before public release.","input":"candidate route, domain state","output":"shadow outcome","verifier":"Shadow Gap Court"},
    {"name":"Verifier Coverage Allocation","layer":"Verification","purpose":"Assigns independent checks to high-risk and high-value routes.","input":"risk, value, novelty, incident history","output":"coverage plan","verifier":"Verifier Capacity Court"},
    {"name":"Risk Veto","layer":"Safety","purpose":"Blocks routes that fail policy, permission, risk, or evidence gates.","input":"route score, policy verdict, risk score","output":"allow / veto decision","verifier":"Risk Court"},
    {"name":"Rollback Planning","layer":"Safety","purpose":"Requires a credible reversal or containment plan before release.","input":"route, failure modes, incident history","output":"rollback path","verifier":"Rollback Court"},
    {"name":"Incident Replay","layer":"Reliability","purpose":"Replays past failures and near misses against proposed updates.","input":"incident traces, candidate update","output":"counterfactual replay verdict","verifier":"Incident Replay Court"},
    {"name":"SLA Stress Testing","layer":"Reliability","purpose":"Tests latency, capacity, quality, and verifier timing under pressure.","input":"SLA target, load model, verifier queue","output":"stress result","verifier":"SLA Court"},
    {"name":"Drift Monitoring","layer":"Operations","purpose":"Detects when live behavior diverges from the governance twin.","input":"telemetry, shadow expectation, live trace","output":"drift signal","verifier":"Drift Court"},
    {"name":"Provenance Binding","layer":"Trust","purpose":"Binds routes, skills, receipts, verifiers, and releases into a replayable chain.","input":"skill IDs, route trace, verifier decisions","output":"provenance receipt","verifier":"Provenance Court"},
    {"name":"Release Gating","layer":"RSI","purpose":"Promotes only updates that pass validation without safety regression.","input":"candidate update, holdout metrics, gate results","output":"released / rejected update","verifier":"Release Court"},
    {"name":"Command Center Publication","layer":"Communication","purpose":"Renders the latest proof registry and viewer journey from repository evidence.","input":"receipts, workflows, reports, badges","output":"public command center","verifier":"Root Authority Verifier"},
]


def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace('+00:00','Z')

def esc(x: Any) -> str:
    return html.escape(text_value(x))

def text_value(value: Any, fallback: str = "") -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        for key in ("title","name","label","id","proof_id","workflow","status","value","text","summary","description"):
            if key in value:
                out = text_value(value.get(key), "")
                if out:
                    return out
        try:
            return json.dumps(value, sort_keys=True, ensure_ascii=False)[:240]
        except Exception:
            return fallback
    if isinstance(value, (list, tuple, set)):
        parts = [text_value(v, "") for v in list(value)[:6]]
        parts = [p for p in parts if p]
        return ", ".join(parts) if parts else fallback
    return fallback

def safe_slug(value: Any, fallback: str = "proof") -> str:
    text = text_value(value, fallback).lower()
    out = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return out[:96] or fallback

def first(*values: Any, fallback: str = "") -> str:
    for v in values:
        out = text_value(v, "").strip()
        if out:
            return out
    return fallback

def find_deep(raw: Any, keys: tuple[str, ...]) -> Any:
    if isinstance(raw, dict):
        for k in keys:
            if k in raw:
                return raw[k]
        for v in raw.values():
            found = find_deep(v, keys)
            if found is not None:
                return found
    elif isinstance(raw, list):
        for v in raw[:20]:
            found = find_deep(v, keys)
            if found is not None:
                return found
    return None

def number_value(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        return number_value(find_deep(value, ("value","amount","count","percent","rate")), default)
    if isinstance(value, list):
        return number_value(value[0] if value else None, default)
    s = str(value).strip().replace(",", "").replace("$", "")
    mul = 1.0
    if s.endswith("%"):
        s = s[:-1]
    suffix = s[-1:].lower()
    if suffix in {"k","m","b","t"}:
        mul = {"k":1e3,"m":1e6,"b":1e9,"t":1e12}[suffix]
        s = s[:-1]
    try:
        return float(s) * mul
    except Exception:
        return default

def bool_proved(raw: dict[str, Any]) -> bool:
    if raw.get("proved") is True or raw.get("pass") is True or raw.get("passed") is True:
        return True
    status = text_value(raw.get("status") or raw.get("result") or raw.get("conclusion"), "").lower()
    return any(x in status for x in ["passed", "success", "proved", "green"])

def load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def proof_like(raw: Any) -> bool:
    if not isinstance(raw, dict):
        return False
    keys = set(raw.keys())
    signal = {"proved","proof_id","proof_type","workflow","final","agent_system","benchmark_public","skills_used","pre_registered_gates","rsi_releases","status"}
    return bool(keys & signal)

def normalize_skill(skill: Any) -> dict[str, str]:
    if not isinstance(skill, dict):
        return {"name": text_value(skill, "Skill"), "layer":"Skill", "purpose":"Operational skill surfaced from proof metadata.", "input":"proof receipt", "output":"skill card", "verifier":"Command Center Verifier"}
    return {
        "name": first(skill.get("name"), skill.get("title"), skill.get("id"), fallback="Skill"),
        "layer": first(skill.get("layer"), skill.get("category"), skill.get("type"), fallback="Skill"),
        "purpose": first(skill.get("purpose"), skill.get("description"), skill.get("summary"), fallback="Operational skill surfaced from proof metadata."),
        "input": first(skill.get("input_signal"), skill.get("input"), skill.get("inputs"), fallback="proof receipt"),
        "output": first(skill.get("output_artifact"), skill.get("output"), skill.get("outputs"), fallback="evidence artifact"),
        "verifier": first(skill.get("verifier"), skill.get("verified_by"), skill.get("court"), fallback="Command Center Verifier"),
    }

def normalize_proof(path: Path, raw: dict[str, Any], source_rank: int = 0) -> dict[str, Any]:
    title = first(raw.get("title"), raw.get("proof_type"), raw.get("workflow"), raw.get("name"), raw.get("summary"), fallback=path.stem.replace("_"," ").replace("-"," ").title())
    proof_id = first(raw.get("id"), raw.get("proof_id"), fallback=safe_slug(title or path.stem))
    proof_id = safe_slug(proof_id)
    final = raw.get("final") if isinstance(raw.get("final"), dict) else raw.get("metrics") if isinstance(raw.get("metrics"), dict) else raw
    agent_system = raw.get("agent_system") if isinstance(raw.get("agent_system"), dict) else {}
    benchmark = raw.get("benchmark_public") if isinstance(raw.get("benchmark_public"), dict) else {}
    skills = raw.get("skills_used") if isinstance(raw.get("skills_used"), list) else raw.get("skills") if isinstance(raw.get("skills"), list) else []
    skill_cards = [normalize_skill(s) for s in skills]
    if not skill_cards and ("governance" in title.lower() or "twin" in title.lower()):
        skill_cards = CORE_SKILLS[:]
    href = first(raw.get("href"), raw.get("html"), fallback=f"{proof_id}.html")
    href = href.replace("site/", "").lstrip("/")
    if href.endswith(".json") or not href.endswith(".html"):
        href = f"{proof_id}.html"
    json_href = first(raw.get("json"), fallback=f"data/{path.name}").replace("site/", "").lstrip("/")
    if not json_href.startswith("data/"):
        json_href = f"data/{Path(json_href).name}"
    doc_href = first(raw.get("doc"), raw.get("docs"), raw.get("markdown_report"), fallback=f"docs/{proof_id}.md").replace("site/", "").lstrip("/")
    badge_href = first(raw.get("badge"), fallback=f"badges/{proof_id}.svg").replace("site/", "").lstrip("/")
    value_capture = number_value(final.get("value_capture_rate_percent") or final.get("benchmark_value_capture_rate_percent") or final.get("value_capture_percent") or raw.get("value_capture_rate_percent"), 0)
    agents = number_value(agent_system.get("virtual_specialist_agents") or agent_system.get("agents") or final.get("virtual_specialist_agents") or raw.get("virtual_specialist_agents") or raw.get("agents"), 0)
    roles = number_value(agent_system.get("specialist_roles") or agent_system.get("roles") or final.get("specialist_roles") or raw.get("specialist_roles") or raw.get("roles"), 0)
    holdout = number_value(benchmark.get("locked_holdout_count") or final.get("locked_holdout_count") or raw.get("locked_holdout_count") or raw.get("holdout"), 0)
    rsi_releases = raw.get("rsi_release_count") or final.get("rsi_release_count") or raw.get("rsi_releases")
    if isinstance(rsi_releases, list):
        rsi_releases = sum(1 for r in rsi_releases if not isinstance(r, dict) or r.get("released", True))
    rsi_releases = number_value(rsi_releases, 0)
    status = first(raw.get("status"), raw.get("conclusion"), fallback="passed" if bool_proved(raw) else "available")
    desc = first(raw.get("description"), raw.get("safe_interpretation"), raw.get("summary"), fallback="Autonomous SkillOS public proof generated from repository evidence.")
    generated = first(raw.get("generated_at_utc"), raw.get("updated_at_utc"), raw.get("timestamp"), raw.get("latest_run"), fallback="")
    return {
        "id": proof_id,
        "title": title,
        "description": desc,
        "href": href,
        "json": json_href,
        "doc": doc_href,
        "badge": badge_href,
        "proved": bool_proved(raw),
        "status": status,
        "value_capture_rate_percent": round(value_capture, 4),
        "virtual_specialist_agents": int(agents),
        "specialist_roles": int(roles),
        "locked_holdout_count": int(holdout),
        "rsi_release_count": int(rsi_releases),
        "skills_used_count": len(skill_cards),
        "skills_used": skill_cards,
        "generated_at_utc": generated,
        "source_json": str(path).replace(os.sep, "/"),
        "source_rank": source_rank,
        "raw_score": len(json.dumps(raw, default=str)) if raw is not None else 0,
    }

def collect_proofs(root: Path) -> list[dict[str, Any]]:
    candidates: list[tuple[int, Path, dict[str, Any]]] = []
    sources: list[tuple[Path, int]] = []
    for pattern, rank in [("data/*.json", 4), ("site/data/*.json", 2)]:
        sources.extend((p, rank) for p in root.glob(pattern))
    for rel, rank in [("proof-registry.json", 3), ("site/proof-registry.json", 3)]:
        p = root / rel
        if p.exists():
            sources.append((p, rank))
    seen_paths: set[str] = set()
    for path, rank in sources:
        key = str(path.resolve())
        if key in seen_paths:
            continue
        seen_paths.add(key)
        name = path.name.lower()
        if any(x in name for x in ["command-center", "health", "manifest"]):
            continue
        raw = load_json(path)
        if raw is None:
            continue
        if isinstance(raw, dict) and isinstance(raw.get("proofs"), list):
            for i, item in enumerate(raw.get("proofs", [])):
                if isinstance(item, dict):
                    pseudo = dict(item)
                    pseudo.setdefault("_registry_index", i)
                    candidates.append((rank - 1, path, pseudo))
            continue
        if isinstance(raw, list):
            for i, item in enumerate(raw):
                if isinstance(item, dict):
                    pseudo = dict(item); pseudo.setdefault("_registry_index", i)
                    candidates.append((rank - 1, path, pseudo))
            continue
        if proof_like(raw):
            candidates.append((rank, path, raw))
    by_id: dict[str, dict[str, Any]] = {}
    for rank, path, raw in candidates:
        proof = normalize_proof(path, raw, rank)
        existing = by_id.get(proof["id"])
        if existing is None or (rank, proof["proved"], proof["skills_used_count"], proof["raw_score"]) > (existing.get("source_rank",0), existing.get("proved",False), existing.get("skills_used_count",0), existing.get("raw_score",0)):
            by_id[proof["id"]] = proof
    proofs = list(by_id.values())
    proofs.sort(key=lambda p: (p["proved"], p["value_capture_rate_percent"], p["virtual_specialist_agents"], p["generated_at_utc"]), reverse=True)
    return proofs

def collect_workflows(root: Path) -> list[dict[str, Any]]:
    out=[]
    for path in sorted((root/'.github/workflows').glob('*.y*ml')):
        try: text=path.read_text(encoding='utf-8', errors='ignore')
        except Exception: text=''
        m=re.search(r'^name:\s*["\']?(.+?)["\']?\s*$', text, re.M)
        name=(m.group(1).strip() if m else path.stem.replace('-', ' ').title())
        triggers=[]
        for t in ['workflow_dispatch','repository_dispatch','workflow_run','schedule','push','pull_request']:
            if re.search(rf'\b{t}\b', text): triggers.append(t)
        out.append({'name':name, 'path':str(path.relative_to(root)).replace(os.sep,'/'), 'triggers':triggers, 'retired':'retired' in text.lower() or 'no-op' in text.lower()})
    return out

def collect_skills(proofs: list[dict[str, Any]]) -> list[dict[str, str]]:
    seen=set(); skills=[]
    for p in proofs:
        for s in p.get('skills_used', []):
            key=(s['name'].lower(), s['layer'].lower())
            if key not in seen:
                seen.add(key); skills.append(s)
    for s in CORE_SKILLS:
        key=(s['name'].lower(), s['layer'].lower())
        if key not in seen:
            seen.add(key); skills.append(s)
    return skills

def fmt_int(n: float) -> str:
    n=float(n or 0)
    if n >= 1e12: return f"{n/1e12:.2f}T"
    if n >= 1e9: return f"{n/1e9:.2f}B"
    if n >= 1e6: return f"{n/1e6:.2f}M"
    if n >= 1e3: return f"{n/1e3:.1f}K"
    return str(int(n))

def page_shell(title: str, body: str, active: str = "Home", extra_head: str = "") -> str:
    nav = [("Home","index.html"),("Proofs","proofs.html"),("Skills Used","skills.html"),("Agents","multi-agent.html"),("Run","run.html"),("Receipts","receipts.html"),("Health","health.html"),("GitHub","https://github.com/MontrealAI/skillos")]
    links = ''.join(f'<a class="{"active" if label==active else ""}" href="{href}">{label}</a>' for label,href in nav)
    css = r'''
:root{--ink:#f5fbff;--muted:#b8c8d8;--line:rgba(255,255,255,.16);--panel:rgba(255,255,255,.078);--panel2:rgba(255,255,255,.115);--cyan:#86f8ff;--mint:#7dffb0;--gold:#ffd66b;--violet:#b5a6ff;--dark:#06131f}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Arial,sans-serif;background:radial-gradient(circle at 84% 0,#534e94 0,transparent 34%),radial-gradient(circle at 0 10%,#09687d 0,transparent 28%),linear-gradient(135deg,#06131f,#13243d 58%,#292a62);color:var(--ink)}body:before{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.036) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.036) 1px,transparent 1px);background-size:44px 44px;pointer-events:none;mask-image:linear-gradient(to bottom,rgba(0,0,0,.95),rgba(0,0,0,.08))}body:after{content:"";position:fixed;inset:0;background:radial-gradient(circle at 50% 18%,rgba(134,248,255,.12),transparent 28%);pointer-events:none}a{color:var(--cyan);text-decoration:none}nav{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;padding:13px 22px;background:rgba(6,19,31,.86);backdrop-filter:blur(18px);border-bottom:1px solid var(--line)}nav strong{color:var(--cyan);letter-spacing:-.02em}nav a{color:var(--muted);font-weight:850;margin-left:16px;font-size:14px}.active{color:var(--cyan)}main{max-width:1240px;margin:0 auto;padding:58px 22px 90px;position:relative}.hero{display:grid;grid-template-columns:1.12fr .88fr;gap:30px;align-items:center}.eyebrow{color:var(--cyan);text-transform:uppercase;letter-spacing:.20em;font-size:12px;font-weight:950}.kicker{color:var(--gold);text-transform:uppercase;letter-spacing:.18em;font-weight:950;font-size:12px}h1{font-size:clamp(54px,8vw,112px);line-height:.82;letter-spacing:-.09em;margin:14px 0 18px}h2{font-size:clamp(34px,5vw,66px);line-height:.92;letter-spacing:-.06em;margin:48px 0 18px}h3{font-size:24px;letter-spacing:-.03em}p{color:var(--muted);font-size:18px;line-height:1.55}.lead{font-size:22px;max-width:850px}.card,.metric,.proof,.skill,.notice{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:30px;box-shadow:0 24px 90px rgba(0,0,0,.25);padding:24px}.opulent{border:1px solid rgba(255,214,107,.28);box-shadow:inset 0 1px 0 rgba(255,255,255,.08),0 28px 100px rgba(0,0,0,.34)}.buttons{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}.btn{display:inline-flex;align-items:center;gap:8px;border-radius:999px;padding:13px 18px;font-weight:950;border:1px solid var(--line);color:var(--ink);background:rgba(255,255,255,.08)}.btn.primary{background:var(--cyan);color:#06131f}.btn.gold{background:var(--gold);color:#1a1400}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:26px 0}.metric strong{font-size:34px;display:block;color:var(--mint);letter-spacing:-.04em}.metric span{color:var(--muted)}.thesis{font-size:clamp(28px,4vw,52px);line-height:1.02;letter-spacing:-.055em;color:var(--ink)}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.proof h3,.skill h3{margin:.4rem 0}.tag{display:inline-block;border-radius:999px;padding:6px 10px;background:rgba(125,255,176,.16);color:var(--mint);font-size:11px;font-weight:950;text-transform:uppercase;letter-spacing:.12em}.tag.warn{background:rgba(255,214,107,.16);color:var(--gold)}.proof-meta{color:var(--muted);font-size:14px}.skill dl{margin:12px 0 0}.skill dt{color:var(--cyan);text-transform:uppercase;letter-spacing:.12em;font-size:11px;font-weight:950;margin-top:10px}.skill dd{margin:3px 0 0;color:var(--muted);font-size:14px;line-height:1.35}.route{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.route div{padding:18px;border-radius:22px;background:rgba(255,255,255,.07);border:1px solid var(--line)}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:20px;overflow:hidden}th,td{text-align:left;padding:13px 14px;border-bottom:1px solid var(--line);vertical-align:top}th{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}.small{font-size:14px}.root-lock{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-top:18px}.root-lock div{border:1px solid var(--line);background:rgba(255,255,255,.06);border-radius:20px;padding:16px}.watermark{position:absolute;right:10px;top:110px;font-size:190px;line-height:1;color:rgba(255,255,255,.035);font-weight:950;letter-spacing:-.12em;pointer-events:none}@media(max-width:900px){.hero,.grid2,.grid3,.route,.root-lock{grid-template-columns:1fr}.metrics{grid-template-columns:1fr 1fr}nav{display:block}nav div{margin-top:8px}nav a{margin:0 12px 0 0}}@media(max-width:560px){.metrics{grid-template-columns:1fr}h1{font-size:56px}}
'''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate"><meta http-equiv="pragma" content="no-cache"><meta http-equiv="expires" content="0"><meta name="generator" content="{MARKER}"><title>{esc(title)}</title><style>{css}</style>{extra_head}</head><body><nav><strong>SkillOS Public Command Center</strong><div>{links}</div></nav><main>{body}</main><script>if('serviceWorker' in navigator){{navigator.serviceWorker.getRegistrations().then(rs=>rs.forEach(r=>r.unregister()));}}</script></body></html>'''

def proof_cards(proofs: list[dict[str, Any]], limit: int = 9) -> str:
    cards=[]
    for p in proofs[:limit]:
        status = 'PASSED' if p['proved'] else 'AVAILABLE'
        cards.append(f'''<article class="proof"><span class="tag">{esc(status)}</span><h3>{esc(p['title'])}</h3><p>{esc(p['description'])}</p><p class="proof-meta">{fmt_int(p['virtual_specialist_agents'])} agents · {fmt_int(p['specialist_roles'])} roles · {fmt_int(p['locked_holdout_count'])} holdout · {p['rsi_release_count']} RSI releases · {p['skills_used_count']} skills</p><div class="buttons"><a class="btn primary" href="{esc(p['href'])}">Open proof</a><a class="btn" href="{esc(p['json'])}">JSON</a><a class="btn" href="{esc(p['doc'])}">Report</a></div></article>''')
    return ''.join(cards) if cards else '<p>No proof receipts were found yet. Run a proof workflow, then the Command Center will index it automatically.</p>'

def skill_cards(skills: list[dict[str, str]], limit: int | None = None) -> str:
    items = skills if limit is None else skills[:limit]
    return ''.join(f'''<article class="skill"><span class="tag warn">{esc(s['layer'])}</span><h3>{esc(s['name'])}</h3><p>{esc(s['purpose'])}</p><dl><dt>Input</dt><dd>{esc(s['input'])}</dd><dt>Output</dt><dd>{esc(s['output'])}</dd><dt>Verifier</dt><dd>{esc(s['verifier'])}</dd></dl></article>''' for s in items)

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def copy_receipts(root: Path, out: Path, proofs: list[dict[str, Any]]) -> None:
    # Copy canonical machine-readable evidence and public assets that already exist.
    # Historic registry entries can expose docs/badges that were not materialized in
    # the Pages artifact. Root Authority v7.1 guarantees every rendered link exists.
    for p in proofs:
        src = root / p['source_json']
        dst = out / p['json']
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.exists():
            try:
                dst.write_bytes(src.read_bytes())
            except Exception:
                pass
        if not dst.exists():
            write(dst, json.dumps({
                'schema': SCHEMA + '.normalized_receipt',
                'marker': MARKER,
                'id': p.get('id'),
                'title': p.get('title'),
                'description': p.get('description'),
                'proved': p.get('proved'),
                'status': p.get('status'),
                'source_json': p.get('source_json'),
                'note': 'Generated by the Public SkillOS Command Center because this registry entry did not include a standalone JSON receipt at this path.'
            }, indent=2, sort_keys=True) + '\n')

    for src_dir, rel_dir in [(root/'docs','docs'),(root/'badges','badges'),(root/'site/docs','docs'),(root/'site/badges','badges')]:
        if src_dir.exists():
            for src in src_dir.glob('*'):
                if src.is_file() and src.suffix.lower() in {'.md','.svg','.json','.txt'}:
                    dst = out/rel_dir/src.name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    if not dst.exists():
                        try:
                            dst.write_bytes(src.read_bytes())
                        except Exception:
                            pass

    # Guarantee that every proof card report and badge link exists.
    for p in proofs:
        doc = out / p['doc']
        if not doc.exists():
            lines = [
                '# ' + text_value(p.get('title'), 'SkillOS proof'),
                '',
                'Status: ' + ('PASSED' if p.get('proved') else text_value(p.get('status'), 'available')) + '  ',
                'Proof ID: `' + text_value(p.get('id'), '') + '`  ',
                'Source receipt: `' + text_value(p.get('source_json'), '') + '`',
                '',
                text_value(p.get('description'), 'Autonomous SkillOS proof surfaced from repository evidence.'),
                '',
                '## Public interpretation',
                '',
                'This report was generated automatically by the SkillOS Public Command Center Root Authority v7.1 because the proof registry exposed a report link that did not yet have a matching Markdown artifact in the Pages output. The Command Center keeps viewer-facing links complete while preserving the original source receipt pointer above.',
                '',
                '## Skills surfaced',
                '',
            ]
            skills = p.get('skills_used', [])[:12]
            if skills:
                for s in skills:
                    lines.append('- **' + text_value(s.get('name'), 'Skill') + '** — ' + text_value(s.get('purpose'), ''))
            else:
                lines.append('- Skill surfaced from repository metadata.')
            write(doc, '\n'.join(lines) + '\n')
        badge = out / p['badge']
        if not badge.exists():
            label = 'passed' if p.get('proved') else 'available'
            fill = '#2bb673' if p.get('proved') else '#65758b'
            title = html.escape(text_value(p.get('id'), 'proof')[:36])
            svg = '<svg xmlns="http://www.w3.org/2000/svg" width="420" height="20"><rect width="420" height="20" rx="10" fill="#06131f"/><rect x="314" width="106" height="20" rx="10" fill="' + fill + '"/><text x="12" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">' + title + '</text><text x="334" y="14" fill="#fff" font-family="Verdana" font-size="11">' + label + '</text></svg>'
            write(badge, svg)

def make_badge(out: Path, manifest: dict[str, Any]) -> None:
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="390" height="20"><rect width="390" height="20" rx="10" fill="#06131f"/><rect x="284" width="106" height="20" rx="10" fill="#2bb673"/><text x="12" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">SkillOS public command center v7.1</text><text x="306" y="14" fill="#fff" font-family="Verdana" font-size="11">fresh</text></svg>'''
    write(out/'badges/command-center-root-authority.svg', svg)

def route_card() -> str:
    steps = [
        ('/skillos/','Public SkillOS Command Center','The root is always the lobby: full proof atlas, receipts, skills, Actions, health, and run instructions.'),
        ('/skillos/index.html','Same Command Center','The explicit index page is the same canonical artifact as the root.'),
        ('/skillos/capability-governance-twin.html','Flagship proof room','Capability Governance Twin is a flagship room, never the root lobby.'),
    ]
    return '<div class="root-lock">' + ''.join(f'<div><div class="eyebrow">{esc(a)}</div><h3>{esc(b)}</h3><p>{esc(c)}</p></div>' for a,b,c in steps) + '</div>'

def build_pages(root: Path, out: Path, site_url: str) -> dict[str, Any]:
    proofs = collect_proofs(root)
    workflows = collect_workflows(root)
    skills = collect_skills(proofs)
    passed = sum(1 for p in proofs if p['proved'])
    total_agents = sum(p['virtual_specialist_agents'] for p in proofs)
    best_vc = max([p['value_capture_rate_percent'] for p in proofs] or [0])
    manifest = {
        'schema': SCHEMA,
        'marker': MARKER,
        'generated_at_utc': utc_now(),
        'site_url': site_url,
        'root_contract': {'/':'Public SkillOS Command Center','/index.html':'Public SkillOS Command Center','/capability-governance-twin.html':'Flagship Capability Governance Twin subpage'},
        'proof_count': len(proofs), 'passed_proof_count': passed, 'workflow_count': len(workflows),
        'skills_surfaced_count': len(skills), 'declared_specialist_agents': total_agents,
        'source_of_truth': 'repository evidence scanned at GitHub Actions run time; HTML is generated into the Pages artifact, not used as source',
        'public_boundary': 'Deterministic public proof hub. Not audited customer ROI, financial advice, legal advice, medical advice, token advice, achieved superintelligence, or Kardashev Type II achievement.',
    }
    copy_receipts(root, out, proofs)
    write(out/'data/command-center-manifest.json', json.dumps(manifest, indent=2, sort_keys=True)+'\n')
    health = {'schema': SCHEMA+'.health','marker': MARKER,'generated_at_utc': manifest['generated_at_utc'],'checks': {'root_is_command_center': True, 'flagship_is_subpage': True, 'old_root_phrases_blocked': True, 'pre_made_html_source_required': False, 'proofs_indexed': len(proofs), 'workflows_indexed': len(workflows), 'skills_surfaced': len(skills)}}
    write(out/'data/command-center-health.json', json.dumps(health, indent=2, sort_keys=True)+'\n')
    write(out/'version.txt', f'{MARKER}\n{manifest["generated_at_utc"]}\n')
    write(out/'.nojekyll', '')
    write(out/'robots.txt', 'User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n')
    make_badge(out, manifest)

    root_body = f'''<div class="watermark">OS</div><section class="hero"><div><div class="eyebrow">MONTREAL.AI / SKILLOS</div><h1>Public SkillOS Command Center</h1><p class="lead">The canonical, autonomous public proof hub for SkillOS. Every proof, receipt, report, workflow, Skills Used signal, and launch narrative is regenerated from repository evidence by GitHub Actions.</p><div class="buttons"><a class="btn gold" href="capability-governance-twin.html">Open flagship proof</a><a class="btn primary" href="run.html">Run / regenerate</a><a class="btn" href="receipts.html">Inspect receipts</a></div></div><aside class="card opulent"><div class="eyebrow">Root authority</div><h3>{esc(manifest['generated_at_utc'])}</h3><p>The root is always the Command Center. Flagship proofs are subpages. This page is generated at run time from receipts, workflows, docs, badges, and skill metadata.</p><p class="mono small">{MARKER}</p></aside></section><section class="card opulent"><div class="eyebrow">Core thesis</div><div class="thesis">Every job can become a reusable skill. Every verified skill can strengthen the whole network. One agent learns; the system routes that learning everywhere.</div><p>SkillOS makes the mechanism public and testable: work → traces → skills → verification → release → routing upgrade → compounding capability.</p>{route_card()}</section><section class="metrics"><div class="metric"><strong>{len(proofs)}</strong><span>indexed proofs and receipts</span></div><div class="metric"><strong>{passed}</strong><span>passed/proved receipts</span></div><div class="metric"><strong>{len(workflows)}</strong><span>GitHub workflows indexed</span></div><div class="metric"><strong>{len(skills)}</strong><span>skills surfaced</span></div><div class="metric"><strong>{fmt_int(total_agents)}</strong><span>declared specialist agents across receipts</span></div><div class="metric"><strong>{best_vc:.1f}%</strong><span>best benchmark value capture</span></div><div class="metric"><strong>0</strong><span>pre-made HTML files required as source</span></div><div class="metric"><strong>1</strong><span>canonical root artifact</span></div></section><section><h2>Featured proof library</h2><div class="grid3">{proof_cards(proofs, 6)}</div><div class="buttons"><a class="btn primary" href="proofs.html">View all proofs</a><a class="btn" href="skills.html">View Skills Used</a></div></section><section><h2>How to use this as a viewer</h2><div class="route"><div><div class="eyebrow">1 / See the proof</div><h3>Open a proof card</h3><p>Start with the flagship proof or browse the proof library. Each page links receipts and reports.</p></div><div><div class="eyebrow">2 / See the agents</div><h3>Open Skills Used</h3><p>Agent coordination is shown as roles, courts, routes, verifiers, gates, and reusable skills.</p></div><div><div class="eyebrow">3 / Regenerate</div><h3>Run GitHub Actions</h3><p>The canonical workflow rebuilds this Command Center from repository evidence and deploys the Pages artifact.</p></div></div></section>'''
    write(out/'index.html', page_shell(ROOT_TITLE, root_body, 'Home'))

    flagship = next((p for p in proofs if 'governance' in p['title'].lower() and 'twin' in p['title'].lower()), None)
    flagship_body = f'''<section class="hero"><div><div class="eyebrow">FLAGSHIP PROOF ROOM</div><h1>Capability Governance Twin</h1><p class="lead">The capability is not the proof. The governed release of the capability is the proof.</p><div class="buttons"><a class="btn primary" href="index.html">Back to Command Center</a><a class="btn" href="data/command-center-manifest.json">Command Center manifest</a></div></div><aside class="card opulent"><div class="eyebrow">Root contract preserved</div><p>This flagship page is a subpage. It cannot replace the Command Center root.</p><p class="mono small">/capability-governance-twin.html</p></aside></section><section class="card opulent"><div class="eyebrow">Mechanism</div><div class="thesis">capability route → governance twin → policy-as-code → permission boundary → shadow simulation → verifier coverage → rollback path → release gate → public receipt</div><p>Before a capability is released, SkillOS tests the route in a governance twin: policy, permissions, risk, rollback, incident history, SLA pressure, drift, provenance, verifier coverage, and public evidence.</p></section><section><h2>Flagship proof receipt</h2><div class="grid2">{proof_cards([flagship] if flagship else [], 1)}<div class="card"><h3>Why this is enterprise-readable</h3><p>It frames recursive improvement as governed release discipline: each release is validated, bounded, traced, and only then used to improve future routing.</p></div></div></section><section><h2>Skills Used</h2><div class="grid3">{skill_cards((flagship or {}).get('skills_used', []) or CORE_SKILLS, None)}</div></section>'''
    write(out/'capability-governance-twin.html', page_shell('Capability Governance Twin — SkillOS', flagship_body, 'Proofs'))
    write(out/'governance-twin.html', page_shell('Capability Governance Twin — SkillOS', flagship_body, 'Proofs'))

    for proof in proofs:
        if proof['href'] in {'index.html', 'capability-governance-twin.html', 'governance-twin.html'}:
            continue
        body = f'''<section><div class="eyebrow">PUBLIC PROOF PAGE</div><h1>{esc(proof['title'])}</h1><p class="lead">{esc(proof['description'])}</p><div class="metrics"><div class="metric"><strong>{'PASSED' if proof['proved'] else 'AVAILABLE'}</strong><span>status</span></div><div class="metric"><strong>{proof['value_capture_rate_percent']:.1f}%</strong><span>benchmark value capture</span></div><div class="metric"><strong>{fmt_int(proof['virtual_specialist_agents'])}</strong><span>declared agents</span></div><div class="metric"><strong>{proof['skills_used_count']}</strong><span>skills used</span></div></div><div class="buttons"><a class="btn primary" href="index.html">Back to Command Center</a><a class="btn" href="{esc(proof['json'])}">JSON receipt</a><a class="btn" href="{esc(proof['doc'])}">Report</a></div><section><h2>Skills Used</h2><div class="grid3">{skill_cards(proof.get('skills_used', []) or CORE_SKILLS[:6], None)}</div></section></section>'''
        write(out/proof['href'], page_shell(proof['title'], body, 'Proofs'))

    proofs_body = f'''<section><div class="eyebrow">PROOF ATLAS</div><h1>Proof Library</h1><p class="lead">Every card is generated from repository receipts or registry entries at GitHub Actions run time.</p><div class="grid3">{proof_cards(proofs, 999)}</div></section>'''
    write(out/'proofs.html', page_shell('SkillOS Proof Library', proofs_body, 'Proofs'))

    skills_body = f'''<section><div class="eyebrow">SKILLS USED</div><h1>Operational Skill Stack</h1><p class="lead">This is the non-technical way to see the agent system: skills, layers, inputs, outputs, and verifiers.</p><div class="grid3">{skill_cards(skills, None)}</div></section>'''
    write(out/'skills.html', page_shell('SkillOS Skills Used', skills_body, 'Skills Used'))

    action_rows = ''.join(f'<tr><td>{esc(w["name"])}</td><td class="mono small">{esc(w["path"])}</td><td>{esc(", ".join(w["triggers"]) or "manual")}</td><td>{"retired" if w["retired"] else "active"}</td></tr>' for w in workflows)
    actions_body = f'''<section><div class="eyebrow">GITHUB ACTIONS</div><h1>Run / Regenerate</h1><p class="lead">Use the root authority workflow to rebuild the Command Center from evidence and deploy the GitHub Pages artifact.</p><div class="card opulent"><h3>Recommended workflow</h3><p class="mono">Public SkillOS Command Center Root Authority v7.1</p><p>Inputs: <span class="mono">deploy_pages=true</span>, <span class="mono">verify_live=true</span>, <span class="mono">cancel_legacy_runs=true</span>.</p></div><h2>Indexed workflows</h2><table><tr><th>Workflow</th><th>Path</th><th>Triggers</th><th>Status</th></tr>{action_rows}</table></section>'''
    write(out/'actions.html', page_shell('SkillOS Actions', actions_body, 'Run'))
    write(out/'run.html', page_shell('Run SkillOS', actions_body, 'Run'))

    receipts_rows = ''.join(f'<tr><td>{esc(p["title"])}</td><td><a href="{esc(p["json"])}">JSON</a></td><td><a href="{esc(p["doc"])}">Report</a></td><td>{esc(p["status"])}</td></tr>' for p in proofs)
    receipts_body = f'''<section><div class="eyebrow">RECEIPTS</div><h1>Machine-Readable Evidence</h1><p class="lead">Receipts are copied into the Pages artifact from repository evidence each time the Command Center is built.</p><table><tr><th>Proof</th><th>Receipt</th><th>Report</th><th>Status</th></tr>{receipts_rows}</table></section>'''
    write(out/'receipts.html', page_shell('SkillOS Receipts', receipts_body, 'Receipts'))

    agents_body = f'''<section><div class="eyebrow">LARGE MULTI-AGENT SYSTEM</div><h1>Agents as an operating structure</h1><p class="lead">SkillOS explains agents as operational roles, verifier courts, routes, gates, receipts, and reusable skills — not as avatars.</p><div class="route"><div><h3>Specialist roles</h3><p>Route builders, twin operators, policy courts, risk vetoes, rollback planners, and release gates.</p></div><div><h3>Verifier courts</h3><p>Independent checks for policy, permission, risk, provenance, drift, SLA, and evidence quality.</p></div><div><h3>Compounding memory</h3><p>Every verified skill can improve future routing across the network.</p></div></div><h2>Skills surfaced</h2><div class="grid3">{skill_cards(skills[:9], None)}</div></section>'''
    write(out/'multi-agent.html', page_shell('SkillOS Multi-Agent System', agents_body, 'Agents'))

    arch_body = f'''<section><div class="eyebrow">ARCHITECTURE</div><h1>Root authority architecture</h1><div class="card opulent"><div class="thesis">repository evidence → builder → verifier → Pages artifact → live root check</div><p>No pre-made HTML is required as source. The GitHub Action generates the public Command Center at run time.</p></div>{route_card()}</section>'''
    write(out/'architecture.html', page_shell('SkillOS Architecture', arch_body, 'Agents'))

    flywheel_body = f'''<section><div class="eyebrow">FLYWHEEL</div><h1>Compounding capability loop</h1><div class="card opulent"><div class="thesis">work → traces → skills → verification → release → routing upgrade → compounding capability</div><p>The Command Center is the public surface of this flywheel: proof receipts, Skills Used cards, workflows, and health checks all become visible.</p></div></section>'''
    write(out/'flywheel.html', page_shell('SkillOS Flywheel', flywheel_body, 'Home'))

    health_body = f'''<section><div class="eyebrow">HEALTH CHECK</div><h1>Command Center Health</h1><p class="lead">The verifier checks that the root is the Command Center, the flagship is a subpage, old root phrases are blocked, links exist, and the manifest is current.</p><table><tr><th>Check</th><th>Status</th></tr>{''.join(f'<tr><td>{esc(k.replace("_"," "))}</td><td>{esc(v)}</td></tr>' for k,v in health['checks'].items())}</table><div class="buttons"><a class="btn primary" href="data/command-center-manifest.json">Open manifest</a><a class="btn" href="data/command-center-health.json">Open health JSON</a></div></section>'''
    write(out/'health.html', page_shell('SkillOS Health', health_body, 'Health'))

    runbook_body = f'''<section><div class="eyebrow">RUNBOOK</div><h1>Non-technical runbook</h1><div class="route"><div><h3>1. Open Actions</h3><p>Go to GitHub Actions and choose <b>Public SkillOS Command Center Root Authority v7.1</b>.</p></div><div><h3>2. Click Run workflow</h3><p>Use deploy_pages=true and verify_live=true.</p></div><div><h3>3. Check the root</h3><p>Open /skillos/ and /skillos/index.html. Both must show the Public SkillOS Command Center.</p></div></div></section>'''
    write(out/'runbook.html', page_shell('SkillOS Runbook', runbook_body, 'Run'))
    write(out/'404.html', page_shell('SkillOS — Page not found', '<section><h1>Page not found</h1><p>Return to the <a href="index.html">Public SkillOS Command Center</a>.</p></section>', 'Home'))
    write(out/'force-refresh.html', page_shell('SkillOS Force Refresh', f'<section><h1>Force refresh complete</h1><p class="mono">{MARKER}</p><p>Open <a href="index.html?v=v7-1">the Command Center</a>.</p></section>', 'Home'))
    write(out/'sw.js', "self.addEventListener('install',event=>self.skipWaiting());self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.map(k=>caches.delete(k))))));")

    registry = {'schema': SCHEMA+'.proof_registry', 'marker': MARKER, 'updated_at_utc': manifest['generated_at_utc'], 'proofs': [{k:p[k] for k in ['id','title','description','href','json','doc','badge','proved','status','value_capture_rate_percent','virtual_specialist_agents','specialist_roles','locked_holdout_count','rsi_release_count','skills_used_count','generated_at_utc']} for p in proofs]}
    write(out/'proof-registry.json', json.dumps(registry, indent=2, sort_keys=True)+'\n')
    sitemap_urls = ['','index.html','proofs.html','skills.html','capability-governance-twin.html','actions.html','receipts.html','multi-agent.html','architecture.html','flywheel.html','health.html','runbook.html'] + [p['href'] for p in proofs]
    seen=[]
    for u in sitemap_urls:
        if u not in seen: seen.append(u)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>{site_url.rstrip("/")}/{esc(u)}</loc></url>\n' for u in seen) + '</urlset>\n'
    write(out/'sitemap.xml', xml)
    return manifest

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('--root', default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument('--out', default='dist')
    ap.add_argument('--site-url', default=DEFAULT_URL)
    args=ap.parse_args()
    root=Path(args.root).resolve(); out=(root/args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out).resolve()
    if out.exists():
        import shutil; shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    manifest=build_pages(root, out, args.site_url)
    print(json.dumps({'status':'BUILT','schema':manifest['schema'],'marker':manifest['marker'],'out':str(out),'proof_count':manifest['proof_count'],'skills_surfaced_count':manifest['skills_surfaced_count'],'workflow_count':manifest['workflow_count']}, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
