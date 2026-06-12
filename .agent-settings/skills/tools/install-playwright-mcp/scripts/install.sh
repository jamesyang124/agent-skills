#!/bin/bash

# install-playwright-mcp.sh
# Installs and configures Playwright MCP server from https://github.com/microsoft/playwright-mcp

set -e

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [[ "${NO_COLOR:-}" != "" ]]; then
    RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''
fi

log_info()    { printf "${BLUE}[INFO]${NC} %s\n" "$1" >&2; }
log_success() { printf "${GREEN}[SUCCESS]${NC} %s\n" "$1" >&2; }
log_warning() { printf "${YELLOW}[WARNING]${NC} %s\n" "$1" >&2; }
log_error()   { printf "${RED}[ERROR]${NC} %s\n" "$1" >&2; }

show_help() {
    printf "${GREEN}Playwright MCP Installer v${VERSION}${NC}\n\n"
    printf "Installs Playwright MCP server (browser automation/testing integration)\n"
    printf "Repository: https://github.com/microsoft/playwright-mcp\n\n"
    printf "${YELLOW}Usage:${NC}\n"
    printf "    ./install-playwright-mcp.sh [OPTIONS]\n\n"
    printf "${YELLOW}Options:${NC}\n"
    printf "    -h, --help              Show help\n"
    printf "    -o, --output FILE       Output file (overrides interactive selection)\n"
    printf "    --agent AGENT           Specify agent: 'gemini', 'claude', or 'copilot'\n"
    printf "    --headless              Configure for headless mode (default: headed)\n\n"
    printf "${YELLOW}Examples:${NC}\n"
    printf "    ./install-playwright-mcp.sh\n"
    printf "    ./install-playwright-mcp.sh --agent copilot\n"
    printf "    ./install-playwright-mcp.sh --agent claude --headless\n\n"
}

# Check for --help flag first
for arg in "$@"; do
    if [[ "$arg" == "-h" ]] || [[ "$arg" == "--help" ]]; then
        show_help
        exit 0
    fi
done

# Parse arguments
OUTPUT_FILE=""
AGENT=""
HEADLESS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output) OUTPUT_FILE="$2"; shift 2 ;;
        --agent) AGENT="$2"; shift 2 ;;
        --headless) HEADLESS=true; shift ;;
        *) log_error "Unknown option: $1"; exit 1 ;;
    esac
done

# Check prerequisites
log_info "Checking Node.js / npx availability..."
if ! command -v npx &>/dev/null; then
    log_error "npx not found. Install Node.js from https://nodejs.org/"
    exit 1
fi
log_success "npx is available"

# Interactive agent selection if not provided
if [[ -z "$AGENT" ]]; then
    printf "\n${YELLOW}Select the target agent:${NC}\n"
    printf "  1) Gemini\n"
    printf "  2) Claude\n"
    printf "  3) GitHub Copilot\n"
    printf "Enter choice [1-3]: "
    read -n 1 -r AGENT_CHOICE
    echo ""
    case $AGENT_CHOICE in
        1) AGENT="gemini" ;;
        2) AGENT="claude" ;;
        3) AGENT="copilot" ;;
        *) log_error "Invalid selection."; exit 1 ;;
    esac
fi

if [[ -z "$OUTPUT_FILE" ]]; then
    if [[ "$AGENT" == "gemini" ]]; then
        if [[ -f "$HOME/.gemini/antigravity/mcp_config.json" ]]; then
            OUTPUT_FILE="$HOME/.gemini/antigravity/mcp_config.json"
        else
            OUTPUT_FILE="${PROJECT_ROOT}/.gemini/settings.json"
        fi
    elif [[ "$AGENT" == "claude" ]]; then
        OUTPUT_FILE="${PROJECT_ROOT}/.mcp.json"
    elif [[ "$AGENT" == "copilot" ]]; then
        OUTPUT_FILE="${PROJECT_ROOT}/.vscode/mcp.json"
    else
        log_error "Invalid agent specified: ${AGENT}. Use 'gemini', 'claude', or 'copilot'."
        exit 1
    fi
fi
log_info "Will write configuration to: ${OUTPUT_FILE}"

# Build args array — add --headless flag if requested
if [[ "$HEADLESS" == "true" ]]; then
    PLAYWRIGHT_ARGS='["@playwright/mcp@latest", "--headless"]'
else
    PLAYWRIGHT_ARGS='["@playwright/mcp@latest"]'
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

log_info "Generating Playwright MCP configuration for ${AGENT}..."

if [[ "$AGENT" == "copilot" ]]; then
    MCP_CONFIG=$(cat <<EOFCONFIG
{
  "servers": {
    "playwright": {
      "command": "npx",
      "args": ${PLAYWRIGHT_ARGS}
    }
  }
}
EOFCONFIG
)
    if [[ -f "$OUTPUT_FILE" ]] && [[ -s "$OUTPUT_FILE" ]]; then
        log_info "Merging with existing configuration..."
        MERGED=$(jq --argjson newConfig "$MCP_CONFIG" '.servers["playwright"] = $newConfig.servers["playwright"]' "$OUTPUT_FILE")
        echo "$MERGED" | jq '.' > "$OUTPUT_FILE"
    else
        echo "$MCP_CONFIG" | jq '.' > "$OUTPUT_FILE"
    fi
else
    MCP_CONFIG=$(cat <<EOFCONFIG
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ${PLAYWRIGHT_ARGS}
    }
  }
}
EOFCONFIG
)
    if [[ -f "$OUTPUT_FILE" ]] && [[ -s "$OUTPUT_FILE" ]]; then
        log_info "Merging with existing configuration..."
        MERGED=$(jq --argjson newConfig "$MCP_CONFIG" '.mcpServers["playwright"] = $newConfig.mcpServers["playwright"]' "$OUTPUT_FILE")
        echo "$MERGED" | jq '.' > "$OUTPUT_FILE"
    else
        echo "$MCP_CONFIG" | jq '.' > "$OUTPUT_FILE"
    fi
fi

log_success "Playwright MCP configuration written to: ${OUTPUT_FILE}"
log_info "Restart your agent to apply changes."
printf "\n${GREEN}Done!${NC} Playwright MCP tools are now available to your ${AGENT} agent.\n"
printf "Capabilities: browser navigation, screenshots, click/type/fill, network interception.\n"
