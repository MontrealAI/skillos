#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import urllib.request
from urllib.error import HTTPError, URLError

REPO = os.environ.get("GITHUB_REPOSITORY", "MontrealAI/skillos")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
RUN_ID = os.environ.get("GITHUB_RUN_ID", "")
LEGACY_MARKERS = [
    "Refresh SkillOS Public Command Center",
    "SkillOS Public Site Command Center Refresh",
    "Deploy SkillOS website with autonomous safe public copy",
    "SkillOS Public Command Center v3 Autopublisher",
    "SkillOS Sovereign Command Center v5 Canonical Deploy",
    "SkillOS Sovereign Command Center v5.1 Canonical Deploy",
]

def request(method: str, url: str) -> tuple[int, str]:
    if not TOKEN:
        return 0, "missing token"
    req = urllib.request.Request(url, method=method, headers={
        "Accept":"application/vnd.github+json",
        "Authorization":f"Bearer {TOKEN}",
        "X-GitHub-Api-Version":"2022-11-28",
        "User-Agent":"SkillOS-legacy-run-canceller/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return int(r.status), r.read().decode("utf-8", errors="ignore")
    except HTTPError as exc:
        return int(exc.code), exc.read().decode("utf-8", errors="ignore")
    except URLError as exc:
        return 0, str(exc)

def main() -> None:
    url = f"https://api.github.com/repos/{REPO}/actions/runs?status=in_progress&per_page=100"
    status, body = request("GET", url)
    if status != 200:
        print(json.dumps({"status":"SKIPPED","reason":body[:240]}))
        return
    runs = json.loads(body).get("workflow_runs", [])
    cancelled = []
    for run in runs:
        rid = str(run.get("id"))
        name = str(run.get("name",""))
        if rid == RUN_ID:
            continue
        if any(marker.lower() in name.lower() for marker in LEGACY_MARKERS):
            s, b = request("POST", f"https://api.github.com/repos/{REPO}/actions/runs/{rid}/cancel")
            cancelled.append({"id":rid,"name":name,"status":s})
    print(json.dumps({"status":"CANCELLED_LEGACY_RUNS","cancelled":cancelled}, indent=2))

if __name__ == "__main__":
    main()
