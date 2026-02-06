---
name: symlink-worktree-ignored-files
description: Symlink git-ignored files from source worktree to an existing target worktree. Intelligently handles ignored files, heavy directories (node_modules, vendor), and submodules without creating the worktree itself.
---

# Symlink Worktree Ignored Files

Symlink git-ignored files and directories from a source worktree to an existing target worktree.

## Description

This skill automates the process of symlinking git-ignored files from a source worktree to an existing target worktree through an **interactive interface**. It intelligently handles:
- Individual git-ignored files (`.env`, config files, etc.)
- Heavy directories separately (`node_modules`, `vendor`)
- Submodule initialization with shared git objects

**Note**: This skill assumes the target worktree already exists. It does **not** create the worktree itself.

## Quick Start

```bash
# 1. First, create a worktree if you haven't already
git worktree add ../my-feature -b feature-branch

# 2. Run the skill in interactive mode (recommended)
/symlink-worktree-ignored-files

# 3. The skill will:
#    - Show you all available worktrees
#    - Let you select which one to symlink files to
#    - Preview what will be symlinked
#    - Ask for confirmation
#    - Create symlinks automatically
```

## Usage

```
/symlink-worktree-ignored-files [target-worktree-path]
```

**Primary Usage (Interactive Mode - Recommended):**
```bash
/symlink-worktree-ignored-files
```
The skill will:
1. Display all existing git worktrees
2. Let you select which worktree to symlink files to
3. Show what will be symlinked before proceeding

**Direct Usage (Optional):**
```bash
/symlink-worktree-ignored-files ../feature-x
/symlink-worktree-ignored-files /path/to/existing/worktree
```

**Prerequisites:**
- Target worktree must already exist (created via `git worktree add`)
- Run this skill from the source worktree (the one containing files to link from)

## Interactive Workflow

When you run `/symlink-worktree-ignored-files`, the skill will:

1. ✅ **Display** all available git worktrees
2. ❓ **Ask** you to select the target worktree
3. 📋 **Preview** what will be symlinked (files, directories, submodules)
4. ❓ **Confirm** before making any changes
5. 🔗 **Create** symlinks for:
   - Individual ignored files (`.env`, configs, etc.)
   - Heavy directories (`node_modules`, `vendor`, etc.)
   - Submodules (with shared git objects via `--reference`)
6. ✅ **Verify** all symlinks work correctly
7. 📊 **Report** results with disk space savings

## Core Script Logic

This skill combines concepts from `git-worktree-full` (for ignored files) and `git-worktree-safe` (for submodules):

```bash
# Adapted logic for existing worktrees
symlink-worktree-ignored() {
    local path="$1"
    local source="$(pwd)"

    # NOTE: This skill does NOT create the worktree - it assumes it exists
    # User should run: git worktree add "$path" [branch-args] first

    # 1. Symlink individual ignored files (skip heavy dirs)
    git ls-files --others --ignored --exclude-standard \
        | grep -v -E '^(node_modules|vendor|\.cache|dist)/' \
        | while read -r file; do
            mkdir -p "$path/$(dirname "$file")"
            [ ! -e "$path/$file" ] && ln -s "$source/$file" "$path/$file"
        done

    # 2. Symlink heavy directories
    for dir in node_modules vendor .cache dist build target; do
        [ -d "$dir" ] && [ ! -e "$path/$dir" ] && ln -s "$source/$dir" "$path/$dir"
    done

    # 3. Initialize submodules with shared git objects (--reference)
    if [ -f .gitmodules ]; then
        cd "$path"
        git submodule foreach --quiet 'echo $sm_path' | while read -r sm; do
            if [ -d "$source/$sm/.git" ] || [ -f "$source/$sm/.git" ]; then
                git submodule update --init --reference "$source/$sm" -- "$sm"
            fi
        done
        cd "$source"
    fi

    echo "✅ Worktree at $path: ignored files symlinked, submodules share git objects."
}
```

