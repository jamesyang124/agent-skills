---
name: install-external-skills
description: Interactive multi-select installer for external agent skill registries. Reads project-config.md to derive best-fit skills for the project, fetches latest version info from GitHub, and installs selected skills via npx. Supports supabase/agent-skills, vercel-labs/agent-skills, and antonbabenko/terraform-skill. Use when asked to install external skills, browse skill registries, or add community skills.
allowed-tools: Bash(npx *), Bash(curl *), Bash(node *), Bash(cat *), Bash(echo *), Bash(printf *), Bash(which *)
---

# Install External Skills

Reads your project config to recommend best-fit skills, fetches the latest registry info from GitHub, and installs your selection via `npx skills add`.

## Usage

```
/install-external-skills
```

---

## Phase 0 — Read Project Config

Check for `.agent-settings/project-config.md`:

```bash
cat .agent-settings/project-config.md 2>/dev/null
```

**If the file exists**: read it and extract:
- `language` / `framework` (e.g. Go/Gin, Node/Next.js, Python/FastAPI)
- `infrastructure` or `iac` fields if present (e.g. Terraform, OpenTofu)
- `database` fields (e.g. Postgres/Supabase)
- Any other tooling signals

Use these signals in **Phase 2** to determine which skills are best-fit for this project. Do NOT show a generic list of all skills — lead with recommendations.

**If the file does not exist**: print this message before continuing:

```
⚠ No project config found at .agent-settings/project-config.md

  Without it, I can only show all available skills without project-specific
  recommendations. Consider running /setup-project-config first to generate it.

  → https://github.com/your-org/agent-settings (setup-project-config skill)

Continue without project config? (y/n)
```

- Blank input: re-prompt — must type `y` or `n`.
- `n` → stop and instruct the user to run `/setup-project-config` first.
- `y` → proceed to Phase 1 in "browse all" mode (no recommendations).

---

## Phase 1 — Registry Selection

Present the supported registries. If project config was read, pre-select registries that are relevant based on the detected stack and note why:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  External Skill Registries
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [1] supabase/agent-skills                              ★ recommended
      Supabase Agent Skills — Postgres, Auth, Supabase tooling.
      → https://github.com/supabase/agent-skills

  [2] vercel-labs/agent-skills
      Vercel's official collection — React, Next.js, deployment, UI.
      → https://github.com/vercel-labs/agent-skills

  [3] antonbabenko/terraform-skill
      Terraform & OpenTofu — testing, modules, CI/CD, security patterns.
      → https://github.com/antonbabenko/terraform-skill

  [0] Cancel

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Select registries to browse (space-separated, e.g. 1 3), or 0 to cancel:
```

Mark registries with ★ when the project config indicates they are relevant. Briefly note the reason (e.g. `★ recommended — Postgres detected in project config`).

---

## Phase 2 — Fetch Registry Info and Derive Recommendations

For each selected registry, fetch the live README from GitHub:

### supabase/agent-skills
- README: `https://raw.githubusercontent.com/supabase/agent-skills/main/README.md`
- Latest commit: `https://api.github.com/repos/supabase/agent-skills/commits/main`
- **Fallback known skills:**
  | Skill ID | Description | Link |
  |---|---|---|
  | `supabase` | Supabase CLI, database, auth, storage, edge functions | https://github.com/supabase/agent-skills/tree/main/skills/supabase |
  | `supabase-postgres-best-practices` | Postgres query optimization, indexing, schema best practices | https://github.com/supabase/agent-skills/tree/main/skills/supabase-postgres-best-practices |
- **Install:** `npx skills add supabase/agent-skills --skill <skill-id>`

### vercel-labs/agent-skills
- README: `https://raw.githubusercontent.com/vercel-labs/agent-skills/main/README.md`
- Latest commit: `https://api.github.com/repos/vercel-labs/agent-skills/commits/main`
- **Fallback known skills:**
  | Skill ID | Description | Link |
  |---|---|---|
  | `react-best-practices` | React/Next.js performance — 40+ rules | https://github.com/vercel-labs/agent-skills/tree/main/skills/react-best-practices |
  | `web-design-guidelines` | UI/UX audit — 100+ rules for a11y, perf, design | https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines |
  | `react-native-guidelines` | React Native best practices | https://github.com/vercel-labs/agent-skills/tree/main/skills/react-native-guidelines |
  | `react-view-transitions` | React View Transition API and Next.js integration | https://github.com/vercel-labs/agent-skills/tree/main/skills/react-view-transitions |
  | `composition-patterns` | React composition patterns — compound components | https://github.com/vercel-labs/agent-skills/tree/main/skills/composition-patterns |
  | `vercel-deploy-claimable` | Deploy to Vercel — auto-detects 40+ frameworks | https://github.com/vercel-labs/agent-skills/tree/main/skills/vercel-deploy-claimable |
