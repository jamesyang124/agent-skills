#!/bin/bash

# install.sh — Sentry MCP installer
# Installs and configures the official Sentry MCP server (https://github.com/getsentry/sentry-mcp).
#   remote (recommended): registers the hosted endpoint https://mcp.sentry.dev/mcp — OAuth, no secret.
#   stdio:                runs npx @sentry/mcp-server@latest with a user auth token.
# Stdio credentials are stored globally in ~/.env.mcp-sentry (not per-project).

set -e

VERSION="1.1.0"
PROJECT_ROOT="${PROJECT_ROOT:-$PWD}"
GLOBAL_ENV_FILE="${HOME}/.env.mcp-sentry"
REMOTE_URL="https://mcp.sentry.dev/mcp"

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
    printf "${GREEN}Sentry MCP Installer v${VERSION}${NC}\n\n"
    printf "Installs the official Sentry MCP server.\n"
    printf "Repository: https://github.com/getsentry/sentry-mcp\n\n"
    printf "${YELLOW}Usage:${NC}\n"
    printf "    install.sh [OPTIONS]\n\n"
    printf "${YELLOW}Options:${NC}\n"
    printf "    -h, --help          Show help\n"
    printf "    -o, --output FILE   Output config file (overrides interactive selection)\n"
    printf "    --agent AGENT       claude | copilot\n"
    printf "    --method METHOD     remote (recommended) | stdio\n"
    printf "    --url URL           Remote endpoint (default: ${REMOTE_URL})\n"
    printf "    --host HOST         Self-hosted Sentry hostname for stdio (e.g. sentry.example.com)\n\n"
    printf "    --scope SCOPE       project (default) | user (Copilot only)\n"
    printf "    --disable-skills    Comma-separated Sentry MCP skills to disable\n\n"
    printf "${YELLOW}Environment:${NC}\n"
    printf "    PROJECT_ROOT        Target project directory (default: \$PWD)\n\n"
    printf "${YELLOW}Examples:${NC}\n"
    printf "    install.sh --agent claude --method remote\n"
    printf "    install.sh --agent copilot --method stdio --host sentry.example.com\n\n"
    printf "    install.sh --agent copilot --method stdio --host sentry.example.com --scope user\n\n"
}

for arg in "$@"; do
    [[ "$arg" == "-h" || "$arg" == "--help" ]] && { show_help; exit 0; }
done

# Parse arguments
OUTPUT_FILE=""
AGENT=""
METHOD=""
URL="$REMOTE_URL"
SENTRY_HOST=""
SCOPE="project"
DISABLED_SKILLS="${MCP_DISABLE_SKILLS:-}"

while [[ $# -gt 0 ]]; do
    case $1 in
        -o|--output) OUTPUT_FILE="$2"; shift 2 ;;
        --agent)     AGENT="$2"; shift 2 ;;
        --method)    METHOD="$2"; shift 2 ;;
        --url)       URL="$2"; shift 2 ;;
        --host)      SENTRY_HOST="$2"; shift 2 ;;
        --scope)     SCOPE="$2"; shift 2 ;;
        --disable-skills) DISABLED_SKILLS="$2"; shift 2 ;;
        *) log_error "Unknown option: $1"; exit 1 ;;
    esac
done

# jq required for config merge
if ! command -v jq &>/dev/null; then
    log_error "jq not found. Install with: brew install jq"
    exit 1
fi

# Interactive agent selection
if [[ -z "$AGENT" ]]; then
    printf "\n${YELLOW}Select the target agent:${NC}\n"
    printf "  1) Claude\n  2) GitHub Copilot\n"
    printf "Enter choice [1-2]: "
    read -n 1 -r AGENT_CHOICE; echo ""
    case $AGENT_CHOICE in
        1) AGENT="claude" ;;
        2) AGENT="copilot" ;;
        *) log_error "Invalid selection."; exit 1 ;;
    esac
fi

# Enforce supported agents (guards the --agent flag on every path, incl. with -o)
case "$AGENT" in
    claude|copilot) ;;
    *) log_error "Unsupported agent: ${AGENT}. Use claude or copilot."; exit 1 ;;
esac
case "$SCOPE" in
    project|user) ;;
    *) log_error "Invalid scope: ${SCOPE}. Use project or user."; exit 1 ;;
esac
if [[ "$SCOPE" == "user" && "$AGENT" != "copilot" ]]; then
    log_error "User scope is supported only for GitHub Copilot. Use --output for a custom Claude config path."
    exit 1
