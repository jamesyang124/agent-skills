---
name: sync-skills
description: >
  Sync the local .agents/skills directory with the ClawHub registry.
  Detects which skills are not yet installed and installs them automatically.
  Use whenever you want to pull down new or missing skills from the registry
  without reinstalling ones that are already present.
  Triggers on: "install new skills", "sync skills", "update skill list",
  "check for new skills", "pull skills from registry".
allowed-tools: Bash(bash *), Bash(node *), Bash(npx *)
---

# Sync Skills from Registry

## Install this skill globally

Install once — available in all projects.

```bash
# Claude
mkdir -p ~/.claude/skills/sync-skills
cp <agent-settings-repo>/.agent-settings/skills/tools/sync-skills/SKILL.md \
   ~/.claude/skills/sync-skills/SKILL.md
# Add to ~/.claude/CLAUDE.md: - **sync-skills** (`~/.claude/skills/sync-skills/SKILL.md`)

# Copilot
mkdir -p ~/.copilot/skills/sync-skills
cp <agent-settings-repo>/.agent-settings/skills/tools/sync-skills/SKILL.md \
   ~/.copilot/skills/sync-skills/SKILL.md

# Gemini
mkdir -p ~/.gemini/skills/sync-skills
cp <agent-settings-repo>/.agent-settings/skills/tools/sync-skills/SKILL.md \
   ~/.gemini/skills/sync-skills/SKILL.md
```


This skill compares the registry catalog against the locally installed skills
and installs any that are missing.  Already-installed skills are never
re-downloaded (idempotent).

## Bundled Script

The logic lives in `scripts/sync-skills.sh` (relative to this skill folder).

```
<skill-dir>/scripts/sync-skills.sh [OPTIONS]

Options:
  --skills-dir <path>   Root skills directory (default: two levels up, i.e. .agents/skills)
  --registry   <url>    Registry base URL   (default: https://skillhub.vrprod.viveport.com)
  --dry-run             Print what would be installed without actually installing
  --limit      <n>      Max skills to fetch from registry (default: 200)
```

## Workflow

### Step 1 — Resolve paths

Determine:
- `SKILL_DIR`: absolute path to this skill folder (`local--sync-skills/`)
- `SKILLS_ROOT`: parent of `SKILL_DIR` (the `.agents/skills/` directory)

```bash
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"   # adjust if called from elsewhere
SKILLS_ROOT="$(dirname "$SKILL_DIR")"
```

### Step 2 — Run sync script

```bash
bash "$SKILL_DIR/scripts/sync-skills.sh" \
  --skills-dir "$SKILLS_ROOT" \
  --registry https://skillhub.vrprod.viveport.com
```

Or with a custom registry:

```bash
bash "$SKILL_DIR/scripts/sync-skills.sh" \
  --skills-dir "$SKILLS_ROOT" \
  --registry https://YOUR_REGISTRY_URL
```

### Step 3 — Interpret results

The script prints a summary:

```
════════════════════════════════════════════
Summary
  Already installed : 16
  Newly installed   : 3
  Failed            : 1

  Failed slugs (server-side issue, retry later):
    ✘ ops--some-skill
════════════════════════════════════════════
```

- **Exit 0** — everything installed successfully (or nothing new to install).
- **Exit 1** — at least one skill could not be installed.  Failed slugs have
  a server-side `Published bundle not found in storage` error; this is a
  registry issue.  Re-run the skill later to retry those slugs.

### Step 4 — Dry-run (optional, for inspection only)

```bash
bash "$SKILL_DIR/scripts/sync-skills.sh" \
  --skills-dir "$SKILLS_ROOT" \
  --dry-run
```

Prints the list of skills that *would* be installed without touching the filesystem.

## When to Use

- After a team member publishes a new skill to the registry.
- As part of project setup / onboarding (`bash .agents/skills/local--sync-skills/scripts/sync-skills.sh`).
- In CI to keep the skills directory up-to-date automatically.

## Requirements

- Node.js 18+ (provides `npx`)
- Network access to the registry URL
- Write permission to the skills directory
