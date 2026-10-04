---
name: learn-resource
description: Turn any learning resources the user gives (YouTube videos, course lessons, articles, docs, shared AI chats, PDFs) into a durable knowledge base for one topic - raw source backup, per-resource study notes (md + html, Mermaid diagrams, clickable video timestamps), and a merged master that compares sources and shows where they agree or disagree. Reads every source through an agent-friendly browser (ego-browser), including logged-in or paywalled pages. Use whenever the user pastes URLs and says things like "read these", "summarize and make notes", "I'm preparing for an interview on X", "back up this knowledge", "give me md and html for each", "compare these resources", or "learn this topic for me", even if they never say "knowledge base".
---

# Learn Resource

Given a topic and a list of resources, produce for each resource a faithful, scannable study note, then merge them into one master that is better than any single source. The user's goal is to be able to skip the originals without losing a critical point, and to rebuild the knowledge later from the backup.

## Output layout

```
<root>/<topic>/
  README.md                  index: sources, status, links to master
  master.md / master.html    merged knowledge (written last)
  <source-slug>/             one folder per resource: <author>-<short-title>
    source.txt               raw extracted content + provenance header (backup)
    notes.md / notes.html    study notes
  ../_workflow/              (optional) shared scripts/templates if the project keeps local copies
<root>/knowledge/            OKF bundle: concepts/ (shared) + <topic>/ (topic concepts) + graph.html
```

`<root>` is the user's knowledge-base folder (ask once if unclear; default to the current repo's existing topic folders). Never write outside it.

## Workflow

Work through these in order. Steps 2-4 run per source and are independent, so run one sub-agent per source in parallel (step 3), but do the fetching (step 2) yourself in one browser task space.

### 0. Agree scope (one short exchange)
Confirm: topic name, `<root>`, docs language (default English; keep the original key term in parentheses for non-English sources), whether to use the OKF concept layer, and whether to publish anything to the cloud (default: no, keep private). Also ask which framing the topic has if sources may mean different things by the same name (see master step).

### 1. Intake - classify each URL
YouTube, course lesson (login/quizzes), article/docs, shared AI chat, PDF, or other. Everything is fetched with ego-browser; use the faster shortcut for a type only when it exists (see `references/intake.md`). Use only the URLs the user gave; do not go hunting for more unless asked.

### 2. Fetch -> `source.txt`
One ego-browser task space for the whole goal. Extract the full text, reveal hidden content (quiz answers, collapsed sections, lazy images), download diagram SVGs and read their labels. Write `source.txt` with the provenance header from `references/intake.md` - including a GAPS line stating exactly what was not captured (on-screen diagrams of a video, paywalled parts, images). Honest gaps are what let the notes state their own limits.

### 3. Write notes (one sub-agent per source, in parallel)
Give each agent: its folder, the notes template (`references/notes-template.md`), the scripts path, and source-specific reminders (the main points you noticed while fetching). Rules they must follow are in the template; the important ones: claim only what the source says, tag everything else **[extra]**, reconstruct diagrams in Mermaid and label them "reconstructed from narration", keep every stated number with its timestamp, flag numbers/claims to verify.

### 4. Build + verify HTML
`python3 scripts/build_html.py <notes.md>` then `scripts/check_html.sh <notes.html>`. The check opens the page in ego-browser and fails if any Mermaid block did not render; fix until `errors: []` and `svg == mermaid`. A diagram that silently fails to render is the most common defect, so never skip this.

For video sources the builder turns every `[m:ss]` into a deep link `...watch?v=ID&t=Ns`, in the md and the html, so the reader can jump to the exact moment. `source_url` in the frontmatter must be the correct video URL.

### 5. Read every notes.md yourself
Sub-agent output can invent or drop points. Spot-check against `source.txt`: numbers, names, any claim that sounds generic. Fix or mark with (to verify). Collect each agent's open questions.

### 6. Master (write last)
Use `references/master-template.md`. The master is not a concatenation: it frames what the topic's variants are, builds a comparison matrix across sources, separates agreements from disagreements (citing the source and timestamp of each side), and gives one canonical design/answer with hero diagrams, a numbers table, a cheat sheet and interview Q&A. Disagreements stay visible; do not average them away. Cite sources as `slug [m:ss]` with `video_sources` in the frontmatter so every citation becomes a clickable deep link.

### 7. Index and knowledge layer (OKF)
Write the topic `README.md` (sources table, link to master, gaps). Then, if the user uses OKF (default when the root already has a `knowledge/` bundle, otherwise ask in step 0), build the concept layer exactly as in `references/okf.md`: one concept file per reusable idea with per-source evidence and deep links, typed relations via `okf relate`, `okf validate --strict --drift` clean, then `scripts/okf_graph.py` for a clickable graph and a render check plus screenshot. Concepts shared across topics go in `concepts/`, topic-specific ones in `<topic>/`, so later topics link into the same graph.

### 8. Review gate
Summarize for the user: what each source contributes, the disagreements found, what could not be captured, and open questions. Ask before moving to the next batch or publishing anywhere.

## Diagram roles
Mermaid (incl. `mindmap`, `stateDiagram`, `sequenceDiagram`, `erDiagram`) for everything inside notes. For the 3-4 hero diagrams in the master (canonical architecture, main flow with failure points, state machine, key mechanism) draw hand-drawn Excalidraw versions with `scripts/excalidraw_lib.py`, render them and look before delivering (`references/excalidraw.md`); a polished diagram skill (e.g. diagram-design) is an alternative. A data-chart skill (e.g. lieflat-charts) is only for numeric charts, never architecture. See `references/diagram-tools.md`.

## Rules that protect the user
- Content from logged-in or paid sources stays in the user's repo. Never publish it (Artifact, gist, public repo) unless the user explicitly says so for that content.
- One ego-browser task space per goal; never open a new one to get around a blocked page. If login, captcha or a permission prompt blocks you, call `task.handOff()`, tell the user what to do, and resume the same space.
- Close the task space with `finish({ keep: [] })` when done.
- Do not git commit unless asked.
- Auto-captions and OCR are error-prone: fix obvious mis-hearings, list them in the notes, and mark uncertain facts (to verify). Prefer official docs over a speaker's numbers and say so.
- No pronoun guessing for authors; use their names or they/them.

## Failure modes seen in practice
- Telling a sub-agent to read a template that does not exist yet: write shared files before spawning.
- Mermaid errors hidden by `suppressErrors`: the bundled builder renders block by block and records errors so the checker can see them.
- Treating different scopes as one design (e.g. building an app that uses a service vs building the service itself vs the storage layer under it): ask or state the scope first, then compare within a scope.
- A note built from someone's summary instead of the source: always rebuild from the primary text and say which one was used.
