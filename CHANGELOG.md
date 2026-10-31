# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- `.claude-plugin/plugin.json` and `marketplace.json`: install every skill as one Claude Code plugin (`/plugin install agent-skills --marketplace jamesyang124/agent-skills`)
- `docs/skill-anatomy.md`: layout, frontmatter and per-project-settings rules for every skill
- `setup-project-config/templates/` (one seed file per topic) and `references/code-scan.md`
- `agent-playtest` — closed-loop agent playtests of web content → audited, evidence-cited observed descriptions; browser adapters, site profiles (VIVERSE example), human-demo recorder, validation / mismatch / spot-check scripts with a self-test
- `ado-open-pr` — pre-PR review (lint + lizard measurements, six clean-context reviewers, fixes with the user, review confidence with a complexity score), repo PR templates, existing-PR and preflight guards, optional Confluence release-notes entry
- `generate-pr-notes/references/pull_request_template.md` — one shared PR template with API impact (compatibility class per route), compatibility and constitution check, deploy notes, spec impact and tests
- `ado-pr-code-review/references/` — `branch-map.md` (PR target per repo) and `review-profile.md` (reviewers, lint and test commands per repo), with example rows

### Removed
- `.agent-settings/` (`setup.sh`, `skills/import-skills.sh`, `skills/README.md`, `README.md`): `npx skills add` and the Claude Code plugin replace them. Also `docs/agent-settings.md`, `docs/skills.md`, `docs/mcps.md` and the per-skill copies under `docs/tools/` and `docs/workflows/` (each skill's `SKILL.md` is its documentation).
- `playground/` skills `git-rebase-conflict-resolver` and `git-stale-branch-cleanup` (a current model handles both on request; the files stay in git history) and `install-external-skills` (its three registries do not match the stack and the `skills` CLI already installs interactively; the registry list moved to the README's Planned section). The now-empty `playground/` category is removed too, with the opt-in checkbox menu in `import-skills.sh` (`get_playground_skills`, `prompt_playground_skills` and its call) and every doc mention. `setup-project-config` no longer lists `install-external-skills` as a project-config consumer.
- `config/`: its only file, `reviewers.example.json`, moved to `ado-open-pr/references/pr-tools.example.json` (the schema of `.github/config/pr-tools.json`: `jiraBaseUrl`, `teams`, `releaseNotes`). `ado-open-pr` no longer reads a local `config/reviewers.json` fallback; the per-repo `.github/config/pr-tools.json` is the only source, and a missing file still degrades to explicit reviewer args.
- `external/` and `skills-lock.json`: all 14 vendored `mattpocock/skills` copies (`setup-matt-pocock-skills`, `caveman`, `to-prd`, `to-issues`, `triage`, `diagnose`, `improve-codebase-architecture`, `prototype`, `tdd`, `zoom-out`, `handoff`, `write-a-skill`, `grill-me`, `grill-with-docs`). Nothing in `.agent-settings/` used them and `import-skills.sh` never installed them. The issue-tracker skills (`to-prd`, `to-issues`, `triage`) depended on the setup skill and target GitHub/GitLab trackers. `grill-me` and `grill-with-docs` are listed under Planned in the README.
- `graphify-monitor`, `btw` (the whole `knowledge-graph/` category) and the external `graphify` skill, with their README and docs entries, the `skills-lock.json` entry, the `graphify-out/` and `KNOWLEDGE_SUMMARY.md` ignore rules and the `GOAL_STATE.md` verification record. `btw` only read graphify's output, so it could not work without it.

### Changed
- **Flat layout `skills/<name>/`** (was `skills/{tools,workflows}/<name>/`), as in addyosmani/agent-skills; the README groups skills by area instead.
- **Per-project settings moved from `.agent-settings/project-config.md` to `docs/agents/<topic>.md`** (`sdd.md`, `code-structure.md`, `atlassian.md`, `azure-devops.md`, `sentry.md`, `playwright.md`), following mattpocock/skills: `setup-project-config` (now user-invoked only) writes them plus an `## Agent skills` pointer block in `CLAUDE.md`/`AGENTS.md`, and migrates a legacy `project-config.md`. The files are meant to be committed. `sync-api-spec` requires `code-structure.md`; the other readers (`ado-open-pr`, `spec-recalibrate`, `tech-plan-to-wiki`, `tech-plan-to-ticket`, `sdd-qa-to-ticket`) use their file when present and fall back to detection or asking.
- Descriptions of `agent-playtest`, `goal-checkpoint`, `prd-to-sdd-spec`, `sdd-qa-to-jira`, `sdd-qa-to-ticket`, `sync-api-spec`, `tech-plan-to-wiki` state their trigger as "Use when ...".
- `sdd-qa-to-jira` points to the `install-atlassian-mcp` skill instead of the deleted `.agent-settings/mcps/install-atlassian-mcp.sh`.
- README restructured: Quick Start (npx + plugin), per-project setup, all skills grouped by area, project structure, contributing.
- **Install with `npx skills add jamesyang124/agent-skills`.** Skills moved from `.agent-settings/skills/{tools,workflows}/` to the top-level `skills/{tools,workflows}/`, the catalog layout the open `skills` CLI discovers. The CLI now finds all 23 skills; before, it fell back to a deep scan and skipped three.
- `ado-open-pr`, `generate-pr-notes`, `sync-api-spec`: quote the `description` so the frontmatter is valid YAML (an unquoted `: ` made the `skills` CLI skip them).
- Every skill's copy-install block (`cp <agent-settings-repo>/.agent-settings/skills/...`) is now one `npx skills add jamesyang124/agent-skills --skill <name> -g` line. Runtime paths are relative to the skill folder (`<skill-dir>/scripts/install.sh`, `references/...`) so installed skills work outside this repo; `symlink-worktree-ignored-files/scripts/run_skill.sh` calls `symlink.sh` next to itself (its old path was already broken).
- `import-skills.sh` and `setup.sh` read skills from `skills/`; both are legacy and stay until the `npx` install has fully replaced them. README install section is `npx`-first; project trees regenerated from the real folders (the old README tree listed a missing `api-spec-to-confluence`).
- `.gitignore`: `skills-lock.json` and `.agents/`, which the CLI creates when it installs into a project.
- `own-skills/` removed: `agent-playtest` and `ado-pr-teams-notify` moved to `.agent-settings/skills/tools/` and rewritten to the tools conventions (short description, `argument-hint`, When to Use and Arguments sections; the non-standard `trigger:` key is gone). `import-skills.sh` only discovers skills under `.agent-settings/skills/<category>/`, so both now install like every other skill (project, `--global`, `--dedup`). The 2026-10-03 entry below keeps the old path as history.
- `import-skills.sh` — `--global` installs into `~/.<agent>/skills`; every install checks for skills installed both globally and in the project and cleans them in one step (`--dedup`, `--yes`, `--pick`, `--project`); `--no-color` is accepted
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
