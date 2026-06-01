#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt, html, json, os, re, tempfile, urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
DATA = ROOT / "data"
DOCS = ROOT / "docs"
BADGES = ROOT / "badges"
WORKFLOWS = ROOT / ".github" / "workflows"
CONTROL_PAGES = {"index.html","proofs.html","actions.html","receipts.html","multi-agent.html","architecture.html","runbook.html","skills.html","health.html","executive.html","flywheel.html","404.html","force-refresh.html"}
SKIP_JSON = {"command-center-manifest.json","command-center-health.json","proof-registry.json","package-lock.json","tsconfig.json"}

PUBLIC_BOUNDARY = ("These are autonomous deterministic benchmark proofs using synthetic/redacted-style public benchmark data and benchmark assumptions. "
"They are not audited customer ROI, live customer adoption, financial advice, investment advice, legal advice, medical advice, employment advice, "
"policy advice, token advice, achieved superintelligence, Kardashev Type II achievement, or guarantees.")

DEFAULT_SKILLS = [
    {"name":"Demand Decomposition","layer":"Coordination","purpose":"Breaks incoming work into testable specialist tasks.","verifier":"Task Consistency Court"},
    {"name":"Capability Routing","layer":"Routing","purpose":"Routes work to the best verified skill or specialist role.","verifier":"Routing Court"},
    {"name":"Verifier Coverage Planning","layer":"Verification","purpose":"Allocates verifier courts to high-value or high-risk decisions.","verifier":"Verifier Capacity Court"},
    {"name":"Risk Veto","layer":"Safety","purpose":"Blocks unsafe or over-claimed actions before release.","verifier":"Risk Court"},
    {"name":"Rollback Planning","layer":"Reliability","purpose":"Requires a safe fallback path before promotion.","verifier":"Rollback Court"},
    {"name":"Incident Replay","layer":"Reliability","purpose":"Replays failures and near misses against candidate updates.","verifier":"Incident Replay Court"},
    {"name":"Provenance Audit","layer":"Trust","purpose":"Binds skills, proofs, receipts, reports, and releases to replayable evidence.","verifier":"Provenance Court"},
    {"name":"Release Gating","layer":"RSI","purpose":"Promotes only validation-improving updates without risk regression.","verifier":"Release Court"},
    {"name":"Executive Receipt Publishing","layer":"Communication","purpose":"Turns machine receipts into readable proof pages.","verifier":"Site Integration Verifier"},
]

def now_iso() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00","Z")

def esc(x: Any) -> str:
    return html.escape("" if x is None else str(x), quote=True)

def slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+","-",s.lower()).strip("-")
    return re.sub(r"-+","-",s) or "proof"

def titleize(s: str) -> str:
    return " ".join(w.capitalize() for w in re.split(r"[-_]+",s) if w)

def atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", dir=str(path.parent)) as f:
        f.write(text); name=f.name
    os.replace(name, path)

def read_json(path: Path) -> Any | None:
    try: return json.loads(path.read_text(encoding="utf-8"))
    except Exception: return None

def num(x: Any, default: float = 0) -> float:
    try:
        if x is None or x == "": return default
        return float(x)
    except Exception: return default

def short(x: Any) -> str:
    v=num(x)
    if v>=1_000_000_000: return f"{v/1_000_000_000:.2f}B"
    if v>=1_000_000: return f"{v/1_000_000:.1f}M"
    if v>=1_000: return f"{v/1_000:.1f}K"
    return str(int(v))

def registry_list(raw: Any) -> list[dict[str,Any]]:
    if isinstance(raw, list): return [x for x in raw if isinstance(x,dict)]
    if isinstance(raw, dict) and isinstance(raw.get("proofs"), list): return [x for x in raw["proofs"] if isinstance(x,dict)]
    return []

def metric(proof: dict[str,Any], *names: str) -> Any:
    for name in names:
        if name in proof: return proof[name]
        for parent in ("final","agent_system","benchmark_public"):
            obj=proof.get(parent)
            if isinstance(obj,dict) and name in obj: return obj[name]
    return None

def normalize(proof: dict[str,Any], source: Path | None = None) -> dict[str,Any]:
    source_name = source.name if source else ""
    pid = proof.get("id") or proof.get("proof_id") or proof.get("slug") or (source_name[:-5] if source_name.endswith(".json") else "")
    title = proof.get("title") or proof.get("proof_type") or proof.get("workflow") or proof.get("name") or titleize(pid)
    pid = slugify(str(pid or title))
    status = str(proof.get("status") or ("PASSED" if proof.get("proved") is True else "NOT_RUN" if proof.get("proved") is None else "FAILED"))
    proved = bool(proof.get("proved") is True or "passed" in status.lower() or "success" in status.lower())
    href = str(proof.get("href") or f"{pid}.html")
    if href.startswith("site/"): href = href[5:]
    j = str(proof.get("json") or f"data/{pid}.json")
    d = str(proof.get("doc") or proof.get("docs") or f"docs/{pid}.md")
    b = str(proof.get("badge") or f"badges/{pid}.svg")
    skills = proof.get("skills_used") if isinstance(proof.get("skills_used"), list) else []
    return {
        "id":pid, "title":str(title), "status":status, "proved":proved, "href":href, "json":j, "doc":d, "badge":b,
        "summary":str(proof.get("summary") or proof.get("safe_interpretation") or proof.get("description") or "Autonomous public SkillOS proof."),
        "generated_at_utc":str(proof.get("generated_at_utc") or proof.get("updated_at_utc") or ""),
        "source":str(source.relative_to(ROOT)) if source and source.exists() else "",
        "virtual_specialist_agents":int(num(metric(proof,"virtual_specialist_agents","agent_count","agents"))),
        "specialist_roles":int(num(metric(proof,"specialist_roles","role_count","roles"))),
        "rsi_release_count": len(metric(proof,"rsi_releases") or []) if isinstance(metric(proof,"rsi_releases"), list) else int(num(metric(proof,"rsi_release_count","rsi_releases"))),
        "locked_holdout_count":int(num(metric(proof,"locked_holdout_count","holdout_count"))),
        "value_capture_rate_percent":num(metric(proof,"value_capture_rate_percent","benchmark_value_capture_rate_percent")),
        "risk_breach_rate_percent":num(metric(proof,"risk_breach_rate_percent")),
        "skills_used_count":len(skills),
        "skills_used":skills,
    }

