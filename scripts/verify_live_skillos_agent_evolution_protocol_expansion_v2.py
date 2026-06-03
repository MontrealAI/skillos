#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, urllib.request

def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.read().decode("utf-8","replace")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--base-url",default="https://montrealai.github.io/skillos/")
    args=p.parse_args()
    base=args.base_url.rstrip("/")+"/"
    root=fetch(base+"?v=agent-evolution-v2")
    protocol=fetch(base+"proof-carrying-intelligence.html?v=agent-evolution-v2")
    manifest=fetch(base+"data/skillos-agent-evolution-protocol-expansion-v2-manifest.json?v=agent-evolution-v2")
    if "Public SkillOS Command Center" not in root:
        raise SystemExit("live root does not contain Public SkillOS Command Center")
    if "Proof-Carrying Intelligence" not in protocol:
        raise SystemExit("protocol room missing")
    if "SKILLOS_AGENT_EVOLUTION_PROTOCOL_EXPANSION_V2" not in manifest:
        raise SystemExit("manifest marker missing")
    print(json.dumps({"status":"LIVE_VERIFIED","base_url":base},indent=2))
if __name__=="__main__":
    main()
