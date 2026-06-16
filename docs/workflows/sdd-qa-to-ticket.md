# sdd-qa-to-ticket

## Overview

Reads local spec-kit artifacts and derives BDD QA scenarios, then creates QA sub-tickets under the existing root Jira ticket. This is the formal QA hand-off step after a PR is created in the spec-kit native SDD workflow.

**Key principle:** Sub-tickets describe *what* to verify (Given/When/Then), not *how*. The SDET owns the testing method, order, and execution approach entirely.

## When to Use

- A PR is open and the implementation is ready for QA
- Handing off to SDET at the **Implement → QA** boundary of the SDD workflow
- After `/generate-pr-notes` has produced a PR

## Prerequisites

- Atlassian MCP Server installed (run `/install-atlassian-mcp`)
- A PR is open for the feature
- Root Jira ticket key from Phase 7 (created by `/tech-plan-to-ticket`)

## Input Sources

| Priority | File | Contribution |
|---|---|---|
| Core | `prd-source.md` | Business-perspective BDD scenarios |
| Core | `spec.md` | Technical context and constraints |
| Core | `requirements.md` | Primary BDD scenarios |
| Core | `plan.md` | Edge cases from alternatives and rejected decisions |
| Extended | Any `*.md` in feature folder | ADRs, impl notes — best source of edge cases |

## Process

1. **Confirm PR readiness** — explicitly asks RD if implementation is ready for QA
2. **Locate spec-kit artifacts** — scans cwd and one level up for `*.md` files
3. **Confirm root ticket** — fetches `PROJ-101` to verify it exists
4. **Derive BDD scenarios** — groups into happy paths, edge cases, error paths, non-functional
5. **Present for review** — shows all scenarios to RD before touching Jira (min 3, max ~10)
6. **Create sub-tickets** — one Jira sub-task per scenario under the root ticket
7. **Update root ticket** — posts QA hand-off comment with PR URL, spec version, and sub-ticket list

## Sub-Ticket Format

- **Summary**: `[QA][SERVICE] Short scenario name`
- **Description**: BDD template (`references/qa-ticket-template.md`)
- **Type**: Sub-task under root ticket

## Workflow Position

```
[/generate-pr-notes] → PR created
        ↓ (RD deliberate decision)
[sdd-qa-to-ticket]  ← HERE
        ↓
[SDET execution] → closes sub-tickets
        ↓ (all QA tickets closed)
[Release ready]
```

## Notes

- Never creates a new root ticket — always sub-tickets under the existing one
- PR URL and Confluence link go on the root ticket comment only, not sub-tickets
- Implementation notes (`impl-notes.md`, `decisions.md`, etc.) often yield the best edge case scenarios
- Scenario "Then" must be observable by SDET without access to internal state
