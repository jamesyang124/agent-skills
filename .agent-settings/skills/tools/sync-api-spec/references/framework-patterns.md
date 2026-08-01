# Framework-Specific Analysis Patterns

Use the framework value from `project-config.md` (`## Code Structure` → `Framework`) to select the correct strategy.

---

## Go — Gin / Echo / Chi

**Where to find the endpoint:**
Read the router file from config (e.g., `router/router.go`, `routes/routes.go`). Search for the API path to find the handler function name. Then read the handler file.

**Annotations (Swaggo):**
`@Summary`, `@Description`, `@Router`, `@Param`, `@Accept`, `@Produce`, `@Success`, `@Failure`, `@Security`

**Request binding patterns:**
- Gin: `c.ShouldBindJSON()`, `c.ShouldBindQuery()`, `c.Param()`, `c.Query()`
- Echo: `c.Bind()`, `c.Param()`, `c.QueryParam()`
- Chi: `chi.URLParam(r, "id")`, `r.URL.Query()`

**Response patterns:**
- Gin: `c.JSON()`, `c.String()`, `c.Status()`
- Echo: `c.JSON()`, `c.String()`, `c.NoContent()`
- Chi: `render.JSON()`, `w.WriteHeader()`, `json.NewEncoder(w).Encode()`

**DTOs**: Check the DTO/model directory from config for request/response struct definitions.

---

## Ruby on Rails

**Where to find the endpoint:**
- Read `config/routes.rb` to find the controller and action (e.g., `resources :users` → `UsersController#show`)
- Read the controller file in `app/controllers/`

**Annotations:**
- Native Rails has no built-in annotations — look for `rswag`, `grape-swagger`, `apipie`, or manual YARD docs
- `rswag`: look for `swagger_path` blocks in spec files (`spec/requests/`)
- `apipie`: look for `api :GET`, `param`, `returns` DSL in the controller
- Otherwise: read the action body and infer from strong params, renders, and responds_to blocks

**Request patterns:**
- Params: `params[:id]`, `params.require(:user).permit(...)`
- Strong params: look for private `def user_params` methods
- Headers: `request.headers['Authorization']`

**Response patterns:**
- `render json: @user`, `render json: { error: ... }, status: :unprocessable_entity`
- `respond_to { |f| f.json { render json: ... } }`
- HTTP status symbols: `:ok`, `:created`, `:not_found`, `:unprocessable_entity`

**Auth/middleware:** `before_action :authenticate_user!` (Devise), `before_action :require_admin`

---

## Node.js — Express / Fastify / Koa

**Where to find the endpoint:**
Read the router/routes file from config (e.g., `routes/users.js`, `src/routes/index.ts`). Search for the API path to find the handler function or inline handler.

**Annotations (JSDoc Swagger):**
```js
/**
 * @swagger
 * /users/{id}:
 *   get:
 *     summary: Get user by ID
 *     parameters: ...
 *     responses: ...
 */
```
Also look for `swagger-jsdoc`, `tsoa`, `routing-controllers` decorators.

**Request patterns:**
- Express: `req.params.id`, `req.query.page`, `req.body`, `req.headers['authorization']`
- Fastify: `request.params`, `request.query`, `request.body`

**Response patterns:**
- Express: `res.json({...})`, `res.status(404).json({...})`, `res.send(...)`
- Fastify: `reply.send({...})`, `reply.code(201).send({...})`

**DTOs/validation**: Look for Joi, Zod, Yup schemas or TypeScript interfaces near the route.

---

## Python — FastAPI

**Where to find the endpoint:**
FastAPI uses decorator-based routing — search for `@app.get("/path")`, `@router.post("/path")`, or `@app.{method}("/path")`. The function signature IS the API contract (no separate router file needed).

**No annotations needed — everything is in the code:**
- Path params: function params matching `{param}` in the path (e.g., `def get_user(user_id: int)`)
- Query params: typed function params without path match (e.g., `page: int = 1`)
- Request body: `body: UserCreate` where `UserCreate(BaseModel)` is a Pydantic model
- Response model: `response_model=UserResponse` in the decorator
- Status code: `status_code=201` in the decorator
- Auth: `Depends(get_current_user)` or `Depends(oauth2_scheme)`

**DTOs**: Read Pydantic model definitions (classes inheriting `BaseModel`) for field names and types.

---

## Python — Flask

**Where to find the endpoint:**
Search for `@app.route("/path", methods=["GET"])` or `@bp.route(...)`. For Blueprint-based apps, find `Blueprint` definitions and their `url_prefix`.

**Annotations:**
- `flasgger`: look for YAML docstrings inside the route function or `swag_from` decorator
- `flask-restx`/`flask-restplus`: look for `@ns.route()`, `@ns.expect()`, `@ns.marshal_with()` and `api.model()` definitions
- Otherwise: infer from `request.json`, `request.args`, `jsonify()`

**Request patterns:** `request.json`, `request.args.get('page')`, `request.form`, `request.headers.get('Authorization')`

**Response patterns:** `jsonify({...})`, `make_response(jsonify(...), 404)`, `return {"key": "val"}, 200`

---

## Auto-Detection (no framework in config)

Search the codebase for these indicators and confirm with the user:

| Indicator | Framework |
|-----------|-----------|
| `go.mod` + `github.com/gin-gonic/gin` | Go / Gin |
| `go.mod` + `github.com/labstack/echo` | Go / Echo |
| `go.mod` + `github.com/go-chi/chi` | Go / Chi |
| `Gemfile` + `rails` gem | Ruby on Rails |
| `package.json` + `express` | Node.js / Express |
| `package.json` + `fastify` | Node.js / Fastify |
| `requirements.txt`/`pyproject.toml` + `fastapi` | Python / FastAPI |
| `requirements.txt`/`pyproject.toml` + `flask` | Python / Flask |