def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists() and not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        try: dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        except Exception: pass

def collect_proofs() -> list[dict[str,Any]]:
    by_id: dict[str,dict[str,Any]] = {}
    for path in [SITE/"proof-registry.json", DATA/"proof-registry.json"]:
        for entry in registry_list(read_json(path)):
            p=normalize(entry,path); by_id[p["id"]] = {**by_id.get(p["id"],{}), **p}
    for folder in [DATA, SITE/"data"]:
        if not folder.exists(): continue
        for path in sorted(folder.glob("*.json")):
            if path.name in SKIP_JSON: continue
            raw=read_json(path)
            if isinstance(raw, dict):
                if "proofs" in raw and len(raw.keys()) <= 5:
                    for entry in registry_list(raw):
                        p=normalize(entry,path); by_id[p["id"]] = {**by_id.get(p["id"],{}), **p}
                else:
                    p=normalize(raw,path)
                    if path.parent.name == "data": p["json"] = f"data/{path.name}"
                    by_id[p["id"]] = {**by_id.get(p["id"],{}), **p}
            elif isinstance(raw, list):
                for entry in raw:
                    if isinstance(entry,dict):
                        p=normalize(entry,path); by_id[p["id"]] = {**by_id.get(p["id"],{}), **p}
    if SITE.exists():
        for path in sorted(SITE.glob("*.html")):
            if path.name in CONTROL_PAGES: continue
            pid=slugify(path.stem)
            if pid not in by_id:
                by_id[pid] = normalize({"id":pid,"title":titleize(pid),"status":"PAGE_ONLY","href":path.name,"summary":"Existing public proof page."}, path)
            by_id[pid]["href"] = path.name
    for p in by_id.values():
        p["page_exists"] = bool(p.get("href") and (SITE/p["href"]).exists())
        if p.get("json", "").startswith("data/"): copy_if_exists(DATA/Path(p["json"]).name, SITE/"data"/Path(p["json"]).name)
        if p.get("doc", "").startswith("docs/"): copy_if_exists(DOCS/Path(p["doc"]).name, SITE/"docs"/Path(p["doc"]).name)
        if p.get("badge", "").startswith("badges/"): copy_if_exists(BADGES/Path(p["badge"]).name, SITE/"badges"/Path(p["badge"]).name)
    proofs=list(by_id.values())
    proofs.sort(key=lambda p:(0 if p.get("proved") else 1, -int(num(p.get("virtual_specialist_agents"))), -num(p.get("value_capture_rate_percent")), p.get("title","")))
    return proofs

def collect_workflows() -> list[dict[str,Any]]:
    items=[]
    if not WORKFLOWS.exists(): return items
    for path in sorted(list(WORKFLOWS.glob("*.yml"))+list(WORKFLOWS.glob("*.yaml"))):
        text=path.read_text(encoding="utf-8",errors="ignore")
        m=re.search(r"(?m)^\s*name\s*:\s*(.+?)\s*$", text)
        name=(m.group(1).strip().strip("'\"") if m else titleize(path.stem))
        triggers=[t for t in ["workflow_dispatch","push","schedule","workflow_run","pull_request"] if t in text]
        items.append({"name":name,"path":str(path.relative_to(ROOT)),"filename":path.name,"triggers":triggers,"has_manual_run":"workflow_dispatch" in text,"url":f"https://github.com/{os.getenv('GITHUB_REPOSITORY','MontrealAI/skillos')}/actions/workflows/{path.name}","latest_status":"","latest_conclusion":"","latest_event":"","latest_run_at":"","latest_run_url":""})
    return items

def enrich_workflows(workflows: list[dict[str,Any]]) -> None:
    token=os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    repo=os.getenv("GITHUB_REPOSITORY","MontrealAI/skillos")
    if not token: return
    req=urllib.request.Request(f"https://api.github.com/repos/{repo}/actions/runs?per_page=100",headers={"Accept":"application/vnd.github+json","Authorization":f"Bearer {token}","X-GitHub-Api-Version":"2022-11-28"})
    try:
        raw=json.loads(urllib.request.urlopen(req,timeout=20).read().decode("utf-8"))
    except Exception:
        return
    latest={}
    for run in raw.get("workflow_runs",[]):
        if run.get("path") and run["path"] not in latest: latest[run["path"]] = run
    for wf in workflows:
        run=latest.get(wf["path"])
        if not run: continue
        wf["latest_status"]=run.get("status") or ""
        wf["latest_conclusion"]=run.get("conclusion") or ""
        wf["latest_event"]=run.get("event") or ""
        wf["latest_run_at"]=run.get("updated_at") or run.get("created_at") or ""
        wf["latest_run_url"]=run.get("html_url") or ""

