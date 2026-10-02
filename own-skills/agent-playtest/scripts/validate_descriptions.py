"""Rebuild derived/ from the per-item folders. Never edit derived/ by hand.

    python3 validate_descriptions.py --base WS [--items-dir items] [--meta declared.jsonl]

Valid description: latest attempt is played/partial; not rejected in audit; summary + semantic_description present;
>= 200 words (CJK characters count half); every cited screenshot exists; with --meta: public and not adult.
Writes derived/descriptions.validated.json and derived/report.json.
"""
import argparse, json, os, re
from collections import Counter
from _common import items, item_id, load_meta


def words(t):
    return len(re.findall(r"[A-Za-z0-9]+", t)) + len(re.findall(r"[぀-ヿ㐀-鿿가-힯]", t)) / 2


def check(d, pt, desc, meta):
    a, why = pt["attempts"][-1], []
    if a.get("outcome") not in ("played", "partial"):
        why.append(f"outcome {a.get('outcome')}")
    if (a.get("audit") or {}).get("verdict") in ("rejected", "C", "B", "T"):
        why.append("rejected in screenshot audit")
    if not desc:
        why.append("no description")
    else:
        c = desc.get("content", {})
        if not c.get("summary") or not c.get("semantic_description"):
            why.append("missing summary / semantic_description")
        elif words(c["semantic_description"]) < 200:
            why.append("under 200 words")
        if not isinstance(c.get("unconfirmed_items", []), list):
            why.append("unconfirmed_items is not a list")
        refs = re.findall(r"shots/[\w.-]+\.png", " ".join(str(e.get("source_ref", "")) for e in desc.get("evidence", [])))
        if any(not os.path.exists(os.path.join(d, r)) for r in refs):
            why.append("cites a missing screenshot")
    if meta is not None:
        m = meta.get(item_id(pt))
        if not m:
            why.append("not in declared metadata")
        elif m.get("adult"):
            why.append("adult-only")
        elif not m.get("public", True):
            why.append("not public")
    return why


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--items-dir", default="items"); ap.add_argument("--meta")
    a = ap.parse_args(); meta = load_meta(a.meta)
    report, valid = [], []
    for d, pt, desc in items(a.base, a.items_dir):
        why, at = check(d, pt, desc, meta), pt["attempts"][-1]
        if not why:
            valid.append({"item_id": item_id(pt), "content": desc["content"], "evidence": desc.get("evidence", []),
                          "confidence": desc.get("confidence")})
        report.append({"item_id": item_id(pt), "title": pt.get("title"), "campaign": at.get("campaign"),
                       "outcome": at.get("outcome"), "observed_kind": at.get("observed_kind"),
                       "verified_s": at.get("verified_gameplay_total_s"), "description_valid": not why, "reasons": why})
    out = os.path.join(a.base, "derived"); os.makedirs(out, exist_ok=True)
    json.dump(valid, open(os.path.join(out, "descriptions.validated.json"), "w"), ensure_ascii=False, indent=1)
    summary = {"items": len(report), "descriptions_valid": len(valid), "outcomes": dict(Counter(r["outcome"] for r in report))}
    json.dump({"summary": summary, "items": report}, open(os.path.join(out, "report.json"), "w"), ensure_ascii=False, indent=1)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
