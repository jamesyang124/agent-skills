---
name: agent-playtest
description: "Run evidence-grounded simulated playtests of interactive web content (browser games, 3D worlds, galleries, interactive scenes) with parallel browser subagents. Each subagent plays closed-loop (look, act, verify), saves screenshots, logs every input, and writes a structured description backed by those screenshots. The orchestrator then audits the evidence, validates outputs, samples a human spot-check, and reports reliability. Browser-agnostic: ego-browser, Playwright (MCP or library), Chrome DevTools MCP, or any agent-friendly browser that can navigate, screenshot, and send mouse/keyboard input. Includes a human-demo mode in which a person plays while their local mouse/keyboard is recorded, and the agent compares that with its own attempt. Use for content audits, building synthetic description data, checking catalog labels against what is actually observed, or search/recommendation eval data. Trigger: /agent-playtest"
---

# Agent playtest: closed-loop play → screenshot evidence → described, audited data

Many catalog entries (rooms, games, worlds, apps) have publisher text that is wrong, empty, or templated. This skill gets an
**observed** description: an agent actually opens each item, plays it, records what it saw, and writes a description in which
every claim cites a screenshot. The output stays separate from the publisher's **declared** data and never overwrites it.
Disagreements are recorded and handed to whoever owns the catalog.

Every item goes through this pipeline:

```
plan  →  dispatch N player subagents  →  play (closed loop)  →  audit screenshots  →  validate  →  spot-check  →  report
                                  ↘ blockers log (anything that could not be done: record it and continue) ↙
```

## Roles

| Role | Who | Does |
|---|---|---|
| **Orchestrator** | the calling session | writes the plan and brief, dispatches players, audits, validates, samples the spot-check, reports, keeps the blockers log |
| **Player** | 1 subagent per slice of items (default ≤ 4 in parallel) | plays its items in order with one browser session, writes `playtest.json`, `shots/`, `description.json` |
| **Human** | the person running it (optional) | spot-checks descriptions; plays hard items in human-demo mode |

## Evidence contract

Read `references/evidence-review.md` before capture or review: content-only screenshots, coverage by content type, declared/observed separation, timing limits, model roles and portable batches. It takes precedence over historical capture/report examples. Keep database schemas unchanged unless separately authorized.

## Before you start (orchestrator)

1. **Pick a browser adapter.** Read `references/browser-adapters.md`. It lists the capabilities a player needs and how
   ego-browser, Playwright and Chrome DevTools provide each one. Record the choice in the campaign entry.
2. **Pick or write a site profile.** Site-specific rules (URLs, metadata source, paywalls, device gates, embed
   origins) go in `profiles/<site>.md`, never in the generic protocol. `profiles/viverse.md` is the worked example.
3. **Set up the workspace** (layout in `references/data-schema.md`). Then add a `campaigns.json` entry and write
   `archive/<campaign>/plan.json` (`templates/plan.example.json`).
4. **Write the brief** from `templates/agent_brief.md`, filling in the adapter, profile, paths, and any rules specific
   to this campaign.

## Dispatch (orchestrator)

Follow `references/orchestration.md`. The short version:
- Split the items into ≤ 4 slices (one per player), in priority order. Never give one item to two players.
- Players that share one browser need focus emulation. Without it, tabs in the background stall.
- Every browser call needs a wall-clock timeout. A killed CLI may leave a script running ("ghost run"), so check for
  that before reusing a session.
- A player that hits a quota or crashes leaves its remaining items `incomplete`. Do not reassign them mid-run.

## Play protocol (player)

Read `references/play-protocol.md` and follow it exactly. Core rules:
- **Closed loop**: screenshot → decide → act → screenshot. Never run a fixed script blind.
- **Count only verified time.** A segment counts only when the screenshot shows real content *and* `scripts/frame_diff.py`
  reports no stall. For games, 30 s is the minimum, 45–60 s the normal target; extend only for a named evidence gap, to at most 90 s verified play. Time alone is insufficient: see the coverage and stop rules in `references/play-protocol.md`. For no-goal scenes, 30 s must cover ≥ 2 distinct areas or objects.
- **Budget**: ≤ 15 rounds per item. Stop after 3 inputs with no effect. Never retry a stuck item in the same campaign.
- **Exclude, don't force**: dead link, login, paywall, age gate, device gate (VR/camera/mic), browser permission prompt.
  Record `excluded_<reason>` and move on. Never grant a permission. If a room's permission is unresolved after 10 s, skip it
  and record the reason (see `references/play-protocol.md`, Exclusions). A stuck room goes to the human to decide (intervene,
  abandon, or accept partial for now); the intervention is recorded and written back into this skill.
