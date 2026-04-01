from __future__ import annotations

import json
import sys
from pathlib import Path

from PySide6.QtCore import QStandardPaths

from ..models.state import RuntimeSettings


class RuntimeSettingsStore:
    def __init__(self, path: Path | None = None):
        self._path_override = Path(path) if path is not None else None

    @property
    def path(self) -> Path:
        if self._path_override is not None:
            return self._path_override

        exe_path = Path(sys.executable if getattr(sys, "frozen", False) else __file__)
        if getattr(sys, "frozen", False):
            return exe_path.parent / "settings.json"

        config_root = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.GenericConfigLocation
        )
        base_path = Path(config_root) if config_root else Path.home() / ".config"
        return base_path / "gmail_ai_qt" / "settings.json"

    @path.setter
    def path(self, value: Path | str) -> None:
        self._path_override = Path(value)

    def load(self) -> tuple[RuntimeSettings, str | None]:
        path = self.path
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return RuntimeSettings.from_dict(data), None
        except Exception as exc:
            return RuntimeSettings(), str(exc)
        return RuntimeSettings(), None

    def save(self, settings: RuntimeSettings) -> tuple[bool, Path, str | None]:
        path = self.path
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(settings.to_dict(), ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            return False, path, str(exc)
        return True, path, None
