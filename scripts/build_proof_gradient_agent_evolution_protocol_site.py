#!/usr/bin/env python3
import argparse, html, json, os, re, shutil, subprocess
from datetime import datetime, timezone
from pathlib import Path

PROOF_ID = "proof-gradient-agent-evolution-protocol"
TITLE = "Proof Gradient · The Agent Evolution Protocol"
MARKER = "SKILLOS_PROOF_GRADIENT_COMMAND_CENTER_V1"
ROOT_TITLE = "Public SkillOS Command Center"
BANNED_ROOT_TITLE_PHRASES = ["Autonomous Proof Command Center", "SkillOS Proof Command Center", "Capability Governance Twin"]

def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def git(cmd, default="unknown"):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode().strip() or default
    except Exception:
        return default

def as_text(x, default=""):
    if x is None:
        return default
    if isinstance(x, str):
        return x
    if isinstance(x, (int, float, bool)):
        return str(x)
    if isinstance(x, dict):
        for k in ("title", "name", "id", "proof_id", "label", "value", "status"):
            if k in x:
                return as_text(x[k], default)
        return json.dumps(x, sort_keys=True)[:140]
    if isinstance(x, list):
        return ", ".join(as_text(i) for i in x[:4])
    return default

def slugify(x):
    text = as_text(x, "proof")
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:96] or "proof"

def esc(x):
    return html.escape(as_text(x), quote=True)

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def proof_status(raw):
    s = as_text(raw.get("status") or raw.get("result") or raw.get("proof_status") or "unknown").lower()
    if "pass" in s or "prove" in s or "success" in s:
        return "PASSED"
    if "fail" in s or "error" in s:
        return "FAILED"
    return "NOT RUN YET"

def normalize_proof(path, raw):
    if isinstance(raw, list):
        return None
    if not isinstance(raw, dict):
        return None
    title = as_text(raw.get("title") or raw.get("name") or raw.get("proof_title") or path.stem.replace("_", " ").replace("-", " ").title())
    pid = as_text(raw.get("id") or raw.get("proof_id") or raw.get("slug") or slugify(title))
    slug = slugify(pid or title)
    metrics = raw.get("summary_metrics") if isinstance(raw.get("summary_metrics"), dict) else {}
    skills = raw.get("skills_used") if isinstance(raw.get("skills_used"), list) else []
    return {
        "id": pid,
        "slug": slug,
        "title": title,
        "status": proof_status(raw),
        "source": str(path),
        "href": f"proofs/{slug}.html" if slug != PROOF_ID else f"{PROOF_ID}.html",
        "json": f"data/proofs/{slug}.json" if slug != PROOF_ID else f"data/{PROOF_ID}.json",
        "summary": as_text(raw.get("thesis") or raw.get("summary") or raw.get("description") or "Generated public proof receipt."),
        "metrics": metrics,
        "skills_used": skills,
        "raw": raw,
    }

def collect_proofs():
    files = []
    for pattern in ["data/*.json", "site/data/*.json", "proof-registry.json", "site/proof-registry.json"]:
        files.extend(Path(".").glob(pattern))
    proofs = []
    seen = set()
    for path in files:
        if "skills_used" in path.name:
            continue
        raw = read_json(path)
        if raw is None:
            continue
        candidates = []
        if isinstance(raw, dict) and isinstance(raw.get("proofs"), list):
            candidates = raw.get("proofs")
        elif isinstance(raw, list):
            candidates = raw
        else:
            candidates = [raw]
        for i, item in enumerate(candidates):
            proof = normalize_proof(path, item)
            if not proof:
                continue
            key = proof["slug"]
            if key in seen:
                continue
            seen.add(key)
            proofs.append(proof)
    if PROOF_ID not in seen:
        raw = read_json(Path("data") / f"{PROOF_ID}.json")
        if raw:
            proofs.insert(0, normalize_proof(Path("data") / f"{PROOF_ID}.json", raw))
    proofs.sort(key=lambda p: (0 if p["slug"] == PROOF_ID else 1, p["status"] != "PASSED", p["title"].lower()))
    return proofs

