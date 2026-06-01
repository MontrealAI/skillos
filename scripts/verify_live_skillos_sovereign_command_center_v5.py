#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
import urllib.request
from urllib.parse import urljoin

MARKER = "SKILLOS_COMMAND_CENTER_V5_1_CANONICAL_ROOT"
FORBIDDEN = ["Autonomous Proof Command Center", "SkillOS Public Command Center v2", "SkillOS Public Command Center v3"]

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"Cache-Control": "no-cache", "Pragma": "no-cache", "User-Agent": "SkillOS-v5.1-live-verifier"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace")

def check(base: str) -> dict:
    base = base.rstrip("/") + "/"
    urls = {
        "root": base + "?v=sovereign-v5-1",
        "index": urljoin(base, "index.html?v=sovereign-v5-1-1"),
        "manifest": urljoin(base, "data/command-center-manifest.json?v=sovereign-v5-1-1"),
    }
    root = fetch(urls["root"])
    index = fetch(urls["index"])
    manifest = json.loads(fetch(urls["manifest"]))
    errors = []
    for label, text in [("root", root), ("index", index)]:
        if MARKER not in text:
            errors.append(f"{label} missing marker")
        for phrase in FORBIDDEN:
            if phrase in text:
                errors.append(f"{label} contains forbidden phrase: {phrase}")
    if manifest.get("schema") != "skillos.command_center.sovereign.v5.1":
        errors.append("manifest schema is not v5.1")
    return {"urls": urls, "errors": errors, "manifest_schema": manifest.get("schema")}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="https://montrealai.github.io/skillos/")
    p.add_argument("--retries", type=int, default=12)
    p.add_argument("--sleep", type=int, default=10)
    args = p.parse_args()
    last = None
    for attempt in range(1, args.retries + 1):
        try:
            last = check(args.base_url)
            if not last["errors"]:
                print(json.dumps({"status":"LIVE_VERIFIED", "attempt":attempt, **last}, indent=2))
                return
            print(json.dumps({"status":"waiting", "attempt":attempt, **last}, indent=2))
        except Exception as exc:
            last = {"errors":[str(exc)]}
            print(json.dumps({"status":"waiting", "attempt":attempt, "error":str(exc)}, indent=2))
        time.sleep(args.sleep)
    raise SystemExit(f"Live verification failed after retries: {last}")

if __name__ == "__main__":
    main()
