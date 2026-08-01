---
name: spec-recalibrate
description: Recalibrate a repo's spec-driven docs against the code that now implements them. Sweeps every source-of-truth spec (spec-kit specs/, openspec openspec/specs/), maps each to its code, classifies drift, and with consent updates stale spec docs to match the code — spec docs only, never the code implementation — recording a per-spec calibration history. Use when asked to recalibrate specs, audit specs against code, refresh stale spec docs, or check whether specs still match the implementation.
argument-hint: "[spec-path|glob] [--changed-since <ref>] [--report-only] [--yes] [--direct]"
allowed-tools: Bash(git *), Bash(date *), Read, Edit, Write, Glob, Grep, Task
---

# Recalibrate Specs Against Code

Keeps spec-driven docs honest over time. Where `ado-open-pr` **Step 1.5** checks **one PR's diff** against **that change's** docs just before the PR, this sweeps **every existing source-of-truth spec** in the repo and re-checks it against the **code as it stands now**. **The code is the source of truth** — a spec that disagrees with the code it describes is the stale thing (people forget to sync docs after the last edits), so drifted specs are updated to match the code, with per-spec consent and a versioned history.

This skill is **local-only** — no Azure DevOps or MCP dependency; it only reads code and writes spec docs on the local filesystem. It's a maintenance companion to the `ado-*` PR skills: hand the recalibrated specs to `ado-open-pr` to commit and ship them.

> **Doc-only invariant — the one rule this skill cannot break.** Every write it makes lands in a **spec doc** (spec-kit `specs/…`) or an **openspec change proposal** — nowhere else. It **reads** code (`Glob` / `Grep` / `Read`) to check specs against it, but it never edits, creates, deletes, or stages a source file. A wrong-*looking* implementation is a **SUSPECT** finding for a human (Step 3), never something this skill fixes. If any step would touch a path outside the spec-doc roots enumerated in Step 1, **stop and report** — that is a bug in the run, not an action to take.

## Dependencies

- An SDD layout in the repo: **spec-kit** (`.specify/` + `specs/`) or **openspec** (`openspec/`). No layout → nothing to calibrate.
- Optional: `.agent-settings/project-config.md` (`## SDD Tool`) to pin the tool without detection.

This skill lives at `.agent-settings/skills/tools/spec-recalibrate/` and is auto-discovered by `import-skills.sh` — no manual copy or registry edit is needed.

## Arguments

All optional.

| Token / flag | Meaning |
|---|---|
| a path or glob (e.g. `specs/001-auth`, `openspec/specs/billing`) | calibrate only matching spec(s); default is **all** specs (full sweep) |
| `--changed-since <ref>` | narrow to specs whose implementing code changed since a git ref (e.g. `main`) |
| `--report-only` | detect and report drift; make **no** edits |
| `--yes` | apply DRIFTED-claim fixes without per-spec prompts (**never** applies SUSPECT / UNVERIFIABLE — see Step 3) |
| `--direct` | openspec only: hand-edit `openspec/specs/` directly instead of emitting a change proposal — bypasses openspec governance; use knowingly |

## Step 1 — Resolve the SDD layout and spec set

1. Resolve the SDD tool: `.agent-settings/project-config.md` → `## SDD Tool` → `Tool:` if present; else detect `.specify`/`.speckit`/`spec-kit.json` → **spec-kit**, `openspec/`/`.openspec`/`openspec.json` → **openspec**. Neither → report *"no SDD layout found — nothing to recalibrate"* and stop.
2. Enumerate the **source-of-truth specs** to calibrate:
   - spec-kit: every `specs/<NNN-name>/spec.md` (treat `plan.md` / `tasks.md` as secondary context, calibrated only if present and referenced by the spec).
   - openspec: every capability spec under `openspec/specs/**/spec.md`.
   - **Never calibrate the rubric:** `.specify/memory/constitution.md` and `openspec/project.md` are human-owned non-negotiables — read-only, never edited or version-stamped. Archived openspec changes (`openspec/changes/archive/**`) are history — excluded.
   - A path/glob arg narrows enumeration here (default is all). `--changed-since <ref>` narrowing is applied later in Step 2 — it needs each spec's code mapping to know which specs a code change actually touched.
