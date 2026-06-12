---
name: setup-project-config
description: One-time setup skill that generates .agent-settings/project-config.md by scanning the codebase and prompting for Confluence and Jira details. Run this before using other Atlassian skills. Use when setting up skills for the first time, configuring Confluence/Jira integration, or asked to init/recalibrate project config.
allowed-tools: Read, Glob, Grep, Write
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

# Gemini
mkdir -p ~/.gemini/skills/setup-project-config
cp <agent-settings-repo>/.agent-settings/skills/tools/setup-project-config/SKILL.md \
   ~/.gemini/skills/setup-project-config/SKILL.md
```

## Dependencies

No external skills or MCPs required. Only needs read access to the project codebase.

---

Generates `.agent-settings/project-config.md` — the shared config file read by all Atlassian skills
(`sync-api-spec`, `tech-plan-to-wiki`, etc.).

**Detect mode automatically** based on whether `.agent-settings/project-config.md` already exists:
- **No file** → Mode A: Initial Setup
- **File exists** → Mode B: Re-calibration

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

### Phase 2 — User Prompts (Atlassian details only)

Ask for the following, one at a time or as a grouped prompt:

1. **Confluence base URL** — e.g., `https://yourcompany.atlassian.net/wiki`
2. **Confluence space key** — e.g., `ENG`
3. **Common parent pages** — ask for up to 3; for each ask: page name + page ID
   - Present as: "Enter parent page 1 name and ID (e.g., 'Technical Design, 1234567890'), or press Enter to skip"
4. **Jira base URL** — usually same domain, e.g., `https://yourcompany.atlassian.net`
5. **Default Jira project key** — e.g., `PROJ`
6. **Default Jira issue type** — default: `Story`
7. **SDD tool** — ask: "Which SDD tool does your team use? (`spec-kit` / `openspec`)" — pre-fill with detected value if any, default `spec-kit`
   - If `spec-kit`: commands are `spec-kit specify` / `spec-kit plan`
   - If `openspec`: ask: "What are the specify and plan commands for openspec in your project?"

If user skips a parent page, stop asking for more parent pages.

### Phase 3 — Confirm and Write

Display all detected + entered values in the final config format, then ask:
```
Write this to .agent-settings/project-config.md? (y/n)
```

On confirmation, write the file using the format defined below.

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

Confluence and Jira settings are unchanged (not re-prompted).

Apply these changes? (y/n, or describe corrections to make first)
```

If nothing changed in Code Structure, say so:
```
Re-scan found no changes to code structure. Confluence and Jira settings unchanged.
Nothing to update.
```

**Atlassian settings (Confluence, Jira) are NOT re-prompted** unless the trigger phrase specifically
targets them (e.g., "update confluence settings", "change jira project key"). In that case, skip
the code scan and prompt only for the Atlassian fields that need updating.

### Phase 3 — Patch and Write

Apply only the changed fields to `project-config.md`, preserving all Atlassian config. Rewrite
the file with merged values.

---

## Output Format & Notes

When writing the config file, use the format defined in `.agent-settings/skills/tools/setup-project-config/references/config-output-format.md`.
