#!/bin/bash

# import-skills.sh
# Automates importing skills from .agent-settings/skills/ to agent-specific folders

set -e

# Colors for output (use --no-color to disable)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Disable colors if --no-color flag is set or NO_COLOR env var exists
if [[ "${NO_COLOR:-}" != "" ]] || [[ "$*" == *"--no-color"* ]]; then
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# Get the script directory (now in .agent-settings/skills/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENT_SETTINGS_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="${PROJECT_ROOT:-$(dirname "$AGENT_SETTINGS_DIR")}"
SKILLS_SOURCE="$SCRIPT_DIR"

# Function to print colored output
print_success() {
    printf "${GREEN}✓${NC} %s\n" "$1"
}

print_error() {
    printf "${RED}✗${NC} %s\n" "$1"
}

print_info() {
    printf "${BLUE}ℹ${NC} %s\n" "$1"
}

print_warning() {
    printf "${YELLOW}⚠${NC} %s\n" "$1"
}

# Function to calculate relative path
get_relative_path() {
    # Check if python3 is available
    if command -v python3 &> /dev/null; then
        python3 -c "import os.path, sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" "$1" "$2"
    else
        # Fallback for systems without python3 (simple common directory case)
        local source=$1
        local target=$2
        local common_part=$source
        local result=""

        while [[ "${target#$common_part}" == "${target}" ]]; do
            common_part=$(dirname $common_part)
            result="../$result"
        done

        if [[ $common_part == "/" ]]; then
            echo "$source"
        else
            local forward_part=${source#$common_part/}
            echo "${result}${forward_part}"
        fi
    fi
}

# Function to get all available skills
get_available_skills() {
    if [ ! -d "$SKILLS_SOURCE" ]; then
        print_error "Skills directory not found: $SKILLS_SOURCE"
        exit 1
    fi

    find "$SKILLS_SOURCE" -mindepth 1 -maxdepth 1 -type d -exec basename {} \;
}

# Function to create symlink
create_skill_link() {
    local agent_name=$1
    # Map 'antigravity' to 'agent' folder convention
    if [ "$agent_name" = "antigravity" ]; then
        agent_name="agent"
    fi
    local skill_name=$2
    local agent_dir="$PROJECT_ROOT/.$agent_name"
    local skills_dir="$agent_dir/skills"
    local link_path="$skills_dir/$skill_name"

    # Calculate relative path from skills_dir to SKILLS_SOURCE
    local rel_path=$(get_relative_path "$SKILLS_SOURCE" "$skills_dir")
    local target_path="$rel_path/$skill_name"

    # Create skills directory if it doesn't exist
    if [ ! -d "$skills_dir" ]; then
        mkdir -p "$skills_dir"
        print_info "Created directory: $skills_dir"
    fi

    # Check if link already exists
    if [ -L "$link_path" ]; then
        local current_target=$(readlink "$link_path")
        if [ "$current_target" = "$target_path" ]; then
            print_info "Symlink already exists and is correct: $link_path"
            return 0
        else
            print_warning "Symlink exists but points to wrong target: $link_path -> $current_target"
            print_info "Removing old symlink..."
            rm "$link_path"
        fi
    elif [ -e "$link_path" ]; then
        print_error "Path exists but is not a symlink: $link_path"
        print_warning "Skipping to avoid overwriting..."
        return 1
    fi

    # Create symlink
    cd "$skills_dir"
    ln -s "$target_path" "$skill_name"
    cd - > /dev/null

    print_success "Created symlink: .$agent_name/skills/$skill_name -> $target_path"
}

# Function to import all skills to an agent
import_all_skills() {
    local agent_name=$1
    local skills=($(get_available_skills))

    if [ ${#skills[@]} -eq 0 ]; then
        print_warning "No skills found in $SKILLS_SOURCE"
        return
    fi

    echo ""
    print_info "Importing ${#skills[@]} skill(s) to .$agent_name..."
    echo ""

    for skill in "${skills[@]}"; do
        create_skill_link "$agent_name" "$skill"
    done
}

# Function to import specific skills to an agent
import_specific_skills() {
    local agent_name=$1
    shift
    local skills=("$@")

    echo ""
    print_info "Importing ${#skills[@]} skill(s) to .$agent_name..."
    echo ""

    for skill in "${skills[@]}"; do
        if [ ! -d "$SKILLS_SOURCE/$skill" ]; then
            print_error "Skill not found: $skill"
            continue
        fi
        create_skill_link "$agent_name" "$skill"
    done
}

# Function to list available skills
list_skills() {
    local skills=($(get_available_skills))

    echo ""
    echo "Available skills in .agent-settings/skills/:"
    echo ""

    if [ ${#skills[@]} -eq 0 ]; then
        print_warning "No skills found"
        return
    fi

    for skill in "${skills[@]}"; do
        echo "  • $skill"
    done
    echo ""
}

# Function to verify symlinks for an agent
verify_agent_links() {
    local agent_name=$1
    # Map 'antigravity' to 'agent' folder convention
    if [ "$agent_name" = "antigravity" ]; then
        agent_name="agent"
    fi
    local skills_dir="$PROJECT_ROOT/.$agent_name/skills"

    if [ ! -d "$skills_dir" ]; then
        print_warning "No skills directory found for .$agent_name"
        return
    fi

    echo ""
    print_info "Verifying symlinks for .$agent_name..."
    echo ""

    local link_count=0
    local valid_count=0
    local broken_count=0

    for link in "$skills_dir"/*; do
        if [ ! -e "$link" ]; then
            continue
        fi

        link_count=$((link_count + 1))
        local skill_name=$(basename "$link")

        if [ -L "$link" ]; then
            local target=$(readlink "$link")
            if [ -d "$link" ]; then
                print_success "$skill_name -> $target"
                valid_count=$((valid_count + 1))
            else
                print_error "$skill_name -> $target (broken link)"
                broken_count=$((broken_count + 1))
            fi
        else
            print_warning "$skill_name (not a symlink)"
        fi
    done

    echo ""
    print_info "Total: $link_count | Valid: $valid_count | Broken: $broken_count"
}

# Function to generate a GitHub Agent file from a SKILL.md (Spec-kit style)
generate_copilot_agent_file() {
    local skill_name=$1
    local skill_md="$SKILLS_SOURCE/$skill_name/SKILL.md"
    local agents_dir="$PROJECT_ROOT/.github/agents"
    local output_file="$agents_dir/agent-settings.$skill_name.agent.md"

    if [ ! -f "$skill_md" ]; then
        print_error "SKILL.md not found: $skill_md"
        return 1
    fi

    mkdir -p "$agents_dir"

    # Extract description value from YAML frontmatter
    local description
    description=$(awk '
        BEGIN { in_fm=0 }
        NR==1 && /^---$/ { in_fm=1; next }
        in_fm && /^---$/ { exit }
        in_fm && /^description:/ {
            val = $0
            sub(/^description:[[:space:]]*/, "", val)
            # Remove surrounding quotes if they exist
            gsub(/^"|"$/, "", val)
            print val
            exit
        }
    ' "$skill_md")

    # Extract body
    local body
    # Detect if there's a third separator (often used to separate Gemini CLI meta-instructions from agent steps)
    local dash_count=$(grep -c "^---$" "$skill_md" || true)
    if [ "$dash_count" -ge 3 ]; then
        # Take everything after the third --- to get the core agent instructions
        body=$(awk '
            BEGIN { dashes=0 }
            /^---$/ { dashes++; next }
            dashes >= 3 { print }
        ' "$skill_md")
    else
        # Take everything after the frontmatter
        body=$(awk '
            BEGIN { dashes=0 }
            /^---$/ { dashes++; next }
            dashes >= 2 { print }
        ' "$skill_md")
    fi

    # Write GitHub Agent file with Proactive Action Directive
    {
        printf '%s\n' '---'
        printf 'description: %s\n' "$description"
        printf '%s\n' '---'
        printf '\n> [!IMPORTANT]\n'
        printf '> **COPILOT EXECUTION MANDATE**: You are now in "Automated-Draft Mode". Upon being invoked:\n'
        printf '> 1. **Immediate Execution**: Use your tools (terminal, git, etc.) immediately to gather context (git status, diffs, etc.).\n'
        printf '> 2. **Automate Choices**: Automate all technical decisions (Scope, Branch, Commit Type) by analyzing the environment. Do not ask the user to choose these unless you are completely unable to proceed.\n'
        printf '> 3. **Single Interaction**: The ONLY question you should proactively ask the user is for the **Jira Ticket ID**. Ask this while simultaneously showing your draft.\n'
        printf '> 4. **Draft then Ask**: Your primary goal is the final result. Provide a draft immediately (using placeholders if necessary) and ask for the Jira ID in the same message.\n'
        printf '> 5. **Mandatory Output**: Never end a response with just a status update. Always show the current state of your work or the final result.\n\n'
        printf '%s\n' "$body"
    } > "$output_file"

    print_success "Created GitHub Agent: .github/agents/agent-settings.$skill_name.agent.md"
}

# Function to create/update .github/copilot-instructions.md with skills table and invocation convention
generate_copilot_instructions() {
    local skills=("$@")
    local instructions_file="$PROJECT_ROOT/.github/copilot-instructions.md"
    local github_dir="$PROJECT_ROOT/.github"
    local sentinel_begin="<!-- BEGIN AGENT-SETTINGS SKILLS -->"
    local sentinel_end="<!-- END AGENT-SETTINGS SKILLS -->"

    mkdir -p "$github_dir"

    # Build managed block in a temp file
    local tmp_block
    tmp_block="$(mktemp)"

    printf '%s\n' "$sentinel_begin" >> "$tmp_block"
    printf '## Skill Invocation Convention\n\n' >> "$tmp_block"
    printf 'Invoke a skill in Copilot Chat by typing `/` or `@@` and selecting the desired agent from the menu (e.g., `/agent-settings.generate-pr-notes` or `@@agent-settings.generate-pr-notes`).\n\n' >> "$tmp_block"
    printf '### Available Skills\n\n' >> "$tmp_block"
    printf '| Skill | Description | Agent Instruction File |\n' >> "$tmp_block"
    printf '|-------|-------------|------------------------|\n' >> "$tmp_block"

    for skill in "${skills[@]}"; do
        local skill_md="$SKILLS_SOURCE/$skill/SKILL.md"
        local desc=""
        if [ -f "$skill_md" ]; then
            desc=$(awk '
                BEGIN { in_fm=0 }
                NR==1 && /^---$/ { in_fm=1; next }
                in_fm && /^---$/ { exit }
                in_fm && /^description:/ {
                    val = $0
                    sub(/^description:[[:space:]]*/, "", val)
                    # Remove surrounding quotes if they exist
                    gsub(/^"|"$/, "", val)
                    if (length(val) > 80) val = substr(val, 1, 80) "..."
                    print val
                    exit
                }
            ' "$skill_md")
        fi
        printf '| %s | %s | `agent-settings.%s.agent.md` |\n' "$skill" "$desc" "$skill" >> "$tmp_block"
    done

    printf '\n### How to Use\n' >> "$tmp_block"
    printf '1. Open Copilot Chat (`Ctrl+Shift+I` / `Cmd+Shift+I`)\n' >> "$tmp_block"
    printf '2. Type `/` or `@@` to see the list of available agents\n' >> "$tmp_block"
    printf '3. Select `agent-settings.<skill-name>` to load the skill instructions\n' >> "$tmp_block"
    printf '4. Copilot will follow the instructions defined in the selected agent file\n' >> "$tmp_block"
    printf '%s\n' "$sentinel_end" >> "$tmp_block"

    if [ ! -f "$instructions_file" ]; then
        # Create fresh file with header
        {
            printf '# GitHub Copilot Instructions\n\n'
            printf 'This file configures GitHub Copilot'\''s behavior for this project.\n\n'
            cat "$tmp_block"
        } > "$instructions_file"
        print_success "Created .github/copilot-instructions.md"
    else
        if grep -qF "$sentinel_begin" "$instructions_file"; then
            # Replace existing managed block
            local tmp_result
            tmp_result="$(mktemp)"
            awk -v begin="$sentinel_begin" -v end="$sentinel_end" -v blockfile="$tmp_block" '
                $0 == begin {
                    while ((getline line < blockfile) > 0) print line
                    close(blockfile)
                    skip=1
                    next
                }
                $0 == end { skip=0; next }
                !skip { print }
            ' "$instructions_file" > "$tmp_result"
            cat "$tmp_result" > "$instructions_file"
            rm -f "$tmp_result"
            print_success "Updated skills section in .github/copilot-instructions.md"
        else
            # Append managed block to existing file
            printf '\n' >> "$instructions_file"
            cat "$tmp_block" >> "$instructions_file"
            print_success "Added skills section to .github/copilot-instructions.md"
        fi
    fi

    rm -f "$tmp_block"
}

# Function to verify GitHub Agent files
verify_copilot_agents() {
    local agents_dir="$PROJECT_ROOT/.github/agents"

    echo ""
    print_info "Verifying GitHub Agent files in .github/agents/..."
    echo ""

    if [ ! -d "$agents_dir" ]; then
        print_warning "No .github/agents/ directory found"
        return
    fi

    local total=0
    local valid=0

    for f in "$agents_dir"/agent-settings.*.agent.md; do
        [ -e "$f" ] || continue
        total=$((total + 1))
        local has_desc
        has_desc=$(grep -c "^description:" "$f" || true)
        if [ "$has_desc" -gt 0 ]; then
            print_success "$(basename "$f")"
            valid=$((valid + 1))
        else
            print_error "$(basename "$f") (missing description: frontmatter)"
        fi
    done

    echo ""
    print_info "Total: $total | Valid: $valid"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] AGENT_NAME [SKILL_NAMES...]

Automates importing skills from .agent-settings/skills/ to agent-specific folders.

Arguments:
  AGENT_NAME          Target agent folder name (e.g., agent, claude, gemini, copilot)
                      Note: 'antigravity' will be automatically mapped to 'agent'
                      Note: 'copilot' generates files in .github/agents/ instead of symlinks

Options:
  -a, --all          Import all available skills (default if no skills specified)
  -l, --list         List all available skills
  -v, --verify       Verify existing symlinks/files for the specified agent
  -h, --help         Show this help message

Examples:
  # Import all skills to Antigravity (targets .agent folder)
  $0 agent

  # Or use the 'antigravity' alias
  $0 antigravity

  # Import all skills to Claude agent
  $0 claude

  # Import all skills to GitHub Copilot (generates .github/agents/ files)
  $0 copilot

  # Import all skills with --all flag
  $0 --all claude

  # Import specific skills to Claude agent
  $0 claude generate-pr-notes git-commit-conventional-strict

  # Import all skills to multiple agents (run separately)
  $0 claude
  $0 gemini
  $0 copilot

  # List available skills
  $0 --list

  # Verify symlinks for Claude agent
  $0 --verify claude

  # Verify Copilot Agent files
  $0 --verify copilot

EOF
}

# Main script logic
main() {
    local mode="import"
    local import_all=false
    local agent_name=""
    local skills=()

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -l|--list)
                mode="list"
                shift
                ;;
            -v|--verify)
                mode="verify"
                shift
                ;;
            -a|--all)
                import_all=true
                shift
                ;;
            -*)
                print_error "Unknown option: $1"
                echo ""
                show_usage
                exit 1
                ;;
            *)
                if [ -z "$agent_name" ]; then
                    agent_name=$1
                else
                    skills+=("$1")
                fi
                shift
                ;;
        esac
    done

    # Execute based on mode
    case $mode in
        list)
            list_skills
            ;;
        verify)
            if [ -z "$agent_name" ]; then
                print_error "Agent name required for verify mode"
                echo ""
                show_usage
                exit 1
            fi
            if [ "$agent_name" = "copilot" ]; then
                verify_copilot_agents
            else
                verify_agent_links "$agent_name"
            fi
            ;;
        import)
            if [ -z "$agent_name" ]; then
                print_error "Agent name required"
                echo ""
                show_usage
                exit 1
            fi

            if [ "$agent_name" = "copilot" ]; then
                local copilot_skills
                if [ ${#skills[@]} -eq 0 ] || [ "$import_all" = true ]; then
                    copilot_skills=($(get_available_skills))
                else
                    copilot_skills=("${skills[@]}")
                fi

                echo ""
                print_info "Importing ${#copilot_skills[@]} skill(s) to GitHub Copilot (as Agents)..."
                echo ""

                for skill in "${copilot_skills[@]}"; do
                    if [ ! -d "$SKILLS_SOURCE/$skill" ]; then
                        print_error "Skill not found: $skill"
                        continue
                    fi
                    generate_copilot_agent_file "$skill"
                done

                generate_copilot_instructions "${copilot_skills[@]}"

                echo ""
                print_success "Import complete!"
                echo ""
                print_info "Commit .github/agents/ and .github/copilot-instructions.md to share with your team."
                print_info "You can verify with: PROJECT_ROOT=\"$PROJECT_ROOT\" $0 --verify copilot"
            else
                if [ ${#skills[@]} -eq 0 ] || [ "$import_all" = true ]; then
                    import_all_skills "$agent_name"
                else
                    import_specific_skills "$agent_name" "${skills[@]}"
                fi

                echo ""
                print_success "Import complete!"
                echo ""
                print_info "You can verify the links with: PROJECT_ROOT=\"$PROJECT_ROOT\" $0 --verify $agent_name"
            fi
            ;;
    esac
}

# Run main function
main "$@"
