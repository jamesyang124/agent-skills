# Human-demo mode

Use this mode when an agent recorded `excluded_unresponsive*`, or when its description looks wrong. A person plays the
item while their local mouse and keyboard are recorded. The agent then compares the recording with its own logged
attempt.

Every human intervention is recorded: the input recording when macOS access is granted, otherwise narration, before/after screenshots and
times. Record what worked and write it into the patterns below.

## Why OS-level recording

Most embedded games run in a cross-origin iframe. Event listeners injected into the host page cannot see inside it,
and some adapters cannot open a CDP session in it (see `browser-adapters.md`). Recording at the OS level sees every
input, whatever the page structure.

## Steps (set, then go)

The orchestrator runs the recorder; the human only plays and narrates. One recording per item.

1. **Set: open.** Open the item in the browser and hand control to the human (ego-browser: `task.handOff()`).
2. **Set: preflight.** `uv run --with pynput python scripts/record_input.py --check` must print `READY_CHECK ok`. If it
   prints `NOT TRUSTED`, the human grants Accessibility and Input Monitoring to the app that runs the agent (Terminal,
   iTerm or the Claude app) and restarts it. Do not continue until the check passes.
3. **Set: start.** Start the recorder in the background, mouse only unless the item needs keys:
   `uv run --with pynput python scripts/record_input.py --out archive/<campaign>/demos/<item_id>.jsonl --seconds 300 [--keys]`.
   Wait until it prints `GO` and `<out>.pid` exists.
4. **Go.** Tell the human "start item X now", and only after you have seen `GO`. The human plays, then says "next"
   with 1–3 sentences: what worked, which input, anything non-obvious.
5. **Stop.** `kill -TERM $(cat <out>.pid)`. Kill the python process through its pid file. Killing the `uv` wrapper
   can leave the recorder running into the next item; this happened once and had to be trimmed. Confirm that
   `pgrep -f record_input.py` is empty and that the file's last line is `{"type": "stop", ...}`. Then repeat from step 3
   for the next item.
6. **Hand back.** When the human hands control back, take one screenshot per item of its end state.
7. **Compare.** Compare each demo with the agent's logged attempt, using the checklist below. Record the result in
   `archive/<campaign>/demos/<item_id>.md`, with the human's narration quoted.
8. **Fix and replay.** If the protocol can fix the difference, update `play-protocol.md` or the adapter notes, then
   re-run the item once as a new attempt with `method: "closed_loop_after_demo"`. If the mechanics are still unclear
   (an unfamiliar card game, say), an external rules source may be used. Cite it as `source_type: "external_reference"`
   in the evidence and keep it apart from what was observed.

## Guiding the human (the orchestrator does this, one step per message)

The human should never have to guess what comes next. Give one short instruction, wait for their answer, then give the next.
Never ask them to do something that exposes personal data, and say what each permission is for.

1. **Browser first.** Run `listTaskSpaces()`. If the space is `agentDelegatedToUser`, a permission prompt is pending: tell
   them exactly which prompt (microphone/camera) and to click **Block/Don't allow** (never Allow), then to say "done".
   Do not claim the space; they release it by finishing that prompt.
2. **Recorder permission.** Run the `--check`. If `NOT TRUSTED`, say: "System Settings -> Privacy & Security ->
   Accessibility: add and switch on <app>; same under Input Monitoring; then quit and reopen <app>." Explain it is only for a
   local, mouse-only, time-limited file. A restart ends the agent session, so first write the current state to the
   campaign notes (what is paused, the next command) and tell them to resume with `claude --resume`.
3. **After they return**, re-run `--check`; continue only on `READY_CHECK ok`.
4. **Ask before every room, start only on the human's go.** Name the room (id and title), say what you want to see demonstrated and how long it takes, then ask "start?" and do nothing else: do not open the page, wait out an ad or start the recorder yet. Begin only after the human answers start. Then open the page, wait for the ad or loading to finish, start the recorder, wait for `GO`, and only then tell them "now". One room at a time; when it is done, stop the recorder at once, summarise what the recording shows, write the lesson into this skill, and ask again before the next room.
5. **Per item**, in this order: "I opened <item> and handed you control" -> wait for `GO` -> "Start now. Play one round, then
   say what you did in a sentence" -> stop the recorder by pid and confirm the `stop` line -> "Thanks, done."
