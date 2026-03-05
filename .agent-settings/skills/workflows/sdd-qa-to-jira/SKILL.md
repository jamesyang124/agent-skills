---
name: sdd-qa-to-jira
description: Reads local spec-kit artifacts and derives BDD QA scenarios, then creates QA sub-tickets under the existing root Jira ticket from Phase 7. Use this as the explicit QA hand-off after a PR is created in the spec-kit native SDD workflow.
---

# SDD QA to Jira

This skill bridges the **Implement** and **QA** phases of the spec-kit native SDD workflow. It reads all spec-kit artifacts in the feature folder, derives end-to-end BDD scenarios, presents them to the RD for review, then creates QA sub-tickets under the existing root Jira ticket — no new root ticket is created.

**Key principle:** Sub-tickets describe *what* to verify (Given/When/Then), not *how*. SDET owns the testing method, order, and approach entirely.

## QA Ticket Template (MANDATORY)

All QA sub-tickets **must follow** the BDD template at:
`references/qa-ticket-template.md` (relative to this skill folder: `.agent-settings/skills/sdd-qa-to-jira`)

## Prerequisites

**IMPORTANT**: This skill requires the **Atlassian MCP Server** to be installed and configured.

Before using this skill, ensure:
1. ✅ Atlassian MCP server is installed (see `.agent-settings/mcps/install-atlassian-mcp.sh`)
2. ✅ Credentials are configured in `.env.mcp-atlassian`
3. ✅ A PR is open (this is the prerequisite that proves implementation is committed and reviewable)
4. ✅ The existing root Jira ticket key from Phase 7 is available (e.g. `PROJ-101`)
5. ✅ The following MCP tools are available:
   - `mcp__atlassian__jira_get_issue`
   - `mcp__atlassian__jira_create_issue`
   - `mcp__atlassian__jira_add_comment`

If the MCP server is not configured, guide the user to run:
```bash
.agent-settings/mcps/install-atlassian-mcp.sh
```

## Input Sources (Tiered by Priority)

| Priority | Source | Contribution |
|----------|--------|-------------|
| Core | `prd-source.md` | Business intent and user-facing requirements → business-perspective BDD scenarios |
| Core | `spec.md` | RD's technical interpretation → scenario context and constraints |
| Core | `requirements.md` | Technical acceptance criteria → primary BDD scenarios |
| Core | `plan.md` | Technical decisions, alternatives rejected → edge cases |
| Extended | Any other `*.md` in the feature folder | ADRs, impl notes, discovery notes → richer edge cases |
| Required | Root Jira ticket key (from Phase 7) | Parent for QA sub-tickets |
| Optional | Confluence design review page ID | Version stamp reference |

**Scan strategy:** Read all `*.md` files found in the spec-kit feature directory. Skip project-level files (`README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`). Implementation notes written during coding (edge cases, discovered constraints, API quirks) are especially valuable — they often surface the best QA scenarios that the original spec didn't anticipate.

## Process

### Step 1: Confirm PR Prerequisite

