"""Shared helpers: workspace iteration and item ids."""
import glob, json, os


def items(base, items_dir):
    """Yield (folder, playtest_dict, description_dict_or_None) for every item that has a playtest.json."""
    for d in sorted(glob.glob(os.path.join(base, items_dir, "*"))):
        p = os.path.join(d, "playtest.json")
        if not os.path.exists(p):
            continue
        q = os.path.join(d, "description.json")
        yield d, json.load(open(p)), (json.load(open(q)) if os.path.exists(q) else None)


def item_id(pt):
    return pt.get("item_id") or pt.get("hub_sid") or pt.get("room_id")


def load_meta(path):
    """declared metadata JSONL: {item_id, declared_kind, public, adult}"""
    if not path:
        return None
    return {r["item_id"]: r for r in (json.loads(l) for l in open(path) if l.strip())}
