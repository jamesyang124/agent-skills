---
name: symlink-worktree-ignored-files
description: The agent will interactively guide the user to select a target worktree from a list of available git worktrees. Once selected, the skill will symlink all git-ignored files and directories from the current (source) worktree to the chosen target worktree.
---

# Symlink Worktree Ignored Files (Agent-Driven Interactive Selection)

This skill utilizes the agent to interactively guide you through the process of symlinking git-ignored files and directories. The agent will first present a numbered list of your existing git worktrees, prompt you to choose the destination, and then symlink all ignored files and directories directly.

## Description

This skill provides an agent-driven interactive approach to symlinking git-ignored files and directories. It takes your current worktree as the source. The agent will then list all available git worktrees as numbered options, allowing you to select the target destination by entering a number. Once the target is selected, the underlying script will perform the symlinking of all ignored files and directories individually.

## Quick Start & Usage

To use this skill, navigate to your source worktree (the one with files to link FROM) and then run the skill **without any arguments**. The agent will then guide you through the selection process.

```bash
# 1. Navigate to your source branch (the one with files to link FROM)
cd /path/to/my-project

# 2. Run the skill
/symlink-worktree-ignored-files
```

The agent will then display a numbered list of available worktrees and prompt you to choose one by entering its number.

You can also provide the target worktree path directly as an argument to bypass the agent's interactive selection:

```bash
/symlink-worktree-ignored-files /path/to/target/worktree
```

## Core Script Logic

The agent will first handle the interactive selection of the target worktree based on user input. Once the `target_path` is determined, it will execute the external `symlink.sh` script with this path as an argument. The `symlink.sh` script will then handle the symlinking of files and directories.

```bash
# Core Script Logic: Agent-driven interactive target worktree selection

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

    local selection_num
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
```

## Benefits of This Approach

### Agent-Driven Interactivity & Usability
- **Guided selection**: The agent handles presenting options and prompting for input.
- **Direct symlinking**: All ignored files and directories are symlinked without complex detection logic.
- **Predictable**: Easy to understand what will be symlinked.

## Important Notes

- **Git-ignored files and directories only**: This skill is designed for git-ignored files and directories. Symlinking tracked files can cause confusion and git issues.
- **All ignored files and directories**: Every file and directory that `git ls-files --others --ignored --exclude-standard` reports will be symlinked. This includes large directories like `node_modules` and `.venv`, which can lead to a very large number of individual symlinks or direct directory symlinks.
- **Target must exist**: The target worktree path must already exist. This skill does not create it.
- **Write operations**: Changes to symlinked files affect the source worktree.
- **Platform compatibility**: Symlinks work on Unix-like systems (Linux, macOS). On Windows, they require administrator privileges or Developer Mode.
- **Cleanup**: When deleting a symlink, use `rm [symlink]` or `unlink [symlink]`. Do NOT use `rm -rf` as it might delete the source files.