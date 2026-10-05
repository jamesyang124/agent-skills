# Intake recipes (ego-browser first)

Load the `ego-browser` skill first and follow its rules (one task space per goal, refs/selectors, `finish()` at the end). Everything below was exercised on real pages. Scripts run in Node; browser code goes inside `page.evaluate()`.

## Provenance header (top of every source.txt)

```
SOURCE: <author/channel> — "<title>"
URL: <url>
FETCHED: <YYYY-MM-DD>
METHOD: <ego-browser transcript panel | youtube-transcript-api (auto|manual captions) | ego-browser DOM extract | ...>
LANGUAGE: <en | zh-Hans | ...>
GAPS: <what is NOT captured: on-screen diagrams, paywalled sections, images, quiz answers hidden, ...>
FORMAT: <how the body is organized, e.g. "[m:ss] paragraph, ~45s per block">
-----
<body>
```

## YouTube

Primary (works with no API and no extra install):
```js
const task = await taskSpace("intake <topic>");
const page = task.page("p1");
await page.goto(url); await page.waitForLoadState(); await page.waitForTimeout(3000);
await page.evaluate(() => document.querySelector("#expand, tp-yt-paper-button#expand")?.click());
await page.evaluate(() => [...document.querySelectorAll("button")]
  .find(b => /show transcript/i.test(b.getAttribute("aria-label") || b.innerText))?.click());
await page.waitForTimeout(2500);
const segs = await page.evaluate(() =>
  [...document.querySelectorAll("ytd-transcript-segment-renderer")].map(s => s.innerText.replace(/\n+/g, " ").trim()));
```
Each segment starts with `m:ss`. Group into ~45 s paragraphs with a `[m:ss]` prefix so notes can cite timestamps.

Shortcut (faster, may be rate-limited): `youtube-transcript-api` in a throwaway venv (`api.list(id)`, prefer the manual (non-generated) track over auto-generated). Note which track was used in METHOD. Title/channel via `https://www.youtube.com/oembed?url=<url>&format=json`.

Caveats to put in GAPS: transcript only, on-screen diagrams/tables not captured; auto-captions mis-hear technical words (e.g. "idempotency" heard as "item potency"). A `&t=` in the URL is only a start offset; the whole video is the source.

## Course lessons / logged-in pages (quizzes, collapsed answers)

ego-browser uses the user's logged-in session, so paywalled pages work. After `goto`, scroll to trigger lazy content (loop `mouse.wheel`), then reveal answers by clicking each leaf element whose text is "Show Answer" - one at a time, because the DOM changes after each click:
```js
for (let i = 0; i < 8; i++) {
  const n = await page.evaluate(() => {
    const e = [...document.querySelectorAll("*")]
      .filter(e => e.children.length === 0 && /^show answer$/i.test(e.textContent.trim()))[0];
    if (e) { e.click(); return 1 } return 0; });
  if (!n) break; await page.waitForTimeout(600);
}
const text = await page.evaluate(() => (document.querySelector("main") || document.body).innerText);
```
Quizzes marked "AI Powered" have no stored answer: write your own and label it as yours.
To find sibling lesson URLs, collect sidebar `<a>` hrefs with `page.evaluate`.

## Diagrams (SVG/images)

```js
const imgs = await page.evaluate(() => [...(document.querySelector("main") || document.body)
  .querySelectorAll("img")].filter(i => i.alt && i.src.startsWith("http")).map(i => ({ alt: i.alt, src: i.src })));
await page.fetch(imgs[0].src, { saveAs: "/abs/path/img0.svg" });   // many course diagrams are SVG
```
Read SVG labels with a regex over `>text<` (Python `re.findall(r">([^<>]{2,120})<", svg)`), de-duplicate. Raster images: screenshot or open and look at them. If a diagram cannot be read, say so in GAPS.

## Articles / docs / blogs
`(document.querySelector("main, article") || document.body).innerText`; scroll first for lazy content; keep headings. Save code blocks verbatim.

## Shared AI chats (claude.ai, ChatGPT)
`goto` the share/chat link, scroll up repeatedly to load earlier messages, read `main` innerText. Side panels (outputs/artifacts) may be hidden and not clickable: say so in GAPS and build from the visible text. Prefer a primary source (the video, the article) over a chat's summary of it; if only the summary is available, say the notes derive from a summary.

## PDFs and slides
Open in the browser viewer and extract text, or `page.fetch(pdfUrl, { saveAs })` and read the file. Scanned PDFs need OCR/screenshots; note the gap.

## When blocked
Login, captcha, permission prompt, or a chooser: `await task.handOff()`, tell the user what to do in the browser, end the round, resume the same space (`takeOverTaskSpace(id)`). Never retry around it or open a second space.

## Course chapters: find the lessons, never trust a saved number
Chapter numbers change when a course is restructured, and a progress file or a user's memory of the numbering can be stale. List a chapter's lessons from the live sidebar, matching by chapter name:
```js
const lines = (await page.snapshot({ scope: "full_page" })).split("\n");
let on = false;
for (const l of lines) {
  const m = l.match(/chapter (\d+):\s*(.*?)"?$/i);
  if (m) { on = m[1] === "43"; continue; }          // the chapter you were asked for
  if (on) { const u = l.match(/url=(\S+?)[\],]/); if (u) console.log(u[1]); }
}
```
When the user's number and your mapping disagree, re-read the live page before writing anything.

## Interactive pages (mock interviews, AI-graded sessions)
A page with a "Start Interview" or similar button is a live session, not lesson text: starting it can spend one of the user's limited attempts. Do not start it. Record it in the notes as a gap (format, limits, focus stated on the landing page) and tell the user.
Such pages may have no `<main>`; `document.body.innerText` then returns the whole sidebar. Take the part after the last sidebar entry, or use the landing-page text only.

## Long fetch loops
Scrolling, revealing answers and downloading SVGs for several lessons can exceed the shell's 2-minute limit and get moved to the background. Wrap risky navigations in `timeout 100 ...`, print one line per lesson as it finishes, write each lesson's files before moving on, and re-run only the missing lesson in the same task space.
