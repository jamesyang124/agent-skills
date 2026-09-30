#!/usr/bin/env python3
"""md2html.py — render a findings/report Markdown file to a single self-contained HTML page.

    python3 md2html.py findings.md > findings.html
    python3 md2html.py findings.md -o findings.html --title "CONNECT-6031 findings"

No third-party dependencies (the `markdown` package is usually not installed and pandoc is not
always available). Supports what perf reports use: headings, paragraphs, bullet/numbered lists,
fenced code blocks, inline code, bold, links, pipe tables, blockquotes, horizontal rules.
Everything else is passed through as escaped text, never dropped.
"""
import argparse
import html
import re
import sys

CSS = """
:root{--bg:#fff;--fg:#1f2328;--muted:#57606a;--line:#d0d7de;--code:#f6f8fa;--accent:#0969da}
@media (prefers-color-scheme:dark){:root{--bg:#0d1117;--fg:#c9d1d9;--muted:#8b949e;--line:#30363d;--code:#161b22;--accent:#58a6ff}}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang TC","Microsoft JhengHei",sans-serif}
main{max-width:1100px;margin:0 auto;padding:24px 16px 64px}
h1{font-size:1.7em;border-bottom:1px solid var(--line);padding-bottom:.3em}
h2{font-size:1.35em;margin-top:1.8em;border-bottom:1px solid var(--line);padding-bottom:.2em}
h3{font-size:1.1em;margin-top:1.4em}
code{background:var(--code);padding:.1em .35em;border-radius:4px;font-size:.92em}
pre{background:var(--code);padding:12px;border-radius:6px;overflow-x:auto;line-height:1.4}
pre code{background:none;padding:0}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:.93em;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:6px 9px;text-align:left;vertical-align:top}
th{background:var(--code)}
blockquote{border-left:4px solid var(--line);margin:0;padding:0 14px;color:var(--muted)}
a{color:var(--accent)}
hr{border:0;border-top:1px solid var(--line);margin:24px 0}
.meta{color:var(--muted);font-size:.85em}
"""

INLINE_CODE = re.compile(r"`([^`]+)`")
BOLD = re.compile(r"\*\*(.+?)\*\*")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def inline(text: str) -> str:
    # protect code spans first so bold/link regexes never touch them
    parts = []
    last = 0
    for m in INLINE_CODE.finditer(text):
        parts.append(_inline_no_code(text[last:m.start()]))
        parts.append(f"<code>{html.escape(m.group(1))}</code>")
        last = m.end()
    parts.append(_inline_no_code(text[last:]))
    return "".join(parts)


def _inline_no_code(text: str) -> str:
    text = html.escape(text, quote=False)
    text = BOLD.sub(r"<strong>\1</strong>", text)
    text = LINK.sub(lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>', text)
    return text


def is_table_sep(line: str) -> bool:
    return bool(re.match(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$", line))


def split_row(line: str):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def render(md: str) -> str:
    lines = md.splitlines()
    out = []
    i = 0
    list_stack = []  # 'ul' / 'ol'

    def close_lists():
        while list_stack:
            out.append(f"</{list_stack.pop()}>")

    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            close_lists()
            lang = line[3:].strip()
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            cls = f' class="language-{html.escape(lang)}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(buf))}</code></pre>")
            i += 1
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            close_lists()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2).strip())}</h{level}>")
            i += 1
            continue

        if re.match(r"^\s*(-{3,}|\*{3,})\s*$", line):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        if "|" in line and i + 1 < len(lines) and is_table_sep(lines[i + 1]):
            close_lists()
            header = split_row(line)
            i += 2
            rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(split_row(lines[i]))
                i += 1
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(h)}</th>" for h in header) + "</tr></thead><tbody>")
            for r in rows:
                r = r + [""] * (len(header) - len(r))
                out.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r[: len(header)]) + "</tr>")
            out.append("</tbody></table>")
            continue

        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", line)
        if m:
            kind = "ol" if m.group(2)[0].isdigit() else "ul"
            if not list_stack or list_stack[-1] != kind:
                close_lists()
                list_stack.append(kind)
                out.append(f"<{kind}>")
            item = m.group(3)
            # continuation lines (indented) belong to this item
            j = i + 1
            while j < len(lines) and lines[j].startswith("  ") and not re.match(r"^\s*([-*]|\d+\.)\s+", lines[j]):
                item += " " + lines[j].strip()
                j += 1
            out.append(f"<li>{inline(item)}</li>")
            i = j
            continue

        if line.startswith(">"):
            close_lists()
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i][1:].strip())
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(buf))}</p></blockquote>")
            continue

        if not line.strip():
            close_lists()
            i += 1
            continue

        # paragraph: gather until blank / block start
        close_lists()
        buf = [line.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|```|\s*([-*]|\d+\.)\s|>|\s*-{3,}\s*$)", lines[i]) and not ("|" in lines[i] and i + 1 < len(lines) and is_table_sep(lines[i + 1])):
            buf.append(lines[i].strip())
            i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")

    close_lists()
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source")
    ap.add_argument("-o", "--output")
    ap.add_argument("--title")
    args = ap.parse_args()
    with open(args.source, encoding="utf-8") as f:
        md = f.read()
    title = args.title
    if not title:
        m = re.search(r"^#\s+(.+)$", md, re.M)
        title = m.group(1).strip() if m else args.source
    body = render(md)
    page = (
        "<!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body><main>"
        f"{body}<hr><p class=\"meta\">Rendered from <code>{html.escape(args.source)}</code> by perf-ticket-harness/md2html.py</p>"
        "</main></body></html>\n"
    )
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(page)
    else:
        sys.stdout.write(page)
    return 0


if __name__ == "__main__":
    sys.exit(main())
