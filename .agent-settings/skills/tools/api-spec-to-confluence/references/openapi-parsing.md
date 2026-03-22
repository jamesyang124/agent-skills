# OpenAPI / Swagger Spec Input

When the user provides a spec file path instead of an API path, skip all code analysis and parse the spec directly.

**Supported formats:** `swagger.json`, `swagger.yaml`, `openapi.json`, `openapi.yaml` (OpenAPI 2.x and 3.x)

## How to Parse

1. Read the spec file with the `Read` tool
2. Locate the path matching the user's endpoint (or ask user to pick from the paths listed in the spec)
3. Extract from the spec object for that path+method:
   - `summary`, `description`, `operationId`
   - `parameters` (in: path, query, header, cookie)
   - `requestBody` / `consumes` + `parameters[in=body]` (Swagger 2.x)
   - `responses` — status codes, schemas, descriptions
   - `security` — security scheme references
   - `tags` — for categorization
4. Resolve `$ref` references to `components/schemas` (OpenAPI 3) or `definitions` (Swagger 2) by reading those schema objects
5. Generate the Confluence documentation from the resolved data — the same template applies

## Common Spec File Locations

If user doesn't specify a path, try these in order:
- `swagger.json`, `docs/swagger.json`, `api/swagger.json`
- `openapi.yaml`, `docs/openapi.yaml`, `api/openapi.yaml`
- `swagger.yaml`, `docs/swagger.yaml`
