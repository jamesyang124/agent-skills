---
name: api-spec-to-confluence
description: Creates or updates a Confluence page from an API endpoint by analyzing the router and handler code, using the documentation template in this skill folder.
---

# API Spec to Confluence

This skill automates the creation or update of a Confluence page for a specific API endpoint. It analyzes the router and handler code to generate a comprehensive API document.

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

1.  **Identify the API endpoint**: The user must provide the API path (e.g., `/api/hubs-cms/v1/me`).
2.  **Choose Operation Mode**: Ask the user if they want to:
    - **Create a new page**: Generate a new Confluence page
    - **Update an existing page**: Update an existing page by providing a page ID or search hint
3.  **Get Target Page**:
    - **For new pages**: Present a list of common parent pages (see below) for the user to choose from. The user can also enter a different page ID.
    - **For existing pages**:
      - If user provides a page ID (numeric), use it directly
      - If user provides a search hint (title/keywords), use `mcp__atlassian__confluence_search` to find matching pages and let user select
      - Retrieve the current page using `mcp__atlassian__confluence_get_page` to preserve the title
4.  **Analyze Router and Handler**:
    a.  Read `router/router.go` and search for the API path to identify the handler function.
    b.  Read the handler file and analyze both swagger annotations and implementation code.
4.  **Generate Comprehensive Documentation** based on the template in
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
    - **For new pages**: Use `mcp__atlassian__confluence_create_page` to create a new page under the specified parent. Title format: `API Spec: {path}` (e.g., "API Spec: /api/hubs-cms/v1/me").
    - **For existing pages**: Use `mcp__atlassian__confluence_update_page` to update the content while preserving the existing title (unless user wants to change it).

## Example Usage

### Example 1: Create New Page

**User**: "Create a Confluence page for the `/api/example-service/v1/users/me` endpoint."

**Agent**:
1. Asks if user wants to create new or update existing
2. User chooses "create new"
3. Presents the list of common parent pages
4. Waits for user selection

**User**: "1" (selects Technical Design)

**Agent**:
1. Reads `router/router.go` to find the handler for `/api/example-service/v1/users/me`
2. Reads the handler file (e.g., `handler/user.go`)
3. Analyzes swagger annotations and implementation code
4. Generates comprehensive markdown documentation
5. Creates Confluence page using `mcp__atlassian__confluence_create_page`
6. Returns the page URL to the user

### Example 2: Update Existing Page by ID

**User**: "Update the Confluence page 1234567890 with the latest spec for `/api/example-service/v1/uploads/init`."

**Agent**:
1. Recognizes the page ID (1234567890)
2. Retrieves the existing page using `mcp__atlassian__confluence_get_page`
3. Reads `router/router.go` to find the handler
4. Analyzes the handler code
5. Generates updated markdown documentation
6. Updates the page using `mcp__atlassian__confluence_update_page` (preserves existing title)
7. Returns confirmation and page URL

### Example 3: Update Existing Page by Search

**User**: "Update the API spec page for the upload endpoint."

**Agent**:
1. Uses `mcp__atlassian__confluence_search` with query: "API Spec upload"
2. Presents matching pages to user
3. User selects the correct page
4. Proceeds with analysis and update as in Example 2

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
- **Search Hint**: Text keywords (e.g., "upload API spec", "BlendVision upload")
- If user provides numeric value, treat it as page ID and use directly
- If user provides text, search for matching pages using `mcp__atlassian__confluence_search`

### Code Analysis
- Use `Grep` to quickly find the API path in router.go: `pattern: '"/api/example-service/v1/users/me"'`
- Look for handler package imports and function names in router definitions
- Read the entire handler function to understand the full workflow
- Check for DTO structs referenced in the handler (in `dto/` directory)
- **CRITICAL**: Search for `c.JSON()` and `c.String()` calls to understand response formats
- Read response DTO files to generate accurate JSON examples (this is mandatory)
- Identify service layer calls (in `service/` directory) for implementation context
- Include code snippets or examples where helpful
- Use clear markdown formatting for readability
- **CRITICAL**: All JSON payloads, response examples, and request bodies MUST be wrapped in markdown code blocks.
- **CRITICAL**: All request parameters (path, query, header) and DTO fields MUST be listed using tables (preferred) or unordered lists. Do not use plain text paragraphs for these.

