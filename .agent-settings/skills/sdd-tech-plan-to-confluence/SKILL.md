---
name: sdd-tech-plan-to-confluence
description: Reads local spec-kit artifacts (spec.md, plan.md, requirements.md) and publishes a collaborative design review page to Confluence. Use this at the Plan→Review transition in the spec-kit native SDD workflow to share your technical plan with the team.
---

# SDD Tech Plan to Confluence

This skill bridges the **Plan** and **Review** phases of the spec-kit native SDD workflow. It reads spec-kit's local output files and publishes a structured design review page to Confluence, giving the team a shared surface to read, comment, and give feedback — without ever editing the source files directly.

**Key principle:** `plan.md` and `requirements.md` are the **source of truth**. The Confluence page is a **shared view** for team review only. Team feedback never goes directly into Confluence — it flows back to the lead RD who refines the local spec-kit files, then re-publishes with this skill.

## Design Review Template (MANDATORY)

All published pages **must follow** the template at:
`references/design-review-template.md` (relative to this skill folder: `.agent-settings/skills/sdd-tech-plan-to-confluence`)

Use the template as the structural skeleton. Populate each section from the spec-kit artifacts. Use `[TODO]` for gaps — never invent content.

## Prerequisites

**IMPORTANT**: This skill requires the **Atlassian MCP Server** to be installed and configured.

Before using this skill, ensure:
1. ✅ Atlassian MCP server is installed (see `.agent-settings/mcps/install-atlassian-mcp.sh`)
2. ✅ Credentials are configured in `.env.mcp-atlassian`
3. ✅ The following MCP tools are available:
   - `mcp__atlassian__confluence_get_page`
   - `mcp__atlassian__confluence_search`
   - `mcp__atlassian__confluence_create_page`
   - `mcp__atlassian__confluence_update_page`

If the MCP server is not configured, guide the user to run:
```bash
.agent-settings/mcps/install-atlassian-mcp.sh
```

## Artifact → Page Section Mapping

| Page Section | Primary Source | Secondary Source |
|---|---|---|
| Context & Problem | `spec.md` | — |
| Technical Proposal | `plan.md` | — |
| Requirements | `requirements.md` | `spec.md` |
| Design Considerations | `plan.md` (alternatives/options sections) | — |
| Open Questions | `plan.md` open items / TBDs | `spec.md` TBDs |

If a source file is missing, populate the section with `[TODO — source file not found]` and note which file was absent.

## Process

### Step 1: Locate Spec-Kit Artifacts

- Scan the current working directory (and one level up) for `spec.md`, `plan.md`, `requirements.md`.
- If multiple sets are found, present them to the user and ask which feature to publish.
- If none are found, ask the user to provide the path to the spec-kit project directory.
- Read all found files in full before proceeding.

### Step 2: Extract Feature Name

- Derive the feature name from the first heading in `spec.md` or `plan.md`.
- If no clear title is found, ask the user: "What should we call this feature on the Confluence page?"

### Step 3: Map Content to Page Sections

Using the artifact mapping above, populate each section of the design review template:

1. **Context & Problem** — Extract the "why" from `spec.md`: problem statement, background, motivation.
2. **Technical Proposal** — Extract the "what and how" from `plan.md`: proposed solution, key decisions, approach.
3. **Requirements** — Extract functional and non-functional requirements from `requirements.md`; supplement with any requirements listed in `spec.md`.
4. **Design Considerations** — Extract any alternatives, trade-offs, or design options noted in `plan.md`.
5. **Open Questions** — Collect unresolved items, TBDs, and questions from both `plan.md` and `spec.md`.

**Do not invent or fill in content** beyond what the source files contain. Use `[TODO]` clearly for missing sections and explain why (e.g., `[TODO — no alternatives section found in plan.md]`).

### Step 4: Check for Existing Confluence Page

- Search for an existing page with title matching `"Technical Plan: [feature-name]"` using `mcp__atlassian__confluence_search`.
- If the user provided a page ID, retrieve it directly with `mcp__atlassian__confluence_get_page`.
- If a match is found, confirm with the user: this will be an **update** run.
- If no match is found, this will be a **create** run.

### Step 5: Confirm with User

Before publishing, present a summary:

```
I've read the spec-kit artifacts and mapped them to a design review page.

Feature: [Feature Name]
Source files found:
  ✅ spec.md        (last modified: [date])
  ✅ plan.md        (last modified: [date])
  ✅ requirements.md (last modified: [date])

Page sections:
  ✅ Context & Problem    — from spec.md
  ✅ Technical Proposal   — from plan.md
  ✅ Requirements         — from requirements.md
  ⚠️  Design Considerations — [TODO: no alternatives section in plan.md]
  ✅ Open Questions       — from plan.md

Target Confluence location:
  - Action: [Create new page | Update existing page (ID: XXXXXXXXX)]
  - Space: [space key]
  - Parent page: [parent page title or ID]
  - Page title: "Technical Plan: [Feature Name]"

Shall I publish? (You can ask me to adjust any section first.)
```

### Step 6: Publish to Confluence

