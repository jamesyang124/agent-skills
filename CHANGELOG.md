# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- `own-skills/agent-playtest` — closed-loop agent playtests of web content → audited, evidence-cited observed descriptions; browser adapters, site profiles (VIVERSE example), human-demo recorder, validation / mismatch / spot-check scripts with a self-test
- `ado-open-pr` — pre-PR review (lint + lizard measurements, six clean-context reviewers, fixes with the user, review confidence with a complexity score), repo PR templates, existing-PR and preflight guards, optional Confluence release-notes entry
- `generate-pr-notes/references/pull_request_template.md` — one shared PR template with API impact (compatibility class per route), compatibility and constitution check, deploy notes, spec impact and tests
- `ado-pr-code-review/references/` — `branch-map.md` (PR target per repo) and `review-profile.md` (reviewers, lint and test commands per repo), with example rows

### Changed
- `ado-open-pr` — uses the consolidated Azure DevOps MCP tools; target branch comes from the branch map, then the ADO default branch (no hard-coded `develop`)
- `ado-pr-code-review` — adds commit provenance, runtime correctness and resource leaks, and standards / spec passes
- `generate-pr-notes` — fills the shared template; the global install copies the whole folder
- `ado-pr-code-review` — five passes (security, runtime, standards and spec, tests, impact outside the diff) with a second look for large or high-risk PRs, at most six sub-agents at once; the target's diff in conflicting files goes to the finders and the verifier; `--preview`, `--deep`, `--fast`; short comments with a `Reviewers:` line
- `ado-open-pr` — five reviewers (`minimal` absorbs `refactor`); after every review choose preview only / fix together / auto-fix / open anyway (`--choice`, `--fast`, `--yes`); merge-tree conflict warning with rebase-first advice; `scripts/complexity.py` with an approved lizard install
- `ado-pr-resolve-comments` — checks that each finding holds before fixing (outcome *not reproducible* with evidence), reads the short comment format, treats renames as non-trivial with a repo-wide impact check, runs lint and tests before pushing; `--auto-trivial`, `--fast`, `--yes`

## [2026-10-03]

### Added
- `own-skills/ado-pr-teams-notify` — Azure DevOps PR → Microsoft Teams channel notifications via one
  Power Automate flow (card per PR + one-line thread reply per event). Includes
  `scripts/gen_flow_definition.py` (builds the flow package from a template export), `ado_hooks.py`
  (Service Hook subscriptions via REST, PAT), `build_test_payloads.py` / `send_event.sh` (state-sequence
  tests), `backfill_pr.py`, and references for architecture, card spec, flow internals, ADO REST,
  browser adapters (ego-browser / Playwright / Chrome DevTools MCP), test plan and troubleshooting.

## [2026-03-06]

### Added
- `CHANGELOG.md` — this file
- `git-commit-conventional-strict`: optional Jira ticket prompt — agent now asks for a ticket
  number to append as `Refs: #TICKET` in the commit footer; skippable with `n`
- `setup-project-config` — new skill that scans the codebase and prompts for Confluence/Jira
  details, then writes `.agent-settings/project-config.md`; all Atlassian skills read from this
  shared config instead of relying on hardcoded placeholder values
- `.gitignore`: added `project-config.md` entry (generated per project, not committed to template repo)

### Updated
- `api-spec-to-confluence`: reads `project-config.md` at Step 0 (halts with setup reminder if
  missing); all hardcoded router paths, parent page IDs, and `example.atlassian.net` URLs removed

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
