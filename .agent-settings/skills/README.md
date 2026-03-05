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
├── tools/                          # Atomic, single-purpose skills
│   ├── generate-pr-notes/
│   │   └── SKILL.md
│   ├── git-commit-conventional-strict/
│   │   └── SKILL.md
│   ├── api-spec-to-confluence/
│   │   └── SKILL.md
│   └── symlink-worktree-ignored-files/
│       └── SKILL.md
└── workflows/                      # Multi-step, orchestrated pipeline skills
    ├── confluence-prd-to-sdd-spec/
    │   └── SKILL.md
    ├── sdd-tech-plan-to-confluence/
    │   └── SKILL.md
    ├── confluence-tech-plan-to-jira/
    │   └── SKILL.md
    └── sdd-qa-to-jira/
        └── SKILL.md

# Installation output is always flat (by skill name, not category):
.agent/skills/
├── generate-pr-notes -> ../../.agent-settings/skills/tools/generate-pr-notes
└── sdd-qa-to-jira -> ../../.agent-settings/skills/workflows/sdd-qa-to-jira

.claude/skills/
├── generate-pr-notes -> ../../.agent-settings/skills/tools/generate-pr-notes
└── confluence-tech-plan-to-jira -> ../../.agent-settings/skills/workflows/confluence-tech-plan-to-jira
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
.agent-settings/skills/import-skills.sh agent generate-pr-notes git-commit-conventional-strict

# Import to multiple agents
.agent-settings/skills/import-skills.sh claude
.agent-settings/skills/import-skills.sh gemini

# List available skills
.agent-settings/skills/import-skills.sh --list

# Verify existing symlinks
.agent-settings/skills/import-skills.sh --verify claude
```

**Script Features:**
- Automatically creates necessary directories
- Validates skill existence before linking
- Detects and handles existing symlinks
- Provides colored output for easy status tracking
- Verifies symlinks after creation

#### Manual Import

If you prefer to create symlinks manually:

##### For Antigravity

```bash
# Create skills directory if it doesn't exist
mkdir -p .agent/skills

# Link a skill from .agent-settings to .agent
ln -s ../../.agent-settings/skills/tools/generate-pr-notes .agent/skills/generate-pr-notes
ln -s ../../.agent-settings/skills/tools/git-commit-conventional-strict .agent/skills/git-commit-conventional-strict
```

##### For Claude Agent

```bash
# Create skills directory if it doesn't exist
mkdir -p .claude/skills

# Link a skill from .agent-settings to .claude
ln -s ../../.agent-settings/skills/tools/generate-pr-notes .claude/skills/generate-pr-notes
ln -s ../../.agent-settings/skills/tools/git-commit-conventional-strict .claude/skills/git-commit-conventional-strict
```

##### For Gemini Agent

```bash
# Create skills directory if it doesn't exist
mkdir -p .gemini/skills

# Link a skill from .agent-settings to .gemini
ln -s ../../.agent-settings/skills/tools/generate-pr-notes .gemini/skills/generate-pr-notes
```

##### For GitHub Copilot

Copilot uses a different mechanism — flat agent files in `.github/agents/` instead of symlinks:

```bash
# Generate agent files and copilot-instructions.md
.agent-settings/skills/import-skills.sh copilot

# Import specific skills only
.agent-settings/skills/import-skills.sh copilot generate-pr-notes

# Verify generated agent files
.agent-settings/skills/import-skills.sh --verify copilot
```

This creates:
- `.github/agents/agent-settings.<skill>.agent.md` — VS Code-compatible agent instruction files
- `.github/copilot-instructions.md` — skills table with `@@skill-name` invocation syntax

**Invocation:** In Copilot Chat, type `@@` to browse available skills or `@@agent-settings.generate-pr-notes` to run one directly.

**Sharing:** Commit `.github/agents/` and `.github/copilot-instructions.md` to Git for team sharing.

##### For Other Agents

```bash
# Generic pattern for any agent folder (replace {category} with tools or workflows)
mkdir -p .{agent-name}/skills
ln -s ../../.agent-settings/skills/{category}/{skill-name} .{agent-name}/skills/{skill-name}
```

### Adding New Skills

1. Create the skill in the appropriate category:
   ```bash
   # For a single-purpose action:
   mkdir -p .agent-settings/skills/tools/my-new-skill
   # For an orchestrated pipeline:
   mkdir -p .agent-settings/skills/workflows/my-new-skill
   # Then create SKILL.md inside it
   ```

2. Import it to the desired agent configurations:

   **Using the automated script (recommended):**
   ```bash
   # Import the new skill to specific agents
   .agent-settings/skills/import-skills.sh claude my-new-skill
   .agent-settings/skills/import-skills.sh gemini my-new-skill

   # Or import all skills (including the new one)
   .agent-settings/skills/import-skills.sh claude
   ```

   **Or manually create symlinks:**
   ```bash
   ln -s ../../.agent-settings/skills/tools/my-new-skill .claude/skills/my-new-skill
   ln -s ../../.agent-settings/skills/tools/my-new-skill .gemini/skills/my-new-skill
   ```

### Verifying Symlinks

**Using the automated script (recommended):**

```bash
# Verify all symlinks for an agent
.agent-settings/skills/import-skills.sh --verify claude
```

**Or manually verify:**

```bash
# List symlinks in an agent's skills folder
ls -la .claude/skills

# Verify a specific symlink target
readlink .claude/skills/generate-pr-notes
# Should output: ../../.agent-settings/skills/tools/generate-pr-notes
```

### Best Practices

1. **Always create skills in `.agent-settings/skills/`** - This is the single source of truth
2. **Use relative paths** - Use `../` to ensure symlinks work across different environments
3. **Document your skills** - Each skill should have clear documentation in its SKILL.md file
4. **Test after linking** - Verify that agents can access the skills after creating symlinks
5. **Version control** - Commit both the skill files and symlinks to git

### Troubleshooting

#### Symlink not working

```bash
# Remove broken symlink
rm .claude/skills/skill-name

# Recreate with correct path
ln -s ../../.agent-settings/skills/skill-name .claude/skills/skill-name
```

#### Checking if a path is a symlink

```bash
file .claude/skills/skill-name
# Output should indicate "symbolic link to ../../.agent-settings/skills/skill-name"
```

### Available Skills

Current skills in `.agent-settings/skills/`:

**Tools** (atomic, single-purpose):
- **generate-pr-notes** - Interactively generates comprehensive pull request descriptions from git changes
- **git-commit-conventional-strict** - Strict Conventional Commits generator with gitmoji, optimized for `git-cliff`
- **api-spec-to-confluence** - Reads a Go API handler and creates/updates a structured Confluence documentation page
- **symlink-worktree-ignored-files** - Symlinks git-ignored files/directories from the current worktree to a target worktree

**Workflows** (multi-step, orchestrated pipelines):
- **confluence-prd-to-sdd-spec** - Fetches a PRD from Confluence and transforms it into a local `prd-source.md` for spec-kit
- **sdd-tech-plan-to-confluence** - Reads local spec-kit artifacts and publishes a structured design review page to Confluence
- **confluence-tech-plan-to-jira** - Fetches a Confluence design review page and creates a Jira root ticket with sub-tasks
- **sdd-qa-to-jira** - Derives BDD QA scenarios from spec-kit artifacts and creates QA sub-tickets in Jira

---

For more information about specific skills, refer to the `SKILL.md` file within each skill directory.
