"""Khan/Santa-style mastery levels. Official stems stay unused."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path

from gbot.dayplan import build_day
from gbot.evaluate import item_stats_from_attempts
from gbot.learner import load_sample
from gbot.mastery import DONE_LEVELS, MASTERY_ORDER, is_done, item_mastery_map, mastery_of

ROOT = Path(__file__).resolve().parent.parent


class TestMastery(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.user = load_sample(ROOT / "data" / "app" / "sample_user.json")

    def test_order_and_done_levels(self) -> None:
        self.assertEqual(MASTERY_ORDER, ("미시도", "익숙", "숙달", "완료"))
        self.assertEqual(DONE_LEVELS, {"숙달", "완료"})

    def test_empty_none_is_untried(self) -> None:
        self.assertEqual(mastery_of(None), "미시도")
        self.assertEqual(mastery_of({}), "미시도")
        self.assertEqual(mastery_of({"attempts": 0}), "미시도")
        self.assertFalse(is_done(None))
        self.assertFalse(is_done({}))

    def test_one_correct_is_familiar(self) -> None:
        stat = {
            "attempts": 1,
            "misses": 0,
            "last_correct": True,
            "streak_wrong": 0,
            "ease": 1.0,
        }
        self.assertEqual(mastery_of(stat), "익숙")
        self.assertFalse(is_done(stat))

    def test_two_correct_zero_miss_is_mastered(self) -> None:
        stat = {
            "attempts": 2,
            "misses": 0,
            "last_correct": True,
            "streak_wrong": 0,
            "ease": 1.0,
        }
        self.assertEqual(mastery_of(stat), "숙달")
        self.assertTrue(is_done(stat))

    def test_three_correct_zero_miss_is_complete(self) -> None:
        stat = {
            "attempts": 3,
            "misses": 0,
            "last_correct": True,
            "streak_wrong": 0,
            "ease": 1.0,
        }
        self.assertEqual(mastery_of(stat), "완료")
        self.assertTrue(is_done(stat))

    def test_ease_below_threshold_stays_familiar(self) -> None:
        stat = {
            "attempts": 3,
            "misses": 1,
            "last_correct": True,
            "streak_wrong": 0,
            "ease": 0.667,
        }
        self.assertEqual(mastery_of(stat), "익숙")
        self.assertFalse(is_done(stat))

    def test_recompute_ignores_stored_mastery(self) -> None:
        stat = {
            "attempts": 3,
            "misses": 0,
            "last_correct": True,
            "streak_wrong": 0,
            "ease": 1.0,
            "mastery": "미시도",
        }
        self.assertEqual(mastery_of(stat), "완료")

    def test_computes_ease_when_missing(self) -> None:
        two = {
            "attempts": 2,
            "misses": 0,
            "last_correct": True,
            "streak_wrong": 0,
        }
        self.assertEqual(mastery_of(two), "숙달")
        low = {
            "attempts": 3,
            "misses": 1,
            "last_correct": True,
            "streak_wrong": 0,
        }
        self.assertEqual(mastery_of(low), "익숙")

    def test_item_stats_from_attempts_includes_mastery(self) -> None:
        derived = item_stats_from_attempts(self.user)
        self.assertTrue(derived)
        for row in derived:
            self.assertIn(row["mastery"], MASTERY_ORDER)
            self.assertEqual(row["mastery"], mastery_of(row))
        math003 = next(r for r in derived if r["item_id"] == "orig-math-003")
        self.assertEqual(math003["mastery"], "익숙")

    def test_item_mastery_map_from_stored(self) -> None:
        levels = item_mastery_map(self.user)
        self.assertEqual(levels["orig-math-003"], "익숙")
        self.assertEqual(levels["orig-kor-001"], "익숙")
        self.assertNotIn(levels["orig-math-003"], DONE_LEVELS)

    def test_new_slot_skips_completed_item(self) -> None:
        baseline = build_day(self.user, "2026-08-19")
        base_new = next(s for s in baseline["steps"] if s["id"] == "new")
        self.assertIn("orig-math-003", base_new["item_ids"])

        user = copy.deepcopy(self.user)
        found = False
        for row in user["item_stats"]:
            if row["item_id"] == "orig-math-003":
                row["attempts"] = 3
                row["misses"] = 0
                row["last_correct"] = True
                row["streak_wrong"] = 0
                row["ease"] = 1.0
                row["mastery"] = "미시도"
                found = True
                break
        self.assertTrue(found)
        self.assertEqual(mastery_of(next(r for r in user["item_stats"] if r["item_id"] == "orig-math-003")), "완료")

        plan = build_day(user, "2026-08-19")
        new = next(s for s in plan["steps"] if s["id"] == "new")
        self.assertNotIn("orig-math-003", new["item_ids"])
        review = next(s for s in plan["steps"] if s["id"] == "review")
        self.assertIn("orig-math-001", review["item_ids"])
        self.assertIn("orig-math-002", review["item_ids"])
        self.assertEqual(review["item_ids"], next(s for s in baseline["steps"] if s["id"] == "review")["item_ids"])


if __name__ == "__main__":
    unittest.main()
