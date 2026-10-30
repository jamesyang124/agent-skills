# external

Vendored copies of skills from other repos. Nothing here is installed by `import-skills.sh` (it only scans `.agent-settings/skills/`).

| Skill | Source | Notes |
|---|---|---|
| `grill-me` | `mattpocock/skills` (productivity/grill-me) | Interview the user about a plan until shared understanding. Standalone. |
| `grill-with-docs` | `mattpocock/skills` (engineering/grill-with-docs) | Same, and keeps `CONTEXT.md` and `docs/adr/` up to date. Standalone; creates those files if missing. |

`skills-lock.json` records the source and content hash of each copy. Restore or update with the `skills` CLI (`npx skills experimental_install`, `npx skills update`). To change a skill, fork it into `.agent-settings/skills/workflows/` so `import-skills.sh` can install it.
