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
├── setup.sh                               # One-command skills + MCP setup
│
├── skills/                                # Skills for AI agents
│   ├── README.md                          # Skills documentation
│   ├── import-skills.sh                   # Skill management script
│   ├── knowledge-graph/                   # Knowledge graph skills
│   ├── playground/                        # Experimental skills
│   ├── tools/                             # Atomic, single-purpose skills
│   └── workflows/                         # Multi-step SDD pipeline skills
│
└── mcps/                                  # MCP server configuration notes
```

Project Root (after configuration):
├── .agent/
│   └── skills/                            # Antigravity skills (symlinks)
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

# Import all skills to Antigravity
.agent-settings/skills/import-skills.sh agent

# Import all skills to Claude
.agent-settings/skills/import-skills.sh claude

# Import specific skills
.agent-settings/skills/import-skills.sh claude generate-pr-notes code-review

# Verify skills are linked correctly
.agent-settings/skills/import-skills.sh --verify claude
```

See [`skills/README.md`](skills/README.md) for detailed documentation.

### Setting Up MCP Servers

Use the MCP installation skills:

```bash
# Atlassian (Jira/Confluence)
/install-atlassian-mcp

# Azure DevOps
/install-azure-devops-mcp

# Playwright browser automation
/install-playwright-mcp
```

## Supported AI Assistants

This configuration supports the following AI coding assistants:

| Assistant | Skills | MCP Servers | Migration |
|-----------|--------|-------------|-----------|
| **Antigravity** | ✅ Native | ✅ Full Support | ✅ From others |
| **Claude Code** | ✅ Native | ✅ Full Support | ✅ From others |
| **Codex CLI** | ✅ Native | ✅ Full Support | ✅ From others |
| **Cursor** | ✅ Via symlinks | ⚠️ Limited | ✅ To Claude |
| **GitHub Copilot** | ✅ Full Support | ✅ Full Support | ✅ To Claude |
| **Google AI Studio** | ⚠️ Limited | ⚠️ Limited | ✅ To Claude |

## Antigravity Configuration

**Skills:** `.agent/skills/` - Project skills (symlinks, commit to Git)

## Claude Code Configuration

**Global:** `~/.claude.json` - User settings (managed by Claude Code)
**Project:** `.claude/mcp.json` - MCP servers (commit to Git)
**Skills:** `.claude/skills/` - Project skills (symlinks, commit to Git)

## Codex CLI Configuration

**Global:** `~/.codex/config.toml` - User settings (managed by Codex CLI)
**Project:** `.codex/config.toml` - MCP servers (commit to Git if desired)

## GitHub Copilot Configuration

**Skills:** `.github/prompts/agent-settings.*.prompt.md` - Prompt files (flat, commit to Git)
**Instructions:** `.github/copilot-instructions.md` - Skills table with `@@skill-name` convention
**MCP:** `.vscode/mcp.json` - VS Code MCP servers (uses `servers` key, commit to Git)

```bash
# Import all skills for Copilot
.agent-settings/skills/import-skills.sh copilot

# Install Atlassian MCP for Copilot
install-atlassian-mcp skill --agent copilot --jira-url https://myteam.atlassian.net
```

In Copilot Chat: type `@@` to browse skills or `@@skill-name` to invoke directly.


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
install-atlassian-mcp skill --dry-run auto .cursor/settings.json

# Check jq installation
which jq || brew install jq
```

## Contributing

When adding new resources to `.agent-settings`:

1. **Skills** - Add to `skills/` directory with a `SKILL.md` file
2. **MCP Servers** - Use the `install-atlassian-mcp` skill
3. **Migration Support** - Update the `install-atlassian-mcp` skill for new assistant types
4. **Update Documentation** - Add examples and usage instructions
5. **Test Thoroughly** - Verify across different agents before committing

## Additional Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Conventional Commits](https://www.conventionalcommits.org)
- [Docker Documentation](https://docs.docker.com)

## License

See the [LICENSE](../LICENSE) file for details.
