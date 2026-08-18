"""앱 런타임 데이터 로더.

밴드·과목 진단 설계·주간 계획·샘플 사용자를 data/ 에서 읽는다.
위키를 훑지 않는다.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

Band = dict[str, Any]
Blueprint = dict[str, Any]
Template = dict[str, Any]


def _read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


class AppData:
    def __init__(self) -> None:
        self.levels: dict[str, Any] = {}
        self.subjects: dict[str, Any] = {}
        self.templates: dict[str, Any] = {}
        self.sample_user: dict[str, Any] = {}
        self._loaded = False

    def load(self, data_dir: Optional[Path] = None) -> "AppData":
        root = Path(data_dir) if data_dir is not None else DATA_DIR
        self.levels = _read_json(root / "diagnostics" / "levels.json")
        self.subjects = _read_json(root / "diagnostics" / "subjects.json")
        self.templates = _read_json(root / "plans" / "templates.json")
        self.sample_user = _read_json(root / "app" / "sample_user.json")
        self._loaded = True
        return self

    def _ensure(self) -> None:
        if not self._loaded:
            self.load()

    def list_bands(self) -> list[Band]:
        self._ensure()
        return list(self.levels.get("bands", []))

    def diagnostic_blueprint(self, subject: str) -> Blueprint:
        self._ensure()
        key = subject.strip()
        for bp in self.subjects.get("blueprints", []):
            if key in (bp.get("subject"), bp.get("subject_code")):
                return bp
        raise KeyError(f"unknown subject: {subject}")

    def plan_for(self, band: str) -> Template:
        self._ensure()
        key = band.strip()
        for tmpl in self.templates.get("templates", []):
            if tmpl.get("band") == key:
                return tmpl
        raise KeyError(f"unknown band: {band}")


_APP = AppData()


def load(data_dir: Optional[Path] = None) -> AppData:
    return _APP.load(data_dir)


def list_bands() -> list[Band]:
    return _APP.list_bands()


def diagnostic_blueprint(subject: str) -> Blueprint:
    return _APP.diagnostic_blueprint(subject)


def plan_for(band: str) -> Template:
    return _APP.plan_for(band)
