"""진단 세션 설계.

블루프린트의 축에 문항 수를 나눠 준다. 공식 지문을 만들지 않는다.
필요하면 해당 과목 은행의 엠바고 슬롯 id만 번호 간격으로 붙인다.
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


def build_diagnostic(subject: str) -> list[dict[str, Any]]:
    """블루프린트에서 {axis, n} 목록을 만든다. stem은 만들지 않는다."""
    bp = diagnostic_blueprint(subject)
    parts = _distribute(int(bp["item_count"]), list(bp["axes"]))

    try:
        from gbot.bank import list_items

        slots = list_items(exam="2026-2", subject=bp["subject_code"])
        slot_ids = _spread_ids([s["id"] for s in slots], int(bp["item_count"]))
        idx = 0
        for part in parts:
            take = int(part["n"])
            part["slot_ids"] = slot_ids[idx : idx + take]
            idx += take
    except Exception:
        pass
    return parts
