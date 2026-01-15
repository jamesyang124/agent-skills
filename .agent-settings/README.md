# Agent Settings Directory

This directory contains centralized configurations, utilities, and resources for AI coding assistants used in this project.

## Purpose

The `.agent-settings` directory serves as a shared repository for:

- **Skills** - Reusable AI agent capabilities (prompts, workflows, templates)
- **MCP Servers** - Model Context Protocol server configurations and documentation
- **Migration Tools** - Scripts to migrate settings between different AI assistants
- **Shared Configurations** - Common settings and utilities across different AI agents

## Directory Structure

```
.agent-settings/
├── README.md                              # This file
│
├── skills/                                # Skills for AI agents
│   ├── README.md                          # Skills documentation
│   ├── import-skills.sh                   # Skill management script
│   ├── generate-pr-notes/                 # Auto-generate PR descriptions
│   │   └── SKILL.md
│   └── git-commit-conventional-strict/    # Conventional commits with emoji
│       └── SKILL.md
│
└── mcps/                                  # MCP server configurations
    ├── README.md                          # MCP setup guide
    └── install-atlassian-mcp.sh           # Atlassian MCP installer

Project Root (after configuration):
├── .claude/
│   ├── mcp.json                           # Claude MCP servers (committed)
│   └── skills/                            # Project skills (symlinks)
├── .cursor/
│   ├── settings.json                      # Cursor settings
│   └── mcp.json                           # Cursor MCP config (optional)
├── .gemini/
│   └── settings.json                      # Gemini settings
└── .env                                   # Environment variables (not committed)
```

## Quick Start

### Using Skills

Skills extend AI agent capabilities with specialized workflows and prompts.

```bash
# List available skills
.agent-settings/skills/import-skills.sh --list

# Import all skills to Claude
.agent-settings/skills/import-skills.sh claude

# Import specific skills
.agent-settings/skills/import-skills.sh claude generate-pr-notes code-review

# Verify skills are linked correctly
.agent-settings/skills/import-skills.sh --verify claude
```

See [`skills/README.md`](skills/README.md) for detailed documentation.

### Setting Up MCP Servers

Install Atlassian MCP (Jira/Confluence integration):

```bash
# Interactive installation
.agent-settings/mcps/install-atlassian-mcp.sh

# With Jira URL
.agent-settings/mcps/install-atlassian-mcp.sh --jira-url https://myteam.atlassian.net

# Help
.agent-settings/mcps/install-atlassian-mcp.sh --help
```

See [`mcps/README.md`](mcps/README.md) for detailed setup.

## Supported AI Assistants

This configuration supports the following AI coding assistants:

| Assistant | Skills | MCP Servers | Migration |
|-----------|--------|-------------|-----------|
| **Claude Code** | ✅ Native | ✅ Full Support | ✅ From others |
| **Cursor** | ✅ Via symlinks | ⚠️ Limited | ✅ To Claude |
| **GitHub Copilot** | ⚠️ Limited | ⚠️ Limited | ✅ To Claude |
| **Google AI Studio** | ⚠️ Limited | ⚠️ Limited | ✅ To Claude |

## Claude Code Configuration

**Global:** `~/.claude.json` - User settings (managed by Claude Code)
**Project:** `.claude/mcp.json` - MCP servers (commit to Git)
**Skills:** `.claude/skills/` - Project skills (symlinks, commit to Git)

## Project-Specific Configuration

### For This Project (hubs-cms-go)

This project uses Claude Code as the primary AI assistant with:

**Skills Available:**
- `generate-pr-notes` - Auto-generate pull request descriptions
- `git-commit-conventional-strict` - Enforce conventional commits with emoji

**Skills Currently Enabled in `.claude/skills/`:**
- `generate-pr-notes` (symlinked)
- `git-commit-conventional-strict` (symlinked)

**MCP Servers:**
- Not yet configured (example configurations available in `mcps/examples/`)
- See `mcps/README.md` for setup instructions

**Configuration Locations:**
- Skills: `.claude/skills/` (symlinked from `.agent-settings/skills/`)
- MCP Settings: `.claude/mcp.json` (not yet created)
- Environment Variables: `.env` (not yet created, should be added to `.gitignore`)

## Best Practices

### Skills

1. **Central Source of Truth** - Always create/edit skills in `.agent-settings/skills/`, never directly in agent folders
2. **Use Symlinks** - Import skills using symbolic links to share across agents
3. **Document Changes** - Update `SKILL.md` files when modifying skill behavior
4. **Test Before Commit** - Verify skills work in target agents before committing

### MCP Servers

1. **Environment Variables** - Use `.env` for sensitive data (API keys, tokens)
2. **Per-Project Configs** - Keep MCP settings in `.claude/mcp.json`
3. **Unique Names** - Use project-specific container names to avoid conflicts
4. **Document Dependencies** - List required MCP servers in project README

### Migration

1. **Always Backup** - Use `--backup` flag when migrating important settings
2. **Dry-Run First** - Preview migrations with `--dry-run` before applying
3. **Review Output** - Manually verify migrated configurations
4. **Protect Secrets** - Never commit API keys or tokens

## Environment Variables

Create a `.env` file in the project root for sensitive configuration:

```bash
# .env (add to .gitignore)

# Atlassian MCP Server
ATLASSIAN_EMAIL=your-email@example.com
ATLASSIAN_API_TOKEN=your-api-token
ATLASSIAN_URL=https://your-domain.atlassian.net

# BlendVision API (project-specific)
BLENDVISION_API_KEY=your-blendvision-key
BLENDVISION_BASE_URI=https://api.blendvision.com

# Other AI Assistants (if migrating)
CURSOR_API_KEY=your-cursor-key
GOOGLE_AI_API_KEY=your-google-key
GITHUB_COPILOT_TOKEN=your-copilot-token
```

**Important:** Add `.env` to `.gitignore`:

```bash
echo ".env" >> .gitignore
```

## Troubleshooting

### Skills Not Appearing

```bash
# Verify symlinks
ls -la .claude/skills

# Re-import skills
.agent-settings/skills/import-skills.sh claude

# Check skill format
cat .agent-settings/skills/generate-pr-notes/SKILL.md
```

### MCP Server Connection Issues

```bash
# Check if container is running
docker ps | grep mcp

# View container logs
docker logs atlassian-mcp

# Verify environment variables
env | grep ATLASSIAN
```

### Migration Failed

```bash
# Validate input JSON
jq empty .cursor/settings.json

# Use dry-run to preview
.agent-settings/mcps/install-atlassian-mcp.sh --dry-run auto .cursor/settings.json

# Check jq installation
which jq || brew install jq
```

## Contributing

When adding new resources to `.agent-settings`:

1. **Skills** - Add to `skills/` directory with a `SKILL.md` file
2. **MCP Servers** - Document setup in `mcps/README.md`
3. **Migration Support** - Update `install-atlassian-mcp.sh` for new assistant types
4. **Update Documentation** - Add examples and usage instructions
5. **Test Thoroughly** - Verify across different agents before committing

## Additional Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Conventional Commits](https://www.conventionalcommits.org)
- [Docker Documentation](https://docs.docker.com)

## License

These configurations are specific to the `hubs-cms-go` project. Adapt as needed for your use case.
