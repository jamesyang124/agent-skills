"""Self-check for the workspace scripts (no browser, no network). Run: python3 selftest.py"""
import json, os, struct, subprocess, sys, tempfile, zlib

HERE = os.path.dirname(os.path.abspath(__file__))


def png(path, v):
    raw = b"".join(b"\x00" + bytes([v]) * 3 * 8 for _ in range(8))
    def chunk(t, d): return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(path, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 8, 8, 8, 2, 0, 0, 0))
                           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def item(ws, iid, outcome, kind, words, cite_missing=False):
    d = os.path.join(ws, "items", iid); os.makedirs(os.path.join(d, "shots"))
    png(os.path.join(d, "shots", "c1_01.png"), 10)
    json.dump({"item_id": iid, "title": iid, "attempts": [{"campaign": "c1", "method": "closed_loop", "outcome": outcome,
               "observed_kind": kind, "observed_kind_evidence": ["shots/c1_01.png"], "shots": [{"file": "shots/c1_01.png"}]}]},
              open(os.path.join(d, "playtest.json"), "w"))
    ref = "shots/c1_99.png" if cite_missing else "shots/c1_01.png"
    json.dump({"item_id": iid, "content": {"summary": "s", "semantic_description": "word " * words, "unconfirmed_items": []},
               "evidence": [{"field": "summary", "source_type": "screenshot", "source_ref": ref}], "confidence": 0.8},
              open(os.path.join(d, "description.json"), "w"))


def run(*args):
    return subprocess.run([sys.executable, *args], cwd=HERE, capture_output=True, text=True, check=True).stdout


with tempfile.TemporaryDirectory() as ws:
    item(ws, "a", "played", "game", 250)                     # valid; declared Experience -> mismatch
    item(ws, "b", "partial", "gallery", 120)                 # too short
    item(ws, "c", "played", "game", 250, cite_missing=True)  # bad citation; declared Game -> no mismatch
    item(ws, "d", "excluded_paywall", "broken", 250)         # excluded; broken never a mismatch
    meta = os.path.join(ws, "declared.jsonl")
    with open(meta, "w") as f:
        for iid, k in [("a", "Experience"), ("b", "Experience"), ("c", "Game"), ("d", "Game")]:
            f.write(json.dumps({"item_id": iid, "declared_kind": k, "public": True, "adult": False}) + "\n")
    run("validate_descriptions.py", "--base", ws, "--meta", meta)
    rep = {r["item_id"]: r for r in json.load(open(os.path.join(ws, "derived/report.json")))["items"]}
    assert rep["a"]["description_valid"] and not rep["b"]["description_valid"] and not rep["c"]["description_valid"]
    assert "under 200 words" in rep["b"]["reasons"] and "cites a missing screenshot" in rep["c"]["reasons"]
    run("observed_kind_mismatches.py", "--base", ws, "--meta", meta)
    mm = [json.loads(l) for l in open(os.path.join(ws, "derived/observed_kind_mismatches.jsonl"))]
    assert [m["item_id"] for m in mm] == ["a"], mm
    run("spot_check.py", "--base", ws, "--campaign", "c1", "--rate", "0.1")
    sc = json.load(open(os.path.join(ws, "archive/c1/spot_check.json")))
    assert sc["population_n"] == 1 and len(sc["sample"]) == 1
    print("selftest: OK")

# Strict gate: provenance and audit must survive even when text length passes.
from copy import deepcopy
from validate_descriptions import check
with tempfile.TemporaryDirectory() as ws:
    item(ws, "a", "partial", "game", 250)
    d = os.path.join(ws, "items", "a")
    pt = json.load(open(os.path.join(d, "playtest.json")))
    desc = json.load(open(os.path.join(d, "description.json")))
    desc["campaign"] = "c1"
    pt["attempts"][-1]["audit"] = {"verdict": "ok", "by": "test reviewer", "note": "scoped evidence"}
    meta = {"a": {"public": True, "adult": False}}
    assert not check(d, pt, desc, meta, strict=True)
    for key, value, reason in [("evidence", [], "missing evidence"),
                               ("campaign", "old", "description campaign mismatch"),
                               ("item_id", "other", "description item mismatch")]:
        bad = deepcopy(desc); bad[key] = value
        assert reason in check(d, pt, bad, meta, strict=True)
    bad = deepcopy(desc); bad["evidence"][0]["source_ref"] = "shots/other.png"
    assert "evidence not in latest attempt shots" in check(d, pt, bad, meta, strict=True)
    bad = deepcopy(pt); bad["attempts"][-1]["audit"] = None
    assert "missing completed audit with reviewer and scope" in check(d, bad, desc, meta, strict=True)
    assert "strict mode requires declared metadata" in check(d, pt, desc, None, strict=True)
    assert "eligibility must be explicit public=true adult=false" in check(d, pt, desc, {"a": {}}, strict=True)
    print("strict selftest: OK")
