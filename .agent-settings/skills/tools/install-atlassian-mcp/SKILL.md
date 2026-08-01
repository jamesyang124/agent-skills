---
name: install-atlassian-mcp
description: Install and configure the Atlassian MCP server (Jira and Confluence) for Claude or GitHub Copilot agents. Supports uvx (recommended) and Docker methods. Use when setting up Atlassian MCP, Jira MCP, Confluence MCP, or asked to install atlassian mcp.
argument-hint: "[claude|copilot] [uvx|docker]"
---

# Install Atlassian MCP

## ⚙️ Install this skill globally

Install once so it's available across all your projects.

### Claude (global)
```bash
mkdir -p ~/.claude/skills/install-atlassian-mcp
cp <agent-settings-repo>/.agent-settings/skills/tools/install-atlassian-mcp/SKILL.md \
   ~/.claude/skills/install-atlassian-mcp/SKILL.md
# Add to ~/.claude/CLAUDE.md:
# - **install-atlassian-mcp** (`~/.claude/skills/install-atlassian-mcp/SKILL.md`)
```

### GitHub Copilot (global)
```bash
mkdir -p ~/.copilot/skills/install-atlassian-mcp
cp <agent-settings-repo>/.agent-settings/skills/tools/install-atlassian-mcp/SKILL.md \
   ~/.copilot/skills/install-atlassian-mcp/SKILL.md
```

---

Adds Jira and Confluence access to your agent: create/search issues, read/write pages, manage sprints.
Repository: https://github.com/sooperset/mcp-atlassian

## Arguments

All optional — anything not passed is asked in Step 1.

| Token | Meaning |
|---|---|
| `claude` / `copilot` | which agent to configure |
| `uvx` / `docker` | install method (`uvx` recommended, no Docker required) |

The API token is never taken as an argument — it is collected in the terminal (Step 2).

---

## Quick Start

Collect parameters, then run the bundled script. API tokens must be collected via terminal — never via a questions tool.

### Step 1 — Collect parameters

Use `vscode_askQuestions` with:

1. **agent** — which agent to configure
   - options: `claude`, `copilot`
2. **method** — installation method
   - options: `uvx` (recommended, no Docker required), `docker`
3. **jira-url** — Jira instance URL (e.g. `https://myteam.atlassian.net`)

### Step 2 — Run the installer

```bash
PROJECT_ROOT="<workspace-root>" \
  bash .agent-settings/skills/tools/install-atlassian-mcp/scripts/install.sh \
  --agent <agent> \
  --method <method> \
  --jira-url <jira-url>
```

- If `~/.env.mcp-atlassian` already exists, the script detects it and asks whether to reuse those credentials — no re-entry needed
- API tokens are always prompted interactively in the terminal (hidden input) when no existing file is found
- Writes `~/.env.mcp-atlassian` to your home directory (global, not per-project) and merges into the agent config

Create API tokens at: https://id.atlassian.com/manage-profile/security/api-tokens

### Step 3 — Confirm

Tell the user: **Restart your agent to load Atlassian MCP.**

## Prerequisites

**uvx** (recommended):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Docker** (alternative): Docker must be installed and running (`docker info`).

## What Gets Written

**Copilot** (`.vscode/mcp.json`) — uvx method:
```json
{
  "servers": {
    "mcp-atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "...",
        "JIRA_USERNAME": "...",
        "JIRA_API_TOKEN": "..."
      }
    }
  }
}
```

**Claude** (`.mcp.json`) use `mcpServers` key instead of `servers`.

The Docker config uses `--env-file ~/.env.mcp-atlassian` (global credential store).

## Troubleshooting

- **`uvx not found`** → run the install command above, then restart your shell
- **`jq not found`** → `brew install jq` on macOS
- **Docker not running** → start Docker Desktop and retry with `--method docker`
- **Authentication errors** → verify API token at https://id.atlassian.com/manage-profile/security/api-tokens
- **Config not loading** → confirm the agent was fully restarted after install
