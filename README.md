# Agent Skills

A collection of custom skills for Claude Code and compatible AI CLI tools.

## Skill Definition

Skills are Markdown files (`SKILL.md`) that enable AI agents to perform specific, repeatable tasks. They utilize a filesystem-based architecture for efficient context consumption.

### Structure

Each skill resides in its own directory:

```
skill-name/
└── SKILL.md  (uppercase)
```

### SKILL.md Format Requirements

- **File Name**: Must be `SKILL.md` (uppercase).
- **YAML Frontmatter**: Includes `name` (lowercase, hyphens for spaces) and `description` fields.

```yaml
---
name: skill-name
description: A clear description of what this skill does and when to use it
---

# Skill Name

[Instructions for the AI agent]
```

## Installation

Skills can be easily installed using the provided `import-skills.sh` script, which handles symlinking and setup for various AI agents. For detailed instructions on both automated and manual skill installation, please refer to the [Skills Management README](.agent-settings/skills/README.md).

### One-Command Setup (Skills + MCP)

To import skills and configure the Atlassian MCP server in a single step, use `setup.sh`:

```bash
./.agent-settings/setup.sh --agent claude --jira-url https://myteam.atlassian.net
```

| Option | Description |
|---|---|
| `--agent claude\|copilot` | Agent to configure (default: interactive prompt) |
| `--jira-url URL` | Pre-fills the Atlassian base URL, skipping the MCP interactive prompt |
| `--skip-mcp` | Import skills only; skip MCP setup entirely |

This is the recommended path when setting up a fresh clone. It chains `import-skills.sh` and the `install-atlassian-mcp` skill automatically.

### Quick Start with Atlassian MCP

To set up Atlassian Jira and Confluence integration, run the `install-atlassian-mcp` skill:

```
/install-atlassian-mcp
```

### Compatibility

The `SKILL.md` format is compatible with:
- **Claude Code** ✓
- **GitHub Copilot** ✓
- **ChatGPT CLI tools** ✓

## Available Skills

This project provides a collection of specialized skills to enhance your AI agent's capabilities. Skills are organized by workflow area.

### Knowledge Graph

*   **graphify-monitor** — Installs graphify, builds an initial knowledge graph of the current project, then spawns a background subagent that runs graphify auto-update every 120 seconds and prints newly-discovered symbols to the terminal. Use when monitoring a project for structural changes during active development by another coding agent. Supports a `stop` argument to terminate the background loop.
    [View Details](.agent-settings/skills/knowledge-graph/graphify-monitor/SKILL.md)

*   **btw** — Reads `graphify-out/graph.json` and appends a timestamped knowledge snapshot to `KNOWLEDGE_SUMMARY.md` in the project root. Entries are always appended, never overwritten — building a chronological evidence log of knowledge graph states. Run after `graphify-monitor` has built a graph to record what the graph currently knows.
    [View Details](.agent-settings/skills/knowledge-graph/btw/SKILL.md)

### Git Workflow

*   **generate-pr-notes** — Automatically generates comprehensive pull request descriptions from git changes. Analyzes commits or branch diffs and creates a ready-to-paste markdown PR description with title, summary, categorized changes, technical details, and breaking changes.
    [View Details](.agent-settings/skills/tools/generate-pr-notes/SKILL.md)

*   **git-commit-conventional-strict** — Strict Conventional Commits generator optimized for `git-cliff` changelog automation. Analyzes staged changes, selects the correct type (`feat`, `fix`, `refactor`, etc.) with SemVer mapping, and adds gitmoji. Automatically detects when spec/doc changes and implementation changes are mixed and splits them into two commits (docs first, implementation second).
    [View Details](.agent-settings/skills/tools/git-commit-conventional-strict/SKILL.md)

### Project Setup

*   **setup-project-config** — One-time setup skill that generates `.agent-settings/project-config.md` by scanning the codebase (language, framework, directory layout, API prefix, annotation style) and prompting for Confluence and Jira details. All Atlassian skills read from this shared config — run once per project, re-run after structural changes.
    [View Details](.agent-settings/skills/tools/setup-project-config/SKILL.md)

### MCP Installation

*   **install-atlassian-mcp** — Install and configure the Atlassian MCP server (Jira and Confluence) for Claude or GitHub Copilot agents. Supports uvx (recommended) and Docker methods.
    [View Details](.agent-settings/skills/tools/install-atlassian-mcp/SKILL.md)

