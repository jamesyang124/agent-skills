---
name: setup-project-config
description: One-time setup skill that generates .agent-settings/project-config.md — a namespaced per-MCP project-settings file. Scans the codebase for structure, discovers installed MCPs from .mcp.json, and prompts for each MCP's project-scoped (non-secret) fields plus the SDD tool. Credentials stay in the global ~/.env.mcp-* store. Run before using MCP-backed skills. Use when setting up skills for the first time, configuring per-project MCP settings (Atlassian/Playwright/Sentry/Azure DevOps), or asked to init/recalibrate project config.
argument-hint: "(no arguments - auto-detects setup vs re-calibration)"
allowed-tools: Read, Glob, Grep, Bash, Write
---

# Setup Project Config

## Install this skill globally

Install once — available in all projects.

```bash
# Claude
mkdir -p ~/.claude/skills/setup-project-config
cp <agent-settings-repo>/.agent-settings/skills/tools/setup-project-config/SKILL.md \
   ~/.claude/skills/setup-project-config/SKILL.md
# Add to ~/.claude/CLAUDE.md: - **setup-project-config** (`~/.claude/skills/setup-project-config/SKILL.md`)

# Copilot
mkdir -p ~/.copilot/skills/setup-project-config
cp <agent-settings-repo>/.agent-settings/skills/tools/setup-project-config/SKILL.md \
   ~/.copilot/skills/setup-project-config/SKILL.md
```

## Dependencies

No external skills or MCPs required. Only needs read access to the project codebase.

---

Generates `.agent-settings/project-config.md` — the shared per-project config file. Consumers and the
sections they read are listed authoritatively in
`references/config-output-format.md` (currently `sync-api-spec`, `ado-open-pr`, `tech-plan-to-wiki`,
`sdd-qa-to-ticket`, `install-external-skills`).

**Detect mode automatically** based on whether `.agent-settings/project-config.md` already exists:
- **No file** → Mode A: Initial Setup
- **File exists, legacy schema** (has a top-level `## Confluence` or `## Jira` section) → **Mode M: Migrate first**, then Mode B
- **File exists, current schema** (`## MCP: <name>` sections) → Mode B: Re-calibration

> **Always run the legacy check on any existing file before Mode B.** Older configs (pre per-MCP schema)
> used flat `## Confluence` / `## Jira` sections that upgraded consumers no longer read — so they break
> silently. Migrate them before anything else.

---

## Arguments

None. The mode is detected from `.agent-settings/project-config.md`: missing file → **Mode A** (initial setup); legacy schema → **Mode M** (migrate) then **Mode B**; current schema → **Mode B** (re-calibration).

---

## Trigger phrases

- **Initial setup**: "set up project config", "init project config", "configure skills"
- **Re-calibrate**: "recalibrate project config", "update project config", "my framework changed", "rescan project structure"
- **Update Atlassian only**: "update confluence settings", "change jira project key"

---

## Mode A: Initial Setup

### Phase 1 — Code Scan (automated)

Scan the project root to detect:

**Language & framework**:
- `go.mod` present → Go. Check imports for `github.com/gin-gonic/gin` → Gin; `github.com/labstack/echo` → Echo; `github.com/go-chi/chi` → Chi
- `package.json` present → Node. Check dependencies for `express`, `fastify`, `koa`, `hapi`
- `pyproject.toml` or `requirements.txt` → Python. Check for `fastapi`, `flask`, `django`
- `Cargo.toml` → Rust. Check for `actix-web`, `axum`

**Router file** — search in this order until found:
1. `router/router.go`
2. `cmd/*/main.go`
3. `internal/router/*.go`
4. `app/router.go`
5. `routes/routes.go`
6. `server/server.go`
7. For Node: `src/routes/index.js`, `routes/index.js`, `app.js`

**Handler directory** — look for files matching `*handler*`, `*controller*` patterns:
- Go: `handler/`, `handlers/`, `internal/handler/`
- Node/Python: `controllers/`, `handlers/`, `routes/`

**DTO/model directory**:
- Go: `dto/`, `model/`, `models/`
- Node: `types/`, `schema/`, `models/`, `interfaces/`
- Python: `schemas/`, `models/`

**Service directory**:
- `service/`, `services/`, `usecase/`, `usecases/`, `domain/`