**Key Approach:**
1. **Ignored files**: Symlinked individually (`.env`, config files, etc.)
2. **Heavy directories**: Symlinked as whole directories (`node_modules`, `vendor`)
3. **Submodules**: Use `--reference` to share git objects while maintaining independent checkouts
4. **Worktree creation**: NOT handled by this skill - assumes worktree already exists

## Instructions

Follow these steps to symlink git-ignored files from the current (source) worktree to an existing target worktree:

### 1. Verify Environment and Display Worktrees

First, verify the current directory is a git repository and list all existing worktrees:

```bash
# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not a git repository"
    exit 1
fi

# Get current worktree path
current_worktree="$(pwd)"
echo "📂 Current worktree (source): $current_worktree"

# List all worktrees with details
echo ""
echo "📋 Available worktrees:"
git worktree list
```

**Expected output:**
```
📂 Current worktree (source): /repo/my-project

📋 Available worktrees:
/repo/my-project          abc123 [main]
/repo/my-project-feature  def456 [feature-branch]
/repo/my-project-hotfix   ghi789 [hotfix-123]
```

### 2. Interactive Selection - Let User Choose Target

**ALWAYS** use `AskUserQuestion` to let the user select the target worktree interactively:

```
Question: "Which worktree should receive the symlinked files?"
Header: "Target Worktree"
```

**Build options dynamically from git worktree list:**

1. Parse `git worktree list` output to extract worktree paths
2. Exclude the current worktree (source) from options
3. For each worktree, create an option with:
   - **Label**: Path + branch name (e.g., "../my-project-feature [feature-branch]")
   - **Description**: Full path and git status

**Example AskUserQuestion structure:**
```
Question: "Which worktree should receive the symlinked files from the current worktree?"
Header: "Target"
Options:
  - Label: "../my-project-feature (feature-branch)"
    Description: "Full path: /repo/my-project-feature | Branch: feature-branch"
  - Label: "../my-project-hotfix (hotfix-123)"
    Description: "Full path: /repo/my-project-hotfix | Branch: hotfix-123"
```

**If user provides target path directly (non-interactive mode):**
- Skip the question and use the provided path
- Still validate the path in the next step

### 3. Validate Target Worktree Exists

Extract the path from the user's selection and validate it:

```bash
# Extract path from user selection (if they chose from the list)
# The user's answer will be in the format: "../path (branch-name)"
# Parse to get just the path part
target_path="<extracted-from-user-selection>"

# Check if path exists
if [ ! -d "$target_path" ]; then
    echo "❌ Error: Target path does not exist: $target_path"
    exit 1
fi

# Verify it's a git worktree
if [ ! -d "$target_path/.git" ] && [ ! -f "$target_path/.git" ]; then
    echo "❌ Error: Target path is not a git worktree: $target_path"
    exit 1
fi

# Get absolute paths for clarity
target_path_abs=$(cd "$target_path" && pwd)
echo "✅ Target worktree validated: $target_path_abs"
```

### 4. Preview What Will Be Symlinked

**CRITICAL: Always show a preview and ask for confirmation before proceeding.**

```bash
source_worktree="$(pwd)"
echo ""
echo "📋 Preview - Files and directories to be symlinked:"
echo ""

# Preview individual ignored files
echo "📄 Individual ignored files:"
ignored_files=$(git ls-files --others --ignored --exclude-standard \
    | grep -v -E '^(node_modules|vendor|\.cache|dist)/' | head -10)

if [ -n "$ignored_files" ]; then
    echo "$ignored_files" | while read -r file; do
        echo "  • $file"
    done

    # Count total
    total=$(git ls-files --others --ignored --exclude-standard \
        | grep -v -E '^(node_modules|vendor|\.cache|dist)/' | wc -l)
    [ "$total" -gt 10 ] && echo "  ... and $((total - 10)) more files"
else
    echo "  (none found)"
fi

echo ""
echo "📦 Heavy directories (if present):"
for dir in node_modules vendor .cache dist build target; do
    if [ -d "$source_worktree/$dir" ]; then
        size=$(du -sh "$source_worktree/$dir" 2>/dev/null | cut -f1)
        echo "  • $dir ($size)"
    fi
done

echo ""
echo "🔧 Submodules (if present):"
if [ -f "$source_worktree/.gitmodules" ]; then
    git submodule foreach --quiet 'echo $sm_path' | while read -r sm; do
        echo "  • $sm (will use --reference for shared git objects)"
    done
else
    echo "  (no submodules detected)"
fi

echo ""
echo "Source: $source_worktree"
echo "Target: $target_path_abs"
```

