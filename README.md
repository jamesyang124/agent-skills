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

### Quick Start with Gemini CLI

To install all available skills for Gemini CLI using the automated script:

```bash
./.agent-settings/skills/import-skills.sh gemini
```

This will create necessary symlinks (e.g., `~/.gemini/skills/skill-name`) and ensure skills are hot-reloaded without restarting your agent.

### Quick Start with Atlassian MCP

To set up Atlassian Jira and Confluence integration via the MCP server:

```bash
./.agent-settings/mcps/install-atlassian-mcp.sh
```

For detailed instructions, refer to the [MCP Setup Guide](.agent-settings/mcps/README.md).

### Compatibility

The `SKILL.md` format is compatible with:
- **Claude Code** ✓
- **Gemini CLI** ✓
- **ChatGPT CLI tools** ✓
- **Antigravity** ✓ (maps to `.agent/skills/`)

## Available Skills

This project provides a collection of specialized skills to enhance your AI agent's capabilities. Skills are organized by workflow area.

### Git Workflow

*   **generate-pr-notes** — Interactively generates comprehensive pull request descriptions from git changes. Asks for scope (single commit vs. full branch), base branch, and optional Jira ticket ID, then produces a ready-to-paste markdown PR description with title, summary, categorized changes, technical details, and breaking changes.
    [View Details](.agent-settings/skills/tools/generate-pr-notes/SKILL.md)

*   **git-commit-conventional-strict** — Strict Conventional Commits generator optimized for `git-cliff` changelog automation. Analyzes staged changes, selects the correct type (`feat`, `fix`, `refactor`, etc.) with SemVer mapping, adds gitmoji, and writes the commit. Automatically detects when spec/doc changes and implementation changes are mixed and splits them into two commits (docs first, implementation second).
    [View Details](.agent-settings/skills/tools/git-commit-conventional-strict/SKILL.md)

### API Documentation

*   **api-spec-to-confluence** — Reads a Go API handler (router + handler code + Swagger annotations) for a given endpoint path and creates or updates a structured Confluence page following a standard documentation template. Covers HTTP method, auth, request/response params, JSON examples, error codes, and implementation details. Requires the Atlassian MCP server.
    [View Details](.agent-settings/skills/tools/api-spec-to-confluence/SKILL.md)

### Spec-Driven Development (SDD) Workflow

These skills integrate with [spec-kit](https://github.com/github/spec-kit) to automate handoffs across the SDD lifecycle. See the [SDD Workflow Guide](docs/sdd-workflow-spec-kit-native.md) for the full picture.

```
[PO writes PRD in Confluence]
        │
        ▼ confluence-prd-to-sdd-spec      ← Phase 1: PO → RD handoff
[spec-kit specify → spec.md]
        │
        ▼ (spec-kit plan)
[plan.md + requirements.md]
        │
        ▼ sdd-tech-plan-to-confluence     ← Phase 4: Plan → Design Review
[Confluence design review page]
        │
        ▼ confluence-tech-plan-to-jira    ← Phase 5: Design → Jira backlog
[Jira root ticket + subtasks]
        │
        ▼ (spec-kit implement → PR)
[PR created]
        │
        ▼ sdd-qa-to-jira                 ← Phase 8: Implement → QA hand-off
[Jira QA sub-tickets (BDD scenarios)]
```

*   **confluence-prd-to-sdd-spec** — Fetches a PRD written by a PO/PM from Confluence and transforms it into a clean local `prd-source.md` file structured for `spec-kit specify`. Faithfully maps PRD sections (Problem Statement, Goals, User Stories, Functional/Non-Functional Requirements, Constraints) without adding opinions, marking any gaps as `[TBD]` for the RD to resolve during the specify session. Requires the Atlassian MCP server.
    [View Details](.agent-settings/skills/workflows/confluence-prd-to-sdd-spec/SKILL.md)

*   **sdd-tech-plan-to-confluence** — Reads local spec-kit artifacts (`spec.md`, `plan.md`, `requirements.md`) and publishes a structured design review page to Confluence. The Confluence page is a read-only shared view for team feedback — source files remain the source of truth. Supports first-publish (Draft) and re-publish (appends revision history row). Requires the Atlassian MCP server.
    [View Details](.agent-settings/skills/workflows/sdd-tech-plan-to-confluence/SKILL.md)

*   **confluence-tech-plan-to-jira** — Fetches a Confluence design review or tech spec page and automatically creates a structured Jira root ticket (Story) with associated sub-tasks. Proposes topic/component brackets, confirms settings interactively, then bulk-creates the ticket hierarchy. Requires the Atlassian MCP server.
    [View Details](.agent-settings/skills/workflows/confluence-tech-plan-to-jira/SKILL.md)

*   **sdd-qa-to-jira** — Reads all spec-kit artifacts in a feature folder (`spec.md`, `plan.md`, `requirements.md`, `prd-source.md`, and any other `*.md` files) and derives BDD QA scenarios (happy paths, edge cases, error paths, non-functional). Presents proposed scenarios to the RD for review, then creates QA sub-tickets under the existing root Jira ticket — no new root ticket is created. Posts a QA hand-off comment on the root ticket. Requires the Atlassian MCP server.
    [View Details](.agent-settings/skills/workflows/sdd-qa-to-jira/SKILL.md)

### Utilities

*   **symlink-worktree-ignored-files** — Interactively guides you to select a target git worktree, then symlinks all git-ignored files and directories (`.env`, `node_modules`, build artifacts, etc.) from the current worktree to the target. Useful for spinning up a new worktree without re-downloading heavy dependencies.
    [View Details](.agent-settings/skills/tools/symlink-worktree-ignored-files/SKILL.md)


## Agent Settings Management

The `.agent-settings` directory centralizes configurations, utilities, and resources for AI coding assistants. This enables sharing skills and Model Context Protocol (MCP) server configurations across agents like Claude Code and Gemini CLI.

*   **Skills Management**: Detailed guidance on importing, creating, and verifying skills.
    [View Skills README](.agent-settings/skills/README.md)
*   **Atlassian MCP Integration**: Setup instructions for integrating with Jira and Confluence via the MCP server.
    [View MCP Setup Guide](.agent-settings/mcps/README.md)

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
│   ├── skills/
│   │   ├── tools/               # Atomic, single-purpose skills
│   │   │   ├── git-commit-conventional-strict/
│   │   │   ├── generate-pr-notes/
│   │   │   ├── api-spec-to-confluence/
│   │   │   └── symlink-worktree-ignored-files/
│   │   ├── workflows/           # Multi-step, orchestrated pipeline skills
│   │   │   ├── confluence-prd-to-sdd-spec/
│   │   │   ├── sdd-tech-plan-to-confluence/
│   │   │   ├── confluence-tech-plan-to-jira/
│   │   │   └── sdd-qa-to-jira/
│   │   └── import-skills.sh     # Scans tools/ + workflows/, installs flat
│   └── mcps/                    # MCP server configurations
└── (AI Agent config folders)    # e.g., .gemini/, .claude/, .agent/
    └── skills/                  # Symlinked skills (flat, by skill name)
```

Skills are organized into `tools/` (atomic actions) and `workflows/` (orchestrated pipelines) in the source, but the installation output is always flat — agent-specific directories (e.g., `.claude/skills/`) contain symlinks directly by skill name.

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
2.  Create a skill directory with a `SKILL.md` file in the correct category under `.agent-settings/skills/tools/` or `.agent-settings/skills/workflows/`.
3.  Use `import-skills.sh` to symlink and test your skill.
4.  Commit and push your changes.

## License

See [LICENSE](LICENSE) file for details.
