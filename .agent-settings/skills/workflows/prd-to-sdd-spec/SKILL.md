---
name: prd-to-sdd-spec
description: Fetches an external PRD from Confluence or from a Jira ticket that links to a PRD wiki, and transforms it into a structured local source file that the RD can reference when running SDD tools like spec-kit specify or openspec. Bridges the PO handoff into the SDD workflow.
---

# PRD to SDD Spec

## Install this skill globally

Install once — available in all projects.

```bash
# Claude
mkdir -p ~/.claude/skills/prd-to-sdd-spec
cp <agent-settings-repo>/.agent-settings/skills/workflows/prd-to-sdd-spec/SKILL.md \
   ~/.claude/skills/prd-to-sdd-spec/SKILL.md
# Add to ~/.claude/CLAUDE.md: - **prd-to-sdd-spec** (`~/.claude/skills/prd-to-sdd-spec/SKILL.md`)

# Copilot
mkdir -p ~/.copilot/skills/prd-to-sdd-spec
cp <agent-settings-repo>/.agent-settings/skills/workflows/prd-to-sdd-spec/SKILL.md \
   ~/.copilot/skills/prd-to-sdd-spec/SKILL.md

# Gemini
mkdir -p ~/.gemini/skills/prd-to-sdd-spec
cp <agent-settings-repo>/.agent-settings/skills/workflows/prd-to-sdd-spec/SKILL.md \
   ~/.gemini/skills/prd-to-sdd-spec/SKILL.md
```


This skill bridges the **PO handoff** and the **Specify** phase of the SDD workflow. When a PO/PM writes a PRD in Confluence, or when a Jira ticket links to a PRD wiki, this skill fetches it and transforms it into a clean local source file that serves as the RD's input when running SDD tools like `spec-kit specify` or `openspec`.

**Key principle:** The Confluence PRD is written by the PO — the RD should not have to copy-paste it manually. This skill pulls it down, restructures it into a spec-kit-friendly format, and saves it locally so the RD can immediately run `spec-kit specify` with full context.

## Workflow Position

```
[PO / PM]
    Writes PRD in Confluence
         │
         ▼
[prd-to-sdd-spec]  ← YOU ARE HERE
    Fetch PRD from Confluence or Jira
    → Transform to SDD source format
    → Save as local prd-source.md
         │
         ▼
[RD runs SDD tool]
    Uses prd-source.md as context
    → AI-assisted discussion with RD
    → spec.md (local source of truth)
         │
         ▼
[SDD plan]
    → plan.md + requirements.md
         │
         ▼
[/tech-plan-to-wiki]
    → Design review page in Confluence
```

## Prerequisites

**IMPORTANT**: This skill requires the **Atlassian MCP Server** to be installed and configured.

Before using this skill, ensure:
1. ✅ Atlassian MCP server is installed (see the `install-atlassian-mcp` skill)
2. ✅ Credentials are configured in `~/.env.mcp-atlassian`
3. ✅ The following MCP tools are available:
   - `mcp__atlassian__confluence_get_page`
   - `mcp__atlassian__confluence_search`
   - `mcp__atlassian__jira_get_issue` (to fetch Jira ticket details and links)

## Process

### Step 1: Locate the PRD Source

- The user provides either:
  - A Confluence page ID or search hint (title/keywords) for the PRD.
  - A Jira ticket key (e.g., "PROJ-123") that links to the PRD wiki.
- **If Confluence input**: If a search hint is provided, use `mcp__atlassian__confluence_search` to find matching pages and let the user select. Fetch the full PRD content using `mcp__atlassian__confluence_get_page`.
- **If Jira input**: Use `mcp__atlassian__jira_get_issue` to fetch the ticket details. Look for remote issue links or description links to Confluence PRD pages. If multiple links, let the user select. Then fetch the PRD content from the selected Confluence page.

### Step 2: Transform to SDD Source Format

Parse and restructure the PRD content into a clean markdown file organized for the SDD `specify` phase. The output must be **faithful to the PRD** — do not add, infer, or editorialize. Gaps in the PRD should appear as explicit `[TBD]` markers so the RD can address them during the SDD specify phase.

Target structure for `prd-source.md`:

