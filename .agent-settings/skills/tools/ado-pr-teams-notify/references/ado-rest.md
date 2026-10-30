# Azure DevOps REST recipes

Base: `https://dev.azure.com/{org}/…?api-version=7.1`. Auth: PAT (Basic, empty user) **or** an already-logged-in browser tab (cookies).

| Need | Call |
|---|---|
| List hooks | `GET /_apis/hooks/subscriptions` |
| One hook | `GET /_apis/hooks/subscriptions/{id}` |
| Create | `POST /_apis/hooks/subscriptions` body `{publisherId:'tfs', eventType, resourceVersion, consumerId:'webHooks', consumerActionId:'httpRequest', publisherInputs:{projectId, repository, branch, notificationType?}, consumerInputs:{url}}` |
| Edit | GET → change `publisherInputs`/`consumerInputs` → `PUT /_apis/hooks/subscriptions/{id}` |
| Delete | `DELETE /_apis/hooks/subscriptions/{id}` (204) |
| Event input descriptors | `GET /_apis/hooks/publishers/tfs/eventTypes/git.pullrequest.updated` → `notificationType` values |
| Repos | `GET /{project}/_apis/git/repositories` (id, defaultBranch) |
| A PR | `GET /{project}/_apis/git/repositories/{repo}/pullrequests/{id}` |

`git.pullrequest.updated` `notificationType`: `StatusUpdateNotification` (merged/abandoned/reactivated/ready), `ReviewerVoteNotification` (approve/reject/waiting),
`ReviewersUpdateNotification`, `PushNotification` (source branch updated; **too noisy, not used**).
Resource versions: created 1.0, comment event 2.0, updated 1.0. Branch filter = PR **target** branch (`main`, not `refs/heads/main`).

## Browser-cookie recipe (no PAT)
Open any `dev.azure.com/{org}/…` page in the session first (same origin, otherwise CORS fails). Then:
- **ego-browser**: `const r = await page.fetch(url, {method, credentials:'include', headers:{Accept:'application/json', 'Content-Type':'application/json'}, body: JSON.stringify(obj)})`; the result has `.status` and `.body` (string).
- **Playwright**: `await page.evaluate(async ([u,m,b]) => { const r = await fetch(u,{method:m,credentials:'include',headers:{Accept:'application/json','Content-Type':'application/json'},body:b}); return {status:r.status, text:await r.text()}; }, [url, method, bodyJsonOrNull])`.
Prefer REST over the Service Hooks UI wizard: its dropdowns are virtualized lists that automation rarely selects correctly, and double-clicking a row shows a misleading "managed by the consumer service" alert (right-click → Edit… is the real editor).

## Backfilling an open PR
`scripts/backfill_pr.py` fetches the PR and POSTs it to the webhook as a `created` event with `createdDate = creationDate`. PRs created before the hooks existed otherwise never get a card.


**Draft to publish (verified 2026-10-05):** ADO sends `git.pullrequest.updated` with message `X published the pull request` and an EMPTY `notificationType`, so a hook filtered on StatusUpdate/ReviewerVote never sees it. Subscribe to `updated` with notificationType Any (3 hooks per repo: created, comment, updated) and let the flow ignore push / reviewer-list / ref-update / marked-as-draft events. Real vote events say only `voted on pull request`; read `resource.reviewers[].vote` (10, 5, 0, -5, -10).
