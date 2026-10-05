# Knowledge layer with OKF (okf-agent-memory)

OKF stores knowledge as Markdown + YAML concept files in git: plain text, bidirectional links, strict validation, BM25 search, optional MCP server. Spiked and verified on a real topic (44 concepts, 48 typed relations, `validate --strict --drift` clean). Source: https://github.com/okf-memory/okf-agent-memory (MIT).

## Install
Needs Go 1.26+: `go install github.com/okf-memory/okf-agent-memory/cmd/okf@v0.5.0` (binary lands in `~/go/bin`). Do not run `okf bootstrap` unless the user wants OKF agent memory in that repo: it rewrites AGENTS.md and related files. `okf init <dir>` is all that is needed here.

## Bundle layout
```
<root>/knowledge/            okf init
  concepts/<slug>.md         shared, reusable across topics (idempotency, outbox, circuit breaker, ...)
  <topic>/<slug>.md          concepts specific to one topic
  index.md, log.md           kept by the tool; subfolders get their own index.md
  graph.html                 generated viewer (scripts/okf_graph.py)
```
Concept ids are paths without `.md`, e.g. `concepts/idempotency-key`. Put a concept in `concepts/` when a second topic could reuse it.

## Concept file convention
- Frontmatter the tool understands: `type` (Concept, Pattern, Problem, Component, Tradeoff, Fact), `title`, `description` (one sentence), `tags`, `status`, `sources` (list of `resource` / `id` / `title`).
- `sources.resource` = relative path from the concept file to that source's `notes.md` (validates fine, even outside the bundle).
- Custom frontmatter that is preserved: `scope` (block list, e.g. `- A`) and `evidence` (block list of `"slug m:ss"` strings). Mirror scope into `tags` as `scope-A`, `scope-B`: filters work on `tags` and scalar keys but not on custom lists.
- Body: one-paragraph definition, then `## What the sources say` with one bullet per source and a deep link to the moment (`[hayk 23:38](https://www.youtube.com/watch?v=ID&t=1418s)`); plain text for non-video sources.
- Relations: `okf relate <from> <to> <bundle> --desc "<type>: <short text>"`. The type is a controlled prefix: `solves`, `causes`, `requires`, `refines`, `part-of`, `alternative-to`, `trade-off-with`, `contradicts`, `mitigates`, `enables`. The tool writes `- [Title](rel.md): <type>: <text>` under `# Related Concepts`; `okf_graph.py` parses exactly that. Every concept needs at least one relation (strict mode flags orphans).
- Source disagreements become a concept with `contradicts`/`trade-off-with` edges and both positions in the body, not a silent pick.

## Procedure
1. Take the `concepts:` lists from every notes.md plus the master's concept index; merge synonyms; drop one-source trivia.
2. Write a throwaway generator: for each concept `okf create ... --body ...`, then add `scope`/`evidence`/`sources` to the frontmatter, then `okf relate` for each edge. After generation the OKF files are the only source of truth; do not keep a second spec that can drift.
3. `okf validate <bundle> --strict --drift` must report 0 errors, 0 orphans, 0 broken links.
4. `python3 scripts/okf_graph.py <bundle> <bundle>/graph.html --title "<Topic> concept graph"`, then `scripts/check_html.sh <bundle>/graph.html` and look at a screenshot (clustering, labels, panel).
5. Use it: `okf search "query" <bundle>`, `okf search --filter "tags=scope-B" <bundle>`, `okf show <id> <bundle> --json`.

## Gotchas found in the spike (v0.5.0)
- `okf relate --help` lists `--no-log` but the flag is rejected. Omit it (relations add log lines).
- Re-serialization (any `relate` call) turns a multi-item flow list in custom frontmatter into a quoted string; write custom lists as block lists.
- `okf create ... --body` takes the whole body as one argument; build it in the generator.
- `okf create --no-log` skips the log entry; add one summary line to `log.md` yourself afterwards.
- Make the generator resumable: it can die midway (a source key missing from its table, a bad flag) and leave half-created concepts. Skip a concept whose file already has `evidence:`, patch one that exists without it, and let the relation step skip links that already exist.
- Derive the topic tag from the topic name; do not hard-code it (a copied generator once tagged LLM concepts `payments`).
- `okf relate` re-serializes the file, so normalize custom frontmatter (`scope` as a block list, `scope-X` tags) in a final pass after all relations are added, and re-run `validate --strict --drift`.
- When a second topic reuses an idea from the first, link to the existing concept (for example function calling requires the idempotency key) rather than creating a duplicate: that is what makes the graph cross-topic.
- `okf` re-orders frontmatter keys whenever it rewrites a file (for example `sources` moves before `evidence` and `scope`). When adding evidence to an existing concept by hand, insert into the right block (find the `sources:` list and append to it, find the `evidence:` list and append to it); appending at the end of the frontmatter can land a source entry under `scope:`, which validation does not catch. After any bulk edit check that every `scope:` block holds only plain values.
- A new topic should add its evidence to concepts it reuses (a bullet in the body, an `evidence` string and a `sources` entry) instead of making near-duplicates.
