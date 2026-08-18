"""문제은행 로더.

공식 문항은 슬롯(메타데이터)만 로드한다. stem이 None이어도 조회·필터가 동작해야 한다.
원문을 요구하거나 만들어 내지 않는다.
없는 키는 로더가 기본값을 채운다: role=bank, unit/wiki_concept/wiki_type=null.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent
BANK_DIR = ROOT / "data" / "bank"

Item = dict[str, Any]
Exam = dict[str, Any]

_ITEM_DEFAULTS: dict[str, Any] = {
    "role": "bank",
    "unit": None,
    "wiki_concept": None,
    "wiki_type": None,
}


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _normalize_exam_key(exam: Optional[str]) -> Optional[str]:
    if exam is None:
        return None
    key = str(exam).strip()
    if key.startswith("go-"):
        key = key[3:]
    return key


def _with_item_defaults(item: Item) -> Item:
    for key, default in _ITEM_DEFAULTS.items():
        item.setdefault(key, default)
    return item


class Bank:
    def __init__(self) -> None:
        self.manifest: dict[str, Any] = {}
        self.exams: list[Exam] = []
        self.items: list[Item] = []
        self._by_id: dict[str, Item] = {}
        self._loaded = False

    def load(self, bank_dir: Optional[Path] = None) -> "Bank":
        root = Path(bank_dir) if bank_dir is not None else BANK_DIR
        self.manifest = _read_json(root / "manifest.json")

        exams: list[Exam] = []
        exam_dir = root / "exams"
        for path in sorted(exam_dir.glob("go-*.json")):
            exams.append(_read_json(path))
        self.exams = exams

        items: list[Item] = []
        item_dir = root / "items"
        for path in sorted(item_dir.glob("go-*.json")):
            batch = _read_json(path)
            if not isinstance(batch, list):
                raise ValueError(f"item file must be an array: {path}")
            for raw in batch:
                items.append(_with_item_defaults(raw))
        self.items = items
        self._by_id = {item["id"]: item for item in items}
        self._loaded = True
        return self

    def _ensure(self) -> None:
        if not self._loaded:
            self.load()

    def list_exams(self) -> list[Exam]:
        self._ensure()
        return list(self.exams)

    def list_items(
        self,
        exam: Optional[str] = None,
        subject: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[Item]:
        self._ensure()
        exam_key = _normalize_exam_key(exam)
        subject_key = subject.strip() if subject is not None else None
        status_key = status.strip() if status is not None else None

        out: list[Item] = []
        for item in self.items:
            if exam_key is not None and item.get("exam") != exam_key:
                continue
            if subject_key is not None:
                if subject_key not in (item.get("subject"), item.get("subject_code")):
                    continue
            if status_key is not None and item.get("status") != status_key:
                continue
            out.append(item)
        return out

    def get(self, id: str) -> Optional[Item]:
        self._ensure()
        return self._by_id.get(id)

    def stats(self) -> dict[str, int]:
        self._ensure()
        embargoed = sum(1 for i in self.items if i.get("status") == "embargoed")
        ready = sum(1 for i in self.items if i.get("status") == "ready")
        return {
            "exams": len(self.exams),
            "items": len(self.items),
            "embargoed": embargoed,
            "ready": ready,
        }


_BANK = Bank()


def load(bank_dir: Optional[Path] = None) -> Bank:
    """Load manifest + exam files + item arrays. stem is never required."""
    return _BANK.load(bank_dir)


def list_exams() -> list[Exam]:
    return _BANK.list_exams()


def list_items(
    exam: Optional[str] = None,
    subject: Optional[str] = None,
    status: Optional[str] = None,
) -> list[Item]:
    return _BANK.list_items(exam=exam, subject=subject, status=status)


def get(id: str) -> Optional[Item]:
    return _BANK.get(id)


def stats() -> dict[str, int]:
    return _BANK.stats()
