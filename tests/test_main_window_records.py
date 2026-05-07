from __future__ import annotations

import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.models.state import RuntimeSettings
from gmail_ai_qt_app.ui.main_window import MainWindow


class _SettingsStore:
    def __init__(self, path: Path) -> None:
        self.path = path


class _RecordWindow:
    REVIEW_RECORD_FIELDS = MainWindow.REVIEW_RECORD_FIELDS

    def __init__(self, provider: str, settings_path: Path) -> None:
        self.runtime_settings = RuntimeSettings(provider=provider)
        self.review_records: list[dict] = []
        self.review_panel_refreshes = 0
        self.settings_store = _SettingsStore(settings_path)
        self.log_events: list[tuple[str, str, dict]] = []

    def refresh_review_panel(self) -> None:
        self.review_panel_refreshes += 1

    def add_log_event(self, message_key: str, tag: str, params=None) -> None:
        self.log_events.append((message_key, tag, dict(params or {})))

    record_review_record = MainWindow.record_review_record
    review_records_path = MainWindow.review_records_path
    _append_review_record_to_disk = MainWindow._append_review_record_to_disk


class MainWindowRecordTests(unittest.TestCase):
    def test_auto_available_hit_is_saved_to_review_records(self) -> None:
        with TemporaryDirectory() as temp_dir:
            settings_path = Path(temp_dir) / "settings.json"
            window = _RecordWindow(provider="google_browser", settings_path=settings_path)

            MainWindow._record_auto_available_hit(
                window,
                "log_name_available",
                {"name": "junx2024"},
            )

            self.assertEqual(len(window.review_records), 1)
            self.assertEqual(window.review_records[0]["candidate"], "junx2024")
            self.assertEqual(window.review_records[0]["decision"], "available")
            self.assertEqual(window.review_records[0]["provider"], "google_browser")
            self.assertTrue(window.review_records[0]["timestamp"])
            self.assertEqual(window.review_panel_refreshes, 1)
            saved_text = window.review_records_path().read_text(encoding="utf-8-sig")
            self.assertIn("timestamp,candidate,decision,provider", saved_text)
            self.assertIn("junx2024,available,google_browser", saved_text)
            self.assertEqual(window.log_events[-1][0], "log_review_record_saved")
            self.assertEqual(window.log_events[-1][1], "info")
            self.assertEqual(window.log_events[-1][2]["path"], str(window.review_records_path()))

    def test_manual_available_hit_is_not_recorded_twice(self) -> None:
        with TemporaryDirectory() as temp_dir:
            settings_path = Path(temp_dir) / "settings.json"
            window = _RecordWindow(provider="manual", settings_path=settings_path)

            MainWindow._record_auto_available_hit(
                window,
                "log_name_available",
                {"name": "junx2024"},
            )

            self.assertEqual(window.review_records, [])
            self.assertEqual(window.review_panel_refreshes, 0)
            self.assertFalse(window.review_records_path().exists())
            self.assertEqual(window.log_events, [])

    def test_failed_realtime_save_is_logged(self) -> None:
        with TemporaryDirectory() as temp_dir:
            blocked_parent = Path(temp_dir) / "blocked"
            blocked_parent.write_text("", encoding="utf-8")
            settings_path = blocked_parent / "settings.json"
            window = _RecordWindow(provider="google_browser", settings_path=settings_path)

            window.record_review_record("junx2024", "available")

            self.assertEqual(len(window.review_records), 1)
            self.assertEqual(window.log_events[-1][0], "log_review_record_save_failed")
            self.assertEqual(window.log_events[-1][1], "error")
            self.assertEqual(window.log_events[-1][2]["path"], str(window.review_records_path()))
            self.assertTrue(window.log_events[-1][2]["error"])


if __name__ == "__main__":
    unittest.main()
