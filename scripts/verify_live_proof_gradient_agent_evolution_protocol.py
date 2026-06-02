#!/usr/bin/env python3
import argparse, json, sys, time, urllib.request

PROOF_ID = "proof-gradient-agent-evolution-protocol"
ROOT_MARKER = "SKILLOS_PROOF_GRADIENT_COMMAND_CENTER_V1"
RECEIPT_MARKER = "SKILLOS_PROOF_GRADIENT_AGENT_EVOLUTION_PROTOCOL_V1"

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="https://montrealai.github.io/skillos/")
    ap.add_argument("--retries", type=int, default=8)
    ap.add_argument("--sleep", type=int, default=12)
    args = ap.parse_args()
    base = args.base_url.rstrip("/") + "/"
    last = ""
    for attempt in range(args.retries):
        try:
            root = fetch(base + f"?v=proof-gradient-{attempt}")
            index = fetch(base + f"index.html?v=proof-gradient-{attempt}")
            manifest = json.loads(fetch(base + f"data/command-center-manifest.json?v=proof-gradient-{attempt}"))
            receipt = json.loads(fetch(base + f"data/{PROOF_ID}.json?v=proof-gradient-{attempt}"))
            proof = fetch(base + f"{PROOF_ID}.html?v=proof-gradient-{attempt}")
            if "Public SkillOS Command Center" in root and "Public SkillOS Command Center" in index and manifest.get("marker") == ROOT_MARKER and receipt.get("marker") == RECEIPT_MARKER and "One agent tries" in proof:
                if "Autonomous Proof Command Center" in root:
                    fail("Live root still contains legacy Autonomous Proof Command Center")
                print(json.dumps({"status":"live_verified", "base_url":base, "attempt":attempt, "manifest_marker":manifest.get("marker"), "receipt_status":receipt.get("status")}, indent=2))
                return
            last = f"root/index/manifest/receipt markers not ready: manifest={manifest.get('marker')} receipt={receipt.get('marker')}"
        except Exception as e:
            last = repr(e)
        time.sleep(args.sleep)
    fail(f"Live verification failed after retries. Last error: {last}")

if __name__ == "__main__":
    main()
