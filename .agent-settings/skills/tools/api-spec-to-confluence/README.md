# API Spec to Confluence Skill

A Claude Code skill that generates comprehensive API documentation from Go handler code and publishes it to Confluence.

## Features

### 🆕 Create New Documentation
- Analyzes router and handler code
- Extracts swagger annotations
- Generates comprehensive markdown documentation
- Creates new Confluence page under specified parent

### 🔄 Update Existing Documentation
- Update by page ID: Provide numeric page ID directly
- Update by search: Search by keywords/title and select from results
- Preserves existing page title and structure
- Maintains version history in Change Log section

## Usage Examples

### Create New Page
```
User: "Create a Confluence page for the /api/example-service/v1/users/me endpoint"
```

### Update by Page ID
```
User: "Update page 1234567890 with latest spec for /api/example-service/v1/uploads/init"
```

### Update by Search
```
User: "Update the API spec page for the upload endpoint"
```

## How It Works

### Operation Mode Detection
The skill automatically detects the operation mode based on user input:

- **CREATE MODE**: Default mode, or when user says "create" or "new"
- **UPDATE MODE (by ID)**: When user provides a numeric page ID
- **UPDATE MODE (by search)**: When user says "update" with keywords

### Documentation Generation
The skill performs deep analysis of:
1. Router definitions in `router/router.go`
2. Handler functions and swagger annotations
3. Request/Response DTOs in `dto/` directory
4. Service layer dependencies in `service/` directory
5. Middleware and authentication requirements

### Confluence Integration
- **Create**: Uses `mcp__atlassian__confluence_create_page`
- **Update**: Uses `mcp__atlassian__confluence_update_page`
- **Search**: Uses `mcp__atlassian__confluence_search` with CQL queries
- **Retrieve**: Uses `mcp__atlassian__confluence_get_page` for existing content

## Documentation Structure

Generated documentation includes:
- ✅ HTTP Method and Path
- ✅ Summary and Description
- ✅ Authentication Requirements
- ✅ Request Specification (params, headers, body)
- ✅ Response Specification with JSON examples
- ✅ Error Responses with status codes
- ✅ Implementation Details
- ✅ Dependencies and External Services
- ✅ Change Log with version history

## Common Parent Pages

Loaded from `.agent-settings/project-config.md`. Run the `setup-project-config` skill to
populate these with your actual Confluence page IDs.

## Setup

Before first use, generate the shared project config by running:

```
"set up project config"
```

This runs the `setup-project-config` skill, which scans your codebase and writes
`.agent-settings/project-config.md` with your Confluence space, parent page IDs, and
code directory layout. All Atlassian skills read from this same file — you only need
to run it once per project.

If the config file is missing when you invoke this skill, the agent will remind you to run setup.

## Requirements

### MCP Server
Requires the Atlassian MCP server to be configured:
- `mcp__atlassian__confluence_create_page`
- `mcp__atlassian__confluence_update_page`
- `mcp__atlassian__confluence_search`
- `mcp__atlassian__confluence_get_page`

## Version History

- **v1.0** (2025-01-XX): Initial version with create functionality
- **v2.0** (2025-02-02): Added update functionality with page search
  - Update by page ID
  - Update by search hint
  - Preserve existing page titles
  - Version tracking in Change Log

## Tips

- Always provide the API path (e.g., `/api/example-service/v1/endpoint`)
- For updates, you can use either page ID or search keywords
- The skill automatically detects middleware and authentication requirements
- JSON response examples are generated from DTO structures
- Version numbers are automatically incremented in the Change Log
