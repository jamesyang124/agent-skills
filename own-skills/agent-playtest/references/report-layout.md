# Offline review report contract

Approved layout (2026-10-04): upper CSS Grid row has Declared on the left and screenshots on the right. Observed spans the full width below; summary, environment/style, interactions, objectives, pacing and unconfirmed facets use a two-column grid. Full semantic description, coverage, devices/timing and Review remain full-width and expanded. Language declarations belong in the main Declared table, not a separate panel. No sticky screenshot dock, independent scroll region, carousel or image pagination by default. The surrounding document is the only vertical scroll surface.

## Presentation

Use bundled `scripts/review_sheet.py` and `assets/review/`; do not rediscover a framework or require Impeccable/prototype at report-generation time. CSS is compiled from Tailwind4.3.0 + daisyUI5.7.47; local Inter is SIL OFL1.1. Body and table values16px, secondary text14px, square corners, left-aligned copy. Tags use wrapping bordered rows; narrative lists use semantic ul/li with CSS markers. Preserve creator text, source logs and screenshot pixels in their source languages; report controls and missing-state labels are English.

Use real metadata names supplied by the profile, not invented `kind` aliases. Hide technical IDs in provenance, except the item identifier needed to find the record. Render language name/code, never an association ID as a language. Distinguish absent/empty, unreviewed, untested, insufficient evidence and confirmed negative; missing profanity is Not assessed, not no profanity. Do not calculate agreement scores without an explicitly calibrated contract.

## Screenshots

Show every supplied content frame once inline; retain originals and original-resolution links. Exclude frames positively classified ad; put loaders in optional diagnostics. Unclassified historical frames remain explicitly unclassified, not newly accepted content. Optional `review.json key_screen_refs` (1–3 content refs) and `key_screen_reasons` identify evidence-selected key frames; highlight them with a single teal border. Do not automatically label an arbitrary representative a semantic key frame. Missing key selection is acceptable. When existing content representatives are supplied, enlarge one as “Representative (display only)” for the reviewed layout, without asserting a new key-screen verdict. With no representatives, show ordinary frames. Ad/platform language is never content-locale evidence. Layout cannot repair missing crops or evidence.

Only audit/provenance, historical logs and loader diagnostics may default to collapsed. Preserve confidence/citations in provenance and do not turn them into accuracy scores. Never mutate data or manufacture missing observations while rendering.

## Two report scopes

- `--registry path/registry.json`: master `room_info_review.html`, including pending status-only records. Rows use item_id/hub_sid and source_campaign; records marked pending must not borrow old prose.
- `--spot path/spot_check.json`: selected `spot_check_review.html`, showing supplied selection_reason, population and seed. Sampling/queue selection is upstream; the renderer does not silently choose cases. Targeted cases and seeded random cases need separate denominators. Generating HTML does not record a human verdict.

Both use the same renderer and item data; do not copy all records into spot-check and call it a sampled set. Existing campaign command remains supported:

```
python3 scripts/review_sheet.py --base /path/workspace --items-dir rooms --spot /path/workspace/archive/campaign/spot_check.json --campaign campaign
python3 scripts/review_sheet.py --base /path/current --registry /path/current/registry.json
```

Output is read-only with respect to input JSON; only HTML and adjacent `review-assets/` are written. Carry those assets and referenced item images when sharing. A mismatched description/review campaign is withheld, not silently shown as current. Relative image paths must resolve inside the item directory.

## Maintaining the style

`cd scripts/review-style && npm ci && npm run build` rebuilds bundled CSS/fonts. Normal rendering needs only Python standard library and bundled assets, no network/npm. Retain license files. Check one real desktop report for upper layout, full-width Observed, image availability, search, escaping and campaign isolation before syncing skill copies. Do not replace an existing master report during validation; use `--out` to write a preview.
