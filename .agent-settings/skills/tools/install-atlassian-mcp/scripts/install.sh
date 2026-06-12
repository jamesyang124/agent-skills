#!/bin/bash

# install.sh — Atlassian MCP installer (uvx method)
# Installs and configures Atlassian MCP server from https://github.com/sooperset/mcp-atlassian
# Uses uvx (recommended) — no Docker required.
# Credentials are stored globally in ~/.env.mcp-atlassian (not per-project).

set -e

VERSION="3.0.0"
PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
GLOBAL_ENV_FILE="${HOME}/.env.mcp-atlassian"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
[[ "${NO_COLOR:-}" != "" ]] && RED='' GREEN='' YELLOW='' BLUE='' NC=''

log_info()    { printf "${BLUE}[INFO]${NC} %s\n" "$1" >&2; }
log_success() { printf "${GREEN}[SUCCESS]${NC} %s\n" "$1" >&2; }
log_error()   { printf "${RED}[ERROR]${NC} %s\n" "$1" >&2; }

show_help() {
    printf "${GREEN}Atlassian MCP Installer v${VERSION}${NC}\n\n"
    printf "Installs Atlassian MCP server (Jira/Confluence) using uvx.\n"
    printf "Repository: https://github.com/sooperset/mcp-atlassian\n\n"
    printf "${YELLOW}Usage:${NC}\n"
    printf "    install.sh [OPTIONS]\n\n"
    printf "${YELLOW}Options:${NC}\n"
    printf "    -h, --help              Show help\n"
    printf "    -o, --output FILE       Output config file (overrides interactive selection)\n"
    printf "    --agent AGENT           gemini | claude | copilot\n"
    printf "    --jira-url URL          Jira instance URL\n"
    printf "    --confluence-url URL    Confluence URL (default: same as Jira)\n\n"
    printf "${YELLOW}Environment:${NC}\n"
    printf "    PROJECT_ROOT            Target project directory (default: \$PWD)\n\n"
    printf "${YELLOW}Prerequisites:${NC}\n"
    printf "    uvx — install with: curl -LsSf https://astral.sh/uv/install.sh | sh\n\n"
    printf "${YELLOW}Examples:${NC}\n"
    printf "    install.sh\n"
    printf "    install.sh --agent copilot --jira-url https://myteam.atlassian.net\n\n"
}

for arg in "$@"; do
    [[ "$arg" == "-h" || "$arg" == "--help" ]] && { show_help; exit 0; }
done

# Parse arguments
OUTPUT_FILE=""
JIRA_URL=""
CONFLUENCE_URL=""
AGENT=""

while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output)          OUTPUT_FILE="$2"; shift 2 ;;
        --agent)              AGENT="$2"; shift 2 ;;
        --jira-url)           JIRA_URL="$2"; shift 2 ;;
        --confluence-url)     CONFLUENCE_URL="$2"; shift 2 ;;
        *) log_error "Unknown option: $1"; exit 1 ;;
    esac
done

# Prerequisites
log_info "Checking uvx availability..."
if ! command -v uvx &>/dev/null; then
    log_error "uvx not found. Install it with:"
    log_error "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    log_error "Then restart your shell and re-run this script."
    exit 1
fi
if ! command -v jq &>/dev/null; then
    log_error "jq not found. Install with: brew install jq"
    exit 1
fi
log_success "uvx is available"

# Interactive agent selection
if [[ -z "$AGENT" ]]; then
    printf "\n${YELLOW}Select the target agent:${NC}\n"
    printf "  1) Gemini\n"
    printf "  2) Claude\n"
    printf "  3) GitHub Copilot\n"
    printf "Enter choice [1-3]: "
    read -n 1 -r AGENT_CHOICE; echo ""
    case $AGENT_CHOICE in
        1) AGENT="gemini" ;;
        2) AGENT="claude" ;;
        3) AGENT="copilot" ;;
        *) log_error "Invalid selection."; exit 1 ;;
    esac
fi

# Resolve output file
if [[ -z "$OUTPUT_FILE" ]]; then
    case "$AGENT" in
        gemini)
            if [[ -f "$HOME/.gemini/antigravity/mcp_config.json" ]]; then
                OUTPUT_FILE="$HOME/.gemini/antigravity/mcp_config.json"
            else
                OUTPUT_FILE="${PROJECT_ROOT}/.gemini/settings.json"
            fi ;;
        claude)   OUTPUT_FILE="${PROJECT_ROOT}/.mcp.json" ;;
        copilot)  OUTPUT_FILE="${PROJECT_ROOT}/.vscode/mcp.json" ;;
        *) log_error "Invalid agent: ${AGENT}. Use gemini, claude, or copilot."; exit 1 ;;
    esac
fi
log_info "Target config: ${OUTPUT_FILE}"

