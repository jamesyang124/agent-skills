# Atlassian MCP Integration Setup

> **Note:** The `mcps/` folder has been replaced by the `install-atlassian-mcp` skill.
> Use the skill instead: `.agent-settings/skills/tools/install-atlassian-mcp/`

~~This guide explains how to use the `install-atlassian-mcp.sh` script to integrate your agent with Jira and Confluence.~~

The script configures a connection to the Atlassian MCP server, which runs in a Docker container.

## Prerequisites

- **Docker:** You must have Docker installed and running.

## Usage

Run the script from the `skills/tools/` directory or project root.

### Interactive Installation

The script will prompt you for your agent, Jira/Confluence URLs, and credentials.

```bash
install-atlassian-mcp skill
```

### Non-Interactive Installation

You can provide all information using command-line flags.

```bash
install-atlassian-mcp skill [OPTIONS]
```

**Options:**

| Flag | Description |
|---|---|
| `-h, --help` | Show help |
| `--agent AGENT` | Specify agent: `claude` or `copilot` |
| `--jira-url URL` | Your Jira instance URL |
| `--confluence-url URL` | Your Confluence instance URL (defaults to Jira URL) |
| `-o, --output FILE`| Output configuration file path (e.g., `.mcp.json`) |

**Example:**

```bash
install-atlassian-mcp skill --agent claude --jira-url https://myteam.atlassian.net
```

## Configuration Output

The script performs two main actions regardless of the selected agent:

1.  **Creates an Environment File:** It generates a `~/.env.mcp-atlassian` file in your project's root directory. This file stores your Jira and Confluence credentials.

2.  **Creates a Configuration File:** It generates a JSON configuration file that tells the agent how to run the Atlassian MCP server using Docker. This file points to the `~/.env.mcp-atlassian` file for credentials.
    -   For **Claude**, the file is `.mcp.json`.
    -   For **GitHub Copilot**, the file is `.vscode/mcp.json`.

After running the script, restart your agent to apply the changes.
