"""교육과정 edition에 묶인 고졸 검정고시 교과서 챕터 트리.

단원 트리는 edition이다. 지금은 2015-go (2015 개정, 2021–2026)만 둔다.
2022 트리는 만들지 않는다. 공식 기출 원문은 여기에 없다.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

Chapter = dict[str, Any]
Edition = dict[str, Any]

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM_DIR = ROOT / "data" / "curriculum"
DEFAULT_YEAR = 2026
DEFAULT_EDITION_ID = "2015-go"

# 대단원. children 은 소단원 (optional).
# axis 는 문항 unit/skill 과 같은 문자열. title 은 교과서 표기.
CHAPTER_TREE: list[dict[str, Any]] = [
    {
        "id": "ch-kor-speech",
        "subject_code": "kor",
        "textbook": "국어",
        "number": "Ⅰ",
        "title": "화법과 작문",
        "parent_id": None,
        "axis": "화법작문",
        "type_id": "type-kor-speech",
        "children": [
            {"id": "ch-kor-speech-talk", "number": "1", "title": "화법", "axis": "화법"},
            {"id": "ch-kor-speech-write", "number": "2", "title": "작문", "axis": "작문"},
        ],
    },
    {
        "id": "ch-kor-grammar",
        "subject_code": "kor",
        "textbook": "국어",
        "number": "Ⅱ",
        "title": "문법",
        "parent_id": None,
        "axis": "문법",
        "type_id": "type-kor-grammar",
        "children": [
            {"id": "ch-kor-grammar-phon", "number": "1", "title": "음운", "axis": "음운"},
            {"id": "ch-kor-grammar-word", "number": "2", "title": "단어와 품사", "axis": "단어와품사"},
            {"id": "ch-kor-grammar-sent", "number": "3", "title": "문장", "axis": "문장"},
            {"id": "ch-kor-grammar-norm", "number": "4", "title": "국어 규범", "axis": "국어규범"},
        ],
    },
    {
        "id": "ch-kor-lit",
        "subject_code": "kor",
        "textbook": "국어",
        "number": "Ⅲ",
        "title": "문학",
        "parent_id": None,
        "axis": "문학",
        "type_id": "type-kor-lit",
        "children": [
            {"id": "ch-kor-lit-poem", "number": "1", "title": "현대시", "axis": "현대시"},
            {"id": "ch-kor-lit-novel", "number": "2", "title": "현대소설", "axis": "현대소설"},
            {"id": "ch-kor-lit-classic", "number": "3", "title": "고전문학", "axis": "고전문학"},
            {"id": "ch-kor-lit-genre", "number": "4", "title": "갈래와 표현", "axis": "갈래와표현"},
        ],
    },
    {
        "id": "ch-kor-reading",
        "subject_code": "kor",
        "textbook": "국어",
        "number": "Ⅳ",
        "title": "독서",
        "parent_id": None,
        "axis": "독서",
        "type_id": "type-kor-reading",
        "children": [
            {"id": "ch-kor-reading-fact", "number": "1", "title": "사실적 이해", "axis": "사실적이해"},
            {"id": "ch-kor-reading-infer", "number": "2", "title": "추론적 이해", "axis": "추론적이해"},
            {"id": "ch-kor-reading-crit", "number": "3", "title": "비판적 이해", "axis": "비판적이해"},
        ],
    },
    {
        "id": "ch-math-poly",
        "subject_code": "math",
        "textbook": "수학",
        "number": "Ⅰ",
        "title": "다항식",
        "parent_id": None,
        "axis": "다항식",
        "type_id": "type-math-poly",
        "children": [
            {"id": "ch-math-poly-ops", "number": "1", "title": "다항식의 연산", "axis": "다항식의연산"},
            {"id": "ch-math-poly-factor", "number": "2", "title": "나머지정리와 인수분해", "axis": "나머지정리와인수분해"},
        ],
    },
    {
        "id": "ch-math-eqineq",
        "subject_code": "math",
        "textbook": "수학",
        "number": "Ⅱ",
        "title": "방정식과 부등식",
        "parent_id": None,
        "axis": "방정식과부등식",
        "type_id": "type-math-eqineq",
        "children": [
            {"id": "ch-math-eqineq-complex", "number": "1", "title": "복소수와 이차방정식", "axis": "복소수와이차방정식"},
            {"id": "ch-math-eqineq-quad", "number": "2", "title": "이차방정식과 이차함수", "axis": "이차방정식과이차함수"},
            {"id": "ch-math-eqineq-eq", "number": "3", "title": "여러 가지 방정식", "axis": "여러가지방정식"},
            {"id": "ch-math-eqineq-ineq", "number": "4", "title": "여러 가지 부등식", "axis": "여러가지부등식"},
        ],
    },
    {
        "id": "ch-math-geoeq",
        "subject_code": "math",
        "textbook": "수학",
        "number": "Ⅲ",
        "title": "도형의 방정식",
        "parent_id": None,
        "axis": "도형의방정식",
        "type_id": "type-math-geoeq",
        "children": [
            {"id": "ch-math-geoeq-coord", "number": "1", "title": "평면좌표", "axis": "평면좌표"},
            {"id": "ch-math-geoeq-line", "number": "2", "title": "직선의 방정식", "axis": "직선의방정식"},
            {"id": "ch-math-geoeq-circle", "number": "3", "title": "원의 방정식", "axis": "원의방정식"},
            {"id": "ch-math-geoeq-move", "number": "4", "title": "도형의 이동", "axis": "도형의이동"},
        ],
    },
    {
        "id": "ch-math-set",
        "subject_code": "math",
        "textbook": "수학",
        "number": "Ⅳ",
        "title": "집합과 명제",
        "parent_id": None,
        "axis": "집합과명제",
        "type_id": "type-math-set",
        "children": [
            {"id": "ch-math-set-set", "number": "1", "title": "집합", "axis": "집합"},
            {"id": "ch-math-set-prop", "number": "2", "title": "명제", "axis": "명제"},
        ],
    },
    {
        "id": "ch-math-func",
        "subject_code": "math",
        "textbook": "수학",
        "number": "Ⅴ",
        "title": "함수",
        "parent_id": None,
        "axis": "함수",
        "type_id": "type-math-func",
        "children": [
            {"id": "ch-math-func-graph", "number": "1", "title": "함수의 뜻과 그래프", "axis": "함수의뜻과그래프"},
            {"id": "ch-math-func-rat", "number": "2", "title": "유리함수와 무리함수", "axis": "유리함수와무리함수"},
        ],
    },
    {
        "id": "ch-math-count",
        "subject_code": "math",
        "textbook": "수학",
        "number": "Ⅵ",
        "title": "경우의 수",
        "parent_id": None,
        "axis": "경우의수",
        "type_id": "type-math-count",
        "children": [
            {"id": "ch-math-count-sumprod", "number": "1", "title": "합의 법칙과 곱의 법칙", "axis": "합의법칙과곱의법칙"},
            {"id": "ch-math-count-permcomb", "number": "2", "title": "순열과 조합", "axis": "순열과조합"},
        ],
    },
    {
        "id": "ch-eng-vocab",
        "subject_code": "eng",
        "textbook": "영어",
        "number": "Ⅰ",
        "title": "어휘",
        "parent_id": None,
        "axis": "어휘",
        "type_id": "type-eng-vocab",
        "children": [
            {"id": "ch-eng-vocab-syn", "number": "1", "title": "유의어와 반의어", "axis": "유의어와반의어"},
            {"id": "ch-eng-vocab-confuse", "number": "2", "title": "혼동어", "axis": "혼동어"},
            {"id": "ch-eng-vocab-phrasal", "number": "3", "title": "구동사", "axis": "구동사"},
        ],
    },
    {
        "id": "ch-eng-life",
        "subject_code": "eng",
        "textbook": "영어",
        "number": "Ⅱ",
        "title": "생활 영어",
        "parent_id": None,
        "axis": "생활영어",
        "type_id": "type-eng-life",
        "children": [
            {"id": "ch-eng-life-daily", "number": "1", "title": "일상 대화", "axis": "일상대화"},
            {"id": "ch-eng-life-request", "number": "2", "title": "요청과 제안", "axis": "요청과제안"},
            {"id": "ch-eng-life-guide", "number": "3", "title": "안내와 설명", "axis": "안내와설명"},
        ],
    },
    {
        "id": "ch-eng-read",
        "subject_code": "eng",
        "textbook": "영어",
        "number": "Ⅲ",
        "title": "독해",
        "parent_id": None,
        "axis": "독해",
        "type_id": "type-eng-read",
        "children": [
            {"id": "ch-eng-read-topic", "number": "1", "title": "주제", "axis": "주제"},
            {"id": "ch-eng-read-detail", "number": "2", "title": "세부 사항", "axis": "세부사항"},
            {"id": "ch-eng-read-blank", "number": "3", "title": "빈칸 추론", "axis": "빈칸추론"},
        ],
    },
    {
        "id": "ch-soc-happiness",
        "subject_code": "soc",
        "textbook": "통합사회",
        "number": "Ⅰ",
        "title": "인간, 사회, 환경과 행복",
        "parent_id": None,
        "axis": "인간사회환경과행복",
        "type_id": "type-soc-happiness",
        "children": [
            {"id": "ch-soc-happiness-view", "number": "1", "title": "인간, 사회, 환경을 보는 눈", "axis": "인간사회환경을보는눈"},
            {"id": "ch-soc-happiness-mean", "number": "2", "title": "행복의 의미와 기준", "axis": "행복의의미와기준"},
            {"id": "ch-soc-happiness-cond", "number": "3", "title": "행복한 삶을 실현하기 위한 조건", "axis": "행복한삶의조건"},
        ],
    },
    {
        "id": "ch-soc-nature",
        "subject_code": "soc",
        "textbook": "통합사회",
        "number": "Ⅱ",
        "title": "자연환경과 인간",
        "parent_id": None,
        "axis": "자연환경과인간",
        "type_id": "type-soc-nature",
        "children": [
            {"id": "ch-soc-nature-life", "number": "1", "title": "자연환경과 인간 생활", "axis": "자연환경과인간생활"},
            {"id": "ch-soc-nature-view", "number": "2", "title": "자연에 대한 다양한 관점", "axis": "자연에대한다양한관점"},
            {"id": "ch-soc-nature-env", "number": "3", "title": "환경 문제의 해결", "axis": "환경문제의해결"},
        ],
    },
    {
        "id": "ch-soc-space",
        "subject_code": "soc",
        "textbook": "통합사회",
        "number": "Ⅲ",
        "title": "생활공간과 사회",
        "parent_id": None,
        "axis": "생활공간과사회",
        "type_id": "type-soc-space",
        "children": [
            {"id": "ch-soc-space-urban", "number": "1", "title": "산업화와 도시화", "axis": "산업화와도시화"},
            {"id": "ch-soc-space-info", "number": "2", "title": "교통·통신의 발달과 정보화", "axis": "교통과정보화"},
            {"id": "ch-soc-space-change", "number": "3", "title": "생활공간의 변화", "axis": "생활공간의변화"},
        ],
    },
    {
        "id": "ch-soc-const",
        "subject_code": "soc",
        "textbook": "통합사회",
        "number": "Ⅳ",
        "title": "인권 보장과 헌법",
        "parent_id": None,
        "axis": "인권보장과헌법",
        "type_id": "type-soc-const",
        "children": [
            {"id": "ch-soc-const-rights", "number": "1", "title": "인권의 의미와 변화", "axis": "인권의의미와변화"},
            {"id": "ch-soc-const-basic", "number": "2", "title": "헌법과 기본권", "axis": "헌법과기본권"},
            {"id": "ch-soc-const-issue", "number": "3", "title": "인권 문제와 해결", "axis": "인권문제와해결"},
        ],
    },
    {
        "id": "ch-soc-market",
        "subject_code": "soc",
        "textbook": "통합사회",
        "number": "Ⅴ",
        "title": "시장경제와 금융",
        "parent_id": None,
        "axis": "시장경제와금융",
        "type_id": "type-soc-market",
        "children": [
            {"id": "ch-soc-market-cap", "number": "1", "title": "자본주의의 전개", "axis": "자본주의의전개"},
            {"id": "ch-soc-market-econ", "number": "2", "title": "시장경제의 이해", "axis": "시장경제의이해"},
            {"id": "ch-soc-market-trade", "number": "3", "title": "국제 분업과 무역", "axis": "국제분업과무역"},
            {"id": "ch-soc-market-fin", "number": "4", "title": "금융 생활", "axis": "금융생활"},
        ],
    },
    {
        "id": "ch-soc-justice",
        "subject_code": "soc",
        "textbook": "통합사회",
        "number": "Ⅵ",
        "title": "사회 정의와 불평등",
        "parent_id": None,
        "axis": "사회정의와불평등",
        "type_id": "type-soc-justice",
        "children": [
            {"id": "ch-soc-justice-mean", "number": "1", "title": "정의의 의미", "axis": "정의의의미"},
            {"id": "ch-soc-justice-view", "number": "2", "title": "다양한 정의관", "axis": "다양한정의관"},
            {"id": "ch-soc-justice-ineq", "number": "3", "title": "사회 불평등과 해결", "axis": "사회불평등과해결"},
        ],
    },
    {
        "id": "ch-soc-culture",
        "subject_code": "soc",
        "textbook": "통합사회",
        "number": "Ⅶ",
        "title": "문화와 다양성",
        "parent_id": None,
        "axis": "문화와다양성",
        "type_id": "type-soc-culture",
        "children": [
            {"id": "ch-soc-culture-world", "number": "1", "title": "세계의 다양성", "axis": "세계의다양성"},
            {"id": "ch-soc-culture-mean", "number": "2", "title": "문화의 의미와 특징", "axis": "문화의의미와특징"},
            {"id": "ch-soc-culture-change", "number": "3", "title": "문화 변동과 세계화", "axis": "문화변동과세계화"},
        ],
    },
    {
        "id": "ch-soc-global",
        "subject_code": "soc",
        "textbook": "통합사회",
        "number": "Ⅷ",
        "title": "세계화와 평화",
        "parent_id": None,
        "axis": "세계화와평화",
        "type_id": "type-soc-global",
        "children": [
            {"id": "ch-soc-global-aspect", "number": "1", "title": "세계화의 양상", "axis": "세계화의양상"},
            {"id": "ch-soc-global-actor", "number": "2", "title": "국제 사회의 행위 주체", "axis": "국제사회의행위주체"},
            {"id": "ch-soc-global-peace", "number": "3", "title": "평화와 공존", "axis": "평화와공존"},
        ],
    },
    {
        "id": "ch-soc-future",
        "subject_code": "soc",
        "textbook": "통합사회",
        "number": "Ⅸ",
        "title": "미래와 지속가능한 삶",
        "parent_id": None,
        "axis": "미래와지속가능한삶",
        "type_id": "type-soc-future",
        "children": [
            {"id": "ch-soc-future-pop", "number": "1", "title": "인구 문제", "axis": "인구문제"},
            {"id": "ch-soc-future-sd", "number": "2", "title": "지속가능한 발전", "axis": "지속가능한발전"},
            {"id": "ch-soc-future-citizen", "number": "3", "title": "세계시민과 미래", "axis": "세계시민과미래"},
        ],
    },
    {
        "id": "ch-sci-matter",
        "subject_code": "sci",
        "textbook": "통합과학",
        "number": "Ⅰ",
        "title": "물질과 규칙성",
        "parent_id": None,
        "axis": "물질과규칙성",
        "type_id": "type-sci-matter",
        "children": [
            {"id": "ch-sci-matter-bond", "number": "1", "title": "물질의 규칙성과 결합", "axis": "물질의규칙성과결합"},
            {"id": "ch-sci-matter-comp", "number": "2", "title": "자연의 구성 물질", "axis": "자연의구성물질"},
            {"id": "ch-sci-matter-mech", "number": "3", "title": "역학적 시스템", "axis": "역학적시스템"},
        ],
    },
    {
        "id": "ch-sci-system",
        "subject_code": "sci",
        "textbook": "통합과학",
        "number": "Ⅱ",
        "title": "시스템과 상호작용",
        "parent_id": None,
        "axis": "시스템과상호작용",
        "type_id": "type-sci-system",
        "children": [
            {"id": "ch-sci-system-earth", "number": "1", "title": "지구 시스템", "axis": "지구시스템"},
            {"id": "ch-sci-system-life", "number": "2", "title": "생명 시스템", "axis": "생명시스템"},
        ],
    },
    {
        "id": "ch-sci-change",
        "subject_code": "sci",
        "textbook": "통합과학",
        "number": "Ⅲ",
        "title": "변화와 다양성",
        "parent_id": None,
        "axis": "변화와다양성",
        "type_id": "type-sci-change",
        "children": [
            {"id": "ch-sci-change-chem", "number": "1", "title": "화학 변화", "axis": "화학변화"},
            {"id": "ch-sci-change-bio", "number": "2", "title": "생물다양성과 유지", "axis": "생물다양성과유지"},
        ],
    },
    {
        "id": "ch-sci-energy",
        "subject_code": "sci",
        "textbook": "통합과학",
        "number": "Ⅳ",
        "title": "환경과 에너지",
        "parent_id": None,
        "axis": "환경과에너지",
        "type_id": "type-sci-energy",
        "children": [
            {"id": "ch-sci-energy-eco", "number": "1", "title": "생태계와 환경", "axis": "생태계와환경"},
            {"id": "ch-sci-energy-power", "number": "2", "title": "에너지와 환경", "axis": "에너지와환경"},
        ],
    },
    {
        "id": "ch-his-premodern",
        "subject_code": "his",
        "textbook": "한국사",
        "number": "Ⅰ",
        "title": "전근대",
        "parent_id": None,
        "axis": "전근대",
        "type_id": "type-his-premodern",
        "children": [
            {"id": "ch-his-premodern-ancient", "number": "1", "title": "고대 국가의 형성과 발전", "axis": "고대사"},
            {"id": "ch-his-premodern-goryeo", "number": "2", "title": "고려의 성립과 변천", "axis": "고려사"},
            {"id": "ch-his-premodern-joseon", "number": "3", "title": "조선의 성립과 발전", "axis": "조선사"},
            {"id": "ch-his-premodern-late", "number": "4", "title": "조선 후기의 변화", "axis": "조선후기"},
        ],
    },
    {
        "id": "ch-his-modern",
        "subject_code": "his",
        "textbook": "한국사",
        "number": "Ⅱ",
        "title": "근대 국민국가",
        "parent_id": None,
        "axis": "근대국민국가",
        "type_id": "type-his-modern",
        "children": [
            {"id": "ch-his-modern-open", "number": "1", "title": "개항과 조선의 대응", "axis": "개항"},
            {"id": "ch-his-modern-reform", "number": "2", "title": "개화 운동과 근대적 개혁", "axis": "개화와개혁"},
            {"id": "ch-his-modern-nation", "number": "3", "title": "구국 민족 운동", "axis": "구국민족운동"},
        ],
    },
    {
        "id": "ch-his-colonial",
        "subject_code": "his",
        "textbook": "한국사",
        "number": "Ⅲ",
        "title": "일제와 민족운동",
        "parent_id": None,
        "axis": "일제와민족운동",
        "type_id": "type-his-colonial",
        "children": [
            {"id": "ch-his-colonial-rule", "number": "1", "title": "일제 식민 통치", "axis": "일제식민통치"},
            {"id": "ch-his-colonial-samil", "number": "2", "title": "3·1 운동과 임시 정부", "axis": "삼일운동과임정"},
            {"id": "ch-his-colonial-resist", "number": "3", "title": "다양한 민족 운동", "axis": "다양한민족운동"},
        ],
    },
    {
        "id": "ch-his-rok",
        "subject_code": "his",
        "textbook": "한국사",
        "number": "Ⅳ",
        "title": "대한민국의 발전",
        "parent_id": None,
        "axis": "대한민국의발전",
        "type_id": "type-his-rok",
        "children": [
            {"id": "ch-his-rok-found", "number": "1", "title": "대한민국 수립과 6·25 전쟁", "axis": "정부수립과전쟁"},
            {"id": "ch-his-rok-demo", "number": "2", "title": "민주주의의 시련과 발전", "axis": "민주주의발전"},
            {"id": "ch-his-rok-econ", "number": "3", "title": "경제 성장과 사회 변화", "axis": "경제성장"},
            {"id": "ch-his-rok-unify", "number": "4", "title": "통일을 위한 노력", "axis": "통일노력"},
        ],
    },
]

_BASE_FIELDS = ("id", "subject_code", "textbook", "number", "title", "parent_id", "axis", "type_id")
_EDITION_FIELDS = ("edition_id", "curriculum", "valid_from", "valid_to")
_FIELDS = _BASE_FIELDS + _EDITION_FIELDS


def load_editions(path: Optional[Path] = None) -> list[Edition]:
    """Load data/curriculum/editions.json."""
    src = Path(path) if path is not None else CURRICULUM_DIR / "editions.json"
    if not src.is_file():
        return []
    with src.open(encoding="utf-8") as f:
        data = json.load(f)
    return [row for row in data if isinstance(row, dict)]


def _edition_by_id(edition_id: str) -> Optional[Edition]:
    for ed in load_editions():
        if ed.get("id") == edition_id:
            return ed
    return None


def edition_for_year(year: int) -> Optional[Edition]:
    """Edition covering year (valid_from <= year <= valid_to). Prefer current_for_year."""
    year_i = int(year)
    hits: list[Edition] = []
    for ed in load_editions():
        vf, vt = ed.get("valid_from"), ed.get("valid_to")
        if vf is not None and year_i < int(vf):
            continue
        if vt is not None and year_i > int(vt):
            continue
        hits.append(ed)
    if not hits:
        return None
    for ed in hits:
        if ed.get("current_for_year") == year_i:
            return ed
    return hits[0]


def edition_for_curriculum(
    curriculum: str,
    year: Optional[int] = None,
) -> Optional[Edition]:
    """Edition whose curriculum matches. If year is set, it must also cover that year."""
    curr = str(curriculum)
    hits = [ed for ed in load_editions() if str(ed.get("curriculum")) == curr]
    if year is not None:
        year_i = int(year)
        covered = []
        for ed in hits:
            vf, vt = ed.get("valid_from"), ed.get("valid_to")
            if vf is not None and year_i < int(vf):
                continue
            if vt is not None and year_i > int(vt):
                continue
            covered.append(ed)
        hits = covered
    if not hits:
        return None
    if year is not None:
        for ed in hits:
            if ed.get("current_for_year") == int(year):
                return ed
    return hits[0]


def edition_for_item(item: dict[str, Any]) -> Optional[Edition]:
    """Resolve edition from item.curriculum / item.year / default 2026.

    Official 2021 한국사 (curriculum=2009) has no edition yet → None.
    """
    curr = item.get("curriculum")
    raw_year = item.get("year")
    year: Optional[int]
    try:
        year = int(raw_year) if raw_year is not None else None
    except (TypeError, ValueError):
        year = None
    if curr:
        return edition_for_curriculum(str(curr), year)
    return edition_for_year(year if year is not None else DEFAULT_YEAR)


def _stamp(edition: Optional[Edition]) -> dict[str, Any]:
    ed = edition or _edition_by_id(DEFAULT_EDITION_ID) or {}
    return {
        "edition_id": ed.get("id") or DEFAULT_EDITION_ID,
        "curriculum": ed.get("curriculum") or "2015",
        "valid_from": ed.get("valid_from"),
        "valid_to": ed.get("valid_to"),
    }


def flatten(
    tree: Optional[list[dict[str, Any]]] = None,
    edition: Optional[Edition] = None,
) -> list[Chapter]:
    """Flatten 대단원 + 소단원 and stamp edition_id / curriculum / valid_from / valid_to."""
    spec_tree = tree if tree is not None else CHAPTER_TREE
    stamp = _stamp(edition if edition is not None else _edition_by_id(DEFAULT_EDITION_ID))
    out: list[Chapter] = []
    for spec in spec_tree:
        row = {key: spec[key] for key in _BASE_FIELDS}
        row.update(stamp)
        out.append(row)
        for child in spec.get("children") or []:
            out.append(
                {
                    "id": child["id"],
                    "subject_code": spec["subject_code"],
                    "textbook": spec["textbook"],
                    "number": child["number"],
                    "title": child["title"],
                    "parent_id": spec["id"],
                    "axis": child["axis"],
                    "type_id": spec["type_id"],
                    **stamp,
                }
            )
    return out


def _load_extra_chapter_files() -> list[Chapter]:
    """Future editions live in data/curriculum/chapters-<id>.json. 2015-go stays in CHAPTER_TREE."""
    extra: list[Chapter] = []
    if not CURRICULUM_DIR.is_dir():
        return extra
    for path in sorted(CURRICULUM_DIR.glob("chapters-*.json")):
        eid = path.name[len("chapters-") : -len(".json")]
        if eid == DEFAULT_EDITION_ID:
            continue
        ed = _edition_by_id(eid)
        if not ed:
            continue
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list) or not data:
            continue
        first = data[0]
        if isinstance(first, dict) and "children" in first:
            extra.extend(flatten(data, ed))
        elif isinstance(first, dict):
            stamp = _stamp(ed)
            for row in data:
                if isinstance(row, dict):
                    extra.append({**row, **stamp})
    return extra


def compile_chapters() -> list[Chapter]:
    """All chapter rows from every known edition (currently 2015-go only)."""
    rows = flatten(CHAPTER_TREE, _edition_by_id(DEFAULT_EDITION_ID))
    rows.extend(_load_extra_chapter_files())
    return rows


def chapters_for_year(year: int) -> list[Chapter]:
    """Chapters whose edition covers year. 2020 → empty (2015-go starts 2021)."""
    ed = edition_for_year(year)
    if not ed:
        return []
    eid = ed.get("id")
    return [c for c in compile_chapters() if c.get("edition_id") == eid]


def chapter_id_for(axis: str, year: int = DEFAULT_YEAR, subject_code: Optional[str] = None) -> Optional[str]:
    """chapter_id for an axis in the edition that covers year. Prefer 대단원."""
    rows = chapters_for_year(year)
    matches = [
        c
        for c in rows
        if c.get("axis") == axis and (subject_code is None or c.get("subject_code") == subject_code)
    ]
    if not matches:
        return None
    tops = [c for c in matches if not c.get("parent_id")]
    return (tops or matches)[0]["id"]


def chapter_index(
    chapters: Optional[list[Chapter]] = None,
    year: Optional[int] = None,
    edition_id: Optional[str] = None,
) -> dict[tuple[str, str], str]:
    """(subject_code, axis) → chapter_id. 소단원 axis 도 포함."""
    if chapters is not None:
        rows = list(chapters)
    elif edition_id:
        rows = [c for c in compile_chapters() if c.get("edition_id") == edition_id]
    elif year is not None:
        rows = chapters_for_year(year)
    else:
        rows = compile_chapters()
    return {(c["subject_code"], c["axis"]): c["id"] for c in rows}


def chapter_by_type_id(
    chapters: Optional[list[Chapter]] = None,
    year: Optional[int] = None,
    edition_id: Optional[str] = None,
) -> dict[str, str]:
    """type_id → 대단원 chapter_id."""
    if chapters is not None:
        rows = list(chapters)
    elif edition_id:
        rows = [c for c in compile_chapters() if c.get("edition_id") == edition_id]
    elif year is not None:
        rows = chapters_for_year(year)
    else:
        rows = compile_chapters()
    return {
        c["type_id"]: c["id"]
        for c in rows
        if c.get("type_id") and not c.get("parent_id")
    }


def infer_chapter_id(
    item: dict[str, Any],
    index: Optional[dict[tuple[str, str], str]] = None,
    type_map: Optional[dict[str, str]] = None,
) -> Optional[str]:
    """Map item unit/skill (or type_id) to a chapter id in the item's edition.

    Uses item.curriculum / item.year / default 2026. Official slots stay null
    when they have no axis. Official 2021 한국사 (curriculum=2009) stays null
    because there is no 2009 edition yet.
    """
    existing = item.get("chapter_id")
    if existing:
        return existing
    edition = edition_for_item(item)
    if not edition:
        return None
    eid = edition.get("id")
    scoped = [c for c in compile_chapters() if c.get("edition_id") == eid]
    idx = {(c["subject_code"], c["axis"]): c["id"] for c in scoped}
    if index is not None:
        # keep caller index only for keys that exist in this edition
        for key, cid in index.items():
            if any(c["id"] == cid and c.get("edition_id") == eid for c in scoped):
                idx[key] = cid
    axis = item.get("unit") or item.get("skill")
    code = item.get("subject_code")
    if axis and code:
        found = idx.get((code, str(axis)))
        if found:
            return found
    tid = item.get("type_id")
    if tid:
        tmap = {c["type_id"]: c["id"] for c in scoped if c.get("type_id") and not c.get("parent_id")}
        if type_map is not None:
            for key, cid in type_map.items():
                if any(c["id"] == cid and c.get("edition_id") == eid for c in scoped):
                    tmap[key] = cid
        return tmap.get(tid)
    return None
