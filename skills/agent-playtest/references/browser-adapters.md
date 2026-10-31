# Browser adapters

The player protocol needs these capabilities. Any browser tool that provides them works.

| # | Capability | Why |
|---|---|---|
| C1 | Navigate to a URL and wait for load | open each item |
| C2 | Viewport screenshot to a file, at a known CSS size | evidence and frame diff |
| C3 | Mouse: move, down, up (separately), click, wheel, at CSS coordinates | canvas games often ignore a synthetic `click` and need press-and-hold |
| C4 | Keyboard: key down / up (held keys), press, type | movement and steering |
| C5 | Focus emulation, or a dedicated window per player | background tabs stall when several players share one browser |
| C6 | Read-only DOM snapshot | DOM games, menus, banners |
| C7 | Detect and refuse permission prompts and dialogs | never grant device permissions |
| C8 | One persistent session per player | reuse across items, close once |

Optional: C9, CDP access for diagnostics.

## ego-browser

- C1 `page.goto(url)`; C2 `page.screenshot({path})`; C3 `page.mouse.move/down/up/click/wheel`; C4 `page.keyboard.down/up/press`.
- C5 `page.cdp("Emulation.setFocusEmulationEnabled", {enabled: true})` after every `goto`.
- C6 `page.snapshot()`. C8 follow the installed ego-browser skill: one orchestrator-owned TaskSpace per goal; allocate worker pages within it when supported. Do not create one TaskSpace per worker. Finish owned resources once.
- When a browser permission prompt or hand-off appears, stop: the space moves to the user (`listTaskSpaces()` shows
  `ownership: "agentDelegatedToUser"`; only the user can release it, never claim it). Record
  `excluded_permission_prompt` and do not retry. The prompt stalls every later item that shares the space, so run rooms
  known or likely to be permission-gated (webcam/mic games, hand-tracking) in a separate final pass, and never promise that
  the profile blocks them: verify before the campaign, and if it cannot be done without user action, just skip those rooms.
- **Pre-deny device permissions: partial, do not rely on it (2 trials on Ego Lite, Chrome 152).** `page.cdp("Browser.setPermission",
  {permission: {name}, setting: "denied", origin: "https://<site host>"})` for `name` in `microphone`, `camera`,
  `geolocation` is accepted (use `page.cdp`, not `task.cdp`; `audioCapture` is rejected; never `grant`). Results: one load
  of a mic-gated room showed no prompt, a second load of the same room still raised the microphone prompt during the
  pre-roll and handed the space to the user. The request most likely comes from the game's cross-origin or opaque (`null`)
  iframe, whose origin cannot be set. Treat it as a best-effort extra, never as the reason a gated room is played.
- **A hand-off ends the script at once.** On ego-browser the CLI throws the moment the prompt appears, so the 10-second rule
  below cannot be applied from inside the run, and the space then belongs to the user. Therefore do not open a room that is
  known or likely to be permission-gated (webcam/mic/hand-tracking, or one that already handed off in an earlier
  campaign): put it in the plan's `skipped` list with `needs <device> permission` as the reason and keep it out of the live
  queue. If an unknown room hands off, stop the whole run, report it, and do not retry or open another space.
- `taskSpace(n)` is the normal way to use an agent-owned space; `takeOverTaskSpace(n)` is only for resuming after a hand-off.
- Synthetic presses can be ignored while hover still registers (seen on two title-screen buttons that worked in an earlier
  campaign). Treat that as an adapter/click-delivery question, not a content verdict, and record it as a blocker.
  `frame_diff` "moving" on a self-animating title screen does not prove input arrived; always compare with a no-input
  control pair over the same box. On a self-animating title screen the control also moves (about 49 % changed seen), so use a
  discrete state change (a HUD or timer value, a new screen, a score) as the success signal instead.
