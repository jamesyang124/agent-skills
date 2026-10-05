"""Renderer safety and scope checks, no browser or external services."""
import subprocess
import sys
import json
import tempfile
import unittest
from pathlib import Path
from review_sheet import render_item, image_ref

class ReviewTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.item = self.root / 'room'
        self.item.mkdir()
        (self.item / 'shots').mkdir()
        (self.item / 'shots/a.png').write_bytes(b'fixture')
        (self.item / 'shots/ad.png').write_bytes(b'fixture')
        self.put('playtest.json', {'attempts':[{'campaign':'new','shots':[{'file':'shots/a.png'},{'file':'shots/ad.png'}]}]})
        self.put('description.json', {'campaign':'new','content':{'summary':'<script>unsafe</script>','semantic_description':'Full observation'}})
        self.put('review.json', {'declared':{'db_snapshot_fields':{'title':'Test','content_type_id':2,'content_type_name':'Game','tags':['Puzzle']}},'languages':{'db_locale':[{'name':'English','code':'en','language_tag_id':58}]},'frames':[{'ref':'shots/a.png','class':'content'},{'ref':'shots/ad.png','class':'ad'}],'key_screen_refs':['shots/a.png']})
    def put(self,name,value):
        (self.item/name).write_text(json.dumps(value))
    def render(self,**kw):
        return render_item(self.item,self.root,{'item_id':'room',**kw},'new',1)
    def test_layout_and_escaping(self):
        out=self.render()
        self.assertIn('&lt;script&gt;',out)
        self.assertNotIn('<script>unsafe',out)
        declared=out.split('<div class="declared-block">')[1].split('</aside>')[0]
        self.assertNotIn('content_type_id',declared)
        self.assertNotIn('language_tag_id',declared)
        self.assertIn('English',declared)
        self.assertIn('Full observation',out)
        self.assertIn('observed-content',out)
        self.assertEqual(out.count('<img '),1)
        self.assertNotIn('shots/ad.png',out)
    def test_stale_description_withheld(self):
        self.put('description.json',{'campaign':'old','content':{'summary':'STALE CLAIM'},'evidence':['STALE REF']})
        out=self.render()
        self.assertNotIn('STALE CLAIM',out)
        self.assertNotIn('STALE REF',out)
    def test_pending_does_not_borrow(self):
        out=self.render(state='legacy_reference_pending_remote')
        self.assertNotIn('Full observation',out)
        self.assertNotIn('<img ',out)
    def test_path_escape(self):
        (self.root/'outside.png').write_bytes(b'fixture')
        self.assertIsNone(image_ref(self.item,self.root,'../outside.png'))
        (self.item/'link.png').symlink_to(self.root/'outside.png')
        self.assertIsNone(image_ref(self.item,self.root,'link.png'))
    def test_no_matching_attempt_no_frames(self):
        self.put('playtest.json',{'attempts':[{'campaign':'old','shots':[{'file':'shots/a.png'}]}]})
        self.assertNotIn('<img ',self.render())


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
            self.assertIn("Missing (not supplied)", page)
            self.assertIn("&lt;summary&gt;", page)
            self.assertIn("Environment / style", page)
            self.assertIn("Full semantic description", page)
            self.assertIn("DB declared language", page)
            self.assertIn("Loading diagnostics (1)", page)
            self.assertIn("Screenshots <small>1 frames", page)
            self.assertEqual(page.count("reviewed_content.png"), 4)  # representative + raw links
            self.assertEqual(page.count("reviewed_loader.png"), 4)   # collapsed loader link
            self.assertNotIn("reviewed_ad.png", page)
            self.assertNotIn("reviewed_stale.png", page)
            self.assertIn('<div class="body-grid"><div class="declared-block">', page)
            self.assertIn('<div class="observed-content">', page)
            self.assertIn("Description campaign differs", page)
            self.assertNotIn("STALE CLAIM", page)
            self.assertNotIn("old evidence", page)
            self.assertIn("No description supplied", page)
            self.assertIn("No screenshots supplied for this campaign.", page)  # legacy representatives
            self.assertIsNone(image_ref(root / "items" / "reviewed", spot.parent, "../outside.png"))


if __name__ == "__main__": unittest.main()
