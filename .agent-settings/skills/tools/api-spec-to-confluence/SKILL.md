---
name: api-spec-to-confluence
description: Creates or updates a Confluence API documentation page from code or an OpenAPI/Swagger spec. Supports Go (Gin, Echo, Chi), Ruby on Rails, Node.js (Express, Fastify), Python (FastAPI, Flask), and direct swagger.json/openapi.yaml input. Use when documenting an API endpoint, publishing API specs to Confluence, updating API docs, or at the Implement & PR phase of the SDD workflow.
allowed-tools: Read, Glob, Grep
---

# API Spec to Confluence

This skill automates the creation or update of a Confluence page for a specific API endpoint. It supports multiple input sources — framework code analysis or a direct OpenAPI/Swagger spec file — and adapts its analysis strategy to the project's framework as detected from `project-config.md`.

## Documentation Template (MANDATORY)

All generated API documents **must be based on** the template at:
`references/documentation-template.md` (relative to this skill folder: `.agent-settings/skills/api-spec-to-confluence`).

Use the template as a structural guide, but do not copy its placeholder text or descriptions verbatim.
Keep the section order, and replace all template placeholders with endpoint-specific content.

## Prerequisites

**IMPORTANT**: This skill requires the **Atlassian MCP Server** to be installed and configured.

Before using this skill, ensure:
1. ✅ Atlassian MCP server is installed (see `.agent-settings/mcps/install-atlassian-mcp.sh`)
2. ✅ Confluence credentials are configured in `.env.mcp-atlassian`
3. ✅ The following MCP tools are available:
   - `mcp__atlassian__confluence_create_page`
   - `mcp__atlassian__confluence_update_page`
   - `mcp__atlassian__confluence_search`
   - `mcp__atlassian__confluence_get_page`

If the MCP server is not configured, guide the user to run:
```bash
.agent-settings/mcps/install-atlassian-mcp.sh
```

## Process

0.  **Load project configuration**: Read `.agent-settings/project-config.md`.
    - If the file is missing: tell the user to run the `setup-project-config` skill first (`"set up project config"`), then stop.
    - Use all values from the config throughout this skill — Confluence space, parent pages, code structure paths, framework details, and documentation format. Do not rely on hardcoded values.

1.  **Identify the API endpoint**: The user must provide either:
    - An API path (e.g., `/api/v1/users/me`), OR
    - A path to an OpenAPI/Swagger spec file (e.g., `swagger.json`, `openapi.yaml`, `docs/swagger.yaml`)
2.  **Choose Operation Mode**: Ask the user if they want to:
    - **Create a new page**: Generate a new Confluence page
    - **Update an existing page**: Update an existing page by providing a page ID or search hint
3.  **Get Target Page**:
    - **For new pages**: Present the list of common parent pages loaded from `.agent-settings/project-config.md` as a numbered list. The user can also enter a different page ID.
    - **For existing pages**:
      - If user provides a page ID (numeric), use it directly
      - If user provides a search hint (title/keywords), use `mcp__atlassian__confluence_search` to find matching pages and let user select
      - Retrieve the current page using `mcp__atlassian__confluence_get_page` to preserve the title
4.  **Detect API Source and Analyze**:
    - **If the user provided a Swagger/OpenAPI spec file**: Read `.agent-settings/skills/tools/api-spec-to-confluence/references/openapi-parsing.md` for parsing instructions. Skip code analysis.
    - **If the user provided an API path**: Read `.agent-settings/skills/tools/api-spec-to-confluence/references/framework-patterns.md` and apply the section matching the framework from `project-config.md`.
    - **If `project-config.md` is missing**: Tell the user to run `setup-project-config` first, then stop.
    - **If no framework is detected in config**: Read `.agent-settings/skills/tools/api-spec-to-confluence/references/framework-patterns.md` → Auto-Detection section, then confirm with user.
5.  **Generate Comprehensive Documentation** based on the template in
    `references/documentation-template.md` and populating its sections:
    - **HTTP Method and Path**: From the router definition
    - **Summary and Description**: From swagger `@Summary` and `@Description` annotations
    - **Authentication**: Identify middleware (e.g., `JWTMiddleware`, `AdminMiddleware`)
    - **Request Parameters**: Extract from `@Param` annotations and analyze context binding code
    - **Request Body**: From `@Accept` and DTO struct analysis (if applicable)
    - **Response**: From `@Success` and `@Failure` annotations, analyze response DTO structures
    - **Response Examples** (**REQUIRED**): Provide JSON response examples for all success and error cases
    - **Implementation Details**: Key business logic, external service calls, database operations
    - **Error Handling**: Common error scenarios and status codes
    - **Dependencies**: Services, clients, or repositories used
