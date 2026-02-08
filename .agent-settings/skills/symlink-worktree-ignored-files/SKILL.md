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
/run_skill.sh
```

The agent will then display a numbered list of available worktrees and prompt you to choose one by entering its number.



You can also provide the target worktree path directly as an argument to bypass the agent's interactive selection:



```bash

/run_skill.sh /path/to/target/worktree

```



## Skill Script Logic



This skill is implemented using two shell scripts:

- `run_skill.sh`: This is the main interactive script that guides the user to select the target worktree.

- `symlink.sh`: This script performs the actual symlinking of ignored files and directories. `run_skill.sh` calls this script after determining the target path.



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
- **.wt directory excluded**: The `.wt` directory and its nested resources are explicitly excluded from symlinking to avoid conflicts with git worktree internal files.
- **Cleanup**: When deleting a symlink, use `rm [symlink]` or `unlink [symlink]`. Do NOT use `rm -rf` as it might delete the source files.