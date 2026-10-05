# Orchestration

## Sizing

The table below gives measured throughput: wall-clock time per item per player, play only. Plan with these figures.

| Run | Items | Players | Wall clock | Per item per player |
|---|---:|---:|---|---|
| 2D web games, many quick exclusions | 37 | 5 | about 23 min, audit included | about 2.3 min |
| 2D games, retry pool | 78 | 6 | about 55 min | about 4 min |
| 3D scenes and games in mixed "experience" rooms | 74 | 4 | about 55 min end to end | about 2 min play, plus about 15 min audit and validation |

Rule of thumb: (items ÷ players) × 3–4 min, plus 15 min of orchestrator work. Increase the estimate for 3D or slow-loading
content.

## Parallelism

- The default is at most 4 players. Above 4 or 5 players sharing one browser, background-tab throttling and input loss
  went up in practice.
- Have each player turn on **focus emulation** after every navigation. This is the CDP call
  `Emulation.setFocusEmulationEnabled {enabled: true}` (see `browser-adapters.md`). Without it, tabs in the background
  stall on loading.
- The orchestrator owns browser allocation. Follow the adapter skill's TaskSpace rules; contexts, tabs and TaskSpaces are not interchangeable. Workers only close resources they own.
- Players write only inside their own items' folders. Only the orchestrator writes `campaigns.json`, `plan.json`,
  `derived/` and `blockers.md`.

## Dispatch recipe (Claude Code)

1. Write `archive/<campaign>/plan.json` with `work.agentN = [item, ...]`, in priority order.
2. Write `archive/<campaign>/AGENT_BRIEF.md` from `templates/agent_brief.md`.
3. Launch one background subagent per slice. Its prompt is: "You are agentN of campaign <id>. Read AGENT_BRIEF.md and do
   your list." A mid-tier model works for playing. Use the strongest model for auditing.
4. Wait for completion notifications. Do not poll.
5. When a player finishes, check that every item in its slice has an attempt for this campaign. Players skip items by
   mistake; it has happened. Re-dispatch only genuinely omitted, unstarted items after confirming no live worker owns them. Quota/crash leftovers stay incomplete for a separately scheduled batch, not a concurrent retry.

## Timeouts and ghost runs

- Wrap every browser call in a shell `timeout` (120–150 s). A single hung wait once blocked a player for 7 minutes.
- Killing the CLI wrapper may not stop a script already running inside the browser runtime. Before reusing a session,
  confirm that no old script is still acting on it, and finish stale sessions explicitly.

## Merging results

There is no merge step. Every attempt is appended to its item's `playtest.json`. `derived/` is always rebuilt from
`items/` by the scripts. Earlier attempts and shots are never deleted, except shots of rejected attempts when a data
owner asks for it.
