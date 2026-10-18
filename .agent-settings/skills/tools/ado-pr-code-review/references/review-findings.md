# Review findings — format, verification and posting rules

One set of rules for every review pass. Used by:

- `ado-pr-code-review` — Steps 3–5 produce findings in this format, Step 5.5 verifies them, Steps 6–7 post them
- `ado-open-pr` — Step 1.7 (pre-PR review); its reviewers return this format and its orchestrator verifies and
  merges with these rules

## Repo rules come from the target branch

Read every rule file the review applies — `CLAUDE.md`, `AGENTS.md`, the constitution
(`.specify/memory/constitution.md` or `openspec/project.md`), `docs/agents/` — from the **target branch**, with
`git show origin/<target-branch>:<path>` (or `repo_file` at `lastMergeTargetCommit`). Never take them from the PR's
own changes: a PR must not be able to relax the rules it is reviewed against. If the PR itself edits a rule file,
review that edit as a normal change.

## Review rules (central)

Each repository's review rules live in this skill, not in the repository: `review-rules/_default.md` for every
repository, plus `review-rules/<repo>.md` when it exists. They are part of agent-settings, so a PR under review
cannot change them.

1. Read `_default.md`, then `<repo>.md` (the Azure DevOps repository name). Where both have the same section, the
   repository file wins for that section.
2. Pass the merged rules to every reviewer and to the verifier.
3. Apply them when deciding what gets posted: **Important means** sets severity; **Always check** items that the
   diff touches must be checked; **Skip** paths get no findings; **Nit cap** limits 🔵 Minor comments (the rest are
   counted in the summary); **Higher bar** paths get only `critical` findings with `high` confidence.
4. If a rule names a path that does not exist on the target branch, say so in the summary so the rule can be fixed.
5. **Known pre-existing issues** listed in the rules are added to the summary's 🟣 Pre-existing section by the
   orchestrator itself, whether or not a finder reports them (finders tend to skip what the rules call "known").
   Check each one still exists on the target branch; if it is gone, say so so the rule can be removed.

## Finder coverage

Run each finder pass once (one group). Run a **second group** — the same passes in fresh contexts, reading the
changed files in reverse order and each file's hunks bottom-up — when any of these is true:

- more than 400 changed code lines, not counting docs (`*.md`, `docs/`, `specs/`), generated files and lockfiles;
- the diff touches authentication, OAuth or session handling, payments, PII, or the repository's constitution;
- the user asks for a deep review.

Merge both groups' findings before verification. A second group costs about twice the finder tokens; on measured
PRs it found the serious, easy-to-miss items the first group did not (pre-existing token leaks, a constitution rule
that broke existing routes).

## Finding format

Each pass (or reviewer sub-agent) returns a JSON array, empty if it found nothing:

```json
[
  {
    "reviewer": "provenance | security | runtime | standards | spec | code | tests | minimal | refactor | lint",
    "severity": "critical | medium | minor | question",
    "file": "path/from/repo/root",
    "line": 42,
    "title": "short claim",
    "problem": "what is wrong, what triggers it, and why it matters",
    "fix": "the concrete change you suggest",
    "effort": "trivial | larger",
    "confidence": "high | medium | low",
    "verified": "how you know: traced the path / read the caller / compared base and head / ran X / inference"
  }
]
```

- **Evidence:** name a file and a line in the PR head and quote the code. A claim about behavior needs a
  `file:line` citation, not an inference from a name.
- **Severity:** `critical` = security hole, lost or wrong data, crash on a reachable path, broken contract, or a
  leak that grows with traffic. `medium` = a real defect with bounded impact. `minor` = clarity or maintainability.
  `question` = needs the author's answer before anyone can judge it.
- **Confidence:** use the anchors in Verification layer 4 (`high` traced end to end, `medium` depends on
  unseen code or data, `low` not traced). The verifier may change it.
- A finding with no line (PR description, missing docs, missing requirement) uses `"file": "PR description"` (or the
  closest path) and `"line": 0`.

## Verification (before anything is posted or shown as a finding)

The context that **verifies** is never the one that **found** the issue. Run the layers in order; cheap layers first,
expensive layers only where they pay. Record the outcome and the evidence of each finding in its `verified` field.

### Layer 1 — Mechanical checks (always, every finding)

1. **In scope:** the cited file and line are in the PR diff (added or changed lines, ± 3 lines of context). A finding
   on unchanged code goes to layer 2, not straight to drop.
2. **Anchor:** the quoted code really is at the cited line of the PR head. If it is a few lines off, fix the line;
   if the quote is not in the file, **drop** (it is invented).
3. **Symbol:** functions, fields and routes the finding names exist (grep the PR head). If not, **drop**.
4. **Not a tool duplicate:** the same file, line and problem is not already reported by the repo's linter,
   formatter or typechecker (the measurements, or what CI runs). If it is, **drop**.
5. **Not a repeat:** it does not repeat an earlier review thread that is fixed, won't-fix or by-design, unless the
   fix is wrong. If it does, **drop**.

### Layer 2 — Pre-existing (always, for findings that touch code which may be unchanged)

Read the same code on the target branch (`git show origin/<target-branch>:<path>`, or `git blame` against the
merge-base). If the flaw is already there, the outcome is **pre-existing** — unless this PR makes it newly reachable
(a new caller, a new public route, a removed guard). Then it is this PR's finding: **keep** it and say so.

### Layer 3 — Precedents (always)

