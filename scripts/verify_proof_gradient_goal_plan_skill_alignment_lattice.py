#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path
from urllib.parse import urlparse, unquote

PROOF_ID = "proof-gradient-goal-plan-skill-alignment-lattice"
MARKER = "SKILLOS_PROOF_GRADIENT_GOAL_PLAN_SKILL_ALIGNMENT_LATTICE_V1"
REQUIRED = ["index.html","proof-gradient-goal-plan-skill-alignment-lattice.html","goals.html","plans.html","skills.html","receipts.html","run.html","data/command-center-manifest.json",f"data/{PROOF_ID}.json",f"badges/{PROOF_ID}.svg","proof-registry.json",".nojekyll"]
BAD_ROOT_TITLES = ["<title>Proof Gradient", "<h1 class=\"h1\">Goal-Plan-Skill Alignment Lattice", "Capability Governance Twin</title>", "Autonomous Proof Command Center"]

def fail(msg):
    print("ERROR:", msg, file=sys.stderr); raise SystemExit(1)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out", default="dist")
    args=ap.parse_args(); root=Path(args.out)
    missing=[p for p in REQUIRED if not (root/p).exists()]
    if missing: fail("Missing required generated files: " + ", ".join(missing))
    index=(root/"index.html").read_text(encoding="utf-8")
    if "<title>Public SkillOS Command Center</title>" not in index: fail("Root title is not Public SkillOS Command Center")
    if "The root is the lobby" not in index: fail("Root does not explain root contract")
    for bad in BAD_ROOT_TITLES:
        if bad in index: fail(f"Root contains forbidden title/content: {bad}")
    proof=(root/"proof-gradient-goal-plan-skill-alignment-lattice.html").read_text(encoding="utf-8")
    for phrase in ["GoalOS", "PlanOS", "SkillOS", "Proof Gradient", "Goals used", "Plans used", "Skills used"]:
        if phrase not in proof: fail(f"Proof page missing {phrase}")
    receipt=json.loads((root/f"data/{PROOF_ID}.json").read_text(encoding="utf-8"))
    if not receipt.get("passed"): fail("Receipt did not pass")
    if len(receipt.get("goals_used",[])) < 6: fail("Not enough goals displayed")
    if len(receipt.get("plans_used",[])) < 5: fail("Not enough plans displayed")
    if len(receipt.get("skills_used",[])) < 8: fail("Not enough skills displayed")
    manifest=json.loads((root/"data/command-center-manifest.json").read_text(encoding="utf-8"))
    if manifest.get("marker") != MARKER: fail("Manifest marker mismatch")
    hrefs=[]
    for html_path in root.glob("*.html"):
        text=html_path.read_text(encoding="utf-8")
        for m in re.finditer(r'href="([^"]+)"', text):
            href=m.group(1)
            if href.startswith(("http://","https://","mailto:","#")): continue
            path=unquote(href.split("#")[0].split("?")[0])
            if not path: continue
            target=(html_path.parent/path).resolve()
            try: target.relative_to(root.resolve())
            except Exception: fail(f"Unsafe internal link {href} in {html_path.name}")
            if not target.exists(): hrefs.append(f"{html_path.name} -> {href}")
    if hrefs: fail("Missing internal links: " + ", ".join(hrefs[:50]))
    print(json.dumps({"verified": True, "root": str(root), "proof": PROOF_ID, "marker": MARKER, "goals": len(receipt.get('goals_used',[])), "plans": len(receipt.get('plans_used',[])), "skills": len(receipt.get('skills_used',[]))}, indent=2))

if __name__ == "__main__":
    main()
