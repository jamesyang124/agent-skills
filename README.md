# Agent Skills

A collection of custom skills for Claude Code and compatible AI CLI tools.

## What are Skills?

Skills are markdown files that teach AI agents how to perform specific, repeatable tasks. They use a filesystem-based architecture with progressive disclosure, consuming minimal context (~100 tokens during scanning, <5k when active).

## Skill Structure

Each skill must follow this structure:

```
skill-name/
└── SKILL.md  (uppercase)
```

### SKILL.md Format

```yaml
---
name: skill-name
description: A clear description of what this skill does and when to use it
---

# Skill Name

[Instructions for the AI agent]

## Usage
...

## Examples
...
```

**Required:**
- File must be named `SKILL.md` (uppercase)
- YAML frontmatter with `name` and `description` fields
- `name` should be lowercase with hyphens for spaces

## Installation

### For Claude Code

Create a symlink to make skills available across all projects:

```bash
# Create skills directory if it doesn't exist
mkdir -p ~/.claude/skills

# Symlink your skill
ln -s /path/to/agent-skills/skill-name ~/.claude/skills/skill-name
```

Example:
```bash
ln -s /Users/murcurial/Coding/agent-skills/generate-pr-notes ~/.claude/skills/generate-pr-notes
```

With Claude Code 2.1.0+, skills are automatically hot-reloaded without restart.

### For Other CLI Tools

The SKILL.md format is compatible with:
- **Claude Code** ✓
- **Codex CLI** ✓
- **Gemini CLI** (if it supports the skill format)
- **ChatGPT CLI tools** ✓

Check each tool's documentation for their skills directory location and create similar symlinks.

## Available Skills

### generate-pr-notes

Automatically generates comprehensive pull request notes based on git changes.

**Usage:** `/generate-pr-notes`

**Features:**
- Analyzes commits or branch diffs
- Creates structured PR descriptions with:
  - Summary (why and business value)
  - Changes organized by category (features, bug fixes, refactoring, etc.)
  - Technical details
  - Testing steps
  - Breaking changes (if applicable)

## Directory Structure

```
~/.claude/
└── skills/              # Personal skills (symlinks)
    └── generate-pr-notes -> /path/to/agent-skills/generate-pr-notes

.claude/
└── skills/              # Project-level skills (optional)
```

**Personal vs Project Skills:**
- `~/.claude/skills/` - Available across all your projects
- `.claude/skills/` - Project-specific, can be shared with team

## Resources

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Official Skills Repository](https://github.com/anthropics/skills)
- [Skills Marketplace (SkillsMP)](https://skillsmp.com/) - 25,000+ skills
- [Awesome Claude Skills](https://github.com/travisvn/awesome-claude-skills)

## Contributing

To add a new skill to this repository:

1. Create a new directory with your skill name (lowercase-with-hyphens)
2. Add a `SKILL.md` file with proper frontmatter
3. Symlink it to your `~/.claude/skills/` directory
4. Test the skill with `/skill-name`
5. Commit and push

## License

See [LICENSE](LICENSE) file for details.