def collect_skills(proofs: list[dict[str,Any]]) -> list[dict[str,str]]:
    seen={}
    for p in proofs:
        for s in p.get("skills_used") or []:
            if isinstance(s,dict) and s.get("name"):
                seen.setdefault(str(s["name"]), {"name":str(s["name"]),"layer":str(s.get("layer") or "Skill"),"purpose":str(s.get("purpose") or "Operational skill used by an autonomous proof."),"verifier":str(s.get("verifier") or "Verifier")})
    for s in DEFAULT_SKILLS: seen.setdefault(s["name"],s)
    return sorted(seen.values(), key=lambda s:(s["layer"],s["name"]))

def inventory() -> dict[str,int]:
    return {
        "json_receipts": len(list(DATA.glob("*.json"))) + (len(list((SITE/"data").glob("*.json"))) if (SITE/"data").exists() else 0),
        "markdown_reports": len(list(DOCS.glob("*.md"))) + (len(list((SITE/"docs").glob("*.md"))) if (SITE/"docs").exists() else 0),
        "badges": len(list(BADGES.glob("*.svg"))) + (len(list((SITE/"badges").glob("*.svg"))) if (SITE/"badges").exists() else 0),
        "html_pages": len(list(SITE.glob("*.html"))) if SITE.exists() else 0,
        "workflows": len(list(WORKFLOWS.glob("*.yml"))) + len(list(WORKFLOWS.glob("*.yaml"))) if WORKFLOWS.exists() else 0,
    }

def status_pill(ok: bool, text: str = "") -> str:
    label=text or ("passed" if ok else "indexed")
    cls="passed" if ok else "neutral"
    return f"<span class='pill {cls}'>{esc(label)}</span>"

def proof_href(p: dict[str,Any]) -> str:
    if p.get("page_exists") and p.get("href"): return p["href"]
    if p.get("json"): return p["json"]
    if p.get("doc"): return p["doc"]
    return "#"

def proof_card(p: dict[str,Any]) -> str:
    meta=[]
    if p.get("virtual_specialist_agents"): meta.append(short(p["virtual_specialist_agents"])+" agents")
    if p.get("specialist_roles"): meta.append(short(p["specialist_roles"])+" roles")
    if p.get("locked_holdout_count"): meta.append(short(p["locked_holdout_count"])+" holdout")
    if p.get("rsi_release_count"): meta.append(str(p["rsi_release_count"])+" RSI releases")
    buttons=f"<a class='button' href='{esc(proof_href(p))}'>Open</a>"
    if p.get("json"): buttons += f"<a class='button secondary' href='{esc(p['json'])}'>JSON</a>"
    if p.get("doc"): buttons += f"<a class='button secondary' href='{esc(p['doc'])}'>Report</a>"
    return f"<article class='proof-card'>{status_pill(bool(p.get('proved')), 'passed' if p.get('proved') else p.get('status','indexed'))}<h3>{esc(p['title'])}</h3><p>{esc(p.get('summary',''))[:240]}</p><p class='small'>{esc(' · '.join(meta) or 'public proof artifact')}</p><div class='actions'>{buttons}</div></article>"

def skill_card(s: dict[str,Any]) -> str:
    return f"<article class='skill-card'><div class='skill-layer'>{esc(s.get('layer','Skill'))}</div><h3>{esc(s.get('name',''))}</h3><p>{esc(s.get('purpose',''))}</p><p class='small'><strong>Verifier:</strong> {esc(s.get('verifier','Verifier'))}</p></article>"

