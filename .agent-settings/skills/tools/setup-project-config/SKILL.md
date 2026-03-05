---
name: setup-project-config
description: One-time setup skill that generates .agent-settings/project-config.md by scanning the codebase and prompting for Confluence and Jira details. Run this before using other Atlassian skills.
---

# Setup Project Config

Generates `.agent-settings/project-config.md` — the shared config file read by all Atlassian skills
(`api-spec-to-confluence`, `sdd-tech-plan-to-confluence`, etc.).

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

## Output format — `.agent-settings/project-config.md`

```markdown
# Project Configuration
# Generated by setup-project-config skill. Re-run the skill to update.

## Confluence
- Base URL: https://yourcompany.atlassian.net/wiki
- Space Key: ENG

### Common Parent Pages
| Name | ID | URL |
|------|----|-----|
| Technical Design | 1234567890 | https://yourcompany.atlassian.net/wiki/spaces/ENG/pages/1234567890 |
| API Documentation | 2345678901 | https://yourcompany.atlassian.net/wiki/spaces/ENG/pages/2345678901 |

### Page Title Format
API Spec: {METHOD} {path}

## Jira
- Base URL: https://yourcompany.atlassian.net
- Default Project Key: PROJ
- Default Issue Type: Story

## Code Structure
- Language: Go
- Framework: Gin (github.com/gin-gonic/gin)
- Router file: router/router.go
- Handler directory: handler/
- DTO directory: dto/
- Service directory: service/
- API base path prefix: /api/v1/

## Documentation Format
- Style: Swaggo inline annotations
- Tags: @Summary, @Description, @Router, @Param, @Accept, @Produce, @Success, @Failure, @Security
- Binding: c.ShouldBindJSON(), c.ShouldBindQuery(), c.Param(), c.Query()
- Response: c.JSON(), c.String(), c.Status()
```

For the Common Parent Pages table:
- Construct the URL as `{Confluence base URL}/spaces/{Space Key}/pages/{ID}`
- If user provided a name but not an ID (or vice versa), omit that row

For Documentation Format:
- Swaggo: list the annotation tags detected in handler files
- Node/JSDoc: list the JSDoc tags found
- FastAPI: note that docs are auto-generated from function signatures
- If not detected, write: `Style: not detected`

---

## Notes

- Write the file to `.agent-settings/project-config.md` (relative to the project root)
- Do not commit this file — it is gitignored in the skills template repo
- If the user is running this inside their project repo (not the template repo), they can choose
  to commit it there
- After writing, tell the user which skills will now use this config
