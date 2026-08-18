"""Compile data/ + wiki/ into pack/ — the only folder the app reads.

Official slot JSON and original items stay the source of truth.
This module copies them and fills pack-only defaults. It never writes
official stems, choices, or answers.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from gbot import __version__
from gbot.appdata import load as load_app
from gbot.bank import load as load_bank
from gbot.chapters import chapter_index, compile_chapters, infer_chapter_id

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
WIKI_DIR = ROOT / "wiki"
PACK_DIR = ROOT / "pack"

Item = dict[str, Any]

# Axis → type_id. Seeded from diagnostic axes, not official questions.
TYPE_SPECS: list[dict[str, str]] = [
    {"id": "type-kor-speech", "subject_code": "kor", "axis": "화법작문", "label": "화법작문"},
    {"id": "type-kor-grammar", "subject_code": "kor", "axis": "문법", "label": "문법"},
    {"id": "type-kor-lit", "subject_code": "kor", "axis": "문학", "label": "문학"},
    {"id": "type-kor-reading", "subject_code": "kor", "axis": "독서", "label": "독서"},
    {"id": "type-math-poly", "subject_code": "math", "axis": "다항식", "label": "다항식"},
    {"id": "type-math-eqineq", "subject_code": "math", "axis": "방정식과부등식", "label": "방정식과부등식"},
    {"id": "type-math-geoeq", "subject_code": "math", "axis": "도형의방정식", "label": "도형의방정식"},
    {"id": "type-math-set", "subject_code": "math", "axis": "집합과명제", "label": "집합과명제"},
    {"id": "type-math-func", "subject_code": "math", "axis": "함수", "label": "함수"},
    {"id": "type-math-count", "subject_code": "math", "axis": "경우의수", "label": "경우의수"},
    {"id": "type-eng-vocab", "subject_code": "eng", "axis": "어휘", "label": "어휘"},
    {"id": "type-eng-life", "subject_code": "eng", "axis": "생활영어", "label": "생활영어"},
    {"id": "type-eng-read", "subject_code": "eng", "axis": "독해", "label": "독해"},
    {"id": "type-soc-happiness", "subject_code": "soc", "axis": "인간사회환경과행복", "label": "인간사회환경과행복"},
    {"id": "type-soc-nature", "subject_code": "soc", "axis": "자연환경과인간", "label": "자연환경과인간"},
    {"id": "type-soc-space", "subject_code": "soc", "axis": "생활공간과사회", "label": "생활공간과사회"},
    {"id": "type-soc-const", "subject_code": "soc", "axis": "인권보장과헌법", "label": "인권보장과헌법"},
    {"id": "type-soc-market", "subject_code": "soc", "axis": "시장경제와금융", "label": "시장경제와금융"},
    {"id": "type-soc-justice", "subject_code": "soc", "axis": "사회정의와불평등", "label": "사회정의와불평등"},
    {"id": "type-soc-culture", "subject_code": "soc", "axis": "문화와다양성", "label": "문화와다양성"},
    {"id": "type-soc-global", "subject_code": "soc", "axis": "세계화와평화", "label": "세계화와평화"},
    {"id": "type-soc-future", "subject_code": "soc", "axis": "미래와지속가능한삶", "label": "미래와지속가능한삶"},
    {"id": "type-sci-matter", "subject_code": "sci", "axis": "물질과규칙성", "label": "물질과규칙성"},
    {"id": "type-sci-system", "subject_code": "sci", "axis": "시스템과상호작용", "label": "시스템과상호작용"},
    {"id": "type-sci-change", "subject_code": "sci", "axis": "변화와다양성", "label": "변화와다양성"},
    {"id": "type-sci-energy", "subject_code": "sci", "axis": "환경과에너지", "label": "환경과에너지"},
    {"id": "type-his-premodern", "subject_code": "his", "axis": "전근대", "label": "전근대"},
    {"id": "type-his-modern", "subject_code": "his", "axis": "근대국민국가", "label": "근대국민국가"},
    {"id": "type-his-colonial", "subject_code": "his", "axis": "일제와민족운동", "label": "일제와민족운동"},
    {"id": "type-his-rok", "subject_code": "his", "axis": "대한민국의발전", "label": "대한민국의발전"},
]

ERROR_PATTERNS: list[dict[str, Any]] = [
    {
        "id": "pat-sign",
        "subject_code": None,
        "type_id": None,
        "label": "부호실수",
        "description": "플러스·마이너스나 부등식 방향을 반대로 쓰는 실수",
    },
    {
        "id": "pat-omit",
        "subject_code": None,
        "type_id": None,
        "label": "조건누락",
        "description": "문제의 조건·범위를 하나 빠뜨리고 푸는 실수",
    },
    {
        "id": "pat-trap",
        "subject_code": None,
        "type_id": None,
        "label": "선지함정",
        "description": "그럴듯한 오답 선지에 끌려 정답을 버리는 실수",
    },
    {
        "id": "pat-anachronism",
        "subject_code": None,
        "type_id": None,
        "label": "시대착오",
        "description": "사건·제도를 다른 시대에 두는 실수",
    },
    {
        "id": "pat-term",
        "subject_code": None,
        "type_id": None,
        "label": "용어혼동",
        "description": "비슷한 용어·개념을 바꿔 쓰는 실수",
    },
    {
        "id": "pat-passage",
        "subject_code": None,
        "type_id": None,
        "label": "지문일치실패",
        "description": "지문에 없는 내용을 있다고 읽거나 있는 내용을 빠뜨리는 실수",
    },
    {
        "id": "pat-calc",
        "subject_code": None,
        "type_id": None,
        "label": "계산실수",
        "description": "식은 맞았으나 산술에서 틀린 실수",
    },
    {
        "id": "pat-formula",
        "subject_code": None,
        "type_id": None,
        "label": "공식오용",
        "description": "공식·정의를 잘못된 상황에 적용하는 실수",
    },
    {
        "id": "pat-cause",
        "subject_code": None,
        "type_id": None,
        "label": "인과혼동",
        "description": "원인과 결과를 뒤집거나 상관을 인과로 읽는 실수",
    },
    {
        "id": "pat-graph",
        "subject_code": None,
        "type_id": None,
        "label": "그래프오독",
        "description": "축·단위·기울기를 잘못 읽어 그래프를 오해하는 실수",
    },
    {
        "id": "pat-exception",
        "subject_code": None,
        "type_id": None,
        "label": "예외무시",
        "description": "일반 규칙만 보고 예외·특수한 경우를 빠뜨리는 실수",
    },
    {
        "id": "pat-rush",
        "subject_code": None,
        "type_id": None,
        "label": "성급추론",
        "description": "근거가 부족한 채 결론을 먼저 내리는 실수",
    },
]

CONTENT_TABLES: dict[str, Any] = {
    "Item": {
        "type": "object",
        "description": "pack/items.json 한 행. 공식 슬롯은 stem/choices/answer가 null.",
        "required": ["id", "type", "source", "status", "subject_code"],
        "properties": {
            "id": {"type": "string"},
            "type": {"const": "item"},
            "source": {"enum": ["official", "original"]},
            "status": {"enum": ["embargoed", "ready"]},
            "kind": {"type": "string"},
            "subject": {"type": "string"},
            "subject_code": {"type": "string"},
            "type_id": {"type": ["string", "null"], "description": "types.json id. unit/skill에서 매핑"},
            "chapter_id": {"type": ["string", "null"], "description": "chapters.json id. unit/skill에서 매핑"},
            "trap_tags": {"type": "array", "items": {"type": "string"}, "default": []},
            "media": {
                "type": ["object", "null"],
                "properties": {
                    "kind": {"type": "string"},
                    "url": {"type": "string"},
                },
            },
            "stem": {"type": ["string", "null"]},
            "choices": {"type": ["array", "null"]},
            "answer": {"type": ["integer", "null"]},
            "explanation": {"type": ["string", "null"]},
        },
    },
    "Concept": {
        "type": "object",
        "description": "wiki/concepts/*.md 를 컴파일한 개념 카드",
        "required": ["id", "subject", "axis", "title", "body"],
        "properties": {
            "id": {"type": "string"},
            "subject": {"type": "string"},
            "subject_code": {"type": "string"},
            "axis": {"type": "string"},
            "title": {"type": "string"},
            "body": {"type": "string"},
        },
    },
    "Type": {
        "type": "object",
        "description": "진단 축에서 만든 채점 유형. 공식 문항이 아님",
        "required": ["id", "subject_code", "axis", "label", "description"],
        "properties": {
            "id": {"type": "string"},
            "subject_code": {"type": "string"},
            "axis": {"type": "string"},
            "label": {"type": "string"},
            "description": {"type": "string"},
        },
    },
    "Level": {
        "type": "object",
        "description": "pack/levels.json. 밴드와 합격 규칙",
    },
    "Blueprint": {
        "type": "object",
        "description": "과목 진단 설계. axes는 교육과정 단원/기능",
        "required": ["subject", "subject_code", "item_count", "axis", "axes"],
    },
    "PlanTemplate": {
        "type": "object",
        "description": "밴드별 주간 계획 템플릿",
        "required": ["band", "label", "focus", "daily_items"],
    },
    "ErrorPatternCatalog": {
        "type": "object",
        "description": "pack/error_patterns.json 공통 오답 패턴 목록",
        "required": ["id", "label", "description"],
        "properties": {
            "id": {"type": "string"},
            "subject_code": {"type": ["string", "null"]},
            "type_id": {"type": ["string", "null"]},
            "label": {"type": "string"},
            "description": {"type": "string"},
        },
    },
    "Chapter": {
        "type": "object",
        "description": "2015 고졸 검정고시 출제 범위 교과서 대단원/소단원",
        "required": ["id", "subject_code", "textbook", "number", "title", "parent_id", "axis", "type_id"],
        "properties": {
            "id": {"type": "string"},
            "subject_code": {"type": "string"},
            "textbook": {"type": "string"},
            "number": {"type": "string"},
            "title": {"type": "string"},
            "parent_id": {"type": ["string", "null"]},
            "axis": {"type": "string"},
            "type_id": {"type": ["string", "null"]},
        },
    },
}


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def _parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    meta: dict[str, str] = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].splitlines():
                if ":" not in line:
                    continue
                key, val = line.split(":", 1)
                meta[key.strip()] = val.strip()
            body = parts[2].lstrip("\n")
    return meta, body


def _title_from_body(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _section(body: str, heading: str) -> str:
    lines = body.splitlines()
    take = False
    buf: list[str] = []
    target = f"## {heading}"
    for line in lines:
        if line.strip() == target:
            take = True
            continue
        if take:
            if line.startswith("## "):
                break
            if line.strip():
                buf.append(line.strip())
    return " ".join(buf)


def axis_of(item: Item) -> Optional[str]:
    unit = item.get("unit")
    if unit:
        return unit
    skill = item.get("skill")
    if skill:
        return skill
    return None


def type_index() -> dict[tuple[str, str], str]:
    return {(t["subject_code"], t["axis"]): t["id"] for t in TYPE_SPECS}


def infer_type_id(item: Item, index: Optional[dict[tuple[str, str], str]] = None) -> Optional[str]:
    existing = item.get("type_id")
    if existing:
        return existing
    idx = index if index is not None else type_index()
    axis = axis_of(item)
    code = item.get("subject_code")
    if not axis or not code:
        return None
    return idx.get((code, axis))


def compile_concepts(wiki_dir: Optional[Path] = None) -> list[dict[str, Any]]:
    root = Path(wiki_dir) if wiki_dir is not None else WIKI_DIR
    concept_dir = root / "concepts"
    out: list[dict[str, Any]] = []
    if not concept_dir.is_dir():
        return out
    for path in sorted(concept_dir.glob("*.md")):
        if "템플릿" in path.name:
            continue
        text = path.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(text)
        axis = meta.get("axis") or path.stem
        title = _title_from_body(body, axis)
        cid = meta.get("id") or f"concept-{axis}"
        out.append(
            {
                "id": cid,
                "subject": meta.get("subject") or "",
                "subject_code": meta.get("subject_code") or "",
                "axis": axis,
                "title": title,
                "body": body.strip() + "\n",
            }
        )
    return out


def compile_types(concepts: Optional[list[dict[str, Any]]] = None) -> list[dict[str, str]]:
    by_axis = {(c.get("subject_code"), c.get("axis")): c for c in (concepts or [])}
    types: list[dict[str, str]] = []
    for spec in TYPE_SPECS:
        concept = by_axis.get((spec["subject_code"], spec["axis"]))
        desc = ""
        if concept:
            desc = _section(concept.get("body") or "", "정의")
        if not desc:
            desc = f"{spec['label']} 유형"
        types.append(
            {
                "id": spec["id"],
                "subject_code": spec["subject_code"],
                "axis": spec["axis"],
                "label": spec["label"],
                "description": desc,
            }
        )
    return types


def pack_item(
    item: Item,
    index: Optional[dict[tuple[str, str], str]] = None,
    ch_index: Optional[dict[tuple[str, str], str]] = None,
) -> Item:
    """Copy all fields and add pack defaults. Official stems stay null."""
    out = dict(item)
    out["type_id"] = infer_type_id(out, index)
    out["chapter_id"] = infer_chapter_id(out, ch_index)
    out.setdefault("trap_tags", [])
    if "media" not in out:
        out["media"] = None
    return out


def _runtime_schema(data_dir: Path) -> dict[str, Any]:
    path = data_dir / "app" / "schema.json"
    if path.is_file():
        return _read_json(path)
    return {}


def build_pack_schema(data_dir: Optional[Path] = None) -> dict[str, Any]:
    root = Path(data_dir) if data_dir is not None else DATA_DIR
    schema = dict(_runtime_schema(root))
    comment = schema.get("$comment", "")
    extra = " 앱은 pack/ 만 읽는다. 편집은 data/ + wiki/."
    if extra.strip() not in comment:
        schema["$comment"] = (comment + extra).strip()
    for name, table in CONTENT_TABLES.items():
        schema[name] = table
    return schema


def build_pack(
    pack_dir: Optional[Path] = None,
    data_dir: Optional[Path] = None,
    wiki_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Read sources and write pack/*. Returns meta."""
    dest = Path(pack_dir) if pack_dir is not None else PACK_DIR
    data = Path(data_dir) if data_dir is not None else DATA_DIR
    wiki = Path(wiki_dir) if wiki_dir is not None else WIKI_DIR
    dest.mkdir(parents=True, exist_ok=True)

    bank = load_bank(data / "bank")
    app = load_app(data)

    concepts = compile_concepts(wiki)
    types = compile_types(concepts)
    chapters = compile_chapters()
    index = type_index()
    ch_index = chapter_index(chapters)
    items = [pack_item(item, index, ch_index) for item in bank.items]

    embargoed = sum(1 for i in items if i.get("status") == "embargoed")
    ready = sum(1 for i in items if i.get("status") == "ready")

    levels = dict(app.levels)
    blueprints = list(app.subjects.get("blueprints", []))
    plan_templates = list(app.templates.get("templates", []))
    # runtime tables (ItemStat, Evaluation, WrongNote, ...) ride along
    schema = build_pack_schema(data)
    sample = _read_json(data / "app" / "sample_user.json")

    meta = {
        "version": __version__,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "counts": {
            "items": len(items),
            "embargoed": embargoed,
            "ready": ready,
            "concepts": len(concepts),
            "types": len(types),
            "chapters": len(chapters),
            "error_patterns": len(ERROR_PATTERNS),
            "blueprints": len(blueprints),
            "plan_templates": len(plan_templates),
            "levels": len(levels.get("bands", [])),
        },
    }

    _write_json(dest / "meta.json", meta)
    _write_json(dest / "items.json", items)
    _write_json(dest / "concepts.json", concepts)
    _write_json(dest / "types.json", types)
    _write_json(dest / "chapters.json", chapters)
    _write_json(dest / "levels.json", levels)
    _write_json(dest / "blueprints.json", blueprints)
    _write_json(dest / "plan_templates.json", plan_templates)
    _write_json(dest / "error_patterns.json", ERROR_PATTERNS)
    _write_json(dest / "schema.json", schema)
    _write_json(dest / "sample_learner.json", sample)
    return meta


