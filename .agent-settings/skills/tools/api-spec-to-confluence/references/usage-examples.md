# Usage Examples & Workflow Reference

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
3. Reads the router file to find the handler
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

---

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

   Which page would you like to update? (Type a number to select, or type n to cancel.)
   ```

3. **Handle Selection**: Wait for user to select a page number or cancel

4. **Retrieve Page**: Once selected, use `mcp__atlassian__confluence_get_page` with the page_id to get current content and metadata

---

## Workflow Decision Tree

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