def collect_workflows():
    rows = []
    for p in sorted(Path(".github/workflows").glob("*.y*ml")):
        text = p.read_text(encoding="utf-8", errors="ignore")
        name = p.stem.replace("-", " ").title()
        m = re.search(r"^name:\s*(.+)$", text, re.M)
        if m:
            name = m.group(1).strip().strip('"\'')
        rows.append({"name": name, "path": str(p), "dispatch": "workflow_dispatch" in text, "pages": "deploy-pages" in text, "proof_gradient": PROOF_ID in text or "Proof Gradient" in text})
    return rows

def metric(raw, key, default="—"):
    v = raw.get("summary_metrics", {}).get(key) if isinstance(raw.get("summary_metrics"), dict) else None
    if v is None:
        return default
    if isinstance(v, float):
        if "rate" in key:
            return f"{v:.1%}"
        return f"{v:,.2f}"
    if isinstance(v, int):
        return f"{v:,}"
    return as_text(v, default)

def chart_line(points, width=720, height=260, key="proof_gradient_value_capture"):
    vals = [float(p.get(key, 0)) for p in points]
    if not vals:
        vals = [0, 1]
    lo, hi = min(vals), max(vals)
    if abs(hi - lo) < 1e-9:
        hi = lo + 1
    xs, ys = [], []
    pad = 34
    for i, v in enumerate(vals):
        x = pad + (width - 2*pad) * i / max(1, len(vals)-1)
        y = height - pad - (height - 2*pad) * (v - lo) / (hi - lo)
        xs.append(x); ys.append(y)
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    area = f"{xs[0]:.1f},{height-pad:.1f} " + d + f" {xs[-1]:.1f},{height-pad:.1f}"
    dots = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#8affc1"/>' for x, y in zip(xs, ys))
    labels = "".join(f'<text x="{x:.1f}" y="{height-10}" text-anchor="middle" class="svg-label">v{points[i].get("release", i)}</text>' for i, x in enumerate(xs) if i % max(1, len(xs)//8) == 0)
    return f'''<svg viewBox="0 0 {width} {height}" class="chart" role="img" aria-label="Proof Gradient release curve">
      <defs><linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#74ffb8" stop-opacity=".34"/><stop offset="1" stop-color="#74ffb8" stop-opacity="0"/></linearGradient></defs>
      <line x1="{pad}" y1="{height-pad}" x2="{width-pad}" y2="{height-pad}" class="axis"/><line x1="{pad}" y1="{pad}" x2="{pad}" y2="{height-pad}" class="axis"/>
      <polygon points="{area}" fill="url(#area)"/>
      <polyline points="{d}" fill="none" stroke="#76ffd6" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
      {dots}{labels}
    </svg>'''

def chart_bars(baselines, width=720, height=300):
    vals = [float(b.get("success_rate", 0)) for b in baselines]
    mx = max(vals) if vals else 1
    pad = 40; gap = 18
    barw = (width - 2*pad - gap*(len(vals)-1)) / max(1, len(vals))
    rects = []
    for i, b in enumerate(baselines):
        v = float(b.get("success_rate", 0)); h = (height - 2*pad) * v / max(0.01, mx)
        x = pad + i*(barw+gap); y = height-pad-h
        name = as_text(b.get("mode")).replace("_", " ")
        rects.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{barw:.1f}" height="{h:.1f}" rx="10" fill="url(#bar{i})"/><text x="{x+barw/2:.1f}" y="{y-8:.1f}" text-anchor="middle" class="svg-value">{v:.1%}</text><text x="{x+barw/2:.1f}" y="{height-12}" text-anchor="middle" class="svg-label">{esc(name)}</text><linearGradient id="bar{i}" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#8affc1"/><stop offset="1" stop-color="#7cf7ff" stop-opacity=".45"/></linearGradient>')
    return f'''<svg viewBox="0 0 {width} {height}" class="chart" role="img" aria-label="Baseline comparison">
      <defs>{''.join('' for _ in [])}</defs>
      <line x1="{pad}" y1="{height-pad}" x2="{width-pad}" y2="{height-pad}" class="axis"/>
      {''.join(rects)}
    </svg>'''

def skill_cards(skills):
    cards = []
    for i, s in enumerate(skills):
        cards.append(f'''<article class="skill-card">
          <div class="skill-index">{i+1:02d}</div>
          <h3>{esc(s.get('name'))}</h3>
          <p class="layer">{esc(s.get('layer'))}</p>
          <p>{esc(s.get('purpose'))}</p>
          <dl><dt>Input</dt><dd>{esc(s.get('input'))}</dd><dt>Output</dt><dd>{esc(s.get('output'))}</dd><dt>Verifier</dt><dd>{esc(s.get('verifier'))}</dd></dl>
        </article>''')
    return "\n".join(cards)

def page(title, body, active="Home", desc="SkillOS public proof command center"):
    nav = [("Home","index.html"),("Proof Gradient","proof-gradient-agent-evolution-protocol.html"),("Proofs","proofs.html"),("Skills Used","skills.html"),("Multi-Agent","multi-agent.html"),("Receipts","receipts.html"),("Run","runbook.html"),("Health","health.html"),("GitHub","https://github.com/MontrealAI/skillos")]
    nav_html = "".join(f'<a class="{ "active" if n==active else "" }" href="{h}">{n}</a>' for n,h in nav)
    return f'''<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="cache-control" content="no-cache, no-store, must-revalidate"><meta http-equiv="pragma" content="no-cache"><meta http-equiv="expires" content="0">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><meta name="generator" content="Proof Gradient Agent Evolution Protocol Builder">
<style>{CSS}</style></head><body><div class="noise"></div><header class="top"><a class="brand" href="index.html">SkillOS</a><nav>{nav_html}</nav></header><main>{body}</main><footer><strong>SkillOS / MontrealAI</strong><span>Generated autonomously from repository evidence · {now_iso()}</span></footer></body></html>'''

CSS = r'''
:root{--bg:#060b18;--ink:#f4fbff;--muted:#b5c4dc;--cyan:#7cf7ff;--mint:#7cffb2;--gold:#ffd86b;--violet:#9886ff;--line:rgba(255,255,255,.16);--glass:rgba(255,255,255,.08)}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(1000px 700px at 12% 12%,rgba(0,222,255,.28),transparent 60%),radial-gradient(900px 700px at 82% 8%,rgba(150,124,255,.32),transparent 60%),linear-gradient(135deg,#06111f 0%,#111b3a 52%,#090b18 100%);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;line-height:1.5;min-height:100vh}.noise{position:fixed;inset:0;pointer-events:none;opacity:.22;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:34px 34px}.top{position:sticky;top:0;z-index:9;display:flex;align-items:center;justify-content:space-between;padding:14px 28px;background:rgba(3,10,20,.84);backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}.brand{font-weight:950;color:var(--cyan);text-decoration:none;letter-spacing:-.04em}.top nav{display:flex;gap:16px;flex-wrap:wrap}.top a{color:#d7e5f7;text-decoration:none;font-weight:800;font-size:14px}.top a.active,.top a:hover{color:var(--cyan)}main{width:min(1180px,calc(100% - 40px));margin:auto;padding:70px 0}.hero{display:grid;grid-template-columns:1.2fr .8fr;gap:32px;align-items:stretch}.eyebrow{letter-spacing:.24em;text-transform:uppercase;color:var(--cyan);font-weight:950;font-size:12px}.hero h1,.headline{font-size:clamp(48px,8vw,104px);line-height:.86;letter-spacing:-.075em;margin:12px 0 20px}.hero p.lead{font-size:clamp(18px,2.2vw,24px);color:#d9e4f2;max-width:780px}.panel,.metric,.proof-card,.skill-card,.glass{background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(255,255,255,.055));border:1px solid var(--line);box-shadow:0 24px 70px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.12);border-radius:28px}.panel{padding:34px}.quote{font-size:clamp(24px,3vw,40px);font-weight:950;letter-spacing:-.045em;line-height:1.02}.accent{color:var(--mint)}.gold{color:var(--gold)}.button-row{display:flex;gap:12px;flex-wrap:wrap;margin-top:26px}.btn{display:inline-flex;align-items:center;justify-content:center;border:1px solid var(--line);border-radius:999px;padding:12px 18px;background:rgba(255,255,255,.08);color:#fff;text-decoration:none;font-weight:900}.btn.primary{background:linear-gradient(135deg,var(--gold),#ffefad);color:#111}.btn.cyan{background:linear-gradient(135deg,var(--cyan),#bfffff);color:#06101c}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:18px;margin:34px 0}.metric{padding:22px}.metric strong{display:block;color:var(--mint);font-size:clamp(28px,4vw,42px);line-height:1}.metric span{color:var(--muted);font-weight:700}.section{margin-top:64px}.section h2{font-size:clamp(34px,5vw,64px);line-height:.95;letter-spacing:-.06em;margin:0 0 20px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:22px}.grid3{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.proof-card,.skill-card{padding:24px}.proof-card h3,.skill-card h3{font-size:24px;line-height:1.05;margin:10px 0;letter-spacing:-.035em}.pill{display:inline-flex;padding:6px 10px;border-radius:999px;background:rgba(124,255,178,.15);border:1px solid rgba(124,255,178,.38);color:var(--mint);font-weight:950;font-size:12px;letter-spacing:.08em;text-transform:uppercase}.pill.warn{background:rgba(255,216,107,.14);border-color:rgba(255,216,107,.36);color:var(--gold)}.pill.fail{background:rgba(255,70,110,.12);border-color:rgba(255,70,110,.35);color:#ff8ca2}.chart-card{padding:22px;border-radius:26px;background:rgba(4,12,28,.45);border:1px solid var(--line);min-height:310px}.chart{width:100%;height:auto}.axis{stroke:rgba(255,255,255,.24);stroke-width:1}.svg-label{fill:#b8c6da;font-size:12px;font-weight:800}.svg-value{fill:#f4fbff;font-size:14px;font-weight:900}.skill-index{color:var(--cyan);font-weight:950;letter-spacing:.2em}.layer{color:var(--gold);font-weight:900;text-transform:uppercase;letter-spacing:.13em;font-size:12px}.skill-card dl{display:grid;gap:8px;margin-top:18px}.skill-card dt{font-size:11px;color:var(--cyan);font-weight:950;letter-spacing:.14em;text-transform:uppercase}.skill-card dd{margin:0;color:#dce8fa}.table{width:100%;border-collapse:collapse;overflow:hidden;border-radius:22px}.table th,.table td{padding:14px 16px;border-bottom:1px solid var(--line);text-align:left}.table th{color:var(--cyan);text-transform:uppercase;letter-spacing:.12em;font-size:12px}.table td{color:#edf6ff}.code{white-space:pre-wrap;background:rgba(0,0,0,.36);border:1px solid var(--line);border-radius:18px;padding:18px;color:#ecfaff;overflow:auto}.manifest{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:13px}.flow{display:flex;gap:10px;flex-wrap:wrap}.flow span{border:1px solid var(--line);background:rgba(255,255,255,.08);border-radius:999px;padding:10px 14px;font-weight:900}.small{color:var(--muted);font-size:14px}footer{width:min(1180px,calc(100% - 40px));margin:40px auto;padding:32px 0;color:var(--muted);border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:20px;flex-wrap:wrap}@media(max-width:900px){.hero,.grid,.grid3{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,1fr)}.top{align-items:flex-start;gap:12px;flex-direction:column}.hero h1,.headline{font-size:58px}}@media(max-width:520px){main{width:min(100% - 24px,1180px);padding:38px 0}.metrics{grid-template-columns:1fr}.panel{padding:24px}.hero h1,.headline{font-size:48px}.top nav{gap:10px}.top a{font-size:12px}}
'''

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def proof_page(proof, receipt):
    gates = "".join(f'<tr><td>{esc(g.get("name"))}</td><td>{esc(g.get("required"))}</td><td>{esc(g.get("observed"))}</td><td>{"✅ Passed" if g.get("passed") else "❌ Failed"}</td></tr>' for g in receipt.get("proof_gates", []))
    baselines = receipt.get("baselines", [])
    skills = receipt.get("skills_used", [])
    body = f'''
<section class="hero"><div><div class="eyebrow">Proof Gradient / Agent Evolution Protocol</div><h1>{esc(TITLE)}</h1><p class="lead">One agent tries. Proof decides. The network evolves.</p><div class="button-row"><a class="btn primary" href="data/{PROOF_ID}.json">Open JSON receipt</a><a class="btn cyan" href="skills.html">See Skills Used</a><a class="btn" href="runbook.html">Run on GitHub</a></div></div><aside class="panel"><span class="pill">{esc(receipt.get('status'))}</span><div class="quote">GoalOS gives <span class="accent">Direction</span>.<br>PlanOS gives <span class="accent">Strategy</span>.<br>SkillOS gives <span class="accent">Capability</span>.<br>Proof Gradient gives <span class="gold">Evolution</span>.</div></aside></section>
<section class="metrics"><div class="metric"><strong>{metric(receipt,'agents')}</strong><span>agents</span></div><div class="metric"><strong>{metric(receipt,'roles')}</strong><span>specialist roles</span></div><div class="metric"><strong>{metric(receipt,'accepted_skills')}</strong><span>accepted skills</span></div><div class="metric"><strong>{metric(receipt,'proof_gradient_success_rate')}</strong><span>holdout success</span></div></section>
<section class="section"><div class="panel"><div class="eyebrow">Evolution thesis</div><h2>The selection layer for agent intelligence.</h2><p class="lead">Agents attempt work. SkillOS extracts candidate skills. Proof decides what propagates. The network evolves through validation-gated gradients instead of manual tuning or vibes.</p><div class="flow"><span>attempt</span><span>trace</span><span>skill</span><span>proof</span><span>gradient</span><span>upgrade</span><span>better attempt</span></div></div></section>
<section class="section grid"><div class="chart-card"><h3>Proof Gradient release curve</h3>{chart_line(receipt.get('release_curve', []))}</div><div class="chart-card"><h3>Baseline comparison</h3>{chart_bars(baselines)}</div></section>
<section class="section"><h2>Proof gates</h2><table class="table"><thead><tr><th>Gate</th><th>Required</th><th>Observed</th><th>Status</th></tr></thead><tbody>{gates}</tbody></table></section>
<section class="section"><h2>Skills Used</h2><p class="lead">The proof displays the operational skills used by the multi-agent system. Each skill names its layer, purpose, input, output, and verifier.</p><div class="grid">{skill_cards(skills)}</div></section>
<section class="section"><div class="panel"><h2>Public boundary</h2><p>{esc(receipt.get('public_claim_boundary'))}</p></div></section>
'''
    return page(TITLE, body, active="Proof Gradient", desc="Proof Gradient is the agent evolution protocol for SkillOS.")

def generated_proof_page(p):
    raw = p.get("raw", {})
    metrics = p.get("metrics", {})
    skills = p.get("skills_used") or []
    metric_html = "".join(f'<div class="metric"><strong>{esc(v if not isinstance(v, float) else (f"{v:.1%}" if "rate" in str(k) else f"{v:,.2f}"))}</strong><span>{esc(str(k).replace("_"," "))}</span></div>' for k,v in list(metrics.items())[:4]) or '<div class="metric"><strong>public</strong><span>normalized proof</span></div>'
    body = f'''<section class="hero"><div><div class="eyebrow">SkillOS proof room</div><h1>{esc(p['title'])}</h1><p class="lead">{esc(p['summary'])}</p><div class="button-row"><a class="btn primary" href="../{p['json']}">Open JSON receipt</a><a class="btn" href="../proofs.html">All proofs</a></div></div><aside class="panel"><span class="pill {'fail' if p['status']=='FAILED' else 'warn' if p['status']!='PASSED' else ''}">{esc(p['status'])}</span><div class="quote">A normalized proof room generated from repository evidence.</div></aside></section><section class="metrics">{metric_html}</section><section class="section"><div class="panel"><h2>Source</h2><p class="code manifest">{esc(p['source'])}</p></div></section>'''
    if skills:
        body += f'<section class="section"><h2>Skills Used</h2><div class="grid">{skill_cards(skills)}</div></section>'
    rendered = page(p["title"], body, active="Proofs")
    for name in ["index.html", "proof-gradient-agent-evolution-protocol.html", "proofs.html", "skills.html", "multi-agent.html", "receipts.html", "architecture.html", "runbook.html", "health.html"]:
        rendered = rendered.replace(f'href="{name}"', f'href="../{name}"')
    return rendered

def build(out):
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    receipt_path = Path("data") / f"{PROOF_ID}.json"
    if not receipt_path.exists():
        raise SystemExit(f"Missing {receipt_path}; run run_proof_gradient_agent_evolution_protocol.py first")
    receipt = read_json(receipt_path)
    proofs = collect_proofs()
    workflows = collect_workflows()
    # Ensure Proof Gradient is first and canonical.
    pg = normalize_proof(receipt_path, receipt)
    proofs = [p for p in proofs if p["slug"] != PROOF_ID]
    proofs.insert(0, pg)
    data_dir = out / "data"
    (data_dir / "proofs").mkdir(parents=True, exist_ok=True)
    write(data_dir / f"{PROOF_ID}.json", json.dumps(receipt, indent=2, sort_keys=True))
    for p in proofs:
        normalized = {k:v for k,v in p.items() if k != "raw"}
        write(data_dir / "proofs" / f"{p['slug']}.json", json.dumps(normalized, indent=2, sort_keys=True))
    manifest = {
        "schema": "skillos.public_command_center.proof_gradient.v1",
        "marker": MARKER,
        "root_contract": "/skillos/ and /skillos/index.html are the Public SkillOS Command Center; Proof Gradient is a proof room.",
        "generated_at": now_iso(),
        "repository": os.environ.get("GITHUB_REPOSITORY", "MontrealAI/skillos"),
        "git_sha": os.environ.get("GITHUB_SHA") or git(["git", "rev-parse", "HEAD"]),
        "proof_count": len(proofs),
        "workflow_count": len(workflows),
        "flagship_proof": PROOF_ID,
        "proof_gradient_status": receipt.get("status"),
    }
    write(data_dir / "command-center-manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
    registry = {"schema":"skillos.proof_registry.v1", "generated_at": now_iso(), "proofs":[{k:v for k,v in p.items() if k != "raw"} for p in proofs]}
    write(out / "proof-registry.json", json.dumps(registry, indent=2, sort_keys=True))
    # badges
    badge_src = Path("badges") / f"{PROOF_ID}.svg"
    if badge_src.exists():
        (out / "badges").mkdir(exist_ok=True)
        shutil.copy2(badge_src, out / "badges" / f"{PROOF_ID}.svg")
    stats = receipt["summary_metrics"]
    cards = "".join(f'''<article class="proof-card"><span class="pill {'fail' if p['status']=='FAILED' else 'warn' if p['status']!='PASSED' else ''}">{esc(p['status'])}</span><h3>{esc(p['title'])}</h3><p>{esc(p['summary'])[:220]}</p><div class="button-row"><a class="btn" href="{p['href']}">Open proof</a><a class="btn" href="{p['json']}">JSON</a></div></article>''' for p in proofs[:6])
    root_body = f'''
<section class="hero"><div><div class="eyebrow">MontrealAI / SkillOS</div><h1>{ROOT_TITLE}</h1><p class="lead">The canonical public lobby for SkillOS proofs, receipts, workflows, Skills Used displays, and multi-agent capability evidence. Generated fresh by GitHub Actions from repository evidence.</p><div class="button-row"><a class="btn primary" href="proof-gradient-agent-evolution-protocol.html">Open Proof Gradient</a><a class="btn cyan" href="proofs.html">All proofs</a><a class="btn" href="runbook.html">Run / regenerate</a></div></div><aside class="panel"><div class="eyebrow">First evolutionary proof</div><div class="quote">One agent tries.<br><span class="accent">Proof decides.</span><br>The network evolves.</div><p>GoalOS gives Direction. PlanOS gives Strategy. SkillOS gives Capability. <strong>Proof Gradient gives Evolution.</strong></p></aside></section>
<section class="section"><div class="panel"><div class="eyebrow">Proof Gradient thesis</div><h2>Agents do not evolve by sounding smart. They evolve when their work survives proof.</h2><p class="lead">Proof Gradient turns SkillOS into an evolving capability network: attempts create traces, traces become candidate skills, proof selects what propagates, and verified skills upgrade future routing.</p></div></section>
<section class="metrics"><div class="metric"><strong>{stats['agents']:,}</strong><span>agents in flagship benchmark</span></div><div class="metric"><strong>{stats['roles']}</strong><span>specialist roles</span></div><div class="metric"><strong>{stats['accepted_skills']}</strong><span>proof-accepted skills</span></div><div class="metric"><strong>{stats['success_uplift_over_static_pp']:.1f} pp</strong><span>uplift over static coordination</span></div></section>
<section class="section grid"><div class="chart-card"><h3>Recursive release curve</h3>{chart_line(receipt.get('release_curve', []))}</div><div class="chart-card"><h3>Baselines</h3>{chart_bars(receipt.get('baselines', []))}</div></section>
<section class="section"><h2>Featured proof library</h2><div class="grid">{cards}</div></section>
<section class="section"><div class="panel"><h2>Root contract</h2><p class="lead">The root is the lobby. Proofs are rooms. This page is always the Public SkillOS Command Center; Proof Gradient lives at <a href="proof-gradient-agent-evolution-protocol.html">proof-gradient-agent-evolution-protocol.html</a>.</p></div></section>
'''
    index = page(ROOT_TITLE, root_body, active="Home", desc="Canonical SkillOS public command center generated from repository evidence.")
    for banned in BANNED_ROOT_TITLE_PHRASES:
        if f"<h1>{banned}" in index:
            raise SystemExit(f"Banned root title: {banned}")
    write(out / "index.html", index)
    write(out / f"{PROOF_ID}.html", proof_page(pg, receipt))
    # alias for memorable URL
    write(out / "proof-gradient.html", proof_page(pg, receipt))
    # generated proof rooms
    (out / "proofs").mkdir(exist_ok=True)
    for p in proofs:
        write(out / "proofs" / f"{p['slug']}.html", generated_proof_page(p))
    proof_list = "".join(f'<tr><td><a href="{esc(p["href"])}">{esc(p["title"])}</a></td><td>{esc(p["status"])}</td><td><a href="{esc(p["json"])}">JSON</a></td></tr>' for p in proofs)
    write(out / "proofs.html", page("SkillOS Proof Library", f'<section class="section"><h1 class="headline">Proof Library</h1><p class="lead">All proof rooms are generated from repository receipts and normalized so every link works.</p><table class="table"><thead><tr><th>Proof</th><th>Status</th><th>Receipt</th></tr></thead><tbody>{proof_list}</tbody></table></section>', active="Proofs"))
    write(out / "skills.html", page("Skills Used · Proof Gradient", f'<section class="hero"><div><div class="eyebrow">Skills Used</div><h1>Operational skills behind Proof Gradient.</h1><p class="lead">Each skill is displayed as an evidence unit: layer, purpose, input, output, and verifier.</p></div><aside class="panel"><div class="quote">Every skill must face proof before it becomes network capability.</div></aside></section><section class="section"><div class="grid">{skill_cards(receipt.get("skills_used", []))}</div></section>', active="Skills Used"))
    wf_rows = "".join(f'<tr><td>{esc(w["name"])}</td><td>{esc(w["path"])}</td><td>{"yes" if w["dispatch"] else "no"}</td><td>{"yes" if w["pages"] else "no"}</td></tr>' for w in workflows)
    write(out / "actions.html", page("SkillOS Actions", f'<section class="section"><h1 class="headline">Run or regenerate</h1><p class="lead">Use GitHub Actions to regenerate the proof, rebuild the public Command Center, deploy Pages, and verify the live root.</p><div class="panel"><h2>Recommended workflow</h2><p class="code">Proof Gradient Agent Evolution Protocol Proof</p><p>Open GitHub Actions, select the workflow, and click <strong>Run workflow</strong>.</p><a class="btn primary" href="https://github.com/MontrealAI/skillos/actions">Open GitHub Actions</a></div><h2>Workflow index</h2><table class="table"><thead><tr><th>Name</th><th>Path</th><th>Manual run</th><th>Pages deploy</th></tr></thead><tbody>{wf_rows}</tbody></table></section>', active="Run"))
    write(out / "runbook.html", page("Runbook · Proof Gradient", f'<section class="section"><h1 class="headline">Runbook</h1><div class="panel"><h2>How to run the proof</h2><p class="code">GitHub → Actions → Proof Gradient Agent Evolution Protocol Proof → Run workflow</p><p>Recommended inputs:</p><p class="code">deploy_pages: true\nverify_live: true\ncancel_legacy_runs: true</p></div><div class="panel" style="margin-top:20px"><h2>What the workflow does</h2><p class="code">run benchmark\n→ write JSON receipt\n→ write Markdown report\n→ render Command Center root\n→ render Proof Gradient page\n→ display Skills Used\n→ verify internal links\n→ deploy GitHub Pages\n→ verify live root</p></div></section>', active="Run"))
    write(out / "receipts.html", page("Receipts · Proof Gradient", f'<section class="section"><h1 class="headline">Receipts</h1><p class="lead">Machine-readable evidence produced by the proof workflow.</p><div class="grid"><article class="proof-card"><h3>Proof Gradient receipt</h3><p>Full JSON receipt with gates, baselines, skills, and release curve.</p><a class="btn primary" href="data/{PROOF_ID}.json">Open receipt</a></article><article class="proof-card"><h3>Command Center manifest</h3><p>Root contract and generation metadata.</p><a class="btn" href="data/command-center-manifest.json">Open manifest</a></article></div></section>', active="Receipts"))
    roles = "".join(f'<span>{esc(r)}</span>' for r in receipt.get("large_multi_agent_system", {}).get("roles", []))
    write(out / "multi-agent.html", page("Multi-Agent System · Proof Gradient", f'<section class="section"><h1 class="headline">Large multi-agent coordination.</h1><p class="lead">The proof is not about agent count. It is about coordinated specialization under proof-gated release.</p><div class="panel"><div class="flow">{roles}</div></div></section>', active="Multi-Agent"))
    write(out / "architecture.html", page("Architecture · Proof Gradient", '<section class="section"><h1 class="headline">Architecture</h1><div class="panel"><p class="code">GoalOS → Direction\nPlanOS → Strategy\nSkillOS → Capability\nProof Gradient → Evolution</p><p class="lead">Proof Gradient is the selection layer: it turns proof outcomes into evolution signals for the network.</p></div></section>', active="Multi-Agent"))
    health = {
        "status": "green" if receipt.get("status") == "PASSED" else "red",
        "root_is_command_center": True,
        "proof_gradient_status": receipt.get("status"),
        "internal_links_verified_by": "scripts/verify_proof_gradient_agent_evolution_protocol.py",
        "generated_at": now_iso(),
    }
    write(data_dir / "command-center-health.json", json.dumps(health, indent=2, sort_keys=True))
    write(out / "health.html", page("Health · Proof Gradient", f'<section class="section"><h1 class="headline">Health</h1><div class="panel"><span class="pill">{esc(health["status"])}</span><p class="lead">Root contract, receipt, proof gates, and internal links are verified before deployment.</p><p class="code manifest">{esc(json.dumps(health, indent=2))}</p></div></section>', active="Health"))
    write(out / "404.html", page("SkillOS · Not Found", '<section class="section"><h1 class="headline">Proof room not found.</h1><p class="lead">Return to the Public SkillOS Command Center.</p><a class="btn primary" href="index.html">Open Command Center</a></section>'))
    write(out / "force-refresh.html", '<!doctype html><meta http-equiv="refresh" content="0; url=index.html?v=proof-gradient-v1"><title>Refreshing SkillOS</title>')
    write(out / "robots.txt", "User-agent: *\nAllow: /\nSitemap: https://montrealai.github.io/skillos/sitemap.xml\n")
    pages = ["index.html", f"{PROOF_ID}.html", "proof-gradient.html", "proofs.html", "skills.html", "actions.html", "receipts.html", "multi-agent.html", "architecture.html", "runbook.html", "health.html"] + [f"proofs/{p['slug']}.html" for p in proofs]
    locs = "\n".join(f"  <url><loc>https://montrealai.github.io/skillos/{p}</loc></url>" for p in pages)
    write(out / "sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{locs}\n</urlset>')
    write(out / ".nojekyll", "")
    write(out / "version.txt", f"{MARKER}\n{now_iso()}\n")
    write(out / "sw.js", "self.addEventListener('install',event=>self.skipWaiting());self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.map(k=>caches.delete(k))))));")
    print(json.dumps({"status":"built", "out":str(out), "proofs":len(proofs), "workflows":len(workflows), "marker":MARKER}, indent=2))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="dist")
    args = ap.parse_args()
    build(args.out)

if __name__ == "__main__":
    main()
