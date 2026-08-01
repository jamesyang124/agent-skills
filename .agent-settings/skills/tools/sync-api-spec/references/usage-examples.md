# Usage Examples & Workflow Reference

## Example Usage

### Example 1: Full sync (first time)

**User**: "sync api spec"

**Agent**:
1. Reads `.agent-settings/project-config.md` for framework, router path, handler directory.
2. Scans the router file — finds 12 routes.
3. `docs/agents/api-spec.md` does not exist → all 12 routes are new.
4. Scans all 12 handler functions, extracting auth, params, response shapes.
5. Writes `docs/agents/api-spec.md` with the endpoints summary table and all 12 entries.
6. Asks: "Would you like to publish this to Confluence as well?"

### Example 2: Incremental sync (new routes added)

**User**: "sync api spec"

**Agent**:
1. Reads config, scans router — finds 14 routes.
2. Reads existing `docs/agents/api-spec.md` — 12 routes already documented.
3. Diff: 2 new routes (`POST /api/v1/orders`, `GET /api/v1/orders/{id}`).
4. Scans only those 2 handler functions.
5. Appends 2 new entries, updates summary table and timestamp.
6. Reports: "Added 2 routes. 12 routes unchanged."

### Example 3: Specific routes only

**User**: "sync api spec for /api/v1/auth/login and /api/v1/auth/refresh"

**Agent**:
1. Reads config, locates the 2 named handlers.
2. Scans those handlers (re-scans even if already documented).
3. Writes/updates those 2 entries, updates summary table.

### Example 4: With OpenAPI spec

**User**: "sync api spec using swagger.json"

**Agent**:
1. Reads config.
2. Reads `.agent-settings/skills/tools/sync-api-spec/references/openapi-parsing.md`.
3. Parses `swagger.json` for all paths and operations.
4. Diffs against existing `docs/agents/api-spec.md`.
5. Writes new/updated entries from spec data (no code analysis needed).

---

## Workflow Decision Tree

```
User: "sync api spec"
    |
    └─> Read project-config.md
        |
        ├─> Missing? → Tell user to run setup-project-config, stop.
        |
        └─> OK
            |
            ├─> Scan router for all current routes
            |
            ├─> docs/agents/api-spec.md exists?
            │     YES → parse existing documented routes → diff
            │     NO  → all routes are new
            |
            ├─> New routes (or user-named routes) → scan handlers
            │
            ├─> Removed routes? → flag with callout, confirm with user
            │
            ├─> Write docs/agents/api-spec.md
            │
            └─> "Publish to Confluence?" → YES → check MCP tools → publish
                                         → NO  → done
```
