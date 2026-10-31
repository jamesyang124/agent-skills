# Card layout and copy (what readers see)

Main card (full width). Order top to bottom; labels are normal-case bold, values wrap, one row per field.

```
▌ 🚀 PR #1234: [PROJ-123] Title, max 2 lines…      ← accent-blue bold, status icon prefix 🚀 active / ✅ merged / 🗑️ abandoned
▌ 🟢 Approved                                           ← chip (plain bold text, colored; no box), equal small spacing above/below
▌ Author     Alice Dev
▌ Repo       my-repo
▌ Branch     feature/x ➔ master                         ← refs/heads/ stripped
▌ Jira       PROJ-123                               ← link built from the first [KEY-123] in the title; "—" if none
▌ Reviewers  👍 Bob · ⏳ Carol · 👎 Dan · 👀 Eve         ← groups (isContainer) are filtered out
▌ Status     Active · no merge conflicts
▌ ───────────────────────────────────────────────
▌ Summary    first 3 non-empty lines under "## Summary" (fallback: first lines of the description; Jira/URL/heading lines skipped)
▌ ───────────────────────────────────────────────
▌ Activity
▌ 10/3 02:42   🎉 **Bob** merged it                     ← time column = same 105px as the labels; newest first; max 5
▌ 10/3 02:40   ✅ **Carol** approved. Ship it!
▌ ───────────────────────────────────────────────
▌ Latest comment
▌ 10/3 02:41   💬 **Bob**
▌              comment text, max 2 lines
▌                                          View comment ↗   ← markdown link, far right; thread deep link, falls back to the PR
▌ [ View in Azure DevOps ]                              ← the only bordered button
```
`▌` = 1px state bar (see gotchas: renders thicker in Teams). No comments yet → one left-aligned line `💬 No comments yet`.

## State (chip + bar) precedence
Merged → Abandoned → Rejected (any vote −10) → Waiting for author (any −5) → Approved (any 10 or 5) → Open.

| State | Chip | Bar | Chip text color |
|---|---|---|---|
| Open | 🔵 Open | #5B5FC7 | Accent |
| Approved | 🟢 Approved | #2E9E4F | Good |
| Waiting for author | 🟡 Waiting for author | #D9A400 | Warning |
| Rejected | 🔴 Rejected | #C4314B | Attention |
| Merged | 🟣 Merged | #8764B8 | Default (Adaptive Cards have no purple text) |
| Abandoned | ⚫ Abandoned | #605E5C | Default |

Status row: `Completed · merged cleanly` · `Active · no merge conflicts` · `Active · ⚠️ merge conflicts` · `Abandoned` (from `status` + `mergeStatus`; no extra API calls).

## Thread replies (plain HTML text, names bold, no time, no tint)
| Event | Reply |
|---|---|
| comment | 💬 **name** left a comment  + next line the quote (≤140 chars, HTML-escaped) |
| approved | ✅ **name** approved. Ship it! |
| approved with suggestions | ✅ **name** approved with suggestions |
| rejected | 💔 **name** rejected this with a heavy heart |
| waiting for author | ⏳ **name** is waiting for the author |
| merged | 🎉 **name** merged it |
| abandoned | 🗑️ **name** abandoned this PR |
| other status change | 🔔 **name** updated this PR |
`created` has no reply: the root card is the post. Activity lines use the same wording with `🚀 **name** opened a PR`.

## Who can see it / what readers should know (copy into the announcement)
- One card per PR; follow its Activity instead of expanding the thread. Active PRs jump to the bottom of the channel.
- Comment in **Azure DevOps**; the card shows the latest comment. Teams replies are free discussion and do **not** sync back to ADO or the card.
- Draft PRs are silent until marked ready. Only PRs targeting the configured branch of each repo appear.
- Bot posts cannot be deleted from Teams.
