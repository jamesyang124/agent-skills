#!/usr/bin/env python3
"""Add Jira tickets to a service's Notes cell in a Confluence release-notes page.

The page is edited as raw storage XML through the Confluence REST API. The only change is
one inserted <li> per new ticket; everything else is kept byte for byte. Dry run by default.

usage:
  confluence_ticket_log.py --list [--limit 5]
  confluence_ticket_log.py --page-id ID --service api-service --ticket PROJ-1234 [--ticket ...] [--apply]
  confluence_ticket_log.py --create-month 2026-11 --service api-service --ticket PROJ-1234 [--apply]
  confluence_ticket_log.py --self-test

--list         the most recently modified release-notes pages (title contains --title-contains),
               and whether this month's "YYYY-MMXX " page exists yet.
--create-month use that month's "YYYY-MMXX " page; if it does not exist, copy the previous month's
               "YYYY-MMXX " page (same parent, content and attachments kept, only "MMXX" in the title
               changed; the sprint number is not touched).
Required: --space, --title-contains and --heading (for example ENG, "Release Notes", "Services"). Credentials come from ~/.env.mcp-atlassian
(CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN).

exit codes: 0 ok (or nothing to do), 1 error, 2 page/row/table not found.
"""
import argparse, base64, datetime, json, os, re, sys, urllib.parse, urllib.request
from xml.sax.saxutils import escape

TICKET_RE = re.compile(r"^[A-Z][A-Z0-9]+-\d+$")
COUNTED = ('ac:name="jira"', 'ac:name="code"', "<ac:image", "ri:attachment", "<a ", "<table", "<tr", "<h2")


# ---------- storage editing (pure, no network) ----------

def find_cell(storage, heading, service):
    """Return (start, end) of the Notes cell of `service`'s row in the table under `heading`."""
    h = re.search(r"<h[1-6]\b[^>]*>\s*" + re.escape(heading) + r"\s*</h[1-6]>", storage)
    if not h:
        raise LookupError(f'heading "{heading}" not found')
    t = re.compile(r"<table\b.*?</table>", re.S).search(storage, h.end())
    if not t:
        raise LookupError(f'no table after heading "{heading}"')
    table = t.group(0)
    # ponytail: flat regex parse; nested tables inside cells are not supported (the page has none).
    if table.count("<table") != 1:
        raise LookupError("nested table in release table; refusing to edit")
    headers = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<th\b.*?</th>", table, re.S)]
    col = next((i for i, x in enumerate(headers) if x.lower().startswith("notes")), len(headers) - 1)
    services = []
    for row in re.finditer(r"<tr\b.*?</tr>", table, re.S):
        cells = list(re.finditer(r"<td\b.*?</td>", row.group(0), re.S))
        if not cells:
            continue
        name = re.sub(r"<[^>]+>", "", cells[0].group(0)).strip()
        services.append(name)
        if name == service:
            c = cells[col]
            base = t.start() + row.start()
            return base + c.start(), base + c.end()
    raise LookupError(f'service "{service}" not in table; rows: {", ".join(services)}')


def jira_macro(server, server_id, key):
    return ('<ac:structured-macro ac:name="jira" ac:schema-version="1">'
            f'<ac:parameter ac:name="server">{escape(server)}</ac:parameter>'
            f'<ac:parameter ac:name="serverId">{escape(server_id)}</ac:parameter>'
            f'<ac:parameter ac:name="key">{key}</ac:parameter></ac:structured-macro>')


def has_ticket(cell, key):
    return (f'<ac:parameter ac:name="key">{key}</ac:parameter>' in cell
            or re.search(r"\b" + re.escape(key) + r"\b", re.sub(r"<[^>]+>", " ", cell)) is not None
            or f"/browse/{key}\"" in cell)


def insert_tickets(storage, heading, service, keys, server, server_id):
    """Return (new_storage, added_keys, skipped_keys, inserted_piece). Only inserts; never rewrites existing markup."""
    start, end = find_cell(storage, heading, service)
    cell = storage[start:end]
    added = [k for k in keys if not has_ticket(cell, k)]
    skipped = [k for k in keys if k not in added]
    if not added:
        return storage, added, skipped, ""
    items = "".join(f"<li><p>{jira_macro(server, server_id, k)}</p></li>" for k in added)
    last_ul = cell.rfind("</ul>")
    if last_ul != -1:  # append to the cell's last list
        pos, piece = start + last_ul, items
    else:  # cell has no list yet: add one before </td>
        pos, piece = end - len("</td>"), f"<ul>{items}</ul>"
    new = storage[:pos] + piece + storage[pos:]
    assert new[:pos] + new[pos + len(piece):] == storage  # nothing but the insertion changed
    return new, added, skipped, piece


