#!/bin/bash

# install-atlassian-mcp.sh
# Installs and configures Atlassian MCP server from https://github.com/sooperset/mcp-atlassian

set -e

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [[ "${NO_COLOR:-}" != "" ]]; then
    RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''
fi

log_info() { printf "${BLUE}[INFO]${NC} %s\n" "$1" >&2; }
log_success() { printf "${GREEN}[SUCCESS]${NC} %s\n" "$1" >&2; }
log_warning() { printf "${YELLOW}[WARNING]${NC} %s\n" "$1" >&2; }
log_error() { printf "${RED}[ERROR]${NC} %s\n" "$1" >&2; }

show_help() {
    printf "${GREEN}Atlassian MCP Installer v${VERSION}${NC}\n\n"
    printf "Installs Atlassian MCP server (Jira/Confluence integration)\n"
    printf "Repository: https://github.com/sooperset/mcp-atlassian\n\n"
    printf "${YELLOW}Usage:${NC}\n"
    printf "    ./install-atlassian-mcp.sh [OPTIONS]\n\n"
    printf "${YELLOW}Options:${NC}\n"
    printf "    -h, --help              Show help\n"
    printf "    -o, --output FILE       Output file (overrides interactive selection)\n"
    printf "    --agent AGENT           Specify agent non-interactively: 'gemini' or 'claude'.\n"
    printf "    --jira-url URL          Jira URL\n"
    printf "    --confluence-url URL    Confluence URL (default: same as Jira)\n\n"
    printf "${YELLOW}Examples:${NC}\n"
    printf "    ./install-atlassian-mcp.sh\n"
    printf "    ./install-atlassian-mcp.sh --agent gemini --jira-url https://myteam.atlassian.net\n\n"
}

# Always show help first
show_help

# Parse arguments
OUTPUT_FILE=""
JIRA_URL=""
CONFLUENCE_URL=""
AGENT="" # Agent will be determined interactively if not passed as an argument

while [[ $# -gt 0 ]]; do
    case $1 in
        # -h or --help is handled by the initial show_help and exit
        -h|--help) exit 0 ;;
        -o|--output) OUTPUT_FILE="$2"; shift 2 ;;
        --agent) AGENT="$2"; shift 2 ;;
        --jira-url) JIRA_URL="$2"; shift 2 ;;
        --confluence-url) CONFLUENCE_URL="$2"; shift 2 ;;
        *) log_error "Unknown option: $1"; exit 1 ;;
    esac
done

# Interactive agent selection if not provided
if [[ -z "$AGENT" ]]; then
    printf "\n${YELLOW}Select the target agent:${NC}\n"
    printf "  1) Gemini\n"
    printf "  2) Claude\n"
    printf "Enter choice [1-2]: "
    read -n 1 -r AGENT_CHOICE
    echo ""
    case $AGENT_CHOICE in
        1) AGENT="gemini" ;;
        2) AGENT="claude" ;;
        *) log_error "Invalid selection."; exit 1 ;;
    esac
fi

if [[ -z "$OUTPUT_FILE" ]]; then
    if [[ "$AGENT" == "gemini" ]]; then
        OUTPUT_FILE="${PROJECT_ROOT}/.gemini/settings.json"
    elif [[ "$AGENT" == "claude" ]]; then
        OUTPUT_FILE="${PROJECT_ROOT}/.mcp.json"
    else
        log_error "Invalid agent specified: ${AGENT}. Use 'gemini' or 'claude'."
        exit 1
    fi
fi
log_info "Will write configuration to: ${OUTPUT_FILE}"

CONFLUENCE_URL="${CONFLUENCE_URL:-${JIRA_URL}}"

# Interactive prompt if no URL
if [[ -z "$JIRA_URL" ]]; then
    printf "${YELLOW}Jira URL${NC} (e.g., https://myteam.atlassian.net): "
    read JIRA_URL
    [[ -z "$JIRA_URL" ]] && { log_error "Jira URL is required"; exit 1; }
fi
# Default Confluence URL to Jira URL if not provided
CONFLUENCE_URL="${CONFLUENCE_URL:-${JIRA_URL}}"

