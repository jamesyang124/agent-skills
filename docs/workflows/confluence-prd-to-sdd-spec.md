# confluence-prd-to-sdd-spec

## Overview

Fetches an external PRD from Confluence (written by PO/PM) and transforms it into a structured local `prd-source.md` file that the RD can reference when running `spec-kit specify`. Bridges the PO handoff into the spec-kit native SDD workflow — no manual copy-paste from Confluence.

**Key principle:** The skill is a faithful import only. It does not add, infer, or editorialize. Gaps in the PRD appear as explicit `[TBD]` markers for the RD to address during `spec-kit specify`.

## When to Use

- A PO/PM has written a PRD in Confluence and it's ready for RD pickup
- Starting the **Specify** phase of the SDD workflow
- Asked to "import the PRD" or "fetch the PRD from Confluence"

## Prerequisites

- Atlassian MCP Server installed and configured (`.agent-settings/mcps/install-atlassian-mcp.sh`)
- `.env.mcp-atlassian` credentials configured
- Confluence page ID or search keywords for the PRD

## Output

Creates `prd-source.md` locally with this structure:

```
# [Feature Name] — PRD Source
> Imported from Confluence: "[Page Title]" (ID: ...)
> Last fetched: [date]

## Problem Statement
## Goals
## Non-Goals / Out of Scope
## User Stories / Use Cases
## Functional Requirements
## Non-Functional Requirements
## Constraints
## Open Questions (from PO)
```

Missing sections are marked `[TBD — not specified in PRD]`.

## Process

1. **Locate PRD** — user provides Confluence page ID or search keywords; skill fetches the page
2. **Transform** — maps PRD sections to the standard structure above; marks gaps as `[TBD]`
3. **Confirm output path** — defaults to `./prd-source.md`; user can override
4. **Write file** — saves `prd-source.md` locally
5. **Report** — lists which sections were populated and which are `[TBD]`

## Workflow Position

```
[PO writes PRD in Confluence]
        ↓
[confluence-prd-to-sdd-spec]  ← HERE
        ↓ prd-source.md created
[spec-kit specify]
        ↓ spec.md produced
[spec-kit plan] → plan.md + requirements.md
        ↓
[/sdd-tech-plan-to-confluence]
```

## Notes

- Re-runs are safe — if PO updates the Confluence PRD, re-run to get a fresh `prd-source.md` and check `git diff` before re-running `spec-kit specify`
- Never add technical opinions or architecture suggestions — those are added by the RD during `specify`
- `[TBD]` markers are intentional discussion points for the specify session, not errors
