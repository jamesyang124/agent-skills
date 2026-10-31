#!/usr/bin/env python3
"""Push an ALREADY-OPEN PR into Teams as if a `created` event had just fired (needs ADO_PAT, stdlib only).

  backfill_pr.py --org ORG --project PROJ --repo REPO --pr 123 --webhook-url URL [--dry-run]
Posts the real PR object as `resource`, with createdDate = the PR's creation date. Skips drafts. Reviews/comments made
before now are NOT replayed; later events update the card normally.
"""
import argparse, base64, json, os, sys, urllib.request
ap=argparse.ArgumentParser()
for k in ('org','project','repo','webhook-url'): ap.add_argument('--'+k,required=True)
ap.add_argument('--pr',type=int,required=True); ap.add_argument('--dry-run',action='store_true'); a=ap.parse_args()
pat=os.environ.get('ADO_PAT') or sys.exit('set ADO_PAT')
req=urllib.request.Request(f'https://dev.azure.com/{a.org}/{a.project}/_apis/git/repositories/{a.repo}/pullrequests/{a.pr}?api-version=7.1',
  headers={'Authorization':'Basic '+base64.b64encode((':'+pat).encode()).decode(),'Accept':'application/json'})
pr=json.load(urllib.request.urlopen(req))
if pr.get('isDraft'): sys.exit('PR is a draft: the flow would skip it')
if pr['status']!='active': print('note: PR status is',pr['status'])
body={'id':f'backfill-{a.pr}','eventType':'git.pullrequest.created','publisherId':'tfs','resourceVersion':'1.0','createdDate':pr['creationDate'],'resource':pr}
if a.dry_run: print(json.dumps({k:pr.get(k) for k in ('pullRequestId','title','status','targetRefName')},indent=1)); sys.exit()
r=urllib.request.urlopen(urllib.request.Request(a.webhook_url,data=json.dumps(body).encode(),headers={'Content-Type':'application/json'}))
print('webhook ->',r.status)
