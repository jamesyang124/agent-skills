# Site profile: VIVERSE rooms (worked example)

> Internal profile. Review before sharing outside the team: it names internal hosts and an internal index.

| Item | Value |
|---|---|
| Item | a VIVERSE room; `item_id` = `hub_sid` (fall back to `room_id`) |
| URL | `https://worlds.viverse.com/<hub_sid>`. Every room lives here, including plain 2D games, so the URL says nothing about the room type |
| Embed | the content runs in a cross-origin iframe `https://<id>.world.viverse.app/`. Never open that URL directly (it returns 403 outside the host page) |
| Viewport | 1908×922 CSS px; content frame box `85,82,1419,832` (use with `frame_diff.py --box` and `contact_sheets.py --crop 1334:750:85:82`) |
| Declared metadata | the search index `rooms` (`GET <index>/_doc/<room_id>`): `title`, `content_type_name` (Game / Experience / Videos / Templates), `tags`, `custom_tags`, `description_plaintext`, `description_core` (a rule-cleaned publisher description: still declared data, not observed), `publisher_claims`, `is_adult_only`, `policy` (`allow_any_user` = public) |
| items_dir | `rooms` |

## Rules specific to this site

- **Paywall**: "付費內容" or a VIVERSE Plus unlock screen that shows only key art or a trailer → `excluded_paywall`. List
  the room for a human who has the entitlement.
- **Unsupported device**: a "不支援的裝置" banner with only a trailer → `excluded_unsupported_device` (VR-only).
- **Mic and camera** are blocked in the player browser profile. Rooms that need them (webcam games, "raise hand to
  start", voice-only play) → `excluded_needs_permission`. A browser permission prompt → `excluded_permission_prompt`.
  Before mic/cam were blocked, prompts handed the player's session to the user and stalled the whole run.
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
