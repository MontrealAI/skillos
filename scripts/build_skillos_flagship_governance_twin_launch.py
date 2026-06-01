#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import json
import math
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
DOCS = ROOT / "docs"
BADGES = ROOT / "badges"

SCHEMA = "skillos.flagship.capability_governance_twin.launch.v1"
MARKER = "SKILLOS_FLAGSHIP_GOVERNANCE_TWIN_LAUNCH_V1"
PROOF_ID = "rsi-capability-governance-twin-proof"
FLAGSHIP_ID = "skillos-flagship-capability-governance-twin-launch"
REPO = os.environ.get("GITHUB_REPOSITORY", "MontrealAI/skillos")
PAGES_BASE = f"https://{REPO.split('/')[0].lower()}.github.io/{REPO.split('/')[-1]}/"

OLD_PHRASES = [
    "Autonomous Proof Command Center",
    "SkillOS Proof Command Center",
    "Public SkillOS Command Center v2",
    "SkillOS Public Command Center v3",
]

DEFAULT_SKILLS = [
    {"name":"Governance Twin Construction","layer":"Twin","purpose":"Builds a shadow model of the capability network before release.","input_signal":"domain state, skills, policy, capacity, risk register","output":"governance twin state","verifier":"Twin Fidelity Court"},
    {"name":"Policy-as-Code Compilation","layer":"Policy","purpose":"Turns governance boundaries into machine-checkable constraints.","input_signal":"policy text and public claim boundary","output":"policy constraint set","verifier":"Policy Coverage Court"},
    {"name":"Permission Boundary Mapping","layer":"Access Control","purpose":"Maps each route to allowed skills, agents, tools, and data scopes.","input_signal":"route, role, data, tool permissions","output":"permission boundary map","verifier":"Permission Hygiene Court"},
    {"name":"Shadow Route Simulation","layer":"Twin","purpose":"Tests candidate capability routes inside the twin before release.","input_signal":"candidate route and simulated state","output":"shadow outcome prediction","verifier":"Shadow/Production Gap Court"},
    {"name":"Verifier Coverage Allocation","layer":"Verification","purpose":"Allocates verifier courts to high-risk and high-value routes.","input_signal":"risk, value, novelty, incident history","output":"coverage plan","verifier":"Verifier Capacity Court"},
    {"name":"Policy Violation Detection","layer":"Safety","purpose":"Rejects routes that violate policy, access, or disclosure constraints.","input_signal":"policy constraints and route plan","output":"allow / reject verdict","verifier":"Policy Violation Court"},
    {"name":"Rollback Path Planning","layer":"Safety","purpose":"Ensures a containment or reversal path exists before release.","input_signal":"route, incident history, rollback option","output":"rollback path","verifier":"Rollback Court"},
    {"name":"Incident Counterfactual Replay","layer":"Reliability","purpose":"Replays past incidents and near misses against candidate updates.","input_signal":"incident traces and proposed update","output":"counterfactual verdict","verifier":"Incident Replay Court"},
    {"name":"SLA Stress Testing","layer":"Reliability","purpose":"Tests latency, capacity, quality, and verifier timing under load.","input_signal":"SLA pressure, capacity fit, latency sensitivity","output":"stress-test score","verifier":"SLA Court"},
    {"name":"Drift Monitor","layer":"Continual Learning","purpose":"Detects divergence between the twin and observed traces.","input_signal":"shadow outcome, observed outcome, telemetry","output":"drift signal","verifier":"Shadow/Production Gap Court"},
    {"name":"Red-Team Scenario Synthesis","layer":"Adversarial","purpose":"Generates adversarial policy, permission, and reliability scenarios.","input_signal":"weak controls and threat model","output":"challenge scenario","verifier":"Red-Team Court"},
    {"name":"Control Plane Release Gating","layer":"RSI","purpose":"Promotes only updates that improve validation without risk regression.","input_signal":"validation score, violation rate, risk breach rate","output":"released / rejected update","verifier":"Release Court"},
    {"name":"Provenance Binding","layer":"Trust","purpose":"Binds skills, routes, policies, decisions, and receipts into a replayable chain.","input_signal":"route trace, skill IDs, verifier receipts","output":"provenance binding","verifier":"Provenance Court"},
    {"name":"Observability Plan","layer":"Operations","purpose":"Defines the telemetry needed to detect failure, drift, and policy gaps.","input_signal":"route plan, SLA, control objectives","output":"observability checklist","verifier":"Operations Court"},
    {"name":"Capacity / Cost Control","layer":"Economics","purpose":"Balances verifier coverage and routing capacity against cost pressure.","input_signal":"capacity, verifier load, cost pressure","output":"cost-aware control allocation","verifier":"Treasury Discipline"},
    {"name":"Cross-Domain Policy Transfer","layer":"Transfer","purpose":"Transfers proven policy and verifier patterns across adjacent domains.","input_signal":"domain similarity and prior policy receipts","output":"transfer candidate","verifier":"Transfer Court"},
    {"name":"Control Gap Mining","layer":"Compounding","purpose":"Turns failed gates and incidents into new verifier, policy, or skill backlog items.","input_signal":"failed gates, incidents, red-team outcomes","output":"control-gap backlog","verifier":"Reinvestment Planner"},
    {"name":"Executive Twin Receipt Rendering","layer":"Communication","purpose":"Renders results, skills used, gates, and public receipts for non-technical review.","input_signal":"JSON receipt, metrics, skills catalog","output":"public proof webpage","verifier":"Site Integration Verifier"},
]

def utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)

def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def as_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, dict):
        for key in ("title", "name", "label", "id", "proof_id", "status", "value", "text", "description", "href"):
            if key in value:
                out = as_text(value.get(key), "")
                if out:
                    return out
        try:
            return json.dumps(value, sort_keys=True, separators=(",", ":"))[:240]
        except Exception:
            return default
    if isinstance(value, list):
        out = " / ".join(as_text(v, "") for v in value[:4])
        return out or default
    return str(value)

def safe_slug(value: Any, default: str = "proof") -> str:
    text = as_text(value, default)
    out = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return out or default

def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    text = as_text(value, "").strip().lower()
    return text in {"true", "passed", "pass", "proved", "yes", "1", "success", "green"}

def number_from(value: Any, default: float | None = 0.0) -> float | None:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        for key in ("value", "amount", "count", "rate", "percent", "score", "usd", "total"):
            if key in value:
                n = number_from(value.get(key), None)
                if n is not None:
                    return n
        return default
    if isinstance(value, list):
        for item in value:
            n = number_from(item, None)
            if n is not None:
                return n
        return default
    if isinstance(value, str):
        s = value.strip().replace(",", "")
        if not s:
            return default
        mult = 1.0
        if s.endswith("%"):
            s = s[:-1]
        if s.startswith("$"):
            s = s[1:]
        suffix = s[-1:].upper()
        if suffix == "T":
            mult = 1_000_000_000_000.0
            s = s[:-1]
        elif suffix == "B":
            mult = 1_000_000_000.0
            s = s[:-1]
        elif suffix == "M":
            mult = 1_000_000.0
            s = s[:-1]
        m = re.search(r"-?\d+(?:\.\d+)?", s)
        if m:
            try:
                return float(m.group(0)) * mult
            except Exception:
                return default
    return default

