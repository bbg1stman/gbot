"""문항 난이도. 학생 밴드와 같은 네 말: 미달·경계·안정·여유.

- original ready: 필수. 네 값 중 하나. null 금지.
- official embargoed 슬롯: null (라이선스+태깅 전까지).
"""

from __future__ import annotations

from typing import Any, Optional

BANDS = ("미달", "경계", "안정", "여유")

_ADJACENT: dict[str, tuple[str, ...]] = {
    "미달": ("경계",),
    "경계": ("미달", "안정"),
    "안정": ("경계", "여유"),
    "여유": ("안정",),
}


def adjacent(band: str) -> tuple[str, ...]:
    """옆 밴드. 미달↔경계, 경계↔안정, 안정↔여유."""
    return _ADJACENT.get(str(band), ())


def infer_difficulty(item: dict[str, Any]) -> Optional[str]:
    """공식·엠바고는 None. 태그 없는 자작은 역할·번호로 추정한다."""
    if item.get("source") == "official" or item.get("status") == "embargoed":
        return None
    existing = item.get("difficulty")
    if existing in BANDS:
        return existing

    role = item.get("role")
    raw_number = item.get("number")
    try:
        number = int(raw_number) if raw_number is not None else None
    except (TypeError, ValueError):
        number = None
    iid = str(item.get("id") or "")

    if role == "diagnostic" and (
        number in (1, 2) or iid.endswith("-001") or iid.endswith("-002")
    ):
        return "미달"
    if role == "diagnostic" and number is not None and number >= 3:
        return "경계"
    if role == "drill":
        return "경계"
    if item.get("source") == "original":
        return "경계"
    return None
