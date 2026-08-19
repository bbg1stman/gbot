"""Daily order frame. Review is always the first slot."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gbot.bank import get, load as load_bank
from gbot.dayplan import build_day, notes_due
from gbot.learner import load_sample

ROOT = Path(__file__).resolve().parent.parent


class TestDayPlan(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_bank()
        sample = ROOT / "data" / "app" / "sample_user.json"
        if not sample.is_file():
            sample = ROOT / "pack" / "sample_learner.json"
        cls.user = load_sample(sample)

    def test_review_first_on_2026_08_19(self) -> None:
        plan = build_day(self.user, "2026-08-19")
        self.assertEqual(plan["user_id"], "u-demo")
        self.assertEqual(plan["date"], "2026-08-19")
        self.assertEqual(len(plan["steps"]), 4)
        self.assertEqual([s["id"] for s in plan["steps"]], ["review", "concept", "type", "new"])
        review = plan["steps"][0]
        self.assertEqual(review["id"], "review")
        self.assertIn("orig-math-001", review["item_ids"])
        self.assertIn("orig-math-002", review["item_ids"])
        self.assertNotIn("orig-his-001", review["item_ids"])
        self.assertIn("wn-1", review["note_ids"])
        self.assertIn("wn-2", review["note_ids"])

    def test_review_empty_on_2026_08_18(self) -> None:
        plan = build_day(self.user, "2026-08-18")
        self.assertEqual([s["id"] for s in plan["steps"]], ["review", "concept", "type", "new"])
        self.assertEqual(len(plan["steps"]), 4)
        review = plan["steps"][0]
        self.assertEqual(review["item_ids"], [])
        self.assertEqual(review["note_ids"], [])
        self.assertEqual(review["count"], 0)

    def test_new_never_official_or_embargoed(self) -> None:
        for on_date in ("2026-08-18", "2026-08-19"):
            plan = build_day(self.user, on_date)
            new = next(s for s in plan["steps"] if s["id"] == "new")
            for iid in new["item_ids"]:
                item = get(iid)
                self.assertIsNotNone(item, msg=iid)
                assert item is not None
                self.assertNotEqual(item.get("source"), "official", msg=iid)
                self.assertNotEqual(item.get("status"), "embargoed", msg=iid)
                self.assertEqual(item.get("source"), "original", msg=iid)
                self.assertEqual(item.get("status"), "ready", msg=iid)

    def test_midal_day_counts_sum_to_8(self) -> None:
        templates = json.loads(
            (ROOT / "data" / "plans" / "templates.json").read_text(encoding="utf-8")
        )
        midal = next(t for t in templates["templates"] if t["band"] == "미달")
        counts = midal["day_counts"]
        self.assertEqual(sum(counts.values()), 8)
        self.assertEqual(sum(counts.values()), midal["daily_items"])
        self.assertEqual(counts["review"], 3)
        self.assertEqual(counts["concept"], 2)
        self.assertEqual(counts["type"], 2)
        self.assertEqual(counts["new"], 1)

    def test_notes_due_helper(self) -> None:
        due19 = notes_due(self.user, "2026-08-19")
        ids = [n["item_id"] for n in due19]
        self.assertIn("orig-math-001", ids)
        self.assertIn("orig-math-002", ids)
        self.assertNotIn("orig-his-001", ids)
        self.assertEqual(notes_due(self.user, "2026-08-18"), [])


if __name__ == "__main__":
    unittest.main()
