# Agent Skills

Skills for AI coding agents that cover Azure DevOps pull requests, spec-driven development (spec-kit / openspec → Confluence → Jira), MCP server setup and git workflows.

Each skill is a folder with a `SKILL.md` ([Agent Skills](https://agentskills.io) format), so it works in Claude Code, GitHub Copilot, Codex and any agent the [`skills`](https://github.com/vercel-labs/skills) CLI supports.

## Quick Start

```bash
npx skills add jamesyang124/agent-skills --list                 # see what is available
npx skills add jamesyang124/agent-skills -g                     # pick skills interactively, install for your user
npx skills add jamesyang124/agent-skills -g --skill ado-open-pr --skill generate-pr-notes
npx skills update -g                                            # update installed skills later
```

`-g` installs at user level, for every project; leave it out to install into the current project only.

<details>
<summary>Claude Code plugin</summary>

Installs every skill as one plugin:

```
/plugin install agent-skills --marketplace jamesyang124/agent-skills
```

On older Claude Code versions:

```
/plugin marketplace add jamesyang124/agent-skills
/plugin install agent-skills@jamesyang124-agent-skills
```

</details>

### Per-project setup

Skills that need per-repo values (Jira project key, Confluence space, ADO org, SDD tool, code layout) read them from `docs/agents/*.md` in your project. Run once per repo, then commit the files:

```
/setup-project-config
```

It writes one file per topic (`sdd.md`, `code-structure.md`, `atlassian.md`, `azure-devops.md`, …) and an `## Agent skills` pointer in your `CLAUDE.md` or `AGENTS.md`. Credentials never go there; they stay in `~/.env.mcp-<name>` or OAuth.

## All 19 Skills

### Setup

| Skill | What it does |
|-------|--------------|
| [setup-project-config](skills/setup-project-config/SKILL.md) | Writes per-repo settings to `docs/agents/*.md` and the `## Agent skills` pointer |
| [install-atlassian-mcp](skills/install-atlassian-mcp/SKILL.md) | Installs the Atlassian (Jira + Confluence) MCP server |
| [install-azure-devops-mcp](skills/install-azure-devops-mcp/SKILL.md) | Installs the Azure DevOps MCP server |
| [install-playwright-mcp](skills/install-playwright-mcp/SKILL.md) | Installs the Playwright browser-automation MCP server |
| [install-sentry-mcp](skills/install-sentry-mcp/SKILL.md) | Installs the Sentry MCP server (remote OAuth or local stdio) |

### Git and pull requests

| Skill | What it does |
|-------|--------------|
| [git-commit-conventional-strict](skills/git-commit-conventional-strict/SKILL.md) | Conventional Commits with gitmoji, tuned for `git-cliff`; splits spec and code changes |
| [generate-pr-notes](skills/generate-pr-notes/SKILL.md) | Writes a pull request description from the branch diff |
| [explain-diff-html](skills/explain-diff-html/SKILL.md) | Explains a diff, branch or PR as a rich HTML page |

### Azure DevOps

| Skill | What it does |
|-------|--------------|
| [ado-open-pr](skills/ado-open-pr/SKILL.md) | Pushes the branch, writes notes, opens the PR, adds reviewers, syncs drifted spec docs |
| [ado-pr-code-review](skills/ado-pr-code-review/SKILL.md) | Security-focused review of a PR with inline comments |
| [ado-pr-resolve-comments](skills/ado-pr-resolve-comments/SKILL.md) | Resolves active review comments with consent-gated fixes |
| [ado-pr-teams-notify](skills/ado-pr-teams-notify/SKILL.md) | PR notifications in a Teams channel through one Power Automate flow |

### Spec-driven development

```
[PRD in Confluence] ─ prd-to-sdd-spec ─▶ [prd-source.md] ─ spec-kit / openspec ─▶ [spec.md, plan.md]
   ─ tech-plan-to-wiki ─▶ [Confluence design review] ─ tech-plan-to-ticket ─▶ [Jira root + subtasks]
   ─ implement, open PR ─▶ sdd-qa-to-ticket ─▶ [Jira QA sub-tickets]
```

| Skill | What it does |
|-------|--------------|
| [prd-to-sdd-spec](skills/prd-to-sdd-spec/SKILL.md) | Turns a Confluence or Jira-linked PRD into a local source file for the SDD tool |
| [tech-plan-to-wiki](skills/tech-plan-to-wiki/SKILL.md) | Publishes spec-kit artifacts as a Confluence design review page |
| [tech-plan-to-ticket](skills/tech-plan-to-ticket/SKILL.md) | Creates a Jira root ticket and subtasks from a design review page |
| [sdd-qa-to-ticket](skills/sdd-qa-to-ticket/SKILL.md) | Derives BDD QA scenarios and creates Jira QA sub-tickets |
| [spec-recalibrate](skills/spec-recalibrate/SKILL.md) | Updates stale spec docs to match the code that implements them |
| [sync-api-spec](skills/sync-api-spec/SKILL.md) | Maintains `docs/agents/api-spec.md` from the API routes; optional Confluence publish |

See the [SDD workflow guide](docs/sdd-workflow-spec-kit-native.md), [quick reference](docs/sdd-quick-reference.md) and [skills map](docs/sdd-skills-map.md).

### Other

| Skill | What it does |
|-------|--------------|
| [agent-playtest](skills/agent-playtest/SKILL.md) | Evidence-grounded simulated playtests of web games and 3D worlds with browser subagents |

## Project Structure

```
.
├── skills/<name>/          # one folder per skill: SKILL.md + optional scripts/, references/, templates/
├── .claude-plugin/         # Claude Code plugin + marketplace manifests
├── docs/                   # skill anatomy and SDD workflow guides
└── scripts/                # validate-skills.sh (run in CI)
```

## Elsewhere

Not vendored here; install them from their own repos when a project needs them:

- [`mattpocock/skills`](https://github.com/mattpocock/skills): `grill-me`, `grill-with-docs` (interview you about a plan until it is clear).
- [`supabase/agent-skills`](https://github.com/supabase/agent-skills): `supabase`, `supabase-postgres-best-practices`.
- [`vercel-labs/agent-skills`](https://github.com/vercel-labs/agent-skills): `react-best-practices`, `composition-patterns`, `react-view-transitions`, `react-native-skills`, `web-design-guidelines`, `deploy-to-vercel`, and more.
- [`antonbabenko/terraform-skill`](https://github.com/antonbabenko/terraform-skill): Terraform and OpenTofu.

```bash
npx skills add mattpocock/skills --skill grill-me -g
```

## Contributing

1. Create `skills/<name>/SKILL.md` following [docs/skill-anatomy.md](docs/skill-anatomy.md).
2. Run `scripts/validate-skills.sh`.
3. Try it locally: `npx skills add . --skill <name>`.
4. Add it to the table above.

## License

[MIT](LICENSE)
