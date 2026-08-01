---
name: install-azure-devops-mcp
description: Install and configure the Azure DevOps MCP server for Claude or GitHub Copilot agents. Use when setting up Azure DevOps MCP, ADO MCP, work items, repos, pipelines, sprints, wikis, or asked to install azure devops mcp.
argument-hint: "[claude|copilot] [ado-org]"
---

# Install Azure DevOps MCP

## ⚙️ Install this skill globally

Install once so it's available across all your projects.

### Claude (global)
```bash
mkdir -p ~/.claude/skills/install-azure-devops-mcp
cp <agent-settings-repo>/.agent-settings/skills/tools/install-azure-devops-mcp/SKILL.md \
   ~/.claude/skills/install-azure-devops-mcp/SKILL.md
# Add to ~/.claude/CLAUDE.md:
# - **install-azure-devops-mcp** (`~/.claude/skills/install-azure-devops-mcp/SKILL.md`)
```

### GitHub Copilot (global)
```bash
mkdir -p ~/.copilot/skills/install-azure-devops-mcp
cp <agent-settings-repo>/.agent-settings/skills/tools/install-azure-devops-mcp/SKILL.md \
   ~/.copilot/skills/install-azure-devops-mcp/SKILL.md
```

---

Adds Azure DevOps access to your agent: work items, repos, branches, PRs, pipelines, test plans, sprints, wikis.
Repository: https://github.com/microsoft/azure-devops-mcp

## Arguments

All optional — anything not passed is asked in Step 1.

| Token | Meaning |
|---|---|
| `claude` / `copilot` | which agent to configure |
| any other bare token | Azure DevOps organization name (e.g. `mycompany`) |

The PAT is never taken as an argument — it is collected in the terminal (Step 2).

---

## Quick Start

Collect parameters, then run the bundled script. The PAT must be collected via terminal — never via a questions tool.

### Step 1 — Collect parameters

Use `vscode_askQuestions` with:

1. **agent** — which agent to configure
   - options: `claude`, `copilot`
2. **org** — Azure DevOps organization name (e.g. `mycompany`)

### Step 2 — Run the installer

Find this skill's directory from the SKILL.md path, then run:

```bash
PROJECT_ROOT="<workspace-root>" \
  bash .agent-settings/skills/tools/install-azure-devops-mcp/scripts/install.sh \
  --agent <agent> \
  --org <org>
```

- Set `PROJECT_ROOT` to the user's current workspace folder
- If `~/.env.mcp-azure-devops` already exists, the script detects it and asks whether to reuse the stored PAT — no re-entry needed
- PAT is always prompted interactively in the terminal (hidden input) when no existing file is found
- The script merges into any existing config file; it will not overwrite other servers

**PAT scopes required:**
- Work Items (Read & Write)
- Code (Read)
- Build (Read)
- Test (Read)

Create at: `https://dev.azure.com/<org>/_usersSettings/tokens`

### Step 3 — Confirm

Tell the user: **Restart your agent to load Azure DevOps MCP.**

## What Gets Written

**Copilot** (`.vscode/mcp.json`):
```json
{
  "servers": {
    "azure-devops-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp", "<org>"],
      "env": { "AZURE_DEVOPS_EXT_PAT": "<pat>" }
    }
  }
}
```

**Claude** (`.mcp.json`):
```json
{
  "mcpServers": {
    "azure-devops-mcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp", "<org>"],
      "env": { "AZURE_DEVOPS_EXT_PAT": "<pat>" }
    }
  }
}
```

An env file is also written to `~/.env.mcp-azure-devops` (global, chmod 600).

## Troubleshooting

- **`npx not found`** → install Node.js from https://nodejs.org/
- **`jq not found`** → `brew install jq` on macOS
- **Authentication errors** → verify PAT scopes and expiry
- **Config not loading** → confirm the agent was fully restarted after install
