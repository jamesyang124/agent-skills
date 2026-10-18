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
- **Confidence:** `high` = traced and it fails as described; `medium` = likely, depends on code or data not seen;
  `low` = a suspicion.
- A finding with no line (PR description, missing docs, missing requirement) uses `"file": "PR description"` (or the
  closest path) and `"line": 0`.

## Verification (before anything is posted or shown as a finding)

The context that **verifies** is never the one that **found** the issue.

| Situation | Who verifies |
|---|---|
| 15 findings or fewer, none critical | the orchestrator, against the code |
| more than 15, or any `critical` | one fresh `general-purpose` verifier sub-agent that receives only the diff range, the repo path, the target branch and the findings. Its job is to **try to disprove** each finding. Without sub-agents, the orchestrator does it and says so |

For each finding, decide one outcome and record why:

| Outcome | When |
|---|---|
| **keep** | the code at the cited line does what the finding says, on a reachable path |
| **downgrade** | real, but the impact or the certainty is smaller than claimed (lower severity or confidence) |
| **drop** | wrong, not reachable, already handled elsewhere, or outside this diff |
| **pre-existing** | the same code already exists on the target branch (`git show origin/<target-branch>:<path>`, or `git blame` shows the lines predate the merge-base). Real, but not introduced by this PR |

Also drop:
- anything a linter or formatter in the repo would catch (formatting, line length, import order);
- a finding that repeats an earlier review thread that is fixed, won't-fix or by-design, unless the fix is wrong.

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

Every posted comment ends with one line that says how the finding was verified:

```
How verified: traced handle_login → state/4 → handle_callback L579 (static). / ran `go test ./x` on head and base. / inference — not traced.
```

## PR description vs code

Compare the PR description with the net diff (`git diff <base>...<head>`), not with the individual commits. A claim
the diff no longer makes (a change undone by a later commit, behavior that changed) is a `[spec]` finding without
a line. When the PR author is the current user, offer to update the description; change it only on approval.
