from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.models.state import RuntimeSettings
from gmail_ai_qt_app.ui.actions_presenter import MainWindowActionsPresenter


class _FakeLineEdit:
    def __init__(self, value: str) -> None:
        self._value = value

    def text(self) -> str:
        return self._value


class _FakeSpinBox:
    def __init__(self, value: int) -> None:
        self._value = value

    def value(self) -> int:
        return self._value


class _FakeCheckBox:
    def __init__(self, checked: bool) -> None:
        self._checked = checked

    def isChecked(self) -> bool:
        return self._checked


class _FakeWorker:
    def __init__(self) -> None:
        self.names_updates: list[list[str]] = []

    def set_names(self, names: list[str]) -> None:
        self.names_updates.append(list(names))


class _FakeListWidget:
    def __init__(self) -> None:
        self.items: list[str] = []

    def clear(self) -> None:
        self.items.clear()

    def addItems(self, items: list[str]) -> None:
        self.items.extend(items)


class _FakeWindow:
    def __init__(self) -> None:
        self.runtime_settings = RuntimeSettings(seeds=["james", "alex"])
        self.generator_source_input = _FakeLineEdit("jun chen studio")
        self.generator_length_spin = _FakeSpinBox(8)
        self.generator_digits_check = _FakeCheckBox(True)
        self.generator_count_spin = _FakeSpinBox(24)
        self.worker = _FakeWorker()
        self.name_list = _FakeListWidget()
        self.seed_summary_refreshed = False
        self.log_events: list[tuple[str, str, dict]] = []

    def refresh_seed_summary(self) -> None:
        self.seed_summary_refreshed = True

    def add_log_event(self, message_key: str, tag: str, params=None) -> None:
        self.log_events.append((message_key, tag, dict(params or {})))


class ActionsPresenterTests(unittest.TestCase):
    def test_generate_name_pool_uses_length_spin_value(self) -> None:
        window = _FakeWindow()
        presenter = MainWindowActionsPresenter(window)

        with mock.patch("gmail_ai_qt_app.ui.actions_presenter.generate_candidates", return_value=["junx2024"]) as generate:
            presenter.generate_name_pool()

        options = generate.call_args.args[0]
        self.assertEqual(options.target_length, 8)
        self.assertTrue(options.allow_digits)
        self.assertEqual(options.max_results, 24)
        self.assertEqual(window.runtime_settings.seeds, ["junx2024"])
        self.assertEqual(window.worker.names_updates, [["junx2024"]])
        self.assertEqual(window.name_list.items, ["junx2024"])
        self.assertTrue(window.seed_summary_refreshed)
        self.assertEqual(window.log_events[-1], ("log_candidates_generated", "info", {"count": 1}))


if __name__ == "__main__":
    unittest.main()