```markdown
# [Feature Name] — PRD Source

> Imported from Confluence: "[PRD Page Title]" (ID: XXXXXXXXX)
> Last fetched: [date]
> Author: [PO/PM name from page metadata if available]

## Problem Statement
[From PRD: the problem being solved]

## Goals
[From PRD: success criteria, objectives]

## Non-Goals / Out of Scope
[From PRD: explicit exclusions]

## User Stories / Use Cases
[From PRD: who does what and why]

## Functional Requirements
[From PRD: what the system must do]

## Non-Functional Requirements
[From PRD: performance, security, scale, compliance]

## Constraints
[From PRD: tech stack, timeline, dependencies, compliance]

## Open Questions (from PO)
[TBDs and unresolved items in the original PRD]
```

**Transformation rules:**
- Map PRD sections to the structure above by content, not by exact heading names (PRDs vary in structure)
- If a PRD section has no clear match, place it under the closest category or add it as a new section at the bottom
- If a target section has no corresponding PRD content, write `[TBD — not specified in PRD]`
- Do not generate or infer requirements that are not in the PRD

### Step 3: Confirm Output Location

Ask the user where to save the file:
- Ask: `"Save path? Type a path or type n to use the default: ./prd-source.md"`
- Treat `n`, `default`, or blank-like responses as "use default"

### Step 4: Write the Local File

Write `prd-source.md` to the confirmed path.

### Step 5: Report and Hand Off

```
✅ PRD imported and transformed:

Source:  "[PRD Page Title]" (Confluence ID: XXXXXXXXX)
Output:  ./prd-source.md

Sections mapped:
  ✅ Problem Statement
  ✅ Goals
  ✅ Non-Goals
  ✅ User Stories
  ✅ Functional Requirements
  ⚠️  Non-Functional Requirements  — [TBD: not specified in PRD]
  ✅ Constraints
  ✅ Open Questions

Next step:
  Run your SDD tool (e.g., spec-kit specify or openspec) and reference prd-source.md as your input context.
  The AI discussion will help you clarify TBDs and produce spec.md.
```

## Tips for the Agent

- **Faithful import only**: Do not add technical opinions, architecture suggestions, or implementation details. The RD adds those during the SDD specify phase.
- **Surface TBDs clearly**: Any gap in the PRD should become a visible `[TBD]` in the output — these become discussion points in the specify phase.
- **Preserve PO intent**: Keep the language and framing from the PRD. Do not rewrite requirements in technical terms.
- **Re-runs are safe**: If the PO updates the Confluence PRD, the RD can re-run this skill to get a fresh `prd-source.md`. Remind the user to check git diff to see what changed before re-running the SDD tool.
- **Jira Integration**: When starting from a Jira ticket, ensure the ticket has clear links to the PRD wiki. If multiple links exist, present options to the user for selection.
- **Jira Integration**: When starting from a Jira ticket, ensure the ticket has clear links to the PRD wiki. If multiple links exist, present options to the user for selection.

## Workflow Example

### Example 1: From Confluence PRD

**User**: "Import the PRD for the notification refactor from Confluence"

**Agent**:
1. Searches Confluence for "notification refactor PRD".
2. Presents 2 matching pages, user selects the correct one.
3. Fetches page content.
4. Maps PRD sections to `prd-source.md` structure. Notes that NFRs are not specified → marks as `[TBD]`.
5. Confirms output path: `./prd-source.md`.
6. Writes file.
7. Reports:
   ```
   ✅ PRD imported and transformed:

   Source:  "Notification System Refactor — PRD" (Confluence ID: 123456789)
   Output:  ./prd-source.md

   ⚠️  Non-Functional Requirements — [TBD: not specified in PRD]
   ⚠️  Constraints                 — [TBD: not specified in PRD]

   Next step:
     Run your SDD tool (e.g., spec-kit specify)
     Reference prd-source.md for context. The 2 TBD sections are
     good discussion topics for the specify session with the PO.
   ```

### Example 2: From Jira Ticket Linking to PRD

**User**: "Import PRD from Jira ticket PROJ-456"

**Agent**:
1. Fetches Jira ticket PROJ-456 using `mcp__atlassian__jira_get_issue`.
2. Finds remote links to Confluence pages. Presents 1 matching PRD page, user confirms.
3. Fetches PRD content from Confluence.
4. Maps PRD sections to `prd-source.md` structure.
5. Confirms output path: `./prd-source.md`.
6. Writes file.
7. Reports:
   ```
   ✅ PRD imported and transformed:

   Source:  "User Profile Enhancement — PRD" (Confluence ID: 987654321)
   Via Jira: PROJ-456
   Output:  ./prd-source.md

   All sections mapped successfully.

   Next step:
     Run your SDD tool (e.g., openspec)
     Reference prd-source.md for context.
   ```
