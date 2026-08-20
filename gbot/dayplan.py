"""하루 순서 틀. 주간 템플릿은 양과 재료, 여기는 오늘 칸. 오답이 항상 첫 칸."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from gbot.evaluate import evaluate
from gbot.learner import hot_types, load_sample, notes_open

ROOT = Path(__file__).resolve().parent.parent
Learner = dict[str, Any]
DayPlan = dict[str, Any]

BAND_RANK = {"미달": 0, "미정": 0, "경계": 1, "안정": 2, "여유": 3}
STEP_IDS = ("review", "concept", "type", "new")


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_day_frame() -> dict[str, Any]:
    """data/plans/day.json, 없으면 pack/day.json."""
    data_path = ROOT / "data" / "plans" / "day.json"
    if data_path.is_file():
        return _read_json(data_path)
    pack_path = ROOT / "pack" / "day.json"
    if pack_path.is_file():
        return _read_json(pack_path)
    raise FileNotFoundError("day.json not found in data/plans or pack/")


def notes_due(user: Learner, on_date: str) -> list[dict[str, Any]]:
    """Unresolved WrongNotes whose next_review is None or <= on_date."""
    due: list[dict[str, Any]] = []
    for note in notes_open(user):
        nxt = note.get("next_review")
        if nxt is None or str(nxt) <= on_date:
            due.append(note)
    return due


def focus_band(user: Learner) -> str:
    """Worst subject band. 미정 is treated like 미달."""
    subjects = user.get("subjects") or {}
    worst = "미달"
    worst_rank = 99
    found = False
    rows = subjects.values() if isinstance(subjects, dict) else subjects
    for info in rows:
        if not isinstance(info, dict):
            continue
        band = info.get("band") or "미정"
        rank = BAND_RANK.get(str(band), 0)
        if not found or rank < worst_rank:
            found = True
            worst_rank = rank
            worst = "미달" if band == "미정" else str(band)
    return worst if found else "미달"


def _day_counts(band: str, frame: dict[str, Any]) -> dict[str, int]:
    steps = frame.get("steps") or {}
    defaults = {
        sid: int((steps.get(sid) or {}).get("default_count") or 0) for sid in STEP_IDS
    }
    try:
        from gbot.appdata import plan_for

        tmpl = plan_for(band)
        counts = tmpl.get("day_counts") or {}
        if counts:
            return {sid: int(counts.get(sid) or 0) for sid in STEP_IDS}
    except Exception:
        pass
    return defaults


def _new_item_ids(
    ev: dict[str, Any],
    exclude: set[str],
    count: int,
    user: Learner,
) -> list[str]:
    if count <= 0:
        return []
    from gbot.bank import list_items
    from gbot.mastery import DONE_LEVELS, item_mastery_map

    levels = item_mastery_map(user)
    weak_codes = {s.get("code") for s in ev.get("subjects") or [] if s.get("weak")}
    candidates: list[dict[str, Any]] = []
    for item in list_items():
        if item.get("source") != "original":
            continue
        if item.get("status") != "ready":
            continue
        if item.get("source") == "official" or item.get("status") == "embargoed":
            continue
        iid = item.get("id")
        if not iid or iid in exclude:
            continue
        if levels.get(str(iid)) in DONE_LEVELS:
            continue
        candidates.append(item)
    candidates.sort(
        key=lambda i: (0 if i.get("subject_code") in weak_codes else 1, i.get("id") or "")
    )
    return [str(i["id"]) for i in candidates[:count]]


def build_day(user: Learner, on_date: str, target_year: int = 2026) -> DayPlan:
    """오늘 칸. 오답 복습이 항상 첫 스텝."""
    from gbot.appdata import load as load_app
    from gbot.bank import load as load_bank

    load_app()
    load_bank()

    frame = load_day_frame()
    order = list(frame.get("order") or STEP_IDS)
    steps_meta = frame.get("steps") or {}
    band = focus_band(user)
    counts = _day_counts(band, frame)
    ev = evaluate(user, target_year=target_year)

    due = notes_due(user, on_date)
    review_n = counts.get("review", 0)
    review_notes = due[:review_n] if review_n else []
    review_item_ids = [str(n.get("item_id")) for n in review_notes if n.get("item_id")]
    review_note_ids = [str(n.get("id")) for n in review_notes if n.get("id")]

    concept_n = counts.get("concept", 0)
    weak_ch = ev.get("weak_chapters") or []
    chapter_ids = [
        str(c.get("chapter_id"))
        for c in (weak_ch[:concept_n] if concept_n else [])
        if c.get("chapter_id")
    ]

    type_n = counts.get("type", 0)
    hot = hot_types(user)
    type_ids = [
        str(t.get("type_id"))
        for t in (hot[:type_n] if type_n else [])
        if t.get("type_id")
    ]

    new_n = counts.get("new", 0)
    new_ids = _new_item_ids(ev, set(review_item_ids), new_n, user)

    filled = {
        "review": {
            "id": "review",
            "label": (steps_meta.get("review") or {}).get("label") or "오답 복습",
            "count": len(review_item_ids),
            "item_ids": review_item_ids,
            "note_ids": review_note_ids,
        },
        "concept": {
            "id": "concept",
            "label": (steps_meta.get("concept") or {}).get("label") or "개념",
            "count": len(chapter_ids),
            "chapter_ids": chapter_ids,
            "item_ids": [],
        },
        "type": {
            "id": "type",
            "label": (steps_meta.get("type") or {}).get("label") or "유형",
            "count": len(type_ids),
            "type_ids": type_ids,
            "item_ids": [],
        },
        "new": {
            "id": "new",
            "label": (steps_meta.get("new") or {}).get("label") or "새 문제",
            "count": len(new_ids),
            "item_ids": new_ids,
        },
    }

    steps = [filled[sid] for sid in order if sid in filled]
    for sid in STEP_IDS:
        if sid not in {s["id"] for s in steps}:
            steps.append(filled[sid])

    return {
        "date": on_date,
        "band": band,
        "user_id": user.get("id") or user.get("user_id"),
        "steps": steps,
    }


def format_day(plan: DayPlan, heading: Optional[str] = None) -> str:
    date = plan.get("date")
    band = plan.get("band")
    lines = [heading if heading is not None else f"오늘 {date}  밴드 {band}"]
    for step in plan.get("steps") or []:
        lines.append(f"{step.get('label')}  {step.get('count')}")
        sid = step.get("id")
        if sid == "review":
            pairs = zip(step.get("item_ids") or [], step.get("note_ids") or [])
            for iid, nid in pairs:
                lines.append(f"  {iid}  {nid}")
        elif sid == "concept":
            for cid in step.get("chapter_ids") or []:
                lines.append(f"  {cid}")
        elif sid == "type":
            for tid in step.get("type_ids") or []:
                lines.append(f"  {tid}")
        else:
            for iid in step.get("item_ids") or []:
                lines.append(f"  {iid}")
    return chr(10).join(lines)


if __name__ == "__main__":
    user = load_sample()
    plan = build_day(user, "2026-08-19")
    print(format_day(plan, heading=f"{plan['date']}  밴드 {plan['band']}"))