**Then use `AskUserQuestion` to confirm:**

```
Question: "Proceed with symlinking these files and directories?"
Header: "Confirm"
Options:
  - Label: "Yes, proceed"
    Description: "Create symlinks for all ignored files, heavy directories, and initialize submodules with shared objects"
  - Label: "No, cancel"
    Description: "Cancel the operation without making any changes"
```

If user selects "No, cancel", exit gracefully without making changes.

### 5. Symlink Individual Git-Ignored Files

Symlink git-ignored files, excluding heavy directories that will be handled separately:

```bash
# Get list of ignored files, excluding heavy directories
ignored_files=$(git ls-files --others --ignored --exclude-standard \
    | grep -v -E '^(node_modules|vendor|\.cache|dist)/')

if [ -n "$ignored_files" ]; then
    echo "🔗 Symlinking individual ignored files..."
    echo "$ignored_files" | while read -r file; do
        # Create parent directory in target if needed
        mkdir -p "$target_path/$(dirname "$file")"

        # Check if file/symlink already exists in target
        if [ -e "$target_path/$file" ] || [ -L "$target_path/$file" ]; then
            echo "  ⚠️  Skipping $file (already exists in target)"
        else
            # Create absolute symlink
            ln -s "$source_worktree/$file" "$target_path/$file"
            echo "  ✅ $file"
        fi
    done
else
    echo "ℹ️  No individual ignored files to symlink"
fi
```

**Note**: Using absolute symlinks for simplicity. For relative symlinks, calculate relative path first.

### 6. Symlink Heavy Directories

Handle heavy directories (`node_modules`, `vendor`, etc.) separately:

```bash
echo "🔗 Symlinking heavy directories..."

for dir in node_modules vendor .cache dist build target; do
    if [ -d "$source_worktree/$dir" ]; then
        if [ -e "$target_path/$dir" ] || [ -L "$target_path/$dir" ]; then
            echo "  ⚠️  $dir already exists in target"
            # Optionally ask user how to handle:
            # - Skip
            # - Backup and replace
            # - Delete and replace
        else
            ln -s "$source_worktree/$dir" "$target_path/$dir"
            echo "  ✅ $dir -> $source_worktree/$dir"
        fi
    fi
done
```

### 7. Initialize Submodules with Shared Git Objects

If the project has submodules, initialize them in the target worktree using `--reference` to share git objects:

```bash
if [ -f "$source_worktree/.gitmodules" ]; then
    echo "🔗 Initializing submodules with shared git objects..."

    cd "$target_path"

    # Use --reference to share git objects (saves disk, still independent checkout)
    git submodule foreach --quiet 'echo $sm_path' | while read -r sm; do
        if [ -d "$source_worktree/$sm/.git" ] || [ -f "$source_worktree/$sm/.git" ]; then
            echo "  📦 Initializing $sm with shared objects..."
            git submodule update --init --reference "$source_worktree/$sm" -- "$sm"
            echo "  ✅ $sm (shared git objects from source)"
        fi
    done

    cd "$source_worktree"
else
    echo "ℹ️  No submodules detected"
fi
```

**Key Benefits**:
- **Shared git objects**: Saves significant disk space (typically 50-90%)
- **Independent checkouts**: Each worktree can have different submodule commits checked out
- **Safe**: No risk of accidentally modifying shared working directory
- **Fast**: Submodule initialization is much faster with `--reference`

**Note**: This approach uses `--reference` instead of symlinking the entire submodule directory, providing both disk savings and operational independence.

### 8. Verify Symlinks

Verify all symlinks were created correctly:

