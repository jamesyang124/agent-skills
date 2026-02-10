---
name: spec-to-tech-design
description: Reads a feature specification from Confluence and generates a Technical Design Document (TDD), publishing it back to Confluence. Use this at the Specify→Plan transition in the SDD workflow to produce a structured tech design before breaking work into tasks.
---

# Spec to Tech Design Document

This skill bridges the **Specify** and **Plan** phases of the SDD workflow. Given a feature specification in Confluence, it analyzes the requirements and generates a comprehensive Technical Design Document (TDD), then creates or updates a linked Confluence page.

## Tech Design Template (MANDATORY)

All generated TDDs **must follow** the template at:
`references/tech-design-template.md` (relative to this skill folder: `.agent-settings/skills/spec-to-tech-design`)

Use the template as the structural skeleton. Populate each section based on the specification content and codebase context. Omit sections that are genuinely not applicable, but always include: Overview, Goals & Non-Goals, Architecture Design, and Implementation Plan.

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

## Process

### Step 1: Locate the Specification

- The user provides a Confluence page ID or a search hint (title/keywords).
- If a search hint is provided, use `mcp__atlassian__confluence_search` to find matching pages and let the user select.
- Fetch the spec content using `mcp__atlassian__confluence_get_page`.

### Step 2: Analyze the Specification

Read the spec page and extract:

- **Feature purpose and goals** — what problem does it solve?
- **Functional requirements** — what must the system do?
- **Non-functional requirements** — performance, security, scale
- **Affected components** — which existing services, modules, or APIs are involved?
- **Constraints** — deadlines, tech stack limitations, compliance requirements

If the codebase is accessible, also inspect relevant source files to understand existing architecture and patterns before designing the solution.

### Step 3: Generate the Technical Design Document

Using `references/tech-design-template.md` as the structure, populate:

1. **Overview** — One-paragraph summary of the solution
2. **Problem Statement** — Restate the problem from the spec's perspective
3. **Goals & Non-Goals** — Derived from spec requirements; be explicit about scope boundaries
4. **Architecture Design** — How this fits the existing system; ASCII diagram if helpful
5. **Component Design** — Key new or modified components with responsibilities and interfaces
6. **Data Models & Schemas** — New tables, fields, or schema changes
7. **API Contracts** — New or modified endpoints with request/response shapes
8. **Dependencies & Integrations** — New libraries or external services required
9. **Security Considerations** — Auth, validation, sensitive data
10. **Performance Considerations** — Caching, scale, bottlenecks
11. **Testing Strategy** — Unit, integration, E2E coverage plan
12. **Implementation Plan** — Phased breakdown that will feed directly into Jira tickets
13. **Open Questions & Risks** — Anything unresolved that needs team input

### Step 4: Confirm with the User

Before publishing, present a summary of the proposed TDD to the user:

```
I've analyzed the spec "[Spec Page Title]" and drafted a Technical Design Document.

Summary:
- Architecture: [brief description]
- Key components: [list]
- Estimated phases: [N]
- Open questions: [N]

Target Confluence location:
- Space: [space key]
- Parent page: [parent page title or ID]
- Page title: "TDD: [Feature Name]"

Shall I create this page? (You can also ask me to adjust any section first.)
```

### Step 5: Publish to Confluence

- If a TDD page already exists for this feature (detected via search), **update** it using `mcp__atlassian__confluence_update_page`.
- Otherwise, **create** a new page using `mcp__atlassian__confluence_create_page`.
  - Default placement: as a child of the spec page, or in the same space under a "Tech Design" parent if one exists.
- Add a back-link comment or label on the original spec page pointing to the new TDD (using `mcp__atlassian__confluence_add_comment` or page labels).

### Step 6: Confirm and Report

Provide the user with:
- Link to the created/updated TDD page
- A note that the TDD is now ready to drive the Plan phase and feed `/confluence-to-jira-tickets`

## Analysis Guidelines

### Deriving Architecture from a Spec
- Look for listed requirements, user stories, and acceptance criteria.
- Identify nouns as data entities, verbs as operations/endpoints.
- Map to existing services or modules where possible; propose new ones only if necessary.

### Implementation Plan Phases
- Each phase should be independently deployable or testable where possible.
- Phase granularity should match Jira epic/story/task breakdown — this feeds directly into `/confluence-to-jira-tickets`.
- Flag dependencies between phases.

### When Spec Is Incomplete
- If required sections cannot be filled due to missing information, list them explicitly in **Open Questions & Risks**.
- Ask the user for clarification before publishing if blockers are critical.

## Workflow Integration

This skill sits at the **Specify → Plan** boundary:

```
[Specify]
    Confluence Spec Page
         │
         ▼
[spec-to-tech-design]  ← YOU ARE HERE
    Reads spec → Generates TDD → Publishes to Confluence
         │
         ▼
[Plan]
    TDD in Confluence
         │
         ▼
[confluence-to-jira-tickets]
    TDD → Jira Tickets
```

## Workflow Example

**User**: "Generate a tech design from the spec page 'Payment Gateway Integration v2'"

**Agent**:
1. Searches Confluence for "Payment Gateway Integration v2".
2. Retrieves page content.
3. Analyzes requirements: Stripe integration, webhook handling, idempotency, PCI compliance.
4. Inspects existing `src/payments/` code for current architecture context.
5. Presents TDD summary to user for confirmation.
6. Creates Confluence page "TDD: Payment Gateway Integration v2" as a child of the spec page.
7. Reports:
   ```
   ✅ Tech Design Document created:
   https://your-org.atlassian.net/wiki/spaces/ENG/pages/987654321

   The TDD covers:
   • Architecture: Event-driven webhook processor with idempotency layer
   • 3 new components: PaymentService, WebhookProcessor, IdempotencyStore
   • 2 new DB tables: payment_events, idempotency_keys
   • Implementation plan: 3 phases

   Ready to proceed to Plan phase. Use /confluence-to-jira-tickets with this page to create Jira tickets.
   ```

## Tips for the Agent

- **Link both ways**: The TDD should reference the spec page, and the spec page should mention/link to the TDD.
- **Be opinionated but flagged**: Make concrete design decisions, but mark anything uncertain as an open question.
- **Implementation Plan drives tickets**: Make the phases in Section 12 detailed enough to directly become Jira stories via `/confluence-to-jira-tickets`.
- **Reuse existing patterns**: Check the constitution/codebase before proposing new patterns or libraries.
