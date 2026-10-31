# Audit and quality

## 1. Screenshot audit (orchestrator, strongest model)

Run `python3 scripts/contact_sheets.py --base <workspace> --campaign <id> --out archive/<id>/contact_sheets`. Each item
gets one row with its first, middle and last screenshot.

- One live content frame proves content was reached only. Before audit ok, inspect claim evidence, coverage and time/input records per `evidence-review.md`; contact sheets alone are insufficient.
- Reject (`rejected_visual_audit`) an item whose screenshots show only loading, a logo, a menu, a tutorial, a result
  screen or a frozen frame.
- Downgrade `played` to `partial` when the claimed seconds are not supported. For example: an empty board, a score that
  never changes, or identical frames.
- Check repetitive templates and unsupported claims. There is no calibrated similarity cutoff; do not apply a numeric threshold without defining and validating the metric.

Write each verdict into that attempt's `audit` field.

## 2. Validation (`scripts/validate_descriptions.py`)

The legacy validator checks structural compatibility only. For new campaigns use `--strict --meta <export>`; this also requires matching item/campaign, a completed non-rejecting audit, explicit eligibility and evidence membership in the latest attempt. Neither mode proves factual accuracy. Legacy checks:
- the outcome is `played` or `partial`;
- the audit did not reject it;
- `summary` and `semantic_description` are present, and the description is ≥ 200 words (each CJK character counts as
  half a word);
- every screenshot it cites exists;
- if `--meta` is given, the item is public and not adult.

The script writes `derived/descriptions.validated.json` and `derived/report.json`.

## 3. Spot-check (human)

Run `python3 scripts/spot_check.py --base <workspace> --campaign <id> --rate 0.1 --seed <n>`. It writes
`archive/<id>/spot_check.json`. Then run `python3 scripts/review_sheet.py --base <workspace> --spot archive/<id>/spot_check.json`, which writes one local HTML page with each description next to its screenshots for the reviewer. Open it locally; do not publish it. For each sampled item, a human opens the description and its screenshots and records
one of:

- `correct`: every claim is supported;
- `minor`: small inaccuracies, but the description is still usable for search;
- `wrong`: the main claim (genre, mechanic or goal) is wrong;
- `hallucinated`: it describes things the screenshots do not show.

Record them in `spot_check.json` under `verdicts`.

## 4. Reliability report (every campaign)

| Metric | Definition |
|---|---|
| attempted | items with an attempt in this campaign |
| reached content | played + partial + rejected_visual_audit |
| **audit rejection rate** | rejected_visual_audit ÷ reached content |
| over-claim rate | downgraded played→partial ÷ claimed played |
| valid descriptions | from `report.json` |
| **spot-check accuracy** | (correct + minor) ÷ human-reviewed; report reviewed/sample coverage and wrong + hallucinated separately; no reviewed items = unknown |
| mismatches | from `observed_kind_mismatches.jsonl` |
| blockers | lines in `blockers.md`, grouped |
| needs a human | paywall, device gate, unresponsive-input items |

Use the observed data downstream (for example as synthetic training or search data) only after spot-check accuracy has
been measured. Report it with its sample size; with n = 7, the confidence interval is wide.

Reference numbers (one real deployment, 773 attempts):
- **Fixed-script capture** (no closed loop): 81% of the screenshots that claimed gameplay were rejected in audit. Do not
  use this method.
- **Closed loop**: a 9.4% audit rejection rate. A mid-tier player model also over-claimed `played` on 62 runs that had
  less than 30 s of play; the orchestrator caught these.