- **Input that worked where `page.mouse.down/up` taps were ignored (one game, Fable, 2026-10-04).** In Dinehaven, plain `mouse.down/up` taps and CDP touch taps placed nothing, while raw CDP mouse events did: `Input.dispatchMouseEvent` `mouseMoved` approach steps, a 300 ms hover on the target, then `mousePressed` with `button:"left"`, `buttons:1`, `clickCount:1`, held 110-130 ms, then `mouseReleased` with `buttons:0`. The game also required the pointer to hover an actual grid tile first (the tile turned green); only that tile accepted the click. Semantic text clicks worked for every DOM button. So when a canvas or game ignores simple taps, try this raw-CDP mouse sequence with the `buttons` bitmask and a prior hover before concluding the room is unresponsive. One game only: confirm on others before treating it as the general cause.
- **Second game, same pattern (Battle of the Lake, Fable, 2026-10-04).** Begin: a semantic `page.click('canvas')`. Okay and Restart: `mouse.move` hover 300 ms, then `mouse.down` 120 ms and `mouse.up`; Okay registered on the first try, Restart ignored a press about 1 s after the round ended and worked on the next press 20 s later (treat Restart as flaky, wait and retry). Fight: `keyboard.down/up` WASD 1.5 s holds with an overlapping second key plus mouse taps of 100 ms every ~270 ms over the play area; no separate focus click was needed after Okay. A 6 s no-input control at the WAVE 1 banner was byte-identical, and the game became live as soon as play input started (no 45 s wait was needed). Both successful retries share the same recipe: hover the exact target first, then press 100-130 ms, retry after a pause.
- **Gaps:**
  - `task.cdp` cannot route commands into a cross-origin iframe session, so you cannot run in-page recorders inside
    embedded games.
  - Killing the CLI does not stop a script that is already running.
  - Each `ego-browser nodejs` call takes about 20–30 s to start. Do timed content inside one call (see
    `play-protocol.md`, Timing).
  - Check that the screenshot size matches the viewport; a mismatched size (about 11 % scaled) was seen once.

## Playwright (library: Node or Python)

- C1 `page.goto(url, wait_until="load")`; C2 `page.screenshot(path=...)`.
- C3 `page.mouse.move/down/up/click/wheel`; C4 `page.keyboard.down/up/press`.
- C5: give each player its own `browser.new_context()` and page. Headed Chromium tabs in separate contexts are not
  throttled the way background tabs in one window are. If you still see throttling, use
  `context.new_cdp_session(page)` → `Emulation.setFocusEmulationEnabled`.
- C6 `page.accessibility.snapshot()` or locators (read only).
- C7: create the context with `permissions=[]` and handle `page.on("dialog")` yourself.
- Embedded content: `page.frame_locator(...)` for same-process frames. For cross-origin iframes,
  `page.frames` exposes them in Chromium, so an in-frame recorder can be injected for **human demos only**, never into
  content under test during an agent run.
- Headless rendering of WebGL may differ from headed. Prefer headed for 3D content.

## Playwright MCP / Chrome DevTools MCP

- They map to `browser_navigate`, `browser_take_screenshot`, `browser_mouse_*` / `browser_click`, `browser_press_key`
  and `browser_snapshot` (names vary by server).
- Check C3: some servers only expose element clicks, with no raw down/up at coordinates. Without C3, canvas games will
  mostly fail. Record that in `blockers.md` and use another adapter.
- One MCP browser is usually shared by every caller, so with parallel players prefer one MCP server per player, or
  serial play.

## Adapter self-test (run once per adapter before a campaign)

1. Open a simple canvas page and press at the centre with a 120 ms hold. The screenshot should change.
2. Hold a key for 500 ms in a keyboard-driven page. Movement should be visible in frame diff.
3. Open 2 players at once. The background one must still load, which confirms C5.
4. Trigger a permission request. The adapter must not grant it.

Record the results in the campaign entry (`adapter`, `adapter_selftest`).
