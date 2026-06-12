---
name: tech-plan-to-ticket
description: Fetches a Confluence design review or tech spec page and creates a Jira root ticket with associated subtasks, or adds subtasks to an existing Jira ticket. Use when turning a Confluence page into Jira tickets, creating tasks from a tech plan, breaking down a design review into Jira issues, or at the Tasks phase of the SDD workflow.
---

# Confluence to Jira Tickets

## Install this skill globally

Install once — available in all projects.

```bash
# Claude
mkdir -p ~/.claude/skills/tech-plan-to-ticket
cp <agent-settings-repo>/.agent-settings/skills/workflows/tech-plan-to-ticket/SKILL.md \
   ~/.claude/skills/tech-plan-to-ticket/SKILL.md
# Add to ~/.claude/CLAUDE.md: - **tech-plan-to-ticket** (`~/.claude/skills/tech-plan-to-ticket/SKILL.md`)

# Copilot
mkdir -p ~/.copilot/skills/tech-plan-to-ticket
cp <agent-settings-repo>/.agent-settings/skills/workflows/tech-plan-to-ticket/SKILL.md \
   ~/.copilot/skills/tech-plan-to-ticket/SKILL.md

# Gemini
mkdir -p ~/.gemini/skills/tech-plan-to-ticket
cp <agent-settings-repo>/.agent-settings/skills/workflows/tech-plan-to-ticket/SKILL.md \
   ~/.gemini/skills/tech-plan-to-ticket/SKILL.md
```


This skill automates the process of turning documentation (like PRDs, tech specs, or meeting notes) into actionable Jira tickets. It fetches a Confluence page, analyzes its content to identify key tasks, and either creates a new parent ticket with multiple subtasks or adds subtasks to an existing Jira ticket as the base.

## Jira Ticket Template (MANDATORY)

All generated Jira ticket descriptions **must be based on** the template at:
`references/jira-ticket-template.md` (relative to this skill folder: `.agent-settings/skills/tech-plan-to-ticket`).

Use the template as a structural guide. Populate the sections based on the analysis of the Confluence page. If a section is not applicable, you may omit it, but keep the core structure (Summary, Context, Requirements).

## Prerequisites

**IMPORTANT**: This skill requires the **Atlassian MCP Server** to be installed and configured.

Before using this skill, ensure:
1. ✅ Atlassian MCP server is installed (see the `install-atlassian-mcp` skill)
2. ✅ Jira and Confluence credentials are configured in `~/.env.mcp-atlassian`
3. ✅ The following MCP tools are available:
   - `mcp__atlassian__confluence_get_page`
   - `mcp__atlassian__confluence_search`
   - `mcp__atlassian__jira_create_issue`
   - `mcp__atlassian__jira_add_comment`
   - `mcp__atlassian__jira_get_all_projects`
   - `mcp__atlassian__jira_search_fields` (optional, for finding custom fields)

## Process

1.  **Identify the Confluence Page**:
    - The user provides a page ID or a search hint (title/keywords).
    - If a search hint is provided, use `mcp__atlassian__confluence_search` to find matching pages and let the user select.
    - Fetch the page content using `mcp__atlassian__confluence_get_page`.

2.  **Analyze Content**:
    - Analyze the retrieved content (Markdown/HTML) to identify:
        - **Project Context**: Determine which Jira project this belongs to.
        - **Root Ticket**: A high-level summary of the overall goal (e.g., "Implement Feature X").
        - **Subtasks**: Granular, actionable tasks derived from requirements, checklists, or technical details in the page.
    - Suggest **TOPIC** and **SERVICE/COMPONENT** based on the page content.
    - Propose a list of tickets to the user before creating them.

3.  **Choose Base Ticket Mode**:
    - Ask the user whether to create a new root ticket or use an existing Jira ticket as the base.
    - If using an existing ticket, ask for the Jira issue key (e.g., "PROJ-123").
    - For existing tickets, the plan and description from the Confluence page will be added as a comment to the ticket, without overwriting the original description.

4.  **Configure Jira Settings (Interactive)**:
    - **Brackets**: Present suggested `[TOPIC]` and `[SERVICE/COMPONENT]` values. Ask the user to confirm or provide new ones. (Applies to new root ticket and subtasks.)
    - **Owner**: Ask the user for the **Assignee** email or name for the tickets.
    - **Project/Type**: Use **EXAMPLE** as the default **Jira Project Key** and **Story** as the default **Issue Type** for the root ticket (if creating new). Allow the user to override.

5.  **Create Tickets**:
    - **If New Root Ticket**: Use `mcp__atlassian__jira_create_issue` to create the root ticket.
    - **If Existing Base Ticket**: Use `mcp__atlassian__jira_add_comment` to add the plan and description as a comment to the existing ticket.
    - **Create Subtasks**: Use `mcp__atlassian__jira_create_issue` for each identified task, passing the root ticket's key/ID as the `parent` (whether new or existing).

