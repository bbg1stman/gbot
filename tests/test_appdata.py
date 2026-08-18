"""앱 런타임 데이터 테스트. 위키 시험 페이지는 없어야 한다."""

from __future__ import annotations

import unittest
from pathlib import Path

from gbot.appdata import diagnostic_blueprint, list_bands, load, plan_for
from gbot.bank import get
from gbot.diagnostic import build_diagnostic

ROOT = Path(__file__).resolve().parent.parent


class TestAppData(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = load()

    def test_four_bands(self) -> None:
        bands = list_bands()
        self.assertEqual(len(bands), 4)
        ids = [b["id"] for b in bands]
        self.assertEqual(ids, ["미달", "경계", "안정", "여유"])
        for band in bands:
            self.assertIn("label", band)
            self.assertIn("score_min", band)
            self.assertIn("score_max", band)
            self.assertIn("next_action", band)
        midal = next(b for b in bands if b["id"] == "미달")
        self.assertLess(midal["score_max"], 40)
        self.assertEqual(midal["next_action"], "개념+유형")
        rules = self.app.levels["pass_rules"]
        self.assertEqual(rules["subject_min"], 40)
        self.assertEqual(rules["average_min"], 60)

    def test_six_blueprints(self) -> None:
        expected = {
            "국어": ("kor", "skill"),
            "수학": ("math", "unit"),
            "영어": ("eng", "skill"),
            "사회": ("soc", "unit"),
            "과학": ("sci", "unit"),
            "한국사": ("his", "unit"),
        }
        self.assertEqual(len(self.app.subjects["blueprints"]), 6)
        for name, (code, axis) in expected.items():
            bp = diagnostic_blueprint(name)
            via_code = diagnostic_blueprint(code)
            self.assertEqual(bp["subject_code"], code)
            self.assertEqual(bp["axis"], axis)
            self.assertEqual(bp, via_code)
            self.assertGreaterEqual(bp["item_count"], 8)
            self.assertLessEqual(bp["item_count"], 12)
            self.assertTrue(bp["axes"])
            self.assertEqual(bp["stop_rule"]["consecutive_misses"], 2)

    def test_plan_templates(self) -> None:
        for band in ("미달", "경계", "안정", "여유"):
            plan = plan_for(band)
            self.assertEqual(plan["band"], band)
            self.assertIn("label", plan)
            self.assertIn("focus", plan)
            self.assertIsInstance(plan["daily_items"], int)
            self.assertIsInstance(plan["include_concept"], bool)
            self.assertIsInstance(plan["include_type"], bool)
            self.assertIsInstance(plan["include_bank_slots"], bool)
        self.assertTrue(plan_for("미달")["include_concept"])
        self.assertTrue(plan_for("경계")["include_type"])
        self.assertTrue(plan_for("경계")["include_bank_slots"])

    def test_wiki_exams_gone(self) -> None:
        self.assertFalse((ROOT / "wiki" / "exams").exists())

    def test_build_diagnostic_no_stems(self) -> None:
        parts = build_diagnostic("국어")
        self.assertTrue(parts)
        self.assertEqual(sum(p["n"] for p in parts), 12)
        for part in parts:
            self.assertIn("axis", part)
            self.assertIn("n", part)
            self.assertNotIn("stem", part)
            self.assertNotIn("choices", part)
            self.assertNotIn("answer", part)

    def test_bank_loader_defaults(self) -> None:
        item = get("go-2026-2-kor-12")
        self.assertIsNotNone(item)
        assert item is not None
        self.assertEqual(item["role"], "bank")
        self.assertIsNone(item["unit"])
        self.assertIsNone(item["wiki_concept"])
        self.assertIsNone(item["wiki_type"])
        self.assertIsNone(item["stem"])


if __name__ == "__main__":
    unittest.main()
