# Site profile: <site name>

> Lives in the project that runs the playtests, at `docs/agents/playtest/<site>.md`. It may name internal
> hosts or indexes, so keep it out of public repos.

| Item | Value |
|---|---|
| Item | what one playtest target is; which field is `item_id` |
| URL | URL pattern for an item, e.g. `https://<host>/<item_id>` |
| Embed | origin the content runs in (iframe?), and whether it may be opened directly |
| Viewport | record actual viewport/DPR and content bounds each run |
| Declared metadata | where title, kind, tags, description, adult/public flags come from |
| items_dir | folder name for per-item data (default `items`) |

## Rules specific to this site

- **Paywall / entitlement**: how it looks → `excluded_paywall`
- **Unsupported device**: how it looks → `excluded_unsupported_device`
- **Mic, camera, permissions**: known prompts → `excluded_needs_permission` / `excluded_permission_prompt`
- **Shell UI to ignore**: pre-rolls, overlays, exit bars; keep them out of content evidence
- **Never play**: e.g. adult items
- **Known traps**: tags that mislead, unusual input bindings

## Declared metadata export (for `--meta`)

```bash
# one JSON line per item: item_id, declared_kind, public, adult
<command that exports declared metadata> > declared.jsonl
```

`declared_kind` → expected `observed_kind` map, if it differs from `observed_kind_mismatches.py`'s default.

## Review workflow

Model roles, who calibrates the initial sample, review sampling, device categories, report metadata fields.
