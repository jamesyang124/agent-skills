"""Offline review HTML. Read-only inputs; --spot selects a sample, --registry a master inventory."""
import argparse
import html
import json
import os
import shutil
from pathlib import Path

FIELDS = [('summary', 'Summary'), ('environment_style', 'Environment / style'),
          ('observable_interactions', 'Observable interactions'), ('gameplay_objectives', 'Gameplay objectives'),
          ('mood_pacing', 'Mood / pacing'), ('unconfirmed_items', 'Unconfirmed')]
ASSETS = Path(__file__).resolve().parent.parent / 'assets' / 'review'
esc = lambda v: html.escape(str(v), quote=True)


def read(path):
    return json.loads(path.read_text()) if path.exists() else {}


def show(value):
    if value is None or value == '':
        return '<span class="muted">Missing (not supplied)</span>'
    if isinstance(value, list):
        return '<ul class="evidence-list">' + ''.join('<li>' + show(v) + '</li>' for v in value) + '</ul>' if value else '<span class="muted">No values supplied</span>'
    if isinstance(value, dict):
        return '<dl>' + ''.join('<dt>' + esc(k) + '</dt><dd>' + show(v) + '</dd>' for k, v in value.items()) + '</dl>'
    value = {'尚未判讀（creator title 原文已提供）': 'Not reviewed (creator title is available)',
             '尚未判讀（creator description 原文已提供）': 'Not reviewed (creator description is available)',
             '資料缺口：快照未提供可確認的裝置宣告對應': 'Missing device declaration in this snapshot'}.get(str(value), str(value))
    if value.lower() == 'unknown':
        return '<span class="muted">Unconfirmed (insufficient evidence)</span>'
    return esc(value)


def tags(value):
    if not isinstance(value, list) or not value:
        return show(value)
    return '<ul class="tag-row">' + ''.join('<li>' + show(v) + '</li>' for v in value) + '</ul>'


def locale(value):
    if not isinstance(value, list):
        return show(value)
    return tags([(v.get('name') or v.get('code') or 'Missing language label') +
                 (' (' + str(v['code']) + ')' if v.get('code') and v.get('name') else '')
                 if isinstance(v, dict) else v for v in value])


def table(rows):
    return '<table class="table table-sm review-table">' + ''.join(
        '<tr><th scope="row">' + esc(k) + '</th><td>' +
        (tags(v) if k in ('tags', 'custom_tags') else locale(v) if k == 'DB declared language' else show(v)) + '</td></tr>'
        for k, v in rows) + '</table>'


def image_ref(item_dir, out_dir, ref):
    if not isinstance(ref, str):
        return None
    path = (item_dir / ref).resolve()
    if not path.is_relative_to(item_dir.resolve()) or not path.is_file() or path.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp'}:
        return None
    return html.escape(os.path.relpath(path, out_dir), quote=True)


def gallery(item_dir, out_dir, refs, keys=(), featured=()):
    result = []
    for ref in dict.fromkeys(refs):
        url = image_ref(item_dir, out_dir, ref)
        if not url:
            continue
        key = ref in keys
        enlarged = key or ref in featured
        result.append(f'<figure class="{"key-screen" if enlarged else "support-screen"}"><a href="{url}" target="_blank" rel="noopener"><img src="{url}" loading="lazy" decoding="async" alt="{esc(item_dir.name)}: {esc(Path(ref).name)}"></a><figcaption><strong>{"Key screen" if key else "Representative (display only)" if enlarged else "Evidence frame"}</strong><br>{esc(Path(ref).name)}</figcaption></figure>')
    return '<div class="shots">' + ''.join(result) + '</div>' if result else '<p class="muted">No screenshots supplied for this campaign.</p>'


