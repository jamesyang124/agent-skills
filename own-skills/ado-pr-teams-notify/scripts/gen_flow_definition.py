#!/usr/bin/env python3
"""Generate the merged PR-notification Power Automate flow definition.

Input : an unzipped *export* of the template flow created from a Teams channel's
        "Send webhook alerts to a channel" Workflows template (needs the
        Microsoft.Flow/flows/<id>/definition.json that the export contains).
Output: the same package tree with `actions` replaced, plus a ready-to-import zip.

Usage : gen_flow_definition.py --export-dir EXPORT --config config.json [--out-dir build] [--no-bar]
"""
import argparse, base64, json, os, shutil, struct, zlib, glob
ap=argparse.ArgumentParser()
ap.add_argument('--export-dir',required=True,help='unzipped export package of the template flow')
ap.add_argument('--config',required=True,help='JSON with group_id, channel_id, jira_base, timezone')
ap.add_argument('--out-dir',default='build')
ap.add_argument('--no-bar',action='store_true',help='omit the left state color bar')
A=ap.parse_args()
CFG=json.load(open(A.config))
GROUP=CFG['group_id']; CHANNEL=CFG['channel_id']
JIRA=CFG.get('jira_base','https://example.atlassian.net/browse/'); TZ=CFG.get('timezone','Taipei Standard Time')
if os.path.exists(A.out_dir): shutil.rmtree(A.out_dir)
shutil.copytree(A.export_dir,A.out_dir)
P_=glob.glob(os.path.join(A.out_dir,'Microsoft.Flow/flows/*/definition.json'))[0]
def _png(rgb):
    ch=lambda t,d: struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+ch(b'IHDR',struct.pack('>IIBBBBB',1,1,8,2,0,0,0))+ch(b'IDAT',zlib.compress(b'\x00'+bytes(rgb)))+ch(b'IEND',b'')
_COL={'Open':(0x5B,0x5F,0xC7),'Approved':(0x2E,0x9E,0x4F),'Waiting for author':(0xD9,0xA4,0x00),'Rejected':(0xC4,0x31,0x4B),'Merged':(0x87,0x64,0xB8),'Abandoned':(0x60,0x5E,0x5C)}
BARS={k:base64.b64encode(_png(v)).decode() for k,v in _COL.items()}   # 1x1 PNGs used as column backgrounds
SHOW_BAR=not A.no_bar   # Teams pads background columns, so even a 1px column renders thick
d=json.load(open(P_)); defn=d['properties']['definition']
host=lambda op: {"apiId":"/providers/Microsoft.PowerApps/apis/shared_teams","connectionName":"shared_teams","operationId":op}
auth="@parameters('$authentication')"
R="triggerOutputs()?['body']?['resource']"; PRX=f"{R}?['pullRequest']"
NL="outputs('NL')"; TIME="outputs('Event_time')"
def teams(op, extra): return {"type":"OpenApiConnection","inputs":{"parameters":{"poster":"Flow bot","location":"Channel","body/recipient/groupId":GROUP,"body/recipient/channelId":CHANNEL,**extra},"host":host(op),"authentication":auth}}
def lookup(p, idexpr):
    return {f"{p}_PR_key":{"type":"Compose","inputs":f"@concat('PR #', string({idexpr}), ':')","runAfter":{}},
     f"{p}_Get_channel_messages":{"runAfter":{f"{p}_PR_key":["Succeeded"]},"type":"OpenApiConnection","inputs":{"parameters":{"groupId":GROUP,"channelId":CHANNEL},"host":host("GetMessagesFromChannel"),"authentication":auth}},
     f"{p}_Find_root_post":{"runAfter":{f"{p}_Get_channel_messages":["Succeeded"]},"type":"Query","inputs":{"from":f"@coalesce(outputs('{p}_Get_channel_messages')?['body']?['value'], json('[]'))","where":f"@contains(string(item()?['attachments']), outputs('{p}_PR_key'))"}}}
