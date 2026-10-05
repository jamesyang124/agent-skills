#!/usr/bin/env python3
"""Create / list / delete the Azure DevOps Service Hook subscriptions that feed the flow (stdlib only, PAT auth).

Auth : export ADO_PAT=<personal access token with "Service Hooks: Read, write, & manage" and "Code: Read">
       (No PAT? use the logged-in-browser recipe in references/ado-rest.md instead -- same endpoints, cookie auth.)

  ado_hooks.py list   --org ORG --project PROJ
  ado_hooks.py create --org ORG --project PROJ --webhook-url URL --repo NAME=BRANCH [--repo NAME=BRANCH ...]
  ado_hooks.py delete --org ORG --project PROJ --id SUBSCRIPTION_ID

`create` makes 3 subscriptions per repo, all pointing at the same flow URL:
  git.pullrequest.created (v1.0, target branch) | ms.vss-code.git-pullrequest-comment-event (v2.0, target branch)
  git.pullrequest.updated, notificationType Any (v1.0, target branch)
Existing subscriptions for the same repo/event/branch/url are skipped (idempotent).
"""
import argparse, base64, json, os, sys, urllib.request, urllib.error

def call(org, method, path, body=None):
    pat=os.environ.get('ADO_PAT')
    if not pat: sys.exit('set ADO_PAT')
    req=urllib.request.Request(f'https://dev.azure.com/{org}/{path}',method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={'Authorization':'Basic '+base64.b64encode((':'+pat).encode()).decode(),'Content-Type':'application/json','Accept':'application/json'})
    try:
        with urllib.request.urlopen(req) as r:
            t=r.read().decode(); return json.loads(t) if t else {}
    except urllib.error.HTTPError as e:
        sys.exit(f'HTTP {e.code} {method} {path}: {e.read().decode()[:400]}')

EVENTS=[('git.pullrequest.created','1.0',None,True),
        ('ms.vss-code.git-pullrequest-comment-event','2.0',None,True),
        ('git.pullrequest.updated','1.0','',True)]   # notificationType Any: ADO sends 'published' with an empty type; the flow ignores push/ref noise

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('cmd',choices=['list','create','delete'])
    ap.add_argument('--org',required=True); ap.add_argument('--project',required=True)
    ap.add_argument('--webhook-url'); ap.add_argument('--repo',action='append',default=[]); ap.add_argument('--id')
    a=ap.parse_args()
    subs=call(a.org,'GET','_apis/hooks/subscriptions?api-version=7.1')['value']
    if a.cmd=='list':
        for s in subs:
            pi=s.get('publisherInputs',{}); print(s['id'],s['eventType'],pi.get('notificationType',''),'repo=',pi.get('repository','')[:8],'branch=',pi.get('branch',''),s['consumerId'],(s.get('consumerInputs',{}).get('url') or '')[:60])
    elif a.cmd=='delete':
        call(a.org,'DELETE',f'_apis/hooks/subscriptions/{a.id}?api-version=7.1'); print('deleted',a.id)
    else:
        if not a.webhook_url or not a.repo: sys.exit('--webhook-url and --repo NAME=BRANCH required')
        proj=call(a.org,'GET',f'_apis/projects/{a.project}?api-version=7.1')['id']
        repos={r['name']:r['id'] for r in call(a.org,'GET',f'{a.project}/_apis/git/repositories?api-version=7.1')['value']}
        for spec in a.repo:
            name,branch=spec.split('=',1)
            if name not in repos: print('!! unknown repo',name); continue
            for ev,ver,nt,use_branch in EVENTS:
                pi={'projectId':proj,'repository':repos[name],'branch':branch if use_branch else ''}
                if ev=='git.pullrequest.updated': pi.update({'notificationType':nt,'pullrequestCreatedBy':'','pullrequestReviewersContains':''})
                elif ev=='git.pullrequest.created': pi.update({'pullrequestCreatedBy':'','pullrequestReviewersContains':''})
                dup=[s for s in subs if s['eventType']==ev and s['publisherInputs'].get('repository')==repos[name] and s['publisherInputs'].get('branch','')==branch and s['publisherInputs'].get('notificationType','')==(nt or '') and s.get('consumerInputs',{}).get('url')==a.webhook_url]
                if dup: print('skip existing',name,ev,nt or ''); continue
                r=call(a.org,'POST','_apis/hooks/subscriptions?api-version=7.1',{'publisherId':'tfs','eventType':ev,'resourceVersion':ver,'consumerId':'webHooks','consumerActionId':'httpRequest','publisherInputs':pi,'consumerInputs':{'url':a.webhook_url}})
                print('created',name,ev,nt or '',r['id'][:8])
if __name__=='__main__': main()