def layout(title: str, active: str, body: str, generated_at: str) -> str:
    repo=os.getenv("GITHUB_REPOSITORY","MontrealAI/skillos")
    nav=[("Home","index.html"),("Executive","executive.html"),("Proofs","proofs.html"),("Actions","actions.html"),("Skills","skills.html"),("Multi-Agent","multi-agent.html"),("Receipts","receipts.html"),("Health","health.html"),("Run / Regenerate","runbook.html"),("GitHub",f"https://github.com/{repo}")]
    nav_html="".join(f"<a class='{ 'active' if n==active else '' }' href='{h}'>{n}</a>" for n,h in nav)
    css = """
:root{--bg:#07131f;--panel:rgba(255,255,255,.075);--panel2:rgba(255,255,255,.11);--line:rgba(255,255,255,.17);--text:#f4fbff;--muted:#bdd0df;--cyan:#86f8ff;--green:#76ffad;--gold:#ffd66b;--bad:#ff7676}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 82% 4%,#494a8f 0,transparent 30%),radial-gradient(circle at 2% 12%,#08687b 0,transparent 27%),linear-gradient(135deg,#06131f,#14233b 58%,#262a5c);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Arial,sans-serif}body:before{content:"";position:fixed;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:38px 38px;mask-image:linear-gradient(to bottom,rgba(0,0,0,.95),rgba(0,0,0,.08));pointer-events:none}a{color:var(--cyan);text-decoration:none}a:hover{text-decoration:underline}nav{position:sticky;top:0;z-index:20;background:rgba(5,16,27,.88);border-bottom:1px solid var(--line);backdrop-filter:blur(18px);display:flex;align-items:center;justify-content:space-between;padding:13px 20px}.brand{font-weight:950;color:var(--cyan)}.links{display:flex;gap:15px;flex-wrap:wrap;justify-content:flex-end}.links a{color:#d7e5f0;font-weight:850;font-size:14px}.links a.active{color:var(--cyan)}main{max-width:1280px;margin:0 auto;padding:50px 24px 90px;position:relative}h1{font-size:clamp(54px,8.6vw,118px);line-height:.86;letter-spacing:-.085em;margin:12px 0 20px}h2{font-size:clamp(30px,4vw,58px);line-height:.95;letter-spacing:-.055em;margin:46px 0 18px}h3{letter-spacing:-.025em}p{color:var(--muted);font-size:18px;line-height:1.55}.eyebrow{color:var(--gold);text-transform:uppercase;font-size:12px;font-weight:950;letter-spacing:.18em}.hero{display:grid;grid-template-columns:1.12fr .88fr;gap:28px;align-items:center;margin-bottom:32px}.card,.metric,.proof-card,.skill-card{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:28px;padding:24px;box-shadow:0 24px 85px rgba(0,0,0,.23), inset 0 1px 0 rgba(255,255,255,.10)}.metric strong{display:block;color:var(--green);font-size:36px;line-height:1}.metric span{color:var(--muted)}.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.grid2{display:grid;grid-template-columns:repeat(2,1fr);gap:16px}.proof-card h3{font-size:24px;margin:12px 0 8px}.proof-card p{font-size:15px}.actions{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}.button{display:inline-block;padding:11px 15px;border-radius:999px;background:var(--cyan);color:#06131f;font-weight:950}.button.secondary{background:rgba(255,255,255,.08);border:1px solid var(--line);color:var(--text)}.button.gold{background:linear-gradient(90deg,var(--gold),#fff0a8);color:#06131f;box-shadow:0 10px 34px rgba(255,214,107,.22)}.lux{background:linear-gradient(135deg,rgba(255,214,107,.18),rgba(134,248,255,.10),rgba(255,255,255,.06));border:1px solid rgba(255,214,107,.24)}.seal{font-size:13px;letter-spacing:.18em;text-transform:uppercase;color:var(--gold);font-weight:950}.orb{height:220px;border-radius:28px;background:radial-gradient(circle at 40% 38%,rgba(255,214,107,.45),transparent 8%),radial-gradient(circle at 60% 45%,rgba(134,248,255,.35),transparent 10%),radial-gradient(circle at 50% 55%,rgba(118,255,173,.20),transparent 15%),linear-gradient(135deg,rgba(255,255,255,.10),rgba(255,255,255,.02));border:1px solid var(--line);position:relative;overflow:hidden}.orb:before{content:"";position:absolute;inset:25px;border-radius:50%;border:1px solid rgba(255,255,255,.18);box-shadow:0 0 80px rgba(134,248,255,.18)}.pill{display:inline-block;border-radius:999px;padding:5px 10px;font-weight:950;font-size:12px;text-transform:uppercase;letter-spacing:.06em}.pill.passed{background:rgba(118,255,173,.18);color:var(--green)}.pill.failed{background:rgba(255,118,118,.18);color:var(--bad)}.pill.neutral{background:rgba(255,214,107,.16);color:var(--gold)}.quote{font-size:clamp(25px,3.1vw,44px);line-height:1.06;letter-spacing:-.045em;color:var(--text)}table{width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:20px;overflow:hidden}th,td{padding:13px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{font-size:12px;text-transform:uppercase;letter-spacing:.10em;color:var(--muted)}code{background:rgba(255,255,255,.08);padding:2px 6px;border-radius:8px;color:#e6fbff}pre{white-space:pre-wrap;background:rgba(0,0,0,.28);border:1px solid var(--line);padding:18px;border-radius:18px;overflow:auto}.skill-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.skill-card h3{font-size:21px;margin:8px 0}.skill-card p{font-size:15px;margin:0 0 12px}.skill-layer{display:inline-block;border:1px solid rgba(134,248,255,.35);color:var(--cyan);border-radius:999px;padding:5px 9px;font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.08em}.notice{border-left:4px solid var(--gold);background:rgba(255,214,107,.08);border-radius:16px;padding:16px 18px;margin:24px 0;color:var(--muted)}.small{font-size:13px;color:var(--muted)}.fresh{font-size:clamp(24px,2.6vw,38px);color:var(--green);font-weight:950;letter-spacing:-.03em}footer{max-width:1280px;margin:0 auto;padding:30px 24px 70px;color:var(--muted)}@media(max-width:980px){.hero,.grid4,.grid3,.grid2,.skill-grid{grid-template-columns:1fr}nav{align-items:flex-start;gap:12px;flex-direction:column}}
"""
    return f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><meta http-equiv='Cache-Control' content='no-store, no-cache, must-revalidate'><meta http-equiv='Pragma' content='no-cache'><meta http-equiv='Expires' content='0'><title>{esc(title)}</title><style>{css}</style></head><body><nav><div class='brand'>SkillOS Public Command Center v3 · Autonomous Proof Atlas</div><div class='links'>{nav_html}</div></nav><main>{body}</main><footer><div class='notice'><strong>Public boundary:</strong> {esc(PUBLIC_BOUNDARY)}</div><p class='small'>Generated autonomously at {esc(generated_at)}. Verify freshness in <a href='data/command-center-manifest.json'>data/command-center-manifest.json</a>.</p></footer></body></html>"

