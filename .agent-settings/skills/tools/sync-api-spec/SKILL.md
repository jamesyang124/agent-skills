---
name: sync-api-spec
description: Scans all API routes in the project and maintains docs/agents/api-spec.md — a machine-readable API reference for coding agents, frontend, and product to understand what APIs do. Incremental: only re-scans handlers for new or changed routes. Optional Confluence publish step after local file is written. Use at the Implement & PR phase of the SDD workflow or any time you want to keep the API spec file current.
allowed-tools: Read, Glob, Grep
---

# Sync API Spec

## Install this skill globally

Install once — available in all projects.

```bash
# Claude
mkdir -p ~/.claude/skills/sync-api-spec
cp <agent-settings-repo>/.agent-settings/skills/tools/sync-api-spec/SKILL.md \
   ~/.claude/skills/sync-api-spec/SKILL.md
# Add to ~/.claude/CLAUDE.md: - **sync-api-spec** (`~/.claude/skills/sync-api-spec/SKILL.md`)

# Copilot
mkdir -p ~/.copilot/skills/sync-api-spec
cp <agent-settings-repo>/.agent-settings/skills/tools/sync-api-spec/SKILL.md \
   ~/.copilot/skills/sync-api-spec/SKILL.md

# Gemini
mkdir -p ~/.gemini/skills/sync-api-spec
cp <agent-settings-repo>/.agent-settings/skills/tools/sync-api-spec/SKILL.md \
   ~/.gemini/skills/sync-api-spec/SKILL.md
```

This skill maintains `docs/agents/api-spec.md` — a compact, machine-readable API reference for the consuming project. It scans the router for all routes, diffs against the existing spec file to find new or changed routes, re-scans only those handlers, and writes an updated file. An optional Confluence publish step is offered after the local file is written.

## Output File

Target: `docs/agents/api-spec.md` (relative to the consuming project root, **not** this repo).

Format is defined in `references/api-spec-format.md`.

## Process

0.  **Load project configuration**: Read `.agent-settings/project-config.md`.
    - If the file is missing: tell the user to run `setup-project-config` first (`"set up project config"`), then stop.
    - Use framework, router file path, handler directory, DTO/model directory, and service directory from config throughout.

0b. **Contract mode check**:
    Ask the user:
    ```
    Generate in contract mode? (y/n)
    ```
    - Blank input: re-prompt — must type `y` or `n`.
    - **Contract mode** (`y`): the spec describes a *planned / agreed-upon* API that has not been implemented yet.
      The agent documents based on user-provided descriptions, not scanned code.
      Set `CONTRACT_MODE=true`. Skip steps 2–4 (no router scan, no handler scan).
    - **Normal mode** (`n`): scan existing code as usual. Set `CONTRACT_MODE=false`.

    If `CONTRACT_MODE=true`, jump directly to the **Contract Mode** section below after this step.

1.  **Determine scope**:
    - Default: scan all routes (full sync).
    - If user names specific routes or says "only new routes", restrict to those.

2.  **Scan the router** using the router file path from config.
    - Apply framework-specific parsing from `.agent-settings/skills/tools/sync-api-spec/references/framework-patterns.md`.
    - Build a list of all current routes: `{method} {path} → handler`.
    - If no framework is in config: use the Auto-Detection section of `framework-patterns.md`, then confirm with user.

3.  **Load existing spec** (if `docs/agents/api-spec.md` exists):
    - Parse the `## Endpoints Summary` table to extract already-documented routes.
    - Diff: routes in router but not in spec = **new**; routes in spec but not in router = **removed** (flag for deletion, confirm with user before removing).
    - Routes in both = **existing** (skip unless user explicitly named them).
    - **Contract promotion check**: scan the spec for any entries with a `🔷 CONTRACT` badge. For each one, check whether that route (`METHOD /path`) now appears in the router scan from step 2.
      - **Found in router** → route has been implemented. Scan its handler (step 4), update the entry with real data, and **remove the `🔷 CONTRACT` badge** automatically. Report to user: `✓ Promoted from contract: METHOD /path`.
      - **Not found in router** → route is still unimplemented. Leave the badge and entry unchanged.
      - After all promotions, if no `🔷 CONTRACT` entries remain, ask: `All contract routes are now implemented. Remove the contract banner? (y/n)` — blank re-prompts, must type `y` or `n`.

4.  **Scan handlers** for new (and user-named) routes only:
    - Apply framework-specific handler analysis from `framework-patterns.md`.
    - For each handler extract: HTTP method, path, purpose (one line), auth/middleware, request params/body, response codes and shapes, key implementation notes.
    - If an OpenAPI/Swagger spec file is available, read `.agent-settings/skills/tools/sync-api-spec/references/openapi-parsing.md` and prefer spec data over code inference.

5.  **Write `docs/agents/api-spec.md`**:
    - Follow the format in `references/api-spec-format.md` exactly.
    - Merge: keep existing documented entries unchanged, append new entries, mark removed routes with a `> ⚠️ Route removed from router — confirm deletion` callout (do not delete automatically).
    - Update the `Last updated` timestamp and `## Endpoints Summary` table.

