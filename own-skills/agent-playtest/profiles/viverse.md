# Site profile: VIVERSE rooms (worked example)

> Internal profile. Review before sharing outside the team: it names internal hosts and an internal index.

| Item | Value |
|---|---|
| Item | a VIVERSE room; `item_id` = `hub_sid` (fall back to `room_id`) |
| URL | `https://worlds.viverse.com/<hub_sid>`. Every room lives here, including plain 2D games, so the URL says nothing about the room type |
| Embed | the content runs in a cross-origin iframe `https://<id>.world.viverse.app/`. Never open that URL directly (it returns 403 outside the host page) |
| Viewport | Record actual viewport/DPR and detected content bounds each run. Historical 1908×922 / box `85,82,1419,832` is an example, not a reusable crop contract |
| Declared metadata | the search index `rooms` (`GET <index>/_doc/<room_id>`): `title`, `content_type_name` (Game / Experience / Videos / Templates), `tags`, `custom_tags`, `description_plaintext`, `description_core` (a rule-cleaned publisher description: still declared data, not observed), `publisher_claims`, `is_adult_only`, `policy` (`allow_any_user` = public) |
| Declared language (2026-10-02 export) | Join `room_language_tag.room_id` to the room UUID, then `room_language_tag.language_tag_id` to `language_tag.id`; display `language_tag.tag` and `name`. `room_language_tag.id` is the association-row ID, **not** the language tag ID. Do not infer labels from a denormalized `room.language_tags[]` value without verifying which ID space it contains. |
| items_dir | `rooms` |

## Rules specific to this site

- **Paywall**: "付費內容" or a VIVERSE Plus unlock screen that shows only key art or a trailer → `excluded_paywall`. List
  the room for a human who has the entitlement.
- **Unsupported device**: a "不支援的裝置" banner with only a trailer → `excluded_unsupported_device` (VR-only).
- **Mic and camera:** rooms that need them (webcam games, "raise hand to start", voice-only play) → `excluded_needs_permission`; a browser
  permission prompt → `excluded_permission_prompt`. Do not assume the player profile blocks them: a camera prompt on load and a
  microphone prompt ~30 s in each handed the space to the user once. Handling: `play-protocol.md`, Exclusions.
- **Shell UI to ignore**: a 29 s pre-roll with no Skip control can precede a room (wait it out, never click or save it);
  an "Are you sure you want to stop playing?" bar appears when the pointer nears the top of the page. Both are shell, so
  keep them out of content evidence.
- **Adult rooms** (`is_adult_only`) are never played.
- **Tags are not proof of genre.** A "Stealth" room turned out to be a card-matching game. Many rooms typed "Experience"
  are games: 66 of the 74 tried in one campaign.
- **Some 3D games bind drag to camera rotation** ("拖曳：旋轉"). Select-then-target moves need a zero-movement press. See
  `play-protocol.md` technique 4.

## Declared metadata export (for `--meta`)

```bash
# one line per room: item_id, declared_kind, public, adult
curl -s "localhost:9200/rooms/_search?size=10000&_source=hub_sid,content_type_name,policy,is_adult_only" \
 | jq -c '.hits.hits[]._source | {item_id: .hub_sid, declared_kind: .content_type_name, public: (.policy=="allow_any_user"), adult: .is_adult_only}' > declared.jsonl
```

`declared_kind` → expected `observed_kind`: `Game` → game; `Experience` and `Templates` → interactive_scene or gallery;
`Videos` → video. This is `observed_kind_mismatches.py`'s default map.

## Review HTML metadata adapter

Supply exact snapshot names in `review.json declared.db_snapshot_fields`: title, content_type_name, description, description_plaintext, tags, custom_tags, view_count and (for Game) game_score_rating. Keep nulls; a populated description_plaintext must not disappear because description is null. game_score_rating is a DB declaration, not an audit verdict or agreement score. content_type_id, UUIDs and language association IDs belong in technical provenance, not the main review table. DB locale presentation uses joined name/code; preserve join IDs and snapshot provenance separately. `languages.title` and `languages.description` are judgments of creator-supplied text, separate from observed UI/subtitle/audio languages. Devices remain HMD, Android, Desktop, iOS with declared/tested/unconfirmed distinctions.

The project adapter owns snapshot/CSV joins and imports; the generic skill renderer only reads supplied metadata. Do not connect to the stack or migrate a schema to render a report. For mixed returned campaigns use the registry's source_campaign per item. Follow `references/report-layout.md`; legacy snapshots remain reference-only.
