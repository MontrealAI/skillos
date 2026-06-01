#!/usr/bin/env python3
from __future__ import annotations
import json, os, subprocess, sys

LEGACY_HINTS=['public-proof-command-center','public-site-refresh','command-center-autopublisher','sovereign-command-center-v5','flagship-governance-twin-launch']

def gh(args):
    return subprocess.run(['gh']+args, capture_output=True, text=True)

def main():
    repo=os.environ.get('GITHUB_REPOSITORY','')
    run_id=os.environ.get('GITHUB_RUN_ID','')
    if not repo:
        print(json.dumps({'status':'SKIPPED','reason':'GITHUB_REPOSITORY missing'})); return
    res=gh(['run','list','--repo',repo,'--status','in_progress','--limit','100','--json','databaseId,workflowName,displayTitle'])
    if res.returncode!=0:
        print(json.dumps({'status':'SKIPPED','reason':'gh run list failed','stderr':res.stderr[-300:]})); return
    try: runs=json.loads(res.stdout)
    except Exception: runs=[]
    cancelled=[]
    for run in runs:
        rid=str(run.get('databaseId',''))
        if rid==str(run_id): continue
        name=(run.get('workflowName') or run.get('displayTitle') or '').lower()
        if any(h in name for h in LEGACY_HINTS):
            c=gh(['run','cancel',rid,'--repo',repo])
            cancelled.append({'id':rid,'name':name,'returncode':c.returncode})
    print(json.dumps({'status':'DONE','cancelled':cancelled}, indent=2))
if __name__=='__main__': main()