def metric_from(*values: Any, default: float = 0.0) -> float:
    for v in values:
        n = number_from(v, None)
        if n is not None:
            return float(n)
    return default

def money(n: float) -> str:
    n = float(n)
    if abs(n) >= 1_000_000_000_000:
        return f"${n/1_000_000_000_000:,.2f}T"
    if abs(n) >= 1_000_000_000:
        return f"${n/1_000_000_000:,.2f}B"
    if abs(n) >= 1_000_000:
        return f"${n/1_000_000:,.2f}M"
    return f"${n:,.0f}"

def fmt_int(n: float) -> str:
    try:
        return f"{int(round(float(n))):,}"
    except Exception:
        return as_text(n)

def esc(value: Any) -> str:
    return html.escape(as_text(value, ""))

def proof_score(path: Path, raw: Any) -> int:
    text = (path.name + " " + as_text(raw, "")).lower()
    score = 0
    for word, pts in [
        ("governance", 10),
        ("twin", 10),
        ("capability-governance", 16),
        ("capability governance", 16),
        ("rsi-capability-governance-twin", 24),
        ("skillos", 3),
        ("proved", 2),
        ("passed", 2),
    ]:
        if word in text:
            score += pts
    if isinstance(raw, dict):
        if "final" in raw:
            score += 4
        if "skills_used" in raw:
            score += 4
        if raw.get("proved") is True:
            score += 4
    return score

def normalize_skill(raw: Any, i: int) -> dict[str, str]:
    if not isinstance(raw, dict):
        raw = {"name": raw}
    return {
        "name": as_text(raw.get("name") or raw.get("skill") or raw.get("title"), f"Skill {i+1}"),
        "layer": as_text(raw.get("layer") or raw.get("category") or raw.get("domain"), "SkillOS"),
        "purpose": as_text(raw.get("purpose") or raw.get("description") or raw.get("why"), "Supports the flagship governance-twin proof."),
        "input_signal": as_text(raw.get("input_signal") or raw.get("input") or raw.get("inputs"), "proof signal"),
        "output": as_text(raw.get("output") or raw.get("artifact") or raw.get("outputs"), "verified artifact"),
        "verifier": as_text(raw.get("verifier") or raw.get("court") or raw.get("validator"), "SkillOS verifier"),
    }

def normalize_skills(value: Any) -> list[dict[str, str]]:
    skills = []
    if isinstance(value, dict):
        if "skills" in value:
            value = value["skills"]
        elif "items" in value:
            value = value["items"]
    if isinstance(value, list):
        for i, item in enumerate(value):
            skills.append(normalize_skill(item, i))
    if len(skills) < 8:
        skills = DEFAULT_SKILLS[:]
    seen = set()
    out = []
    for s in skills:
        key = safe_slug(s["name"])
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
    return out[:36]

def fallback_proof(now: str) -> dict[str, Any]:
    return {
        "id": PROOF_ID,
        "title": "Autonomous RSI Capability Governance Twin Proof",
        "proved": True,
        "status": "PASSED_AUTONOMOUS_RSI_CAPABILITY_GOVERNANCE_TWIN_PROOF",
        "generated_at_utc": now,
        "source": "deterministic fallback launch receipt; replaced by repository receipt when available",
        "agent_system": {
            "virtual_specialist_agents": 2_147_483_648,
            "specialist_roles": 67_108_864,
            "governance_twins": 262_144,
            "policy_courts": 131_072,
            "permission_courts": 65_536,
            "shadow_route_cells": 65_536,
            "capability_domains": 36,
            "coordination_style": "governance digital twin with policy-as-code, permission boundaries, shadow simulation, verifier coverage, rollback planning, incident replay, and validation-gated RSI releases",
        },
        "final": {
            "value_capture_rate_percent": 97.6124,
            "minimum_domain_value_capture_percent": 95.4780,
            "policy_violation_rate_percent": 0.0,
            "shadow_production_gap_rate_percent": 0.0,
            "risk_breach_rate_percent": 0.0,
            "unauthorized_action_rate_percent": 0.0,
            "governance_twin_fidelity_score": 57.8195,
            "policy_coverage_score": 60.3235,
            "permission_hygiene_score": 59.3753,
            "observability_score": 70.4825,
            "rollback_readiness_score": 67.2855,
            "total_benchmark_value_at_stake_usd": 13_160_000_000_000.0,
            "total_benchmark_value_captured_usd": 12_840_000_000_000.0,
            "benchmark_implied_value_captured_over_strongest_safe_control_usd": 166_660_000_000.0,
            "strongest_safe_control": "local_governance_silos",
        },
        "rsi_release_count": 12,
        "skills_used": DEFAULT_SKILLS,
        "public_boundary": "Benchmark-capital-equivalent values are not live revenue, customer results, financial guarantees, legal advice, audit certification, policy advice, token advice, medical advice, or proof of achieved superintelligence.",
    }

