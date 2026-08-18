"""진단 세션 설계.

블루프린트의 축에 문항 수를 나눠 준다. 공식 지문을 만들지 않는다.
준비된 original 문항을 축(skill/unit)에 맞춰 붙이고,
모자라면 해당 과목 은행의 엠바고 슬롯 id만 번호 간격으로 붙인다.
"""

from __future__ import annotations

from typing import Any

from gbot.appdata import diagnostic_blueprint


def _distribute(total: int, axes: list[str]) -> list[dict[str, Any]]:
    if not axes:
        return []
    base, rem = divmod(total, len(axes))
    out: list[dict[str, Any]] = []
    for i, axis in enumerate(axes):
        n = base + (1 if i < rem else 0)
        out.append({"axis": axis, "n": n})
    return out


def _spread_ids(ids: list[str], n: int) -> list[str]:
    if n <= 0 or not ids:
        return []
    if n >= len(ids):
        return list(ids[:n])
    if n == 1:
        return [ids[0]]
    last = len(ids) - 1
    return [ids[round(i * last / (n - 1))] for i in range(n)]


def _axis_match(item: dict[str, Any], axis: str) -> bool:
    return item.get("skill") == axis or item.get("unit") == axis


def build_diagnostic(subject: str) -> list[dict[str, Any]]:
    """블루프린트에서 {axis, n, item_ids} 목록을 만든다. stem은 만들지 않는다."""
    bp = diagnostic_blueprint(subject)
    parts = _distribute(int(bp["item_count"]), list(bp["axes"]))

    try:
        from gbot.bank import list_items

        originals = [
            item
            for item in list_items(status="ready")
            if item.get("source") == "original"
            and bp["subject_code"] in (item.get("subject_code"), item.get("subject"))
        ]
        slots = list_items(exam="2026-2", subject=bp["subject_code"])
        leftover_slots = _spread_ids([s["id"] for s in slots], int(bp["item_count"]))
        slot_idx = 0
        for part in parts:
            take = int(part["n"])
            axis = part["axis"]
            matched = [item for item in originals if _axis_match(item, axis)]
            preferred = [item for item in matched if item.get("role") == "diagnostic"]
            extras = [item for item in matched if item.get("role") != "diagnostic"]
            chosen = (preferred + extras)[:take]
            part["item_ids"] = [item["id"] for item in chosen]
            need = take - len(part["item_ids"])
            if need > 0:
                part["slot_ids"] = leftover_slots[slot_idx : slot_idx + need]
                slot_idx += need
    except Exception:
        pass
    return parts