def render_item(item_dir, out_dir, sample, camp, number):
    title = sample.get('title') or sample.get('item_id') or sample.get('hub_sid')
    iid = str(sample.get('item_id') or sample.get('hub_sid'))
    if sample.get('state') in ('legacy_reference_pending_remote', 'pending', 'not_started'):
        return f'<section class="card review-room" data-search="{esc(str(title).lower())}"><header class="room-head"><h2>{number}. {esc(title)}</h2></header><p>Pending current review. Legacy observations are reference-only.</p></section>'
    description, playtest, review = [read(item_dir / f) for f in ('description.json', 'playtest.json', 'review.json')]
    attempts = [a for a in playtest.get('attempts', []) if a.get('campaign') == camp]
    attempt = attempts[-1] if attempts else {}
    stale = bool(description.get('campaign') and description['campaign'] != camp)
    stale_review = bool(review.get('campaign') and review['campaign'] != camp)
    if stale_review:
        review = {}
    desc = {} if stale else description.get('content') or {}
    declared = review.get('declared') or {}
    db = declared.get('db_snapshot_fields') or declared.get('fields') or {k: v for k, v in declared.items() if k not in ('source', 'snapshot_date')}
    technical = {k: v for k, v in db.items() if k == 'id' or k.endswith('_id') or k in ('hub_sid', 'source', 'snapshot_date')}
    public = [(k, v) for k, v in db.items() if k not in technical]
    languages = review.get('languages') or {}
    public += [('DB declared language', languages.get('db_locale')),
               ('Creator title language', languages.get('title', 'Not reviewed')),
               ('Creator description language', languages.get('description', 'Not reviewed'))]
    frames = {f.get('ref'): f.get('class') for f in review.get('frames', []) if isinstance(f, dict)}
    raw = [s['file'] for s in attempt.get('shots', []) if isinstance(s, dict) and s.get('file')]
    # Only matching-attempt references are eligible; old review refs do not extend the cohort.
    refs = list(dict.fromkeys(raw))
    content = [v for v in refs if frames.get(v) not in ('ad', 'loader')]
    loaders = [v for v in refs if frames.get(v) == 'loader']
    keys = [v for v in review.get('key_screen_refs', []) if v in content and frames.get(v) == 'content'][:3]
    # Representatives do not automatically become semantic key screens.
    reps = [v for v in review.get('representative_refs', []) if v in content and frames.get(v) == 'content']
    featured = [] if keys or not reps else [reps[len(reps)//2]]
    front = keys or featured
    ordered = front + [v for v in content if v not in front]
    audit = attempt.get('audit') or read(item_dir / 'audit.json') or {}
    warning = 'Description campaign differs; its claims and citations are withheld.' if stale else 'No description supplied.' if not description else ''
    if stale_review:
        warning += ' Review campaign differs; review metadata is withheld.'
    obs = review.get('observed') or {}
    observed_rows = [(k, obs.get(k, attempt.get(k))) for k in ('observed_kind', 'outcome', 'verified_gameplay_total_s')]
    observed_rows += [('content_ui language', languages.get('content_ui')), ('subtitles', languages.get('subtitles')), ('heard_audio', languages.get('heard_audio'))]
    facets = '<div class="observed-grid">' + ''.join('<div class="observed-field"><h3>' + label + '</h3>' + show(desc.get(k)) + '</div>' for k, label in FIELDS) + '</div>'
    selection = '<p>Selection reason: ' + show(sample['selection_reason']) + '</p>' if sample.get('selection_reason') else ''
    provenance = {'campaign': camp, 'description_campaign': description.get('campaign'), 'source': declared.get('source'),
                  'snapshot_date': declared.get('snapshot_date'), 'technical_fields': technical, 'raw_language_associations': languages.get('db_locale'),
                  'description_source': description.get('source'), 'confidence': None if stale else description.get('confidence'),
                  'evidence': None if stale else description.get('evidence'), 'audit': audit, 'human_review': review.get('human_review'),
                  'key_screen_reasons': review.get('key_screen_reasons')}
    search = esc(json.dumps([iid, title, db, desc, languages], ensure_ascii=False).lower())
    return f'''<section class="card bg-base-100 review-room" data-search="{search}">
<header class="room-head"><div><h2 class="card-title">{number}. {esc(title)}</h2><small>{esc(iid)} / {esc(camp)}</small></div><span class="badge badge-outline">{esc(audit.get('verdict', 'Not audited'))}</span></header>
{('<p class="source-note">'+esc(warning)+'</p>') if warning else ''}{selection}
<div class="body-grid"><div class="declared-block"><h3 class="column-label">Declared</h3>{table(public)}</div>
<aside class="evidence-panel"><h3 class="column-label">Screenshots <small>{len(ordered)} frames</small></h3><p class="image-note">Original evidence. Unclassified historical frames may contain platform UI or ads; their presence is not a content classification. No automatic crop or new visual verdict.</p>{gallery(item_dir, out_dir, ordered, keys, featured)}<details><summary>Loading diagnostics ({len(loaders)})</summary>{gallery(item_dir, out_dir, loaders)}</details></aside>
<div class="observed-content"><div class="observed-block"><h3 class="column-label">Observed</h3>{table(observed_rows)}{facets}
<div class="review-field"><h3>Full semantic description</h3>{show(desc.get('semantic_description'))}</div>
<div class="review-field"><h3>Coverage / Evidence gaps</h3>{show(review.get('coverage'))}</div>
<div class="review-field"><h3>Devices / Timing</h3>{show(review.get('devices'))}{show(review.get('timing'))}</div>
<details><summary>Audit / Provenance / Evidence references</summary>{show(provenance)}</details>
<details><summary>Historical interaction log</summary>{show(attempt.get('log'))}</details></div>
<div class="assessment"><h3>Review</h3><p>Human review: {show(review.get('human_review', 'Pending; no verdict supplied'))}</p><h4>Profanity assessment</h4>{show(review.get('profanity', 'Not assessed; no structured result supplied.'))}<p>Weighted declared–observed agreement: Not calculated. No calibrated weights or threshold supplied.</p></div></div></div></section>'''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--base', required=True)
    ap.add_argument('--items-dir', default='items')
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument('--spot')
    group.add_argument('--registry')
    ap.add_argument('--campaign')
    ap.add_argument('--out', help='Optional HTML path; existing output replaced, input JSON untouched')
    a = ap.parse_args()
    manifest_path = Path(a.spot or a.registry).resolve()
    manifest = read(manifest_path)
    samples = manifest['sample'] if a.spot else manifest['records']
    path = Path(a.out).resolve() if a.out else manifest_path.parent / ('spot_check_review.html' if a.spot else 'room_info_review.html')
    path.parent.mkdir(parents=True, exist_ok=True)
    camp = a.campaign or manifest.get('campaign') or manifest_path.parent.name
    base = (Path(a.base) / a.items_dir).resolve()
    parts = []
    for n, sample in enumerate(samples, 1):
        iid = str(sample.get('item_id') or sample.get('hub_sid'))
        item = (base / iid).resolve()
        if not item.is_relative_to(base):
            raise ValueError(f'item ID escapes items directory: {iid}')
        parts.append(render_item(item, path.parent, sample, a.campaign or sample.get('source_campaign') or sample.get('campaign') or camp, n))
    # Dedicated namespaced output assets avoid overwriting unrelated report CSS.
    assets = path.parent / 'review-assets'
    shutil.copytree(ASSETS, assets, dirs_exist_ok=True)
    label = 'Spot-check review' if a.spot else 'Room evidence review'
    sampling = f'<p>Sample: {len(samples)} of {show(manifest.get("population_n"))}; seed: {show(manifest.get("seed"))}. Targeted cases are not an unbiased accuracy sample.</p>' if a.spot else '<p>Master inventory includes pending records. A returned review is not human acceptance.</p>'
    page = f'''<!doctype html><html lang="en" data-theme="review"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{label}</title><link rel="stylesheet" href="review-assets/review.css"></head><body><h1>{label}</h1>{sampling}<label for="query">Search rooms and evidence</label><input class="input input-bordered w-full" type="search" id="query" name="query" autocomplete="off" placeholder="Title, room ID or description…"><p id="count" role="status">{len(samples)} records</p>{''.join(parts)}<script>const q=document.querySelector('#query');q.addEventListener('input',()=>{{const terms=q.value.toLowerCase().trim().split(/\\s+/).filter(Boolean);let n=0;document.querySelectorAll('section').forEach(s=>{{s.hidden=!terms.every(t=>s.dataset.search.includes(t));if(!s.hidden)n++}});document.querySelector('#count').textContent=n+' records';}});</script></body></html>'''
    path.write_text(page)
    print(path)


if __name__ == '__main__':
    main()