**API base path prefix** — scan router file for repeated prefix patterns:
- Look for lines like `r.Group("/api/v1")` or `router.GET("/api/v1/..."`
- Extract the common prefix shared by most routes

**Documentation format**:
- Swaggo: search for `// @Summary` in handler files
- JSDoc: search for `@param`, `@returns` in JS/TS files
- OpenAPI spec file: look for `openapi.yaml`, `swagger.yaml`, `api.yaml`
- FastAPI/automatic: check for `@app.get`, `@router.post` decorators with docstrings

**SDD tool**:
- Check for `.speckit` or `spec-kit.json` → `spec-kit`
- Check for `openspec.json` or `.openspec` → `openspec`
- If neither found → note as "not detected — will prompt"

After scanning, show the agent's findings before prompting:
```
Detected project structure:
  Language:    Go
  Framework:   Gin (github.com/gin-gonic/gin)
  Router file: router/router.go
  Handlers:    handler/
  DTOs:        dto/
  Services:    service/
  API prefix:  /api/v1/
  Doc style:   Swaggo annotations
  SDD tool:    spec-kit
```

If anything could not be detected, note it as "not detected — will prompt".

### Phase 2 — MCP-scoped prompts (driven by installed MCPs)

**What this phase captures — and what it does NOT.** Three planes, three homes:

| Plane | Home | This phase? |
|-------|------|-------------|
| Secrets / tokens / connection URL | global `~/.env.mcp-<name>` (or OAuth) | never — not prompted, not stored here |
| Auto-derivable from the codebase | `## Code Structure` (Phase 1) | no — auto-detected |
| Per-project, user-chosen, non-secret MCP behavior | `## MCP: <name>` sections | **yes** |

`project-config.md` is a **namespaced per-MCP settings file**. Each installed MCP that has project-scoped
knobs gets one `## MCP: <name>` section. Credentials always stay in the global env store.

**Precedence:** `~/.env.mcp-<name>` dominates as the authoritative source (connection + all secrets).
A `project-config.md` field is a per-project *override* that wins only when explicitly present; blank or
absent → the global env value stands. project-config never replaces the env store, only layers non-secret
overrides on top.

**Step 1 — Discover installed MCPs.** Read the MCP registration for the active agent (do not depend on
env files existing — Playwright has no creds, Sentry-remote uses OAuth):

```bash
# Claude
cat .mcp.json .claude/mcp.json 2>/dev/null
# Copilot / VS Code
cat .vscode/mcp.json 2>/dev/null
```

Collect the `mcpServers` (Copilot uses `servers`) keys → the set of installed MCP names. If none found,
tell the user no MCPs are registered and skip to the SDD-tool prompt.

**Step 2 — For each installed MCP that appears in the registry below, prompt only its scoped fields.**
Skip MCPs that are not installed. Skip fields the user leaves blank. For each MCP, note whether its
credential store is present and warn if the MCP is installed but its creds/OAuth are missing.

Then, regardless of MCPs:

**SDD tool** (top-level, not an MCP) — ask: "Which SDD tool does your team use? (`spec-kit` / `openspec`)"
— pre-fill with the Phase 1 detected value if any, default `spec-kit`.
- If `spec-kit`: commands are `spec-kit specify` / `spec-kit plan`
- If `openspec`: ask: "What are the specify and plan commands for openspec in your project?"

---

### Per-MCP scoped-field registry

Each MCP's own install/consumer skill owns its schema; this table is the orchestrator's copy. When a skill
adds or drops a project-scoped field, update its row here and the matching block in
`references/config-output-format.md`.

**`atlassian`** — creds: `~/.env.mcp-atlassian` (`CONFLUENCE_URL`, `JIRA_URL` + tokens)
- Confluence Space Key — e.g., `ENG`
- Common Parent Pages — up to 3; for each: page name + page ID
  - Prompt: "Enter parent page 1 name and ID (e.g., 'Technical Design, 1234567890'), or press Enter to skip"; stop at first skip
- Jira Project Key — e.g., `PROJ`
- Jira Issue Type — default `Story`
- *(optional)* Base URL override — only if this repo targets a **different** instance than the global env; omit otherwise, do not prompt unless asked

**`playwright`** — creds: none (local browser automation)
- User-Agent — e.g., `HTCVRSDET`; press Enter to skip
- Allowed Domains — comma-separated; e.g., `portal.your-org.com, docs.your-org.com`
- Base URL — default target origin, e.g., `https://staging.example.com`
- *(optional)* Viewport / Headless — only if the user has non-default needs

