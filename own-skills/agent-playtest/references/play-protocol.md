# Play protocol (player)

## Per item

1. Read the item's declared metadata (title, tags, description) from the source named in the site profile. It hints
   at the controls. Do not trust it: tags and content types are often wrong.
2. Navigate, enable focus emulation when supported, and inspect the screen (round 1). Follow `evidence-review.md`: no delivered ad screenshots; at most one diagnostic loader image.
3. Loop: classify the screen state, act, take a screenshot. Each screenshot you look at, plus the action that follows,
   is one round. **Max 15 rounds.**
4. Stop when both the applicable time and coverage gates are met, or earlier when a budget, no-effect stop or exclusion applies. Record unmet gates; never extend a run merely to fill time or screenshot quotas.
5. Append the attempt to `playtest.json`. Write `description.json` only when real content was seen (`played` or
   `partial`).

## Screen states

| State | Recognize by | Action |
|---|---|---|
| `loading` | blank or dark frame, spinner, progress bar | wait 8–10 s and check again (counts as a round) |
| `preroll_ad` | "Ad", a countdown, an advertiser video over the frame | wait it out or press its own Skip. Never click the ad |
| `click_to_play` | "Click to play", a fullscreen prompt, a play overlay | press it |
| `main_menu` | title art plus Play / Start buttons | take the play path |
| `menu_select` | level, character or mode picker | pick the first unlocked option and confirm |
| `tutorial` | how-to text, a control diagram | read it, because it is description evidence, then continue |
| `modal` | reward, level complete, "continue" | press continue |
| `gameplay` / `exploring` | player-controlled content that responds to input | play (see below) |

Exclude surrounding ads and recommendation UI from saved content evidence. Read `evidence-review.md` for coverage targets and cropping rules.

## Input techniques (match a learned pattern first, then use fallbacks)

Before guessing an input, consult the pattern table in `human-demo.md`. Match current visible controls, not the room title/tag. Execute one bounded attempt, inspect the result, then continue only if confirmed. Never replay old absolute coordinates or assume shared artwork means shared mechanics.

1. **Press**: move → down → wait 120 ms → up. Canvas games often ignore a plain click.
2. **Slow press**: hold for about 400 ms.
3. **Plain click**: some placement modes accept only this.
4. **Drag / swipe**: down → 8–15 moves of 10–20 px, 10–15 ms apart → up. **Check whether drag is bound to something
   else** (camera rotation, for example). If the on-screen help says "drag = rotate view", select-then-target games
   need a press with **zero** movement between down and up.
5. **Keys**: press once inside the content first, to give it focus. Then hold movement keys (down … up). Tap steering
   keys for 300–450 ms.
6. **Learned from human demos.** See `human-demo.md`; the median values below come from real demos.
   - *Select, then target* (peg solitaire, chess-like): press the piece with a zero-movement press, about 100 ms, and
     **look for the highlighted legal targets** (for example green spots). Press one of those, not a guessed square. In 3D boards, press the **visible rim** of the highlight: its centre can sit behind a piece in front, and pressing there selects that piece instead.
   - *Connect a path* (link adjacent same-colour tiles): hold the button down and drag slowly through each tile, about
     25 px per tile. This is not a swap; try it when swapping does nothing.
   - *Drag and drop* (card games): hold about 400 ms and drag about 150 px onto the target pile, with moves 10–20 ms
     apart.
7. Real-time DOM games that move too fast for screenshot-by-screenshot play: a polling loop over read-only snapshots is
   allowed.

After 3 inputs with no effect on the same screen, stop. Record `excluded_unresponsive_input` with the techniques you
tried in `log.inputs_tried`. That record is what a human demo is later compared against.

## Timing: browser-call startup vs. timed content (read before any timed game)

- Each browser-tool call can take **20–30 s just to start** (ego-browser measured). Many casual games run **30 s rounds**.
  If you send one input per call, the round is usually over before the input arrives, and the content looks
  "unresponsive" when it is not. This was the real cause behind 2 of 4 "unresponsive" rooms in one campaign.
- **Rule:** for anything timed, run the whole round inside **one** call: (re)start → read the state → act → verify →
  repeat, with screenshots every 3–5 s, all in the same script.
  - Read the state without vision: sample pixel colours with 1×1 clip screenshots (`Page.captureScreenshot` with a
    1 px `clip`) at known cell positions. Classify them, and compute the move in the script.
  - After each move, re-read the state. If nothing changed, mark that move as tried and choose another, so the script
    does not loop on a misread state.