5.  **Create or Update Confluence Page**:
    - **For new pages**: Use `mcp__atlassian__confluence_create_page` to create a new page under the specified parent. Title format: `API Spec: {path}` (e.g., "API Spec: /api/example-service/v1/users/me").
    - **For existing pages**: Use `mcp__atlassian__confluence_update_page` to update the content while preserving the existing title (unless user wants to change it).

## Tips for the Agent

### Prerequisites Check
- **ALWAYS check first**: Verify that Atlassian MCP tools are available before proceeding
- If MCP tools are NOT available, inform the user and guide them to install:
  ```
  The Atlassian MCP server is required for this skill. Please run:
  .agent-settings/mcps/install-atlassian-mcp.sh
  ```
- Do NOT attempt to use this skill without the required MCP tools

### Operation Mode Detection
- **Creating new page**: User says "create", "new page", or specifies a parent page
- **Updating existing page**: User says "update", provides a page ID (numeric), or provides a search hint (page title/keywords)
- If ambiguous, ask the user to clarify

### Page ID vs Search Hint
- **Page ID**: A numeric value (e.g., "4152098820" or just "4152098820")
- **Search Hint**: Text keywords (e.g., "upload API spec", "product upload")
- If user provides numeric value, treat it as page ID and use directly
- If user provides text, search for matching pages using `mcp__atlassian__confluence_search`

### Code Analysis
- Use the router file, handler/controller directory, DTO/model directory, and service directory from project config
- Use `Grep` to quickly find the API path in the router/routes file
- Read the full handler/action/view function to understand the complete workflow
- Check for DTO/model/schema definitions referenced in the handler (in the model/DTO directory from config)
- **CRITICAL**: Search for the response call patterns for the detected framework (see `.agent-settings/skills/tools/api-spec-to-confluence/references/framework-patterns.md`) to understand response formats
- Read response DTO/model/schema files to generate accurate JSON examples (this is mandatory)
- Identify service layer calls for implementation context
- Use clear markdown formatting for readability
- **CRITICAL**: All JSON payloads, response examples, and request bodies MUST be wrapped in markdown code blocks.
- **CRITICAL**: All request parameters (path, query, header) and DTO/model fields MUST be listed using tables (preferred) or unordered lists. Do not use plain text paragraphs for these.

### Update Strategy
- When updating, retrieve the existing page first to preserve the title
- Add a "Last Updated" timestamp in the Change Log section
- Increment the version number in the Change Log
- Preserve any manual edits in sections not managed by this skill (if user requests)

## Common Parent Pages

Loaded from `.agent-settings/project-config.md` — the `### Common Parent Pages` table under `## Confluence`.
Present them as a numbered list when asking the user where to create a new page.
For page search/selection details and workflow decision tree, see `.agent-settings/skills/tools/api-spec-to-confluence/references/usage-examples.md`.

## Analysis Guidelines

### Documentation Structure
Use the template at `references/documentation-template.md` as the base structure. Do not reorder,
rename, or omit sections. Replace all placeholder text with endpoint-specific content based on code analysis.
Ensure **Services Used** and **External Dependencies** are formatted as a list or table (not inline text).
Keep **Change Log** to at most 3 entries (most recent only).

### Response Examples Requirements

**CRITICAL**: All API documentation MUST include JSON response examples. This is mandatory for:

1. **Success Responses**:
   - Analyze the response DTO structure from `@Success` annotations
   - Read the DTO file to understand the exact JSON structure
   - Create realistic example responses with actual field names and data types
   - Include nested objects and arrays as they appear in the DTO

2. **Error Responses**:
   - Include examples for each error status code (400, 401, 403, 404, 500, etc.)
   - Show the error message format used by the API
   - Include both simple error strings and structured error objects

3. **Example Format**:
   ```markdown
   ### Success Response

   **Status Code**: `200 OK`

   ```json
   {
     "data": {
       "id": "550e8400-e29b-41d4-a716-446655440000",
       "name": "Example Room",
       "created_at": "2024-01-15T10:30:00Z"
     },
     "meta": {
       "total": 1
     }
   }
   ```

   ### Error Response

   **Status Code**: `403 Forbidden`

   ```json
   {
     "error": "insufficient permissions",
     "code": "FORBIDDEN"
   }
   ```
   ```

4. **How to Generate Examples**:
   - Use the response patterns for your framework (see Framework-Specific Analysis) to find actual response structures
   - Read the response DTO/model/schema files referenced in annotations or function signatures
   - Check service layer return values for response shapes
   - For OpenAPI/Swagger spec input: use the `example` fields in the spec if present, otherwise generate from the schema
   - For simple string/text responses, show as plain text examples