6. **Report back** in plain words: what their inputs were (type, hold, drag length) versus what the agent did, and which
   skill rule changes as a result.

## Comparison checklist

| Look at | Agent log | Human demo |
|---|---|---|
| input type | press / click / drag / key | from `record_input.py` events |
| movement between down and up | `inputs_tried[].dist` (0 for a synthetic press) | `dist` per click |
| hold time | `hold_ms` | `held_ms` |
| target position | x, y in CSS px | screen px; convert using the browser window position and device pixel ratio |
| order and timing | log order | event `t` |
| focus | was the content pressed before keys? | first event inside the content |
| on-screen hint | `controls_observed` | narration |

Typical causes found this way:
- a game that binds drag to the camera, so any tiny movement between press and release counts as a drag;
- select-then-target mechanics;
- a timing threshold for double clicks;
- the need to scroll the content into view;
- keyboard focus never reaching the content.

## Privacy

- The recorder runs only for a demo the human agreed to, for a limited time (`--seconds`, default 180), and writes one
  local file. It sends nothing anywhere.
- **The keyboard is off by default.** Key listeners are global: they also see the human typing to the agent in another
  window. In one real session, 355 chat keystrokes were captured before this default existed. With `--keys`, only
  game keys are kept by name and every other key is masked as `*`. Even so, do not type passwords while it runs.
- Stop the recorder the moment the human says they are done (their typed reply to the agent otherwise lands in the file with --keys). If it ran on, delete every non-game key event after the last play action straight away and say so.
- Delete demos that are no longer needed. Do not commit them to shared repositories.


## Reusable operation patterns (consult before requesting a new demo)

Derived from the historical four-room human review in `example-human-ai-review.md`. Timings are starting points, not guaranteed game rules; recompute coordinates from the current viewport/content. Old screenshots and human outcomes are hypotheses for a new room, never evidence of its observed behavior.

| Pattern | Match only when visible | First bounded attempt | Success signal / stop condition |
|---|---|---|---|
| Select then target | Pieces and selectable destinations; selection produces a highlight | Zero-movement press around 100–120 ms, inspect highlights, then press visible rim of a legal target | Piece moves/removes and board/counter changes. No highlight: reconsider selection; never guess repeated targets. |
| Connect adjacent tiles | Instructions or observed response indicate linking same-colour adjacent tiles | Hold and drag through one short visible adjacent path, then release | Linked tiles clear or score changes. No result: do not assume swapping is equivalent. |
| Card drag/drop | Cards, hand/build/discard areas and compatible visible instructions | Hold around 400 ms, stepwise drag one candidate card to a plausible legal pile | Card remains there and pile/hand/stock changes. Failed drop is not proof the game is broken; inspect legality. |
| Adjacent swap match-3 | Swappable grid and match-3 instruction | One adjacent swap using a deliberate drag; inspect board and score | Swap yields a match or visibly returns as invalid. Do not reuse connect-path logic. |
| Timed puzzle | Visible countdown shorter than tool round-trip overhead | One bounded closed-loop browser call with readable visual/DOM state and 3–5 s evidence frames | Actual score/board progression within round; stop at result, not a fixed blind script. |

Log pattern name, historical reference, current-match reason, attempted input and current evidence of success/failure. Three no-effect inputs and existing budgets still apply. Persist a new pattern only after demonstrated success with evidence; retain its scope and counterexamples. Store generic techniques in the skill, raw OS-input recordings only in the local campaign, never commit them to shared skill repos.

