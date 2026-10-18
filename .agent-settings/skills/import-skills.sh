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
GLOBAL=false
ORIG_PWD="$PWD"
DEDUP_PROJECT=""
PICK=false

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

# Resolve a skill name to its full path (under tools/ or workflows/)
find_skill_path() {
    local skill_name=$1
    local result
    result=$(find "$SKILLS_SOURCE" -mindepth 2 -maxdepth 2 -type d -name "$skill_name" | head -1)
    echo "$result"
}

# Function to get all available skills (excludes playground/)
get_available_skills() {
    if [ ! -d "$SKILLS_SOURCE" ]; then
        print_error "Skills directory not found: $SKILLS_SOURCE"
        exit 1
    fi

    find "$SKILLS_SOURCE" -mindepth 2 -maxdepth 2 -type d \
        ! -path "$SKILLS_SOURCE/playground/*" \
        -exec basename {} \;
}

# Function to get playground skills only
get_playground_skills() {
    local playground_dir="$SKILLS_SOURCE/playground"
    if [ ! -d "$playground_dir" ]; then
        return
    fi
    find "$playground_dir" -mindepth 1 -maxdepth 1 -type d -exec basename {} \;
}

# Interactively prompt the user to multi-select playground skills via checkbox menu
# Navigation: ↑/↓ to move cursor, space to toggle, a=all, n=none, Enter=confirm, q=skip
prompt_playground_skills() {
    local agent_name=$1
    local playground_skills=()
    while IFS= read -r line; do
        [ -n "$line" ] && playground_skills+=("$line")
    done < <(get_playground_skills)

    if [ ${#playground_skills[@]} -eq 0 ]; then
        return
    fi

    local count=${#playground_skills[@]}
    local checked=()
    local cursor=0
    local i=0
    while [ $i -lt $count ]; do
        checked+=("0")
        i=$((i + 1))
    done

    # Fixed menu height: 8 lines of chrome + count skill lines
    # (blank + sep + title + sep + blank + N skills + blank + legend + blank)
    local menu_height=$((count + 8))

    _print_playground_menu() {
        echo ""
        printf "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
        printf "${YELLOW}  Playground Skills (experimental / opt-in)${NC}\n"
        printf "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
        echo ""
        local j=0
        while [ $j -lt $count ]; do
            local box="[ ]"
            [ "${checked[$j]}" = "1" ] && box="[✓]"
            if [ "$j" = "$cursor" ]; then
                printf "  ${BLUE}▶ %s %s${NC}\n" "$box" "${playground_skills[$j]}"
            else
                printf "    %s %s\n" "$box" "${playground_skills[$j]}"
            fi
            j=$((j + 1))
        done
        echo ""
        printf "  ${BLUE}↑/↓${NC}=move  ${BLUE}space${NC}=toggle  ${BLUE}a${NC}=all  ${BLUE}n${NC}=none  ${BLUE}Enter${NC}=confirm  ${BLUE}q${NC}=skip\n"
        echo ""
    }

    _print_playground_menu

    while true; do
        IFS= read -r -s -n 1 key

        if [[ "$key" = $'\e' ]]; then
            # Arrow key escape sequence: read remaining 2 bytes of ESC [ A/B
            IFS= read -r -s -n 2 seq
            case "$seq" in
                "[A") [ "$cursor" -gt 0 ] && cursor=$((cursor - 1)) ;;
                "[B") [ "$cursor" -lt $((count - 1)) ] && cursor=$((cursor + 1)) ;;
            esac
        elif [[ "$key" = " " ]]; then
            if [ "${checked[$cursor]}" = "1" ]; then
                checked[$cursor]="0"
            else
                checked[$cursor]="1"
            fi
        elif [[ "$key" = "a" ]] || [[ "$key" = "A" ]]; then
            local j=0
            while [ $j -lt $count ]; do
                checked[$j]="1"
                j=$((j + 1))
            done
        elif [[ "$key" = "n" ]] || [[ "$key" = "N" ]]; then
            local j=0
            while [ $j -lt $count ]; do
                checked[$j]="0"
                j=$((j + 1))
            done
        elif [[ "$key" = "" ]]; then
            # Enter key — confirm
            break
        elif [[ "$key" = "q" ]] || [[ "$key" = "0" ]]; then
            printf "\033[%dA\033[J" "$menu_height"
            print_info "Skipping playground skills."
            return
        fi

        # Redraw in-place: move up menu_height lines, clear to bottom, reprint
        printf "\033[%dA\033[J" "$menu_height"
        _print_playground_menu
    done

    # Clear the menu before showing import results
    printf "\033[%dA\033[J" "$menu_height"

    # Collect confirmed selections
    local selected_skills=()
    local j=0
    while [ $j -lt $count ]; do
        [ "${checked[$j]}" = "1" ] && selected_skills+=("${playground_skills[$j]}")
        j=$((j + 1))
    done

    if [ ${#selected_skills[@]} -eq 0 ]; then
        print_info "No playground skills selected."
        return
    fi

    echo ""
    print_info "Importing ${#selected_skills[@]} playground skill(s)..."
    echo ""

    for skill in "${selected_skills[@]}"; do
        create_skill_link "$agent_name" "$skill"
    done
}

# Resolve the canonical agent name (handles aliases).
resolve_agent_name() {
    local agent_name=$1
    case "$agent_name" in
        copilot)     echo "claude" ;;  # Copilot reads from .claude folder
        *)           echo "$agent_name" ;;
    esac
}

# Resolve the skills directory for a given agent name.
# Returns the absolute path to the agent's skills directory.
get_agent_skills_dir() {
    local agent_name
    agent_name=$(resolve_agent_name "$1")
    echo "$PROJECT_ROOT/.$agent_name/skills"
}

# True if the symlink at $1 points into this repo's skills tree (i.e. we own it).
is_owned_link() {
    local resolved
    resolved=$(cd "$(dirname "$1")" && cd "$(dirname "$(readlink "$1")")" 2>/dev/null && pwd -P)
    [[ "$resolved" == "$(cd "$SKILLS_SOURCE" && pwd -P)"/* ]]
}

# Function to create symlink
create_skill_link() {
    local agent_name
    agent_name=$(resolve_agent_name "$1")
    local skill_name=$2
    local skills_dir
    skills_dir=$(get_agent_skills_dir "$agent_name")
    local link_path="$skills_dir/$skill_name"

    # Resolve skill to its category subdir (tools/ or workflows/)
    local skill_abs_path
    skill_abs_path=$(find_skill_path "$skill_name")
    if [ -z "$skill_abs_path" ]; then
        print_error "Skill not found: $skill_name"
        return 1
    fi

    local target_path
    target_path=$(get_relative_path "$skill_abs_path" "$skills_dir")

    # Create skills directory if it doesn't exist
    if [ ! -d "$skills_dir" ]; then
        mkdir -p "$skills_dir"
        print_info "Created directory: $skills_dir"
    fi

    # Check if link already exists
    if [ -L "$link_path" ]; then
        local current_target
        current_target=$(readlink "$link_path")
        if [ "$current_target" = "$target_path" ]; then
            print_info "Symlink already exists and is correct: $link_path"
            return 0
        else
            if [ "$GLOBAL" = true ] && ! is_owned_link "$link_path"; then
                print_warning "Skipping $skill_name: global link owned by something else ($current_target)"
                return 0
            fi
            print_warning "Symlink exists but points to wrong target: $link_path -> $current_target"
            print_info "Removing old symlink..."
            rm "$link_path"
        fi
    elif [ -e "$link_path" ]; then
        print_error "Path exists but is not a symlink: $link_path"
        print_warning "Skipping to avoid overwriting..."
        return 1
    fi

    # Create symlink (cd into target dir first for reliable relative symlinks)
    cd "$skills_dir"
    ln -s "$target_path" "$skill_name"
    cd - > /dev/null
    print_success "Created symlink: .$agent_name/skills/$skill_name -> $target_path"
}

# Function to import all skills to an agent
import_all_skills() {
    local agent_name
    agent_name=$(resolve_agent_name "$1")
    local skills=($(get_available_skills))

    if [ ${#skills[@]} -eq 0 ]; then
        print_warning "No skills found in $SKILLS_SOURCE"
        return
    fi

    local skills_dir
    skills_dir=$(get_agent_skills_dir "$agent_name")

    # Remove all existing symlinks first so no stale skills linger
    if [ -d "$skills_dir" ]; then
        print_info "Removing existing skills from .$agent_name/skills..."
        for link in "$skills_dir"/*; do
            if [ -L "$link" ]; then
                if [ "$GLOBAL" != true ] || is_owned_link "$link"; then rm "$link"; fi
            fi
        done
    fi

    echo ""
    print_info "Importing ${#skills[@]} skill(s) to .$agent_name/skills..."
    echo ""

    for skill in "${skills[@]}"; do
        create_skill_link "$agent_name" "$skill"
    done
}

# Function to import specific skills to an agent
import_specific_skills() {
    local agent_name
    agent_name=$(resolve_agent_name "$1")
    shift
    local skills=("$@")

    echo ""
    print_info "Importing ${#skills[@]} skill(s) to .$agent_name/skills..."
    echo ""

    for skill in "${skills[@]}"; do
        if [ -z "$(find_skill_path "$skill")" ]; then
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
    local agent_name
    agent_name=$(resolve_agent_name "$1")
    local skills_dir
    skills_dir=$(get_agent_skills_dir "$agent_name")

    if [ ! -d "$skills_dir" ]; then
        print_warning "No skills directory found for .$agent_name/skills"
        return
    fi

    echo ""
    print_info "Verifying symlinks for .$agent_name/skills..."
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

# Function to prune orphaned skills for an agent
prune_agent_skills() {
    local agent_name
    agent_name=$(resolve_agent_name "$1")
    local force=${2:-false}
    local skills_dir
    skills_dir=$(get_agent_skills_dir "$agent_name")

    if [ ! -d "$skills_dir" ]; then
        print_warning "No skills directory found for .$agent_name/skills"
        return
    fi

    echo ""
    print_info "Scanning for orphaned skills in .$agent_name/skills..."
    echo ""

    local pruned=0
    local skipped=0

    for link in "$skills_dir"/*; do
        [ -e "$link" ] || [ -L "$link" ] || continue
        local skill_name
        skill_name=$(basename "$link")
        # Global dirs hold other tools' skills: only prune symlinks that point into this repo.
        if [ "$GLOBAL" = true ] && { [ ! -L "$link" ] || ! is_owned_link "$link"; }; then
            continue
        fi

        if [ -z "$(find_skill_path "$skill_name")" ]; then
            if [ -L "$link" ]; then
                print_warning "Orphaned symlink: $skill_name (source no longer exists)"
            else
                print_warning "Orphaned entry: $skill_name (source no longer exists)"
            fi

            if [ "$force" = true ]; then
                rm -rf "$link"
                print_success "Removed: $skill_name"
                pruned=$((pruned + 1))
            else
                while true; do
                    printf "  Remove? (y/n) "
                    read -r answer
                    if [[ "$answer" =~ ^[Yy]$ ]]; then
                        rm -rf "$link"
                        print_success "Removed: $skill_name"
                        pruned=$((pruned + 1))
                        break
                    elif [[ "$answer" =~ ^[Nn]$ ]]; then
                        print_info "Skipped: $skill_name"
                        skipped=$((skipped + 1))
                        break
                    fi
                    # blank or other — re-prompt
                done
            fi
        fi
    done

    echo ""
    if [ $pruned -eq 0 ] && [ $skipped -eq 0 ]; then
        print_success "No orphaned skills found for .$agent_name/skills"
    else
        print_info "Pruned: $pruned | Skipped: $skipped"
    fi
}

# True if the symlink at $1 points into any agent-settings skills tree (this checkout or a repo's submodule copy).
is_agent_settings_link() {
    [ -L "$1" ] || return 1
    local resolved
    resolved=$(cd "$(dirname "$1")" && cd "$(readlink "$1")" 2>/dev/null && pwd -P) || return 1
    [[ "$resolved" == */.agent-settings/skills/* ]]
}

# The project whose skills are compared with the global ones.
dedup_project_root() {
    if [ -n "$DEDUP_PROJECT" ]; then (cd "$DEDUP_PROJECT" && pwd -P); return; fi
    if [ "$GLOBAL" = true ]; then git -C "$ORIG_PWD" rev-parse --show-toplevel 2>/dev/null; return; fi
    (cd "$PROJECT_ROOT" && pwd -P)
}

# Remove skills that are installed both globally and in a project (both show up in the agent).
# $2 = auto: clean without asking; ask: one Y/n for all; report: list only. --pick asks per skill.
dedup_skills() {
    local agent_name
    agent_name=$(resolve_agent_name "$1")
    local how=$2
    local project
    project=$(dedup_project_root)
    local global_dir="$HOME/.$agent_name/skills"
    [ -n "$project" ] && [ "$project" != "$(cd "$HOME" && pwd -P)" ] || return 0
    local project_dir="$project/.$agent_name/skills"
    [ -d "$global_dir" ] && [ -d "$project_dir" ] || return 0

    local removable=() committed=() foreign=()
    local link name
    for link in "$project_dir"/*; do
        [ -L "$link" ] || [ -e "$link" ] || continue
        name=$(basename "$link")
        [ -e "$global_dir/$name" ] || [ -L "$global_dir/$name" ] || continue
        if ! is_agent_settings_link "$link" || ! is_agent_settings_link "$global_dir/$name"; then
            foreign+=("$name")
        elif git -C "$project" ls-files --error-unmatch ".$agent_name/skills/$name" >/dev/null 2>&1; then
            committed+=("$name")
        else
            removable+=("$name")
        fi
    done
    [ $((${#removable[@]} + ${#committed[@]} + ${#foreign[@]})) -gt 0 ] || return 0

    echo ""
    print_warning "Skills installed both globally (~/.$agent_name/skills) and in $project (they show up twice):"
    [ ${#removable[@]} -gt 0 ] && print_info "  can clean (project link, not committed): ${removable[*]}"
    [ ${#committed[@]} -gt 0 ] && print_info "  committed in the repo — remove them there in a PR: ${committed[*]}"
    [ ${#foreign[@]} -gt 0 ] && print_info "  not agent-settings links, left alone: ${foreign[*]}"
    [ ${#removable[@]} -gt 0 ] || return 0

    if [ "$PICK" = true ] && [ -t 0 ]; then
        for name in "${removable[@]}"; do
            printf "  %s: keep (g)lobal, keep (p)roject — removes the global link for every repo — or (b)oth? [g] " "$name"
            read -r answer
            case "$answer" in
                p|P) rm "$global_dir/$name"; print_success "Removed global link: $name" ;;
                b|B) print_info "Kept both: $name" ;;
                *)   rm "$project_dir/$name"; print_success "Removed project link: $name" ;;
            esac
        done
        return 0
    fi
    if [ "$how" = ask ] && [ -t 0 ]; then
        printf "Remove the %d project link(s) and keep the global ones? [Y/n] " "${#removable[@]}"
        read -r answer
        [[ "$answer" =~ ^[Nn] ]] && { print_info "Left as they are. Run --dedup later, or --dedup --pick to choose per skill."; return 0; }
    elif [ "$how" != auto ]; then
        print_info "Clean them with: $0 --dedup --yes $agent_name"
        return 0
    fi
    for name in "${removable[@]}"; do rm "$project_dir/$name"; done
    print_success "Removed ${#removable[@]} duplicate project link(s); the global ones stay"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS] AGENT_NAME [SKILL_NAMES...]

Automates importing skills from .agent-settings/skills/ to agent-specific folders.

Arguments:
  AGENT_NAME          Target agent folder name: claude, copilot or codex
                      Note: 'copilot' is an alias for 'claude' (.claude/skills/)

Options:
  -g, --global       Install into ~/.<agent>/skills instead of the project (never touches
                     links it does not own, so other global skills are safe)
  -a, --all          Import all available skills (default if no skills specified)
  -l, --list         List all available skills
  -v, --verify       Verify existing symlinks for the specified agent
  -p, --prune        Remove orphaned skills (interactively prompts per entry)
  -y, --yes          Auto-confirm removals (with --prune or --dedup)
  -d, --dedup        Remove skills installed both globally and in a project (keeps the global link;
                     one Y/n for all). Committed project links and other tools' links are left alone
      --pick         With --dedup: choose per skill (keep global, keep project, or both)
      --project PATH Project to compare with ~/.<agent>/skills (default: this project, or the git repo
                     you run --global from)
  -h, --help         Show this help message

Examples:
  # Import all skills to Claude agent
  # (removes all existing symlinks first, then re-adds — no stale skills)
  $0 claude

  # Import all skills to GitHub Copilot (uses .claude/skills/ — same as claude)
  $0 copilot

  # Import all skills with --all flag
  $0 --all claude

  # Import specific skills to Claude agent
  $0 claude generate-pr-notes git-commit-conventional-strict

  # Claude covers Copilot too (both read from .claude/skills/)
  $0 claude

  # List available skills
  $0 --list

  # Verify symlinks for Claude/Copilot (same directory)
  $0 --verify claude

  # Prune orphaned skills from Claude (interactive prompts)
  $0 --prune claude

  # Prune without prompting (auto-remove all orphans)
  $0 --prune --yes claude

  # Clean skills that show up twice (global + this project), no questions
  $0 --dedup --yes claude

EOF
}

# Main script logic
main() {
    local mode="import"
    local import_all=false
    local force=false
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
            -g|--global)
                GLOBAL=true
                PROJECT_ROOT="$HOME"
                shift
                ;;
            -a|--all)
                import_all=true
                shift
                ;;
            -p|--prune)
                mode="prune"
                shift
                ;;
            -y|--yes)
                force=true
                shift
                ;;
            -d|--dedup)
                mode="dedup"
                shift
                ;;
            --pick)
                PICK=true
                shift
                ;;
            --no-color)
                shift
                ;;
            --project)
                DEDUP_PROJECT="$2"
                shift 2
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
        prune)
            if [ -z "$agent_name" ]; then
                print_error "Agent name required for prune mode"
                echo ""
                show_usage
                exit 1
            fi
            prune_agent_skills "$agent_name" "$force"
            ;;
        dedup)
            if [ -z "$agent_name" ]; then
                print_error "Agent name required for dedup mode"
                echo ""
                show_usage
                exit 1
            fi
            if [ "$force" = true ]; then dedup_skills "$agent_name" auto; else dedup_skills "$agent_name" ask; fi
            ;;
        import)
            if [ -z "$agent_name" ]; then
                print_error "Agent name required"
                echo ""
                show_usage
                exit 1
            fi

            case "$agent_name" in
                claude|copilot|codex) ;;
                *)
                    print_error "Unsupported agent: '$agent_name'. Supported agents: claude, copilot, codex."
                    exit 1
                    ;;
            esac

            if [ ${#skills[@]} -eq 0 ] || [ "$import_all" = true ]; then
                import_all_skills "$agent_name"
            else
                import_specific_skills "$agent_name" "${skills[@]}"
            fi

            [ -t 0 ] && prompt_playground_skills "$agent_name"

            # The other side (global vs this project) may hold the same skills: offer to clean them once.
            if [ "$force" = true ]; then dedup_skills "$agent_name" auto; else dedup_skills "$agent_name" ask; fi

            echo ""
            print_success "Import complete!"
            echo ""
            print_info "You can verify the links with: PROJECT_ROOT=\"$PROJECT_ROOT\" $0 --verify $agent_name"
            ;;
    esac
}

# Run main function
main "$@"
