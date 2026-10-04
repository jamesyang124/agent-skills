# Per-resource notes template

Goal: notes.md that lets the reader skip the original resource without losing any critical point, plus notes.html (built by `build_html.py`).

## Rules
1. **Only claim what is in `source.txt`.** Read all of it first. Paraphrase; no long verbatim quotes.
2. **Tag additions.** Anything not in the source (standard practice, interview depth, corrections) is marked **[extra]** and kept short. Never mix an [extra] into a source claim.
3. **Fix caption errors silently but list them** in "Source artifacts" (e.g. "item potency" -> idempotency).
4. **Diagrams:** the source is audio-only. Reconstruct diagrams in Mermaid and label them `*Reconstructed from narration.*`. Never imply they are the author's slide.
5. **Numbers:** keep every number the author states, with unit and timestamp. If a number looks wrong or contradicts common knowledge, keep it and add `(to verify)`.
6. **Timestamps:** every deep dive and key claim carries `[m:ss]` from source.txt (video sources). Write them as plain `[m:ss]`; `build_html.py` turns them into clickable deep links (`...watch?v=ID&t=Ns`) in both notes.md and notes.html, so `source_url` in the frontmatter must be a correct YouTube URL. Ranges like `[3:46-4:32]` link to the start.
7. **English.** For non-English sources keep the original key term in parentheses on first use.
8. **Mermaid safety:** quote labels containing `() [] {} : ; ,` or `/` (`A["text (x)"]`); no raw `<` `>` in labels; `mindmap` children are indentation-based, one root only; `erDiagram` attribute types are single words (`bigint`, `string`); no `Note` inside flowcharts; sequence participants declared once.
9. After writing: run `build_html.py` then `check_html.sh`; fix until `errors: []` and `svg == mermaid`.

## File layout

```
---
title: <resource title>
source_url: <url>
author: <author / channel>
source_type: youtube | educative | article | chat | pdf | other
scope: <short label for the variant of the problem this source actually designs; labels are defined per topic in the master, e.g. A/B/C>   # state it, then explain in one line
fetched: YYYY-MM-DD
concepts: [kebab-case-slugs]   # 10-30 reusable concepts, e.g. idempotency-key, transactional-outbox, double-entry-ledger
---

# <Title> — Notes

> Source: <title> by <author> (<url>). Fetched <date> via <method>. Tags: **[extra]** = added by me, not in the source. See "Source artifacts" for coverage gaps.

## 1. TL;DR            (<= 8 bullets; the whole design in one breath)
## 2. Mindmap          (mermaid `mindmap`, 2 levels deep: root -> branches -> leaves)
## 3. Scope & framing  (what exactly is being designed; which variant label; what is out of scope; what the author assumes)
## 4. Requirements     (functional, non-functional, scale numbers - tables)
## 5. APIs and data model   (endpoints + tables/fields; only what the source states)
## 6. Architecture     (reconstructed diagram + component table: component | job | notes/timestamp)
## 7. Deep dives       (one subsection per topic: Problem -> Solution -> Why it works -> Trade-offs; with [m:ss])
## 8. Failure cases    (table: failure | what goes wrong | author's handling | [m:ss])
## 9. Numbers and assumptions   (every number stated, with unit and [m:ss])
## 10. Trade-offs and alternatives the author names
## 11. Source artifacts and claims to verify   (caption errors fixed, what on-screen content is missing, numbers/claims to check against official docs)
## 12. Interview Q&A   (6-12 questions answerable from this source; short answers)
## 13. Timestamp index (topic -> [m:ss])
## 14. [extra] Additions   (optional, short, clearly separated)
```

Keep each section proportional: a 15-minute video should give roughly 250-450 lines of markdown, mostly tables, bullets and diagrams.
