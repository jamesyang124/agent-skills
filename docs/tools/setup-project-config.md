# Setup Project Config

A one-time setup skill that generates `.agent-settings/project-config.md` by scanning your
codebase and asking for your Confluence and Jira details.

## Why

Other skills (`api-spec-to-confluence`, `sdd-tech-plan-to-confluence`, `confluence-tech-plan-to-jira`)
need to know your project's structure and Atlassian workspace. Instead of configuring each skill
separately, this skill generates one shared config file that all of them read.

## When to Run

- **First time**: after installing skills into a project
- **After structure changes**: framework migration, directory rename, new API prefix, etc.
- **After Atlassian changes**: moved to a new space, different Jira project, etc.

## How to Use

**Initial setup** — scans codebase + asks for Confluence/Jira details:
```
"set up project config"
"init project config"
"configure skills"
```

**Re-calibrate after code changes** — re-scans structure, preserves Atlassian settings:
```
"recalibrate project config"
"update project config"
"my framework changed, update the config"
```

**Update Atlassian settings only** — skips code scan:
```
"update confluence settings"
"change jira project key"
```

## What the Agent Does

1. Detects mode (initial vs. re-calibration) based on whether the config file exists
2. Scans the codebase to detect language, framework, router file, handler/DTO/service directories,
   API path prefix, and documentation annotation style
3. For initial setup: prompts for Confluence URL, space key, parent pages, Jira URL and project key
4. For re-calibration: shows only what changed in code structure and preserves existing Atlassian settings
5. Confirms the full config before writing `.agent-settings/project-config.md`

## What Gets Generated

`.agent-settings/project-config.md` contains:

| Section | Fields |
|---------|--------|
| Confluence | Base URL, space key, common parent pages (name + ID + URL) |
| Jira | Base URL, default project key, default issue type |
| Code Structure | Language, framework, router file path, handler/DTO/service directories, API prefix |
| Documentation Format | Annotation style (Swaggo, JSDoc, FastAPI), specific tags and binding patterns |

## Supported Project Types

| Language | Frameworks Detected |
|----------|---------------------|
| Go | Gin, Echo, Chi |
| Node.js | Express, Fastify, Koa, Hapi |
| Python | FastAPI, Flask, Django |
| Rust | Actix-web, Axum |

## Notes

- The config file is gitignored in this template repo — it belongs to your project, not the skills repo
- If you've installed the skills into your own project repo, you can choose to commit `project-config.md` there
- To update any values, just re-run the skill — it will show a diff and confirm before writing
- Atlassian credentials (username, API token) are stored separately in `.env.mcp-atlassian`, not in this config
