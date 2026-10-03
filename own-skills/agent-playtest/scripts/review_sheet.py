"""Render a local spot-check page from descriptions and optional per-item review.json.

python3 review_sheet.py --base WS [--items-dir items] --spot archive/<campaign>/spot_check.json [--campaign ID]
"""
import argparse
import html
import json
import os
from pathlib import Path


FIELDS = ("summary", "environment_style", "observable_interactions", "gameplay_objectives",
          "mood_pacing", "unconfirmed_items", "semantic_description")
LANGUAGES = ("db_locale", "title", "description", "content_ui", "subtitles", "heard_audio", "generated_text")


def show(value):
    if value is None:
        return "unknown"
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    return html.escape(str(value)) if value != "" else "empty"


def row(label, value):
    return f"<tr><th>{html.escape(label)}</th><td>{show(value)}</td></tr>"


def image_ref(item_dir, out_dir, ref):
    """Only local files below this item may become image links."""
    if not isinstance(ref, str):
        return None
    path = (item_dir / ref).resolve()
    if not path.is_relative_to(item_dir.resolve()) or not path.is_file() or path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
        return None
    return html.escape(os.path.relpath(path, out_dir), quote=True)


def gallery(item_dir, out_dir, refs):
    links = []
    for ref in dict.fromkeys(refs):
        url = image_ref(item_dir, out_dir, ref)
        if url:
            links.append(f'<a href="{url}" target="_blank" rel="noopener"><img src="{url}" loading="lazy"><span>{html.escape(Path(ref).name)}</span></a>')
    return '<div class="shots">' + "".join(links) + "</div>" if links else "<p>unknown</p>"


