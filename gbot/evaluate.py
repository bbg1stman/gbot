"""종합 평가: 문항 숙달(ItemStat)과 취약 과목·단원·유형·문항."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from gbot.chapters import edition_for_year
from gbot.learner import hot_patterns, hot_types
from gbot.mastery import mastery_of

Learner = dict[str, Any]
ItemStat = dict[str, Any]
Evaluation = dict[str, Any]

SUBJECT_MIN = 40
AVERAGE_MIN = 60
HISTORY_MAX = 10
SUBJECT_CODES = ("kor", "math", "eng", "soc", "sci", "his")
BAND_ACTION = {
    "미달": "개념+유형",
    "경계": "유형+기출슬롯",
    "안정": "기출 세트",
    "여유": "약한 과목 집중",
}
KST = timezone(timedelta(hours=9))


def _rows(user: Learner, *keys: str) -> list[dict[str, Any]]:
    for key in keys:
        rows = user.get(key)
        if isinstance(rows, list):
            return [r for r in rows if isinstance(r, dict)]
    return []


def _pass_rules() -> tuple[int, int]:
    try:
        from gbot.appdata import _APP

        rules = (_APP.levels or {}).get("pass_rules") or {}
        return int(rules.get("subject_min", SUBJECT_MIN)), int(
            rules.get("average_min", AVERAGE_MIN)
        )
    except Exception:
        return SUBJECT_MIN, AVERAGE_MIN


def subject_code_of(row: dict[str, Any]) -> Optional[str]:
    """Infer subject_code from type_id or item_id. Official stems are not used."""
    existing = row.get("subject_code")
    if existing:
        return existing
    type_id = row.get("type_id") or ""
    parts = str(type_id).split("-")
    if len(parts) >= 2 and parts[0] == "type" and parts[1] in SUBJECT_CODES:
        return parts[1]
    item_id = row.get("item_id") or ""
    wrapped = f"-{item_id}-"
    for code in SUBJECT_CODES:
        if f"-{code}-" in wrapped:
            return code
    return None


def item_stats_from_attempts(user: Learner) -> list[ItemStat]:
    """Build ItemStat rows from attempts (and open WrongNotes for next_review)."""
    attempts = sorted(
        _rows(user, "attempts", "Attempt"),
        key=lambda a: a.get("ts") or "",
    )
    by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for att in attempts:
        item_id = att.get("item_id")
        if item_id:
            by_item[str(item_id)].append(att)

    notes = {n.get("item_id"): n for n in _rows(user, "wrong_notes", "WrongNote")}
    user_id = user.get("id") or user.get("user_id")
    out: list[ItemStat] = []
    for item_id, rows in by_item.items():
        last = rows[-1]
        n = len(rows)
        misses = sum(1 for r in rows if not r.get("correct"))
        streak = 0
        for r in reversed(rows):
            if r.get("correct"):
                break
            streak += 1
        ease = round((n - misses) / n, 3) if n else None
        last_correct = last.get("correct")
        if last_correct is not None:
            last_correct = bool(last_correct)
        note = notes.get(item_id) or {}
        next_review = note.get("next_review") if note and not note.get("resolved") else None
        history = [
            {
                "attempt_id": r.get("id"),
                "correct": bool(r.get("correct")),
                "ts": r.get("ts"),
            }
            for r in rows[-HISTORY_MAX:]
        ]
        out.append(
            {
                "id": f"is-{item_id}",
                "user_id": user_id,
                "item_id": item_id,
                "subject_code": subject_code_of(last) or subject_code_of({"item_id": item_id}),
                "type_id": last.get("type_id"),
                "axis": last.get("axis"),
                "attempts": n,
                "misses": misses,
                "last_correct": last_correct,
                "last_choice": last.get("choice"),
                "last_ts": last.get("ts"),
                "streak_wrong": streak,
                "ease": ease,
                "next_review": next_review,
                "history": history,
                "mastery": mastery_of(
                    {
                        "attempts": n,
                        "misses": misses,
                        "last_correct": last_correct,
                        "streak_wrong": streak,
                        "ease": ease,
                    }
                ),
            }
        )
    out.sort(key=lambda r: str(r.get("item_id") or ""))
    return out


def _stored_item_stats(user: Learner) -> list[ItemStat]:
    stored = _rows(user, "item_stats", "ItemStat")
    if stored:
        return stored
    return item_stats_from_attempts(user)


def _weak_types(user: Learner) -> list[dict[str, Any]]:
    hot = hot_types(user)
    if hot:
        return [
            {
                "type_id": row.get("type_id"),
                "subject_code": row.get("subject_code"),
                "misses": int(row.get("misses") or 0),
                "streak_wrong": int(row.get("streak_wrong") or 0),
            }
            for row in hot
        ]
    if _rows(user, "type_stats", "TypeStat"):
        return []
    by_type: dict[str, dict[str, Any]] = {}
    attempts = sorted(
        _rows(user, "attempts", "Attempt"),
        key=lambda a: a.get("ts") or "",
    )
    for att in attempts:
        tid = att.get("type_id")
        if not tid:
            continue
        row = by_type.setdefault(
            tid,
            {
                "type_id": tid,
                "subject_code": subject_code_of(att),
                "attempts": 0,
                "misses": 0,
                "streak_wrong": 0,
            },
        )
        row["attempts"] += 1
        if att.get("correct"):
            row["streak_wrong"] = 0
        else:
            row["misses"] += 1
            row["streak_wrong"] += 1
    return [
        {
            "type_id": row["type_id"],
            "subject_code": row["subject_code"],
            "misses": row["misses"],
            "streak_wrong": row["streak_wrong"],
        }
        for row in by_type.values()
        if row["misses"] >= 3 or row["streak_wrong"] >= 2
    ]


def _chapter_lookups(
    target_year: int = 2026,
) -> tuple[
    dict[str, dict[str, Any]],
    dict[tuple[Optional[str], str], dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    """Load chapters for target_year + items. Join key: chapter_id / axis / type_id."""
    import json
    from pathlib import Path

    from gbot.chapters import chapters_for_year

    chapters = chapters_for_year(target_year)
    by_id: dict[str, dict[str, Any]] = {}
    by_axis: dict[tuple[Optional[str], str], dict[str, Any]] = {}
    by_type: dict[str, dict[str, Any]] = {}
    for ch in chapters:
        by_id[ch["id"]] = ch
        axis = ch.get("axis")
        if axis:
            key = (ch.get("subject_code"), str(axis))
            prev = by_axis.get(key)
            if prev is None or (prev.get("parent_id") and not ch.get("parent_id")):
                by_axis[key] = ch
        if ch.get("type_id") and not ch.get("parent_id"):
            by_type[str(ch["type_id"])] = ch
    items_by_id: dict[str, dict[str, Any]] = {}
    items_path = Path(__file__).resolve().parent.parent / "pack" / "items.json"
    if items_path.is_file():
        with items_path.open(encoding="utf-8") as f:
            raw = json.load(f)
        for item in raw:
            if isinstance(item, dict) and item.get("id"):
                items_by_id[str(item["id"])] = item
    return by_id, by_axis, by_type, items_by_id


def _resolve_chapter(
    att: dict[str, Any],
    by_id: dict[str, dict[str, Any]],
    by_axis: dict[tuple[Optional[str], str], dict[str, Any]],
    by_type: dict[str, dict[str, Any]],
    items_by_id: dict[str, dict[str, Any]],
) -> Optional[dict[str, Any]]:
    item = items_by_id.get(str(att.get("item_id") or "")) or {}
    cid = att.get("chapter_id") or item.get("chapter_id")
    if cid and cid in by_id:
        return by_id[str(cid)]
    code = subject_code_of(att) or item.get("subject_code")
    axis = att.get("axis") or item.get("unit") or item.get("skill")
    if axis:
        ch = by_axis.get((code, str(axis)))
        if ch:
            return ch
    tid = att.get("type_id") or item.get("type_id")
    if tid and tid in by_type:
        return by_type[str(tid)]
    return None


def _weak_chapters(
    attempts: list[dict[str, Any]],
    target_year: int = 2026,
) -> list[dict[str, Any]]:
    """Same weakness rule as axes: accuracy < 0.6 or misses >= 2.

    Chapter tree is the edition covering target_year.
    """
    by_id, by_axis, by_type, items_by_id = _chapter_lookups(target_year)
    if not by_id:
        return []
    stats: dict[str, dict[str, Any]] = {}
    for att in attempts:
        ch = _resolve_chapter(att, by_id, by_axis, by_type, items_by_id)
        if not ch:
            continue
        row = stats.setdefault(
            ch["id"],
            {
                "chapter_id": ch["id"],
                "subject_code": ch.get("subject_code"),
                "title": ch.get("title"),
                "attempts": 0,
                "misses": 0,
                "parent_id": ch.get("parent_id"),
            },
        )
        row["attempts"] += 1
        if not att.get("correct"):
            row["misses"] += 1
    weak: list[dict[str, Any]] = []
    for row in stats.values():
        att_n, miss_n = row["attempts"], row["misses"]
        acc = round((att_n - miss_n) / att_n, 4) if att_n else 0.0
        if acc < 0.6 or miss_n >= 2:
            weak.append({**row, "accuracy": acc})
    weak.sort(key=lambda r: (r["accuracy"], -r["misses"], r.get("title") or ""))
    return weak


def _weak_patterns(user: Learner) -> list[dict[str, Any]]:
    pats = hot_patterns(user)
    if pats:
        return [
            {
                "pattern_id": row.get("pattern_id"),
                "miss_count": int(row.get("miss_count") or 0),
            }
            for row in pats
        ]
    if _rows(user, "error_patterns", "ErrorPattern"):
        return []
    counts: dict[str, int] = defaultdict(int)
    for note in _rows(user, "wrong_notes", "WrongNote"):
        pid = note.get("pattern_id")
        if pid:
            counts[str(pid)] += 1
    return [
        {"pattern_id": pid, "miss_count": n}
        for pid, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        if n > 0
    ]


def evaluate(user: Learner, target_year: int = 2026) -> Evaluation:
    """종합 평가. 과락선 40 / 평균 60. 공식 원문은 쓰지 않는다.

    weak_chapters 는 target_year 의 edition 단원 트리를 쓴다.
    """
    subject_min, average_min = _pass_rules()
    stats = _stored_item_stats(user)
    attempts = _rows(user, "attempts", "Attempt")

    by_subject: dict[str, dict[str, int]] = defaultdict(lambda: {"attempts": 0, "correct": 0})
    by_axis: dict[tuple[Optional[str], str], dict[str, int]] = defaultdict(
        lambda: {"attempts": 0, "misses": 0}
    )
    for att in attempts:
        code = subject_code_of(att)
        if code:
            by_subject[code]["attempts"] += 1
            if att.get("correct"):
                by_subject[code]["correct"] += 1
        axis = att.get("axis")
        if axis:
            key = (code, str(axis))
            by_axis[key]["attempts"] += 1
            if not att.get("correct"):
                by_axis[key]["misses"] += 1

    subjects_out: list[dict[str, Any]] = []
    estimates: list[float] = []
    raw = user.get("subjects") or {}
    for code, info in raw.items():
        if not isinstance(info, dict):
            continue
        est = info.get("estimate")
        if isinstance(est, (int, float)):
            estimates.append(float(est))
        att_n = by_subject[code]["attempts"]
        cor_n = by_subject[code]["correct"]
        accuracy = round(cor_n / att_n, 4) if att_n else None
        band = info.get("band")
        weak = (isinstance(est, (int, float)) and est < subject_min) or band == "미달"
        subjects_out.append(
            {
                "code": code,
                "band": band,
                "estimate": est,
                "attempts": att_n,
                "accuracy": accuracy,
                "weak": bool(weak),
            }
        )

    estimate_avg = round(sum(estimates) / len(estimates), 2) if estimates else 0.0
    subject_min_risk = any(e < subject_min for e in estimates)
    average_risk = estimate_avg < average_min
    pass_ready = (not subject_min_risk) and (not average_risk)

    weak_axes: list[dict[str, Any]] = []
    for (code, axis), row in by_axis.items():
        att_n, miss_n = row["attempts"], row["misses"]
        acc = round((att_n - miss_n) / att_n, 4) if att_n else 0.0
        if acc < 0.6 or miss_n >= 2:
            weak_axes.append(
                {
                    "subject_code": code,
                    "axis": axis,
                    "attempts": att_n,
                    "misses": miss_n,
                    "accuracy": acc,
                }
            )
    weak_axes.sort(key=lambda r: (r["accuracy"], -r["misses"], r["axis"] or ""))

    weak_types = _weak_types(user)
    weak_patterns = _weak_patterns(user)
    weak_chapters = _weak_chapters(attempts, target_year=target_year)

    weak_codes = {s["code"] for s in subjects_out if s["weak"]}
    stat_by_item = {s.get("item_id"): s for s in stats}
    weak_items: list[dict[str, Any]] = []
    for st in stats:
        misses = int(st.get("misses") or 0)
        last_ok = st.get("last_correct")
        if misses >= 1 and last_ok is not True:
            weak_items.append(
                {
                    "item_id": st.get("item_id"),
                    "misses": misses,
                    "last_correct": last_ok,
                }
            )

    def _item_key(w: dict[str, Any]) -> tuple:
        st = stat_by_item.get(w.get("item_id")) or {}
        code = st.get("subject_code") or subject_code_of({"item_id": w.get("item_id")})
        return (0 if code in weak_codes else 1, -int(w.get("misses") or 0), w.get("item_id") or "")

    weak_items.sort(key=_item_key)

    focus: list[dict[str, Any]] = []
    for s in subjects_out:
        if not s["weak"]:
            continue
        est = s.get("estimate")
        focus.append(
            {
                "subject_code": s["code"],
                "reason": f"과락 위험 (추정 {est} < {subject_min})",
                "action": BAND_ACTION.get(s.get("band") or "", "개념+유형"),
            }
        )
    for t in weak_types:
        focus.append(
            {
                "subject_code": t.get("subject_code"),
                "reason": f"약한 유형 {t.get('type_id')}",
                "action": "유형 반복",
            }
        )

    edition = edition_for_year(target_year)
    generated_at = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S+09:00")
    return {
        "user_id": user.get("id") or user.get("user_id"),
        "generated_at": generated_at,
        "target_year": target_year,
        "edition_id": (edition or {}).get("id"),
        "overall": {
            "estimate_avg": estimate_avg,
            "pass_ready": pass_ready,
            "subject_min_risk": subject_min_risk,
            "average_risk": average_risk,
        },
        "subjects": subjects_out,
        "weak_axes": weak_axes,
        "weak_chapters": weak_chapters,
        "weak_types": weak_types,
        "weak_patterns": weak_patterns,
        "weak_items": weak_items,
        "focus": focus,
    }