Match-3 / timed-round practicals (from a pilot where a 30 s round expired between calls): (1) calibrate the grid classifier in an earlier
call on the idle board, and start the timer only when the script is ready; a dry run costs a round. (2) Classify tiles with a
per-pixel hue histogram, not a mean colour per cell (mean colour gave 13 clusters for 5 animals); validate it against one
screenshot first. (3) Tell a running round from a game-over/score screen with a discrete HUD signal (the timer value
changing), not with the grid detector. (4) Restart and title buttons may ignore a correct 120 ms press right after a round
ends; an 8 s idle once worked, 12 s did not, so treat that control as flaky, not as "no effect x3". (5) Debugging the
classifier eats the 15-round budget; stop and record the gap instead of looping.

Recorded human timing (2026-10-04, two timed games on VIVERSE, mouse-only recording): buttons were tapped for 86-114 ms with no movement; match-3 swaps (Valentines Match3) were slow drags held 0.8-1.9 s (median about 1.3 s) over 143-285 px, about one per 3 s; castle aiming (Block Castle Breaker) was a pull of about 250 px held 1.2-2.9 s. An agent's fast drag of 10 moves at 10-15 ms (about 0.15 s, about 65 px) did not register in the match-3 game. Fruit Snake (keyboard, same day): the human steered only with ArrowLeft/ArrowRight (relative turns of the snake, so a left/right key, not up/down); 588 left/right key-down events in about 77 s including OS auto-repeat (first repeat about 450 ms after the first key-down, then every ~33 ms), single holds 50-1850 ms (median about 300-400 ms), menu buttons tapped 77-141 ms. An agent should send ArrowLeft/ArrowRight key-down then key-up with a 100-400 ms hold per turn and confirm a turn on the next frame, never W/A/S/D or up/down for steering.

Fruit Snake start and steering (human, second take): the game sits on a 'TAP TO PLAY' screen that only a click starts (bottom centre of the game area; keys do nothing there). Steering during play was mostly quick taps (76-110 ms, about every 0.2 s, zero movement) on the large on-screen left and right arrow icons in the bottom corners of the game area, with the arrow keys as a secondary option. An agent that only sends ArrowLeft/ArrowRight stays stuck on the start screen: click the start control first, then tap the on-screen left/right icons, and verify each turn on the next frame. Rule of thumb: when keys do nothing, look for large on-screen touch controls and tap those.

Dinehaven (build-your-restaurant, click game): the human placed furniture by pairs of clicks about 1 s apart, first selecting an item in the left catalogue list and then clicking a floor tile in the middle-right of the game area (every click 98-152 ms, zero movement), after one drag of a catalogue card onto the floor (held about 0.6 s over about 660 px). An agent that armed an item and tapped three floor tiles saw no green tiles and no placement: select the catalogue item with its own click first (a semantic DOM click worked for the start button when coordinate taps did not), wait a beat, then click a floor tile; if that fails try the drag. After placing, the game waits for the shop to earn money, so use a visible currency or customer change as the success signal.

Battle of the Lake (combat, same day): after Begin and Okay (taps 94-193 ms) the human sat idle about 35 s before acting (probably the WAVE 1 banner or a countdown, so an agent that sees a frozen WAVE 1 banner should wait about 40 s before declaring it stuck), then held the mouse about 4.7 s while moving 546 px (view or charge), then fought by tapping the mouse about every 0.25-0.3 s (80-130 ms, no movement, over the lower-middle area where enemies are) while holding WASD 1-2 s at a time (W about 1.1 s, A about 1.3 s, D about 1.2 s, S about 2 s, up to 5 s). Treat WASD plus rapid taps as the combat shape for similar arena games; success signals are enemy removal or the wave counter, not frame_diff.

Start from the human shape: hold at least about 1 s, move continuously with one pointer event every 30-50 ms, drag 150-280 px, tap buttons 90-120 ms, and expect a title button to need several taps. Re-check against the HUD (score, timer, turn counter), not frame_diff. Start the recorder only after the human says go, and run it for the whole round (a recorder started early expired before the human played).

When the core action, result and subsequent loop are already verified, stop rather than idle to pad time. Preserve actual verified seconds: below 30 s remains partial under the current outcome contract, with a note that core-mechanism coverage is complete. Whether to add a separate early-complete outcome is a future schema decision, not an implicit reinterpretation of played.
