#!/usr/bin/env python3
import json, os, sys, urllib.request

TOKEN=os.environ.get("GITHUB_TOKEN")
REPO=os.environ.get("GITHUB_REPOSITORY")
CURRENT=os.environ.get("GITHUB_RUN_ID")
LEGACY=["public-site", "command center refresh", "sovereign", "capability governance twin launch"]

def req(url, method="GET"):
    if not TOKEN or not REPO: return None
    r=urllib.request.Request(url, method=method, headers={"Authorization":"Bearer "+TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"})
    try:
        with urllib.request.urlopen(r, timeout=20) as resp:
            return resp.read().decode()
    except Exception as e:
        print("cancel helper ignored:", e)
        return None

def main():
    if not TOKEN or not REPO:
        print("No token/repo available; skipping cancellation."); return
    url=f"https://api.github.com/repos/{REPO}/actions/runs?status=in_progress&per_page=100"
    data=req(url)
    if not data: return
    runs=json.loads(data).get("workflow_runs",[])
    for run in runs:
        if str(run.get("id")) == str(CURRENT): continue
        name=(run.get("name") or "").lower()
        if any(x in name for x in LEGACY):
            print("Cancelling legacy run", run.get("id"), run.get("name"))
            req(f"https://api.github.com/repos/{REPO}/actions/runs/{run.get('id')}/cancel", method="POST")
if __name__ == "__main__": main()
