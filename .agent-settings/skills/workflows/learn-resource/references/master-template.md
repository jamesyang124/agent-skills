# Master template (merged topic knowledge)

The master is the document the user reads before an interview. It must be more useful than any single source: framed, compared, and reconciled, with every claim traceable to a source and a timestamp. Build it only after all per-source notes are verified.

## Rules
1. Cite every non-trivial claim as `slug [m:ss]` (e.g. `hayk [23:38]`). Put `video_sources: slug=VIDEOID, slug2=VIDEOID2` in the frontmatter and `build_html.py` turns each citation into a deep link to that video moment (in md and html). For non-video sources cite the section as plain text (`edu P2 §4`).
2. **Disagreements stay visible.** When sources differ (numbers, who does X, which design) put both sides in a table with citations, then add a short "how to answer in an interview" line. Never average them away.
3. Tag anything not found in any source as **[extra]**. Keep it small.
4. A number appears once in the numbers table with its source; contradictions are flagged `(to verify)` and, where possible, checked against official documentation.
5. Diagrams: Mermaid for most; 3-4 hero diagrams drawn with a polished diagram skill (canonical architecture, main flow, state machine, failure/recovery flow). Label which are reconstructions.
6. Verify the html with `check_html.sh`; zero Mermaid errors.

## File layout

```
---
title: <Topic> - Master
topic: <topic>
sources: [<source-slug>, ...]
video_sources: <short-slug>=<YouTube video id>, ...   # only for video sources
built: YYYY-MM-DD
---

# <Topic> - Master

## 1. How to use this page            (reading order, 5 lines)
## 2. Framing: which problem is it?    (the variants/scopes the sources actually design, e.g. A/B/C; ask-the-interviewer line; which source covers which)
## 3. Mindmap of the whole topic       (mermaid mindmap)
## 4. Source map                       (table: source | scope | what it uniquely adds | link to its notes)
## 5. Comparison matrix                (rows = design decisions: requirements, API, data model, idempotency, consistency, failure handling, scaling, security...; columns = sources; cells cite)
## 6. What every source agrees on      (the must-say points)
## 7. Where sources differ             (table + interview guidance per row)
## 8. Canonical design                 (the best merged answer, step by step, with hero diagrams)
## 9. Deep dives                       (one per reusable topic: problem -> options across sources -> recommendation -> trade-offs)
## 10. Numbers and estimation          (single table, source per row, flagged contradictions)
## 11. Failure modes and handling      (merged table)
## 12. Interview cheat sheet           (60-second pitch, order of presentation, pitfalls)
## 13. Interview Q&A                   (10-20 questions; short answers with citations)
## 14. Open questions and to-verify    (collected from every notes.md + what no source covers)
## 15. Concept index                   (concept -> where it appears; the data the optional knowledge layer is built from)
```

## topic/README.md
Short index: one line per source (title, author, type, status), link to `master.html`, date of last build, list of known gaps.