fi

# Interactive method selection
if [[ -z "$METHOD" ]]; then
    printf "\n${YELLOW}Select the installation method:${NC}\n"
    printf "  1) remote  (recommended — OAuth, no token stored)\n"
    printf "  2) stdio   (local npx process — needs a Sentry auth token)\n"
    printf "Enter choice [1-2]: "
    read -n 1 -r METHOD_CHOICE; echo ""
    case $METHOD_CHOICE in
        1) METHOD="remote" ;;
        2) METHOD="stdio" ;;
        *) log_error "Invalid selection."; exit 1 ;;
    esac
fi
[[ "$METHOD" != "remote" && "$METHOD" != "stdio" ]] && { log_error "Invalid method: ${METHOD}. Use remote or stdio."; exit 1; }

# Preserve the CLI --host before any env-file source can overwrite $SENTRY_HOST
CLI_HOST="$SENTRY_HOST"

# stdio requires Node/npx
NPX_COMMAND=""
NPX_DIR=""
if [[ "$METHOD" == "stdio" ]]; then
    if ! command -v npx &>/dev/null; then
        log_error "npx not found. Install Node.js >= 18, then restart your shell and re-run."
        exit 1
    fi
    NPX_COMMAND="$(command -v npx)"
    NPX_DIR="$(dirname "$NPX_COMMAND")"
fi

# Resolve output file
if [[ -z "$OUTPUT_FILE" ]]; then
    case "$AGENT" in
        claude)  OUTPUT_FILE="${PROJECT_ROOT}/.mcp.json" ;;
        copilot)
            if [[ "$SCOPE" == "user" ]]; then
                case "$(uname -s)" in
                    Darwin) OUTPUT_FILE="${HOME}/Library/Application Support/Code/User/mcp.json" ;;
                    Linux) OUTPUT_FILE="${XDG_CONFIG_HOME:-${HOME}/.config}/Code/User/mcp.json" ;;
                    MINGW*|MSYS*|CYGWIN*)
                        [[ -n "${APPDATA:-}" ]] || { log_error "APPDATA is required for Windows user scope."; exit 1; }
                        OUTPUT_FILE="${APPDATA}/Code/User/mcp.json"
                        ;;
                    *) log_error "Unsupported OS for Copilot user scope. Use --output to provide the config path."; exit 1 ;;
                esac
            else
                OUTPUT_FILE="${PROJECT_ROOT}/.vscode/mcp.json"
            fi
            ;;
        *) log_error "Invalid agent: ${AGENT}. Use claude or copilot."; exit 1 ;;
    esac
fi
log_info "Target config: ${OUTPUT_FILE}"

# Top-level key: Copilot/VS Code uses "servers", others use "mcpServers"
if [[ "$AGENT" == "copilot" ]]; then SERVERS_KEY="servers"; else SERVERS_KEY="mcpServers"; fi

# Build the server entry
INPUT_ENTRY=""
if [[ "$METHOD" == "remote" ]]; then
    log_info "Configuring remote Sentry MCP: ${URL}"
    SERVER_ENTRY=$(jq -n --arg url "$URL" '{"type":"http","url":$url}')
