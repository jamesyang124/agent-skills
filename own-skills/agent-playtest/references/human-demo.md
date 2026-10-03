# Human-demo mode

Use this mode when an agent recorded `excluded_unresponsive*`, or when its description looks wrong. A person plays the
item while their local mouse and keyboard are recorded. The agent then compares the recording with its own logged
attempt.

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
- If a recording captured text anyway, delete the key events from the file straight away and say so.
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

When the core action, result and subsequent loop are already verified, stop rather than idle to pad time. Preserve actual verified seconds: below 30 s remains partial under the current outcome contract, with a note that core-mechanism coverage is complete. Whether to add a separate early-complete outcome is a future schema decision, not an implicit reinterpretation of played.
