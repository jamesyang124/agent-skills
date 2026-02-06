---
name: confluence-to-jira-tickets
description: Analyzes a Confluence page and automatically creates a Jira root ticket with associated subtasks.
---

# Confluence to Jira Tickets

This skill automates the process of turning documentation (like PRDs, tech specs, or meeting notes) into actionable Jira tickets. It fetches a Confluence page, analyzes its content to identify key tasks, and creates a parent ticket with multiple subtasks.

## Jira Ticket Template (MANDATORY)

All generated Jira ticket descriptions **must be based on** the template at:
`references/jira-ticket-template.md` (relative to this skill folder: `.agent-settings/skills/confluence-to-jira-tickets`).

Use the template as a structural guide. Populate the sections based on the analysis of the Confluence page. If a section is not applicable, you may omit it, but keep the core structure (Summary, Context, Requirements).

## Prerequisites

**IMPORTANT**: This skill requires the **Atlassian MCP Server** to be installed and configured.

Before using this skill, ensure:
1. ✅ Atlassian MCP server is installed (see `.agent-settings/mcps/install-atlassian-mcp.sh`)
2. ✅ Jira and Confluence credentials are configured in `.env.mcp-atlassian`
3. ✅ The following MCP tools are available:
   - `mcp__atlassian__confluence_get_page`
   - `mcp__atlassian__confluence_search`
   - `mcp__atlassian__jira_create_issue`
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

3.  **Configure Jira Settings (Interactive)**:
    - **Brackets**: Present suggested `[TOPIC]` and `[SERVICE/COMPONENT]` values. Ask the user to confirm or provide new ones.
    - **Owner**: Ask the user for the **Assignee** email or name for the tickets.
    - **Project/Type**: Use your default **Jira Project Key** (e.g., **PROJECT**) and **Story** as the default **Issue Type** for the root ticket. Allow the user to override.

4.  **Create Tickets**:
    - **Step 1: Create Root Ticket**: Use `mcp__atlassian__jira_create_issue`.
    - **Step 2: Create Subtasks**: Use `mcp__atlassian__jira_create_issue` for each identified task, passing the root ticket's key/ID as the `parent`.

5.  **Confirm and Link**:
    - Provide the user with links to the created Jira tickets.
    - (Optional) Add a comment to the Confluence page with the Jira ticket links using `mcp__atlassian__confluence_add_comment`.

## Analysis Guidelines

When analyzing the Confluence page:

### Identifying the Root Ticket
- Look for the page title, "Overview", or "Objective" sections.
- The summary should be concise but descriptive.
- Use the page content to populate the Jira description (summarized).

### Identifying Subtasks
- Look for tables, bulleted lists, "Requirements", "Tasks", or "Checklist" sections.
- Each subtask should have a clear, actionable summary.
- If the page contains a "Technical Design" or "Implementation Plan", extract steps as subtasks.
- Ensure each subtask is distinct and not redundant.

### Mapping to Jira Fields
- **Summary**: **MANDATORY**: Follow the pattern `[TOPIC][SERVICE/COMPONENT] Description`.
  - All text within brackets MUST be UPPERCASE (e.g., `[PROJECT][MODULE]`, `[FEATURE][SERVICE]`).
  - The `TOPIC` refers to the main title or key topic of the documentation (e.g., `MARKETPLACE`, `AUTHENTICATION`).
  - The `SERVICE/COMPONENT` refers to the specific system or module (e.g., `API`, `WEB_UI`, `DATABASE`).
  - The `Description` must start with an uppercase letter.
  - Example: `[MARKETPLACE][API] Implement robust search filtering for product listings`.
- **Description**: **MANDATORY**: Use the structure defined in `references/jira-ticket-template.md`. Include context from the Confluence page, link back to the source, and list clear acceptance criteria.
- **Project**: Use the provided Project Key.
- **IssueType**: Use "Sub-task" for child issues.
- **Parent**: The key of the root ticket.
- **Assignee**: Use the user-provided identifier.

## Workflow Example

**User**: "Create Jira tickets from this Confluence page: 'Service Feature Spec - User Profiles'"

**Agent**:
1. Uses `mcp__atlassian__confluence_search` to find the page.
2. Retrieves page content.
3. Analyzes content and presents a proposal:
   ```
   Based on the spec, I propose:
   - Root Ticket: Implement User Profile Management
   - Subtasks: ...
   
   I've suggested the following brackets:
   - [TOPIC]: USER_PROFILES
   - [SERVICE/COMPONENT]: CORE_SERVICE
   
   Settings:
   - Project: PROJECT (default)
   - Root Issue Type: Story (default)
   
   Would you like to change any of these values or set an owner (assignee)?
   ```
4. User responds: "Use [TOPIC] PROFILE and set assignee to user@example.com"
5. Agent creates the root ticket and subtasks with the updated values.
6. Agent provides the URLs for all created tickets.

## Tips for the Agent

- **Batch Creation**: If many subtasks are identified, inform the user you are creating them in sequence.
- **Validation**: If the Confluence page is empty or doesn't contain actionable items, ask the user for clarification.
- **Project Selection**: Use the configured default project key but allow the user to override. You can use `mcp__atlassian__jira_get_all_projects` to show a list of available projects if they wish to change.
- **Mapping Custom Fields**: If the project requires specific custom fields, use `mcp__atlassian__jira_search_fields` to identify them.
