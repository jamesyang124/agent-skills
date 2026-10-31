# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### ⚠️ Breaking: repo restructured around `npx skills add`

This repo is now a plain skill catalog, installed the same way as other public skill repos
([vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills),
[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills),
[mattpocock/skills](https://github.com/mattpocock/skills)) instead of from a local clone with
`.agent-settings/` scripts. Each choice is copied from the repo that does it best:

| Area | Before | Now | Follows |
|------|--------|-----|---------|
| Install | clone the repo, run `.agent-settings/skills/import-skills.sh` or `setup.sh` (symlinks) | `npx skills add jamesyang124/agent-skills [-g] [--skill <name>]`; update with `npx skills update -g`. Also installable as a Claude Code plugin (`.claude-plugin/`) | [vercel-labs/skills](https://github.com/vercel-labs/skills) CLI |
| Layout | `.agent-settings/skills/{tools,workflows,playground,…}/<name>/`, vendored `external/` copies | flat `skills/<name>/SKILL.md`; external skills are listed in the README, not copied | addyosmani/agent-skills |
| Skill format | mixed frontmatter, no checks | [docs/skill-anatomy.md](docs/skill-anatomy.md): spec keys only (plus Claude Code's `argument-hint`, `disable-model-invocation`), "Use when ..." descriptions, enforced by `scripts/validate-skills.sh` in CI | addyosmani/agent-skills |
| Per-project settings | one git-ignored `.agent-settings/project-config.md` per developer | `docs/agents/<topic>.md` committed in each project (shared by the team) plus an `## Agent skills` pointer in `CLAUDE.md`/`AGENTS.md`, written by `/setup-project-config` | mattpocock/skills (`setup-matt-pocock-skills`) |

Rule of thumb: keep a skill only if a current model or the agent itself does not already do the job
reliably. Removed on that basis: `graphify`/`btw`, the playground skills, `symlink-worktree-ignored-files`,
`sync-skills`, `goal-checkpoint` and `sdd-qa-to-jira` (see Removed).

**Migrating an existing setup**
1. Remove old symlinked copies (`~/.claude/skills/<name>` pointing into a clone), then
   `npx skills add jamesyang124/agent-skills -g`.
2. In each project, run `/setup-project-config`; it converts `.agent-settings/project-config.md` to
   `docs/agents/*.md` and offers to delete the old file.
3. Projects that vendored this repo as an ignored `agent-skills/` clone (listed in `.gitmodules`, linked through a
   `.agent-settings` symlink and `.claude/skills/*` links) can delete the clone, the symlink, the stale links and the
   `.gitmodules` entry.

### Added
- `scripts/validate-skills.sh` and `.github/workflows/validate-skills.yml`: CI checks frontmatter keys, name = folder, the install line, "Use when" descriptions (max 1024 chars), relative links in skills, README and docs, and that the `skills` CLI finds every skill; warns on SKILL.md over 500 lines
- `.claude-plugin/plugin.json` and `marketplace.json`: install every skill as one Claude Code plugin (`/plugin install agent-skills --marketplace jamesyang124/agent-skills`)
- `docs/skill-anatomy.md`: layout, frontmatter and per-project-settings rules for every skill
- `setup-project-config/templates/` (one seed file per topic) and `references/code-scan.md`
- `agent-playtest` — closed-loop agent playtests of web content → audited, evidence-cited observed descriptions; browser adapters, site profiles, human-demo recorder, validation / mismatch / spot-check scripts with a self-test
- `ado-open-pr` — pre-PR review (lint + lizard measurements, six clean-context reviewers, fixes with the user, review confidence with a complexity score), repo PR templates, existing-PR and preflight guards, optional Confluence release-notes entry
- `generate-pr-notes/references/pull_request_template.md` — one shared PR template with API impact (compatibility class per route), compatibility and constitution check, deploy notes, spec impact and tests
- `ado-pr-code-review/references/` — `branch-map.md` (PR target per repo) and `review-profile.md` (reviewers, lint and test commands per repo), with example rows

### Removed
- `sync-skills` (installed from a placeholder ClawHub registry; `npx skills add` / `npx skills update -g` cover it), `goal-checkpoint` (relied on the agent sensing ~90% context and committed `GOAL_STATE.md` into the repo; Claude Code's auto-compaction and plan skills cover it) and `sdd-qa-to-jira` (legacy duplicate of `sdd-qa-to-ticket`).
- `symlink-worktree-ignored-files`: Claude Code copies git-ignored files into new worktrees from a committed `.worktreeinclude` (gitignore syntax), which copies rather than symlinks, so worktrees no longer share one `node_modules`/`.venv`. The skill also created one symlink per file inside ignored folders (`git ls-files` without `--directory`) and never initialised submodules. For repos with submodules, put "after creating a worktree, run `git submodule update --init --recursive` in it" in `CLAUDE.md`.
- `.agent-settings/` (`setup.sh`, `skills/import-skills.sh`, `skills/README.md`, `README.md`): `npx skills add` and the Claude Code plugin replace them. Also `docs/agent-settings.md`, `docs/skills.md`, `docs/mcps.md` and the per-skill copies under `docs/tools/` and `docs/workflows/` (each skill's `SKILL.md` is its documentation).
- `playground/` skills `git-rebase-conflict-resolver` and `git-stale-branch-cleanup` (a current model handles both on request; the files stay in git history) and `install-external-skills` (its three registries do not match the stack and the `skills` CLI already installs interactively; the registry list moved to the README's Planned section). The now-empty `playground/` category is removed too, with the opt-in checkbox menu in `import-skills.sh` (`get_playground_skills`, `prompt_playground_skills` and its call) and every doc mention. `setup-project-config` no longer lists `install-external-skills` as a project-config consumer.
- `config/`: its only file, `reviewers.example.json`, moved to `ado-open-pr/references/pr-tools.example.json` (the schema of `.github/config/pr-tools.json`: `jiraBaseUrl`, `teams`, `releaseNotes`). `ado-open-pr` no longer reads a local `config/reviewers.json` fallback; the per-repo `.github/config/pr-tools.json` is the only source, and a missing file still degrades to explicit reviewer args.
- `external/` and `skills-lock.json`: all 14 vendored `mattpocock/skills` copies (`setup-matt-pocock-skills`, `caveman`, `to-prd`, `to-issues`, `triage`, `diagnose`, `improve-codebase-architecture`, `prototype`, `tdd`, `zoom-out`, `handoff`, `write-a-skill`, `grill-me`, `grill-with-docs`). Nothing in `.agent-settings/` used them and `import-skills.sh` never installed them. The issue-tracker skills (`to-prd`, `to-issues`, `triage`) depended on the setup skill and target GitHub/GitLab trackers. `grill-me` and `grill-with-docs` are listed under Planned in the README.
- `graphify-monitor`, `btw` (the whole `knowledge-graph/` category) and the external `graphify` skill, with their README and docs entries, the `skills-lock.json` entry, the `graphify-out/` and `KNOWLEDGE_SUMMARY.md` ignore rules and the `GOAL_STATE.md` verification record. `btw` only read graphify's output, so it could not work without it.

### Changed

Repo:
- **Install with `npx skills add jamesyang124/agent-skills`** (or the Claude Code plugin). Every skill's copy-install block is now one `npx skills add jamesyang124/agent-skills --skill <name> -g` line, and runtime paths are relative to the skill folder (`<skill-dir>/scripts/...`, `references/...`) so installed skills work outside this repo.
- **Flat layout `skills/<name>/`** (was `.agent-settings/skills/{tools,workflows}/<name>/`, plus `own-skills/`), as in addyosmani/agent-skills; the README groups skills by area instead.
- **Per-project settings moved from `.agent-settings/project-config.md` to `docs/agents/<topic>.md`** (`sdd.md`, `code-structure.md`, `atlassian.md`, `azure-devops.md`, `sentry.md`, `playwright.md`), following mattpocock/skills: `setup-project-config` (now user-invoked only) writes them plus an `## Agent skills` pointer block in `CLAUDE.md`/`AGENTS.md`, and migrates a legacy `project-config.md`. The files are meant to be committed. `sync-api-spec` requires `code-structure.md`; the other readers (`ado-open-pr`, `spec-recalibrate`, `tech-plan-to-wiki`, `tech-plan-to-ticket`, `sdd-qa-to-ticket`) use their file when present and fall back to detection or asking.
- README restructured: Quick Start (npx + plugin), per-project setup, all skills grouped by area, project structure, contributing. SDD guides point the Constitution phase at `setup-project-config` and no longer list `claude-mem`, which this repo never set up.
- `.gitignore`: ignores `skills-lock.json` and `.agents/` (created when the CLI installs into a checkout) and keeps `.github/workflows/`.

Skills:
- Every skill has an `## Install this skill` section and a description with a "Use when ..." trigger.
- `agent-playtest`: site profiles live in the consuming project at `docs/agents/playtest/<site>.md` (written from `templates/site-profile.md` on first run). The bundled example profile and site-specific wording were removed. `own-skills/agent-playtest` and `ado-pr-teams-notify` were rewritten to the repo conventions (the non-standard `trigger:` key is gone).
- `ado-open-pr`, `generate-pr-notes`, `sync-api-spec`: quote the `description` so the frontmatter is valid YAML (an unquoted `: ` made the `skills` CLI skip them).
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
