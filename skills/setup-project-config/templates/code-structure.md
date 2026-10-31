# Code Structure

Read by `sync-api-spec`. Re-run `setup-project-config code-structure` after a framework or layout change.

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
