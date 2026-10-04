#!/usr/bin/env python3
"""notes.md -> notes.html (marked + mermaid via CDN). Also deep-links [m:ss] timestamps for YouTube sources.
Usage: build_html.py path/to/notes.md"""
import sys, re, pathlib

def link_timestamps(md):
    """Deep-link timestamps (idempotent, skips code fences).
    Single video: frontmatter source_url (YouTube) -> [m:ss] / [h:mm:ss] / [a-b] / [a, b] become links.
    Multi video (master): frontmatter `video_sources: slug=VIDEOID, slug2=VIDEOID2` -> `slug [m:ss, m:ss]` becomes `slug` + deep links."""
    fm = re.match(r"\A---\n(.*?)\n---\n", md, flags=re.S)
    if not fm: return md
    head = fm[1]
    ts = r"(?:\d+:)?\d{1,2}:\d{2}"
    item = rf"{ts}(?:\s*[\u2013-]\s*{ts})?"
    lst = rf"{item}(?:\s*,\s*{item})*"
    def secs(t):
        parts = [int(x) for x in t.split(":")]
        return sum(p * 60 ** i for i, p in enumerate(reversed(parts)))
    def mk(base):
        def conv(items):
            return ", ".join(f"[{it}]({base}&t={secs(re.match(ts, it)[0])}s)" for it in re.split(r"\s*,\s*", items))
        return conv
    rules = []  # (compiled pattern, replacement fn)
    vs = re.search(r"^video_sources:\s*(.+)$", head, re.M)
    if vs:
        ids = dict(x.strip().split("=", 1) for x in vs[1].split(",") if "=" in x)
        for slug, vid in ids.items():
            conv = mk("https://www.youtube.com/watch?v=" + vid.strip())
            rules.append((re.compile(rf"\b{re.escape(slug)}\s+\[({lst})\](?!\()"),
                          lambda m, conv=conv, slug=slug: f"{slug} " + conv(m[1])))
    url = (re.search(r"^source_url:\s*(\S+)", head, re.M) or [None, ""])[1]
    vid = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", url)
    if vid and "youtu" in url:
        conv = mk("https://www.youtube.com/watch?v=" + vid[1])
        rules.append((re.compile(rf"\[({lst})\](?!\()"), lambda m, conv=conv: conv(m[1])))
    if not rules: return md
    out, fence = [], False
    for line in md.split("\n"):
        if line.startswith("```"): fence = not fence
        if not fence:
            for pat, fn in rules: line = pat.sub(fn, line)
        out.append(line)
    return "\n".join(out)

p = pathlib.Path(sys.argv[1]); md = p.read_text()
linked = link_timestamps(md)
if linked != md: p.write_text(linked); md = linked  # persist links in the .md too
md = re.sub(r"\A---\n.*?\n---\n", "", md, flags=re.S)  # drop frontmatter
title = (re.search(r"^# (.+)$", md, re.M) or [None, p.stem])[1]
body = md.replace("</script>", "<\\/script>")
html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root{{--bg:#fff;--fg:#1f2328;--mut:#656d76;--bd:#d0d7de;--cd:#f6f8fa;--ac:#0969da}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0d1117;--fg:#e6edf3;--mut:#8d96a0;--bd:#30363d;--cd:#161b22;--ac:#58a6ff}}}}
body{{background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,system-ui,sans-serif;margin:0}}
main{{max-width:920px;margin:0 auto;padding:24px 16px 80px}}
a{{color:var(--ac)}} h1,h2,h3{{line-height:1.25}} h2{{border-bottom:1px solid var(--bd);padding-bottom:.3em;margin-top:2em}}
table{{border-collapse:collapse;display:block;overflow-x:auto}} td,th{{border:1px solid var(--bd);padding:6px 12px;text-align:left;vertical-align:top}} th{{background:var(--cd)}}
code{{background:var(--cd);padding:.15em .35em;border-radius:4px;font-size:90%}} pre{{background:var(--cd);padding:12px;overflow:auto;border-radius:6px}} pre code{{background:none;padding:0}}
blockquote{{border-left:4px solid var(--bd);margin:0;padding:0 1em;color:var(--mut)}}
.mermaid{{background:var(--cd);border-radius:6px;padding:12px;overflow-x:auto;text-align:center}}
</style></head><body><main id="out"></main>
<script id="md" type="text/markdown">{body}</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<script type="module">
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
const out=document.getElementById("out");
out.innerHTML=marked.parse(document.getElementById("md").textContent);
mermaid.initialize({{startOnLoad:false,theme:matchMedia("(prefers-color-scheme:dark)").matches?"dark":"default"}});
window.__errors=[];
let i=0;
for (const c of [...out.querySelectorAll("pre > code.language-mermaid")]) {{
  const d=document.createElement("div"); d.className="mermaid"; c.parentElement.replaceWith(d);
  try {{ const r=await mermaid.render("m"+(i++), c.textContent); d.innerHTML=r.svg; }}
  catch(e) {{ d.innerHTML="<pre style='color:#c00;text-align:left'>Mermaid error: "+String(e.message||e).replace(/</g,"&lt;")+"</pre>"; window.__errors.push({{n:i,msg:String(e.message||e).slice(0,200),src:c.textContent.slice(0,60)}}); }}
}}
window.__done=true;
</script></body></html>'''
out = p.with_suffix(".html"); out.write_text(html); print("wrote", out)
