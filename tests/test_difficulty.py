"""Item difficulty matches student bands. Official slots stay null."""

from __future__ import annotations

import copy
import unittest
from pathlib import Path

from gbot.bank import get, list_items, load as load_bank
from gbot.dayplan import _new_item_ids, build_day, focus_band
from gbot.difficulty import BANDS, adjacent, infer_difficulty
from gbot.learner import load_sample
from gbot.pack import pack_item

ROOT = Path(__file__).resolve().parent.parent


def _midal_user() -> dict:
    return {
        "id": "u-midal-test",
        "subjects": {
            code: {"band": "미달", "estimate": 20, "last_diagnostic": None}
            for code in ("kor", "math", "eng", "soc", "sci", "his")
        },
        "sessions": [],
        "attempts": [],
        "wrong_notes": [],
        "error_patterns": [],
        "type_stats": [],
        "item_stats": [],
    }


class TestDifficultyHelper(unittest.TestCase):
    def test_bands_and_adjacent(self) -> None:
        self.assertEqual(BANDS, ("미달", "경계", "안정", "여유"))
        self.assertEqual(adjacent("미달"), ("경계",))
        self.assertEqual(adjacent("경계"), ("미달", "안정"))
        self.assertEqual(adjacent("안정"), ("경계", "여유"))
        self.assertEqual(adjacent("여유"), ("안정",))

    def test_infer_official_null(self) -> None:
        self.assertIsNone(
            infer_difficulty({"source": "official", "status": "embargoed"})
        )

    def test_infer_keeps_tagged(self) -> None:
        self.assertEqual(
            infer_difficulty({"source": "original", "difficulty": "안정"}),
            "안정",
        )

    def test_infer_diagnostic_early_is_midal(self) -> None:
        self.assertEqual(
            infer_difficulty(
                {
                    "id": "orig-math-001",
                    "source": "original",
                    "role": "diagnostic",
                    "number": 1,
                }
            ),
            "미달",
        )

    def test_infer_diagnostic_later_or_drill_is_border(self) -> None:
        self.assertEqual(
            infer_difficulty(
                {
                    "id": "orig-math-005",
                    "source": "original",
                    "role": "diagnostic",
                    "number": 5,
                }
            ),
            "경계",
        )
        self.assertEqual(
            infer_difficulty(
                {"id": "orig-eng-008", "source": "original", "role": "drill", "number": 8}
            ),
            "경계",
        )


class TestDifficultyOnItems(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_bank()

    def test_originals_all_have_band(self) -> None:
        originals = [i for i in list_items() if i.get("source") == "original"]
        self.assertTrue(originals)
        for item in originals:
            self.assertIn(item.get("difficulty"), BANDS, msg=item["id"])
            self.assertIsNotNone(item.get("difficulty"), msg=item["id"])

    def test_official_slots_difficulty_null(self) -> None:
        official = [i for i in list_items() if i.get("source") == "official"]
        self.assertEqual(len(official), 1740)
        for item in official:
            self.assertIsNone(item.get("difficulty"), msg=item["id"])

    def test_pack_item_keeps_original_and_nulls_official(self) -> None:
        orig = get("orig-math-001")
        assert orig is not None
        packed = pack_item(orig)
        self.assertEqual(packed["difficulty"], "미달")
        official = get("go-2026-2-kor-12")
        assert official is not None
        packed_off = pack_item(official)
        self.assertIsNone(packed_off["difficulty"])
        missing = dict(orig)
        missing.pop("difficulty", None)
        inferred = pack_item(missing)
        self.assertIn(inferred["difficulty"], BANDS)


class TestDayPlanPrefersFocusBand(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        load_bank()

    def test_midal_user_new_prefers_midal_or_adjacent(self) -> None:
        user = _midal_user()
        self.assertEqual(focus_band(user), "미달")
        ids = _new_item_ids({"subjects": []}, set(), 12, user)
        self.assertTrue(ids)
        allowed = {"미달", "경계"}
        diffs = []
        for iid in ids:
            item = get(iid)
            self.assertIsNotNone(item, msg=iid)
            assert item is not None
            self.assertEqual(item.get("source"), "original")
            self.assertNotEqual(item.get("status"), "embargoed")
            self.assertIn(item.get("difficulty"), allowed, msg=iid)
            diffs.append(item["difficulty"])
        self.assertEqual(diffs[0], "미달")
        self.assertIn("미달", diffs)

    def test_sample_user_new_still_midal_math(self) -> None:
        user = load_sample(ROOT / "data" / "app" / "sample_user.json")
        self.assertEqual(focus_band(user), "미달")
        plan = build_day(user, "2026-08-19")
        new = next(s for s in plan["steps"] if s["id"] == "new")
        self.assertTrue(new["item_ids"])
        for iid in new["item_ids"]:
            item = get(iid)
            assert item is not None
            self.assertIn(item.get("difficulty"), ("미달", "경계"), msg=iid)
        # existing mastery test relies on this pick
        self.assertIn("orig-math-003", new["item_ids"])

    def test_done_items_still_skipped(self) -> None:
        user = copy.deepcopy(load_sample(ROOT / "data" / "app" / "sample_user.json"))
        for row in user["item_stats"]:
            if row["item_id"] == "orig-math-003":
                row["attempts"] = 3
                row["misses"] = 0
                row["last_correct"] = True
                row["streak_wrong"] = 0
                row["ease"] = 1.0
        plan = build_day(user, "2026-08-19")
        new = next(s for s in plan["steps"] if s["id"] == "new")
        self.assertNotIn("orig-math-003", new["item_ids"])


if __name__ == "__main__":
    unittest.main()
