# Skill Anatomy

How a skill in this repo is laid out. `scripts/validate-skills.sh` enforces the rules marked **(checked)**.

## Layout

```
skills/
  skill-name/
    SKILL.md        # required
    scripts/        # optional: runnable helpers
    references/     # optional: detail loaded on demand
    templates/      # optional: files the skill copies or fills in
```

Add a folder only when the skill needs it; no empty `scripts/` for symmetry.

## Frontmatter

```yaml
---
name: skill-name
description: "Does X for Y. Use when <trigger>, <trigger>, or when asked to <phrase>."
argument-hint: "<what the user may pass>"   # optional
allowed-tools: Read, Bash                    # optional
---
```

- `name`: lowercase, hyphenated, equal to the folder name. **(checked)**
- `description`: what the skill does, then one or more "Use when ..." triggers, at most 1024 characters. **(checked)**
  The description is all the agent sees before loading the skill, so state *when*, not the steps.
- Allowed keys: the [Agent Skills spec](https://agentskills.io) fields (`name`, `description`, `license`,
  `compatibility`, `metadata`, `allowed-tools`) plus Claude Code's `argument-hint` and
  `disable-model-invocation`. Anything else goes under `metadata`. **(checked)**
- Quote a description that contains `: ` so YAML parses it.

## Body

Common order (sections a skill doesn't need are left out):

1. `# Title`
2. `## Install this skill`: the `npx skills add jamesyang124/agent-skills --skill <name> -g` line **(checked)**
3. `## Dependencies`: other skills, MCPs or CLIs it needs
4. Overview / when to use
5. Process: numbered steps the agent follows
6. Verification: how the agent proves it worked

## Size and references

- Keep `SKILL.md` under 500 lines (the validator warns above that). Move long reference material to `references/`.
- Link supporting files directly from `SKILL.md` (one level deep) with paths relative to the skill folder,
  e.g. `references/foo.md`. Relative links must resolve. **(checked)**
- Prefer a script over a long inline code block: running a script costs only its output.

## Per-project settings

Skills that need per-repo values (Jira key, ADO org, SDD tool, code layout) read them from the consuming
repo's `docs/agents/<topic>.md`, written by `/setup-project-config`. Secrets never go there; they stay in
`~/.env.mcp-<name>` or OAuth.

- A skill that cannot work without the file says one line: "... should have been provided to you in
  `docs/agents/<topic>.md`; run `/setup-project-config` if not."
- A skill that works without it uses the file when present and falls back to detection or asking, with no
  setup pointer.

## Scripts

- `#!/usr/bin/env bash` and `set -euo pipefail`.
- Status messages to stderr, machine-readable output to stdout.
- Reference them from `SKILL.md` as `<skill-dir>/scripts/<name>.sh`.