6.  **Offer optional Confluence publish**:
    - Ask: `Publish to Confluence? (y/n)` — blank re-prompts, must type `y` or `n`.
    - If `n`: skip.
    - If `y`:
      - Check that Atlassian MCP tools are available (`mcp__atlassian__confluence_create_page` / `mcp__atlassian__confluence_update_page`). If not available, tell user to configure the MCP server first and skip this step.
      - **Only publish routes changed in this session** — not the full spec:
        - **Normal mode**: determine changed routes by running `git diff HEAD -- docs/agents/api-spec.md` and extracting only the `## METHOD /path` headings that appear in the diff (added `+` lines). Publish only those endpoint cards.
        - **Contract mode**: publish only the endpoint cards added during the current contract session (the ones written in step 1c).
        - **Promoted routes** (contract → implemented): publish the updated card for each promoted route.
      - Confluence page: use the space and parent page from `project-config.md`. Page title: `API Spec — {Project Name}`.
      - If the Confluence page already exists: update only the sections for the changed endpoints (do not overwrite the full page). If it does not exist: create it with the full spec content.

---

## Contract Mode

Only entered when the user answers `y` to the contract mode prompt in step 0b.

Contract mode documents **planned APIs** that do not yet exist in code. The agent works from user input, not scanned source files.

### Contract Mode Process

1. **Endpoint input loop** — repeat until the user is done:

   a. Ask:
      ```
      Describe the next planned endpoint (method + path + purpose), or paste a spec:
      (Type "n" to finish adding endpoints)
      ```

   b. If user provides an endpoint, collect details:
      - Method and path
      - Purpose (one sentence)
      - Auth requirements
      - All request headers, path params, query params, body fields (required and optional, including nested — use dot-notation)
      - Expected response codes and shapes

   c. **Immediately write / prepend** that endpoint's card to `docs/agents/api-spec.md` following `references/api-spec-format.md`:
      - **First endpoint**: write the full file from scratch — `# API Spec` heading → `## Endpoints Summary` table → Contract Banner → `## Endpoints` section heading → `---` separator → the card. Create the file if it does not exist.
      - **Subsequent CONTRACT endpoints**: insert the new `---` + card block as the **first item inside `## Endpoints`** (directly after the `## Endpoints` line), before all other cards. NEVER append to the end of the file.
      - Each card: `🔷 CONTRACT` badge on the `## METHOD /path` heading, status `planned`.
      - Update the `## Endpoints Summary` table: insert the new CONTRACT row at the top (above all other CONTRACT rows and all ✅ rows).

   d. After writing, ask:
      ```
      ✓ Added METHOD /path.  Do you have another endpoint to add? (Y/n)
      ```
      - `n` or `N` → exit the loop and continue to step 2.
      - Blank input or any other value → loop back to step 1a (do not accept blank as exit).

2. **Branch creation** — once the loop ends, ask:
   ```
   Create a contract branch from origin/master?
   Enter branch suffix (e.g. "user-auth") to create contract/<suffix>, or type "n" to skip:
   ```
   - If user types `n` or `N`: skip.
   - Blank input or any other non-`n` value: re-prompt — do not accept blank as skip.
   - If suffix provided:
     1. Run `git fetch origin` first (always, to ensure a fresh `origin/master`).
     2. Then run `git checkout -b contract/<suffix> origin/master`.
     3. Confirm: `✓ Branch contract/<suffix> created from origin/master.`

3. **Offer Confluence publish** (same as normal mode step 6 — publishes only the endpoint cards added this contract session).

### Contract Banner Format

Insert this block **immediately after the `## Endpoints Summary` table**. Never place it above `# API Spec`.

The banner is present whenever the spec contains any `🔷 CONTRACT` entries (regardless of whether there are also implemented entries):

```markdown
> [!CAUTION]
> **CONTRACT SPEC — Contains unimplemented endpoints**
> Endpoints marked 🔷 CONTRACT in the table above have not been built and are subject to change.
> Remove each badge and this banner once all endpoints are implemented and verified.
```

Immediately after the Contract Banner (or after the Summary table when no banner), write the `## Endpoints` section heading. All cards live inside this section.

The `## Endpoints Summary` table must always include a `Status` column:
- `🔷 CONTRACT` rows are listed **first** (before all `✅` rows), regardless of insertion order.
- `✅` for implemented routes
- `🔷 CONTRACT` for planned/unimplemented routes

**Ordering rule for CONTRACT cards**: CONTRACT endpoint cards are always placed **above all implemented cards** in the file. When a new CONTRACT entry is added, it is **prepended to the top of the CONTRACT block** (last-in, stays at top). Implemented cards follow below, in the order they were documented.

### Mixed Contract + Implemented Entries

Handled automatically by the normal sync **step 3 contract promotion check**:
- `🔷 CONTRACT` routes found in the router → promoted, badge removed, handler re-scanned.
- `🔷 CONTRACT` routes not yet in router → left unchanged.
- When all badges are gone → offer to remove the Contract Banner.

## Tips for the Agent

### Incremental Scanning
- **Only re-scan handlers for new or user-named routes.** Never re-scan routes already documented unless explicitly asked.
- "Changed" routes are ones the user names explicitly, or routes flagged by the user as stale.
- Routes disappearing from the router are candidates for removal — always confirm with the user before deleting an entry from the spec.

### Code Analysis
- Use the router file, handler/controller directory, DTO/model directory, and service directory from project config.
- Use `Grep` to quickly find route registrations and handler function names.
- Read the full handler function to understand auth, request binding, response shapes, and service calls.
- Read DTO/model/schema files referenced by the handler to generate accurate field lists and JSON examples.
- **CRITICAL**: All JSON examples MUST be wrapped in markdown code blocks.
- **CRITICAL**: All parameter and field lists MUST use tables.

### Confluence (Optional Step)
- Do NOT require Confluence — the local file is the primary output.
- Only check for MCP tools if the user says yes to the publish prompt.
- If MCP tools are unavailable, skip Confluence and confirm the local file was written successfully.

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