- Before the first press on a page, **take a screenshot and locate the target.** Guessed coordinates hit a pre-roll ad
  once.
- **Check that the screenshot size matches the viewport** (`innerWidth` / `innerHeight`). One adapter returned
  1920×934 screenshots for a 1908×922 viewport, with the content drawn about 11 % larger, so coordinates read from
  the image missed. Convert, or re-take the screenshot, before acting.
- Some content needs a hover before the press: move near the target, move onto it, wait about 100 ms, then press.
- **Escalate to a human** only after the timing fix and the demo-learned techniques have both failed (the budget is
  the same 15 rounds). Then use human-demo mode.

## Verification gates (both must pass for a segment to count)

1. **Visual**: the screenshot shows real content (gameplay, or exploring a scene). An animated menu is not gameplay.
2. **Frame diff**: `uv run --with pillow python scripts/frame_diff.py <segment shots...> [--box x0,y0,x1,y1]` reports no `STALL`
   (< 0.1 % of pixels changed means frozen, paused, or input not arriving).

Play in segments of 6–10 s with a screenshot every 1.5–3 s, all inside one browser call.

| Content | `played` when |
|---|---|
| game (goal, score, win/lose) | ≥ 30 s verified gameplay AND core action → observed result → subsequent gameplay loop evidenced |
| interactive scene / world / gallery | ≥ 30 s verified movement or interaction covering ≥ 2 distinct areas or objects |
| choice-based story | ≥ 3 real choices, each branching to new content |
| video-only | not playable: write the description from what the video shows; outcome `partial` |

Anything less is `partial`.

### Small-game duration and stopping

- Minimum: **30 s verified gameplay**. Normal acquisition target: **45–60 s**. End at 30 s if the core action, its visible result and a subsequent gameplay loop are already evidenced; do not wait mechanically for 60 s.
- Extend beyond 60 s only to answer a named missing observation (for example another successful match or the next turn). Log the gap before extending. **90 s verified gameplay is the cap**, not a new default.
- Time excludes loading, ads, menus, passive tutorial reading, agent deliberation and browser-tool startup. Preserve actual segment timestamps and verified intervals; do not substitute wall-clock session duration.
- Before stopping check: did the core input succeed, did it cause an observable change, and did subsequent play confirm the mechanism? A timer alone cannot satisfy these gates. No requirement to win, finish all levels or see an ending.
- The existing **15 decision-round budget**, exclusions and three-no-effect stop still apply and may end the attempt sooner. Do not reset a budget to reach 90 s. Dense frames inside a segment are not separate decision rounds.
- A complete short round under 30 s keeps its actual duration and evidence; under the current schema mark `partial` and note that a complete short round was observed. Do not replay blindly to pad time.
- These targets apply to games. Keep scene exploration, choice-story and video criteria above; video samples do not become full-film coverage at 45 or 90 s.
- Preserve all original verification frames. Report representatives remain 8–12 for games/scenes (target 10), selected for coverage rather than increasing linearly with duration. Timed games keep their 3–5 s capture cadence; do not replay to fill the representative quota.

## Exclusions (leave after 1 round, no retries)

`excluded_dead`, `excluded_private`, `excluded_login`, `excluded_gated_age`, `excluded_paywall`, `excluded_unsupported_device`
(for example VR-only), `excluded_needs_permission` (the content asks for camera or mic), `excluded_permission_prompt`
(a browser prompt appeared; never accept or dismiss it), `excluded_blank_frame` (still frozen after one 10 s wait),
`excluded_unresponsive*` (3 inputs with no effect), `excluded_adult_only`.

## observed_kind (every attempt)

One of `game` (goal, score or win/lose), `interactive_scene` (explorable, no goal), `gallery` (mainly viewing),
`video` (essentially a video), or `broken` (content never reached). Add 1–3 shots as `observed_kind_evidence`. Sites can
add more observed attributes (input devices, multiplayer, language). Keep them in the attempt, never in the declared
metadata.

## Writing the description

Describe only what you saw: mechanic, controls, goal, setting, art style, mood and pacing. For scenes, also the layout,
the objects, and what you can do. Every field cites screenshots in `evidence`. Put what you could not verify in
`unconfirmed_items`, not in the description. `semantic_description` has at least 200 words; each CJK character counts
as half a word. Write in English unless the profile says otherwise. Quote text you read on screen in its original
language.