6.  **Confirm and Link**:
    - Provide the user with links to the created Jira tickets.
    - (Optional) Add a comment to the Confluence page with the Jira ticket links using `mcp__atlassian__confluence_add_comment`.

## Analysis Guidelines

When analyzing the Confluence page:

### Identifying the Root Ticket
- Look for the page title, "Overview", or "Objective" sections.
- The summary should be concise but descriptive.
- If creating a new root ticket, use the page content to populate the Jira description (summarized). If using an existing ticket as base, the description will be added as a comment instead.

### Identifying Subtasks
- Look for tables, bulleted lists, "Requirements", "Tasks", or "Checklist" sections.
- Each subtask should have a clear, actionable summary.
- If the page contains a "Technical Design" or "Implementation Plan", extract steps as subtasks.
- Ensure each subtask is distinct and not redundant.

### Mapping to Jira Fields
- **For New Root Ticket**:
  - **Summary**: **MANDATORY**: Follow the pattern `[TOPIC][SERVICE/COMPONENT] Description`.
    - All text within brackets MUST be UPPERCASE (e.g., `[PROJECT][BACKEND]`, `[FEATURE][API]`).
    - The `TOPIC` refers to the main title or key topic of the documentation (e.g., `PROJECT`, `FEATURE`).
    - The `SERVICE/COMPONENT` refers to the specific system or module (e.g., `API`, `FRONTEND`, `DATABASE`).
    - The `Description` must start with an uppercase letter.
    - Example: `[PROJECT][BACKEND] Dynamic URL Domain Migration - Versioned Content URLs`.
  - **Description**: **MANDATORY**: Use the structure defined in `references/jira-ticket-template.md`. Include context from the Confluence page, link back to the source, and list clear acceptance criteria.
- **For Existing Base Ticket**: Do not modify the summary or description. Add the plan and description as a comment using `mcp__atlassian__jira_add_comment`.
- **For Subtasks** (always created):
  - **Summary**: Follow the same pattern as root ticket: `[TOPIC][SERVICE/COMPONENT] Description`.
  - **Description**: Use the structure from the template, tailored to the subtask.
  - **Project**: Use the provided Project Key (must match the root ticket's project).
  - **IssueType**: Use "Sub-task" for child issues.
  - **Parent**: The key of the root ticket (new or existing).
  - **Assignee**: Use the user-provided identifier.

## Workflow Example

### Example 1: Creating New Root Ticket

**User**: "Create Jira tickets from this Confluence page: 'CMS Feature Spec - User Profiles'"

**Agent**:
1. Uses `mcp__atlassian__confluence_search` to find the page.
2. Retrieves page content.
3. Analyzes content and presents a proposal:
   ```
   Based on the spec, I propose:
   - Root Ticket: Implement CMS User Profile Management
   - Subtasks: ...
   
   I've suggested the following brackets:
   - [TOPIC]: USER_PROFILES
   - [SERVICE/COMPONENT]: CMS
   
   Settings:
   - Project: EXAMPLE (default)
   - Root Issue Type: Story (default)

   Would you like to create a new root ticket or use an existing Jira ticket as the base? (Type 'new' or provide the issue key, e.g., 'PROJ-123')
   ```
4. User responds: "new"
5. Agent asks for confirmation on brackets, assignee, etc.
6. Agent creates the root ticket and subtasks.
7. Agent provides the URLs for all created tickets.

### Example 2: Using Existing Jira Ticket as Base

**User**: "Add subtasks from this Confluence page to existing ticket PROJ-456"

**Agent**:
1. Uses `mcp__atlassian__confluence_search` to find the page.
2. Retrieves page content.
3. Analyzes content and presents a proposal:
   ```
   Based on the spec, I propose adding subtasks to PROJ-456:
   - Subtasks: ...
   
   I've suggested the following brackets:
   - [TOPIC]: USER_PROFILES
   - [SERVICE/COMPONENT]: CMS

   The plan and description will be added as a comment to PROJ-456 without overwriting its description.

   Confirm assignee and proceed? (Type y or provide assignee)
   ```
4. User confirms.
5. Agent adds a comment to PROJ-456 with the plan/description.
6. Agent creates subtasks under PROJ-456.
7. Agent provides the URLs for the subtasks.

## Tips for the Agent

- **Batch Creation**: If many subtasks are identified, inform the user you are creating them in sequence.
- **Validation**: If the Confluence page is empty or doesn't contain actionable items, ask the user for clarification.
- **Project Selection**: Default to **EXAMPLE** but allow the user to override. You can use `mcp__atlassian__jira_get_all_projects` to show a list of available projects if they wish to change. Ensure the project matches for existing base tickets.
- **Mapping Custom Fields**: If the project requires specific custom fields, use `mcp__atlassian__jira_search_fields` to identify them.
- **Existing Ticket Mode**: When using an existing ticket, verify the issue key exists and belongs to the correct project. Do not overwrite the ticket's description; always use comments for additional information.
