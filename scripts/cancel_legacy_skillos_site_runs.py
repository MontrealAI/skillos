#!/usr/bin/env python3
import json, os, urllib.request
TOKEN=os.environ.get('GITHUB_TOKEN'); REPO=os.environ.get('GITHUB_REPOSITORY','MontrealAI/skillos'); CURRENT=os.environ.get('GITHUB_RUN_ID')
LEGACY=['skillos-public-proof-command-center-refresh.yml','skillos-public-site-refresh.yml','refresh-skillos-command-center.yml','skillos-command-center-autopublisher-v2.yml','skillos-command-center-autopublisher-v3.yml','skillos-sovereign-command-center-v5.yml','skillos-flagship-governance-twin-launch.yml']
def req(url,method='GET'):
    if not TOKEN: print('No GITHUB_TOKEN; skip.'); return None
    r=urllib.request.Request(url,method=method,headers={'Authorization':f'Bearer {TOKEN}','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
    try:
        with urllib.request.urlopen(r,timeout=20) as resp: return resp.read().decode()
    except Exception as e: print('skip',url,e); return None
def main():
    data=req(f'https://api.github.com/repos/{REPO}/actions/runs?status=in_progress&per_page=100')
    if not data: return
    cancelled=[]
    for run in json.loads(data).get('workflow_runs',[]):
        if str(run.get('id'))==str(CURRENT): continue
        path=run.get('path','') or ''
        if any(x in path for x in LEGACY):
            req(f'https://api.github.com/repos/{REPO}/actions/runs/{run["id"]}/cancel',method='POST'); cancelled.append({'id':run.get('id'),'name':run.get('name'),'path':path})
    print(json.dumps({'cancelled':cancelled},indent=2))
if __name__=='__main__': main()
