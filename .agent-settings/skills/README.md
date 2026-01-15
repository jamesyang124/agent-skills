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
├── generate-pr-notes/
│   └── SKILL.md
├── git-commit-conventional-strict/
│   └── SKILL.md
├── code-review/
│   └── SKILL.md
├── frontend-design/
│   └── SKILL.md
└── keybindings-help/
    └── SKILL.md

.claude/skills/
├── generate-pr-notes -> ../../.agent-settings/skills/generate-pr-notes
├── git-commit-conventional-strict -> ../../.agent-settings/skills/git-commit-conventional-strict
└── code-review -> ../../.agent-settings/skills/code-review

.cursor/skills/
└── generate-pr-notes -> ../../.agent-settings/skills/generate-pr-notes

.gemini/skills/
└── frontend-design -> ../../.agent-settings/skills/frontend-design
```

### Creating Skill Symlinks

#### Automated Import (Recommended)

Use the `import-skills.sh` script to automatically create symlinks:

```bash
# Import all skills to an agent
.agent-settings/skills/import-skills.sh claude

# Import specific skills to an agent
.agent-settings/skills/import-skills.sh claude generate-pr-notes git-commit-conventional-strict

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

##### For Claude Agent

```bash
# Create skills directory if it doesn't exist
mkdir -p .claude/skills

# Link a skill from .agent-settings to .claude
ln -s ../../.agent-settings/skills/generate-pr-notes .claude/skills/generate-pr-notes
ln -s ../../.agent-settings/skills/git-commit-conventional-strict .claude/skills/git-commit-conventional-strict
```

##### For Gemini Agent

```bash
# Create skills directory if it doesn't exist
mkdir -p .gemini/skills

# Link a skill from .agent-settings to .gemini
ln -s ../../.agent-settings/skills/generate-pr-notes .gemini/skills/generate-pr-notes
```

##### For Other Agents

```bash
# Generic pattern for any agent folder
mkdir -p .{agent-name}/skills
ln -s ../../.agent-settings/skills/{skill-name} .{agent-name}/skills/{skill-name}
```

### Adding New Skills

1. Create the skill in `.agent-settings/skills/`:
   ```bash
   mkdir -p .agent-settings/skills/my-new-skill
   # Create SKILL.md or other skill files
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
   ln -s ../../.agent-settings/skills/my-new-skill .claude/skills/my-new-skill
   ln -s ../../.agent-settings/skills/my-new-skill .gemini/skills/my-new-skill
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
# Should output: ../../.agent-settings/skills/generate-pr-notes
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

- **generate-pr-notes** - Automates generation of pull request notes from commit history
- **git-commit-conventional-strict** - Enforces strict conventional commit message formatting

---

For more information about specific skills, refer to the `SKILL.md` file within each skill directory.
