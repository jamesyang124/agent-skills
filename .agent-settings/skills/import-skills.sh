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
PROJECT_ROOT="$(dirname "$AGENT_SETTINGS_DIR")"
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
    local target_path="../../.agent-settings/skills/$skill_name"

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

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] AGENT_NAME [SKILL_NAMES...]

Automates importing skills from .agent-settings/skills/ to agent-specific folders.

Arguments:
  AGENT_NAME          Target agent folder name (e.g., agent, claude, gemini)
                      Note: 'antigravity' will be automatically mapped to 'agent'

Options:
  -a, --all          Import all available skills (default if no skills specified)
  -l, --list         List all available skills
  -v, --verify       Verify existing symlinks for the specified agent
  -h, --help         Show this help message

Examples:
  # Import all skills to Antigravity (targets .agent folder)
  $0 agent
  
  # Or use the 'antigravity' alias
  $0 antigravity

  # Import all skills to Claude agent
  $0 claude

  # Import all skills with --all flag
  $0 --all claude

  # Import specific skills to Claude agent
  $0 claude generate-pr-notes git-commit-conventional-strict

  # Import all skills to multiple agents (run separately)
  $0 claude
  $0 gemini

  # List available skills
  $0 --list

  # Verify symlinks for Claude agent
  $0 --verify claude

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
            verify_agent_links "$agent_name"
            ;;
        import)
            if [ -z "$agent_name" ]; then
                print_error "Agent name required"
                echo ""
                show_usage
                exit 1
            fi

            if [ ${#skills[@]} -eq 0 ] || [ "$import_all" = true ]; then
                import_all_skills "$agent_name"
            else
                import_specific_skills "$agent_name" "${skills[@]}"
            fi

            echo ""
            print_success "Import complete!"
            echo ""
            print_info "You can verify the links with: $0 --verify $agent_name"
            ;;
    esac
}

# Run main function
main "$@"
