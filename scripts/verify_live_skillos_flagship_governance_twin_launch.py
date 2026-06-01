#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.request
from urllib.error import URLError, HTTPError

MARKER = "SKILLOS_FLAGSHIP_GOVERNANCE_TWIN_LAUNCH_V1"
SCHEMA = "skillos.flagship.capability_governance_twin.launch.v1"
OLD_PHRASES = [
    "Autonomous Proof Command Center",
    "SkillOS Proof Command Center",
    "Public SkillOS Command Center v2",
    "SkillOS Public Command Center v3",
]

def fetch(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"Cache-Control":"no-cache", "Pragma":"no-cache", "User-Agent":"SkillOS-live-verifier/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return int(r.status), r.read().decode("utf-8", errors="ignore")

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default="https://montrealai.github.io/skillos/")
    ap.add_argument("--attempts", type=int, default=18)
    ap.add_argument("--sleep", type=int, default=10)
    args = ap.parse_args()
    base = args.base_url.rstrip("/") + "/"
    last = ""
    for attempt in range(1, args.attempts + 1):
        try:
            root_status, root = fetch(base + f"?v=flagship-{attempt}")
            index_status, index = fetch(base + f"index.html?v=flagship-{attempt}")
            manifest_status, manifest_raw = fetch(base + f"data/flagship-capability-governance-twin-manifest.json?v=flagship-{attempt}")
            manifest = json.loads(manifest_raw)
            root_ok = root_status == 200 and MARKER in root and all(p not in root for p in OLD_PHRASES)
            index_ok = index_status == 200 and MARKER in index
            manifest_ok = manifest_status == 200 and manifest.get("schema") == SCHEMA and manifest.get("marker") == MARKER
            if root_ok and index_ok and manifest_ok:
                print(json.dumps({"status":"LIVE_VERIFIED","base_url":base,"attempt":attempt,"marker":MARKER,"schema":SCHEMA}, indent=2))
                return
            last = f"attempt={attempt}, root_ok={root_ok}, index_ok={index_ok}, manifest_ok={manifest_ok}, root_status={root_status}, index_status={index_status}, manifest_status={manifest_status}"
        except (URLError, HTTPError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last = f"attempt={attempt}, error={exc}"
        print(last)
        time.sleep(args.sleep)
    raise SystemExit(f"Live verification failed after {args.attempts} attempts: {last}")

if __name__ == "__main__":
    main()
