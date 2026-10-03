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
- When a browser permission prompt or hand-off appears, stop: the space moves to the user. Record
  `excluded_permission_prompt`.
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