# Interactive prompt for credentials
printf "\n${YELLOW}Enter your Atlassian credentials.${NC}\n"
printf "You can create API tokens at: https://id.atlassian.com/manage-profile/security/api-tokens\n\n"

printf "${YELLOW}Jira Username (email):${NC} "
read JIRA_USERNAME
[[ -z "$JIRA_USERNAME" ]] && { log_error "Jira Username is required"; exit 1; }

printf "${YELLOW}Jira API Token:${NC} "
read -s JIRA_API_TOKEN
echo ""
[[ -z "$JIRA_API_TOKEN" ]] && { log_error "Jira API Token is required"; exit 1; }

# Ask if Confluence credentials are the same as Jira's
printf "\n${YELLOW}Are your Confluence credentials the same as your Jira credentials?${NC} (y/N): "
read -n 1 -r CONFLUENCE_SAME_AS_JIRA_CHOICE
echo ""

if [[ "$CONFLUENCE_SAME_AS_JIRA_CHOICE" =~ ^[Yy]$ ]]; then
    CONFLUENCE_USERNAME="$JIRA_USERNAME"
    CONFLUENCE_API_TOKEN="$JIRA_API_TOKEN"
    log_info "Using Jira credentials for Confluence."
else
    printf "${YELLOW}Confluence Username (email):${NC} "
    read CONFLUENCE_USERNAME
    [[ -z "$CONFLUENCE_USERNAME" ]] && { log_error "Confluence Username is required"; exit 1; }

    printf "${YELLOW}Confluence API Token:${NC} "
    read -s CONFLUENCE_API_TOKEN
    echo ""
    [[ -z "$CONFLUENCE_API_TOKEN" ]] && { log_error "Confluence API Token is required"; exit 1; }
fi

# Create configuration
log_info "Creating Atlassian MCP configuration to use Docker..."

# Generate the .env file for all agents
ENV_FILE_PATH="${PROJECT_ROOT}/.env.mcp-atlassian"
log_info "Generating environment file at: ${ENV_FILE_PATH}"
cat <<EOF_ENV > "$ENV_FILE_PATH"
JIRA_URL=${JIRA_URL}
JIRA_USERNAME=${JIRA_USERNAME}
JIRA_API_TOKEN=${JIRA_API_TOKEN}
CONFLUENCE_URL=${CONFLUENCE_URL}
CONFLUENCE_USERNAME=${CONFLUENCE_USERNAME}
CONFLUENCE_API_TOKEN=${CONFLUENCE_API_TOKEN}
EOF_ENV
log_success "Created ${ENV_FILE_PATH}"

# Create the agent-specific config that uses the env file
MCP_CONFIG=$(cat <<EOFCONFIG
{
  "mcpServers": {
    "atlassian": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env-file",
        "${ENV_FILE_PATH}",
        "ghcr.io/sooperset/mcp-atlassian:latest"
      ]
    }
  }
}
EOFCONFIG
)

mkdir -p "$(dirname "$OUTPUT_FILE")"

# Merge with existing
if [[ -f "$OUTPUT_FILE" ]] && [[ -s "$OUTPUT_FILE" ]]; then
    log_info "Merging with existing configuration..."
    # Using jq is the robust way to set/overwrite the atlassian config.
    MERGED=$(jq --argjson newConfig "$MCP_CONFIG" '.mcpServers.atlassian = $newConfig.mcpServers.atlassian' "$OUTPUT_FILE")
    echo "$MERGED" | jq '.' > "$OUTPUT_FILE"
else
    echo "$MCP_CONFIG" | jq '.' > "$OUTPUT_FILE"
fi

log_success "Atlassian MCP configuration updated to use Docker in: $OUTPUT_FILE"

echo ""
log_info "Next steps:"
echo "  1. Make sure you have Docker installed and running."
echo "  2. Review the generated configuration in ${OUTPUT_FILE}."
echo "  3. Review the environment file at ${PROJECT_ROOT}/.env.mcp-atlassian."
echo "  4. Restart your development environment to apply the changes."

