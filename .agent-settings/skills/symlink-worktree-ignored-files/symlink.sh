#!/bin/bash

# Script for symlinking ignored files to a specified target worktree.
# Expects the target worktree path as the first argument.

source_path="$(pwd)"
target_path="$1" # Expect target path as the first argument

if [ -z "$target_path" ]; then
    echo "❌ Error: Target worktree path is required as the first argument."
    exit 1
fi

if [ ! -d "$target_path" ]; then
    echo "❌ Error: Target path does not exist: $target_path"
    exit 1
fi

# Ensure target_path is an absolute path for consistency
target_path=$(cd "$target_path" && pwd)

echo "🔗 Symlinking ignored files from '$source_path' to '$target_path'..."

# Get ALL ignored files and directories
while IFS= read -r item; do
    if [ -n "$item" ]; then
        full_source_path="$source_path/$item"
        full_target_path="$target_path/$item"

        if [ -f "$full_source_path" ]; then
            # It's a file, symlink individually
            mkdir -p "$target_path/$(dirname "$item")"
            if [ -e "$full_target_path" ] || [ -L "$full_target_path" ]; then
                echo "  ⚠️  '$item' already exists in target - skipping"
            else
                ln -s "$full_source_path" "$full_target_path"
                echo "  ✅ Symlinked file: '$item'"
            fi
        elif [ -d "$full_source_path" ]; then
            # It's a directory, symlink the entire directory
            if [ -e "$full_target_path" ] || [ -L "$full_target_path" ]; then
                echo "  ⚠️  '$item' directory already exists in target - skipping"
            else
                ln -s "$full_source_path" "$full_target_path"
                echo "  ✅ Symlinked directory: '$item'"
            fi
        fi
    fi
done < <(git ls-files --others --ignored --exclude-standard)

echo "🎉 Symlinking complete for '$target_path'."
