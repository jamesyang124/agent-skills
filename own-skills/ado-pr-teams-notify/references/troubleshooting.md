# Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Webhook returns **400 `WorkflowTriggerIsNotEnabled`** | the flow is Off (always after an import): details page → Turn on |
| Webhook 202 but the run **fails** `Property 'type' must be 'AdaptiveCard'` | the template's default definition is still in place → import the generated package |
| Import fails `WorkflowOperationParametersExtraParameter … parentMessageId` | `body/recipient/parentMessageId` is wrong; it is `body/parentMessageId` |
| Import page: Import button never enables | flow row not set to Update/target, or connection row not saved: reopen each panel, pick a row, Save (the panels need a real mouse click on the row, then Save) |
| Download event never fires (ego) | `Page.setDownloadBehavior` first; click the Download button |
| Card says `Alice updated updated this PR` / names carry extra words | verb not in the marker list; add it to `markers` in the generator |
| Someone cannot see the cards | channel is private or they are not in the team; add them (flow unaffected) |
| Cards appear for PRs targeting other branches | hook branch filter missing/wrong; branch is the PR *target* |
| Orphan comment cards | comment hook has no branch filter → set it like the others |
| Thread does not move to the bottom | only replies bump; check the reply action ran (run history) |
| Old PR gets a new card on every event | the root is no longer in the last page of channel messages; backfill or accept |
| Teams card too tall / colored bar thick | platform padding; use `--no-bar` if the bar is unwanted |
| Reviewer shows `⬜`/white items invisible | white emojis vanish on white surfaces; use 👀 |
| `GET /hooks/subscriptions` CORS error in a browser | not on a `dev.azure.com` page; navigate there first, or use a PAT |
| ADO UI hook list: "managed by the consumer service" | that row is a different consumer; right-click → Edit… on Web Hooks rows, or use REST |
| Cannot delete bot posts | not possible in Teams or via the connector; channel owner/admin only |


## After every flow import
Importing a package turns the flow Off. Turn it On right away on the details page: while it is Off the webhook returns 400 `WorkflowTriggerIsNotEnabled`, ADO marks those deliveries failed and puts the hook on probation, and events in that window are lost (resend them from the hook's notification history).
