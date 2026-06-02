#!/usr/bin/env python3
import argparse, json, sys, time, urllib.request

MARKER = "SKILLOS_PROOF_GRADIENT_GOAL_PLAN_SKILL_ALIGNMENT_LATTICE_V1"

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8", "replace")

def fail(msg):
    print("ERROR:", msg, file=sys.stderr); raise SystemExit(1)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--base", default="https://montrealai.github.io/skillos/"); ap.add_argument("--retries", type=int, default=8); ap.add_argument("--sleep", type=float, default=7)
    args=ap.parse_args(); base=args.base.rstrip("/") + "/"
    last=""
    for i in range(args.retries):
        try:
            root=fetch(base+f"?v=pg-gps-{i}"); idx=fetch(base+f"index.html?v=pg-gps-{i}"); manifest=fetch(base+"data/command-center-manifest.json"); proof=fetch(base+"proof-gradient-goal-plan-skill-alignment-lattice.html")
            if "<title>Public SkillOS Command Center</title>" in root and "<title>Public SkillOS Command Center</title>" in idx and MARKER in manifest and "Goal-Plan-Skill Alignment Lattice" in proof:
                print(json.dumps({"live_verified": True, "base": base, "marker": MARKER}, indent=2)); return
            last="root/index/manifest/proof content mismatch"
        except Exception as e:
            last=str(e)
        time.sleep(args.sleep)
    fail("Live verification failed: " + last)

if __name__ == "__main__":
    main()