```bash
echo "🔍 Verifying symlinks in target worktree..."

cd "$target_path"

# Count symlinks
symlink_count=$(find . -maxdepth 3 -type l | wc -l)
echo "Found $symlink_count symlinks"

# Check for broken symlinks
broken=$(find . -maxdepth 3 -type l ! -exec test -e {} \; -print)
if [ -n "$broken" ]; then
    echo "❌ Broken symlinks detected:"
    echo "$broken"
else
    echo "✅ All symlinks are valid"
fi

cd "$source_worktree"
```

### 9. Report Results

Provide a comprehensive summary:

```
🎉 Symlink Operation Complete!

📂 Source worktree: $source_worktree
📁 Target worktree: $target_path

✅ Individual ignored files: XX symlinked
✅ Heavy directories: node_modules, vendor (if present)
✅ Submodules: XX symlinked (if present)

⚠️  Files skipped (already existed):
  - .env.backup
  - some-file.txt

📝 Summary:
  - Total symlinks created: XX
  - Disk space saved: ~XXX MB (estimated)
  - Target worktree ready to use

💡 Next steps:
  cd $target_path
  git status
  # Start working in your target worktree!
```

## Safety Checks

**CRITICAL SAFETY REQUIREMENTS:**

1. **Never symlink tracked files** without explicit user confirmation
2. **Always backup existing files** before replacing them with symlinks (unless user chooses delete)
3. **Verify symlink targets exist** before creating links
4. **Use relative paths** when possible for portability
5. **Check for circular symlinks** to avoid infinite loops

## Common Use Cases

### Creating a Feature Branch with Shared Dependencies
```bash
# Create worktree and link node_modules to avoid reinstalling
/symlink-worktree-ignored-files ../feature-auth feature-auth node_modules .env
```

### Hotfix Branch with Environment Configuration
```bash
# Create hotfix worktree with shared env files
/symlink-worktree-ignored-files ../hotfix-security hotfix/security-patch .env .env.local
```

### Development Branch with Build Artifacts
```bash
# Create dev worktree, share build output to speed up development
/symlink-worktree-ignored-files ../dev-branch develop dist build node_modules
```

### Testing Multiple Branches with Shared Python Environment
```bash
# Create test worktree with shared Python virtual environment
/symlink-worktree-ignored-files ../test-branch test-feature .venv .env
```

## Benefits of This Approach

### Disk Space Savings
- **Submodules**: Git objects shared via `--reference` (typically 50-90% space savings)
- **Dependencies**: `node_modules`, `.venv` symlinked instead of duplicated
- **Build artifacts**: Share `dist`, `build`, `target` directories

### Time Savings
- **No reinstalling**: Dependencies like `node_modules` or `.venv` are instantly available
- **Faster setup**: Skip `npm install`, `pip install`, or build steps
- **Quick context switching**: Create new worktrees in seconds

### Consistency
- **Same environment**: All worktrees use identical `.env` files
- **Version alignment**: Shared dependencies ensure no version mismatches
- **Configuration sync**: Changes to config files reflected across all worktrees

### Safety
- **Independent checkouts**: Each worktree has its own git working directory
- **No merge conflicts**: Symlinked files aren't tracked by git
- **Easy cleanup**: Remove worktree without affecting shared resources

## Important Notes

- **Git-ignored files only**: This skill is designed for git-ignored files. Symlinking tracked files can cause confusion and git issues.
- **Relative vs Absolute**: Prefer relative symlinks for portability, but use absolute if the worktrees might be moved independently.
- **Disk space**: Symlinks save disk space by sharing files instead of duplicating them.
- **Write operations**: Changes to symlinked files affect the source worktree - make sure this is intended behavior.
- **Platform compatibility**: Symlinks work on Unix-like systems (Linux, macOS). On Windows, they require administrator privileges or Developer Mode.
- **Cleanup**: When deleting a symlink, use `rm [symlink]` or `unlink [symlink]`. Do NOT use `rm -rf` as it might delete the source files.

## Troubleshooting

### Broken Symlinks
If symlinks are broken (pointing to non-existent files):
```bash
# Find broken symlinks
find . -xtype l

# Remove broken symlinks
find . -xtype l -delete
```

### Permission Issues
If you encounter permission errors:
```bash
# Check permissions on source file
ls -la [source-file]

# Check if you have read access to source
test -r [source-file] && echo "Readable" || echo "Not readable"
```

