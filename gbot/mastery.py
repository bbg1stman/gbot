"""칸 숙달 단계. 숙달·완료 문항은 새 문제 칸에서 뺀다."""

from __future__ import annotations

from typing import Any, Optional

Learner = dict[str, Any]
ItemStat = dict[str, Any]

MASTERY_ORDER = ("미시도", "익숙", "숙달", "완료")
DONE_LEVELS = {"숙달", "완료"}


def _rows(user: Learner, *keys: str) -> list[dict[str, Any]]:
    for key in keys:
        rows = user.get(key)
        if isinstance(rows, list):
            return [r for r in rows if isinstance(r, dict)]
    return []


def mastery_of(stat: Optional[dict[str, Any]]) -> str:
    """미시도 | 익숙 | 숙달 | 완료. 저장된 mastery는 쓰지 않고 숫자로 다시 계산."""
    if not stat:
        return "미시도"
    attempts = int(stat.get("attempts") or 0)
    if attempts <= 0:
        return "미시도"
    misses = int(stat.get("misses") or 0)
    streak_wrong = int(stat.get("streak_wrong") or 0)
    last_correct = stat.get("last_correct")
    ease = stat.get("ease")
    if ease is None:
        ease = (attempts - misses) / attempts
    ease_f = float(ease)
    mastered = (
        attempts >= 2
        and streak_wrong == 0
        and last_correct is True
        and ease_f >= 0.8
    )
    if mastered and attempts >= 3 and misses == 0:
        return "완료"
    if mastered:
        return "숙달"
    return "익숙"


def is_done(stat: Optional[dict[str, Any]]) -> bool:
    """숙달 또는 완료."""
    return mastery_of(stat) in DONE_LEVELS


def item_mastery_map(user: Learner) -> dict[str, str]:
    """item_id → mastery. 저장 ItemStat이 있으면 그걸 쓰고, 없으면 시도에서 파생."""
    stored = _rows(user, "item_stats", "ItemStat")
    if stored:
        rows = stored
    else:
        from gbot.evaluate import item_stats_from_attempts

        rows = item_stats_from_attempts(user)
    out: dict[str, str] = {}
    for row in rows:
        item_id = row.get("item_id")
        if item_id:
            out[str(item_id)] = mastery_of(row)
    return out