*   **install-azure-devops-mcp** — Install and configure the Azure DevOps MCP server for Claude or GitHub Copilot agents. Covers work items, repos, pipelines, sprints, and wikis.
    [View Details](.agent-settings/skills/tools/install-azure-devops-mcp/SKILL.md)

*   **install-playwright-mcp** — Install and configure the Playwright browser-automation MCP server for Claude or GitHub Copilot agents.
    [View Details](.agent-settings/skills/tools/install-playwright-mcp/SKILL.md)

*   **install-sentry-mcp** — Install and configure the official Sentry MCP server for Claude or GitHub Copilot agents. Supports remote (OAuth, recommended) and local stdio (npx + access token) methods.
    [View Details](.agent-settings/skills/tools/install-sentry-mcp/SKILL.md)

### Azure DevOps

*   **ado-pr-code-review** — Security-focused code review on an Azure DevOps PR by URL. Posts inline LOC-level comments. Checks for PII exposure, missing input validation (XSS/injection), and error response structure. Requires the Azure DevOps MCP server.
    [View Details](.agent-settings/skills/tools/ado-pr-code-review/SKILL.md)

*   **ado-pr-resolve-comments** — Reads active review comments on an Azure DevOps PR and resolves them by applying suggested fixes with user consent. Trivial fixes shown as before/after diffs; non-trivial changes produce a refactoring plan for review. Companion to `ado-pr-code-review`. Requires the Azure DevOps MCP server.
    [View Details](.agent-settings/skills/tools/ado-pr-resolve-comments/SKILL.md)

*   **ado-open-pr** — Opens an Azure DevOps pull request for the current branch: pushes the branch, generates the description via `generate-pr-notes`, opens the PR against a target branch, and adds reviewers resolved from teams or explicit emails. By default also syncs drifted spec-kit/openspec docs to match the committed diff before opening the PR. Requires the Azure DevOps MCP server.
    [View Details](.agent-settings/skills/tools/ado-open-pr/SKILL.md)

### Spec-Driven Development (SDD) Workflow

These skills automate handoffs across the SDD lifecycle. See the [SDD Workflow Guide](docs/sdd-workflow-spec-kit-native.md) for the full picture.

```
[PO writes PRD in Confluence]
        │
        ▼ prd-to-sdd-spec              ← Phase 1: PO → RD handoff
[local prd-source.md]
        │
        ▼ (spec-kit / openspec specify + plan)
[spec.md + plan.md + requirements.md]
        │
        ▼ tech-plan-to-wiki            ← Phase 4: Plan → Design Review
[Confluence design review page]
        │
        ▼ tech-plan-to-ticket          ← Phase 5: Design → Jira backlog
[Jira root ticket + subtasks]
        │
        ▼ (spec-kit implement → PR)
[PR created]
        │
        ▼ sdd-qa-to-ticket             ← Phase 8: Implement → QA hand-off
[Jira QA sub-tickets (BDD scenarios)]
```

*   **prd-to-sdd-spec** — Fetches a PRD from Confluence or a Jira ticket that links to a PRD wiki, and transforms it into a structured local source file for `spec-kit specify` or `openspec`. Bridges the PO handoff into the SDD workflow. Requires the Atlassian MCP server.
    [View Details](.agent-settings/skills/workflows/prd-to-sdd-spec/SKILL.md)

*   **tech-plan-to-wiki** — Reads local spec-kit artifacts (`spec.md`, `plan.md`, `requirements.md`) and publishes a collaborative design review page to Confluence. Supports first-publish (Draft) and re-publish (appends revision history). Requires the Atlassian MCP server.
    [View Details](.agent-settings/skills/workflows/tech-plan-to-wiki/SKILL.md)

*   **tech-plan-to-ticket** — Fetches a Confluence design review or tech spec page and creates a Jira root ticket (Story) with associated subtasks, or adds subtasks to an existing Jira ticket. Requires the Atlassian MCP server.
    [View Details](.agent-settings/skills/workflows/tech-plan-to-ticket/SKILL.md)

*   **sdd-qa-to-ticket** — Reads local SDD artifacts and derives BDD QA scenarios (happy paths, edge cases, error paths, non-functional), then creates QA sub-tickets under the existing root Jira ticket. No new root ticket is created. Requires the Atlassian MCP server.
    [View Details](.agent-settings/skills/workflows/sdd-qa-to-ticket/SKILL.md)

