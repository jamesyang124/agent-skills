# Evidence coverage and review contract

Read before planning, capture, description generation or audit. Revision: 2026-10-03.
Keep the existing playtest/description formats. Extra observations use optional per-item `review.json` (see `data-schema.md`); this contract does not authorize a DB/schema migration.

## Coverage, not just screenshot count

Keep dense chronological frames for verification (normal play every 1.5–3 s within 6–10 s segments; timed rounds every 3–5 s). Separately select a small representative set for the report. These are different products: selecting representatives must not delete raw evidence.

Campaign defaults below are acquisition targets, not automatic acceptance thresholds. Record which states were reached, evidence references, and unobserved states. Before ending, check this table and use remaining rounds for the missing state most relevant to a description claim. Stay within 15 decision rounds and existing exclusions; never force success or secretly extend a run. Segment frames do not each consume a decision round.

| Observed content | Representative target | Required coverage to assess, not merely count |
|---|---|---|
| Game | 8–12 content frames (target 10) | Actual gameplay overview; before/after one meaningful action; a later gameplay state showing progression. Capture result/win/lose only if reached. Tutorial/menu alone is not gameplay. |
| Scene/world/gallery | 8–12 content frames (target 10) | Spatial overview; at least two distinct areas or objects; close detail; interaction before/after when interaction exists. Do not invent interaction for a passive gallery. |
| Choice story | 4–6 content frames | Setup and consequences of at least three actual choices for played; clearly mark linear pages vs verified branches. |
| Video | 3–5 content frames | Confirm actual film rather than ad/trailer; record duration if available, media timestamps and viewed intervals. Sample separated early/middle/late positions when seeking is available and budget permits; disclose seeking and unwatched gaps. Never call a sampled video fully watched or played. |

Frames may support multiple coverage points; near-identical frames do not satisfy different states. For very short/static content, keep fewer frames with a reason. Missing coverage yields a scoped description and explicit gap, not padded screenshots. Successful played time and description coverage are separate: 30 seconds in one corner does not demonstrate the whole world. Completion, multiplayer, every level, every language/device and full-video viewing are never assumed.

## What goes into a formal screenshot

Capture the actual content bounds, preserving its HUD, subtitles and controls. Record crop coordinates/viewport and original reference for derived crops. Exclude platform header, recommendation sidebar and surrounding advertisements from evidence used for content classification, OCR and description. Re-check bounds after layout/fullscreen changes; never blindly reuse a fixed site crop.

Ad label, countdown and Skip Ad are clues, not a location-only classifier. Wait or use a positively identified Skip control; never click the creative. Do not save ads as delivered content evidence, count them as play, or crop off their label to disguise them. Inspection for navigation is allowed. A blocker is a valid result.

At most one useful loader frame per attempt, optional and kept as diagnostic evidence, never a representative content frame. Label loader/platform separately from engine; a VIVERSE logo does not prove Unity. Unknown is valid. Preserve historical originals; do not delete them during cleanup.

## Declared, observed and derived

Keep DB and creator title/description/tags/view count with source and snapshot date. Blank declared values are allowed. Language evidence must separate DB locale, title language, description language, content UI/OCR, subtitles, actually heard audio and generated text language. Ignore shell/ad language; short names can be unknown. Device categories for VIVERSE are HMD, Android, Desktop, iOS; list declared/tested/unknown separately. HMD suggests VR but is not proof of support; emulation is not physical-device testing.

Preserve summary, environment_style, observable_interactions, gameplay_objectives, mood_pacing, unconfirmed_items, semantic_description, confidence and evidence. Describe mechanics, setting, style and pacing naturally; do not bury them in input timing/loading diaries. Existing 200-word validation remains for compatibility: if evidence cannot support it, mark insufficient rather than padding. No new word-count target is an excuse to invent facts.

Search-friendly summaries/phrases and SEO drafts are derived outputs, never replacement observations or creator edits. Ground each factual claim; avoid keyword stuffing, unsupported multiplayer/device/language claims and promises of search ranking gains. Index import/publication is separate. Profanity review only identifies text, context, language, uncertainty and evidence; it does not reject a room or alter retrieval. No calibrated acceptance score or bias percentage exists by default.

## Opportunistic timing

Record browser timestamps for navigation, content-start action, first useful content and first successful interaction (video: first actual content frame). Record loader/ad intervals separately from human/agent/tool waits. If only polling is available, give last-not-ready/first-ready bounds instead of invented exact latency. Cross-origin missing timing is unknown. Record device/browser/network/cache/method; a single playtest is not Lighthouse, field Web Vitals or a fair cross-machine ranking. No timing backfill without original timestamp evidence.

## Reviewer responsibilities

Read original content frames and input/timing records, not just generated prose or a three-frame contact sheet. A contact sheet is triage. At least one real content image proves content was reached, not 30 seconds, complete coverage or all claims. Frame change alone can be an ad/menu animation. Static turn-based frames alone do not prove a stall either; inspect input/result evidence.

Record separately: structural validity, reached content, verified play, coverage gaps, factual support, declared/observed conflicts and human review status. Use audit ok/rejected/downgraded with a scoped note. Missing evidence is unknown; never manufacture an audit pass. Human reliability remains unknown until human review. For bias/unsupported-claim rates report the definition, numerator, denominator and sample; no model self-confidence as measured accuracy.

For this VIVERSE workflow Astra Medium orchestrates criteria, initial per-item calibration and batch review; Sonnet 5.5 generates, or Sol in Codex-only execution. Record actual model/version/effort. Review all ambiguous cases plus seeded random ordinary cases after calibration; expand review if systematic errors appear. Escalate reasoning only for bounded unresolved questions. Do not run every item through three models. James calibrates the initial sample; cross-model agreement is not ground truth.

## Portable batch / second Mac

Coordinator freezes IDs, campaign, skill files and SHA-256 manifest, metadata snapshot, original attempts/descriptions and referenced images. Assign non-overlapping item lists; explicitly label any calibration duplicates. Worker operates on its isolated copy, never stack/DB/index, canonical files or shared reports. Back up before editing existing playtest files; append new attempts, never erase history. Return all assigned IDs including failures, per-item evidence/gaps, A (render only)/B (reanalyze)/C (targeted capture)/D (replay) recommendation, actual model/method, and files with hashes. A/B must not claim new play.

Coordinator verifies room/campaign/source hashes, changed-file scope and missing/extra IDs, audits raw evidence, then explicitly integrates. A return bundle does not authorize canonical overwrite. Do not include credentials. Report environment differences; do not pool cross-machine timings as a controlled benchmark.

## Reporting

Read `report-layout.md` and use the bundled renderer. Keep Declared and Observed distinct; the approved report places Declared and screenshots in the upper row, with full-width Observed below. Preserve substantive fields, missing-state semantics, source/campaign, audit scope and human review. Presentation is not collection or truth verification. Do not label absent language/coverage data as collected.
