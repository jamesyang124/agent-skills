"""List items whose observed_kind disagrees with their declared kind. Declared data is read, never written.

    python3 observed_kind_mismatches.py --base WS [--items-dir items] --meta declared.jsonl [--expect '{"Game":["game"]}']

Default map: Game -> game; Experience/Templates -> interactive_scene|gallery; Videos -> video. observed "broken" is never a
mismatch. Writes derived/observed_kind_mismatches.jsonl.
"""
import argparse, json, os
from _common import items, item_id, load_meta

DEFAULT = {"Game": ["game"], "Experience": ["interactive_scene", "gallery"], "Templates": ["interactive_scene", "gallery"],
           "Videos": ["video"]}


def mismatches(base, items_dir, meta, expect):
    n, out = 0, []
    for _, pt, _ in items(base, items_dir):
        att = [a for a in pt.get("attempts", []) if a.get("observed_kind")]
        if not att:
            continue
        n += 1; a = att[-1]; k = a["observed_kind"]
        c = (meta.get(item_id(pt)) or {}).get("declared_kind")
        if k == "broken" or c not in expect or k in expect[c]:
            continue
        out.append({"item_id": item_id(pt), "title": pt.get("title"), "declared_kind": c, "observed_kind": k,
                    "campaign": a.get("campaign"), "outcome": a.get("outcome"),
                    "evidence": [f"{item_id(pt)}/{s}" for s in a.get("observed_kind_evidence", [])]})
    return n, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--items-dir", default="items")
    ap.add_argument("--meta", required=True); ap.add_argument("--expect")
    a = ap.parse_args()
    n, out = mismatches(a.base, a.items_dir, load_meta(a.meta), json.loads(a.expect) if a.expect else DEFAULT)
    os.makedirs(os.path.join(a.base, "derived"), exist_ok=True)
    with open(os.path.join(a.base, "derived/observed_kind_mismatches.jsonl"), "w") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in out)
    print(f"{n} items with observed_kind, {len(out)} mismatches")


if __name__ == "__main__":
    main()
