# Browser adapters

Needed capabilities: navigate+wait; read page text/DOM; click by selector or by **coordinates** (Power Automate's import side panels live in a
cross-origin iframe); set a file on an upload control; download a file; run `fetch` with the page's cookies; take a screenshot (only if asked).

| Capability | ego-browser | Playwright | Chrome DevTools MCP |
|---|---|---|---|
| navigate | `page.goto(url)` (+ `waitForLoadState`) | `page.goto(url)` | `navigate_page` |
| read text | `page.evaluate(()=>document.body.innerText)` | same | `evaluate_script` |
| click | `page.click(sel)` / `page.mouse.click(x,y)` | `page.click` / `page.mouse.click(x,y)` | `click` (uid) |
| upload file | `page.setInputFiles('input[type=file]', path)` | `page.setInputFiles(...)` | `upload_file` |
| download | `Page.setDownloadBehavior` via `page.cdp` then click Download; `waitForEvent('download')` never fires | `page.waitForEvent('download')` + `download.saveAs` | download dir via CDP |
| cookie fetch | `page.fetch(url,{credentials:'include'})` (returns `{status, body}`) | `page.evaluate(fetch…)` | `evaluate_script(fetch…)` |
| scroll a post into view | `el.scrollIntoView()` in `evaluate` | same | same |

## ego-browser specifics (hard-won)
- Each `ego-browser nodejs` call is a new process: variables do not persist; `document` exists only inside `page.evaluate`; env vars do not reach the script, hard-code values.
- Resume the same task space (`taskSpace(id)` / `takeOverTaskSpace(id)`); never create another to recover. A browser permission prompt (e.g. notifications) hands the space to the user: stop and ask them to dismiss it.
- Downloads: `await page.cdp('Page.setDownloadBehavior',{behavior:'allow',downloadPath:DIR})` before clicking the Download button.
- Import side panels (Flow row "Update", connection row "Select during import") sit in an iframe: take a screenshot once, then use `page.mouse.click(x,y)`; DOM selectors do not reach them. Coordinates observed at a 1908×922 viewport: open flow setup (1236,571), pick target flow (1550,390), Save (1697,886), open connection setup (1259,721), pick connection (1537,433).
- `page.fetch` obeys CORS: be on a same-origin page; a tab can go stale (CDP timeouts) → open a fresh page.
- Do not capture bearer tokens from the app's network calls; use REST with the cookie session or a PAT.

## Playwright specifics
- Use a persistent context (`launchPersistentContext`) with the user's profile so SSO sessions exist; headed mode.
- For the import panels use `page.frameLocator('iframe').…` instead of coordinates if the frame is reachable.

## Human-in-the-loop points (any browser)
Import click may be blocked for agents by a safety classifier; turning the flow On after import is easy to forget; Teams permission prompts; first-time SSO. Stage everything, then ask for exactly one human action.
