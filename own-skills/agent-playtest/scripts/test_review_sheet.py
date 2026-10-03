"""Focused local renderer check; no browser or network."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from review_sheet import image_ref


SCRIPT = Path(__file__).with_name("review_sheet.py")


class ReviewSheetTest(unittest.TestCase):
    def test_review_and_legacy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "items").mkdir()
            (root / "items" / "outside.png").write_bytes(b"image")
            for iid in ("reviewed", "legacy"):
                item = root / "items" / iid
                (item / "shots").mkdir(parents=True)
                (item / "description.json").write_text(json.dumps({"content": {
                    "summary": "<summary>", "environment_style": "forest",
                    "observable_interactions": ["jump"], "gameplay_objectives": "reach gate",
                    "mood_pacing": "calm", "unconfirmed_items": ["multiplayer"],
                    "semantic_description": "A forest scene."
                }}))
                (item / "playtest.json").write_text(json.dumps({"title": iid, "attempts": [{
                    "campaign": "c1", "outcome": "played", "observed_kind": "game",
                    "audit": {"by": "reviewer", "verdict": "ok", "note": "scoped"},
                    "shots": [{"file": f"shots/{iid}_{name}.png"} for name in ("content", "ad", "loader")]
                }]}))
                for name in ("content", "ad", "loader"):
                    (item / "shots" / f"{iid}_{name}.png").write_bytes(b"image")
            (root / "items" / "reviewed" / "review.json").write_text(json.dumps({
                "declared": {"source": "catalog <x>", "snapshot_date": "2026-10-03",
                             "title": "", "kind": "Game", "description": "creator text",
                             "tags": ["puzzle"], "view_count": 3},
                "languages": {"db_locale": "en", "content_ui": "ja"},
                "devices": {"declared": ["HMD"], "tested": ["Desktop"], "unknown": ["Android", "iOS"]},
                "coverage": {"reached": ["gameplay"], "missing": ["result"]},
                "timing": {"method": "browser timestamps"},
                "frames": [{"ref": f"shots/reviewed_{name}.png", "class": "content" if name == "stale" else name}
                           for name in ("content", "ad", "loader", "stale")],
                "representative_refs": ["shots/reviewed_ad.png", "shots/reviewed_loader.png",
                                        "shots/reviewed_content.png", "shots/reviewed_stale.png",
                                        "../outside.png"],
                "human_review": "pending"
            }))
            (root / "items" / "reviewed" / "shots" / "reviewed_stale.png").write_bytes(b"image")
            stale = root / "items" / "stale"
            stale.mkdir()
            (stale / "description.json").write_text(json.dumps({
                "campaign": "old", "content": {"summary": "STALE CLAIM"}, "evidence": ["old evidence"]
            }))
            blocked = root / "items" / "blocked"
            blocked.mkdir()
            spot = root / "archive" / "c1" / "spot_check.json"
            spot.parent.mkdir(parents=True)
            spot.write_text(json.dumps({"sample": [{"item_id": "reviewed"}, {"item_id": "legacy"},
                                                    {"item_id": "stale"}, {"item_id": "blocked"}],
                                        "population_n": 4, "seed": 1}))
            subprocess.run([sys.executable, str(SCRIPT), "--base", str(root), "--spot", str(spot)],
                           check=True, capture_output=True, text=True)
            page = spot.with_name("spot_check_review.html").read_text()
            self.assertIn("catalog &lt;x&gt;", page)
            self.assertIn("<td>empty</td>", page)
            self.assertIn("&lt;summary&gt;", page)
            self.assertIn("environment_style", page)
            self.assertIn("semantic_description", page)
            self.assertIn("Language evidence", page)
            self.assertIn("Loader diagnostic (1)", page)
            self.assertIn("Raw frames (1; inspect originals)", page)
            self.assertEqual(page.count("reviewed_content.png"), 6)  # representative + raw links
            self.assertEqual(page.count("reviewed_loader.png"), 3)   # collapsed loader link
            self.assertNotIn("reviewed_ad.png", page)
            self.assertNotIn("reviewed_stale.png", page)
            self.assertIn('<div class="grid"><div><h3>Declared</h3>', page)
            self.assertIn('</table></div><div><h3>Observed</h3>', page)
            self.assertIn("Description campaign differs", page)
            self.assertNotIn("STALE CLAIM", page)
            self.assertNotIn("old evidence", page)
            self.assertIn("Description missing", page)
            self.assertIn("<p>unknown</p>", page)  # legacy representatives
            self.assertIsNone(image_ref(root / "items" / "reviewed", spot.parent, "../outside.png"))


if __name__ == "__main__":
    unittest.main()
