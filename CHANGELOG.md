# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2026-03-06]

### Added
- `CHANGELOG.md` — this file
- `git-commit-conventional-strict`: optional Jira ticket prompt — agent now asks for a ticket
  number to append as `Refs: #TICKET` in the commit footer; skippable with `n`

### Changed

#### Skills restructured into `tools/` and `workflows/` subdirectories
Skills are now organized by category under `.agent-settings/skills/`:
- `tools/` — atomic, single-purpose skills (`generate-pr-notes`, `git-commit-conventional-strict`, `api-spec-to-confluence`, `symlink-worktree-ignored-files`)
- `workflows/` — multi-step, orchestrated pipeline skills (`confluence-prd-to-sdd-spec`, `sdd-tech-plan-to-confluence`, `confluence-tech-plan-to-jira`, `sdd-qa-to-jira`)

Installation output remains flat — agent skill directories (e.g. `.claude/skills/`) still contain symlinks directly by skill name.

#### Codex CLI support removed
Codex CLI is no longer a supported agent. Affected changes:
- `import-skills.sh` — now exits with an error if invoked with `codex`
- `install-atlassian-mcp.sh` — removed `codex` from the interactive agent menu and `--agent` flag; removed the TOML config generation block
- Documentation updated across `.agent-settings/README.md`, `.agent-settings/mcps/README.md`

#### Interactive prompts standardized across all skills
All skills now use explicit typed-response hints instead of implied press-Enter patterns:
- Skippable inputs: "Type the value or type `n` to skip"
- Defaults: "Type the value or type `n` to use `[default]`"
- Confirmations: "Type `y` to confirm, or describe changes to make first"

Affected skills: `generate-pr-notes`, `confluence-prd-to-sdd-spec`,
`sdd-tech-plan-to-confluence`, `sdd-qa-to-jira`, `api-spec-to-confluence`,
`confluence-tech-plan-to-jira`

#### `generate-pr-notes`: improved no-ticket handling
- Accepts more inputs as "no ticket": `n`, `no`, `none`, `skip`, `-`
- Commit bodies now use bullet lists when multiple points are needed

#### Documentation updates
- All "View Details" skill links in `README.md` updated to include the `tools/` or `workflows/` path prefix
- Manual symlink examples in `.agent-settings/skills/README.md` updated to include category subdirectory
- "Available Skills" list in `.agent-settings/skills/README.md` expanded from 2 to all 8 skills, grouped by category
- Contributing section in `README.md` updated to explain `tools/` vs `workflows/` placement
- Broken reference link in `docs/sdd-workflow-spec-kit-native.md` fixed (`workflows/sdd-tech-plan-to-confluence`)
