# Data schema

## Workspace layout

```
<workspace>/
  campaigns.json                 one entry per campaign (written before the run)
  <items_dir>/<item_id>/         raw per-item data, written while playing (items_dir defaults to "items"; VIVERSE uses "rooms")
    playtest.json                {"item_id", "title", "url", "attempts": [...]}; append only
    description.json             observed description + evidence + confidence
    review.json                  optional sourced review notes for local HTML reports
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

## Optional per-item review.json

This file enriches the local `review_sheet.py` report; it does not change `playtest.json`, `description.json`, validation, or a database. Omit fields that have not been collected. The renderer shows them as **unknown**; an empty declared string is shown as **empty**. Copy declared values from a dated source snapshot, never infer them from play. Paths are relative to the item directory and must identify original local images.

```json
{
  "declared": {
    "source": "catalog export URI or file and row", "snapshot_date": "2026-10-03",
    "title": "Creator title", "kind": "Game", "description": "",
    "tags": ["puzzle"], "view_count": 123
  },
  "description_source": "description.json from campaign c1",
  "languages": {
    "db_locale": "en", "title": "unknown", "description": "unknown",
    "content_ui": "en (shots/c1_03.png)", "subtitles": "unknown",
    "heard_audio": "unknown", "generated_text": "en"
  },
  "devices": {
    "declared": ["Desktop"], "tested": ["Desktop: Chrome on macOS"],
    "unknown": ["HMD", "Android", "iOS"]
  },
  "coverage": {
    "reached": ["gameplay overview: shots/c1_03.png"],
    "missing": ["result screen"], "note": "one level reached"
  },
  "timing": {
    "navigation": "2026-10-03T10:00:00Z",
    "content_start": "2026-10-03T10:00:02Z",
    "first_useful_content": "2026-10-03T10:00:06Z",
    "first_interaction": "2026-10-03T10:00:09Z",
    "loader_intervals": ["10:00:02–10:00:06 UTC"],
    "ad_intervals": [], "method": "browser timestamps",
    "environment": "Desktop Chrome, macOS; network/cache unknown"
  },
  "frames": [
    {"ref": "shots/c1_01.png", "class": "loader"},
    {"ref": "shots/c1_02.png", "class": "ad"},
    {"ref": "shots/c1_03.png", "class": "content"}
  ],
  "representative_refs": ["shots/c1_03.png"],
  "human_review": "pending"
}
```

`frames[].class` is `content`, `loader`, `ad`, or `unknown`. Representative images appear only when explicitly listed, classified as content, and present in the selected campaign attempt's `shots`. The report excludes classified ads, keeps classified loaders in a collapsed diagnostic section, and keeps all other original attempt frames in a collapsed raw section. It warns and withholds description claims and citations when `description.json` names a different campaign; absent descriptions render as unknown so blocked items remain reviewable. Do not use platform shell, ads, or loaders as content evidence. `coverage.reached` and timing values require source references or timestamp evidence; omit them if unavailable. `human_review` is a status, not an inferred reliability score. Device emulation is not physical-device testing.