**Create (first run):**
- Use `mcp__atlassian__confluence_create_page` to create the page.
- Default placement: under the user's chosen parent page or space root.
- Set initial **Status** to `Draft`.
- Append the "source of truth" notice footer (from the template) directing reviewers to comment rather than edit.

**Update (re-run):**
- Retrieve existing page with `mcp__atlassian__confluence_get_page` to get current version.
- Use `mcp__atlassian__confluence_update_page` to replace content with the new version.
- Append a new row to the **Revision History** table with today's date, version bump, and a brief change summary.
- Do NOT change the Status unless user explicitly requests it.

### Step 7: Report and Remind

After successful publish:

```
✅ Design review page published:
https://your-org.atlassian.net/wiki/spaces/ENG/pages/XXXXXXXXX

Status: Draft
Next steps:
  1. Share the link with your team for review.
  2. Collect feedback as Confluence comments (not direct page edits).
  3. Take feedback → refine plan.md and requirements.md in spec-kit.
  4. Re-run /sdd-tech-plan-to-confluence to publish the updated version.
  5. Repeat until team reaches consensus and status is Approved (v1).

📌 Save your page ID for future re-runs: XXXXXXXXX
   You can pass it directly next time: /sdd-tech-plan-to-confluence [page-id]
```

## Operation Mode Detection

- **Creating new page**: User says "create", "publish", "share my plan", or provides no page ID.
- **Updating existing page**: User provides a numeric page ID, or says "update", "re-publish", "push updates".
- If ambiguous, ask: "Is this a first publish or an update to an existing page?"

## Status Field Progression

The **Status** field on the page progresses through:

```
Draft  →  Under Review  →  Approved (v1)
```

- **Draft**: Set automatically on first publish.
- **Under Review**: Update manually (or ask user) when team review begins.
- **Approved (v1)**: Update when team reaches consensus and plan is finalized.
  - After `Approved (v1)`, the plan is ready for `/confluence-tech-plan-to-jira-tickets`.

## Handling Missing Files

| Scenario | Behavior |
|---|---|
| `spec.md` missing | Context & Problem section → `[TODO — spec.md not found]`. Ask user if they want to provide a path. |
| `plan.md` missing | Technical Proposal + Design Considerations → `[TODO — plan.md not found]`. Warn: this is the primary source. |
| `requirements.md` missing | Requirements section → attempt to derive from `spec.md`; if insufficient → `[TODO — requirements.md not found]`. |
| All files missing | Stop. Ask user to provide the spec-kit project directory path. |

## Workflow Integration

This skill sits at the **Plan → Review** boundary in the spec-kit native workflow:

```
[spec-kit plan]
    plan.md + requirements.md  (local source of truth)
         │
         ▼
[sdd-tech-plan-to-confluence]  ← YOU ARE HERE
    Reads local files → Maps to design review page → Publishes to Confluence
         │
         ▼
[Team Review Loop]
    Team reviews Confluence → Comments → RD refines spec-kit files → /sdd-tech-plan-to-confluence again
         │
         ▼ (consensus reached)
[Plan Finalized — Approved (v1)]
         │
         ▼
[confluence-tech-plan-to-jira-tickets]
    Design review page → Jira root ticket + subtasks
```

## Workflow Example

**User**: "Publish my plan to Confluence for team review"

**Agent**:
1. Scans cwd, finds `spec.md`, `plan.md`, `requirements.md`.
2. Reads all three files.
3. Extracts feature name: "Notification Service Refactor".
4. Maps content: Context from `spec.md`, Proposal from `plan.md`, Requirements from `requirements.md`. Notes no alternatives section in `plan.md` (marks Design Considerations as TODO).
5. Searches Confluence for "Technical Plan: Notification Service Refactor" — no results.
6. Presents summary to user, confirms create.
7. Creates Confluence page titled "Technical Plan: Notification Service Refactor".
8. Reports:
   ```
   ✅ Design review page published:
   https://your-org.atlassian.net/wiki/spaces/ENG/pages/987654321

   Status: Draft

   📌 Save your page ID: 987654321
      Next time you can run: /sdd-tech-plan-to-confluence 987654321
   ```

**Later — After team feedback:**

**User**: "/sdd-tech-plan-to-confluence 987654321"

**Agent**:
1. Reads updated `plan.md` (RD has incorporated team feedback).
2. Retrieves existing page 987654321.
3. Re-maps content with new material.
4. Updates page, appends Revision History row: `v2 | 2026-03-03 | [author] | Incorporated team feedback on retry strategy`.
5. Reports updated URL.

## Tips for the Agent

- **Never invent content**: If a section cannot be populated from the source files, use `[TODO]` with an explanation. This preserves trust in the page as a direct reflection of local files.
- **Source of truth notice is mandatory**: Always include the footer notice from the template. This prevents team members from editing the Confluence page directly.
- **Page ID reminder**: Always remind the user to save the page ID on first publish. Re-runs without a page ID will create duplicates.
- **Revision history matters**: On updates, always append to the revision history table so reviewers can track what changed between versions.
- **Don't change the status silently**: Only update the Status field if the user explicitly requests it.
- **Link back to source**: In the page footer or metadata, note which spec-kit directory the content came from (if available) so the team knows where the local files live.
