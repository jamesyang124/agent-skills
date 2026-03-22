#!/bin/bash

# This script interactively guides the user to select a target git worktree
# and then symlinks all git-ignored files and directories from the current
# (source) worktree to the chosen target worktree.
# It also offers the option to update git submodules.

source_path="$(pwd)"
target_path_arg="$1" # Allow direct path as argument

target_path=""

if [ -n "$target_path_arg" ]; then
    target_path="$target_path_arg"
else
    echo "📂 Current worktree (SOURCE): $source_path"
    echo ""
    echo "📋 Available git worktrees:"

    # Get current worktree path for filtering
    current_worktree_abs="$(pwd)"

    # Parse git worktree list and store options
    declare -a worktree_options=()
    declare -a worktree_paths=()
    i=1

    # Read git worktree list line by line
    while read -r line; do
        if [[ "$line" == worktree* ]]; then
            path="${line#worktree }"
            abs_path="$(cd "$path" && pwd)" # Resolve to absolute path

            if [[ "$abs_path" != "$current_worktree_abs" ]]; then
                worktree_paths+=("$path")
                branch_name="$(git -C "$path" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "N/A")" # Get branch name, handle errors
                worktree_options+=("[$i] $(basename "$path") ($branch_name) - $path")
                i=$((i+1))
            fi
        fi
    done < <(git worktree list --porcelain)

    if [ ${#worktree_options[@]} -eq 0 ]; then
        echo "❌ No other worktrees found to link to."
        exit 1
    fi

    for option in "${worktree_options[@]}"; do
        echo "$option"
    done

    while true; do
        read -p "Please enter the number of the TARGET worktree: " selection_num
        if [[ "$selection_num" =~ ^[0-9]+$ ]] && [ "$selection_num" -ge 1 ] && [ "$selection_num" -le "${#worktree_options[@]}" ]; then
            target_path="${worktree_paths[$((selection_num-1))]}"
            break
        else
            echo "Invalid selection. Please enter a number between 1 and ${#worktree_options[@]}."
        fi
    done
fi



# Now execute the external symlink.sh script with the determined target_path
./.agent-settings/skills/symlink-worktree-ignored-files/symlink.sh "$target_path"