# Architecture and design decisions

## Data flow
1. ADO fires a Service Hook (`webHooks` consumer, action `httpRequest`) with `eventType`, `resource`, `message.text`, `createdDate`.
2. The flow's trigger is the Teams-webhook trigger (kind `TeamsWebhook`); the schema is relaxed to `{"type":"object","properties":{}}` so any ADO payload is accepted.
3. `Switch` on `eventType` (`git.pullrequest.created`, `git.pullrequest.updated`, `ms.vss-code.git-pullrequest-comment-event`).
4. State is kept **in the card itself**: hidden TextBlocks with ids `p_activity`, `p_lc_head`, `p_lc_text`, `p_lc_url`. On each event the flow finds the
   root post (`Get messages` in the channel → filter where the attachment text contains `PR #<id>:`), reads those blocks back, and rebuilds the whole card.
   No database. Limit: only the most recent page of channel messages is searched; a very old PR falls back to posting a new card.

## Why these choices
| Decision | Reason |
|---|---|
| One flow, one webhook for all repos/events | one thing to maintain; the card shows Repo; ADO subscriptions are the only per-repo config |
| One card per PR, updated in place | threads stay readable; status visible without opening anything |
| A one-line reply per event | **replies bump a thread to the bottom and notify; edits do not** (verified: A then B created, event on A → order becomes B, A) |
| Full-width cards (`msteams.width = Full`) | text fits; sections align |
| Activity kept as `text‖time` lines in a hidden block | fixed-width time column on the left; 5 newest events; older v-cards seed from `p_latest` |
| Draft PRs skipped | noise; they appear as a new card on the first non-draft `updated` event if no root exists |
| Comment hook has the target-branch filter | otherwise comments on unannounced PRs would create orphan cards |
| Replies are plain HTML text, not cards | cannot be tinted; keeps the thread visually quiet |
| `Reply with a message` / `Reply with an adaptive card` need `body/parentMessageId` at the top of `body` | NOT under `recipient` (that fails import with `WorkflowOperationParametersExtraParameter`) |

## Not supported
- Syncing Teams replies back to ADO (the channel trigger only fires for root messages).
- Deleting or merging bot replies.
