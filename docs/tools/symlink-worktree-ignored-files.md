# symlink-worktree-ignored-files

## Overview

Interactively guides the user to select a target git worktree, then symlinks all git-ignored files and directories from the current worktree to the target. Eliminates the need to manually copy `.env` files, credentials, or large build artifacts across worktrees.

## When to Use

- Setting up a new git worktree and need to share `.env`, secrets, or other ignored files
- Asked to "symlink ignored files to another worktree"
- Any time you need `.gitignore`d content to be available in a second worktree without duplicating it

## Usage

Run from the **source** worktree (the one that has the files you want to share):

```
/symlink-worktree-ignored-files [target-worktree-path]
```

Without an argument, the skill presents a numbered list of all existing worktrees and prompts you to pick the target. With an argument, it skips straight to symlinking.

## How It Works

1. Lists all git worktrees via `git worktree list`
2. Prompts user to select the target worktree
3. Runs `git ls-files --others --ignored --exclude-standard` to enumerate ignored files/dirs
4. Creates individual symlinks in the target worktree pointing back to the source

## Notes

- **Source of truth stays in the source worktree** — edits via a symlink affect the original file
- `node_modules`, `.venv`, and other large directories are symlinked as directories (not per-file)
- The `.wt` directory is excluded to avoid conflicting with git worktree internals
- Target worktree must already exist — this skill does not create it
- Works on macOS and Linux; Windows requires Developer Mode or admin privileges for symlinks
- To remove a symlink: `rm symlink` or `unlink symlink` — never `rm -rf`