elif [[ "$AGENT" == "copilot" ]]; then
    # VS Code keeps promptString values out of mcp.json and asks when it starts the server.
    ENV_BLOCK=$(jq -n \
        --arg path "${NPX_DIR}:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin" \
        --arg token '${input:sentry-access-token}' \
        --arg host "$CLI_HOST" \
        --arg disabled "$DISABLED_SKILLS" \
        '{"PATH":$path,"SENTRY_ACCESS_TOKEN":$token}
         + (if $host == "" then {} else {"SENTRY_HOST":$host} end)
         + (if $disabled == "" then {} else {"MCP_DISABLE_SKILLS":$disabled} end)')
    SERVER_ENTRY=$(jq -n --arg command "$NPX_COMMAND" --argjson env "$ENV_BLOCK" \
        '{"command":$command,"args":["-y","@sentry/mcp-server@latest"],"env":$env}')
    INPUT_ENTRY=$(jq -n \
        '{"id":"sentry-access-token","type":"promptString","description":"Sentry access token","password":true}')
else
    # stdio — collect / reuse the auth token from the global env file
    if [[ -f "${GLOBAL_ENV_FILE}" ]]; then
        log_info "Existing credential file found: ${GLOBAL_ENV_FILE}"
        printf "${YELLOW}Reuse existing Sentry token?${NC} (Y/n): "
        read -n 1 -r REUSE_CREDS; echo ""
        if [[ ! "$REUSE_CREDS" =~ ^[Nn]$ ]]; then
            set -a; source "${GLOBAL_ENV_FILE}"; set +a
            log_success "Loaded stored Sentry token"
        fi
    fi
    if [[ -z "${SENTRY_ACCESS_TOKEN:-}" ]]; then
        printf "\n${YELLOW}Enter your Sentry user auth token.${NC}\n"
        printf "Create one at: https://sentry.io/settings/account/api/auth-tokens/\n"
        printf "Scopes: org:read, project:read, project:write, team:read, team:write, event:write\n\n"
        printf "${YELLOW}Sentry Auth Token:${NC} "
        read -s SENTRY_ACCESS_TOKEN; echo ""
        [[ -z "$SENTRY_ACCESS_TOKEN" ]] && { log_error "Sentry auth token is required"; exit 1; }
    fi
    # CLI --host wins; otherwise keep whatever was sourced from the env file
    STORED_HOST="${CLI_HOST:-${SENTRY_HOST:-}}"

    log_info "Storing token in: ${GLOBAL_ENV_FILE}"
    mkdir -p "$(dirname "${GLOBAL_ENV_FILE}")"
    {
        printf "SENTRY_ACCESS_TOKEN=%q\n" "$SENTRY_ACCESS_TOKEN"
        [[ -n "$STORED_HOST" ]] && printf "SENTRY_HOST=%q\n" "$STORED_HOST"
        [[ -n "$DISABLED_SKILLS" ]] && printf "MCP_DISABLE_SKILLS=%q\n" "$DISABLED_SKILLS"
    } > "${GLOBAL_ENV_FILE}"
    chmod 600 "${GLOBAL_ENV_FILE}"
    log_success "Token stored in ${GLOBAL_ENV_FILE}"

    SHELL_COMMAND="set -a; . \"${GLOBAL_ENV_FILE}\"; set +a; exec \"${NPX_COMMAND}\" -y @sentry/mcp-server@latest"
    SERVER_ENTRY=$(jq -n --arg command "$SHELL_COMMAND" \
        '{"command":"bash","args":["-lc",$command]}')
fi

mkdir -p "$(dirname "$OUTPUT_FILE")"

# Merge into existing config (preserve other servers) or create fresh
if [[ -n "$INPUT_ENTRY" ]]; then
    if [[ -f "$OUTPUT_FILE" && -s "$OUTPUT_FILE" ]]; then
        jq --arg k "$SERVERS_KEY" --arg inputId "sentry-access-token" \
            --argjson entry "$SERVER_ENTRY" --argjson input "$INPUT_ENTRY" \
            '(.[$k] //= {}) | .[$k].sentry = $entry | (.inputs //= []) |
             .inputs = ((.inputs | map(select(.id != $inputId))) + [$input])' \
            "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
    else
        jq -n --arg k "$SERVERS_KEY" --argjson entry "$SERVER_ENTRY" --argjson input "$INPUT_ENTRY" \
            '{($k): {"sentry": $entry}, "inputs": [$input]}' > "$OUTPUT_FILE"
    fi
else
    MCP_CONFIG=$(jq -n --arg k "$SERVERS_KEY" --argjson entry "$SERVER_ENTRY" \
        '{($k): {"sentry": $entry}}')
    if [[ -f "$OUTPUT_FILE" && -s "$OUTPUT_FILE" ]]; then
        jq --arg k "$SERVERS_KEY" --argjson entry "$SERVER_ENTRY" \
            '(.[$k] //= {}) | .[$k].sentry = $entry' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" \
            && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"
    else
        echo "$MCP_CONFIG" | jq '.' > "$OUTPUT_FILE"
    fi
fi

log_success "Written to: ${OUTPUT_FILE}"
printf "\n${GREEN}Done!${NC} Restart your agent to load Sentry MCP.\n"
if [[ "$METHOD" == "remote" ]]; then
    printf "First Sentry tool call opens a browser to authorize (OAuth).\n"
fi
if [[ "$AGENT" == "copilot" && "$METHOD" == "stdio" ]]; then
    printf "VS Code will securely prompt for the Sentry access token when it starts the server.\n"
fi
if [[ "$AGENT" == "copilot" && "$SCOPE" == "project" ]]; then
    printf "Note: .vscode/mcp.json may need 'git add -f' if .vscode/ is gitignored.\n"
fi