*   **sdd-qa-to-jira** — Legacy spec-kit–specific variant of `sdd-qa-to-ticket`. Prefer `sdd-qa-to-ticket` for new projects.
    [View Details](.agent-settings/skills/workflows/sdd-qa-to-jira/SKILL.md)

*   **goal-checkpoint** — General-purpose goal tracking with automatic checkpoint/resume support. Commits current state and writes a `GOAL_STATE.md` snapshot when context usage approaches 90%, so the next session can restore and continue.
    [View Details](.agent-settings/skills/workflows/goal-checkpoint/SKILL.md)

*   **learn-resource** — Turns any resources (videos, course lessons, articles, chats) into per-resource study notes plus a merged master, read via ego-browser. Includes raw-source backup, Mermaid diagrams, clickable video timestamps and a render check.
    [View Details](.agent-settings/skills/workflows/learn-resource/SKILL.md)

### Utilities

*   **sync-api-spec** — Scans all API routes in the project and maintains `docs/agents/api-spec.md` — a machine-readable API reference for agents, frontend, and product. Incremental: only re-scans handlers for new or changed routes. Optional Confluence publish step after local file is written. Use at the Implement & PR phase of the SDD workflow.
    [View Details](.agent-settings/skills/tools/sync-api-spec/SKILL.md)

*   **symlink-worktree-ignored-files** — Guides you to select a target git worktree, then symlinks all git-ignored files and directories (`.env`, `node_modules`, build artifacts, etc.) from the current worktree to the target. Useful for spinning up a new worktree without re-downloading heavy dependencies.
    [View Details](.agent-settings/skills/tools/symlink-worktree-ignored-files/SKILL.md)

*   **sync-skills** — Syncs the local `.agents/skills` directory with the ClawHub registry. Detects which skills are not yet installed and installs them automatically.
    [View Details](.agent-settings/skills/tools/sync-skills/SKILL.md)

*   **spec-recalibrate** — Recalibrates a repo's spec-driven docs (spec-kit `specs/`, openspec `openspec/specs/`) against the code that now implements them: maps each spec to its code, classifies drift, and with consent updates stale spec docs to match the code — spec docs only, never the implementation.
    [View Details](.agent-settings/skills/tools/spec-recalibrate/SKILL.md)

*   **explain-diff-html** — Produces a rich HTML explanation of a code change, diff, branch, or PR.
    [View Details](.agent-settings/skills/tools/explain-diff-html/SKILL.md)

*   **agent-playtest** — Evidence-grounded simulated playtests of interactive web content (games, 3D worlds, galleries) with parallel browser subagents: closed-loop play, screenshot evidence, structured observed descriptions kept separate from declared metadata, screenshot audit, validation, human spot-check and reliability report. Browser-agnostic (ego-browser, Playwright, MCP browsers); includes a human-demo mode that records local mouse/keyboard to compare with the agent's attempt.
    [View Details](own-skills/agent-playtest/SKILL.md)

### Playground (Experimental)

*   **git-rebase-conflict-resolver** — Interactive git rebase conflict resolver with Dry-run, Progressive, and Auto modes. Dry-run predicts conflict paths without touching the branch. Progressive mode is interactive per-conflict. Auto mode resolves autonomously then presents an audit report for approval or rollback.
    [View Details](.agent-settings/skills/playground/git-rebase-conflict-resolver/SKILL.md)

*   **git-stale-branch-cleanup** — Scans remote origin branches behind the base branch, filters by staleness threshold, and generates a per-branch report with intent analysis and Jira detection. Optionally deletes remote branches and prunes local counterparts. Dry-run mode reports without deleting.
    [View Details](.agent-settings/skills/playground/git-stale-branch-cleanup/SKILL.md)

*   **install-external-skills** — Interactive multi-select installer for external agent skill registries. Reads `project-config.md` to recommend best-fit skills, fetches latest version info from GitHub, and installs selected skills via `npx`. Supports supabase/agent-skills, vercel-labs/agent-skills, and antonbabenko/terraform-skill.
    [View Details](.agent-settings/skills/playground/install-external-skills/SKILL.md)


## Agent Settings Management

The `.agent-settings` directory centralizes configurations, utilities, and resources for AI coding assistants. This enables sharing skills and Model Context Protocol (MCP) server configurations across agents like Claude Code and GitHub Copilot.

