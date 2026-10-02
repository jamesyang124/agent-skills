"""Render a spot-check sample as one local HTML page: each item's description next to its screenshots.

    python3 review_sheet.py --base WS [--items-dir items] --spot archive/<campaign>/spot_check.json [--campaign ID]

Writes <spot_check dir>/spot_check_review.html (relative image paths; open it locally, do not publish it).
The reviewer records a verdict per item: correct | minor | wrong | hallucinated, plus a note.
"""
import argparse, glob, html, json, os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--items-dir", default="items")
    ap.add_argument("--spot", required=True); ap.add_argument("--campaign")
    a = ap.parse_args()
    spot = json.load(open(a.spot)); out_dir = os.path.dirname(os.path.abspath(a.spot))
    camp = a.campaign or os.path.basename(out_dir)
    parts = []
    for n, s in enumerate(spot["sample"], 1):
        iid = s.get("item_id") or s.get("hub_sid"); d = os.path.join(a.base, a.items_dir, iid)
        desc = json.load(open(os.path.join(d, "description.json")))["content"]
        shots = sorted(glob.glob(os.path.join(d, "shots", f"{camp}_*.png")))
        imgs = "".join(f'<a href="{html.escape(os.path.relpath(p, out_dir))}" target="_blank"><img src="{html.escape(os.path.relpath(p, out_dir))}" loading="lazy"><span>{os.path.basename(p)}</span></a>' for p in shots)
        rows = "".join(f"<tr><th>{k}</th><td>{html.escape(str(desc.get(k, '')))}</td></tr>" for k in
                       ("summary", "environment_style", "observable_interactions", "gameplay_objectives", "mood_pacing", "unconfirmed_items"))
        parts.append(f'<section><h2>{n}. {html.escape(s.get("title", iid))} <small>{iid} · {html.escape(str(s.get("outcome", "")))}</small></h2>'
                     f'<div class="grid"><div><table>{rows}</table><p class="sd">{html.escape(desc.get("semantic_description", ""))}</p>'
                     f'<p class="v">Verdict: correct / minor / wrong / hallucinated — note:</p></div><div class="shots">{imgs}</div></div></section>')
    page = f"""<!doctype html><meta charset="utf-8"><title>Spot-check review {html.escape(camp)}</title>
<style>body{{font:14px/1.5 system-ui,sans-serif;margin:16px;background:#f5f6f7;color:#1d2328}}section{{background:#fff;border:1px solid #d9dde1;border-radius:8px;padding:12px 16px;margin:0 0 16px}}
h2{{margin:0 0 8px;font-size:17px}}small{{color:#66727d;font-weight:400}}.grid{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.2fr);gap:16px}}
th{{text-align:left;vertical-align:top;width:9em;color:#66727d;font-weight:500;padding:2px 8px 2px 0}}td{{padding:2px 0}}.sd{{background:#f0f3f5;padding:8px;border-radius:6px}}
.v{{font-weight:600}}.shots{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:6px}}.shots a{{font-size:11px;color:#66727d;text-decoration:none}}.shots img{{width:100%;border:1px solid #d9dde1;border-radius:4px}}
@media(max-width:900px){{.grid{{grid-template-columns:1fr}}}}</style>
<h1>Spot-check review — {html.escape(camp)} ({len(spot["sample"])} of {spot.get("population_n", "?")}, seed {spot.get("seed")})</h1>
<p>For each item: does every claim in the description match what the screenshots show? Click a screenshot to enlarge it.</p>{"".join(parts)}"""
    path = os.path.join(out_dir, "spot_check_review.html"); open(path, "w").write(page); print(path)


if __name__ == "__main__":
    main()
