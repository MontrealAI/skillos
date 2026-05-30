#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, time, urllib.request, urllib.error
from typing import Any

REPO = os.environ.get("GITHUB_REPOSITORY", "MontrealAI/skillos")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""
REF = os.environ.get("GITHUB_REF_NAME", "main")
SERVER_URL = os.environ.get("GITHUB_SERVER_URL", "https://github.com")

EXCLUDE = [
    "run all public proofs",
    "proof command center refresh",
    "public site",
    "refresh reusable",
    "pages",
    "safe public copy",
]
INCLUDE = ["proof", "rsi", "capability", "market", "command", "capital", "multi-agent"]

def api(method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any] | None:
    if not TOKEN:
        raise RuntimeError("GITHUB_TOKEN is required.")
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else None

def workflows() -> list[dict[str, Any]]:
    data = api("GET", f"/repos/{REPO}/actions/workflows?per_page=100") or {}
    return data.get("workflows", [])

def selected(w: dict[str, Any], filter_text: str) -> bool:
    name = (w.get("name") or "").lower()
    path = (w.get("path") or "").lower()
    text = f"{name} {path}"
    if w.get("state") != "active":
        return False
    if filter_text and filter_text.lower() not in text:
        return False
    if any(x in text for x in EXCLUDE):
        return False
    return any(x in text for x in INCLUDE)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", default=REF)
    parser.add_argument("--filter", default=os.environ.get("PROOF_FILTER", ""))
    parser.add_argument("--dry-run", action="store_true", default=os.environ.get("DRY_RUN", "false").lower() == "true")
    parser.add_argument("--sleep", type=float, default=2.0)
    args = parser.parse_args()

    rows = [w for w in workflows() if selected(w, args.filter)]
    print(json.dumps({
        "status": "PUBLIC_PROOF_WORKFLOWS_SELECTED",
        "repository": REPO,
        "ref": args.ref,
        "dry_run": args.dry_run,
        "selected_count": len(rows),
        "selected": [{"name": w.get("name"), "path": w.get("path"), "html_url": w.get("html_url")} for w in rows],
    }, indent=2))

    if args.dry_run:
        return

    for w in rows:
        print(f"Dispatching {w.get('name')}")
        api("POST", f"/repos/{REPO}/actions/workflows/{w.get('id')}/dispatches", {"ref": args.ref})
        time.sleep(args.sleep)

    print(json.dumps({
        "status": "PUBLIC_PROOF_WORKFLOWS_DISPATCHED",
        "selected_count": len(rows),
        "actions_url": f"{SERVER_URL}/{REPO}/actions",
    }, indent=2))

if __name__ == "__main__":
    main()
