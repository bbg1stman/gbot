"""App pack tests. Official stems stay null. Learner notes are first-class."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gbot.chapters import (
    chapter_id_for,
    chapters_for_year,
    edition_for_year,
    flatten,
    load_editions,
)
from gbot.learner import hot_patterns, hot_types, load_sample, notes_open
from gbot.pack import PACK_DIR, build_pack, load_pack

ROOT = Path(__file__).resolve().parent.parent


class TestPack(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.meta = build_pack()
        cls.pack = load_pack()

    def test_pack_files_exist(self) -> None:
        expected = [
            "meta.json",
            "items.json",
            "concepts.json",
            "types.json",
            "chapters.json",
            "editions.json",
            "levels.json",
            "blueprints.json",
            "plan_templates.json",
            "schema.json",
            "error_patterns.json",
            "sample_learner.json",
        ]
        for name in expected:
            path = PACK_DIR / name
            self.assertTrue(path.is_file(), msg=name)

    def test_items_length_1828(self) -> None:
        items = self.pack.items
        self.assertEqual(len(items), 1828)
        self.assertEqual(self.meta["counts"]["items"], 1828)
        ready = [i for i in items if i.get("status") == "ready"]
        embargoed = [i for i in items if i.get("status") == "embargoed"]
        self.assertEqual(len(ready), 88)
        self.assertEqual(len(embargoed), 1740)
        self.assertEqual(self.meta["counts"]["ready"], 88)

    def test_official_stems_still_null(self) -> None:
        official = [i for i in self.pack.items if i.get("source") == "official"]
        self.assertEqual(len(official), 1740)
        for item in official:
            self.assertIsNone(item["stem"], msg=item["id"])
            self.assertIsNone(item["choices"], msg=item["id"])
            self.assertIsNone(item["answer"], msg=item["id"])
        slot = self.pack.get("go-2026-2-kor-12")
        self.assertIsNotNone(slot)
        assert slot is not None
        self.assertIsNone(slot["stem"])
        self.assertIsNone(slot["type_id"])
        self.assertIsNone(slot.get("chapter_id"))
        self.assertEqual(slot["trap_tags"], [])
        self.assertIsNone(slot["media"])

    def test_originals_have_type_id(self) -> None:
        math = self.pack.get("orig-math-001")
        self.assertIsNotNone(math)
        assert math is not None
        self.assertEqual(math["type_id"], "type-math-poly")
        self.assertTrue(math["stem"])
        self.assertEqual(math["trap_tags"], [])
        his = self.pack.get("orig-his-001")
        assert his is not None
        self.assertEqual(his["type_id"], "type-his-premodern")
        kor = self.pack.get("orig-kor-005")
        assert kor is not None
        self.assertEqual(kor["type_id"], "type-kor-grammar")
        self.assertEqual(math["chapter_id"], "ch-math-poly")
        self.assertEqual(his["chapter_id"], "ch-his-premodern")
        self.assertEqual(kor["chapter_id"], "ch-kor-grammar")

    def test_types_match_axes(self) -> None:
        types = self.pack.types
        self.assertEqual(len(types), 30)
        ids = [t["id"] for t in types]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("type-math-poly", ids)
        self.assertIn("type-kor-grammar", ids)
        self.assertIn("type-his-premodern", ids)
        for t in types:
            self.assertIn("subject_code", t)
            self.assertIn("axis", t)
            self.assertIn("label", t)
            self.assertIn("description", t)

    def test_concepts_compiled(self) -> None:
        concepts = self.pack.concepts
        self.assertGreaterEqual(len(concepts), 30)
        ids = {c["id"] for c in concepts}
        self.assertIn("concept-math-다항식", ids)
        poly = next(c for c in concepts if c["axis"] == "다항식")
        self.assertEqual(poly["subject"], "수학")
        self.assertTrue(poly["body"])
        self.assertEqual(poly["title"], "다항식")

    def test_schema_has_learner_tables(self) -> None:
        for schema_path in (
            ROOT / "data" / "app" / "schema.json",
            PACK_DIR / "schema.json",
        ):
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            for name in ("WrongNote", "ErrorPattern", "TypeStat", "ItemStat", "Evaluation", "User", "Attempt", "Session", "Plan"):
                self.assertIn(name, schema, msg=f"{schema_path.name} {name}")
            required = schema["Attempt"]["required"]
            for field in ("session_id", "choice", "time_ms", "axis", "type_id"):
                self.assertIn(field, required, msg=field)

    def test_pack_schema_has_content_tables(self) -> None:
        schema = self.pack.schema
        for name in ("Item", "Concept", "Type", "Chapter", "Edition", "Blueprint", "ErrorPatternCatalog"):
            self.assertIn(name, schema)

    def test_chapters_six_subjects(self) -> None:
        chapters = self.pack.chapters
        self.assertTrue(chapters)
        codes = {c["subject_code"] for c in chapters}
        self.assertEqual(codes, {"kor", "math", "eng", "soc", "sci", "his"})
        ids = [c["id"] for c in chapters]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("ch-math-poly", ids)
        self.assertIn("ch-soc-market", ids)
        self.assertIn("ch-kor-grammar", ids)
        self.assertEqual(len(chapters), 119)
        for c in chapters:
            for key in ("id", "subject_code", "textbook", "number", "title", "axis", "type_id", "edition_id", "curriculum", "valid_from", "valid_to"):
                self.assertIn(key, c, msg=f"{c.get('id')} {key}")
            self.assertIn("parent_id", c)
            self.assertEqual(c["edition_id"], "2015-go")
            self.assertEqual(c["curriculum"], "2015")
            self.assertEqual(c["valid_from"], 2021)
            self.assertEqual(c["valid_to"], 2026)
        tops = [c for c in chapters if not c.get("parent_id")]
        self.assertEqual(len(tops), 30)
        poly = next(c for c in chapters if c["id"] == "ch-math-poly")
        self.assertEqual(poly["title"], "다항식")
        self.assertEqual(poly["axis"], "다항식")
        self.assertEqual(poly["type_id"], "type-math-poly")
        self.assertEqual(self.meta["counts"].get("chapters"), len(chapters))

    def test_error_patterns_seeded(self) -> None:
        labels = {p["label"] for p in self.pack.error_patterns}
        self.assertEqual(len(self.pack.error_patterns), 12)
        for name in (
            "부호실수",
            "조건누락",
            "선지함정",
            "시대착오",
            "용어혼동",
            "지문일치실패",
            "계산실수",
            "공식오용",
            "인과혼동",
            "그래프오독",
            "예외무시",
            "성급추론",
        ):
            self.assertIn(name, labels)

    def test_levels_and_blueprints(self) -> None:
        self.assertEqual(len(self.pack.levels["bands"]), 4)
        self.assertEqual(len(self.pack.blueprints), 6)
        self.assertEqual(len(self.pack.plan_templates), 4)

    def test_source_bank_untouched(self) -> None:
        official_src = ROOT / "data" / "bank" / "items" / "go-2026-2-kor.json"
        raw = json.loads(official_src.read_text(encoding="utf-8"))
        self.assertEqual(len(raw), 25)
        self.assertIsNone(raw[11]["stem"])
        self.assertTrue((ROOT / "data" / "bank" / "items" / "original" / "orig-math.json").is_file())


class TestLearner(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.user = load_sample()

    def test_sample_has_notes(self) -> None:
        notes = self.user.get("wrong_notes") or []
        self.assertGreaterEqual(len(notes), 3)
        self.assertEqual(self.user["id"], "u-demo")
        for note in notes:
            self.assertTrue(str(note["item_id"]).startswith("orig-"))
            self.assertTrue(note.get("auto_hint"))

    def test_notes_open(self) -> None:
        open_notes = notes_open(self.user)
        self.assertEqual(len(open_notes), 3)

    def test_hot_types_finds_math_poly(self) -> None:
        hot = hot_types(self.user)
        ids = [row["type_id"] for row in hot]
        self.assertIn("type-math-poly", ids)
        math = next(row for row in hot if row["type_id"] == "type-math-poly")
        self.assertGreaterEqual(math["misses"], 3)
        his_ids = [row["type_id"] for row in hot]
        self.assertNotIn("type-his-premodern", his_ids)

    def test_hot_patterns(self) -> None:
        pats = hot_patterns(self.user)
        self.assertGreaterEqual(len(pats), 2)
        pattern_ids = {p["pattern_id"] for p in pats}
        self.assertIn("pat-sign", pattern_ids)
        self.assertIn("pat-anachronism", pattern_ids)

    def test_type_stats_his_once(self) -> None:
        stats = self.user["type_stats"]
        his = next(s for s in stats if s["type_id"] == "type-his-premodern")
        self.assertEqual(his["misses"], 1)
        self.assertEqual(his["streak_wrong"], 1)


class TestEditions(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.pack = load_pack()

    def test_editions_2015_go_covers_2026(self) -> None:
        editions = load_editions()
        self.assertTrue(editions)
        ids = [e["id"] for e in editions]
        self.assertIn("2015-go", ids)
        ed = next(e for e in editions if e["id"] == "2015-go")
        self.assertEqual(ed["curriculum"], "2015")
        self.assertEqual(ed["valid_from"], 2021)
        self.assertEqual(ed["valid_to"], 2026)
        self.assertEqual(ed["current_for_year"], 2026)
        self.assertEqual(ed["level"], "고졸")
        packed = self.pack.editions
        self.assertEqual(len(packed), 1)
        self.assertEqual(packed[0]["id"], "2015-go")
        current = edition_for_year(2026)
        self.assertIsNotNone(current)
        assert current is not None
        self.assertEqual(current["id"], "2015-go")
        self.assertEqual(self.pack.meta.get("current_edition"), "2015-go")
        self.assertEqual(self.pack.meta.get("current_year"), 2026)

    def test_flatten_stamps_edition_fields(self) -> None:
        rows = flatten()
        self.assertEqual(len(rows), 119)
        for row in rows:
            self.assertEqual(row["edition_id"], "2015-go")
            self.assertEqual(row["curriculum"], "2015")
            self.assertEqual(row["valid_from"], 2021)
            self.assertEqual(row["valid_to"], 2026)

    def test_chapters_for_year_2020_empty(self) -> None:
        rows = chapters_for_year(2020)
        self.assertEqual(rows, [])
        self.assertIsNone(edition_for_year(2020))
        self.assertNotIn("2015-go", {c.get("edition_id") for c in rows})
        self.assertIsNone(chapter_id_for("다항식", 2020))

    def test_chapter_id_for_2026(self) -> None:
        self.assertEqual(chapter_id_for("다항식", 2026), "ch-math-poly")
        self.assertEqual(chapter_id_for("문법"), "ch-kor-grammar")

    def test_official_2021_his_chapter_id_null(self) -> None:
        his = [i for i in self.pack.items if i.get("subject_code") == "his" and i.get("year") == 2021]
        self.assertEqual(len(his), 50)
        for item in his:
            self.assertEqual(item["curriculum"], "2009", msg=item["id"])
            self.assertIsNone(item.get("chapter_id"), msg=item["id"])


if __name__ == "__main__":
    unittest.main()