def build_pages(proofs, workflows, skills, inv, generated_at, latest):
    passed=sum(1 for p in proofs if p.get("proved"))
    total_agents=sum(int(num(p.get("virtual_specialist_agents"))) for p in proofs)
    proof_cards="".join(proof_card(p) for p in proofs[:12]) or "<div class='card'><p>No proof receipts found yet. Run a proof workflow, then refresh this Command Center.</p></div>"
    index_body=f"""
<section class='hero'><div><div class='eyebrow'>MONTREAL.AI / SKILLOS</div><h1>Public SkillOS Command Center</h1><p>Iconic, GitHub-native, self-refreshing proof atlas for every SkillOS proof, run, receipt, report, badge, workflow, and Skills Used display.</p><div class='actions'><a class='button gold' href='proofs.html'>View all proofs</a><a class='button' href='actions.html'>Run / regenerate</a><a class='button secondary' href='receipts.html'>Inspect receipts</a></div></div><div class='card'><div class='eyebrow'>Live freshness</div><div class='fresh'>Updated {esc(latest)}</div><p>Autonomously regenerated from GitHub workflows, proof JSON receipts, Markdown reports, badges, visual proof pages, and latest run metadata when available.</p><p>Repository: <a href='https://github.com/{esc(os.getenv("GITHUB_REPOSITORY","MontrealAI/skillos"))}'>{esc(os.getenv("GITHUB_REPOSITORY","MontrealAI/skillos"))}</a></p></div></section>
<section class='card'><div class='eyebrow'>Core thesis</div><div class='quote'>Every job can become a reusable skill. Every verified skill can strengthen the whole network. One agent learns; the system can route that learning everywhere — turning execution into compounding capability.</div><p>SkillOS makes the mechanism public and testable: work → traces → skills → verification → release → routing upgrade → compounding capability.</p></section>
<section class='grid4'><div class='metric'><strong>{len(proofs)}</strong><span>indexed proofs and pages</span></div><div class='metric'><strong>{passed}</strong><span>passed / proved receipts</span></div><div class='metric'><strong>{len(workflows)}</strong><span>GitHub workflows</span></div><div class='metric'><strong>{len(skills)}</strong><span>skills surfaced</span></div></section>
<section class='grid4'><div class='metric'><strong>{short(total_agents)}</strong><span>declared specialist agents across receipts</span></div><div class='metric'><strong>{inv["json_receipts"]}</strong><span>JSON receipt files</span></div><div class='metric'><strong>{inv["markdown_reports"]}</strong><span>Markdown reports</span></div><div class='metric'><strong>{inv["badges"]}</strong><span>badges</span></div></section>
<h2>Featured proof library</h2><div class='grid3'>{proof_cards}</div>
<h2>How to see the agents</h2><div class='grid3'><div class='card'><h3>1. Open a proof page</h3><p>The visual page shows the mechanism, metrics, baselines, release history, and boundary.</p></div><div class='card'><h3>2. Read Skills Used</h3><p>Skills cards show what the agent system did: routing, verification, risk vetoes, rollback, policy checks, and release gates.</p></div><div class='card'><h3>3. Open the receipt</h3><p>The JSON receipt is the machine-readable evidence that the proof generated and verified.</p></div></div>
<h2>Operational skill stack</h2><div class='skill-grid'>{"".join(skill_card(s) for s in skills[:18])}</div>
<h2>Run or regenerate</h2><div class='grid3'><div class='card'><div class='eyebrow'>Run one proof</div><p>Open <a href='actions.html'>Actions</a>, choose a proof workflow, then click <strong>Run workflow</strong>.</p></div><div class='card'><div class='eyebrow'>Refresh the hub</div><p>Run <strong>SkillOS Command Center Autopublisher v3</strong>. It rebuilds this site and deploys GitHub Pages directly.</p></div><div class='card'><div class='eyebrow'>Verify freshness</div><p>Open <a href='data/command-center-manifest.json'>the manifest</a> and compare its timestamp to this page.</p></div></div>
"""
    atomic(SITE/"index.html", layout("SkillOS Public Command Center v3","Home",index_body,generated_at))
    proof_rows="".join(f"<tr><td>{status_pill(bool(p.get('proved')), 'passed' if p.get('proved') else p.get('status','indexed'))}</td><td><a href='{esc(proof_href(p))}'><strong>{esc(p['title'])}</strong></a><br><span class='small'>{esc(p.get('summary',''))[:180]}</span></td><td>{short(p.get('virtual_specialist_agents',0))}</td><td>{short(p.get('specialist_roles',0))}</td><td>{p.get('rsi_release_count',0)}</td><td>{p.get('value_capture_rate_percent',0)}%</td><td>{('<a href='+esc(p['json'])+'>JSON</a>') if p.get('json') else ''}</td><td>{('<a href='+esc(p['doc'])+'>Report</a>') if p.get('doc') else ''}</td></tr>" for p in proofs)
    atomic(SITE/"proofs.html", layout("SkillOS Proof Library","Proofs",f"<h1>Proof Library</h1><p>Every indexed proof, receipt, report, badge, and visual page discovered by the autonomous Command Center builder.</p><table><thead><tr><th>Status</th><th>Proof</th><th>Agents</th><th>Roles</th><th>RSI</th><th>Value</th><th>JSON</th><th>Report</th></tr></thead><tbody>{proof_rows}</tbody></table>",generated_at))
    action_rows=""
    for w in workflows:
        status=w.get("latest_conclusion") or w.get("latest_status") or "available"
        pill = f"<span class='pill {'failed' if status in ('failure','cancelled','timed_out') else 'passed' if status=='success' else 'neutral'}'>{esc(status)}</span>"
        latest=f"<a href='{esc(w.get('latest_run_url',''))}'>{esc(w.get('latest_run_at',''))}</a>" if w.get("latest_run_url") else esc(w.get("latest_run_at",""))
        action_rows += f"<tr><td><a href='{esc(w['url'])}'><strong>{esc(w['name'])}</strong></a><br><span class='small'>{esc(w['path'])}</span></td><td>{pill}</td><td>{esc(', '.join(w.get('triggers',[])))}</td><td>{'yes' if w.get('has_manual_run') else 'no'}</td><td>{latest}</td></tr>"
    atomic(SITE/"actions.html", layout("SkillOS Actions","Actions",f"<h1>Run / Regenerate</h1><p>Use this page to find every autonomous GitHub workflow. The Command Center v3 workflow is the canonical way to refresh and deploy the public hub.</p><div class='notice'><strong>Recommended:</strong> open <code>SkillOS Command Center Autopublisher v3</code>, click <code>Run workflow</code>, set <code>publish_to_repo=true</code>, <code>deploy_pages=true</code>, and <code>force_rebuild=true</code>.</div><table><thead><tr><th>Workflow</th><th>Status</th><th>Triggers</th><th>Manual</th><th>Latest run</th></tr></thead><tbody>{action_rows}</tbody></table>",generated_at))
    receipt_cards="".join(f"<article class='proof-card'><h3>{esc(p['title'])}</h3><p class='small'>Machine-readable proof evidence and report.</p><div class='actions'>{('<a class=button href='+esc(p['json'])+'>JSON</a>') if p.get('json') else ''}{('<a class=\"button secondary\" href='+esc(p['doc'])+'>Report</a>') if p.get('doc') else ''}{('<a class=\"button secondary\" href='+esc(p['badge'])+'>Badge</a>') if p.get('badge') else ''}</div></article>" for p in proofs if p.get("json") or p.get("doc") or p.get("badge"))
    atomic(SITE/"receipts.html", layout("SkillOS Receipts","Receipts",f"<h1>Receipts</h1><p>Machine-readable proof receipts, Markdown reports, and badges.</p><div class='grid3'>{receipt_cards}</div>",generated_at))
    atomic(SITE/"multi-agent.html", layout("SkillOS Multi-Agent System","Multi-Agent",f"<h1>Multi-Agent System</h1><p>The agents are represented operationally: specialist roles, skills, verifier courts, routing systems, risk vetoes, rollback plans, release gates, and public receipts.</p><section class='grid4'><div class='metric'><strong>{short(total_agents)}</strong><span>declared specialist agents across receipts</span></div><div class='metric'><strong>{len(skills)}</strong><span>skills surfaced</span></div><div class='metric'><strong>{len(proofs)}</strong><span>proofs indexed</span></div><div class='metric'><strong>RSI</strong><span>validation-gated release loop</span></div></section><div class='card'><div class='quote'>Many agents are not the moat. Verified skill compounding is the moat.</div><p>SkillOS turns work into traces, traces into reusable skills, skills into verified releases, and verified releases into better future routing.</p></div><h2>Skills Used across the network</h2><div class='skill-grid'>{"".join(skill_card(s) for s in skills)}</div>",generated_at))
    atomic(SITE/"architecture.html", layout("SkillOS Architecture","Architecture","<h1>Architecture</h1><p>The public Command Center is a GitHub-native proof and publication layer.</p><pre>Proof workflow\n  → deterministic benchmark\n  → JSON receipt\n  → Markdown report\n  → badge\n  → visual proof page\n  → proof registry\n  → Command Center Autopublisher v3\n  → GitHub Pages deployment</pre><h2>SkillOS flywheel</h2><pre>work\n→ trace\n→ candidate skill\n→ verifier court\n→ risk / policy / rollback checks\n→ signed release\n→ routing upgrade\n→ better future work\n→ stronger skill network</pre>",generated_at))
    atomic(SITE/"runbook.html", layout("SkillOS Runbook","Run / Regenerate","<h1>Runbook</h1><p>Non-technical instructions for keeping the public SkillOS Command Center fresh.</p><div class='grid3'><div class='card'><div class='eyebrow'>Step 1</div><h3>Open GitHub Actions</h3><p>Go to the repository Actions tab and select <strong>SkillOS Command Center Autopublisher v3</strong>.</p></div><div class='card'><div class='eyebrow'>Step 2</div><h3>Run workflow</h3><p>Click <strong>Run workflow</strong>. Use <code>publish_to_repo=true</code>, <code>deploy_pages=true</code>, and <code>force_rebuild=true</code>.</p></div><div class='card'><div class='eyebrow'>Step 3</div><h3>Verify the site</h3><p>Wait for the green check, then open the manifest and confirm the freshness timestamp changed.</p></div></div><h2>If you still see the old site</h2><pre>1. Wait 60-120 seconds after the green deployment.\n2. Hard refresh the browser.\n3. Open: https://montrealai.github.io/skillos/?v=latest\n4. Open: https://montrealai.github.io/skillos/data/command-center-manifest.json\n5. Confirm the workflow used deploy_pages=true.</pre>",generated_at))
    atomic(SITE/"404.html", layout("SkillOS Page Not Found","Home","<h1>Page not found</h1><p>Return to the <a href='index.html'>SkillOS Public Command Center</a>.</p>",generated_at))
    atomic(SITE/"force-refresh.html", f"<!doctype html><html><head><meta charset='utf-8'><meta http-equiv='refresh' content='0; url=index.html?v={generated_at.replace(':','').replace('-','')}'><title>Refreshing SkillOS</title></head><body><p>Refreshing SkillOS Command Center…</p></body></html>")
    # Generate elegant detail pages for receipts that do not already have a visual proof page.
    (SITE/"proofs").mkdir(exist_ok=True)
    for p in proofs:
        if str(p.get("href","")).startswith("proofs/"):
            atomic(SITE/p["href"], proof_detail_page(p, generated_at))
    # Additional executive, skills, flywheel, and health pages for non-technical users.
    atomic(SITE/"executive.html", layout("SkillOS Executive Briefing","Executive", f"<section class='hero'><div><div class='eyebrow'>Executive briefing</div><h1>SkillOS turns work into compounding capability.</h1><p>Every completed job can produce a trace. Every trace can become a verified skill. Every verified skill can improve future routing across a large multi-agent network.</p></div><div class='card lux'><div class='orb'></div><p class='small'>A prestigious, public-facing summary for viewers who want the meaning before the machinery.</p></div></section><section class='card'><div class='quote'>One agent learns. The network levels up.</div><p>SkillOS is a public proof system for validation-gated recursive skill improvement. The Command Center shows proofs, receipts, workflows, Skills Used, and regeneration links in one place.</p></section>", generated_at))
    atomic(SITE/"skills.html", layout("SkillOS Skills Used","Skills", f"<h1>Skills Used</h1><p>These cards explain the operational skills surfaced across proof receipts. They are the most user-friendly way to see the agent system.</p><div class='skill-grid'>{''.join(skill_card(s) for s in skills)}</div>", generated_at))
    atomic(SITE/"flywheel.html", layout("SkillOS Flywheel","Architecture", "<h1>SkillOS Flywheel</h1><div class='card lux'><div class='quote'>work → trace → skill → verification → release → routing upgrade → compounding capability</div></div><p>The flywheel is operational when proof workflows generate receipts, receipts generate pages, pages update the hub, and the hub makes regeneration easy for viewers.</p>", generated_at))
    atomic(SITE/"health.html", layout("SkillOS Health","Health", f"<h1>Command Center Health</h1><section class='grid4'><div class='metric'><strong>{len(proofs)}</strong><span>proofs indexed</span></div><div class='metric'><strong>{len(workflows)}</strong><span>workflows indexed</span></div><div class='metric'><strong>{len(skills)}</strong><span>skills surfaced</span></div><div class='metric'><strong>{esc(latest)}</strong><span>latest signal</span></div></section><p>Machine-readable health: <a href='data/command-center-health.json'>command-center-health.json</a></p>", generated_at))


