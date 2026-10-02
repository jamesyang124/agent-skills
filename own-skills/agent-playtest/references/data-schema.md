# Data schema

## Workspace layout

```
<workspace>/
  campaigns.json                 one entry per campaign (written before the run)
  <items_dir>/<item_id>/         raw per-item data, written while playing (items_dir defaults to "items"; VIVERSE uses "rooms")
    playtest.json                {"item_id", "title", "url", "attempts": [...]}; append only
    description.json             observed description + evidence + confidence
    shots/<campaign>_NN.png      screenshots in capture order
  derived/                       rebuilt by scripts only, never edited by hand
    descriptions.validated.json
    report.json
    observed_kind_mismatches.jsonl
  archive/<campaign>/            plan.json, AGENT_BRIEF.md, blockers.md, contact_sheets/, spot_check.json
```

The **declared** metadata (the publisher's title, type, tags, description) stays in its own source, such as a DB, an
index, or an export file. This skill reads it and never writes it. The **observed** data lives only in this workspace.
Keep the two separate in naming too: if you ever load observed fields into a shared store, prefix them, e.g.
`observed_kind`, `observed_description`.

## campaigns.json entry

```json
{"id": "2026-10-01_r9", "date": "2026-10-01", "method": "closed_loop", "model": "<player model>",
 "adapter": "ego-browser | playwright | playwright-mcp | ...", "adapter_selftest": "pass 4/4",
 "profile": "profiles/viverse.md", "scope": "<which items and why>", "players": 4,
 "rules": "<campaign-specific additions>", "verified_play_seconds": 30}
```

## playtest.json attempt

```json
{"campaign": "2026-10-01_r9", "method": "closed_loop", "agent": "agent2",
 "outcome": "played | partial | excluded_<reason> | rejected_visual_audit | incomplete",
 "observed_kind": "game | interactive_scene | gallery | video | broken",
 "observed_kind_evidence": ["shots/2026-10-01_r9_03.png"],
 "verified_gameplay_total_s": 33.1, "rounds_used": 11, "audit": null,
 "shots": [{"file": "shots/2026-10-01_r9_01.png", "note": "main menu"}],
 "log": {"entry": [{"shot": "shots/..._01.png", "state": "main_menu", "action": "press PLAY (120 ms)"}],
         "play": [{"shots": "05..08", "input": "hold W + tap A/D", "moving_intervals": "4/4", "verified_s": 8.4}],
         "inputs_tried": [{"type": "press", "x": 640, "y": 410, "hold_ms": 120, "effect": "none"}],
         "controls_observed": "on-screen help: drag = rotate view", "not_verified": "multiplayer"}}
```

`audit` is set by the orchestrator: `{"by": "<who, date>", "verdict": "ok | rejected | downgraded", "note": "..."}`.

## description.json

```json
{"item_id": "...", "campaign": "...", "source": "playtest.json attempts[-1]",
 "content": {"summary": "...", "environment_style": "...", "observable_interactions": "...",
             "gameplay_objectives": "...", "mood_pacing": "...", "unconfirmed_items": ["..."],
             "semantic_description": ">= 200 words"},
 "evidence": [{"field": "summary", "source_type": "screenshot | on_screen_text | metadata", "source_ref": "shots/..._02.png"}],
 "confidence": 0.8}
```

## Declared metadata file (input to the validation and mismatch scripts)

JSONL, one line per item: `{"item_id": "...", "declared_kind": "Game", "public": true, "adult": false}`. Export it from
the site's source; the site profile says how.
