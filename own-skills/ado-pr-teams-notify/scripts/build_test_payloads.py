#!/usr/bin/env python3
"""Write one sample ADO webhook payload per PR state so the flow can be verified end to end.

  build_test_payloads.py --out DIR --pr 999900 --repo my-repo --org-url https://dev.azure.com/ORG/PROJECT [--jira PROJ-1234]

Files (send in this order, ~30 s apart): 01_open 02_conflict 03_waiting 04_rejected 05_approved_sugg 06_approved
07_comment 08_merged 09_abandoned 10_draft (must NOT post).
"""
import argparse, copy, json, os
ap=argparse.ArgumentParser(); ap.add_argument('--out',required=True); ap.add_argument('--pr',type=int,default=999900)
ap.add_argument('--repo',default='my-repo'); ap.add_argument('--org-url',required=True); ap.add_argument('--jira',default='PROJ-1'); ap.add_argument('--target',default='main')
A=ap.parse_args(); os.makedirs(A.out,exist_ok=True)
web=f'{A.org_url}/_git/{A.repo}'; T=f'[{A.jira}] flow test: all PR states'
base={'id':'t','eventType':'git.pullrequest.created','publisherId':'tfs','resourceVersion':'1.0','createdDate':'2026-01-01T08:00:00Z',
 'resource':{'pullRequestId':A.pr,'title':T,'status':'active','mergeStatus':'succeeded','isDraft':False,
  'description':f'Jira: https://example.invalid/browse/{A.jira}\n\n## Summary\nFirst summary line.\nSecond summary line.\nThird summary line.\nFourth line must not show.\n\n## Changes\n- not in summary',
  'createdBy':{'displayName':'Alice Dev'},'sourceRefName':'refs/heads/feature/flow-test','targetRefName':f'refs/heads/{A.target}',
  'repository':{'name':A.repo,'webUrl':web},
  'reviewers':[{'displayName':'Bob Reviewer','vote':0},{'displayName':'Carol Reviewer','vote':0},{'displayName':'Some Group','isContainer':True,'vote':0}],
  '_links':{'web':{'href':f'{web}/pullrequest/{A.pr}'}}}}
def ev(cid,kind,text,minute,votes=None,**r):
    e=copy.deepcopy(base); e['id']=cid; e['eventType']=kind; e['createdDate']=f'2026-01-01T08:{minute:02d}:00Z'
    if votes: e['resource']['reviewers'][0]['vote'],e['resource']['reviewers'][1]['vote']=votes
    e['resource'].update(r)
    if text: e['message']={'text':text}; e['detailedMessage']=e['message']
    return e
U='git.pullrequest.updated'; sfx=f'pull request {A.pr} ({T})'
steps=[('01_open',base),
 ('02_conflict',ev('c',U,f'Alice Dev updated {sfx}',1,mergeStatus='conflicts')),
 ('03_waiting',ev('w',U,f'Carol Reviewer voted waiting for author on {sfx}',2,(0,-5))),
 ('04_rejected',ev('r',U,f'Carol Reviewer rejected {sfx}',3,(0,-10))),
 ('05_approved_sugg',ev('s',U,f'Carol Reviewer approved with suggestions {sfx}',4,(0,5))),
 ('06_approved',ev('a',U,f'Carol Reviewer approved {sfx}',5,(10,10)))]
cm=copy.deepcopy(base); cm.update(id='k',eventType='ms.vss-code.git-pullrequest-comment-event',resourceVersion='2.0',createdDate='2026-01-01T08:06:00Z')
pr=copy.deepcopy(cm['resource']); pr['reviewers'][0]['vote']=10; pr['reviewers'][1]['vote']=10
cm['resource']={'comment':{'id':1,'content':'Looks good.\nSecond line, <b>html</b> must be escaped in the reply.','author':{'displayName':'Bob Reviewer'},
  '_links':{'threads':{'href':f'{A.org_url}/_apis/git/repositories/r/pullRequests/{A.pr}/threads/777'}}},'pullRequest':pr}
steps+=[('07_comment',cm),('08_merged',ev('m',U,f'Bob Reviewer completed {sfx}',7,(10,10),status='completed',mergeStatus='succeeded')),
 ('09_abandoned',ev('x',U,f'Bob Reviewer abandoned {sfx}',8,(10,10),status='abandoned'))]
dr=copy.deepcopy(base); dr['id']='d'; dr['resource'].update(pullRequestId=A.pr+1,isDraft=True,title='[TEST] draft must not post'); steps.append(('10_draft',dr))
for n,p in steps: json.dump(p,open(os.path.join(A.out,n+'.json'),'w'),ensure_ascii=False)
print('wrote',len(steps),'payloads to',A.out)