3. Warn if the working tree is dirty (calibration will edit spec files, leaving them as working-tree changes); continue unless the user redirects. Capture the run date once: `date +%F`.

## Step 2 — Map each spec's claims to code

Decompose each spec into its individual **claims** — testable statements about behavior, endpoints, fields, config keys, steps. For **each claim**, try to locate the implementing code:
- Start from concrete anchors in or around the claim: file paths, module / function / type names, endpoints, config keys, CLI flags.
- Expand with `Glob` / `Grep` over the codebase for those anchors and the claim's domain terms.

Mark each claim **LOCATED** (you can point to the code that implements it) or **UNLOCATED** (you cannot confidently find its code). Record the evidence for each LOCATED claim; the union of a spec's evidence is its **evidence set**.

> **Locating gates editing, per claim — not per spec.** The absence of a behavior in the code you found is evidence of drift **only for a claim you positively located**. A claim you could not locate is **UNLOCATED**, never "the code dropped it" — treating a search miss as drift is how a correct spec gets rewritten to match code you never read. A spec that is 90% locatable does **not** make its unlocated 10% editable.

**`--changed-since <ref>` narrowing (applied here, after mapping):** if the flag was passed, compute the changed files with `git diff --name-only <ref>...HEAD`, then keep only specs whose evidence set intersects that list; report the rest as *"unchanged since `<ref>` — skipped"*. This runs after mapping because it needs each spec's evidence set.

## Step 3 — Classify each claim

Assign a verdict to **each claim** (a spec normally carries a mix of verdicts). Do this **inline** (read spec + code yourself) so the skill runs on every harness; you *may* offload a spec to a read-only `Task subagent_type="general-purpose"` sub-agent for token isolation **only where sub-agents are supported** (Claude Code yes; the VS Code Copilot agent no — fall back to inline). Never make the sub-agent a hard requirement.

| Verdict | Applies to a claim that… | Action |
|---|---|---|
| **ALIGNED** | is LOCATED and matches its code | none |
| **DRIFTED** | is LOCATED, its code changed, and the spec text is stale | edit-eligible (Step 5) |
| **SUSPECT** | is LOCATED but the *code* looks wrong (likely regression / lost behavior), not the spec | report for a human — **never auto-edit**; the spec may correctly document a code bug |
| **UNVERIFIABLE** | is UNLOCATED (its code was not found) | report for a human — **never auto-edit** |

A spec is edited in Step 5 **only for its DRIFTED claims**; ALIGNED, SUSPECT, and UNVERIFIABLE claims in the same spec are left exactly as written. Roll the per-claim verdicts up into a per-spec line for the report, but **never let a spec-level roll-up make an unlocated or suspect claim editable** — eligibility is decided per claim.

**Exclude calibration metadata from this analysis.** The `## Calibration history` section and the `calibrated:` / `calibration-version:` frontmatter keys (Step 6) are bookkeeping, not spec claims — do not treat them as claims, verify them against code, or diff them.

## Step 4 — Report

Emit a per-spec table rolling up its claims: spec, per-verdict counts, the specific DRIFTED mismatches with proposed edits, and every SUSPECT / UNVERIFIABLE claim with why. This is the entire output under `--report-only`.

## Step 5 — Update drifted claims (code→doc), with consent

Only **DRIFTED** claims are eligible to edit; touch nothing else in the spec. Before editing a spec, run `git status --porcelain -- <spec-path>`; if it already has uncommitted changes, **skip that spec** and report it — never edit over the user's in-progress work. For each editable spec, mirror the `ado-pr-resolve-comments` consent UX:
- Trivial edit → show a before/after diff; apply on approval.
- Larger rewrite → present an update plan; apply on approval.
- `--yes` applies **DRIFTED** claim fixes without prompting. `--yes` **never** touches SUSPECT or UNVERIFIABLE claims — those always wait for a human.
- A non-interactive / headless run reports drift but applies no edits unless `--yes` is set (and even then only DRIFTED claims) — never blocks on a prompt.