def proof_detail_page(p: dict[str,Any], generated_at: str) -> str:
    skills = p.get("skills_used") or DEFAULT_SKILLS
    meta = f"""<section class='hero'><div><div class='eyebrow'>SkillOS Proof Detail</div><h1>{esc(p['title'])}</h1><p>{esc(p.get('summary','Autonomous SkillOS proof.'))}</p><div class='actions'>{('<a class=button href=../'+esc(p['json'])+'>Open JSON receipt</a>') if p.get('json') else ''}{('<a class="button secondary" href=../'+esc(p['doc'])+'>Open report</a>') if p.get('doc') else ''}<a class='button secondary' href='../proofs.html'>Back to proof library</a></div></div><div class='card lux'><div class='seal'>Autonomous proof receipt</div><div class='quote'>{'Passed' if p.get('proved') else esc(p.get('status','Indexed'))}</div><p class='small'>Agents: {short(p.get('virtual_specialist_agents',0))} · Roles: {short(p.get('specialist_roles',0))} · RSI releases: {p.get('rsi_release_count',0)} · Value capture: {p.get('value_capture_rate_percent',0)}%</p></div></section>"""
    skill_html = "".join(skill_card(s) for s in skills if isinstance(s,dict))
    body = meta + f"<section class='card'><div class='eyebrow'>How to read this proof</div><div class='quote'>The visual page explains the result. The JSON receipt is the machine-readable evidence. The Skills Used cards explain what the agent system did.</div></section><h2>Skills Used</h2><div class='skill-grid'>{skill_html}</div>"
    return layout(str(p['title']), "Proofs", body, generated_at).replace("href='index.html'","href='../index.html'").replace("href='proofs.html'","href='../proofs.html'").replace("href='actions.html'","href='../actions.html'").replace("href='multi-agent.html'","href='../multi-agent.html'").replace("href='receipts.html'","href='../receipts.html'").replace("href='architecture.html'","href='../architecture.html'").replace("href='runbook.html'","href='../runbook.html'").replace("href='skills.html'","href='../skills.html'").replace("href='health.html'","href='../health.html'").replace("href='executive.html'","href='../executive.html'")

