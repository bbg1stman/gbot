"""ItemStat + Evaluation. Official stems stay unused."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gbot.evaluate import evaluate, item_stats_from_attempts
from gbot.learner import item_stat, load_sample
from gbot.pack import PACK_DIR, load_pack

ROOT = Path(__file__).resolve().parent.parent


class TestEvaluate(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.user = load_sample(ROOT / "data" / "app" / "sample_user.json")
        cls.ev = evaluate(cls.user)

    def test_evaluate_math_weak_not_pass_ready(self) -> None:
        ev = self.ev
        self.assertEqual(ev["user_id"], "u-demo")
        overall = ev["overall"]
        self.assertFalse(overall["pass_ready"])
        self.assertTrue(overall["subject_min_risk"])
        self.assertTrue(overall["average_risk"])
        self.assertAlmostEqual(overall["estimate_avg"], 56.67, places=2)
        math = next(s for s in ev["subjects"] if s["code"] == "math")
        self.assertTrue(math["weak"])
        self.assertEqual(math["estimate"], 33)
        self.assertEqual(math["band"], "미달")
        self.assertLess(math["estimate"], 40)
        self.assertEqual(math["attempts"], 4)
        self.assertEqual(math["accuracy"], 0.25)
        others_weak = [s["code"] for s in ev["subjects"] if s["weak"] and s["code"] != "math"]
        self.assertEqual(others_weak, [])

    def test_weak_chapters_includes_math_poly(self) -> None:
        rows = self.ev["weak_chapters"]
        ids = [c["chapter_id"] for c in rows]
        self.assertIn("ch-math-poly", ids)
        poly = next(c for c in rows if c["chapter_id"] == "ch-math-poly")
        self.assertEqual(poly["subject_code"], "math")
        self.assertEqual(poly["title"], "다항식")
        self.assertGreaterEqual(poly["misses"], 2)
        self.assertLess(poly["accuracy"], 0.6)
        self.assertIsNone(poly["parent_id"])
        self.assertEqual(poly["attempts"], 3)
        self.assertEqual(poly["misses"], 3)
        self.assertEqual(poly["accuracy"], 0.0)

    def test_weak_types_includes_math_poly(self) -> None:
        ids = [t["type_id"] for t in self.ev["weak_types"]]
        self.assertIn("type-math-poly", ids)
        poly = next(t for t in self.ev["weak_types"] if t["type_id"] == "type-math-poly")
        self.assertEqual(poly["subject_code"], "math")
        self.assertGreaterEqual(poly["misses"], 3)
        self.assertGreaterEqual(poly["streak_wrong"], 2)
        self.assertNotIn("type-his-premodern", ids)

    def test_item_stats_per_attempted_item(self) -> None:
        derived = item_stats_from_attempts(self.user)
        attempted = {a["item_id"] for a in self.user["attempts"]}
        self.assertEqual({s["item_id"] for s in derived}, attempted)
        stored = self.user.get("item_stats") or []
        self.assertEqual({s["item_id"] for s in stored}, attempted)
        for item_id in attempted:
            row = item_stat(self.user, item_id)
            self.assertIsNotNone(row, msg=item_id)
            assert row is not None
            self.assertEqual(row["item_id"], item_id)
            self.assertIn("attempts", row)
            self.assertIn("misses", row)
            self.assertLessEqual(len(row.get("history") or []), 10)
        math001 = item_stat(self.user, "orig-math-001")
        assert math001 is not None
        self.assertEqual(math001["misses"], 1)
        self.assertIs(math001["last_correct"], False)
        self.assertEqual(math001["type_id"], "type-math-poly")
        self.assertFalse(item_stat(self.user, "missing-item"))

    def test_item_stats_derive_without_store(self) -> None:
        bare = {
            "id": self.user["id"],
            "subjects": self.user["subjects"],
            "attempts": self.user["attempts"],
            "wrong_notes": self.user["wrong_notes"],
            "type_stats": self.user["type_stats"],
            "error_patterns": self.user["error_patterns"],
        }
        stats = item_stats_from_attempts(bare)
        self.assertEqual(len(stats), 6)
        ev = evaluate(bare)
        self.assertFalse(ev["overall"]["pass_ready"])
        self.assertTrue(next(s for s in ev["subjects"] if s["code"] == "math")["weak"])
        self.assertIn("type-math-poly", [t["type_id"] for t in ev["weak_types"]])

    def test_weak_items_and_focus(self) -> None:
        ids = [w["item_id"] for w in self.ev["weak_items"]]
        self.assertIn("orig-math-001", ids)
        self.assertIn("orig-math-002", ids)
        self.assertIn("orig-math-003", ids)
        self.assertNotIn("orig-math-004", ids)
        self.assertNotIn("orig-kor-001", ids)
        self.assertTrue(all(str(i).startswith("orig-") for i in ids))
        focus_codes = [f["subject_code"] for f in self.ev["focus"]]
        self.assertEqual(focus_codes[0], "math")
        self.assertTrue(any("과락" in (f.get("reason") or "") for f in self.ev["focus"]))
        self.assertTrue(any("type-math-poly" in (f.get("reason") or "") for f in self.ev["focus"]))

    def test_snapshot_and_schema(self) -> None:
        snap = self.user.get("evaluation") or {}
        self.assertEqual(snap.get("user_id"), "u-demo")
        self.assertFalse(snap["overall"]["pass_ready"])
        math = next(s for s in snap["subjects"] if s["code"] == "math")
        self.assertTrue(math["weak"])
        self.assertEqual(math["band"], "미달")
        for schema_path in (ROOT / "data" / "app" / "schema.json", PACK_DIR / "schema.json"):
            if not schema_path.is_file():
                continue
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            self.assertIn("ItemStat", schema, msg=schema_path.name)
            self.assertIn("Evaluation", schema, msg=schema_path.name)
            for field in ("attempts", "misses", "last_correct", "next_review", "history"):
                self.assertIn(field, schema["ItemStat"]["required"], msg=field)
            for field in ("overall", "weak_chapters", "weak_types", "weak_items", "focus"):
                self.assertIn(field, schema["Evaluation"]["required"], msg=field)

    def test_official_stems_still_unused(self) -> None:
        pack = load_pack()
        official = [i for i in pack.items if i.get("source") == "official"]
        self.assertEqual(len(official), 1740)
        for item in official:
            self.assertIsNone(item.get("stem"), msg=item["id"])
            self.assertIsNone(item.get("choices"), msg=item["id"])
            self.assertIsNone(item.get("answer"), msg=item["id"])
        for w in self.ev["weak_items"]:
            self.assertFalse(str(w["item_id"]).startswith("go-"), msg=w["item_id"])
        for st in item_stats_from_attempts(self.user):
            self.assertTrue(str(st["item_id"]).startswith("orig-"), msg=st["item_id"])
        blob = json.dumps(self.ev, ensure_ascii=False)
        self.assertNotIn("훈민정음은 세종", blob)
        self.assertNotIn("(x+3)(x-2)", blob)


if __name__ == "__main__":
    unittest.main()
