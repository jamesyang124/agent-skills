# Skills Directory

This directory contains shared skills that can be imported into different AI agent configurations (Claude, Cursor, Gemini, GitHub Copilot, etc.) using symbolic links.

## Overview

Skills are stored centrally in this directory (`.agent-settings/skills/`) and can be imported into specific agent configurations using symbolic links. This approach allows you to:

- Maintain a single source of truth for each skill
- Share skills across multiple agent configurations
- Update skills in one place and have changes reflected everywhere
- Reduce duplication and keep the repository clean

### Directory Structure

```
.agent-settings/skills/
├── README.md (this file)
├── import-skills.sh (skill management script)
├── knowledge-graph/
│   ├── btw/
│   │   └── SKILL.md
│   └── graphify-monitor/
│       └── SKILL.md
├── playground/
│   ├── git-rebase-conflict-resolver/
│   │   └── SKILL.md
│   ├── git-stale-branch-cleanup/
│   │   └── SKILL.md
│   └── install-external-skills/
│       └── SKILL.md
├── tools/
│   ├── ado-pr-code-review/
│   │   └── SKILL.md
│   ├── ado-pr-resolve-comments/
│   │   └── SKILL.md
│   ├── generate-pr-notes/
│   │   └── SKILL.md
│   ├── git-commit-conventional-strict/
│   │   └── SKILL.md
│   ├── install-atlassian-mcp/
│   │   └── SKILL.md
│   ├── install-azure-devops-mcp/
│   │   └── SKILL.md
│   ├── install-playwright-mcp/
│   │   └── SKILL.md
│   ├── setup-project-config/
│   │   └── SKILL.md
│   ├── symlink-worktree-ignored-files/
│   │   └── SKILL.md
│   └── sync-skills/
│       └── SKILL.md
└── workflows/
    ├── goal-checkpoint/
    │   └── SKILL.md
    ├── prd-to-sdd-spec/
    │   └── SKILL.md
    ├── sdd-qa-to-jira/
    │   └── SKILL.md
    ├── sdd-qa-to-ticket/
    │   └── SKILL.md
    ├── tech-plan-to-ticket/
    │   └── SKILL.md
    └── tech-plan-to-wiki/
        └── SKILL.md
```

### Creating Skill Symlinks

#### Automated Import (Recommended)

Use the `import-skills.sh` script to automatically create symlinks:

```bash
# Import all skills to Antigravity (targets .agent folder)
.agent-settings/skills/import-skills.sh agent

# Import all skills to Claude
.agent-settings/skills/import-skills.sh claude

# Import specific skills
.agent-settings/skills/import-skills.sh claude generate-pr-notes git-commit-conventional-strict

# Import to GitHub Copilot (alias for claude — uses .claude/skills/)
.agent-settings/skills/import-skills.sh copilot

# List available skills
.agent-settings/skills/import-skills.sh --list

# Verify existing symlinks
.agent-settings/skills/import-skills.sh --verify claude

# Prune orphaned skills (interactive)
.agent-settings/skills/import-skills.sh --prune claude
```

**Script Features:**
- Automatically creates necessary directories
- Validates skill existence before linking (searches tools/ and workflows/ subdirs)
- Detects and handles existing symlinks
- Provides colored output for easy status tracking
- Verifies symlinks after creation
- Prunes orphaned skill links

#### Manual Import

If you prefer to create symlinks manually:

```bash
# Create skills directory if it doesn't exist
mkdir -p .claude/skills

# Link a skill from .agent-settings to .claude
ln -s ../../.agent-settings/skills/tools/generate-pr-notes .claude/skills/generate-pr-notes
ln -s ../../.agent-settings/skills/tools/git-commit-conventional-strict .claude/skills/git-commit-conventional-strict
```

##### For GitHub Copilot

Copilot reads skills from `.claude/skills/` per project (and `~/.claude/skills` for personal skills), so `copilot` is an alias for `claude`:

```bash
# Import skills for Copilot (same as importing for Claude)
.agent-settings/skills/import-skills.sh copilot

# Verify
.agent-settings/skills/import-skills.sh --verify copilot
```

**Invocation:** In Copilot Chat, type `#` to reference a skill from `.claude/skills/`.

### Available Skills

#### Knowledge Graph

- **btw** — Appends a timestamped knowledge snapshot from `graphify-out/graph.json` to `KNOWLEDGE_SUMMARY.md`. Append-only evidence log.
- **graphify-monitor** — Installs graphify, builds an initial knowledge graph, then runs auto-update every 120 seconds in a background subagent. Supports `stop` argument.

#### Tools

- **setup-project-config** — One-time setup that generates `.agent-settings/project-config.md`. Run before using any Atlassian or ADO skills.
- **generate-pr-notes** — Automatically generates comprehensive pull request notes based on git changes.
- **git-commit-conventional-strict** — Strict Conventional Commits generator optimized for git-cliff, with SemVer, Emoji, and commit-splitting support.
- **install-atlassian-mcp** — Install and configure the Atlassian MCP server (Jira/Confluence) for Claude, Copilot, or Gemini.
- **install-azure-devops-mcp** — Install and configure the Azure DevOps MCP server.
- **install-playwright-mcp** — Install and configure the Playwright browser-automation MCP server.
- **ado-pr-code-review** — Security-focused inline code review on an Azure DevOps PR. Requires Azure DevOps MCP.
- **ado-pr-resolve-comments** — Resolves active review comments on an Azure DevOps PR with user consent. Requires Azure DevOps MCP.
- **symlink-worktree-ignored-files** — Symlinks git-ignored files from source worktree to a target worktree.
- **sync-skills** — Syncs local `.agents/skills` with the ClawHub registry, installing only missing skills.

#### Workflows (SDD)

- **prd-to-sdd-spec** — Fetches a PRD from Confluence or Jira and transforms it into a local SDD source file.
- **tech-plan-to-wiki** — Reads local spec-kit artifacts and publishes a technical design review page to Confluence.
- **tech-plan-to-ticket** — Analyzes a Confluence page and creates a Jira root ticket with associated subtasks.
- **sdd-qa-to-ticket** — Reads local SDD artifacts, derives BDD QA scenarios, and creates QA sub-tickets under the Jira root ticket.
- **sdd-qa-to-jira** — Legacy spec-kit–specific variant of `sdd-qa-to-ticket`.
- **goal-checkpoint** — Goal tracking with automatic checkpoint/resume. Commits state and writes `GOAL_STATE.md` near context limit.

#### Playground (Experimental)

- **git-rebase-conflict-resolver** — Dry-run / Progressive / Auto modes for resolving git rebase conflicts. All modes generate a report.
- **git-stale-branch-cleanup** — Scans and optionally deletes stale remote branches with intent analysis and Jira detection.
- **install-external-skills** — Interactive installer for external skill registries (supabase, vercel-labs, terraform).

### Adding New Skills

1. Create the skill in the appropriate subdirectory:
   ```bash
   mkdir -p .agent-settings/skills/tools/my-new-skill
   # Create SKILL.md
   ```

2. Import it to the desired agent configurations:
   ```bash
   .agent-settings/skills/import-skills.sh claude my-new-skill
   ```

### Best Practices

1. **Always create skills in `.agent-settings/skills/`** — This is the single source of truth
2. **Use `tools/` for standalone utilities and `workflows/` for multi-step SDD processes**
3. **Run `setup-project-config` first** before using any Atlassian (Confluence/Jira) skills
4. **Use relative paths** — Use `../` to ensure symlinks work across different environments
5. **Document your skills** — Each skill should have clear documentation in its SKILL.md file

---

For more information about specific skills, refer to the `SKILL.md` file within each skill directory.