def main() -> None:
    generated_at=now_iso()
    SITE.mkdir(parents=True,exist_ok=True); (SITE/"data").mkdir(exist_ok=True); (SITE/"docs").mkdir(exist_ok=True); (SITE/"badges").mkdir(exist_ok=True)
    proofs=collect_proofs()
    for p in proofs:
        href = str(p.get("href", ""))
        local = SITE / href if href else SITE / "__missing__"
        if not href.endswith(".html") or not local.exists():
            p["href"] = f"proofs/{p['id']}.html"
            p["page_exists"] = True
            p["generated_detail_page"] = True
    workflows=collect_workflows(); enrich_workflows(workflows)
    skills=collect_skills(proofs)
    inv=inventory()
    stamps=[generated_at]+[p.get("generated_at_utc","") for p in proofs if p.get("generated_at_utc")]+[w.get("latest_run_at","") for w in workflows if w.get("latest_run_at")]
    latest=max(stamps)
    manifest={"schema":"skillos.command_center.v3","generated_at_utc":generated_at,"site_latest_signal_utc":latest,"repository":os.getenv("GITHUB_REPOSITORY","MontrealAI/skillos"),"counts":{"proofs_indexed":len(proofs),"proofs_passed":sum(1 for p in proofs if p.get("proved")),"workflows_indexed":len(workflows),"manual_workflows":sum(1 for w in workflows if w.get("has_manual_run")),"skills_surfaced":len(skills)},"inventory":inv,"public_boundary":PUBLIC_BOUNDARY,"proof_ids":[p["id"] for p in proofs],"workflow_files":[w["path"] for w in workflows],"skills":skills}
    build_pages(proofs,workflows,skills,inv,generated_at,latest)
    registry={"updated_at_utc":generated_at,"proofs":[{k:v for k,v in p.items() if k!="skills_used"} for p in proofs]}
    atomic(SITE/"proof-registry.json", json.dumps(registry,indent=2,sort_keys=True)+"\n")
    atomic(SITE/"data/command-center-manifest.json", json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    health={"status":"fresh","generated_at_utc":generated_at,"proofs_indexed":len(proofs),"workflows_indexed":len(workflows),"skills_surfaced":len(skills),"site_files":sorted(str(p.relative_to(SITE)) for p in SITE.rglob("*") if p.is_file())}
    atomic(SITE/"data/command-center-health.json", json.dumps(health,indent=2,sort_keys=True)+"\n")
    svg="<svg xmlns='http://www.w3.org/2000/svg' width='360' height='20' role='img' aria-label='SkillOS command center fresh'><rect width='360' height='20' rx='10' fill='#14233a'/><rect x='230' width='130' height='20' rx='10' fill='#2bb673'/><text x='10' y='14' fill='#dff7ff' font-family='Verdana' font-size='11'>SkillOS command center</text><text x='244' y='14' fill='#fff' font-family='Verdana' font-size='11'>fresh v3</text></svg>"
    atomic(BADGES/"command-center-fresh.svg", svg); atomic(SITE/"badges/command-center-fresh.svg", svg)
    atomic(SITE/".nojekyll",""); atomic(SITE/"version.txt",generated_at+"\n"); atomic(SITE/"robots.txt","User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n")
    urls=["https://montrealai.github.io/skillos/"]+[f"https://montrealai.github.io/skillos/{x}" for x in ["executive.html","proofs.html","actions.html","skills.html","receipts.html","multi-agent.html","architecture.html","flywheel.html","health.html","runbook.html"]]
    urls += [f"https://montrealai.github.io/skillos/{p['href']}" for p in proofs if p.get("href","").endswith(".html")]
    atomic(SITE/"sitemap.xml", "<?xml version='1.0' encoding='UTF-8'?>\n<urlset xmlns='http://www.sitemaps.org/schemas/sitemap/0.9'>\n"+"\n".join(f"  <url><loc>{esc(u)}</loc></url>" for u in sorted(set(urls)))+"\n</urlset>\n")
    DOCS.mkdir(parents=True, exist_ok=True)
    atomic(DOCS/"SKILLOS_PUBLIC_COMMAND_CENTER_V3.md", f"# SkillOS Public Command Center v3\n\nGenerated: `{generated_at}`\n\nRun `SkillOS Command Center Autopublisher v3` with `publish_to_repo=true`, `deploy_pages=true`, and `force_rebuild=true`.\n\n## Manifest\n\n```json\n{json.dumps(manifest, indent=2, sort_keys=True)}\n```\n\n## Boundary\n\n{PUBLIC_BOUNDARY}\n")
    print(json.dumps({"status":"BUILT_SKILLOS_COMMAND_CENTER_V3","generated_at_utc":generated_at,"proofs_indexed":len(proofs),"workflows_indexed":len(workflows),"skills_surfaced":len(skills),"site_latest_signal_utc":latest},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
