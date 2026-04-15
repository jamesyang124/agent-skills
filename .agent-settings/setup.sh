#!/bin/bash

# setup.sh
# One-command setup: imports skills and configures MCP for a given agent.
# Run this after adding agent-settings as a submodule.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMPORT_SKILLS="$SCRIPT_DIR/skills/import-skills.sh"
INSTALL_MCP="$SCRIPT_DIR/mcps/install-atlassian-mcp.sh"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

if [[ "${NO_COLOR:-}" != "" ]]; then
    RED=''; GREEN=''; YELLOW=''; BLUE=''; BOLD=''; NC=''
fi

log_info()    { printf "${BLUE}[INFO]${NC} %s\n" "$1"; }
log_success() { printf "${GREEN}[OK]${NC}   %s\n" "$1"; }
log_warn()    { printf "${YELLOW}[WARN]${NC} %s\n" "$1"; }
log_error()   { printf "${RED}[ERR]${NC}  %s\n" "$1" >&2; }
log_step()    { printf "\n${BOLD}▶ %s${NC}\n" "$1"; }

show_help() {
    printf "${GREEN}${BOLD}agent-settings setup${NC}\n\n"
    printf "One-command setup: imports skills and configures Atlassian MCP.\n\n"
    printf "${YELLOW}Usage:${NC}\n"
    printf "    ./setup.sh [OPTIONS]\n\n"
    printf "${YELLOW}Options:${NC}\n"
    printf "    -h, --help              Show this help\n"
    printf "    --agent AGENT           Agent to set up: claude, copilot, gemini\n"
    printf "    --jira-url URL          Jira URL (skips MCP prompt, sets up MCP automatically)\n"
    printf "    --skip-mcp              Import skills only, skip MCP setup\n\n"
    printf "${YELLOW}Examples:${NC}\n"
    printf "    ./setup.sh\n"
    printf "    ./setup.sh --agent claude\n"
    printf "    ./setup.sh --agent claude --jira-url https://myteam.atlassian.net\n"
    printf "    ./setup.sh --agent gemini --skip-mcp\n\n"
}

# Parse args
AGENT=""
JIRA_URL=""
SKIP_MCP=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help) show_help; exit 0 ;;
        --agent)    AGENT="$2"; shift 2 ;;
        --jira-url) JIRA_URL="$2"; shift 2 ;;
        --skip-mcp) SKIP_MCP=true; shift ;;
        *) log_error "Unknown option: $1"; echo ""; show_help; exit 1 ;;
    esac
done

show_help

# Step 1: Select agent
if [[ -z "$AGENT" ]]; then
    printf "${YELLOW}Select agent to set up:${NC}\n"
    printf "  1) Claude Code\n"
    printf "  2) GitHub Copilot (VS Code)\n"
    printf "  3) Gemini CLI\n"
    printf "Enter choice [1-3]: "
    read -n 1 -r AGENT_CHOICE
    echo ""
    case $AGENT_CHOICE in
        1) AGENT="claude" ;;
        2) AGENT="copilot" ;;
        3) AGENT="gemini" ;;
        *) log_error "Invalid selection."; exit 1 ;;
    esac
fi

case "$AGENT" in
    claude|copilot|gemini) ;;
    *) log_error "Invalid agent: $AGENT. Use claude, copilot, or gemini."; exit 1 ;;
esac

# Step 2: Import skills
log_step "Step 1/2 — Importing skills for $AGENT"
"$IMPORT_SKILLS" "$AGENT"

# Step 3: MCP setup
if [[ "$SKIP_MCP" == true ]]; then
    log_info "Skipping MCP setup (--skip-mcp)."
    echo ""
    log_success "Setup complete! Skills are ready for $AGENT."
    exit 0
fi

log_step "Step 2/2 — Atlassian MCP setup (Jira + Confluence)"

# Check Docker is available before prompting
if ! command -v docker &>/dev/null; then
    log_warn "Docker not found. Skipping MCP setup."
    log_info "Install Docker and re-run: $0 --agent $AGENT --jira-url <url>"
    echo ""
    log_success "Setup complete! Skills are ready. Run again to add MCP."
    exit 0
fi

if ! docker info &>/dev/null 2>&1; then
    log_warn "Docker is not running. Skipping MCP setup."
    log_info "Start Docker and re-run: $0 --agent $AGENT --jira-url <url>"
    echo ""
    log_success "Setup complete! Skills are ready. Run again to add MCP."
    exit 0
fi

# If jira-url was passed, go straight to MCP install
if [[ -n "$JIRA_URL" ]]; then
    "$INSTALL_MCP" --agent "$AGENT" --jira-url "$JIRA_URL"
else
    printf "${YELLOW}Set up Atlassian MCP (Jira/Confluence)?${NC} (y/N): "
    read -n 1 -r MCP_CHOICE
    echo ""
    if [[ "$MCP_CHOICE" =~ ^[Yy]$ ]]; then
        "$INSTALL_MCP" --agent "$AGENT"
    else
        log_info "Skipped MCP. Run later: ./.agent-settings/mcps/install-atlassian-mcp.sh --agent $AGENT"
    fi
fi

echo ""
log_success "Setup complete!"