- **Log every input** (type, coordinates, hold time, keys) and what changed. Comparing these logs with human demos is
  how the protocol improves.
- **Observed vs declared**: record `observed_kind` and other observed attributes in the attempt. Never edit the item's
  declared metadata.

## Report layout

Before generating HTML, read `references/report-layout.md`. Use the bundled offline renderer: Declared/screenshots above, full-width Observed below. The master inventory and selected spot-check have distinct scopes; rendering does not approve data.

## After play (orchestrator)

1. **Audit** with `scripts/contact_sheets.py`: first, middle and last screenshot per item. Mark items whose evidence
   shows only a loading screen, logo, menu, tutorial or frozen frame as `rejected_visual_audit`, and downgrade
   over-claimed seconds to `partial`.
2. **Validate new campaigns** with `scripts/validate_descriptions.py --strict` and a declared metadata export (`--meta`). Legacy mode is compatibility only, not acceptance. It rebuilds `derived/` and never needs hand edits.
3. **Mismatches** with `scripts/observed_kind_mismatches.py --meta <declared.jsonl>`. It lists items where what was
   observed differs from what was declared.
4. **Spot-check**: `scripts/spot_check.py --campaign <id> --rate 0.1 --seed <n>`. A human compares each sampled
   description against its screenshots. Record the verdicts. **Reliability is unknown until this is done.**
5. **Report** (`references/audit-and-quality.md`): counts by outcome, audit rejection rate, valid descriptions,
   mismatches, spot-check accuracy, blockers, and items that need a human.

## Human-demo mode (collaborative)

For items an agent could not play: a person plays while `scripts/record_input.py` records local mouse and keyboard
events (opt-in, time-limited, local file only). The person also says in one or two sentences what they did. The agent
compares the recording and narration with its own logged attempt, names the difference (input type, timing, drag
distance, focus, missed control hint), and proposes a protocol or adapter change. See `references/human-demo.md`.
Use OS-level recording because in-page recorders cannot see inside cross-origin iframes, and most embedded games run
in one. For a complete run to copy, see `references/example-human-ai-review.md`.

## Blockers log: record it and keep going

Whenever something cannot be done, append one line to `archive/<campaign>/blockers.md` and continue with the next item:
`- <date> <item or "all"> | <what was tried> | <what failed, exact error> | <workaround or "none"> | <proposed fix>`.
At the end of the run, roll recurring blockers up into the protocol, the adapter notes, or the profile. That is how the
skill improves.

## Hard boundaries

- Never click ads, buy anything, log in with someone else's account, or bypass a paywall or age gate.
- Never grant camera, microphone, location or other device permissions.
- Never inject into or modify the content under test (no `evaluate` into game internals). Read-only DOM snapshots are
  fine for DOM games.
- Skip adult-only items, even if one shows up in the queue.
- Outputs are local files. Importing them into a search index or database is a separate, explicit step that the
  data owner decides on.

## Files

| Path | What |
|---|---|
| `references/evidence-review.md` | coverage, content screenshots, provenance, review and portable batches |
| `references/orchestration.md` | splitting, dispatch, parallelism, timeouts, ghost runs, merging results |
| `references/browser-adapters.md` | capability contract and per-browser recipes, with known gaps |
| `references/play-protocol.md` | screen states, input techniques, verification gates, budgets, exclusions |
| `references/data-schema.md` | workspace layout, campaign / plan / playtest / description schemas, observed-vs-declared |
| `references/audit-and-quality.md` | audit rules, validation checks, spot-check, reliability metrics, report template |
| `references/human-demo.md` | human-demo recording, comparison checklist, privacy rules |
| `references/example-human-ai-review.md` | worked example of a full human + AI review (triage → demo → compare → replay), with a reuse checklist |
| `profiles/viverse.md` | worked example of a site profile |
| `templates/agent_brief.md`, `templates/plan.example.json` | starting points for a campaign |
| `scripts/` | `frame_diff.py`, `contact_sheets.py`, `validate_descriptions.py`, `observed_kind_mismatches.py`, `spot_check.py`, `review_sheet.py`, `record_input.py`, `selftest.py` |
| `references/report-layout.md`, `assets/review/` | approved review-report layout, offline stylesheet, font and licenses |
