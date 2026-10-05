---
name: ado-pr-teams-notify
description: "Set up and operate Azure DevOps pull-request notifications in a Microsoft Teams channel via one Power Automate flow: one color-coded Adaptive Card per PR (state chip, reviewers, Jira link, Summary, stacked Activity, latest comment), a one-line thread reply per event so active PRs float to the bottom, draft PRs skipped, many repos and branches into one flow. Covers the whole path: Teams channel Workflows template, export/edit/import of the flow package, Azure DevOps Service Hook subscriptions (REST), end-to-end state tests, backfilling an already-open PR, adding repos, switching channels, and the Teams/Power Automate gotchas. Browser-agnostic: ego-browser, Playwright, Chrome DevTools MCP, or any agent-friendly browser; REST parts also run browserless with a PAT. Trigger: /ado-pr-teams-notify"
trigger: /ado-pr-teams-notify
---

# ADO pull requests → one card per PR in a Teams channel

```
Azure DevOps Service Hooks (4 per repo) ──HTTP POST──▶ Power Automate flow (Teams "webhook alerts" template, one URL)
   created · commented · updated(any type)          │ Switch on eventType
                                                                   ├─ created   → post root card            (skip drafts)
                                                                   ├─ updated   → update root card + 1-line reply
                                                                   └─ commented → update root card + 1-line reply (quote)
```

Result in Teams: **one main card per PR** (updated in place) + **one short reply per event** (bumps the thread to the bottom
of the channel and notifies). The card shows what a reader needs without opening the thread. Layout and exact copy:
`references/card-and-copy-spec.md`. Architecture and the reasoning behind each choice: `references/architecture.md`.

## What you need before starting (ask the user for anything missing)

| Input | Where it comes from |
|---|---|
| ADO org, project, and `repo = target branch` list | the user (branch = the PR **target**; use the repo's default branch unless told otherwise, and say so if it differs from what they stated) |
| Teams team + channel | the user; the channel must be one the flow owner is a member of. Private channel = only its members can see the cards |
| Jira base URL, display timezone | the user (cards link `[KEY-123]` in PR titles; times shown in that timezone) |
| A browser session logged in to Teams, Power Automate and Azure DevOps | the user (this skill does not log in; an SSO session must already exist) |
| Optional: an ADO personal access token | lets the REST steps run without a browser (`ADO_PAT`) |

Browser: any of **ego-browser, Playwright, Chrome DevTools MCP** works; mapping in `references/browser-adapters.md`.

## Phases

1. **Create the template flow** (Teams). In the target channel use *Workflows → "Send webhook alerts to a channel"*. This yields a flow with a
   Teams-webhook trigger, a connection, and the **webhook URL** (HTTP POST URL of the trigger). Record: team id (`groupId`), channel id
   (`19:…@thread.tacv2`), flow id, webhook URL. (The ids are also visible in the flow's code view / the Teams channel link.)
2. **Export the template** (`flows/<id>/export` → name → Export → Download; zip) and unzip it.
3. **Generate the merged flow** and import it over the template:
   ```
   python3 scripts/gen_flow_definition.py --export-dir <unzipped export> --config config.json --out-dir build
   ```
   (`config.json`: copy `scripts/config.example.json`.) It writes `build/` and `flow-package.zip`. Import with *My flows → Import → Import
   Package (Legacy)*: upload the zip; flow row = **Update** → pick the existing flow; connection row = **Select during import** → your
   Teams connection; Save; **Import**. After import the flow is **Off**: open its details page and turn it **On**.
   **The final Import click may be blocked by an auto-mode safety classifier for agents; if it is, stage everything and ask the human to click Import once.**
4. **Create the Service Hooks** (4 per repo, all to the same webhook URL):
   ```
   export ADO_PAT=…; python3 scripts/ado_hooks.py create --org ORG --project PROJ --webhook-url URL --repo hubs=master --repo infra=main
   ```
   No PAT? Run the same REST calls inside a logged-in ADO tab (recipe in `references/ado-rest.md`). The comment hook gets the same target-branch
   filter as the others so comments follow only PRs that were announced.
5. **Verify with a state sequence**: `scripts/build_test_payloads.py` then `scripts/send_event.sh URL …`; read the card text back from the
   Teams page after each step (test plan and expected values: `references/test-plan.md`). Report results as text unless the user wants screenshots.
6. **Hand over**: tell the user what remains manual (Import click, deleting test posts, anything only a human could verify such as how the
   colors render) and give them `references/card-and-copy-spec.md` as the "what RDs will see" description.

## Operating the setup later

| Task | How |
|---|---|
| Show an already-open PR in Teams | `scripts/backfill_pr.py --pr N …` (posts a real `created` event; skips drafts) |
| Add a repo | `ado_hooks.py create --repo NAME=BRANCH` (idempotent) |
| Remove old hooks | `ado_hooks.py list` then `delete --id` |
| Change card layout/copy | edit `scripts/gen_flow_definition.py`, regenerate, re-import, turn the flow back **On**, re-run the state sequence |
| Move to another channel | repeat phase 1 for the new channel, put its ids in `config.json`, regenerate, import over the new template flow, repoint the hooks to its webhook URL |
| Someone cannot see the cards | they are not in the (private) channel/team; add them. Nothing to change in the flow |

## Rules that save hours (details in `references/troubleshooting.md`)

- **Edit the flow by regenerating the package, not by clicking in the designer.** The designer DOM is hard to automate; the package route is deterministic.
- After every import the flow is **Off**. A POST to an Off flow returns HTTP 400 `WorkflowTriggerIsNotEnabled`.
- Teams bot posts **cannot be deleted** (no menu item, no connector action). Use obviously fake PR numbers for tests and expect to leave them.
- Only a **reply** moves a thread to the bottom; editing a card does not. That is why every event posts one short reply.
- Do not use light-grey or white elements (⚪ ⬜, `Light` text color): cards render on a white/dark surface and become invisible.
- Colored columns get padding in Teams, so a "1px" state bar still renders thick; keep it only if the user wants the at-a-glance color.
- Real ADO event wording differs from fake payloads. Names are cut at the first verb in `message.text`; verify against the first real PR.
- Never click Import/On for the user if the harness blocks it; stage and hand it over. Never put the webhook URL signature or PAT into committed files.
