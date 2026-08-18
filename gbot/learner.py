"""Learner runtime helpers: 오답노트, 반복 유형, 오답 패턴."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent

Learner = dict[str, Any]


def _rows(user: Learner, *keys: str) -> list[dict[str, Any]]:
    for key in keys:
        rows = user.get(key)
        if isinstance(rows, list):
            return rows
    return []


def notes_open(user: Learner) -> list[dict[str, Any]]:
    """Unresolved WrongNotes for this learner."""
    return [n for n in _rows(user, "wrong_notes", "WrongNote") if not n.get("resolved")]


def hot_types(user: Learner, min_misses: int = 3) -> list[dict[str, Any]]:
    """Types the learner keeps missing: misses>=min_misses or streak_wrong>=2."""
    hot: list[dict[str, Any]] = []
    for row in _rows(user, "type_stats", "TypeStat"):
        misses = int(row.get("misses") or 0)
        streak = int(row.get("streak_wrong") or 0)
        if misses >= min_misses or streak >= 2:
            hot.append(row)
    return hot


def hot_patterns(user: Learner) -> list[dict[str, Any]]:
    """Per-user ErrorPattern rows with at least one miss."""
    rows = [
        row
        for row in _rows(user, "error_patterns", "ErrorPattern")
        if int(row.get("miss_count") or 0) > 0
    ]
    return sorted(rows, key=lambda r: int(r.get("miss_count") or 0), reverse=True)


def item_stat(user: Learner, item_id: str) -> Optional[dict[str, Any]]:
    """문항 단위 ItemStat. 저장분이 없으면 attempts에서 파생."""
    for row in _rows(user, "item_stats", "ItemStat"):
        if row.get("item_id") == item_id:
            return row
    from gbot.evaluate import item_stats_from_attempts

    for row in item_stats_from_attempts(user):
        if row.get("item_id") == item_id:
            return row
    return None


def load_sample(path: Optional[Path] = None) -> Learner:
    """Load pack/sample_learner.json, falling back to data/app/sample_user.json."""
    if path is not None:
        with Path(path).open(encoding="utf-8") as f:
            return json.load(f)
    pack_sample = ROOT / "pack" / "sample_learner.json"
    if pack_sample.is_file():
        with pack_sample.open(encoding="utf-8") as f:
            return json.load(f)
    data_sample = ROOT / "data" / "app" / "sample_user.json"
    with data_sample.open(encoding="utf-8") as f:
        return json.load(f)