LW="105px"; BOXW="97px"   # emphasis-box inner padding ~8px, so the box columns are 8px narrower to keep text on the same x as the rows above
def row(label, val, sep=False, spacing="Small"):
    r={"type":"ColumnSet","spacing":spacing,"columns":[{"type":"Column","width":LW,"items":[{"type":"TextBlock","text":label,"weight":"Bolder","wrap":True}]},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":val,"wrap":True}]}]}
    if sep: r["separator"]=True
    return r
def rootcard(p, P):
    o=lambda n: f"@{{outputs('{p}_{n}')}}"
    oe=lambda n: f"@outputs('{p}_{n}')"
    content=[
      {"type":"TextBlock","size":"Medium","weight":"Bolder","color":"Accent","wrap":True,"maxLines":2,"text":f"{o('icon')} PR #@{{{P}?['pullRequestId']}}: @{{{P}?['title']}}"},
      {"type":"TextBlock","weight":"Bolder","spacing":"Small","wrap":True,"color":oe('chipcolor'),"text":o('chip')},
      row("Author",f"@{{{P}?['createdBy']?['displayName']}}",spacing="Small"),
      row("Repo",f"@{{{P}?['repository']?['name']}}"),
      row("Branch",o('branches')),
      row("Jira",o('jira')),
      row("Reviewers",o('votes')),
      row("Status",o('statustext')),
      {"type":"ColumnSet","separator":True,"spacing":"Medium","isVisible":f"@not(equals(outputs('{p}_summary'),' '))","columns":[
         {"type":"Column","width":LW,"items":[{"type":"TextBlock","text":"Summary","weight":"Bolder"}]},
         {"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":o('summary'),"wrap":True,"maxLines":3}]}]},
      {"type":"TextBlock","text":"Activity","weight":"Bolder","separator":True,"spacing":"Medium"},
      {"type":"ColumnSet","spacing":"Small","isVisible":f"@greater(length(outputs('{p}_acts')),0)","columns":[{"type":"Column","width":LW,"items":[{"type":"TextBlock","isSubtle":True,"size":"Small","wrap":False,"text":f"@{{if(contains(coalesce(first(skip(outputs('{p}_acts'),0)),''),'‖'),last(split(coalesce(first(skip(outputs('{p}_acts'),0)),''),'‖')),'')}}"}]},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","wrap":True,"text":f"@{{first(split(coalesce(first(skip(outputs('{p}_acts'),0)),''),'‖'))}}"}]}]},
      {"type":"ColumnSet","spacing":"Small","isVisible":f"@greater(length(outputs('{p}_acts')),1)","columns":[{"type":"Column","width":LW,"items":[{"type":"TextBlock","isSubtle":True,"size":"Small","wrap":False,"text":f"@{{if(contains(coalesce(first(skip(outputs('{p}_acts'),1)),''),'‖'),last(split(coalesce(first(skip(outputs('{p}_acts'),1)),''),'‖')),'')}}"}]},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","wrap":True,"text":f"@{{first(split(coalesce(first(skip(outputs('{p}_acts'),1)),''),'‖'))}}"}]}]},
      {"type":"ColumnSet","spacing":"Small","isVisible":f"@greater(length(outputs('{p}_acts')),2)","columns":[{"type":"Column","width":LW,"items":[{"type":"TextBlock","isSubtle":True,"size":"Small","wrap":False,"text":f"@{{if(contains(coalesce(first(skip(outputs('{p}_acts'),2)),''),'‖'),last(split(coalesce(first(skip(outputs('{p}_acts'),2)),''),'‖')),'')}}"}]},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","wrap":True,"text":f"@{{first(split(coalesce(first(skip(outputs('{p}_acts'),2)),''),'‖'))}}"}]}]},
      {"type":"ColumnSet","spacing":"Small","isVisible":f"@greater(length(outputs('{p}_acts')),3)","columns":[{"type":"Column","width":LW,"items":[{"type":"TextBlock","isSubtle":True,"size":"Small","wrap":False,"text":f"@{{if(contains(coalesce(first(skip(outputs('{p}_acts'),3)),''),'‖'),last(split(coalesce(first(skip(outputs('{p}_acts'),3)),''),'‖')),'')}}"}]},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","wrap":True,"text":f"@{{first(split(coalesce(first(skip(outputs('{p}_acts'),3)),''),'‖'))}}"}]}]},
      {"type":"ColumnSet","spacing":"Small","isVisible":f"@greater(length(outputs('{p}_acts')),4)","columns":[{"type":"Column","width":LW,"items":[{"type":"TextBlock","isSubtle":True,"size":"Small","wrap":False,"text":f"@{{if(contains(coalesce(first(skip(outputs('{p}_acts'),4)),''),'‖'),last(split(coalesce(first(skip(outputs('{p}_acts'),4)),''),'‖')),'')}}"}]},{"type":"Column","width":"stretch","items":[{"type":"TextBlock","wrap":True,"text":f"@{{first(split(coalesce(first(skip(outputs('{p}_acts'),4)),''),'‖'))}}"}]}]},
      {"type":"TextBlock","text":"Latest comment","weight":"Bolder","separator":True,"spacing":"Medium"},
      {"type":"TextBlock","wrap":True,"spacing":"Small","isVisible":f"@contains(outputs('{p}_lc_head'),'No comments yet')","text":o('lc_head')},
      {"type":"ColumnSet","spacing":"Small","isVisible":f"@not(contains(outputs('{p}_lc_head'),'No comments yet'))","columns":[
         {"type":"Column","width":LW,"items":[{"type":"TextBlock","isSubtle":True,"size":"Small","wrap":False,"text":f"@{{if(contains(outputs('{p}_lc_head'),'‖'),last(split(outputs('{p}_lc_head'),'‖')),'')}}"}]},
         {"type":"Column","width":"stretch","items":[{"type":"TextBlock","weight":"Bolder","wrap":True,"text":f"@{{first(split(outputs('{p}_lc_head'),'‖'))}}"}]}]},
      {"type":"ColumnSet","spacing":"None","isVisible":f"@not(contains(outputs('{p}_lc_head'),'No comments yet'))","columns":[
         {"type":"Column","width":LW,"items":[{"type":"TextBlock","text":" "}]},
         {"type":"Column","width":"stretch","items":[{"type":"TextBlock","wrap":True,"maxLines":2,"text":o('lc_text')}]}]},
      {"type":"ColumnSet","spacing":"None","isVisible":f"@not(contains(outputs('{p}_lc_head'),'No comments yet'))","columns":[
         {"type":"Column","width":"stretch","items":[{"type":"TextBlock","text":" "}]},
         {"type":"Column","width":"auto","items":[{"type":"TextBlock","text":f"[View comment ↗](@{{outputs('{p}_lc_url')}})","wrap":False}]}]},
      {"type":"ActionSet","spacing":"Medium","actions":[{"type":"Action.OpenUrl","title":"View in Azure DevOps","url":oe('link')}]}]
    bars=[{"type":"Column","width":"1px","isVisible":f"@equals(outputs('{p}_state'),'{st}')","backgroundImage":{"url":"data:image/png;base64,"+img,"fillMode":"Repeat"},"items":[{"type":"TextBlock","text":" "}]} for st,img in (BARS.items() if SHOW_BAR else [])]
    return {"type":"AdaptiveCard","$schema":"http://adaptivecards.io/schemas/adaptive-card.json","version":"1.4","msteams":{"width":"Full"},
     "body":[
      {"type":"ColumnSet","columns":bars+[{"type":"Column","width":"stretch","items":content}]},
      {"type":"TextBlock","id":"p_activity","isVisible":False,"text":o('activity')},
      {"type":"TextBlock","id":"p_lc_head","isVisible":False,"text":o('lc_head')},
      {"type":"TextBlock","id":"p_lc_text","isVisible":False,"text":o('lc_text')},
      {"type":"TextBlock","id":"p_lc_url","isVisible":False,"text":o('lc_url')}]}
def builder(p, P, root_ref, F, final):
    A={}; last=None
    def add(n, body):
        nonlocal last
        body=dict(body); body['runAfter']={last:["Succeeded"]} if last else {}
        A[n]=body; last=n
    comp=lambda e: {"type":"Compose","inputs":e}
    title=f"coalesce({P}?['title'],'')"
    link=f"coalesce({P}?['_links']?['web']?['href'], concat({P}?['repository']?['webUrl'],'/pullrequest/',string({P}?['pullRequestId'])))"
    add(f"{p}_link", comp(f"@{link}"))
    defaults={"pl":"","pa":"","ph":"💬 No comments yet","pt":" ","pu":f"@outputs('{p}_link')"}
    keys={"pl":"p_latest","pa":"p_activity","ph":"p_lc_head","pt":"p_lc_text","pu":"p_lc_url"}
    if root_ref:
        add(f"{p}_prev", comp(f"@if(empty(first({root_ref})?['attachments']), json('{{\"body\":[]}}'), json(first({root_ref})['attachments'][0]['content']))"))
        for k,idn in keys.items():
            add(f"{p}_f_{k}", {"type":"Query","inputs":{"from":f"@coalesce(outputs('{p}_prev')?['body'], json('[]'))","where":f"@equals(item()?['id'], '{idn}')"}})
            dv=defaults[k]; dv_expr=dv[1:] if dv.startswith('@') else f"'{dv}'"
            add(f"{p}_{k}", comp(f"@if(empty(body('{p}_f_{k}')), {dv_expr}, first(body('{p}_f_{k}'))['text'])"))
    else:
        for k,v in defaults.items(): add(f"{p}_{k}", comp(v))
    SEP="concat(outputs('NL'),outputs('NL'))"
    add(f"{p}_pact", comp(f"@if(empty(outputs('{p}_pa')),outputs('{p}_pl'),outputs('{p}_pa'))"))
    add(f"{p}_pl2", {"type":"Query","inputs":{"from":f"@split(outputs('{p}_pact'),{SEP})","where":"@not(empty(trim(item())))"}})
    newline=F['latest'](p)
    if newline is None: add(f"{p}_activity", comp(f"@join(take(body('{p}_pl2'),5),{SEP})"))
    else: add(f"{p}_activity", comp(f"@join(take(union(createArray(concat({newline[1:]},'‖',outputs('Event_time'))),body('{p}_pl2')),5),{SEP})"))
    add(f"{p}_acts", comp(f"@split(outputs('{p}_activity'),{SEP})"))
    add(f"{p}_lc_head", comp(F['lc_head'](p))); add(f"{p}_lc_text", comp(F['lc_text'](p))); add(f"{p}_lc_url", comp(F['lc_url'](p)))
    add(f"{p}_branches", comp(f"@concat(replace(coalesce({P}?['sourceRefName'],''),'refs/heads/',''),' ➔ ',replace(coalesce({P}?['targetRefName'],''),'refs/heads/',''))"))
    add(f"{p}_jira_c", comp(f"@if(and(greaterOrEquals(indexOf({title},'['),0),greater(indexOf({title},']'),indexOf({title},'['))), substring({title},add(indexOf({title},'['),1),sub(sub(indexOf({title},']'),indexOf({title},'[')),1)), '')"))
    add(f"{p}_jira_k", comp(f"@if(and(greater(length(outputs('{p}_jira_c')),0),lessOrEquals(length(outputs('{p}_jira_c')),20),contains(outputs('{p}_jira_c'),'-'),not(contains(outputs('{p}_jira_c'),' '))), outputs('{p}_jira_c'), '')"))
    add(f"{p}_jira", comp(f"@if(empty(outputs('{p}_jira_k')),'—',concat('[',outputs('{p}_jira_k'),']({JIRA}',outputs('{p}_jira_k'),')'))"))
    add(f"{p}_rv_f", {"type":"Query","inputs":{"from":f"@coalesce({P}?['reviewers'], json('[]'))","where":"@not(equals(item()?['isContainer'], true))"}})
    add(f"{p}_rv_s", {"type":"Select","inputs":{"from":f"@body('{p}_rv_f')","select":"@concat(if(or(equals(item()?['vote'],10),equals(item()?['vote'],5)),'👍 ',if(equals(item()?['vote'],-10),'👎 ',if(equals(item()?['vote'],-5),'⏳ ','👀 '))),item()?['displayName'])"}})
    add(f"{p}_votes", comp(f"@if(empty(body('{p}_rv_s')),'—',join(body('{p}_rv_s'),' · '))"))
    add(f"{p}_rj", {"type":"Query","inputs":{"from":f"@body('{p}_rv_f')","where":"@equals(item()?['vote'],-10)"}})
    add(f"{p}_wt", {"type":"Query","inputs":{"from":f"@body('{p}_rv_f')","where":"@equals(item()?['vote'],-5)"}})
    add(f"{p}_ap", {"type":"Query","inputs":{"from":f"@body('{p}_rv_f')","where":"@or(equals(item()?['vote'],10),equals(item()?['vote'],5))"}})
    st=f"{P}?['status']"; ms=f"coalesce({P}?['mergeStatus'],'')"
    add(f"{p}_state", comp(f"@if(equals({st},'completed'),'Merged',if(equals({st},'abandoned'),'Abandoned',if(greater(length(body('{p}_rj')),0),'Rejected',if(greater(length(body('{p}_wt')),0),'Waiting for author',if(greater(length(body('{p}_ap')),0),'Approved','Open')))))"))
    S=f"outputs('{p}_state')"
    add(f"{p}_chip", comp(f"@concat(if(equals({S},'Merged'),'🟣 ',if(equals({S},'Abandoned'),'⚫ ',if(equals({S},'Rejected'),'🔴 ',if(equals({S},'Waiting for author'),'🟡 ',if(equals({S},'Approved'),'🟢 ','🔵 '))))),{S})"))
    add(f"{p}_chipcolor", comp(f"@if(equals({S},'Merged'),'Default',if(equals({S},'Abandoned'),'Default',if(equals({S},'Rejected'),'Attention',if(equals({S},'Waiting for author'),'Warning',if(equals({S},'Approved'),'Good','Accent')))))"))
    add(f"{p}_barstyle", comp(f"@if(equals({S},'Abandoned'),'emphasis',if(equals({S},'Rejected'),'attention',if(equals({S},'Waiting for author'),'warning',if(equals({S},'Approved'),'good','accent'))))"))
    add(f"{p}_ismerged", comp(f"@equals({S},'Merged')"))
    add(f"{p}_statustext", comp(f"@if(equals({st},'completed'),if(equals({ms},'succeeded'),'Completed · merged cleanly','Completed'),if(equals({st},'abandoned'),'Abandoned',if(equals({ms},'conflicts'),'Active · ⚠️ merge conflicts',if(equals({ms},'succeeded'),'Active · no merge conflicts','Active'))))"))
    add(f"{p}_sd", comp(f"@replace(coalesce({P}?['description'],''),decodeUriComponent('%0D'),'')"))
    add(f"{p}_ss", comp(f"@if(contains(toLower(outputs('{p}_sd')),'## summary'), first(split(join(skip(split(substring(outputs('{p}_sd'),indexOf(toLower(outputs('{p}_sd')),'## summary')),{NL}),1),{NL}),concat({NL},'#'))), outputs('{p}_sd'))"))
    add(f"{p}_sl", {"type":"Query","inputs":{"from":f"@split(outputs('{p}_ss'),{NL})","where":"@and(not(empty(trim(item()))),not(startsWith(trim(item()),'http')),not(startsWith(trim(item()),'#')),not(startsWith(toLower(trim(item())),'jira')))"}})
    add(f"{p}_sj", comp(f"@join(take(body('{p}_sl'),3),' ')"))
    add(f"{p}_summary", comp(f"@if(empty(outputs('{p}_sj')),' ',if(greater(length(outputs('{p}_sj')),320),concat(substring(outputs('{p}_sj'),0,320),'…'),outputs('{p}_sj')))"))
    add(f"{p}_icon", comp(f"@if(equals({P}?['status'],'completed'),'✅',if(equals({P}?['status'],'abandoned'),'🗑️','🚀'))"))
    add(f"{p}_card", comp(rootcard(p,P)))
    if final=='post': add(f"{p}_post", teams("PostCardToConversation",{"body/messageBody":f"@string(outputs('{p}_card'))"}))
    else: add(f"{p}_update", teams("UpdateCardInConversation",{"body/messageId":final[1],"body/messageBody":f"@string(outputs('{p}_card'))"}))
    return A, last
notDraft=lambda e: {"and":[{"not":{"equals":[f"@coalesce({e}?['isDraft'], false)", True]}}]}
def reply(name, after, parent, html):
    a=teams("ReplyWithMessageToConversation",{"body/parentMessageId":parent,"body/messageBody":html}); a["runAfter"]={after:["Succeeded","Failed"]}; return {name:a}
opened=lambda p:f"@concat('🚀 **',{R}?['createdBy']?['displayName'],'** opened a PR')"
keep=dict(lc_head=lambda p:f"@outputs('{p}_ph')",lc_text=lambda p:f"@outputs('{p}_pt')",lc_url=lambda p:f"@outputs('{p}_pu')")
# ---- created
CA,_=builder("Cre", R, None, {"latest":opened,**keep}, 'post')
created={"case":"git.pullrequest.created","actions":{"Created_not_draft":{"type":"If","expression":notDraft(R),"actions":CA,"else":{"actions":{}}}}}
# ---- updated
MSGF="coalesce(triggerOutputs()?['body']?['message']?['text'], triggerOutputs()?['body']?['detailedMessage']?['text'], '')"
upd=lookup("Upd", f"{R}?['pullRequestId']")
def after(prev): return {prev:["Succeeded"]}
upd["Upd_ml"]={"runAfter":after("Upd_Find_root_post"),"type":"Compose","inputs":f"@toLower({MSGF})"}
K="outputs('Upd_kind')"; ML="outputs('Upd_ml')"; STU=f"{R}?['status']"
upd["Upd_kind"]={"runAfter":after("Upd_ml"),"type":"Compose","inputs":f"@if(equals({STU},'completed'),'merged',if(equals({STU},'abandoned'),'abandoned',if(contains({ML},'with suggestions'),'sugg',if(contains({ML},'approved'),'approved',if(contains({ML},'rejected'),'rejected',if(contains({ML},'waiting'),'waiting','other'))))))"}
upd["Upd_base"]={"runAfter":after("Upd_kind"),"type":"Compose","inputs":f"@if(greater(indexOf({MSGF},' pull request'),0), substring({MSGF},0,indexOf({MSGF},' pull request')), {MSGF})"}
B="outputs('Upd_base')"
markers=[' approved',' rejected',' completed',' abandoned',' is waiting',' waiting',' voted',' updated',' set ',' published',' reactivated',' added',' removed',' changed',' marked']
cands=",".join(f"if(greater(indexOf({B},'{m}'),0),indexOf({B},'{m}'),9999)" for m in markers)
upd["Upd_cut"]={"runAfter":after("Upd_base"),"type":"Compose","inputs":f"@min({cands})"}
upd["Upd_name"]={"runAfter":after("Upd_cut"),"type":"Compose","inputs":f"@trim(if(less(outputs('Upd_cut'),9999),substring({B},0,outputs('Upd_cut')),{B}))"}
def pick(table, default):
    e=f"'{default}'"
    for k,v in reversed(list(table.items())): e=f"if(equals({K},'{k}'),'{v}',{e})"
    return "@"+e
upd["Upd_icon"]={"runAfter":after("Upd_name"),"type":"Compose","inputs":pick({"merged":"🎉","abandoned":"🗑️","sugg":"✅","approved":"✅","rejected":"💔","waiting":"⏳"},"🔔")}
upd["Upd_phrase"]={"runAfter":after("Upd_icon"),"type":"Compose","inputs":pick({"merged":" merged it","abandoned":" abandoned this PR","sugg":" approved with suggestions","approved":" approved. Ship it!","rejected":" rejected this with a heavy heart","waiting":" is waiting for the author"}," updated this PR")}
upd["Upd_md"]={"runAfter":after("Upd_phrase"),"type":"Compose","inputs":"@concat(outputs('Upd_icon'),' **',outputs('Upd_name'),'**',outputs('Upd_phrase'))"}
upd["Upd_html"]={"runAfter":after("Upd_md"),"type":"Compose","inputs":"@concat(outputs('Upd_icon'),' <b>',outputs('Upd_name'),'</b>',outputs('Upd_phrase'))"}
UA,ulast=builder("UpdR", R, "body('Upd_Find_root_post')", {"latest":lambda p:"@outputs('Upd_md')",**keep}, ('update',"@first(body('Upd_Find_root_post'))?['id']"))
UA.update(reply("Upd_reply", ulast, "@first(body('Upd_Find_root_post'))?['id']", "@outputs('Upd_html')"))
LA,_=builder("Late", R, None, {"latest":opened,**keep}, 'post')
upd["Upd_Root_post_found"]={"runAfter":after("Upd_html"),"type":"If","expression":{"and":[{"greater":["@length(body('Upd_Find_root_post'))",0]}]},"actions":UA,
  "else":{"actions":{"Published_or_unknown_active_PR":{"type":"If","expression":{"and":[{"equals":[f"@{R}?['status']","active"]},{"not":{"equals":[f"@coalesce({R}?['isDraft'], false)",True]}}]},"actions":LA,"else":{"actions":{}}}}}}
updated={"case":"git.pullrequest.updated","actions":upd}
# ---- commented
CMT=f"coalesce({R}?['comment']?['content'],'')"
flat=f"replace(replace({CMT},decodeUriComponent('%0D'),' '),{NL},' ')"
CN=f"{R}?['comment']?['author']?['displayName']"
cm=lookup("Cmt", f"{PRX}?['pullRequestId']")
cm["Cmt_text"]={"runAfter":after("Cmt_Find_root_post"),"type":"Compose","inputs":f"@if(greater(length({flat}),200), concat(substring({flat},0,200),'…'), {flat})"}
cm["Cmt_quote"]={"runAfter":after("Cmt_text"),"type":"Compose","inputs":"@replace(replace(if(greater(length(outputs('Cmt_text')),140),concat(substring(outputs('Cmt_text'),0,140),'…'),outputs('Cmt_text')),'<','&lt;'),'>','&gt;')"}
cm["Cmt_thread"]={"runAfter":after("Cmt_quote"),"type":"Compose","inputs":f"@if(empty({R}?['comment']?['_links']?['threads']?['href']),'',last(split(first(split({R}?['comment']?['_links']?['threads']?['href'],'?')),'/')))"}
CF={"latest":lambda p:None,"lc_head":lambda p:f"@concat('💬 ',{CN},'‖',{TIME})","lc_text":lambda p:"@outputs('Cmt_text')",
    "lc_url":lambda p:f"@if(empty(outputs('Cmt_thread')),outputs('{p}_link'),concat(outputs('{p}_link'),'?_a=overview&discussionId=',outputs('Cmt_thread')))"}
FA,flast=builder("CmtR", PRX, "body('Cmt_Find_root_post')", CF, ('update',"@first(body('Cmt_Find_root_post'))?['id']"))
FA.update(reply("Cmt_reply", flast, "@first(body('Cmt_Find_root_post'))?['id']", f"@concat('💬 <b>',{CN},'</b> left a comment<br/><i>“',outputs('Cmt_quote'),'”</i>')"))
NA,_=builder("CmtN", PRX, None, CF, 'post')
cm["Cmt_Root_post_found"]={"runAfter":after("Cmt_thread"),"type":"If","expression":{"and":[{"greater":["@length(body('Cmt_Find_root_post'))",0]}]},"actions":FA,"else":{"actions":NA}}
commented={"case":"ms.vss-code.git-pullrequest-comment-event","actions":{"Comment_not_draft":{"type":"If","expression":notDraft(PRX),"actions":cm,"else":{"actions":{}}}}}
acts={"Do_Not_Remove_FlowIL":defn['actions']['Do_Not_Remove_FlowIL']}   # keep the template's marker action
acts["NL"]={"runAfter":{"Do_Not_Remove_FlowIL":["Succeeded"]},"type":"Compose","inputs":"@decodeUriComponent('%0A')"}
acts["Event_time"]={"runAfter":{"NL":["Succeeded"]},"type":"Compose","inputs":"@formatDateTime(convertTimeZone(coalesce(triggerOutputs()?['body']?['createdDate'], utcNow()),'UTC','"+TZ+"'),'M/d HH:mm')"}
acts["Event_type"]={"runAfter":{"Event_time":["Succeeded"]},"type":"Compose","inputs":"@coalesce(triggerOutputs()?['body']?['eventType'], '')"}
acts["Switch_on_event"]={"runAfter":{"Event_type":["Succeeded"]},"type":"Switch","expression":"@outputs('Event_type')","default":{"actions":{}},
  "cases":{"PR_created":created,"PR_updated":updated,"PR_commented":commented}}
defn['actions']=acts
defn['triggers']['manual']['inputs']['schema']={"type":"object","properties":{}}   # accept any Azure DevOps payload
json.dump(d,open(P_,'w'),ensure_ascii=False,indent=1); s=open(P_).read(); json.loads(s)
shutil.make_archive(os.path.join(A.out_dir,'..','flow-package'),'zip',A.out_dir); print('zip:',os.path.abspath(os.path.join(A.out_dir,'..','flow-package.zip')))
names=[]
def walk(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k=='actions' and isinstance(v,dict): names.extend(v.keys())
            walk(v)
    elif isinstance(o,list):
        for x in o: walk(x)
walk(defn['actions']); dup={n for n in names if names.count(n)>1}
print("v13 ok | actions:",len(names),"| duplicates:",dup or "none","| bytes:",len(s))
