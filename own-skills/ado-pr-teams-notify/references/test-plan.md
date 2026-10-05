# End-to-end test plan (state sequence)

Use fake PR numbers (e.g. 9999xx) and a title containing `[KEY-123]`. Teams bot posts cannot be deleted, so test on a channel you can tolerate cluttering.

1. Make payloads: `python3 scripts/build_test_payloads.py --out p --pr 999900 --repo REPO --org-url https://dev.azure.com/ORG/PROJECT --jira KEY-123`
2. Make sure the flow is **On**. Send in order with ~30 s gaps: `scripts/send_event.sh WEBHOOK p/01_open.json p/02_conflict.json …` (HTTP 202 = accepted).
3. After each (or at the end for the final state), read the card text from the Teams page (scroll the `PR #999900:` root into view; `document.body.innerText`).

| Step | Expect on the card |
|---|---|
| 01 open | `🚀 PR #…`, `🔵 Open`, Status `Active · no merge conflicts`, Reviewers `👀 …`, Summary = 3 lines (no 4th, no Changes), Jira link, Activity `… opened a PR`, `No comments yet` |
| 02 conflict | Status `Active · ⚠️ merge conflicts`, reply `🔔 … updated this PR` |
| 03 waiting | `🟡 Waiting for author`, Reviewers `⏳ …`, reply `⏳ … is waiting for the author` |
| 04 rejected | `🔴 Rejected`, `👎 …` |
| 05 approved with suggestions | `🟢 Approved`, reply `✅ … approved with suggestions` |
| 06 approved | `🟢 Approved`, `👍 …`, reply `… approved. Ship it!` |
| 07 comment | Latest comment box filled with time + name + text, `View comment ↗` present; reply 💬 + quoted text, `<b>` shown as text |
| 08 merged | `✅` title, `🟣 Merged`, Status `Completed · merged cleanly`, reply `🎉 … merged it` |
| 09 abandoned | `🗑️` title, `⚫ Abandoned`, Status `Abandoned` |
| 10 draft | **nothing** posted |

Also check: Activity keeps the newest 5, newest first; run history shows all runs succeeded (or read the HTTP 202 only if the run page is unreachable).
Bump test: create PR A then PR B, send an event for A → A should end up below B in the channel.
What only a human can confirm: colors/bar rendering, spacing/alignment, purple/grey bar images, notification behavior.