Before proceeding, confirm with the user:
- Is a PR open for this feature?
- Is the implementation ready for QA (not just "PR exists", but the RD's deliberate judgment)?

If the user hasn't explicitly confirmed readiness, surface this: "This skill creates QA tickets as a formal hand-off to SDET. Are you confident the implementation is ready for testing?"

### Step 2: Locate Spec-Kit Artifacts

- Scan the current working directory (and one level up) for `*.md` files.
- Skip: `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`.
- Prioritize reading: `prd-source.md`, `spec.md`, `requirements.md`, `plan.md` first.
- Then read any remaining `*.md` files (impl notes, ADRs, etc.).
- If no files are found, ask the user for the spec-kit feature directory path.
- Read all found files in full before proceeding.

### Step 3: Confirm Root Ticket

- The user should provide the root Jira ticket key (e.g. `PROJ-101`) from Phase 7.
- If not provided, ask: "What is the root Jira ticket key for this feature? (created in Phase 7 with `/confluence-tech-plan-to-jira`)"
- Retrieve the root ticket with `mcp__atlassian__jira_get_issue` to confirm it exists and get its project key.

### Step 4: Derive BDD Scenarios

Read all spec-kit artifacts and derive scenarios grouped by type:

**Happy paths** — the primary success flows described in `requirements.md` and `spec.md`.
**Edge cases** — boundary conditions, alternative inputs, unexpected states from `plan.md` and impl notes.
**Error paths** — failure modes, timeouts, invalid inputs, degraded state from `spec.md` and impl notes.
**Non-functional** — performance, security, data integrity requirements from `requirements.md`.

**Derivation rules:**
- Each scenario maps to exactly one BDD triple (Given/When/Then).
- Scenarios must be observable (the "Then" must be something SDET can verify without access to internals).
- Do not write test steps — only behavioral outcomes.
- Source every scenario to a specific file and section so the RD can verify the derivation.

**Scenario count guidance:**
- Minimum: 3 scenarios (at least one happy path, one edge case, one error path).
- Maximum: ~10 scenarios per feature (more than 10 suggests the feature scope needs scoping).
- If scenarios exceed 10, group related ones and flag to the RD for scope discussion.

### Step 5: Present Proposed Scenarios for Review

Before creating any Jira tickets, present all derived scenarios to the RD:

```
Proposed QA scenarios for [Feature Name]
Derived from: spec.md, requirements.md, plan.md, [other files found]

Happy Paths:
1. [SCENARIO] [Short name]
   Given [precondition]
   When [action]
   Then [outcome]
   Source: requirements.md §[section]

Edge Cases:
2. [SCENARIO] [Short name]
   Given [precondition]
   When [action]
   Then [outcome]
   Source: plan.md §[section]

Error Paths:
3. [SCENARIO] [Short name]
   Given [precondition]
   When [action]
   Then [outcome]
   Source: spec.md §[section]

Root ticket: [PROJ-101]
Sub-tickets will be created as: [QA][SERVICE] [Scenario name]

Shall I create these as Jira sub-tickets? (Type y to proceed, n/skip to cancel, or describe any changes to make first.)
```

### Step 6: Create QA Sub-Tickets in Jira

After RD confirmation, create one sub-ticket per scenario using `mcp__atlassian__jira_create_issue`:

- **Issue type:** Sub-task
- **Parent:** Root ticket key from Step 3
- **Summary:** `[QA][SERVICE] [Short scenario name]`
- **Description:** Follow the BDD template at `references/qa-ticket-template.md`

Do **not** include PR URL or Confluence page links in sub-tickets — those belong on the root ticket only.

### Step 7: Update Root Ticket with QA Hand-Off Note

After creating all sub-tickets, post a comment on the root ticket using `mcp__atlassian__jira_add_comment`:

```
## QA Verification

PR: [PR URL — ask user if not known]
Source: [Confluence design review URL — ask user if not known, or mark as N/A]
Spec version: [from local files date or Confluence page version]

QA sub-tickets added:
- [PROJ-104] [Short scenario name]
- [PROJ-105] [Short scenario name]
- [PROJ-106] [Short scenario name]

Scenarios derived from: spec.md, requirements.md, plan.md, [other files].
SDET owns testing approach — sub-tickets define WHAT to verify, not HOW.
```

### Step 8: Report

After all tickets are created:

```
✅ QA hand-off complete

Sub-tickets created under [PROJ-101]:
- [PROJ-104]: [QA][SERVICE] [Scenario 1]
- [PROJ-105]: [QA][SERVICE] [Scenario 2]
- [PROJ-106]: [QA][SERVICE] [Scenario 3]

Root ticket [PROJ-101] updated with QA hand-off note.

Next steps:
  1. Share the ticket keys with your SDET.
  2. SDET owns execution order and testing method.
  3. SDET closes sub-tickets as scenarios are verified.
  4. When all QA sub-tickets are closed, the feature is ready for release.
```

## Scenario Quality Checklist

Before presenting scenarios to the RD, verify each one:

- [ ] "Then" describes an observable outcome (not an internal state)
- [ ] Scenario is independent of other scenarios (can run in isolation)
- [ ] No test steps — only Given/When/Then
- [ ] "Given" describes a realistic precondition (not test setup steps)
- [ ] Scenario maps to at least one requirement or spec section

If a scenario fails this check, either fix it or drop it. Do not create low-quality tickets.

## Handling Missing Files

| Scenario | Behavior |
|----------|----------|
| `requirements.md` missing | Derive primary scenarios from `spec.md`; warn that coverage may be incomplete. |
| `spec.md` missing | Proceed with `requirements.md` and `plan.md`; warn RD. |
| `plan.md` missing | Edge cases may be thin; warn RD and proceed with what's available. |
| `prd-source.md` missing | Skip business-perspective scenarios; proceed with technical files. |
| All files missing | Stop. Ask user to provide the spec-kit feature directory path. |
| Root ticket key not provided | Ask user before proceeding — cannot create sub-tickets without a parent. |

## Workflow Integration

This skill sits at the **Implement → QA** boundary in the spec-kit native workflow:

```
[/generate-pr-notes]
    PR created (phase exit condition for Phase 8)
         │
         ▼ (RD deliberate decision — not automatic)
[sdd-qa-to-jira]  ← YOU ARE HERE
    Reads spec-kit *.md files → Derives BDD scenarios → Creates QA sub-tickets
         │
         ▼
[SDET execution]
    SDET claims sub-tickets → Executes in own order/method → Closes tickets when verified
         │
         ▼ (all QA sub-tickets closed)
[Release ready]
```

## Tips for the Agent

- **RD judgment, not automation**: This skill is triggered by the RD's deliberate decision. Surface the readiness question clearly — don't skip it.
- **prd-source.md is valuable**: Business-perspective scenarios from the PO's original requirements often catch gaps that technical specs miss. Always read it if present.
- **Implementation notes are gold**: Files like `impl-notes.md`, `decisions.md`, or any `*.md` written during coding often contain the best edge cases (API quirks, discovered constraints, timing issues). Prioritize these for edge case scenario derivation.
- **No test steps**: If you find yourself writing "Step 1: navigate to...", that's a test step. Convert it to a Given/When/Then behavioral description.
- **Sub-tickets are lean**: All traceability (PR link, Confluence link, spec version) goes on the root ticket comment. Sub-tickets contain only the BDD scenario and brief context.
- **Confirm before creating**: Always present scenarios for RD review before touching Jira. The RD may want to add, remove, or reword scenarios.
