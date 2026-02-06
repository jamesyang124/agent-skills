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
- **Codex CLI** ✓
- **Gemini CLI** ✓
- **ChatGPT CLI tools** ✓

## Available Skills

This project provides a collection of specialized skills to enhance your AI agent's capabilities. For detailed usage and features of each skill, refer to their respective `SKILL.md` files.

*   **generate-pr-notes**: Automatically generates comprehensive pull request notes based on git changes.
    [View Details](.agent-settings/skills/generate-pr-notes/SKILL.md)
*   **git-commit-conventional-strict**: A strict Conventional Commits generator optimized for git-cliff, supporting SemVer and Emoji.
    [View Details](.agent-settings/skills/git-commit-conventional-strict/SKILL.md)
*   **api-spec-to-confluence**: Creates or updates a Confluence page from an API endpoint by analyzing the router and handler code, using the documentation template in this skill folder.
    [View Details](.agent-settings/skills/api-spec-to-confluence/SKILL.md)
*   **symlink-worktree-ignored-files**: Symlink git-ignored files from source worktree to an existing target worktree. Handles ignored files, heavy directories (node_modules, vendor), and initializes submodules with shared git objects using --reference.
    [View Details](.agent-settings/skills/symlink-worktree-ignored-files/SKILL.md)


## Agent Settings Management

The `.agent-settings` directory centralizes configurations, utilities, and resources for AI coding assistants. This enables sharing skills and Model Context Protocol (MCP) server configurations across agents like Claude Code and Gemini CLI.

*   **Skills Management**: Detailed guidance on importing, creating, and verifying skills.
    [View Skills README](.agent-settings/skills/README.md)
*   **Atlassian MCP Integration**: Setup instructions for integrating with Jira and Confluence via the MCP server.
    [View MCP Setup Guide](.agent-settings/mcps/README.md)

## Project Structure

```
.
├── .agent-settings/               # Centralized agent configurations and resources
│   ├── skills/                  # Definitions for reusable AI agent skills
│   └── mcps/                    # Model Context Protocol (MCP) server configurations
└── (AI Agent config folders)      # e.g., .gemini/, .claude/, .codex/
    └── skills/                  # Symlinked skills for specific agents
```

Agent-specific skill directories (e.g., `~/.gemini/skills/`) contain symlinks to skills defined in `.agent-settings/skills/`.

## Resources

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Official Skills Repository](https://github.com/anthropics/skills)
- [Skills Marketplace (SkillsMP)](https://skillsmp.com/) - 25,000+ skills
- [Awesome Claude Skills](https://github.com/travisvn/awesome-claude-skills)

## Contributing

To contribute a new skill:

1.  Create a skill directory with a `SKILL.md` file in `.agent-settings/skills/`.
2.  Use `import-skills.sh` to symlink and test your skill.
3.  Commit and push your changes.

## License

See [LICENSE](LICENSE) file for details.