def jira_server(storage):
    m = re.search(r'ac:name="jira".*?<ac:parameter ac:name="server">(.*?)</ac:parameter>'
                  r'<ac:parameter ac:name="serverId">(.*?)</ac:parameter>', storage, re.S)
    return (m.group(1), m.group(2)) if m else (None, None)


def counts(s):
    return {k: s.count(k) for k in COUNTED}


# ---------- Confluence REST ----------

class Confluence:
    def __init__(self, env_path="~/.env.mcp-atlassian"):
        env = {}
        for line in open(os.path.expanduser(env_path)):
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.rstrip("\n").split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
        self.base = env["CONFLUENCE_URL"].rstrip("/")
        if not self.base.endswith("/wiki"):
            self.base += "/wiki"
        token = f'{env["CONFLUENCE_USERNAME"]}:{env["CONFLUENCE_API_TOKEN"]}'
        self.auth = "Basic " + base64.b64encode(token.encode()).decode()

    def call(self, method, path, body=None):
        req = urllib.request.Request(
            self.base + path, method=method,
            data=None if body is None else json.dumps(body).encode(),
            headers={"Authorization": self.auth, "Accept": "application/json",
                     "Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            return json.load(r)

    def get(self, page_id):
        return self.call("GET", f"/rest/api/content/{page_id}?expand=body.storage,version,ancestors")

    def find_month_page(self, space, prefix):
        cql = f'space = "{space}" and type = page and title ~ "{prefix}"'
        res = self.call("GET", "/rest/api/content/search?limit=50&cql=" + urllib.parse.quote(cql))
        hits = [p for p in res["results"] if p["title"].startswith(prefix + " ")]
        if len(hits) > 1:
            raise LookupError(f'more than one page starts with "{prefix} ": '
                              + ", ".join(f'{p["id"]} {p["title"]}' for p in hits))
        return hits[0] if hits else None

    def recent(self, space, title_contains, limit):
        cql = (f'space = "{space}" and type = page and title ~ "{title_contains}" '
               'order by lastmodified desc')
        res = self.call("GET", f"/rest/api/content/search?limit={limit}&expand=version&cql="
                        + urllib.parse.quote(cql))
        return res["results"]

    def copy(self, src, title):
        parent = src["ancestors"][-1]["id"]
        return self.call("POST", f'/rest/api/content/{src["id"]}/copy', {
            "copyAttachments": True, "copyPermissions": True, "copyProperties": True,
            "copyLabels": True, "copyCustomContents": True,
            "destination": {"type": "parent_page", "value": parent}, "pageTitle": title})

    def put(self, page, storage, message):
        return self.call("PUT", f'/rest/api/content/{page["id"]}', {
            "id": page["id"], "type": "page", "title": page["title"],
            "version": {"number": page["version"]["number"] + 1, "minorEdit": True, "message": message},
            "body": {"storage": {"value": storage, "representation": "storage"}}})


def month_prefix(d):
    return f"{d.year}-{d.month:02d}XX"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--space")
    ap.add_argument("--title-contains")
    ap.add_argument("--heading")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--limit", type=int, default=5)
    ap.add_argument("--page-id")
    ap.add_argument("--create-month", help="YYYY-MM")
    ap.add_argument("--service")
    ap.add_argument("--ticket", action="append", default=[])
    ap.add_argument("--apply", action="store_true", help="write the change (default: dry run)")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.space and a.title_contains and a.heading):
        ap.error("--space, --title-contains and --heading are required")

    c = Confluence()
    if a.list:
        for p in c.recent(a.space, a.title_contains, a.limit):
            print(f'{p["id"]}\t{p["version"]["when"][:10]}\t{p["title"]}')
        prefix = month_prefix(datetime.date.today())
        hit = c.find_month_page(a.space, prefix)
        print(f'this month: {hit["id"]} "{hit["title"]}"' if hit else f'this month: no "{prefix} " page yet')
        return 0

    if not a.service or not a.ticket or bool(a.page_id) == bool(a.create_month):
        ap.error("--service, --ticket and exactly one of --page-id / --create-month are required")
    bad = [t for t in a.ticket if not TICKET_RE.match(t)]
    if bad:
        ap.error(f"not a Jira key: {', '.join(bad)}")

    if a.page_id:
        page = c.get(a.page_id)
    else:
        month = datetime.date.fromisoformat(a.create_month + "-01")
        prefix = month_prefix(month)
        hit = c.find_month_page(a.space, prefix)
        if hit:
            print(f'"{prefix} " page already exists; using it')
            page = c.get(hit["id"])
        else:
            prev = month_prefix((month - datetime.timedelta(days=1)).replace(day=1))
            src_hit = c.find_month_page(a.space, prev)
            if not src_hit:
                print(f'no "{prefix} " page and no "{prev} " page to copy in space {a.space}')
                return 2
            src = c.get(src_hit["id"])
            title = src["title"].replace(prev, prefix, 1)
            if not a.apply:
                print(f'would create "{title}" by copying {src["id"]} "{src["title"]}" '
                      f'(sprint number kept as-is; update it by hand)')
                print("dry run: preview below is computed on the source page")
                page = src
            else:
                created = c.copy(src, title)
                print(f'created {created["id"]} "{title}" from {src["id"]} — update the sprint number by hand')
                page = c.get(created["id"])

    orig = page["body"]["storage"]["value"]
    server, server_id = jira_server(orig)
    if not server_id:
        print("no existing Jira macro on the page to copy server/serverId from")
        return 1
    try:
        new, added, skipped, piece = insert_tickets(orig, a.heading, a.service, a.ticket, server, server_id)
    except LookupError as e:
        print(e)
        return 2
    print(f'page {page["id"]} v{page["version"]["number"]} "{page["title"]}"')
    print(f"service {a.service}: add {added or '-'}; already present {skipped or '-'}")
    if not added:
        return 0
    print("inserted storage:\n  " + piece)
    before, expect = counts(orig), counts(new)
    print("element counts before -> after: " + ", ".join(
        f"{k} {before[k]}->{expect[k]}" for k in COUNTED if before[k] != expect[k] or k == 'ac:name="jira"'))
    if not a.apply:
        print("dry run, nothing written")
        return 0
    c.put(page, new, f"Add {', '.join(added)} to {a.service}")
    after = c.get(page["id"])
    got = counts(after["body"]["storage"]["value"])
    if got != expect:
        print(f'WARNING: saved page differs from expected counts {expect} vs {got}; '
              f'restore v{page["version"]["number"]} from page history if it looks wrong')
        return 1
    print(f'written v{after["version"]["number"]}; counts verified')
    return 0


def self_test():
    head = '<h2 local-id="a">Services</h2>'
    row = lambda name, notes: f'<tr><td><p>{name}</p></td><td><p></p></td><td>{notes}</td></tr>'
    page = (head + '<table><tbody><tr><th><p>service</p></th><th><p>version</p></th>'
            '<th><p>Notes (Optional)</p></th></tr>'
            + row("api-service", '<ul><li><p>x</p></li></ul><ul><li><p>' + jira_macro("S", "ID", "PROJ-1") + '</p></li></ul>')
            + row("web-app", '<p local-id="e"></p>')
            + '</tbody></table><h2>Configuration Notes</h2><p>PROJ-9</p>')
    new, added, skipped, _ = insert_tickets(page, "Services", "api-service", ["PROJ-1", "PROJ-2"], "S", "ID")
    assert added == ["PROJ-2"] and skipped == ["PROJ-1"], (added, skipped)
    assert new.count('ac:name="jira"') == 2 and new.index("PROJ-2") < new.index("web-app")
    assert new.rindex("PROJ-2") < new.index("</td></tr>", new.index("api-service"))
    new2, added2, _, _ = insert_tickets(page, "Services", "web-app", ["PROJ-9"], "S", "ID")
    assert added2 == ["PROJ-9"]  # a key elsewhere on the page does not count as present in this cell
    assert '<p local-id="e"></p><ul><li><p>' in new2 and new2.endswith("<p>PROJ-9</p>")
    assert insert_tickets(new, "Services", "api-service", ["PROJ-2"], "S", "ID")[0] == new
    try:
        insert_tickets(page, "Services", "nope", ["PROJ-3"], "S", "ID")
        raise AssertionError("missing row not reported")
    except LookupError as e:
        assert "api-service" in str(e)
    print("self-test ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