def render_item(item_dir, out_dir, sample, camp, number):
    description = json.loads((item_dir / "description.json").read_text()) if (item_dir / "description.json").exists() else {}
    stale = bool(description.get("campaign") and description["campaign"] != camp)
    desc = description.get("content") or {} if not stale else {}
    playtest = json.loads((item_dir / "playtest.json").read_text()) if (item_dir / "playtest.json").exists() else {}
    review = json.loads((item_dir / "review.json").read_text()) if (item_dir / "review.json").exists() else {}
    attempts = [a for a in playtest.get("attempts", []) if a.get("campaign") == camp]
    attempt = attempts[-1] if attempts else {}
    declared = review.get("declared") or {}
    observed = review.get("observed") or {}
    frames = {f.get("ref"): f.get("class") for f in review.get("frames", []) if isinstance(f, dict)}
    raw = [s.get("file") for s in attempt.get("shots", []) if isinstance(s, dict) and s.get("file")]
    reps = [r for r in review.get("representative_refs", []) if r in raw and frames.get(r) == "content"]
    content_raw = [r for r in raw if frames.get(r) not in ("ad", "loader")]
    loaders = [r for r in raw if frames.get(r) == "loader"]
    title = sample.get("title") or playtest.get("title") or sample.get("item_id") or sample.get("hub_sid")
    audit = attempt.get("audit") or {}
    coverage = review.get("coverage") or {}
    languages = review.get("languages") or {}
    devices = review.get("devices") or {}
    timing = review.get("timing") or {}
    declared_rows = "".join(row(k, declared.get(k)) for k in ("title", "kind", "description", "tags", "view_count"))
    observed_rows = "".join(row(k, observed.get(k, attempt.get(k))) for k in ("observed_kind", "outcome", "verified_gameplay_total_s"))
    observed_rows += "".join(row(k, desc.get(k)) for k in FIELDS)
    observed_rows += row("confidence", description.get("confidence") if not stale else None)
    observed_rows += row("evidence", description.get("evidence") if not stale else None)
    language_rows = "".join(row(k, languages.get(k)) for k in LANGUAGES)
    device_rows = "".join(row(k, devices.get(k)) for k in ("declared", "tested", "unknown"))
    coverage_rows = "".join(row(k, coverage.get(k)) for k in ("reached", "missing", "note"))
    timing_rows = "".join(row(k, timing.get(k)) for k in ("navigation", "content_start", "first_useful_content", "first_interaction", "loader_intervals", "ad_intervals", "method", "environment"))
    provenance = row("source", declared.get("source")) + row("snapshot date", declared.get("snapshot_date"))
    provenance += row("campaign", camp) + row("description campaign", description.get("campaign"))
    provenance += row("description source", description.get("source", review.get("description_source", "description.json")) if not stale else None)
    provenance += row("audit", audit.get("verdict")) + row("audit by", audit.get("by")) + row("audit note", audit.get("note"))
    provenance += row("human review", review.get("human_review"))
    warning = ("Description campaign differs from selected campaign; description claims and citations are withheld."
               if stale else "Description missing; observed prose and citations are unknown." if not description else "")
    return (f'<section><h2>{number}. {show(title)} <small>{show(sample.get("item_id") or sample.get("hub_sid"))}</small></h2>'
            f'{f"<p class=warning>{warning}</p>" if warning else ""}'
            f'<div class="grid"><div><h3>Declared</h3><table>{declared_rows}</table></div>'
            f'<div><h3>Observed</h3><table>{observed_rows}</table></div></div>'
            f'<div class="grid"><div><h3>Language evidence</h3><table>{language_rows}</table><h3>Devices</h3><table>{device_rows}</table>'
            f'<h3>Coverage</h3><table>{coverage_rows}</table></div>'
            f'<div><h3>Timing</h3><table>{timing_rows}</table><h3>Provenance and review</h3><table>{provenance}</table></div></div>'
            f'<h3>Representative content</h3>{gallery(item_dir, out_dir, reps)}'
            f'<details><summary>Raw frames ({len(content_raw)}; inspect originals)</summary>{gallery(item_dir, out_dir, content_raw)}</details>'
            f'<details><summary>Loader diagnostic ({len(loaders)})</summary>{gallery(item_dir, out_dir, loaders)}</details>'
            f'<p class="v">Verdict: correct / minor / wrong / hallucinated — note:</p></section>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--items-dir", default="items")
    ap.add_argument("--spot", required=True)
    ap.add_argument("--campaign")
    a = ap.parse_args()
    spot = json.loads(Path(a.spot).read_text())
    out_dir = Path(a.spot).resolve().parent
    camp = a.campaign or out_dir.name
    base = Path(a.base).resolve() / a.items_dir
    parts = []
    for n, sample in enumerate(spot["sample"], 1):
        iid = str(sample.get("item_id") or sample.get("hub_sid"))
        item_dir = (base / iid).resolve()
        if not item_dir.is_relative_to(base.resolve()):
            raise ValueError(f"item ID escapes items directory: {iid}")
        parts.append(render_item(item_dir, out_dir, sample, camp, n))
    page = f"""<!doctype html><meta charset="utf-8"><title>Spot-check review {html.escape(camp)}</title>
<style>body{{font:14px/1.5 system-ui,sans-serif;margin:16px;background:#f5f6f7;color:#1d2328}}section{{background:#fff;border:1px solid #d9dde1;border-radius:8px;padding:12px 16px;margin:0 0 16px}}
h2{{margin:0 0 8px;font-size:17px}}h3{{margin:12px 0 3px}}small{{color:#66727d;font-weight:400}}.grid{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:16px}}
 .warning{{color:#8a3100;background:#fff0e6;padding:8px}}
th{{text-align:left;vertical-align:top;width:9em;color:#66727d;font-weight:500;padding:2px 8px 2px 0}}td{{padding:2px 0;overflow-wrap:anywhere}}table{{width:100%}}.v{{font-weight:600}}
.shots{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:6px}}.shots a{{font-size:11px;color:#66727d;text-decoration:none}}.shots img{{width:100%;border:1px solid #d9dde1;border-radius:4px}}
details{{margin:12px 0}}summary{{cursor:pointer}}@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}</style>
<h1>Spot-check review — {html.escape(camp)} ({len(spot["sample"])} of {show(spot.get("population_n"))}, seed {show(spot.get("seed"))})</h1>
<p>Compare each claim with the original content frames and input records. Unknown means the review notes do not establish that field.</p>{"".join(parts)}"""
    path = out_dir / "spot_check_review.html"
    path.write_text(page)
    print(path)


if __name__ == "__main__":
    main()