*   **Skills Management**: Detailed guidance on importing, creating, and verifying skills.
    [View Skills README](.agent-settings/skills/README.md)
*   **MCP Installation**: Use the `install-atlassian-mcp`, `install-azure-devops-mcp`, or `install-playwright-mcp` skills to set up MCP servers interactively.

## Spec-Driven Development (SDD) Integration

Learn how to integrate these agent skills and MCP tools with GitHub's Spec-Kit for a complete Spec-Driven Development workflow.

*   **Complete Workflow Guide**: Detailed workflow diagrams and integration architecture.
    [View SDD Workflow Guide](docs/sdd-workflow-spec-kit-native.md)
*   **Quick Reference**: Visual guide with examples and quick start commands.
    [View Quick Reference](docs/sdd-quick-reference.md)
*   **Skills Mapping**: Simple reference showing which skills to use at each SDD phase.
    [View Skills Map](docs/sdd-skills-map.md)

## Project Structure

```
.
├── .agent-settings/
│   ├── project-config.md        # Generated by setup-project-config (gitignored)
│   ├── skills/
│   │   ├── knowledge-graph/     # Knowledge graph skills
│   │   │   ├── btw/
│   │   │   └── graphify-monitor/
│   │   ├── playground/          # Experimental skills
│   │   │   ├── git-rebase-conflict-resolver/
│   │   │   ├── git-stale-branch-cleanup/
│   │   │   └── install-external-skills/
│   │   ├── tools/               # Atomic, single-purpose skills
│   │   │   ├── ado-open-pr/
│   │   │   ├── ado-pr-code-review/
│   │   │   ├── ado-pr-resolve-comments/
│   │   │   ├── api-spec-to-confluence/
│   │   │   ├── explain-diff-html/
│   │   │   ├── generate-pr-notes/
│   │   │   ├── git-commit-conventional-strict/
│   │   │   ├── install-atlassian-mcp/
│   │   │   ├── install-azure-devops-mcp/
│   │   │   ├── install-playwright-mcp/
│   │   │   ├── install-sentry-mcp/
│   │   │   ├── setup-project-config/
│   │   │   ├── spec-recalibrate/
│   │   │   ├── symlink-worktree-ignored-files/
│   │   │   ├── sync-api-spec/
│   │   │   └── sync-skills/
│   │   ├── workflows/           # Multi-step, orchestrated pipeline skills
│   │   │   ├── goal-checkpoint/
│   │   │   ├── learn-resource/
│   │   │   ├── prd-to-sdd-spec/
│   │   │   ├── sdd-qa-to-jira/
│   │   │   ├── sdd-qa-to-ticket/
│   │   │   ├── tech-plan-to-ticket/
│   │   │   └── tech-plan-to-wiki/
│   │   └── import-skills.sh     # Scans all subdirs, installs flat
│   └── mcps/                    # MCP server configurations
├── config/
│   └── reviewers.example.json   # Team → reviewer-email roster (used by ado-open-pr)
└── (AI Agent config folders)    # e.g., .claude/, .github/
    └── skills/                  # Symlinked skills (flat, by skill name)
```

Skills are organized by category (`knowledge-graph/`, `playground/`, `tools/`, `workflows/`) in the source, but the installation output is always flat — agent-specific directories (e.g., `.claude/skills/`) contain symlinks directly by skill name.

## Resources

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Official Skills Repository](https://github.com/anthropics/skills)
- [Skills Marketplace (SkillsMP)](https://skillsmp.com/) - 25,000+ skills
- [Awesome Claude Skills](https://github.com/travisvn/awesome-claude-skills)

## Contributing

To contribute a new skill:

1.  Determine the appropriate category for your skill:
    - **`tools/`** — atomic, single-purpose actions (e.g., generate a commit message, create a PR description)
    - **`workflows/`** — multi-step, orchestrated pipelines (e.g., fetch PRD → transform → publish to Confluence)
    - **`knowledge-graph/`** — skills that build or read knowledge graph artifacts
    - **`playground/`** — experimental skills not yet promoted to stable
2.  Create a skill directory with a `SKILL.md` file in the correct category under `.agent-settings/skills/<category>/`.
3.  Use `import-skills.sh` to symlink and test your skill.
4.  Commit and push your changes.

## License

See [LICENSE](LICENSE) file for details.