- **Install:** `npx skills add vercel-labs/agent-skills --skill <skill-id>`

### antonbabenko/terraform-skill
- README: `https://raw.githubusercontent.com/antonbabenko/terraform-skill/master/README.md`
- Latest commit: `https://api.github.com/repos/antonbabenko/terraform-skill/commits/master`
- Latest release: `https://api.github.com/repos/antonbabenko/terraform-skill/releases/latest`
- **This is a single-skill repo** — installs as one unit covering: testing strategy, module patterns, CI/CD workflows, security/compliance, and common anti-patterns.
  | Skill ID | Description | Link |
  |---|---|---|
  | `terraform-skill` | Terraform & OpenTofu — testing, modules, CI/CD, IaC best practices | https://github.com/antonbabenko/terraform-skill |
- **Install (claude plugin):**
  ```bash
  git clone https://github.com/antonbabenko/terraform-skill ~/.claude/skills/terraform-skill
  ```
  Or via Claude Code marketplace: `/plugin marketplace add antonbabenko/terraform-skill`

### Recommendation logic (apply when project config was read)

| Detected signal | Recommended skill(s) |
|---|---|
| `database: postgres` or `supabase` in stack | `supabase`, `supabase-postgres-best-practices` |
| `framework: next.js` or `react` | `react-best-practices`, `web-design-guidelines` |
| `framework: react-native` or `expo` | `react-native-guidelines` |
| `iac: terraform` or `opentofu` in config | `terraform-skill` |
| Deploying to Vercel (detected `vercel.json` or `vercel` in scripts) | `vercel-deploy-claimable` |
| No strong signals | show all skills without ★ |

---

## Phase 3 — Display Skills with Version and Recommendations

For each selected registry, display:
1. Latest commit SHA + message (or latest release tag if available)
2. Skills list — **recommended skills marked ★**, others listed below a divider
3. A brief sentence explaining why ★ skills match this project (if config was read)
4. `[All]` option to install everything from that registry

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  supabase/agent-skills  (latest: abc1234 — "feat: add release...")
  → https://github.com/supabase/agent-skills
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Recommended for your project (Postgres detected):

  [1] supabase-postgres-best-practices ★
      Postgres query optimization, indexing, schema best practices.
      → https://github.com/supabase/agent-skills/tree/main/skills/supabase-postgres-best-practices

  Other available:
  [2] supabase
      Supabase CLI, database, auth, storage, edge functions.
      → https://github.com/supabase/agent-skills/tree/main/skills/supabase

  [A] Install ALL supabase/agent-skills skills
...
```

Numbers are globally unique across all displayed registries. `A`, `B`, `C` correspond to "install all" per registry in display order.

---

## Phase 4 — Confirm Before Install

Show a confirmation summary **before** running any commands:

```
The following skills will be installed:

  • supabase/agent-skills  --skill supabase-postgres-best-practices
      npx skills add supabase/agent-skills --skill supabase-postgres-best-practices

  • antonbabenko/terraform-skill
      git clone https://github.com/antonbabenko/terraform-skill ~/.claude/skills/terraform-skill

Proceed? (y/n)
```

- Blank input: re-prompt — must type `y` or `n`.
- `n` → return to Phase 3.

---

## Phase 5 — Execute Installation

Run each install command sequentially. For each:

1. Print: `Installing <skill-id> from <registry>...`
2. Run the appropriate install command (npx for supabase/vercel-labs; git clone for terraform-skill).
3. On success: print ✓ and the skill name.
4. On error: print ✗, show the error output, ask `[r]etry / [s]kip / [a]bort all`.

After all installs complete, print a summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Installation complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓ supabase-postgres-best-practices  (supabase/agent-skills)
  ✓ terraform-skill                   (antonbabenko/terraform-skill)

Reference links:
  • https://github.com/supabase/agent-skills
  • https://github.com/antonbabenko/terraform-skill

Skills are now available to your agent. Restart your agent session if needed.
```

---

## Error Handling

- **`npx` not found**: warn and suggest installing Node.js from https://nodejs.org
- **Network error fetching README**: fall back to the known-skills table in Phase 2, note it may be outdated.
- **Registry returns 404**: warn that it may have moved and show the reference URL.
- **GitHub API rate-limited (403/429)**: use cached/hardcoded data, note the limit.
- **`npx skills add` or `git clone` exits non-zero**: show full error output. Offer `[r]etry`, `[s]kip`, `[a]bort all`.

---

## Global Rules

- **Always fetch live README** before displaying skills — do not rely solely on the hardcoded table, which is a fallback only.
- **Always show reference links** for every registry and every individual skill.
- **Never install without confirmation** (Phase 4 is mandatory).
- When fetching from the GitHub API, handle rate-limit responses (HTTP 403/429) gracefully by noting the limit and using cached/hardcoded data instead.