**openspec governance.** `openspec/specs/` is openspec's source of truth; its model routes changes through a proposal → `/opsx:apply` → `/opsx:archive`, and `ado-open-pr` Step 1.5 treats it as read-only for exactly that reason. So for openspec, recalibrate **does not hand-edit `openspec/specs/` by default** — it writes the code→doc deltas as an `/opsx:apply`-consumable change proposal under `openspec/changes/spec-recalibrate-<run-date>/`: a `proposal.md` (why + which capabilities drifted) plus per-capability `specs/<capability>/spec.md` deltas, the same `openspec/changes/<name>/{proposal.md, specs/}` layout `ado-open-pr` Step 1.5 documents. Pass `--direct` to hand-edit `openspec/specs/` instead (bypasses that governance — use knowingly). The spec-kit `specs/` tree has no such gate and is hand-edited directly. This deliberate difference is why recalibrate writes specs that Step 1.5 won't: Step 1.5 is a pre-PR guard, recalibrate is governance-aware maintenance.

## Step 6 — Record calibration history (per spec)

Applies only to spec files that received a **DRIFTED** edit in Step 5 (spec-kit `specs/`, or openspec `specs/` under `--direct`). A spec with no applied edit — every claim ALIGNED / SUSPECT / UNVERIFIABLE, or the spec skipped for uncommitted changes — is left **byte-for-byte untouched** (no version churn). In default openspec proposal mode nothing under `openspec/specs/` is edited, so the **change proposal itself (plus git) is the calibration record** — no per-spec stamp there.

For each edited spec:
1. Compute a **one-line change summary** from the **spec-content diff only** — exclude the frontmatter keys and the `## Calibration history` block below, so an entry never describes a previous entry (no self-feeding loop).
2. Bump frontmatter (creating a YAML frontmatter block if the spec has none): set `calibrated: <run-date>` and increment `calibration-version:` (start at `1` if absent).
3. Append to a `## Calibration history` section at the end of the spec (create it if missing):
   `- v<N> (<run-date>): <one-line change summary>`
   The block grows across runs — that is the version-controlled record; keep all entries.

## Step 7 — Assert doc-only and summarize

This skill **does not commit, push, or open a PR** — it calibrates spec docs and leaves them as working-tree changes. Shipping them is a separate, user-invoked step (`ado-open-pr`), so the user reviews the recalibration before it becomes a commit or PR.

1. **Assert the write surface (doc-only gate).** You know exactly which files you edited or created in Steps 5–6. Confirm that set contains **only** spec docs under a Step 1 root — spec-kit `specs/`, the openspec proposal dir `openspec/changes/spec-recalibrate-<run-date>/`, or `openspec/specs/` under `--direct`. If your own edit set includes anything else — above all a source file — that is a bug in this run: **reverse that specific edit in place** — apply the inverse of the `Edit` / `Write` you just made — and report it as a contract violation. If you cannot reconstruct the file's original content, **stop and hand it to the human**; never run `git restore` / `git checkout -- <file>` / `git clean` on it (those revert to HEAD and would erase the user's pre-existing uncommitted work).
2. Report: counts by verdict (aligned / updated / suspect / unverifiable), the specs edited (left modified in the working tree, unstaged), and **every SUSPECT / UNVERIFIABLE spec that needs a human** (with why). If any spec was edited, point the user at `ado-open-pr` to review, commit, and ship the recalibration.

## Notes

- **Code is never edited.** A SUSPECT verdict flags a possible code bug for a human to resolve; recalibrate only ever changes docs.
- **Best-effort per spec:** a spec that can't be mapped or read is reported as UNVERIFIABLE and skipped — it never blocks the rest of the sweep.
- The `## Calibration history` block and the `calibrated:` / `calibration-version:` keys are metadata — excluded from drift analysis (Step 3) and from the change-summary diff (Step 6).
- Relationship to siblings: `ado-open-pr` Step 1.5 = pre-PR, per-change guard; this = deliberate, repo-wide, governance-aware maintenance. They intentionally differ on whether `openspec/specs/` is writable.
