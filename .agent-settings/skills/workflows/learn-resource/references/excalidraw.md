# Hero diagrams with Excalidraw

For the 3-4 diagrams a reader should memorize (canonical architecture, main flow with failure points, state machine, key mechanism). Everything else stays Mermaid.

## Tools
- Skill `excalidraw-diagram-generator` (github/awesome-copilot): rules for the .excalidraw format and layout. Install: `npx skills add github/awesome-copilot --skill excalidraw-diagram-generator --agent claude-code -g -y`. Its three bundled Python scripts are stdlib-only and just edit JSON files.
- `scripts/excalidraw_lib.py`: a small builder (boxes with bound text, arrows with bindings and labels, notes, sequence messages) so you place nodes by coordinates instead of hand-writing JSON. Read its docstring for the layout rules that avoided overlaps.
- `scripts/excalidraw_render.html`: renders a diagram with Excalidraw's own `exportToSvg` so you can see it before delivering.

## Procedure
1. Pick the diagrams from the master's section on the canonical design; one idea per diagram, at most about 16 boxes.
2. Write a throwaway script that imports `excalidraw_lib` and saves `<topic>/diagrams/NN-name.excalidraw`.
3. Render and look. Per diagram, with ego-browser (same task space for the whole job):
   ```js
   await page.goto("file:///<skill>/scripts/excalidraw_render.html");
   await page.waitForFunction(() => window.__ready === true, undefined, { timeout: 90000 });
   const doc = JSON.parse(await fs.readFile(path, "utf8"));
   await page.evaluate(async (d) => await window.renderDiagram(d), doc);
   await fs.writeFile(svgPath, await page.evaluate(() => document.querySelector("#o svg").outerHTML));
   await page.screenshot({ path: pngPath });   // the page fits the SVG to the viewport
   ```
   Open the PNG and check: labels fit their gaps, no arrow crosses a label, text stays inside boxes, colors mean something. Fix coordinates or shorten labels and repeat.
4. Keep both files: `.excalidraw` (editable at excalidraw.com) and `.svg` (embedded in the master via `![alt](./diagrams/x.svg)`).
5. After embedding, check the page: every `img` has `naturalWidth > 0`.

## Notes
- The render page loads Excalidraw 0.18 from esm.sh with an import map for React, so it needs internet. The exported SVG references the Excalifont web font, so offline viewers fall back to a system font.
- Use `fontFamily: 5` for all text. Palette: blue `#a5d8ff`, green `#b2f2bb`, yellow `#ffd43b` (central or extra), red `#ffc9c9` (failure), gray `#e9ecef` (data stores), purple `#d0bfff` (external systems).
- Mark anything not from a source (extra) inside the diagram itself, with a dashed border or a note.
- Lessons: edge labels longer than the gap between two boxes overlap both boxes; a long straight arrow through a crowded row hides labels; put a "what happens on replay" legend below a diagram, not across its arrows.