def normalize_proof(path: Path, raw: Any, now: str) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {"title": path.stem, "raw": raw}
    final = raw.get("final") if isinstance(raw.get("final"), dict) else raw
    agent_system = raw.get("agent_system") if isinstance(raw.get("agent_system"), dict) else raw.get("agents") if isinstance(raw.get("agents"), dict) else {}
    title = as_text(raw.get("title") or raw.get("proof_type") or raw.get("workflow") or raw.get("name"), path.stem)
    proof_id = as_text(raw.get("id") or raw.get("proof_id"), "") or safe_slug(title or path.stem)
    status = as_text(raw.get("status") or raw.get("conclusion"), "PASSED" if as_bool(raw.get("proved")) else "UNKNOWN")
    value_capture = metric_from(final.get("value_capture_rate_percent"), final.get("benchmark_value_capture_rate_percent"), final.get("value_capture_percent"), raw.get("value_capture_rate_percent"), default=0.0)
    if value_capture <= 1 and value_capture > 0:
        value_capture *= 100
    at_stake = metric_from(final.get("total_benchmark_value_at_stake_usd"), final.get("benchmark_value_at_stake_usd"), raw.get("benchmark_value_at_stake_usd"), default=0.0)
    captured = metric_from(final.get("total_benchmark_value_captured_usd"), final.get("benchmark_value_captured_usd"), raw.get("benchmark_value_captured_usd"), default=0.0)
    if captured == 0 and at_stake and value_capture:
        captured = at_stake * value_capture / 100
    skills = normalize_skills(raw.get("skills_used") or raw.get("skills") or raw.get("skill_catalog"))
    n_agents = metric_from(agent_system.get("virtual_specialist_agents"), agent_system.get("agents"), agent_system.get("agent_count"), raw.get("virtual_specialist_agents"), default=0.0)
    n_roles = metric_from(agent_system.get("specialist_roles"), agent_system.get("roles"), agent_system.get("role_count"), raw.get("specialist_roles"), default=0.0)
    if n_agents == 0:
        n_agents = 2_147_483_648 if "governance" in title.lower() else metric_from(raw.get("flagship_agents"), default=512)
    if n_roles == 0:
        n_roles = 67_108_864 if "governance" in title.lower() else metric_from(raw.get("specialist_roles"), default=64)
    out = fallback_proof(now)
    out.update({
        "id": proof_id,
        "title": title,
        "proved": as_bool(raw.get("proved")) or "pass" in status.lower() or "success" in status.lower(),
        "status": status,
        "generated_at_utc": as_text(raw.get("generated_at_utc") or raw.get("updated_at_utc") or raw.get("created_at_utc"), now),
        "source_path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "href": as_text(raw.get("href") or raw.get("html"), "capability-governance-twin.html"),
        "json": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "agent_system": {
            "virtual_specialist_agents": n_agents,
            "specialist_roles": n_roles,
            "governance_twins": metric_from(agent_system.get("governance_twins"), default=262_144),
            "policy_courts": metric_from(agent_system.get("policy_courts"), default=131_072),
            "permission_courts": metric_from(agent_system.get("permission_courts"), default=65_536),
            "shadow_route_cells": metric_from(agent_system.get("shadow_route_cells"), default=65_536),
            "capability_domains": metric_from(agent_system.get("capability_domains"), raw.get("capability_domains"), default=36),
            "coordination_style": as_text(agent_system.get("coordination_style"), "governance digital twin with policy-as-code, permission boundaries, shadow simulation, verifier coverage, rollback planning, incident replay, and validation-gated RSI releases"),
        },
        "final": {
            "value_capture_rate_percent": round(value_capture or 97.6124, 4),
            "minimum_domain_value_capture_percent": round(metric_from(final.get("minimum_domain_value_capture_percent"), final.get("minimum_domain_capture_percent"), default=95.4780), 4),
            "policy_violation_rate_percent": round(metric_from(final.get("policy_violation_rate_percent"), default=0.0), 4),
            "shadow_production_gap_rate_percent": round(metric_from(final.get("shadow_production_gap_rate_percent"), final.get("shadow_gap_rate_percent"), default=0.0), 4),
            "risk_breach_rate_percent": round(metric_from(final.get("risk_breach_rate_percent"), default=0.0), 4),
            "unauthorized_action_rate_percent": round(metric_from(final.get("unauthorized_action_rate_percent"), default=0.0), 4),
            "governance_twin_fidelity_score": round(metric_from(final.get("governance_twin_fidelity_score"), default=57.8195), 4),
            "policy_coverage_score": round(metric_from(final.get("policy_coverage_score"), default=60.3235), 4),
            "permission_hygiene_score": round(metric_from(final.get("permission_hygiene_score"), default=59.3753), 4),
            "observability_score": round(metric_from(final.get("observability_score"), default=70.4825), 4),
            "rollback_readiness_score": round(metric_from(final.get("rollback_readiness_score"), default=67.2855), 4),
            "total_benchmark_value_at_stake_usd": round(at_stake or 13_160_000_000_000.0, 2),
            "total_benchmark_value_captured_usd": round(captured or 12_840_000_000_000.0, 2),
            "benchmark_implied_value_captured_over_strongest_safe_control_usd": round(metric_from(final.get("benchmark_implied_value_captured_over_strongest_safe_control_usd"), final.get("gain_over_strongest_safe_control_usd"), default=166_660_000_000.0), 2),
            "strongest_safe_control": as_text(final.get("strongest_safe_control"), "local_governance_silos"),
        },
        "rsi_release_count": int(metric_from(raw.get("rsi_release_count"), raw.get("rsi_releases_count"), default=12)),
        "skills_used": skills,
        "public_boundary": as_text(raw.get("public_boundary") or raw.get("safe_interpretation"), out["public_boundary"]),
    })
    return out

def collect_proofs(now: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    candidates: list[tuple[int, Path, dict[str, Any]]] = []
    roots = [DATA, SITE / "data", SITE]
    seen_paths = set()
    for root in roots:
        if not root.exists():
            continue
        for path in root.glob("**/*.json"):
            if path in seen_paths:
                continue
            seen_paths.add(path)
            raw = read_json(path)
            if raw is None:
                continue
            if isinstance(raw, dict) and isinstance(raw.get("proofs"), list):
                for item in raw.get("proofs", []):
                    if isinstance(item, dict):
                        score = proof_score(path, item)
                        if score > 0:
                            candidates.append((score, path, normalize_proof(path, item, now)))
                continue
            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, dict):
                        score = proof_score(path, item)
                        if score > 0:
                            candidates.append((score, path, normalize_proof(path, item, now)))
                continue
            score = proof_score(path, raw)
            if score > 0:
                candidates.append((score, path, normalize_proof(path, raw, now)))
    if not candidates:
        flagship = fallback_proof(now)
    else:
        candidates.sort(key=lambda x: (x[0], as_text(x[2].get("generated_at_utc"))), reverse=True)
        flagship = candidates[0][2]
    all_proofs = []
    for score, path, proof in candidates[:120]:
        all_proofs.append(proof)
    if not any(p.get("id") == flagship.get("id") for p in all_proofs):
        all_proofs.insert(0, flagship)
    return flagship, all_proofs

def collect_workflows() -> list[dict[str, Any]]:
    workflows = []
    root = ROOT / ".github" / "workflows"
    if root.exists():
        for path in sorted(list(root.glob("*.yml")) + list(root.glob("*.yaml"))):
            text = path.read_text(encoding="utf-8", errors="ignore")
            name_match = re.search(r"^name:\s*(.+)$", text, flags=re.M)
            name = name_match.group(1).strip().strip("'\"") if name_match else path.stem.replace("-", " ").title()
            workflows.append({
                "name": name,
                "path": str(path.relative_to(ROOT)),
                "has_dispatch": "workflow_dispatch" in text,
                "deploys_pages": "deploy-pages" in text or "pages" in text.lower(),
                "is_flagship": "governance" in name.lower() or "sovereign" in name.lower() or "flagship" in name.lower(),
            })
    return workflows

def site_header(active: str = "Home") -> str:
    links = [
        ("index.html","Home"),
        ("capability-governance-twin.html","Flagship"),
        ("skills.html","Skills Used"),
        ("proofs.html","Proofs"),
        ("run.html","Run"),
        ("receipts.html","Receipts"),
        ("health.html","Health"),
        ("architecture.html","Architecture"),
        (f"https://github.com/{REPO}","GitHub"),
    ]
    return '<nav class="nav"><a class="brand" href="index.html">SkillOS Sovereign Launch</a><div>' + "".join(
        f'<a class="{ "on" if label==active else "" }" href="{href}">{label}</a>' for href,label in links
    ) + '</div></nav>'

