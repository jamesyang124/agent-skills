# Campaign <CAMPAIGN_ID>: player brief (agent1..agentN)

This is a real task. Capture real play evidence and write real descriptions. No mock data, no placeholders.

## Read first, in order
1. The adapter's own docs (for example the ego-browser skill), then `<SKILL>/references/browser-adapters.md` → section <ADAPTER>.
2. `<SKILL>/references/play-protocol.md` and `references/evidence-review.md`. Follow the capture coverage and source-separation rules.
3. `<SKILL>/references/data-schema.md`, for the playtest.json and description.json formats. Open 1–2 existing
   `<WORKSPACE>/<ITEMS_DIR>/*/description.json` files and copy their shape.
4. `<SKILL>/profiles/<PROFILE>.md`, for the site rules.
5. `<WORKSPACE>/archive/<CAMPAIGN_ID>/plan.json`. Your list is `work.<your agent id>`, in priority order.

## Campaign rules
- Work through your list in order. Before each item, read its declared metadata from: <METADATA SOURCE>.
- <CAMPAIGN-SPECIFIC ADDITIONS, e.g. what counts as played for this content, extra observed attributes>
- Games: minimum 30 s verified play; target 45–60 s; extend to at most 90 s only for a logged evidence gap. Require core action, result and subsequent loop. Existing 15-round/exclusion/no-effect limits still win. Preserve raw frames; select representatives without deleting originals.
- No retries: if an item is stuck, record it once and move on.
- Never change declared metadata. Never import anything anywhere.
- Write only inside your own items' folders, and append to playtest.json, never overwrite.
- Use one browser session, created once. Turn on focus emulation after every navigation. Wrap every browser call in
  `timeout 150`. Keep helper scripts in `<SCRATCH>/<agent id>-*`.
- If something cannot be done (a tool error, a missing capability), do not stop. Note it in your final summary under
  "blockers" with the exact error, and continue.
- Before finishing, check that every item in your list has an attempt for <CAMPAIGN_ID>. Then close the session exactly
  once.

## Return
For each item: item_id, title, outcome, observed_kind, verified seconds, rounds used, and whether description.json
was written (y/n). Include representative evidence, covered/missing states, timing method/unknowns, declared/observed conflicts, actual model/effort and A–D gap category. Then list blockers and anything that needs a human. For remote batches return only your assigned files and their hashes; do not integrate into canonical data.
