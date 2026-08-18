"""문제은행 슬롯 테스트. stem이 None이어도 동작해야 한다."""

from __future__ import annotations

import unittest

from gbot.bank import Bank, get, list_exams, list_items, load, stats


class TestBank(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bank = load()

    def test_exam_count(self) -> None:
        exams = list_exams()
        self.assertEqual(len(exams), 12)
        ids = [e["id"] for e in exams]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("go-2021-1", ids)
        self.assertIn("go-2026-2", ids)

    def test_item_count(self) -> None:
        items = list_items()
        self.assertEqual(len(items), 1740)
        self.assertEqual(12 * 145, 1740)

    def test_all_official_embargoed(self) -> None:
        items = list_items()
        self.assertTrue(items)
        for item in items:
            self.assertEqual(item["type"], "item")
            self.assertEqual(item["source"], "official")
            self.assertEqual(item["status"], "embargoed")
            self.assertEqual(item["license"], "none")
            self.assertEqual(item["kind"], "official-slot")
            self.assertEqual(item["level"], "고졸")
            self.assertIsNone(item["stem"])
            self.assertIsNone(item["choices"])
            self.assertIsNone(item["answer"])
            self.assertIsNone(item["topic"])
            self.assertIsNone(item["skill"])
            self.assertIsNone(item["explanation"])

    def test_unique_ids(self) -> None:
        ids = [item["id"] for item in list_items()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_math_has_20_not_25(self) -> None:
        math_items = list_items(subject="수학")
        self.assertEqual(len(math_items), 12 * 20)
        math_by_code = list_items(subject="math")
        self.assertEqual(len(math_by_code), 12 * 20)
        for exam in list_exams():
            sitting = exam["id"].removeprefix("go-")
            found = list_items(exam=sitting, subject="math")
            self.assertEqual(len(found), 20, msg=sitting)
            self.assertTrue(all(i["number"] <= 20 for i in found))
            self.assertFalse(any(i["id"].endswith("-25") for i in found))

    def test_required_counts(self) -> None:
        expected = {
            "kor": 25,
            "math": 20,
            "eng": 25,
            "soc": 25,
            "sci": 25,
            "his": 25,
        }
        for exam in list_exams():
            sitting = exam["id"].removeprefix("go-")
            for code, count in expected.items():
                found = list_items(exam=sitting, subject=code)
                self.assertEqual(len(found), count, msg=f"{sitting} {code}")

    def test_his_2021_curriculum_2009(self) -> None:
        for sitting in ("2021-1", "2021-2"):
            items = list_items(exam=sitting, subject="his")
            self.assertEqual(len(items), 25)
            for item in items:
                self.assertEqual(item["curriculum"], "2009")

    def test_other_curriculum_2015(self) -> None:
        for item in list_items():
            if item["subject_code"] == "his" and item["year"] == 2021:
                continue
            self.assertEqual(item["curriculum"], "2015", msg=item["id"])

    def test_get_slot_without_stem(self) -> None:
        item = get("go-2026-2-kor-12")
        self.assertIsNotNone(item)
        assert item is not None
        self.assertEqual(item["number"], 12)
        self.assertEqual(item["subject"], "국어")
        self.assertEqual(item["exam"], "2026-2")
        self.assertIsNone(item["stem"])
        self.assertIsNone(item["choices"])
        self.assertIsNone(get("no-such-id"))

    def test_stats(self) -> None:
        s = stats()
        self.assertEqual(s["exams"], 12)
        self.assertEqual(s["items"], 1740)
        self.assertEqual(s["embargoed"], 1740)
        self.assertEqual(s["ready"], 0)

    def test_filter_exam_and_subject(self) -> None:
        items = list_items(exam="2026-2", subject="국어")
        self.assertEqual(len(items), 25)
        self.assertTrue(all(i["exam"] == "2026-2" for i in items))
        self.assertTrue(all(i["subject"] == "국어" for i in items))
        via_id = list_items(exam="go-2026-2", subject="kor")
        self.assertEqual([i["id"] for i in items], [i["id"] for i in via_id])

    def test_filter_status(self) -> None:
        self.assertEqual(len(list_items(status="embargoed")), 1740)
        self.assertEqual(len(list_items(status="ready")), 0)

    def test_stem_none_does_not_break_load(self) -> None:
        bank = Bank()
        bank.load()
        sample = bank.get("go-2021-1-math-1")
        self.assertIsNotNone(sample)
        assert sample is not None
        self.assertIsNone(sample["stem"])
        self.assertEqual(bank.stats()["items"], 1740)


if __name__ == "__main__":
    unittest.main()
