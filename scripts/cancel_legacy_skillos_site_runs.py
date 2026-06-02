#!/usr/bin/env python3
import json, os, sys, time, urllib.request

LEGACY_HINTS = [
    "public proof command center", "public site refresh", "command center refresh", "sovereign command center", "capability governance twin launch"
]

def request(url, token, method="GET", data=None):
    headers = {"Accept":"application/vnd.github+json", "X-GitHub-Api-Version":"2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read().decode()
        return json.loads(raw) if raw else {}

def main():
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    current = os.environ.get("GITHUB_RUN_ID")
    if not token or not repo:
        print("No GITHUB_TOKEN or GITHUB_REPOSITORY; legacy cancellation skipped.")
        return
    api = f"https://api.github.com/repos/{repo}/actions/runs?status=in_progress&per_page=100"
    try:
        runs = request(api, token).get("workflow_runs", [])
    except Exception as e:
        print(f"Could not list runs: {e}")
        return
    cancelled = []
    for run in runs:
        rid = str(run.get("id"))
        if rid == str(current):
            continue
        name = (run.get("name") or "").lower()
        path = (run.get("path") or "").lower()
        if any(h in name or h.replace(" ", "-") in path for h in LEGACY_HINTS):
            url = f"https://api.github.com/repos/{repo}/actions/runs/{rid}/cancel"
            try:
                request(url, token, method="POST", data={})
                cancelled.append({"id":rid, "name":run.get("name"), "path":run.get("path")})
                time.sleep(0.2)
            except Exception as e:
                print(f"Could not cancel {rid}: {e}")
    print(json.dumps({"cancelled": cancelled, "count": len(cancelled)}, indent=2))

if __name__ == "__main__":
    main()