# Collect Jira URL
if [[ -z "$JIRA_URL" ]]; then
    printf "${YELLOW}Jira URL${NC} (e.g., https://myteam.atlassian.net): "
    read JIRA_URL
    [[ -z "$JIRA_URL" ]] && { log_error "Jira URL is required"; exit 1; }
fi
CONFLUENCE_URL="${CONFLUENCE_URL:-${JIRA_URL}}"

# Collect credentials
printf "\n${YELLOW}Enter your Atlassian credentials.${NC}\n"
printf "Create API tokens at: https://id.atlassian.com/manage-profile/security/api-tokens\n\n"

printf "${YELLOW}Jira Username (email):${NC} "
read JIRA_USERNAME
[[ -z "$JIRA_USERNAME" ]] && { log_error "Jira Username is required"; exit 1; }

printf "${YELLOW}Jira API Token:${NC} "
read -s JIRA_API_TOKEN; echo ""
[[ -z "$JIRA_API_TOKEN" ]] && { log_error "Jira API Token is required"; exit 1; }

printf "\n${YELLOW}Are your Confluence credentials the same as Jira?${NC} (y/N): "
read -n 1 -r CONFLUENCE_SAME; echo ""

if [[ "$CONFLUENCE_SAME" =~ ^[Yy]$ ]]; then
    CONFLUENCE_USERNAME="$JIRA_USERNAME"
    CONFLUENCE_API_TOKEN="$JIRA_API_TOKEN"
    log_info "Using Jira credentials for Confluence."
else
    printf "${YELLOW}Confluence Username (email):${NC} "
    read CONFLUENCE_USERNAME
    [[ -z "$CONFLUENCE_USERNAME" ]] && { log_error "Confluence Username is required"; exit 1; }

    printf "${YELLOW}Confluence API Token:${NC} "
    read -s CONFLUENCE_API_TOKEN; echo ""
    [[ -z "$CONFLUENCE_API_TOKEN" ]] && { log_error "Confluence API Token is required"; exit 1; }
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

log_info "Writing Atlassian MCP (uvx) config for ${AGENT}..."

# Write credentials to global env file (~/.env.mcp-atlassian)
# This allows the credentials to be reused across all projects.
log_info "Storing credentials in: ${GLOBAL_ENV_FILE}"
cat > "${GLOBAL_ENV_FILE}" <<ENVEOF
JIRA_URL=${JIRA_URL}
JIRA_USERNAME=${JIRA_USERNAME}
JIRA_API_TOKEN=${JIRA_API_TOKEN}
CONFLUENCE_URL=${CONFLUENCE_URL}
CONFLUENCE_USERNAME=${CONFLUENCE_USERNAME}
CONFLUENCE_API_TOKEN=${CONFLUENCE_API_TOKEN}
ENVEOF
chmod 600 "${GLOBAL_ENV_FILE}"
log_success "Credentials stored in ${GLOBAL_ENV_FILE}"

ENV_BLOCK=$(cat <<ENVEOF
{
  "JIRA_URL": "${JIRA_URL}",
  "JIRA_USERNAME": "${JIRA_USERNAME}",
  "JIRA_API_TOKEN": "${JIRA_API_TOKEN}",
  "CONFLUENCE_URL": "${CONFLUENCE_URL}",
  "CONFLUENCE_USERNAME": "${CONFLUENCE_USERNAME}",
  "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}"
}
ENVEOF
)

if [[ "$AGENT" == "copilot" ]]; then
    MCP_CONFIG=$(jq -n --argjson env "$ENV_BLOCK" \
        '{"servers":{"mcp-atlassian":{"command":"uvx","args":["mcp-atlassian"],"env":$env}}}')
    if [[ -f "$OUTPUT_FILE" && -s "$OUTPUT_FILE" ]]; then
        jq --argjson c "$MCP_CONFIG" '.servers["mcp-atlassian"] = $c.servers["mcp-atlassian"]' \
            "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
    else
        echo "$MCP_CONFIG" | jq '.' > "$OUTPUT_FILE"
    fi
else
    MCP_CONFIG=$(jq -n --argjson env "$ENV_BLOCK" \
        '{"mcpServers":{"mcp-atlassian":{"command":"uvx","args":["mcp-atlassian"],"env":$env}}}')
    if [[ -f "$OUTPUT_FILE" && -s "$OUTPUT_FILE" ]]; then
        jq --argjson c "$MCP_CONFIG" '.mcpServers["mcp-atlassian"] = $c.mcpServers["mcp-atlassian"]' \
            "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
    else
        echo "$MCP_CONFIG" | jq '.' > "$OUTPUT_FILE"
    fi
fi

log_success "Written to: ${OUTPUT_FILE}"
printf "\n${GREEN}Done!${NC} Restart your agent to load Atlassian MCP.\n"
if [[ "$AGENT" == "copilot" ]]; then
    printf "Note: .vscode/mcp.json may need 'git add -f' if .vscode/ is gitignored.\n"
fi
