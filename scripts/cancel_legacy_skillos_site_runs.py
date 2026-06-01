#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess

LEGACY_KEYWORDS = [
    "skillos-public-proof-command-center-refresh",
    "skillos-public-site-refresh",
    "refresh-skillos-command-center",
    "skillos-command-center-autopublisher-v2",
    "skillos-command-center-autopublisher-v3",
    "skillos-command-center-autopublisher-v4",
]

def main() -> None:
    repo = os.environ.get("GITHUB_REPOSITORY")
    run_id = os.environ.get("GITHUB_RUN_ID")
    if not repo:
        print("No GITHUB_REPOSITORY; skipping.")
        return
    try:
        out = subprocess.check_output(["gh", "run", "list", "--repo", repo, "--status", "in_progress", "--json", "databaseId,workflowName,url"], text=True)
    except Exception as exc:
        print(f"Could not list runs: {exc}")
        return
    runs = json.loads(out)
    cancelled = []
    for run in runs:
        rid = str(run.get("databaseId"))
        if rid == str(run_id):
            continue
        name = (run.get("workflowName") or "").lower()
        url = (run.get("url") or "").lower()
        if any(key in name or key in url for key in LEGACY_KEYWORDS):
            subprocess.run(["gh", "run", "cancel", rid, "--repo", repo], check=False)
            cancelled.append({"id": rid, "name": name})
    print(json.dumps({"cancelled": cancelled}, indent=2))

if __name__ == "__main__":
    main()
