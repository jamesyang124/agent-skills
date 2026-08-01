# tech-plan-to-wiki

## Overview

Reads local spec-kit artifacts (`spec.md`, `plan.md`, `requirements.md`) and publishes a structured design review page to Confluence. Use this at the **Plan → Review** transition in the SDD workflow to give the team a shared surface to read and comment on the technical plan.

**Key principle:** `plan.md` and `requirements.md` are the source of truth. The Confluence page is a read-only shared view. Team feedback flows back to the RD who refines local files, then re-publishes with this skill.

## When to Use

- Technical plan is ready and needs team review
- At the Plan → Review boundary of the spec-kit native SDD workflow
- Re-publishing after incorporating team feedback into spec-kit files

## Prerequisites

- Atlassian MCP Server installed and configured (`install-atlassian-mcp skill`)
- `~/.env.mcp-atlassian` credentials configured
- `spec.md`, `plan.md`, and `requirements.md` present locally

## Artifact → Page Section Mapping

| Page Section | Primary Source |
|---|---|
| Context & Problem | `spec.md` |
| Technical Proposal | `plan.md` |
| Requirements | `requirements.md` |
| Design Considerations | `plan.md` (alternatives/options) |
| Open Questions | `plan.md` + `spec.md` TBDs |

Missing files → section marked `[TODO — source file not found]`.

## Usage

```
/tech-plan-to-wiki [page-id]
```

- No argument → creates a new page
- With a page ID → updates the existing page and appends a revision history row

## Page Status Lifecycle

```
Draft → Under Review → Approved (v1)
```

- **Draft**: set automatically on first publish
- **Under Review**: update manually when team review begins
- **Approved (v1)**: set when consensus is reached; triggers `/tech-plan-to-ticket`

## Workflow Position

```
[spec-kit plan] → plan.md + requirements.md
        ↓
[tech-plan-to-wiki]  ← HERE
        ↓ Confluence page (Draft)
[Team Review Loop]
  team comments → RD refines spec-kit → re-publishes
        ↓ (Approved v1)
[tech-plan-to-ticket]
```

## Notes

- Always confirm with user before publishing (shows section mapping and create vs. update action)
- On first publish, save the page ID — required for future re-runs to avoid duplicates
- Never invent content; use `[TODO]` with explanation for gaps
- Source-of-truth footer is mandatory on every publish to prevent direct page edits by reviewers
- Revision history table is appended on every update run
