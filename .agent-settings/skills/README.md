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
├── tools/
│   ├── generate-pr-notes/
│   │   └── SKILL.md
│   ├── git-commit-conventional-strict/
│   │   └── SKILL.md
│   ├── sync-api-spec/
│   │   ├── SKILL.md
│   │   └── references/api-spec-format.md
│   ├── setup-project-config/
│   │   ├── SKILL.md
│   │   └── README.md
│   └── symlink-worktree-ignored-files/
│       ├── SKILL.md
│       └── run_skill.sh
└── workflows/
    ├── prd-to-sdd-spec/
    │   └── SKILL.md
    ├── tech-plan-to-wiki/
    │   └── SKILL.md
    ├── tech-plan-to-ticket/
    │   └── SKILL.md
    └── sdd-qa-to-ticket/
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

#### Tools

- **setup-project-config** — One-time setup that generates `.agent-settings/project-config.md`. Run this first before using any Atlassian skills.
- **generate-pr-notes** — Automatically generates comprehensive pull request notes based on git changes.
- **git-commit-conventional-strict** — Strict Conventional Commits generator optimized for git-cliff, with SemVer, Emoji, and commit-splitting support.
- **sync-api-spec** — Scans all API routes and maintains `docs/agents/api-spec.md`. Incremental: only re-scans handlers for new or changed routes. Optional Confluence publish.
- **symlink-worktree-ignored-files** — Symlinks git-ignored files from source worktree to a target worktree.

#### Workflows (SDD)

- **prd-to-sdd-spec** — Fetches an external PRD from Confluence or Jira and transforms it into a local SDD source file.
- **tech-plan-to-wiki** — Reads local spec-kit artifacts and publishes a technical design review page to Confluence.
- **tech-plan-to-ticket** — Analyzes a Confluence page and automatically creates a Jira root ticket with associated subtasks.
- **sdd-qa-to-ticket** — Reads local spec-kit artifacts, derives BDD QA scenarios, and creates QA sub-tickets under the Jira root ticket.

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