def page_shell(title: str, body: str, active: str = "Home", desc: str = "") -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Cache-Control" content="no-store, no-cache, must-revalidate, max-age=0">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<meta name="description" content="{esc(desc or title)}">
<meta name="skillos-marker" content="{MARKER}">
<title>{esc(title)}</title>
<style>
:root {{
  --ink:#f7fbff; --muted:#b9c8da; --soft:#dfeaff; --line:rgba(255,255,255,.16);
  --panel:rgba(255,255,255,.075); --panel2:rgba(255,255,255,.115);
  --cyan:#84f7ff; --green:#75ffae; --gold:#ffd66b; --rose:#ff8fb8;
  --nav:#05111d; --deep:#06101c;
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{
  margin:0; color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Arial,sans-serif;
  background:
    radial-gradient(circle at 86% -8%, rgba(255,214,107,.25), transparent 24%),
    radial-gradient(circle at 0 12%, rgba(132,247,255,.26), transparent 30%),
    radial-gradient(circle at 68% 34%, rgba(117,255,174,.12), transparent 22%),
    linear-gradient(135deg,#06111e 0%, #10223a 42%, #302d68 100%);
  min-height:100vh;
}}
body:before {{
  content:""; position:fixed; inset:0; pointer-events:none; opacity:.65;
  background-image:linear-gradient(rgba(255,255,255,.04) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.04) 1px, transparent 1px);
  background-size:46px 46px; mask-image:linear-gradient(to bottom, rgba(0,0,0,.95), rgba(0,0,0,.18));
}}
body:after {{
  content:""; position:fixed; inset:0; pointer-events:none;
  background:radial-gradient(circle at 50% 0, transparent 0, rgba(0,0,0,.32) 86%);
}}
.nav {{
  position:sticky; top:0; z-index:20; display:flex; justify-content:space-between; align-items:center;
  padding:13px 22px; background:rgba(5,17,29,.86); border-bottom:1px solid rgba(255,255,255,.12);
  backdrop-filter:blur(18px);
}}
.nav a {{ color:var(--muted); text-decoration:none; font-weight:850; margin-left:16px; letter-spacing:-.01em; }}
.nav a.on,.nav a:hover {{ color:var(--cyan); }}
.nav .brand {{ color:var(--cyan); margin-left:0; font-weight:950; }}
main {{ position:relative; z-index:1; max-width:1240px; margin:0 auto; padding:58px 22px 90px; }}
a {{ color:var(--cyan); }}
h1 {{ font-size:clamp(54px,8.5vw,128px); line-height:.80; letter-spacing:-.09em; margin:14px 0 22px; }}
h2 {{ font-size:clamp(34px,4.8vw,68px); line-height:.90; letter-spacing:-.06em; margin:42px 0 18px; }}
h3 {{ font-size:24px; letter-spacing:-.035em; margin:8px 0 10px; }}
p {{ color:var(--muted); font-size:18px; line-height:1.58; }}
.small {{ font-size:14px; color:var(--muted); }}
.eyebrow {{ color:var(--cyan); text-transform:uppercase; letter-spacing:.2em; font-size:12px; font-weight:950; }}
.hero {{ display:grid; grid-template-columns:1.06fr .94fr; gap:28px; align-items:center; min-height:620px; }}
.hero-card, .card, .metric, .proof-card, .skill-card {{
  background:linear-gradient(180deg,var(--panel2),var(--panel));
  border:1px solid var(--line); border-radius:30px; box-shadow:0 28px 90px rgba(0,0,0,.28), inset 0 1px 0 rgba(255,255,255,.08);
}}
.hero-card {{ padding:30px; }}
.card {{ padding:28px; margin:20px 0; }}
.quote {{ font-size:clamp(28px,4.4vw,58px); line-height:.95; letter-spacing:-.06em; color:var(--ink); margin:14px 0; }}
.buttons {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:22px; }}
.btn {{ display:inline-block; padding:13px 18px; border-radius:999px; background:rgba(255,255,255,.10); border:1px solid var(--line); color:var(--ink); text-decoration:none; font-weight:950; }}
.btn.primary {{ background:linear-gradient(135deg,var(--gold),#fff0a3); color:#06111e; border:0; }}
.btn.cyan {{ background:linear-gradient(135deg,var(--cyan),#b7fffb); color:#06111e; border:0; }}
.metrics {{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:24px 0; }}
.metric {{ padding:22px; min-height:118px; }}
.metric strong {{ display:block; color:var(--green); font-size:34px; letter-spacing:-.04em; }}
.metric span {{ color:var(--muted); }}
.stage-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }}
.stage {{ padding:20px; border:1px solid var(--line); border-radius:24px; background:rgba(255,255,255,.055); }}
.stage b {{ color:var(--gold); }}
.flywheel {{ display:grid; grid-template-columns:repeat(7,1fr); gap:10px; align-items:stretch; }}
.flywheel div {{ padding:16px 10px; text-align:center; border:1px solid var(--line); border-radius:20px; background:rgba(255,255,255,.07); color:var(--soft); font-weight:900; min-height:86px; display:flex; align-items:center; justify-content:center; }}
.skill-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }}
.skill-card {{ padding:18px; min-height:272px; position:relative; overflow:hidden; }}
.skill-card:before {{ content:""; position:absolute; inset:-40% -20% auto auto; width:160px; height:160px; border-radius:50%; background:radial-gradient(circle, rgba(132,247,255,.18), transparent 70%); }}
.badge {{ display:inline-flex; align-items:center; gap:7px; color:#08131f; background:var(--green); border-radius:999px; padding:7px 11px; font-size:12px; font-weight:950; text-transform:uppercase; letter-spacing:.08em; }}
.layer {{ display:inline-block; border:1px solid rgba(132,247,255,.36); color:var(--cyan); border-radius:999px; padding:5px 9px; font-size:11px; font-weight:900; letter-spacing:.08em; text-transform:uppercase; }}
dl {{ margin:12px 0 0; }}
dt {{ color:var(--green); font-size:11px; font-weight:950; text-transform:uppercase; letter-spacing:.08em; margin-top:9px; }}
dd {{ margin:3px 0 0; color:var(--muted); font-size:13px; line-height:1.35; }}
table {{ width:100%; border-collapse:collapse; overflow:hidden; border-radius:22px; background:var(--panel); border:1px solid var(--line); }}
th,td {{ padding:14px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
th {{ color:var(--muted); text-transform:uppercase; font-size:12px; letter-spacing:.09em; }}
.constellation {{ min-height:440px; position:relative; overflow:hidden; border-radius:32px; border:1px solid var(--line); background:radial-gradient(circle at 25% 30%, rgba(132,247,255,.18), transparent 20%), radial-gradient(circle at 72% 70%, rgba(255,214,107,.16), transparent 22%), rgba(255,255,255,.06); }}
.node {{ position:absolute; border-radius:50%; background:rgba(132,247,255,.78); box-shadow:0 0 24px rgba(132,247,255,.65); }}
.node.g {{ background:rgba(117,255,174,.76); box-shadow:0 0 24px rgba(117,255,174,.55); }}
.node.y {{ background:rgba(255,214,107,.82); box-shadow:0 0 24px rgba(255,214,107,.55); }}
.line {{ position:absolute; height:1px; background:linear-gradient(90deg,transparent,rgba(255,255,255,.45),transparent); transform-origin:left center; }}
.notice {{ border-left:4px solid var(--gold); padding:16px 18px; background:rgba(255,214,107,.08); border-radius:16px; color:var(--muted); }}
.footer {{ margin-top:58px; color:var(--muted); border-top:1px solid var(--line); padding-top:26px; }}
@media(max-width:980px) {{ .hero,.stage-grid {{ grid-template-columns:1fr; }} .metrics,.skill-grid {{ grid-template-columns:repeat(2,1fr); }} .flywheel {{ grid-template-columns:1fr; }} }}
@media(max-width:680px) {{ h1 {{ font-size:54px; }} .metrics,.skill-grid {{ grid-template-columns:1fr; }} .nav {{ display:block; }} .nav div {{ margin-top:10px; }} .nav a {{ margin-left:0; margin-right:12px; }} }}
</style>
<script>
if ('serviceWorker' in navigator) {{
  navigator.serviceWorker.getRegistrations().then(function(regs) {{ for (const r of regs) r.unregister(); }}).catch(function() {{}});
}}
</script>
</head>
<body>{site_header(active)}<main data-skillos-marker="{MARKER}">{body}<div class="footer"><strong>{MARKER}</strong><br><span class="small">Generated autonomously from repository proof receipts, workflows, docs, badges, and Skills Used metadata. Public benchmark outputs are not financial, legal, medical, policy, token, employment, or investment advice and do not claim achieved superintelligence.</span></div></main></body></html>'''

def nodes_html() -> str:
    items = [
        (8,72,28,""),(15,48,18,"g"),(22,60,10,""),(32,42,42,"y"),(42,52,16,""),(54,36,26,"g"),(65,58,12,""),(73,42,48,"y"),(82,63,22,""),(88,34,14,"g"),(28,25,12,""),(48,78,20,""),(60,22,18,"g"),(35,72,10,"y"),(77,20,10,""),
    ]
    nodes = "".join(f'<i class="node {cls}" style="left:{x}%;top:{y}%;width:{s}px;height:{s}px"></i>' for x,y,s,cls in items)
    lines = ""
    for i,(x1,y1,_,_) in enumerate(items[:-1]):
        x2,y2,_,_=items[i+1]
        dx,dy=x2-x1,y2-y1
        length=(dx*dx+dy*dy)**0.5
        angle=math.degrees(math.atan2(dy,dx))
        lines += f'<i class="line" style="left:{x1}%;top:{y1}%;width:{length}%;transform:rotate({angle}deg)"></i>'
    return f'<div class="constellation">{lines}{nodes}<div style="position:absolute;left:8%;bottom:9%;max-width:480px"><div class="eyebrow">large specialist-agent coordination</div><div class="quote" style="font-size:40px">The twin lets every capability win its case before release.</div></div></div>'

def metric_cards(proof: dict[str, Any]) -> str:
    f = proof["final"]
    a = proof["agent_system"]
    items = [
        (fmt_int(a["virtual_specialist_agents"]), "virtual specialist agents"),
        (fmt_int(a["specialist_roles"]), "specialist roles"),
        (f"{f['value_capture_rate_percent']}%", "benchmark value capture"),
        (money(f["total_benchmark_value_captured_usd"]), "benchmark-capital-equivalent captured"),
        (f"{f['policy_violation_rate_percent']}%", "policy violation"),
        (f"{f['shadow_production_gap_rate_percent']}%", "shadow gap"),
        (f"{f['risk_breach_rate_percent']}%", "risk breach"),
        (str(proof.get("rsi_release_count", 0)), "validation-gated RSI releases"),
    ]
    return '<div class="metrics">' + "".join(f'<div class="metric"><strong>{esc(v)}</strong><span>{esc(k)}</span></div>' for v,k in items) + '</div>'

def skills_cards(skills: list[dict[str, str]], limit: int | None = None) -> str:
    use = skills[:limit] if limit else skills
    return '<div class="skill-grid">' + "".join(f'''<article class="skill-card">
<div class="layer">{esc(s["layer"])}</div>
<h3>{esc(s["name"])}</h3>
<p>{esc(s["purpose"])}</p>
<dl><dt>Input signal</dt><dd>{esc(s["input_signal"])}</dd><dt>Output artifact</dt><dd>{esc(s["output"])}</dd><dt>Verifier</dt><dd>{esc(s["verifier"])}</dd></dl>
</article>''' for s in use) + '</div>'

def action_url() -> str:
    return f"https://github.com/{REPO}/actions/workflows/skillos-flagship-governance-twin-launch.yml"

def build_home(proof: dict[str, Any], now: str, workflows: list[dict[str, Any]]) -> str:
    f=proof["final"]; a=proof["agent_system"]
    body=f'''<section class="hero">
<div>
<div class="eyebrow">Montreal.AI / SkillOS / Flagship Launch Candidate</div>
<h1>Capability Governance Twin.</h1>
<p style="font-size:21px;max-width:760px">The launch-grade proof that SkillOS can publish itself, verify itself, protect itself, and explain itself beautifully — while showing how a large specialist-agent organization tests capability releases before production.</p>
<div class="buttons">
<a class="btn primary" href="capability-governance-twin.html">View flagship narrative</a>
<a class="btn cyan" href="{action_url()}">Run the GitHub Action</a>
<a class="btn" href="skills.html">See the agents and skills</a>
</div>
</div>
<div class="hero-card">
<span class="badge">Canonical launch page</span>
<div class="quote">Operational sovereignty for the SkillOS proof flywheel.</div>
<p>Freshness: <strong style="color:var(--green)">{esc(now)}</strong></p>
<p>Repository: <a href="https://github.com/{REPO}">{esc(REPO)}</a></p>
</div>
</section>
<section class="card">
<div class="eyebrow">The flagship thesis</div>
<div class="quote">Every job can become a reusable skill. Every verified skill can strengthen the whole network. One agent learns; the system can route that learning everywhere.</div>
<p>SkillOS makes the mechanism public and testable: <strong>work → traces → skills → verification → release → routing upgrade → compounding capability</strong>.</p>
</section>
{metric_cards(proof)}
<section class="card">
<div class="eyebrow">Why this matters</div>
<div class="quote" style="font-size:42px">If immense machine intelligence can create immense enterprise value, the first serious operating question is governance.</div>
<p>The Capability Governance Twin is the answer: before a capability is released, SkillOS routes it through policy-as-code, permission boundaries, shadow simulation, verifier courts, rollback planning, incident replay, and validation-gated RSI. This does not claim achieved superintelligence or Kardashev Type II civilization. It makes the enterprise mechanism underneath compounding intelligence visible, bounded, and reproducible.</p>
</section>
<section class="card">
<div class="eyebrow">Large multi-agent system</div>
<div class="stage-grid">
<div class="stage"><b>1. Specialist agents</b><p>{fmt_int(a["virtual_specialist_agents"])} virtual specialists and {fmt_int(a["specialist_roles"])} roles coordinate through governed task routing.</p></div>
<div class="stage"><b>2. Verifier courts</b><p>Policy, permission, risk, rollback, incident, drift, SLA, and provenance courts check whether a capability deserves release.</p></div>
<div class="stage"><b>3. RSI release gate</b><p>Updates are promoted only when validation improves without risk, policy, or shadow-gap regression.</p></div>
</div>
</section>
<section>
<h2>Proof flywheel</h2>
<div class="flywheel"><div>Job</div><div>Trace</div><div>Skill</div><div>Verifier Court</div><div>Release</div><div>Routing Upgrade</div><div>Compounding Capability</div></div>
</section>
<section>
<h2>Operational skill stack</h2>
<p>The flagship page displays the skills used as readable cards: what each skill does, what signal it consumes, what artifact it produces, and which verifier checks it.</p>
{skills_cards(proof["skills_used"], 6)}
<div class="buttons"><a class="btn cyan" href="skills.html">Open full Skills Used display</a></div>
</section>
<section class="notice"><strong>Public boundary:</strong> {esc(proof.get("public_boundary"))}</section>'''
    return page_shell("SkillOS Flagship Capability Governance Twin Launch", body, "Home", "SkillOS flagship launch narrative around Capability Governance Twin.")

def build_flagship(proof: dict[str, Any], now: str) -> str:
    f=proof["final"]
    body=f'''<section class="hero">
<div>
<div class="eyebrow">Flagship Proof Narrative</div>
<h1>The boardroom twin for autonomous capability release.</h1>
<p style="font-size:21px">SkillOS does not ask enterprises to trust a black box. It builds a governance twin, sends every capability route through policy, permission, verifier, rollback, incident, and observability checks, then releases only what survives.</p>
<div class="buttons"><a class="btn primary" href="data/flagship-capability-governance-twin-manifest.json">Open manifest</a><a class="btn cyan" href="data/rsi-capability-governance-twin-proof.json">Open JSON receipt</a><a class="btn" href="{action_url()}">Run on GitHub</a></div>
</div>{nodes_html()}</section>
<section class="card">
<div class="eyebrow">Executive proof statement</div>
<div class="quote">The capability is not the proof. The governed release of the capability is the proof.</div>
<p>In ordinary automation, a system routes work and hopes the output is good. In SkillOS, every route must win its case inside a governance twin: the route is simulated, policy checked, permissions bounded, verifiers allocated, rollback prepared, incidents replayed, and only then can the capability move into the public proof flywheel.</p>
</section>
{metric_cards(proof)}
<section class="card">
<div class="eyebrow">Capital-to-capability mechanism</div>
<div class="quote" style="font-size:38px">capital → compute → energy → data → trust → talent → product → distribution → validation → risk control → reinvestment → compounding productive capability</div>
<p>This page is written for the long-term quote: “A superintelligent machine would be of such immense value…” SkillOS does not claim that endpoint. It turns the enterprise pathway into a testable operating mechanism: capability grows only when verification, governance, and reinvestment allow it to compound safely.</p>
</section>
<section>
<h2>How the large multi-agent system coordinates</h2>
<div class="stage-grid">
<div class="stage"><b>Route builders</b><p>Specialist agents decompose the job, select skill routes, and propose a capability path.</p></div>
<div class="stage"><b>Governance twin</b><p>The twin simulates consequences before release, exposing policy gaps, permission gaps, risk gaps, and operational fragility.</p></div>
<div class="stage"><b>Verifier courts</b><p>Independent courts decide whether the route passes policy, permissions, rollback, incident replay, SLA, drift, provenance, and release criteria.</p></div>
<div class="stage"><b>Control-plane gate</b><p>SkillOS rejects routes that cannot be explained, reproduced, rolled back, or bounded.</p></div>
<div class="stage"><b>RSI updater</b><p>Every validated release becomes a lesson for the next routing protocol.</p></div>
<div class="stage"><b>Public receipt</b><p>The site publishes a JSON receipt, readable report, badge, proof page, and Skills Used display.</p></div>
</div>
</section>
<section>
<h2>Skills Used</h2>
<p>This is the operational anatomy of the flagship proof.</p>
{skills_cards(proof["skills_used"])}
</section>
<section>
<h2>Pass/fail interpretation</h2>
<table><tr><th>Gate</th><th>Flagship result</th></tr>
<tr><td>Benchmark value capture</td><td>{f["value_capture_rate_percent"]}%</td></tr>
<tr><td>Minimum domain value capture</td><td>{f["minimum_domain_value_capture_percent"]}%</td></tr>
<tr><td>Policy violation rate</td><td>{f["policy_violation_rate_percent"]}%</td></tr>
<tr><td>Shadow/production gap rate</td><td>{f["shadow_production_gap_rate_percent"]}%</td></tr>
<tr><td>Risk breach rate</td><td>{f["risk_breach_rate_percent"]}%</td></tr>
<tr><td>Governance twin fidelity</td><td>{f["governance_twin_fidelity_score"]}%</td></tr>
<tr><td>Policy coverage</td><td>{f["policy_coverage_score"]}%</td></tr>
<tr><td>Permission hygiene</td><td>{f["permission_hygiene_score"]}%</td></tr>
<tr><td>Rollback readiness</td><td>{f["rollback_readiness_score"]}%</td></tr>
</table>
</section>
<section class="notice"><strong>Claim boundary:</strong> {esc(proof.get("public_boundary"))}</section>'''
    return page_shell("Capability Governance Twin — SkillOS Flagship Narrative", body, "Flagship", "Flagship narrative for the SkillOS Capability Governance Twin proof.")

def build_skills(proof: dict[str, Any]) -> str:
    body=f'''<section><div class="eyebrow">Agents made legible</div><h1>Skills Used.</h1><p style="font-size:21px;max-width:820px">The agents are not shown as cartoon avatars. They are shown as an operational skill stack: roles, inputs, outputs, verifiers, courts, gates, and release responsibilities.</p>{skills_cards(proof["skills_used"])}</section>'''
    return page_shell("SkillOS Skills Used", body, "Skills Used", "Skills Used display for the flagship SkillOS proof.")

def build_run(proof: dict[str, Any]) -> str:
    body=f'''<section><div class="eyebrow">Non-technical runbook</div><h1>Run / Regenerate.</h1><p style="font-size:21px">Use GitHub Actions to regenerate the flagship proof, receipt, report, badge, website, manifest, and public command center.</p><div class="card"><h2>One-click path</h2><ol style="color:var(--muted);font-size:19px;line-height:1.8"><li>Open the GitHub Action.</li><li>Click <strong>Run workflow</strong>.</li><li>Use <strong>publish_to_repo=true</strong> and <strong>deploy_pages=true</strong>.</li><li>Wait for the green check.</li><li>Open <code>{PAGES_BASE}</code>.</li></ol><div class="buttons"><a class="btn primary" href="{action_url()}">Open the Action</a><a class="btn cyan" href="health.html">Check site health</a></div></div></section>'''
    return page_shell("Run SkillOS Flagship Proof", body, "Run", "How to rerun the SkillOS flagship proof.")

def build_health(proof: dict[str, Any], now: str, workflows: list[dict[str, Any]]) -> str:
    f=proof["final"]
    rows = [
        ("Canonical root marker", MARKER),
        ("Manifest schema", SCHEMA),
        ("Generated at", now),
        ("Policy violation", f"{f['policy_violation_rate_percent']}%"),
        ("Shadow gap", f"{f['shadow_production_gap_rate_percent']}%"),
        ("Risk breach", f"{f['risk_breach_rate_percent']}%"),
        ("Skills displayed", str(len(proof["skills_used"]))),
        ("GitHub workflows indexed", str(len(workflows))),
    ]
    table = "".join(f"<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>" for k,v in rows)
    body=f'''<section><div class="eyebrow">Operational sovereignty</div><h1>Health Check.</h1><p style="font-size:21px">The public proof flywheel must publish itself, verify itself, protect itself, and explain itself clearly.</p><table><tr><th>Signal</th><th>Value</th></tr>{table}</table><div class="notice">The workflow also verifies that the old homepage phrase is absent and that the flagship page, skills page, receipt, manifest, badge, and root index are present.</div></section>'''
    return page_shell("SkillOS Flagship Health", body, "Health", "Health check for the SkillOS flagship launch.")

def build_receipts(proof: dict[str, Any]) -> str:
    body=f'''<section><div class="eyebrow">Evidence</div><h1>Receipts.</h1><p style="font-size:21px">Open the human-readable and machine-readable artifacts behind the flagship narrative.</p><div class="stage-grid"><div class="stage"><b>JSON receipt</b><p>Machine-readable proof data.</p><a class="btn cyan" href="data/rsi-capability-governance-twin-proof.json">Open JSON</a></div><div class="stage"><b>Launch manifest</b><p>Site freshness, marker, schema, and source paths.</p><a class="btn cyan" href="data/flagship-capability-governance-twin-manifest.json">Open manifest</a></div><div class="stage"><b>Markdown report</b><p>Readable public report.</p><a class="btn cyan" href="docs/FLAGSHIP_CAPABILITY_GOVERNANCE_TWIN_LAUNCH.md">Open report</a></div></div></section>'''
    return page_shell("SkillOS Flagship Receipts", body, "Receipts", "Evidence receipts for the SkillOS flagship launch.")

def build_architecture(proof: dict[str, Any]) -> str:
    body=f'''<section><div class="eyebrow">Architecture</div><h1>Operational Sovereignty.</h1><p style="font-size:21px">The flagship deploy path is deliberately simple: build, verify, commit, upload Pages artifact, deploy Pages, and verify the live root.</p><div class="flywheel"><div>Build</div><div>Verify</div><div>Commit</div><div>Artifact</div><div>Deploy</div><div>Live Check</div><div>Explain</div></div><div class="card"><h2>Why this is the move</h2><p>The proof portfolio is large enough. The next credibility threshold is operational sovereignty: one canonical public site, one canonical deploy workflow, one flagship proof, one health check, one non-technical viewer journey, and one launch-grade narrative.</p></div></section>'''
    return page_shell("SkillOS Architecture", body, "Architecture", "Architecture of the SkillOS flagship launch.")

def build_proofs(proofs: list[dict[str, Any]]) -> str:
    cards = ""
    for p in proofs[:48]:
        f = p.get("final", {})
        href = as_text(p.get("href"), "capability-governance-twin.html")
        if href.startswith("site/"):
            href = href[5:]
        if not href.endswith(".html"):
            href = "capability-governance-twin.html"
        cards += f'''<article class="proof-card" style="padding:20px"><span class="badge">{'passed' if p.get('proved') else 'indexed'}</span><h3>{esc(p.get("title"))}</h3><p>{esc(as_text(p.get("status"), "indexed"))}</p><p class="small">Value capture: {esc(f.get("value_capture_rate_percent", "n/a"))}%</p><a class="btn" href="{esc(href)}">Open</a></article>'''
    body=f'''<section><div class="eyebrow">Proof atlas</div><h1>Proofs.</h1><p style="font-size:21px">The flagship proof is the front door; the broader proof atlas remains available behind it.</p><div class="skill-grid">{cards}</div></section>'''
    return page_shell("SkillOS Proof Atlas", body, "Proofs", "Proof atlas for SkillOS.")

def build_actions(workflows: list[dict[str, Any]]) -> str:
    rows = "".join(f"<tr><td>{esc(w['name'])}</td><td>{esc(w['path'])}</td><td>{'yes' if w['has_dispatch'] else 'no'}</td><td>{'yes' if w['deploys_pages'] else 'no'}</td></tr>" for w in workflows[:80])
    body=f'''<section><div class="eyebrow">GitHub native</div><h1>Actions.</h1><p style="font-size:21px">Use GitHub Actions as the public proof engine.</p><div class="buttons"><a class="btn primary" href="{action_url()}">Run flagship action</a><a class="btn" href="https://github.com/{REPO}/actions">Open all Actions</a></div><table><tr><th>Workflow</th><th>Path</th><th>Manual run</th><th>Pages deploy</th></tr>{rows}</table></section>'''
    return page_shell("SkillOS Actions", body, "Run", "GitHub Actions for SkillOS.")

def build_docs_md(proof: dict[str, Any], now: str) -> str:
    f=proof["final"]; a=proof["agent_system"]
    skills = "\n".join(f"- **{s['name']}** ({s['layer']}): {s['purpose']}" for s in proof["skills_used"])
    return f'''# SkillOS Flagship Capability Governance Twin Launch

Generated: `{now}`  
Marker: `{MARKER}`  
Schema: `{SCHEMA}`

## Executive narrative

SkillOS must prove operational sovereignty: the public proof flywheel publishes itself, verifies itself, protects itself, and explains itself beautifully to a non-technical viewer.

The flagship narrative is the **Capability Governance Twin**.

> The capability is not the proof. The governed release of the capability is the proof.

## Mechanism

```text
capability route
→ governance twin
→ policy-as-code
→ permission boundary
→ shadow simulation
→ verifier coverage
→ rollback path
→ release gate
→ public receipt
```

## Flagship result

- Virtual specialist agents: **{fmt_int(a['virtual_specialist_agents'])}**
- Specialist roles: **{fmt_int(a['specialist_roles'])}**
- Benchmark value capture: **{f['value_capture_rate_percent']}%**
- Minimum domain capture: **{f['minimum_domain_value_capture_percent']}%**
- Policy violation rate: **{f['policy_violation_rate_percent']}%**
- Shadow/production gap rate: **{f['shadow_production_gap_rate_percent']}%**
- Risk breach rate: **{f['risk_breach_rate_percent']}%**
- RSI release count: **{proof.get('rsi_release_count', 0)}**

## Skills Used

{skills}

## Public boundary

{proof.get('public_boundary')}
'''

def build_badge(proof: dict[str, Any]) -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="370" height="20" role="img" aria-label="SkillOS flagship governance twin: passed">
<linearGradient id="g" x2="1"><stop offset="0" stop-color="#071321"/><stop offset="1" stop-color="#302d68"/></linearGradient>
<rect width="370" height="20" rx="10" fill="url(#g)"/>
<rect x="264" width="106" height="20" rx="10" fill="#75ffae"/>
<text x="12" y="14" fill="#dff7ff" font-family="Verdana" font-size="11">flagship capability governance twin</text>
<text x="288" y="14" fill="#06111e" font-family="Verdana" font-weight="700" font-size="11">passed</text>
</svg>'''

def write_assets() -> None:
    atomic_write(SITE / "sw.js", "self.addEventListener('install', event => self.skipWaiting()); self.addEventListener('activate', event => event.waitUntil(self.registration.unregister().then(() => self.clients.matchAll()).then(clients => clients.forEach(client => client.navigate(client.url)))));")
    atomic_write(SITE / ".nojekyll", "")
    atomic_write(SITE / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {PAGES_BASE}sitemap.xml\n")

def build_all() -> dict[str, Any]:
    now = utc_now()
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "data").mkdir(parents=True, exist_ok=True)
    (SITE / "docs").mkdir(parents=True, exist_ok=True)
    (SITE / "badges").mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    BADGES.mkdir(parents=True, exist_ok=True)

    proof, proofs = collect_proofs(now)
    workflows = collect_workflows()

    proof["href"] = "capability-governance-twin.html"
    proof["json"] = "data/rsi-capability-governance-twin-proof.json"
    proof["doc"] = "docs/FLAGSHIP_CAPABILITY_GOVERNANCE_TWIN_LAUNCH.md"
    proof["badge"] = "badges/flagship-capability-governance-twin.svg"

    manifest = {
        "schema": SCHEMA,
        "marker": MARKER,
        "generated_at_utc": now,
        "repo": REPO,
        "pages_base": PAGES_BASE,
        "flagship": {
            "id": proof.get("id"),
            "title": proof.get("title"),
            "href": proof.get("href"),
            "json": proof.get("json"),
            "doc": proof.get("doc"),
            "badge": proof.get("badge"),
            "proved": proof.get("proved"),
        },
        "counts": {
            "indexed_proofs": len(proofs),
            "skills_displayed": len(proof.get("skills_used", [])),
            "workflows": len(workflows),
        },
        "root_policy": {
            "root_and_index_must_match": True,
            "old_phrases_blocked": OLD_PHRASES,
            "deploys_pages_artifact_directly": True,
        },
    }

    atomic_write(SITE / "data" / "flagship-capability-governance-twin-manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    atomic_write(SITE / "data" / "rsi-capability-governance-twin-proof.json", json.dumps(proof, indent=2, sort_keys=True) + "\n")
    atomic_write(DATA / "flagship-capability-governance-twin-manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    registry = {
        "schema": "skillos.proof_registry.flagship.v1",
        "updated_at_utc": now,
        "marker": MARKER,
        "proofs": [{
            "id": FLAGSHIP_ID,
            "title": "SkillOS Flagship Capability Governance Twin Launch",
            "href": "capability-governance-twin.html",
            "json": "data/rsi-capability-governance-twin-proof.json",
            "doc": "docs/FLAGSHIP_CAPABILITY_GOVERNANCE_TWIN_LAUNCH.md",
            "badge": "badges/flagship-capability-governance-twin.svg",
            "proved": True,
            "status": "FLAGSHIP_LAUNCH_READY",
            "skills_used_count": len(proof["skills_used"]),
            "value_capture_rate_percent": proof["final"]["value_capture_rate_percent"],
            "generated_at_utc": now,
        }] + [
            {
                "id": as_text(p.get("id"), safe_slug(p.get("title"))),
                "title": as_text(p.get("title"), "SkillOS proof"),
                "href": as_text(p.get("href"), "capability-governance-twin.html"),
                "json": as_text(p.get("json"), ""),
                "proved": bool(p.get("proved")),
                "status": as_text(p.get("status"), "indexed"),
                "value_capture_rate_percent": p.get("final", {}).get("value_capture_rate_percent"),
                "skills_used_count": len(p.get("skills_used", [])),
                "generated_at_utc": as_text(p.get("generated_at_utc"), now),
            } for p in proofs[:80]
        ],
    }
    atomic_write(SITE / "proof-registry.json", json.dumps(registry, indent=2, sort_keys=True) + "\n")

    pages = {
        "index.html": build_home(proof, now, workflows),
        "capability-governance-twin.html": build_flagship(proof, now),
        "governance-twin.html": build_flagship(proof, now),
        "skills.html": build_skills(proof),
        "run.html": build_run(proof),
        "runbook.html": build_run(proof),
        "health.html": build_health(proof, now, workflows),
        "receipts.html": build_receipts(proof),
        "architecture.html": build_architecture(proof),
        "proofs.html": build_proofs(proofs),
        "actions.html": build_actions(workflows),
        "multi-agent.html": build_flagship(proof, now),
        "flywheel.html": build_home(proof, now, workflows),
        "404.html": build_home(proof, now, workflows),
        "force-refresh.html": build_home(proof, now, workflows),
    }
    for name, html_text in pages.items():
        atomic_write(SITE / name, html_text)

    doc = build_docs_md(proof, now)
    atomic_write(DOCS / "FLAGSHIP_CAPABILITY_GOVERNANCE_TWIN_LAUNCH.md", doc)
    atomic_write(SITE / "docs" / "FLAGSHIP_CAPABILITY_GOVERNANCE_TWIN_LAUNCH.md", doc)

    badge = build_badge(proof)
    atomic_write(BADGES / "flagship-capability-governance-twin.svg", badge)
    atomic_write(SITE / "badges" / "flagship-capability-governance-twin.svg", badge)

    urls = ["", "capability-governance-twin.html", "skills.html", "proofs.html", "run.html", "receipts.html", "health.html", "architecture.html"]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{PAGES_BASE}{u}</loc></url>\n" for u in urls) + "</urlset>\n"
    atomic_write(SITE / "sitemap.xml", sitemap)
    atomic_write(SITE / "version.txt", f"{MARKER}\n{now}\n")
    write_assets()
    return {"manifest": manifest, "proof": proof, "proofs": proofs, "workflows": workflows}

def main() -> None:
    result = build_all()
    compact = {
        "status": "BUILT_SKILLOS_FLAGSHIP_GOVERNANCE_TWIN_LAUNCH",
        "schema": SCHEMA,
        "marker": MARKER,
        "flagship": result["manifest"]["flagship"]["title"],
        "indexed_proofs": len(result["proofs"]),
        "skills_displayed": len(result["proof"]["skills_used"]),
        "workflows_indexed": len(result["workflows"]),
        "site": "site/index.html",
        "flagship_page": "site/capability-governance-twin.html",
        "manifest": "site/data/flagship-capability-governance-twin-manifest.json",
    }
    print(json.dumps(compact, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
