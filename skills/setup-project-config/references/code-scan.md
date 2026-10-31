# Code Scan

Detect these values for `docs/agents/code-structure.md`. Show the findings before asking; mark anything
not found as "not detected" and ask for it.

**Language & framework**
- `go.mod` → Go. Imports: `github.com/gin-gonic/gin` → Gin; `github.com/labstack/echo` → Echo; `github.com/go-chi/chi` → Chi
- `package.json` → Node. Dependencies: `express`, `fastify`, `koa`, `hapi`
- `pyproject.toml` / `requirements.txt` → Python. `fastapi`, `flask`, `django`
- `Cargo.toml` → Rust. `actix-web`, `axum`

**Router file**, first match wins: `router/router.go`, `cmd/*/main.go`, `internal/router/*.go`,
`app/router.go`, `routes/routes.go`, `server/server.go`; Node: `src/routes/index.js`, `routes/index.js`, `app.js`.

**Handler directory**: Go `handler/`, `handlers/`, `internal/handler/`; Node/Python `controllers/`, `handlers/`, `routes/`.

**DTO / model directory**: Go `dto/`, `model/`, `models/`; Node `types/`, `schema/`, `models/`, `interfaces/`; Python `schemas/`, `models/`.

**Service directory**: `service/`, `services/`, `usecase/`, `usecases/`, `domain/`.

**API base path prefix**: the common prefix in the router file, e.g. `r.Group("/api/v1")`.

**Documentation format**
- Swaggo: `// @Summary` in handler files; list the tags found
- JSDoc: `@param`, `@returns` in JS/TS files
- OpenAPI file: `openapi.yaml`, `swagger.yaml`, `api.yaml`
- FastAPI: route decorators with docstrings (docs generated from signatures)
- None found: `Style: not detected`