### Worktree Not Found
If the source worktree path is incorrect:
```bash
# List all worktrees
git worktree list

# Verify worktree path exists
test -d [worktree-path] && echo "Exists" || echo "Not found"
```

## Example Workflow

### Scenario: Create a feature branch worktree and symlink ignored files

```bash
# 1. Start in your main/source worktree
cd /repo/my-project
source_worktree="$(pwd)"

# 2. Check existing worktrees
git worktree list
# Output:
# /repo/my-project  abc123 [main]

# 3. Create new worktree for feature branch
target_path="../my-project-feature-x"
git worktree add "$target_path" -b feature-x
# Output: Preparing worktree (new branch 'feature-x')

# 4. Now use this skill to symlink ignored files
# Run: /symlink-worktree-ignored-files ../my-project-feature-x
# Or execute the following steps manually:

# Step 4a: Symlink individual ignored files (excluding heavy dirs)
git ls-files --others --ignored --exclude-standard \
    | grep -v -E '^(node_modules|vendor|\.cache|dist)/' \
    | while read -r file; do
        mkdir -p "$target_path/$(dirname "$file")"
        if [ ! -e "$target_path/$file" ]; then
            ln -s "$source_worktree/$file" "$target_path/$file"
            echo "✅ Symlinked: $file"
        fi
    done

# Step 4b: Symlink heavy directories
for dir in node_modules vendor .cache dist; do
    if [ -d "$dir" ] && [ ! -e "$target_path/$dir" ]; then
        ln -s "$source_worktree/$dir" "$target_path/$dir"
        echo "✅ Symlinked directory: $dir"
    fi
done

# Step 4c: Initialize submodules with shared git objects
if [ -f .gitmodules ]; then
    cd "$target_path"
    git submodule foreach --quiet 'echo $sm_path' | while read -r sm; do
        if [ -d "$source_worktree/$sm/.git" ] || [ -f "$source_worktree/$sm/.git" ]; then
            git submodule update --init --reference "$source_worktree/$sm" -- "$sm"
            echo "✅ Submodule $sm initialized with shared objects"
        fi
    done
    cd "$source_worktree"
fi

# 5. Verify the setup
cd "$target_path"
ls -la .env node_modules
# Output (examples):
# lrwxr-xr-x  .env -> /repo/my-project/.env
# lrwxr-xr-x  node_modules -> /repo/my-project/node_modules

# 6. Test a symlinked file
cat .env
# Should show contents from source worktree

# 7. Check git status
git status
# Output: On branch feature-x, nothing to commit, working tree clean

# 8. Start working!
echo "Ready to work in feature-x branch with shared resources!"
```

### Result
- ✅ New worktree at `/repo/my-project-feature-x`
- ✅ Branch `feature-x` checked out independently
- ✅ Ignored files (`.env`, configs) symlinked from source
- ✅ Heavy directories (`node_modules`) symlinked to save disk space
- ✅ Submodules share git objects via `--reference` (saves ~50-90% disk space)
- ✅ Independent git working directory for parallel development
- ✅ No need to reinstall dependencies or rebuild

### Disk Space Comparison

**Without this skill:**
- Main worktree: `node_modules` (300 MB) + submodules (200 MB) = 500 MB
- Feature worktree: `node_modules` (300 MB) + submodules (200 MB) = 500 MB
- **Total: 1000 MB**

**With this skill:**
- Main worktree: `node_modules` (300 MB) + submodules (200 MB) = 500 MB
- Feature worktree: symlinks (< 1 MB) + submodule git objects shared (20 MB) = ~20 MB
- **Total: ~520 MB** (saves ~480 MB or 48%)

## Additional Features

Consider implementing these optional enhancements:

- **Batch operations**: Link multiple files with a single command
- **Pattern matching**: Support glob patterns like `*.env`, `.env.*`
- **Reverse operation**: Remove all symlinks and restore original files from backups
- **Dry run mode**: Show what would be linked without actually creating symlinks
- **Config file**: Save common linking patterns in a config file for reuse