**`sentry`** — creds: OAuth (remote `mcp.sentry.dev`) or `SENTRY_ACCESS_TOKEN` (local stdio); no URL/token prompted here
- Org Slug — e.g., `my-org`
- Project Slug — e.g., `my-proj`

**`azure-devops` (ado)** — creds: `~/.env.mcp-azure-devops` (PAT)
- Organization — e.g., `my-org`
- Project — e.g., `my-project`
- Default Repo — e.g., `my-repo`

Unknown / unlisted MCP names: note them as detected but skip (no known scoped schema); the owning skill
can add a row when it needs project-scoped config.

### Phase 3 — Confirm and Write

Display all detected + entered values in the final config format, then ask:
```
Write this to .agent-settings/project-config.md? (y/n)
```

On confirmation, write the file using the format defined below.

---

## Mode M: Migrate legacy schema

Runs when an existing `project-config.md` still uses the flat pre-MCP layout. **Detect** by grepping the
file for a top-level `## Confluence` or `## Jira` heading (the current schema has neither — Atlassian lives
under `## MCP: atlassian`).

### Phase 1 — Announce and map

Tell the user the config predates the per-MCP schema and that consumers (e.g. `sync-api-spec`) no longer
read the old sections, so it must be migrated. Show the exact field mapping before touching the file:

```
Legacy project-config.md detected. Migrating to per-MCP schema:

  ## Confluence → ## MCP: atlassian
    - Space Key            → Confluence Space Key
    - Common Parent Pages  → (kept as-is under ## MCP: atlassian)
    - Page Title Format    → (kept as-is)
  ## Jira → ## MCP: atlassian
    - Default Project Key  → Jira Project Key
    - Default Issue Type   → Jira Issue Type
  Base URL (both)          → dropped (inherited from ~/.env.mcp-atlassian);
                             kept only if it differs from the global env value → Base URL override

  ## Code Structure / ## Documentation Format / ## SDD Tool → unchanged

Rewrite in the new format? (y/n)
```

### Phase 2 — Rewrite

On `y`, merge `## Confluence` + `## Jira` into a single `## MCP: atlassian` section per the mapping,
preserving every user value (space key, parent-page table, project key, issue type). Drop each `Base URL`
unless it differs from the global env `CONFLUENCE_URL` / `JIRA_URL`, in which case keep it as an
`Base URL` override line. Leave `## Code Structure`, `## Documentation Format`, and `## SDD Tool` intact.
Write the file, then continue into **Mode B** (re-scan + diff) as normal.

On `n`, warn that Atlassian-backed skills will not find their config until migrated, and stop.

---

## Mode B: Re-calibration

### Phase 1 — Re-scan code structure (automated)

Re-run the same code scan as Mode A Phase 1 to get fresh detected values.

### Phase 2 — Diff against existing config

Read the existing `.agent-settings/project-config.md`. Compare the `## Code Structure` section
values against the freshly detected values. Show only what changed:

```
Re-scan detected changes:

  Framework:    Gin → Echo
  Router file:  router/router.go → internal/server/routes.go
  API prefix:   /api/v1/ → unchanged
  SDD tool:     spec-kit → unchanged

MCP-scoped settings are unchanged (not re-prompted).

Apply these changes? (y/n, or describe corrections to make first)
```

If nothing changed in Code Structure, say so:
```
Re-scan found no changes to code structure. MCP-scoped settings unchanged.
Nothing to update.
```

**`## MCP: <name>` sections are NOT re-prompted** unless the trigger phrase specifically targets one
(e.g., "update confluence settings", "change jira project key", "update playwright domains"). In that
case, skip the code scan and prompt only for that MCP's scoped fields.

Also re-run **Step 1 (discover installed MCPs)**: if a new MCP was installed since last run, offer to add
its `## MCP: <name>` section; if an MCP was removed, note its now-orphaned section but do not delete it
without asking.

### Phase 3 — Patch and Write

Apply only the changed fields to `project-config.md`, preserving all other `## MCP: <name>` sections and
the SDD Tool section. Rewrite the file with merged values.

---

## Output Format & Notes

When writing the config file, use the format defined in `.agent-settings/skills/tools/setup-project-config/references/config-output-format.md`.