### Update Strategy
- When updating, retrieve the existing page first to preserve the title
- Add a "Last Updated" timestamp in the Change Log section
- Increment the version number in the Change Log
- Preserve any manual edits in sections not managed by this skill (if user requests)

## Common Parent Pages

-   [Technical Design](https://example.atlassian.net/wiki/spaces/DEMO/pages/1234567/Technical+Design) (1234567)
-   [Data Requirements](https://example.atlassian.net/wiki/spaces/DEMO/pages/2345678/Data+Requirements) (2345678)
-   [Technical Documentation](https://example.atlassian.net/wiki/spaces/DEMO/pages/3456789/Technical+Documentation) (3456789)
-   [Release Notes](https://example.atlassian.net/wiki/spaces/DEMO/pages/4567890/Release+Notes) (4567890)
-   [Project Documentation](https://example.atlassian.net/wiki/spaces/DEMO/pages/5678901/Project+Documentation) (5678901)

## Page Search and Selection

When updating an existing page using a search hint:

1. **Construct Search Query**: Use `mcp__atlassian__confluence_search` with a CQL query:
   - For API specs: `type=page AND title~"API Spec" AND text~"{keywords}"`
   - Example: `type=page AND title~"API Spec" AND text~"upload"`

2. **Present Results**: Show user a numbered list of matching pages:
   ```
   Found 3 matching pages:
   1. API Spec: /api/example-service/v1/uploads/init (ID: 1234567890)
   2. API Spec: /api/example-service/v1/uploads/complete (ID: 1234567891)
   3. API Spec: /api/example-service/v1/uploads/status (ID: 1234567892)

   Which page would you like to update? (Enter number or 'cancel')
   ```

3. **Handle Selection**: Wait for user to select a page number or cancel

4. **Retrieve Page**: Once selected, use `mcp__atlassian__confluence_get_page` with the page_id to get current content and metadata

## Workflow Decision Tree

Follow this decision tree when handling user requests:

```
User Request
    |
    └─> Check Prerequisites
        |
        ├─> MCP Atlassian tools available? ──NO──> Guide user to install MCP server
        |                                           (.agent-settings/mcps/install-atlassian-mcp.sh)
        |
        └─> YES
            |
            ├─> Contains page ID (numeric)? ──YES─> UPDATE MODE
    │                                       - Retrieve page with mcp__atlassian__confluence_get_page
    │                                       - Analyze API endpoint
    │                                       - Update page with mcp__atlassian__confluence_update_page
    │
    ├─> Contains "update" keyword? ──YES─> SEARCH MODE
    │                                      - Extract search hint from request
    │                                      - Search with mcp__atlassian__confluence_search
    │                                      - Present options to user
    │                                      - Proceed with UPDATE MODE
    │
    └─> Otherwise ──> CREATE MODE
                      - Present parent page options
                      - User selects parent
                      - Analyze API endpoint
                      - Create page with mcp__atlassian__confluence_create_page
```

## Analysis Guidelines

When analyzing handler code, look for:

### Swagger Annotations
- `@Summary`: Brief description
- `@Description`: Detailed explanation
- `@Router`: Path and HTTP method
- `@Param`: Query params, path params, headers
- `@Accept`: Request content type
- `@Produce`: Response content type
- `@Success`: Successful response structure
- `@Failure`: Error response structures
- `@Security`: Authentication requirements

### Implementation Patterns
- **Middleware**: JWT validation, admin checks, rate limiting
- **Request Binding**: `c.ShouldBindJSON()`, `c.ShouldBindQuery()`, context parameter extraction
- **Response Handling** (**REQUIRED**): Look for `c.JSON()`, `c.String()`, `c.Status()` calls to understand response formats
- **Service Calls**: Identify which services/clients are used
- **Database Operations**: Direct DB queries or through repositories
- **External APIs**: Third-party services, CMS systems, payment providers, etc.
- **Error Handling**: Common error scenarios and HTTP status codes returned
- **Business Logic**: Key validation rules, transformations, workflows

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
   - Look for `c.JSON()` calls in the handler code to see actual response structures
   - Read the response DTO files referenced in `@Success` annotations
   - Check service layer return values for response shapes
   - For simple string responses (`c.String()`), show as plain text examples
