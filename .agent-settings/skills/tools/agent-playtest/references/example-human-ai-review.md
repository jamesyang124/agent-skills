# Worked example: human + AI review of items the agents could not play

This is one real run, written up so someone else can repeat the process. Roles: **orchestrator** (the AI session),
**reviewer** (the human), **players** (AI subagents). Site: a web game catalog (VIVERSE profile). Total reviewer time:
about 15 minutes of play plus short narrations.

## 1. Trigger

A 74-item campaign finished with 4 items `excluded_unresponsive`: the agents' inputs had no visible effect. 7 more were
paywalled and set aside as exceptions until someone with the entitlement could check them.

## 2. Triage: is a human review worth it?

The orchestrator first compared the 4 items with the rest of the campaign, so the reviewer could decide on evidence
and not on a guess:

| Signal | The 4 items | Campaign median |
|---|---|---|
| real searches (sampled log, 2 weeks) | 0–2 | 2 / 0 |
| autocomplete requests | 3–32 | 22.5 |
| views | 56–141 | 96.5 |
| similar items already described | match-3: 6, solitaire: 4, memory: 3 | — |

The orchestrator recommended skipping all 4, and named one exception (the highest autocomplete count and a mechanic
nobody had covered yet). The reviewer chose to review all 4. Both outcomes are fine. What matters is that the decision
and its reason are written down.

## 3. Setup

1. The orchestrator opened the 4 items in one browser session, one tab each, and handed control to the reviewer.
2. The first attempt at recording, injecting an event recorder into the page, failed: the games run in cross-origin
   iframes, and the adapter cannot send commands into them. The orchestrator logged a blocker and switched to an
   OS-level recorder (`scripts/record_input.py`).
3. Set, then go, for each item (`human-demo.md` steps 2–5): permission preflight → recorder started in the background →
   wait for `GO` → only then tell the reviewer "start item N".

## 4. Demo loop (per item)

The reviewer played, then said "next" with one sentence. Each recording lasted 2 to 4.5 minutes.

| Item | Reviewer's narration (short) | What the recording showed | What the agent had done |
|---|---|---|---|
| peg solitaire (3D) | press a peg, then a hole; legal moves glow green | 99 presses, 62 with zero movement, about 100 ms each | pressed the peg, then a guessed hole; the counter stayed at 0 |
| connect-tiles puzzle | drag through adjacent same-colour tiles before the timer runs out | 48 drags, median 25 px, held about 175 ms | tried swaps (the wrong mechanic) |
| card game | play hand cards onto centre piles in order; extras go to side piles; full rules unclear | 49 of 80 presses were drags, median 162 px, held about 400 ms | stopped after the menus and never reached a hand |
| match-3 (swap) | drag to swap adjacent hearts, like another match-3 already described | 15 of 18 presses were drags, median 155 px, held about 570 ms | fast drags with 30 ms steps |

At the end, the orchestrator took the browser back, saved one end-state screenshot per item as evidence of what the
reviewer reached (for example "Game Over, 4 pegs left, 28 moves"), and closed the session.

## 5. Compare → fix → replay

For each item, the orchestrator wrote `demos/<item>.md`: the narration verbatim, the recording statistics, the agent's
logged attempt, the difference, and the fix. It turned the fixes into protocol rules (`play-protocol.md` technique 6)
and sent one player per item to replay it (`method: closed_loop_after_demo`).

| Item | Replay result | What made the difference |
|---|---|---|
| peg solitaire | **played**, about 80 s, 4 moves | zero-movement press on the peg; screenshot; press the **visible rim** of a green spot (a spot's centre can sit behind a front peg) |
| card game | **played**, about 50 s | drag-and-drop with a 400 ms hold onto the build pile; the rules were observed, not looked up |
| match-3 (swap) | first replay: still unresponsive. **Then played** (about 36 s, 2 rounds, score 0→95 twice), run by the orchestrator | the cause was **call-startup time** (20–30 s per browser call against a 30 s round), not the input; the fix was a whole round inside one call that reads tile colours and computes swaps |
| connect-tiles puzzle | first replay: partial after audit (over-claimed). **Then played** (about 50 s, 2 rounds, score 0→95 and 0→245) | same timing fix with a path search; the first replay's "only the first drag scores" was the same timing problem |

**Outcome:** all 4 "unplayable" items were played. Two needed only the reviewer's technique. The other two needed the timing fix, which the reviewer anticipated ("you are probably just stuck on the menu"). Valid descriptions went from 376 to 380. The audit step caught one over-claim. One incident: a guessed press hit a pre-roll ad. It is logged, and the rule "screenshot before the first press" is now in the protocol.

## 6. Incidents during the review, and the fixes now in the skill

- **Keystrokes captured.** The first recording logged the reviewer's chat typing (355 keys). The orchestrator deleted
  those events immediately and told the reviewer. The recorder now defaults to mouse only; with `--keys` it keeps game
  keys only and masks everything else.
- **Recorder not stopped.** Killing the `uv` wrapper left the recorder running into the next item, and the overlap had
  to be trimmed. The recorder now writes `<out>.pid`; stop it with `kill -TERM $(cat <out>.pid)`, then confirm the
  file ends with `stop`.
- **No in-page recording in cross-origin iframes.** Use OS-level recording (see `browser-adapters.md`).

## 7. Reuse checklist

- [ ] The triage table is written, and the reviewer decides which items to review
- [ ] Items are open in one session and control is handed to the reviewer
- [ ] Preflight shows `READY_CHECK ok`
- [ ] Per item: `GO` seen → "start" → reviewer plays and narrates → recorder stopped and the stop confirmed
- [ ] End-state screenshots saved, and the session closed
- [ ] `demos/<item>.md` written (narration verbatim, stats, agent attempt, difference, fix)
- [ ] Protocol rules updated, then one replay per item with `closed_loop_after_demo`
- [ ] Blockers logged; items still stuck → a human-demo-based description or a documented exception
- [ ] Keyboard events checked for accidental text before the files are kept