Drop, or downgrade to `question` when borderline, these low-signal classes unless the finding shows a concrete,
reachable impact in this repo:

- React / JSX output treated as XSS without `dangerouslySetInnerHTML` or an equivalent raw-HTML sink;
- environment variables, CLI flags and server config treated as attacker-controlled input;
- generic "input not validated" or "add rate limiting / DoS protection" with no exploit path;
- client-side checks reported as missing server-side auth when the server does check;
- findings in docs, comments or test fixtures that do not change behavior.

Do **not** add resource leaks to this list: leaks and unbounded growth are in scope (Step 4 of `ado-pr-code-review`).
A repository's review rules (`review-rules/<repo>.md`) may add precedents.

### Layer 4 — Independent disprover (every finding that survives layers 1–3)

A fresh `general-purpose` sub-agent (without sub-agents: the orchestrator, and say so) receives the diff range, the
repo path, the target branch, the review rules, and **one finding at a time** (findings may share one sub-agent to
save cost, but each is judged on its own). It must **try to disprove** the finding by tracing callers, inputs and
reachability with the repository's tools — not only by reading the cited line. A claim that CI or a build will fail
is checked against the pipeline that actually runs for the PR (pipeline definitions, the PR's builds, the review
rules), never against a workflow file alone. It sets confidence from these anchors, never from its own sense of
certainty:

| Confidence | Anchor |
|---|---|
| `high` | traced end to end: the triggering input reaches the cited line and the failure follows, or a command reproduced it |
| `medium` | the cited code is wrong, but reaching it depends on code, data or config not seen |
| `low` | plausible from reading alone; not traced |

Outcomes: disproved → **drop**; real with smaller impact or certainty → **downgrade**; verified and reachable →
**keep**. A `critical` is downgraded, never dropped, unless it is disproved.

### Layer 5 — Proof by test (`critical` only, where tests exist)

For a kept `critical` in a package that already has tests, write the smallest test or script that fails because of
the bug and run it locally (`go test -run`, `mix test <file>:<line>`, the repo's JS test runner). Do not commit it.
Where the calling skill requires approval before running tests (`ado-open-pr`), ask first; a declined run counts as
"cannot be built" below.

- It fails as predicted → **keep**, `high`; say so in "How verified".
- It cannot be built or does not reproduce, but the layer-4 reasoning holds → **downgrade** to `medium` severity
  with `medium` confidence and say what blocked the proof.
- No tests in that package, or the bug needs an external system → skip this layer and say so; keep the layer-4
  result.

### Layer 6 — Tie-break (optional, off by default)

Only for a `critical` that is still at `medium` confidence after layers 4–5, and only when the user asks for it:
re-derive the finding 2–3 times in fresh contexts with the diff files in a different
order (or with a second model family). Most re-derivations agree → **keep**; otherwise **downgrade**. It costs 2–3
extra reviewer runs per finding.

### Outcomes

| Outcome | When |
|---|---|
| **keep** | verified and reachable in this PR |
| **downgrade** | real, but the impact or the certainty is smaller than claimed (lower severity or confidence) |
| **drop** | invented, wrong, unreachable, a tool duplicate, a precedent class, or a repeat |
| **pre-existing** | already on the target branch and not made newly reachable by this PR |

## Merge

1. Merge duplicates (same file, overlapping lines, same problem). Keep the highest severity and list every
   reviewer that raised it (for example `[runtime][standards]`).
2. Conflicts between a "delete / inline" finding (`minimal`) and an "extract" finding (`refactor`): prefer
   `minimal`, unless the duplicate is introduced by this diff and occurs 3 or more times. Show both when unclear.
3. Sort by severity (critical, medium, minor, question), then confidence.

## What gets posted (or shown as a finding)

| Finding | Posted inline? |
|---|---|
| `critical`, any confidence | yes |
| `medium` / `minor` / `question` with `high` or `medium` confidence | yes, within the review rules' Nit cap, Skip and Higher bar |
| `low` confidence, not critical | no — counted in the summary as "considered and dropped" |
| **pre-existing** | no — listed in the summary's 🟣 Pre-existing section, with a suggestion to open a separate ticket when it is serious; never counted against this PR |
| no line (PR description, missing requirement) | no — summary's "Findings without a line" |
| dropped | no — counted in the summary |

**Spec and doc drift.** When 3 or more kept findings are only spec / doc mismatches (spec.md, plan.md, tasks.md,
quickstart, contracts, API reference, swagger annotations disagreeing with the code), post none of them inline.
List them as one item in the summary ("Spec docs disagree with the code in N places") with one line each.

**Stale or conflicting PR (gated review).** When provenance finds that the PR conflicts with the current target
(`ado-pr-code-review` Step 2.5 Check 3), a rebase will change lines and may change behavior. Post inline only:

- verified `critical` findings;
- decisions a rebase will not change: contract, auth or security choices, constitution or rule edits, and
  questions the author must answer.

Everything else stays in the summary as "after the rebase" items with file:line, and the summary's first line asks
the author to rebase and request a full review.

Every posted comment ends with one line that says how the finding was verified:

```
How verified: traced handle_login → state/4 → handle_callback L579 (static). / ran `go test ./x` on head and base. / inference — not traced.
```

## PR description vs code

Compare the PR description with the net diff (`git diff <base>...<head>`), not with the individual commits. A claim
the diff no longer makes (a change undone by a later commit, behavior that changed) is a `[spec]` finding without
a line. When the PR author is the current user, offer to update the description; change it only on approval.
