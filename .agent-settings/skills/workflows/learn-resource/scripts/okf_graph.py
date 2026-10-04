#!/usr/bin/env python3
"""OKF bundle -> graph.html (typed concept graph, d3 force layout, single file).
Usage: okf_graph.py <bundle-dir> [out.html] [--title "Title"]
Reads concept files (frontmatter + '# Related Concepts' lines of the form
`- [Title](rel/path.md): relation-type: text`). Nothing here is topic specific."""
import sys, re, os, json, pathlib

args = [a for a in sys.argv[1:] if not a.startswith("--")]
title = "Knowledge graph"
if "--title" in sys.argv:
    title = sys.argv[sys.argv.index("--title") + 1]; args = [a for a in args if a != title]
bundle = pathlib.Path(args[0]).resolve()
out = pathlib.Path(args[1]) if len(args) > 1 else bundle / "graph.html"

def fm_split(s):
    m = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", s, re.S)
    return (m[1], m[2]) if m else ("", s)

def scalar(fm, key):
    m = re.search(rf"^{key}:\s*(.*)$", fm, re.M)
    if not m: return ""
    v = m[1].strip()
    return v[1:-1] if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'" else v

def block_list(fm, key):
    m = re.search(rf"^{key}:\n((?:  - .*\n?)+)", fm, re.M)
    if m: return [x.strip()[2:].strip().strip('"') for x in m[1].strip().split("\n")]
    m = re.search(rf"^{key}:\s*\[(.*)\]\s*$", fm, re.M)
    return [x.strip().strip('"') for x in m[1].split(",") if x.strip()] if m else []

nodes, edges = {}, []
files = [p for p in bundle.rglob("*.md") if p.name not in ("index.md", "log.md") and ".okf" not in p.parts]
for p in files:
    cid = str(p.relative_to(bundle).with_suffix(""))
    fm, body = fm_split(p.read_text())
    related = ""
    if "# Related Concepts" in body:
        body, related = body.split("# Related Concepts", 1)
    nodes[cid] = {"id": cid, "title": scalar(fm, "title") or cid, "type": scalar(fm, "type") or "Concept",
                  "desc": scalar(fm, "description"), "scope": block_list(fm, "scope"),
                  "tags": block_list(fm, "tags"), "evidence": block_list(fm, "evidence"),
                  "status": scalar(fm, "status"), "body": body.strip()}
    for line in related.split("\n"):
        m = re.match(r"^- \[(.+?)\]\((.+?)\.md\): ([a-z][a-z-]*): (.*)$", line.strip())
        if m:
            tgt = os.path.normpath(os.path.join(os.path.dirname(cid), m[2]))
            edges.append({"source": cid, "target": tgt, "type": m[3], "text": m[4]})
edges = [e for e in edges if e["target"] in nodes]
for e in edges:
    for k in ("source", "target"): nodes[e[k]]["deg"] = nodes[e[k]].get("deg", 0) + 1
data = {"title": title, "nodes": list(nodes.values()), "edges": edges}

HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
:root{--bg:#fff;--fg:#1f2328;--mut:#656d76;--bd:#d0d7de;--cd:#f6f8fa;--ac:#0969da}
@media(prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#e6edf3;--mut:#8d96a0;--bd:#30363d;--cd:#161b22;--ac:#58a6ff}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,system-ui,sans-serif}
header{padding:12px 16px;border-bottom:1px solid var(--bd);display:flex;flex-wrap:wrap;gap:10px;align-items:center}
header h1{font-size:17px;margin:0 12px 0 0}
input[type=search]{padding:6px 10px;border:1px solid var(--bd);border-radius:6px;background:var(--cd);color:var(--fg);min-width:200px}
.chip{border:1px solid var(--bd);border-radius:14px;padding:2px 10px;font-size:12px;cursor:pointer;background:var(--cd);user-select:none}
.chip.off{opacity:.35;text-decoration:line-through}
.chip i{display:inline-block;width:18px;height:0;border-top:3px solid;vertical-align:middle;margin-right:5px}
.chip b{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;vertical-align:middle}
#row{display:flex;flex-wrap:wrap;gap:6px;padding:8px 16px;border-bottom:1px solid var(--bd)}
#main{display:flex;height:calc(100vh - 150px);min-height:520px}
#svgwrap{flex:1;min-width:0;position:relative}svg{width:100%;height:100%;display:block}
#panel{width:380px;max-width:45%;border-left:1px solid var(--bd);overflow:auto;padding:14px 16px;background:var(--cd)}
#panel h2{margin:0 0 4px;font-size:18px}#panel .meta{color:var(--mut);font-size:12px;margin-bottom:8px}
#panel ul{padding-left:18px}#panel a{color:var(--ac)}#panel li{margin:3px 0}
.rel{cursor:pointer;color:var(--ac)}.t{font-size:11px;color:var(--mut)}
.node text{font-size:11px;fill:var(--fg);pointer-events:none;paint-order:stroke;stroke:var(--bg);stroke-width:3px}
.node circle{stroke:var(--bg);stroke-width:1.5px;cursor:pointer}
.link{fill:none;stroke-opacity:.75}.dim{opacity:.12}
@media(max-width:800px){#main{flex-direction:column;height:auto}#svgwrap{height:60vh}#panel{width:100%;max-width:none;border-left:0;border-top:1px solid var(--bd)}}
</style></head><body>
<header><h1>__TITLE__</h1><input id="q" type="search" placeholder="Search concepts..."><span id="count" class="t"></span></header>
<div id="row"></div>
<div id="main"><div id="svgwrap"><svg id="svg"></svg></div><div id="panel"><p class="t">Click a concept. Drag to move, scroll to zoom. Chips toggle relation types, concept types and scopes.</p></div></div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script>
const DATA=__DATA__;
const REL={solves:["#2da44e",""],causes:["#d4731a",""],requires:["#8c959f",""],refines:["#0969da",""],"part-of":["#a0a8b0",""],
 "alternative-to":["#8250df","6 4"],"trade-off-with":["#bf3989","6 4"],contradicts:["#cf222e","3 3"],mitigates:["#1a7f37","2 3"],enables:["#0a7ea4",""]};
const TYPEC=d3.scaleOrdinal(["#0969da","#cf222e","#8250df","#2da44e","#d4731a","#bf3989","#0a7ea4","#6e7781"]);
const nodes=DATA.nodes.map(d=>({...d})),byId=Object.fromEntries(nodes.map(d=>[d.id,d]));
const links=DATA.edges.map(e=>({...e}));
const off={rel:new Set(),type:new Set(),scope:new Set()};let sel=null,q="";
const types=[...new Set(nodes.map(n=>n.type))].sort(),scopes=[...new Set(nodes.flatMap(n=>n.scope))].sort();
const usedRel=[...new Set(links.map(l=>l.type))].sort();
const row=document.getElementById("row");
function chip(kind,key,html){const c=document.createElement("span");c.className="chip";c.innerHTML=html;
 c.onclick=()=>{off[kind].has(key)?off[kind].delete(key):off[kind].add(key);c.classList.toggle("off");update()};row.appendChild(c)}
usedRel.forEach(r=>chip("rel",r,`<i style="border-color:${(REL[r]||["#888"])[0]}"></i>${r}`));
types.forEach(t=>chip("type",t,`<b style="background:${TYPEC(t)}"></b>${t}`));
scopes.forEach(s=>chip("scope",s,`scope ${s}`));
const svg=d3.select("#svg"),g=svg.append("g");
const defs=svg.append("defs");
Object.entries(REL).forEach(([k,[c]])=>defs.append("marker").attr("id","a-"+k).attr("viewBox","0 -5 10 10").attr("refX",20).attr("refY",0).attr("markerWidth",6).attr("markerHeight",6).attr("orient","auto").append("path").attr("d","M0,-4L10,0L0,4").attr("fill",c));
const link=g.append("g").selectAll("path").data(links).join("path").attr("class","link")
 .attr("stroke",d=>(REL[d.type]||["#888"])[0]).attr("stroke-width",1.6).attr("stroke-dasharray",d=>(REL[d.type]||["",""])[1])
 .attr("marker-end",d=>REL[d.type]?`url(#a-${d.type})`:null);
link.append("title").text(d=>`${byId[d.source.id||d.source].title} ${d.type} ${byId[d.target.id||d.target].title}: ${d.text}`);
const node=g.append("g").selectAll("g").data(nodes).join("g").attr("class","node")
 .call(d3.drag().on("start",(e,d)=>{if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y}).on("drag",(e,d)=>{d.fx=e.x;d.fy=e.y}).on("end",(e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=d.fy=null}))
 .on("click",(e,d)=>{sel=d.id;show(d);update()});
node.append("circle").attr("r",d=>6+Math.min(12,(d.deg||0)*1.4)).attr("fill",d=>TYPEC(d.type));
node.append("text").attr("dx",d=>9+Math.min(12,(d.deg||0)*1.4)).attr("dy",3).text(d=>d.title);
node.append("title").text(d=>d.desc);
const W=()=>document.getElementById("svgwrap").clientWidth,H=()=>document.getElementById("svgwrap").clientHeight;
const sim=d3.forceSimulation(nodes).force("link",d3.forceLink(links).id(d=>d.id).distance(95).strength(.5))
 .force("charge",d3.forceManyBody().strength(-340)).force("center",d3.forceCenter(W()/2,H()/2)).force("collide",d3.forceCollide(26))
 .force("x",d3.forceX(W()/2).strength(.06)).force("y",d3.forceY(H()/2).strength(.09)).stop();
function ticked(){link.attr("d",d=>{const dx=d.target.x-d.source.x,dy=d.target.y-d.source.y,r=Math.hypot(dx,dy)*1.6;return`M${d.source.x},${d.source.y}A${r},${r} 0 0,1 ${d.target.x},${d.target.y}`});
  node.attr("transform",d=>`translate(${d.x},${d.y})`)}
const zoom=d3.zoom().scaleExtent([.2,4]).on("zoom",e=>g.attr("transform",e.transform));svg.call(zoom);
function fit(){const b=g.node().getBBox();if(!b.width)return;const w=W(),h=H(),k=Math.min(2,.92*Math.min(w/b.width,h/b.height));
 svg.call(zoom.transform,d3.zoomIdentity.translate(w/2-k*(b.x+b.width/2),h/2-k*(b.y+b.height/2)).scale(k))}
for(let i=0;i<320;i++)sim.tick();ticked();fit();sim.on("tick",ticked);
window.addEventListener("resize",fit);
function visible(n){return !off.type.has(n.type)&&!(n.scope.length&&n.scope.every(s=>off.scope.has(s)))&&(!q||(n.title+" "+n.desc+" "+n.id+" "+n.tags.join(" ")).toLowerCase().includes(q))}
function update(){const vis=new Set(nodes.filter(visible).map(n=>n.id));
 const nb=new Set();if(sel){nb.add(sel);links.forEach(l=>{const s=l.source.id,t=l.target.id;if(s===sel)nb.add(t);if(t===sel)nb.add(s)})}
 node.classed("dim",d=>!vis.has(d.id)||(sel&&!nb.has(d.id)));
 link.classed("dim",l=>off.rel.has(l.type)||!vis.has(l.source.id)||!vis.has(l.target.id)||(sel&&l.source.id!==sel&&l.target.id!==sel));
 document.getElementById("count").textContent=`${vis.size}/${nodes.length} concepts, ${links.length} relations`}
function show(d){const out=links.filter(l=>l.source.id===d.id),inn=links.filter(l=>l.target.id===d.id);
 const rl=(l,o)=>`<li><span class="t">${l.type}</span> <span class="rel" data-id="${o.id}">${o.title}</span><br><span class="t">${l.text}</span></li>`;
 const ev=d.evidence.length?`<p class="t">Evidence: ${d.evidence.join(" · ")}</p>`:"";
 document.getElementById("panel").innerHTML=`<h2>${d.title}</h2><div class="meta">${d.type}${d.scope.length?" · scope "+d.scope.join(", "):""} · <code>${d.id}</code></div><p>${d.desc}</p>${marked.parse(d.body)}
 <h3 style="font-size:14px">Outgoing</h3><ul>${out.map(l=>rl(l,l.target)).join("")||"<li class=t>none</li>"}</ul>
 <h3 style="font-size:14px">Incoming</h3><ul>${inn.map(l=>rl(l,l.source)).join("")||"<li class=t>none</li>"}</ul>`;
 document.querySelectorAll("#panel .rel").forEach(e=>e.onclick=()=>{const n=byId[e.dataset.id];sel=n.id;show(n);update()});
 document.querySelectorAll("#panel a").forEach(a=>a.target="_blank")}
document.getElementById("q").oninput=e=>{q=e.target.value.trim().toLowerCase();update()};
update();window.__graph={nodes:nodes.length,edges:links.length};window.__errors=[];window.__done=true;
</script></body></html>'''
out.write_text(HTML.replace("__TITLE__", title).replace("__DATA__", json.dumps(data).replace("</", "<\\/")))
print(f"wrote {out}: {len(data['nodes'])} nodes, {len(edges)} edges")
