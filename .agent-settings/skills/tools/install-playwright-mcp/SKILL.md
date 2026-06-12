---
name: install-playwright-mcp
description: Install and configure the Playwright browser-automation MCP server for Claude, GitHub Copilot, or Gemini agents. Use when setting up Playwright MCP, browser automation, web testing tools, or asked to install playwright mcp.
---

# Install Playwright MCP

## ⚙️ Install this skill globally

Install once so it's available across all your projects.

### Claude (global)
```bash
mkdir -p ~/.claude/skills/install-playwright-mcp
cp <agent-settings-repo>/.agent-settings/skills/tools/install-playwright-mcp/SKILL.md \
   ~/.claude/skills/install-playwright-mcp/SKILL.md
# Add to ~/.claude/CLAUDE.md:
# - **install-playwright-mcp** (`~/.claude/skills/install-playwright-mcp/SKILL.md`)
```

### GitHub Copilot (global)
```bash
mkdir -p ~/.copilot/skills/install-playwright-mcp
cp <agent-settings-repo>/.agent-settings/skills/tools/install-playwright-mcp/SKILL.md \
   ~/.copilot/skills/install-playwright-mcp/SKILL.md
```

### Gemini (global)
```bash
mkdir -p ~/.gemini/skills/install-playwright-mcp
cp <agent-settings-repo>/.agent-settings/skills/tools/install-playwright-mcp/SKILL.md \
   ~/.gemini/skills/install-playwright-mcp/SKILL.md
```

---

Adds browser automation to your agent: navigate, screenshot, click, fill forms, intercept network.
Repository: https://github.com/microsoft/playwright-mcp

## Quick Start

Ask the user two questions, then run the bundled script.

### Step 1 — Collect parameters

Use `vscode_askQuestions` with:

1. **agent** — which agent to configure
   - options: `gemini`, `claude`, `copilot`
2. **mode** — browser mode
   - options: `headed` (default, shows browser window), `headless`

### Step 2 — Run the installer

Find this skill's directory from the SKILL.md path, then run:

```bash
PROJECT_ROOT="<workspace-root>" \
  bash .agent-settings/skills/tools/install-playwright-mcp/scripts/install.sh \
  --agent <agent> \
  [--headless]
```

- Set `PROJECT_ROOT` to the user's current workspace folder
- Add `--headless` only when the user chose headless mode
- The script merges into any existing config file; it will not overwrite other servers

### Step 3 — Confirm

Tell the user: **Restart your agent to load Playwright MCP.**

## What Gets Written

**Copilot** (`.vscode/mcp.json`):
```json
{
  "servers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

**Claude** (`.mcp.json`) / **Gemini** (`.gemini/settings.json`):
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

## Troubleshooting

- **`npx not found`** → install Node.js from https://nodejs.org/
- **`jq not found`** → `brew install jq` on macOS
- **Config not loading** → confirm the agent was fully restarted after install