class Pack:
    def __init__(self) -> None:
        self.meta: dict[str, Any] = {}
        self.items: list[Item] = []
        self.concepts: list[dict[str, Any]] = []
        self.types: list[dict[str, Any]] = []
        self.chapters: list[dict[str, Any]] = []
        self.levels: dict[str, Any] = {}
        self.blueprints: list[dict[str, Any]] = []
        self.plan_templates: list[dict[str, Any]] = []
        self.error_patterns: list[dict[str, Any]] = []
        self.schema: dict[str, Any] = {}
        self.sample_learner: dict[str, Any] = {}
        self._by_id: dict[str, Item] = {}
        self._loaded = False

    def load(self, pack_dir: Optional[Path] = None) -> "Pack":
        root = Path(pack_dir) if pack_dir is not None else PACK_DIR
        self.meta = _read_json(root / "meta.json")
        self.items = _read_json(root / "items.json")
        self.concepts = _read_json(root / "concepts.json")
        self.types = _read_json(root / "types.json")
        ch = root / "chapters.json"
        self.chapters = _read_json(ch) if ch.is_file() else []
        self.levels = _read_json(root / "levels.json")
        self.blueprints = _read_json(root / "blueprints.json")
        self.plan_templates = _read_json(root / "plan_templates.json")
        ep = root / "error_patterns.json"
        self.error_patterns = _read_json(ep) if ep.is_file() else []
        self.schema = _read_json(root / "schema.json")
        sample = root / "sample_learner.json"
        self.sample_learner = _read_json(sample) if sample.is_file() else {}
        self._by_id = {item["id"]: item for item in self.items}
        self._loaded = True
        return self

    def get(self, id: str) -> Optional[Item]:
        if not self._loaded:
            self.load()
        return self._by_id.get(id)


_PACK = Pack()


def load_pack(pack_dir: Optional[Path] = None) -> Pack:
    return _PACK.load(pack_dir)
