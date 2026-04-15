# Atlassian MCP Integration Setup

This guide explains how to integrate your agent with Jira and Confluence via the Atlassian MCP server.

> **VS Code Copilot users:** Skip the install script. See [Using Skills Instead of the Script](#vs-code-copilot-use-skills-instead-of-the-script) below.

The script configures a connection to the Atlassian MCP server, which runs in a Docker container.

## Prerequisites

- **Docker:** Must be installed and **running**. The MCP server executes as a Docker container — without it, no Jira/Confluence tools will be available.
  - Verify Docker is running: `docker info`
  - Pull the image before first use: `docker pull ghcr.io/sooperset/mcp-atlassian:latest`

## Usage

Run the script from the `mcps` directory or project root.

### Interactive Installation

The script will prompt you for your agent, Jira/Confluence URLs, and credentials.

```bash
./install-atlassian-mcp.sh
```

### Non-Interactive Installation

You can provide all information using command-line flags.

```bash
./install-atlassian-mcp.sh [OPTIONS]
```

**Options:**

| Flag | Description |
|---|---|
| `-h, --help` | Show help |
| `--agent AGENT` | Specify agent: `gemini`, `claude`, or `copilot` |
| `--jira-url URL` | Your Jira instance URL |
| `--confluence-url URL` | Your Confluence instance URL (defaults to Jira URL) |
| `-o, --output FILE`| Output configuration file path (e.g., `.gemini/settings.json`) |

**Example:**

```bash
./install-atlassian-mcp.sh --agent gemini --jira-url https://myteam.atlassian.net
```

## Configuration Output

The script performs two main actions regardless of the selected agent:

1.  **Creates an Environment File:** It generates a `.env.mcp-atlassian` file in your project's root directory. This file stores your Jira and Confluence credentials.

2.  **Creates a Configuration File:** It generates a configuration file that tells the agent how to run the Atlassian MCP server using Docker. This file points to the `.env.mcp-atlassian` file for credentials.
    -   For **Gemini**, the file is `.gemini/settings.json`.
    -   For **Claude**, the file is `.mcp.json`.
    -   For **GitHub Copilot**, the file is `.vscode/mcp.json`.

After running the script, restart your agent to apply the changes.

## Claude Code Setup

Claude Code reads MCP servers from `.mcp.json` in the project root. Without it, Jira/Confluence tools are unavailable.

Run the install script to generate it:

```bash
./.agent-settings/mcps/install-atlassian-mcp.sh --agent claude --jira-url https://myteam.atlassian.net
```

This creates `.mcp.json` (gitignored, machine-local) using the `mcpServers` key (Claude's format). Restart Claude Code to apply.

---

## VS Code Copilot: Use Skills Instead of the Script

Since GitHub Copilot now reads skills from `.claude/skills/` (the same directory as Claude Code), you can set up and use Atlassian tools interactively via Copilot Chat — no need to run the install script manually.

**One-time setup:**

1. Import skills into `.claude/skills/` (once per machine):
   ```bash
   ./.agent-settings/skills/import-skills.sh claude
   # 'copilot' is an alias — both use .claude/skills/
   ```

2. Run the install script once to write `.vscode/mcp.json` and `.env.mcp-atlassian`:
   ```bash
   ./.agent-settings/mcps/install-atlassian-mcp.sh --agent copilot --jira-url https://myteam.atlassian.net
   ```
   Then reload the VS Code window (`Ctrl+Shift+P` → `Developer: Reload Window`).

**Using skills in Copilot Chat:**

Once skills are imported and MCP is running, invoke them in Copilot Chat:

| What you want | Type in Copilot Chat |
|---------------|----------------------|
| Configure project settings | `/setup-project-config` |
| Generate PR notes | `/generate-pr-notes` |
| Commit with conventional format | `/git-commit-conventional-strict` |
| Create Confluence tech plan | `/sdd-tech-plan-to-confluence` |

> Copilot will load the skill instructions and execute the workflow, using the MCP server's Jira/Confluence tools automatically.

## GitHub Copilot (VS Code) — Script-based Setup

GitHub Copilot uses VS Code's MCP format, which differs from other agents:

```bash
./install-atlassian-mcp.sh --agent copilot --jira-url https://myteam.atlassian.net
```

This writes `.vscode/mcp.json` using the `servers` key (VS Code format):

```json
{
  "servers": {
    "atlassian": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--env-file", "/path/.env.mcp-atlassian", "ghcr.io/sooperset/mcp-atlassian:latest"],
      "env": {}
    }
  }
}
```

After installation, reload the VS Code window (`Ctrl+Shift+P` → `Developer: Reload Window`) for the MCP server to be recognized.

> **Note:** `.vscode/mcp.json` is gitignored (machine-local, contains absolute paths). Each developer runs the install script once to generate it locally.
