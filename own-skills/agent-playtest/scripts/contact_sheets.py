"""Audit contact sheets: one row per item (first / middle / last screenshot of its latest attempt), 6 items per sheet.

    python3 contact_sheets.py --base WS [--items-dir items] --campaign ID [--outcome played,partial] [--crop W:H:X:Y] --out DIR

Needs ffmpeg. Writes DIR/sheet_NN.png and DIR/index.json (sheet, row -> item, outcome, seconds). Sheets are disposable;
record verdicts in each attempt's "audit" field.
"""
import argparse, json, os, subprocess
from _common import items, item_id

TW, TH, PER = 400, 225, 6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--items-dir", default="items")
    ap.add_argument("--campaign"); ap.add_argument("--outcome", default="played,partial")
    ap.add_argument("--crop", help="ffmpeg crop W:H:X:Y of the content frame (CSS px)"); ap.add_argument("--out", required=True)
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    rows = []
    for d, pt, _ in items(a.base, a.items_dir):
        at = pt["attempts"][-1]
        if (a.campaign and at.get("campaign") != a.campaign) or at.get("outcome") not in a.outcome.split(","):
            continue
        shots = [os.path.join(d, s["file"]) for s in at.get("shots", []) if os.path.exists(os.path.join(d, s["file"]))]
        pick = [shots[i] for i in sorted({0, len(shots) // 2, len(shots) - 1})] if shots else []
        rows.append({"item_id": item_id(pt), "title": pt.get("title"), "outcome": at.get("outcome"),
                     "verified_s": at.get("verified_gameplay_total_s"), "shots": pick})
    crop = f"crop={a.crop}," if a.crop else ""
    for i in range(0, len(rows), PER):
        group, inputs, filt, n = rows[i:i + PER], [], [], 0
        for j, r in enumerate(group):
            files = (r["shots"] + [r["shots"][-1] if r["shots"] else None] * 3)[:3]
            for k, f in enumerate(files):
                inputs += ["-i", f] if f else ["-f", "lavfi", "-i", f"color=gray:s={TW}x{TH}"]
                filt.append(f"[{n}:v]{crop}scale={TW}:{TH},setsar=1[r{j}c{k}]" if f else f"[{n}:v]null[r{j}c{k}]"); n += 1
            filt.append(f"[r{j}c0][r{j}c1][r{j}c2]hstack=3[row{j}]")
            r["sheet"], r["row"] = i // PER + 1, j + 1
        filt.append("".join(f"[row{j}]" for j in range(len(group))) + (f"vstack={len(group)}[out]" if len(group) > 1 else "null[out]"))
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]",
                        "-frames:v", "1", os.path.join(a.out, f"sheet_{i // PER + 1:02d}.png")], check=True)
    json.dump([{k: v for k, v in r.items() if k != "shots"} for r in rows], open(os.path.join(a.out, "index.json"), "w"),
              ensure_ascii=False, indent=1)
    print(len(rows), "items ->", a.out)


if __name__ == "__main__":
    main()
