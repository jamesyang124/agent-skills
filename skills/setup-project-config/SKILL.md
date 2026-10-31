---
name: setup-project-config
description: "Configures a repo for these skills: writes per-topic settings to docs/agents/*.md (SDD tool, code structure, and project-scoped values for installed MCPs - Atlassian, Azure DevOps, Sentry, Playwright) and adds an `## Agent skills` pointer block to CLAUDE.md or AGENTS.md. Credentials stay in the global ~/.env.mcp-* store. Use when setting up skills in a repo for the first time, when a skill says to run setup-project-config, or when asked to update project settings (e.g. change Jira project key, framework changed)."
argument-hint: "[topic, e.g. atlassian] (optional - default sets up every topic)"
disable-model-invocation: true
allowed-tools: Read, Glob, Grep, Bash, Write, Edit
---

# Setup Project Config

## Install this skill

```bash
npx skills add jamesyang124/agent-skills --skill setup-project-config -g
```

Scaffold the per-repo settings the other skills read. Each topic is one small file under `docs/agents/`,
committed with the repo so teammates share it. Different repos get different files; a topic that does not
apply (no Sentry MCP, no SDD tool) gets no file.

| File | Holds | Read by |
|------|-------|---------|
| `docs/agents/sdd.md` | SDD tool + its commands | `ado-open-pr`, `spec-recalibrate`, `tech-plan-to-wiki`, `sdd-qa-to-ticket` |
| `docs/agents/code-structure.md` | language, framework, router/handler/DTO dirs, API prefix, doc style | `sync-api-spec` (**required**) |
| `docs/agents/atlassian.md` | Confluence space, parent pages, Jira project key / issue type | `sync-api-spec`, `tech-plan-to-wiki`, `tech-plan-to-ticket` |
| `docs/agents/azure-devops.md` | organization, project, default repo | Azure DevOps MCP users |
| `docs/agents/sentry.md` | org slug, project slug | Sentry MCP users |
| `docs/agents/playwright.md` | base URL, allowed domains, user-agent | Playwright MCP users |

**Secrets never go in these files.** Tokens, PATs, passwords and connection URLs stay in
`~/.env.mcp-<name>` (or OAuth). A value in `docs/agents/` is a non-secret per-repo override; blank or
absent → the global env value stands.

This is a prompt-driven skill, not a script. Explore, present what you found, confirm, then write.

## Process

### 1. Explore

Read what exists; don't assume.

- `CLAUDE.md` / `AGENTS.md` at the repo root: does either exist? Is there already an `## Agent skills` block?
- `docs/agents/`: which topic files already exist? Existing ones are updated, not recreated.
- Legacy `.agent-settings/project-config.md`: if present, migrate it (step 2a).
- Installed MCPs: `.mcp.json`, `.claude/mcp.json` (`mcpServers` keys), `.vscode/mcp.json` (`servers` keys).
  Only installed MCPs get a topic. Warn if one is installed but its `~/.env.mcp-<name>` / OAuth is missing.
- `git remote -v`: a `dev.azure.com` / `visualstudio.com` remote pre-fills `azure-devops.md`.
- SDD tool: `.specify/`, `.speckit` or `spec-kit.json` → spec-kit; `openspec/`, `.openspec` or `openspec.json` → openspec.
- Code structure: follow [references/code-scan.md](references/code-scan.md).

If the user named a topic (e.g. `atlassian`), explore and ask only for that topic.

### 2. Present findings and ask

Summarise what was detected and what is missing. Then take the topics in order: one topic, one answer,
then the next. Lead each with the detected or recommended value so the user can accept it in a word.
Skip a topic when exploration settled it or it does not apply.

The fields per topic are the ones in its template under [templates/](templates/). For Atlassian parent
pages, ask for up to 3 `name, page ID` pairs and stop at the first blank.

#### 2a. Legacy migration

If `.agent-settings/project-config.md` exists, show this mapping before writing and keep every user value:

| Legacy section | New file |
|----------------|----------|
| `## MCP: atlassian` (or older `## Confluence` + `## Jira`) | `atlassian.md` |
| `## MCP: azure-devops` / `sentry` / `playwright` | `azure-devops.md` / `sentry.md` / `playwright.md` |
| `## SDD Tool` | `sdd.md` |
| `## Code Structure` + `## Documentation Format` | `code-structure.md` |

After writing, offer to delete the legacy file and the then-empty `.agent-settings/` folder.

### 3. Confirm

Show a draft of each topic file and of the `## Agent skills` block. Let the user edit before writing.

### 4. Write

**Pick the rules file:**
- If `CLAUDE.md` exists, edit it.
- Else if `AGENTS.md` exists, edit it.
- If neither exists, ask which one to create; don't pick for them.

Never create `AGENTS.md` when `CLAUDE.md` exists (or vice versa). If an `## Agent skills` block already
exists, update it in place; don't touch the surrounding sections.

The block has one line per topic file written:

```markdown
## Agent skills

- SDD: spec-kit. See `docs/agents/sdd.md`.
- Code structure: Go / Gin. See `docs/agents/code-structure.md`.
- Atlassian: Jira PROJ, Confluence space ENG. See `docs/agents/atlassian.md`.
- Azure DevOps: my-org/my-project. See `docs/agents/azure-devops.md`.
```

Then write each topic file from its template. Re-runs rewrite only the topics that changed and keep hand
edits elsewhere.

For the Atlassian parent-page table, build each URL as `{base}/spaces/{Space Key}/pages/{ID}`, where
`base` is the file's Base URL override if present, else `CONFLUENCE_URL` from `~/.env.mcp-atlassian`.
If neither is available, leave the URL cell blank.

### 5. Done

Tell the user which files were written and which skills now read them (table above). They can edit
`docs/agents/*.md` directly later; re-run this skill only to add a topic or rescan the code structure.
