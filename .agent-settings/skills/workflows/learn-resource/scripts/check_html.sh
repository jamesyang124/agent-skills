#!/usr/bin/env bash
# Render check via ego-browser: every mermaid block must become an <svg> with no error. Usage: check_html.sh file.html [file2.html ...]
for f in "$@"; do
abs=$(cd "$(dirname "$f")" && pwd)/$(basename "$f")
ego-browser nodejs <<EOF
const task = await taskSpace("render check");
const page = task.page("p1");
await page.goto("file://$abs");
await page.waitForFunction(() => window.__done === true, undefined, { timeout: 30000 }).catch(()=>{});
const r = await page.evaluate(() => {
  const blocks=[...document.querySelectorAll(".mermaid")];
  return {done:window.__done===true, h2:document.querySelectorAll("h2").length, mermaid:blocks.length, svg:blocks.filter(b=>b.querySelector("svg")).length, errors:window.__errors||[], graph:window.__graph||null};
});
console.log("$f", JSON.stringify(r));
await task.finish({ keep: [] });
EOF
done
