"""Sample items for a human spot-check of description accuracy.

    python3 spot_check.py --base WS [--items-dir items] --campaign ID [--rate 0.1] [--seed 20261001]

Population = items whose latest attempt is this campaign and whose description is valid in derived/report.json
(run validate_descriptions.py first). Writes archive/<campaign>/spot_check.json with an empty "verdicts" map for the
human to fill: correct | minor | wrong | hallucinated.
"""
import argparse, json, math, os, random


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--items-dir", default="items")
    ap.add_argument("--campaign", required=True); ap.add_argument("--rate", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=20261001)
    a = ap.parse_args()
    rep = json.load(open(os.path.join(a.base, "derived/report.json")))["items"]
    pop = sorted(r["item_id"] for r in rep if r["campaign"] == a.campaign and r["description_valid"])
    k = min(len(pop), max(1, math.ceil(len(pop) * a.rate))) if pop else 0
    sample = random.Random(a.seed).sample(pop, k)
    out = os.path.join(a.base, "archive", a.campaign); os.makedirs(out, exist_ok=True)
    doc = {"seed": a.seed, "method": "random.Random(seed).sample(sorted(valid item_ids), ceil(rate*n))", "population_n": len(pop),
           "sample": [{"item_id": s, "description": f"{a.items_dir}/{s}/description.json", "shots": f"{a.items_dir}/{s}/shots/"} for s in sample],
           "verdicts": {}}
    json.dump(doc, open(os.path.join(out, "spot_check.json"), "w"), ensure_ascii=False, indent=1)
    print(f"{k} of {len(pop)} sampled -> {out}/spot_check.json")


if __name__ == "__main__":
    main()
