---
name: install-sentry-mcp
description: Install and configure the official Sentry MCP server for Claude or GitHub Copilot agents. Supports remote (OAuth, recommended) and local stdio (npx + access token) methods. Use when setting up Sentry MCP, error-monitoring MCP, Seer, or asked to install sentry mcp.
argument-hint: "[claude|copilot] [remote|stdio]"
---

# Install Sentry MCP

## ⚙️ Install this skill globally

Install once so it's available across all your projects.

### Claude (global)
```bash
rm -rf ~/.claude/skills/install-sentry-mcp
mkdir -p ~/.claude/skills/install-sentry-mcp
cp -R <agent-settings-repo>/.agent-settings/skills/tools/install-sentry-mcp/. \
  ~/.claude/skills/install-sentry-mcp/
# Add to ~/.claude/CLAUDE.md:
# - **install-sentry-mcp** (`~/.claude/skills/install-sentry-mcp/SKILL.md`)
```

### GitHub Copilot (global)
```bash
rm -rf ~/.copilot/skills/install-sentry-mcp
mkdir -p ~/.copilot/skills/install-sentry-mcp
cp -R <agent-settings-repo>/.agent-settings/skills/tools/install-sentry-mcp/. \
  ~/.copilot/skills/install-sentry-mcp/
```

---

Adds Sentry access to your agent: list/inspect issues and events, read stack traces and breadcrumbs,
query traces, and trigger Seer AI root-cause analysis.
Official repository: https://github.com/getsentry/sentry-mcp — hosted endpoint: https://mcp.sentry.dev/mcp

## Two methods

| Method | Auth | Secret stored | When |
|--------|------|---------------|------|
| **remote** (recommended) | browser OAuth to `mcp.sentry.dev` | none | SaaS sentry.io; simplest, most tools, auto-updated |
| **stdio** | user auth token | `~/.env.mcp-sentry` | self-hosted Sentry, or when a local process is required |

Prefer **remote** unless the user is on self-hosted Sentry or explicitly needs the local process.

## Arguments

All optional — anything not passed is asked in Step 1.

| Token | Meaning |
|---|---|
| `claude` / `copilot` | which agent to configure |
| `remote` / `stdio` | install method (`remote` OAuth recommended; `stdio` for self-hosted Sentry) |

The access token is never accepted as an argument. For Copilot `stdio`, VS Code asks for it in a password
prompt when the server starts. For Claude `stdio`, the installer collects it in the terminal.

---

## Quick Start

Collect parameters, then run the bundled script. Never request or pass an access token through a chat or
command-line argument.

### Step 1 — Collect parameters

Use `vscode_askQuestions` with:

1. **agent** — which agent to configure
   - options: `claude`, `copilot`
2. **method** — installation method
   - options: `remote` (recommended, OAuth, no token), `stdio` (local, needs token)
3. **host** — *(stdio + self-hosted only)* Sentry hostname, e.g. `sentry.example.com`. Omit for SaaS sentry.io.
4. **scope** — `project` (default) or `user` (Copilot only). Use `user` to register Sentry globally for all
  VS Code workspaces.
5. **disabled skills** — *(optional)* comma-separated Sentry MCP skills to disable, e.g. `seer`.

### Step 2 — Run the installer

```bash
PROJECT_ROOT="<workspace-root>" \
  bash .agent-settings/skills/tools/install-sentry-mcp/scripts/install.sh \
  --agent <agent> \
  --method <method>
```

For a self-hosted Sentry MCP available across all VS Code workspaces:

```bash
bash ~/.copilot/skills/install-sentry-mcp/scripts/install.sh \
  --agent copilot \
  --method stdio \
  --host sentry.example.com \
  --scope user \
  --disable-skills seer
```

- **remote**: writes only the MCP registration (a `url` entry). No credentials stored — the agent runs a
  browser OAuth flow to `https://mcp.sentry.dev/mcp` on first use.
- **Copilot stdio**: writes a password-protected VS Code input reference. The token is entered only when
  VS Code starts the server and is never written to the MCP configuration file.
- **Claude stdio**: prompts for a Sentry user auth token (hidden input), stores it globally in
  `~/.env.mcp-sentry` (chmod 600), and launches the MCP process through that protected file. Add
  `--host sentry.example.com` for self-hosted.
- The script merges into any existing config file; it will not overwrite other servers.

Create a user auth token at: **Sentry → Settings → Auth Tokens**
(`https://sentry.io/settings/account/api/auth-tokens/`). Scopes: `org:read`, `project:read`,
`project:write`, `team:read`, `team:write`, `event:write`.

### Step 3 — Confirm

Tell the user: **Restart your agent to load Sentry MCP.** For the remote method, the first Sentry tool
call opens a browser to authorize.

## Prerequisites

- **remote**: none beyond an agent that supports remote/HTTP MCP servers.
- **stdio**: Node.js ≥ 18 (`node -v`) so `npx @sentry/mcp-server@latest` can run. `jq` for config merge
  (`brew install jq`).

## What Gets Written

**Remote** — Claude (`.mcp.json`) uses `mcpServers`; Copilot (`.vscode/mcp.json`) uses `servers`:
```json
{
  "mcpServers": {
    "sentry": { "type": "http", "url": "https://mcp.sentry.dev/mcp" }
  }
}
```

**Copilot stdio** — resolves `npx` to its absolute path so VS Code can launch it even when its GUI
environment has not loaded NVM. The token is requested as a password input:
```json
{
  "servers": {
    "sentry": {
      "command": "/absolute/path/to/npx",
      "args": ["-y", "@sentry/mcp-server@latest"],
      "env": {
        "SENTRY_ACCESS_TOKEN": "${input:sentry-access-token}",
        "SENTRY_HOST": "sentry.example.com"
      }
    }
  },
  "inputs": [{
    "id": "sentry-access-token",
    "type": "promptString",
    "description": "Sentry access token",
    "password": true
  }]
}
```
`SENTRY_HOST` is omitted for SaaS sentry.io.

## Per-project settings

Auth and connection are global (OAuth / `~/.env.mcp-sentry`). Which **Sentry org/project this repo maps
to** is per-project — captured by `setup-project-config` under `## MCP: sentry` (Org Slug, Project Slug).
Run `setup-project-config` after installing to record them.

## Troubleshooting

- **`node`/`npx not found`** → install Node.js ≥ 18, then restart your shell (stdio only)
- **`jq not found`** → `brew install jq` on macOS
- **OAuth window does not open (remote)** → confirm the agent supports remote MCP; re-trigger a Sentry tool call
- **`401`/auth errors (stdio)** → regenerate the token and re-run; verify the scopes listed above
- **Self-hosted not reachable** → confirm `--host` is the hostname only (no `https://`, no path)
- **Copilot token prompt does not appear** → reload VS Code, then start the `sentry` server from MCP server
  management. Enter the token in the password prompt, not in `mcp.json` or chat.
- **Config not loading** → confirm the agent was fully restarted after install
