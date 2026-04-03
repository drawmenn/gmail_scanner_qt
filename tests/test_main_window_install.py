from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock
import unittest

from PySide6.QtCore import QProcess


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.ui.main_window import MainWindow


class _DummyProcess:
    def __init__(self, error_text: str) -> None:
        self._error_text = error_text
        self.deleted = False

    def errorString(self) -> str:
        return self._error_text

    def deleteLater(self) -> None:
        self.deleted = True


class _FakeInstallWindow:
    _take_chromium_install_state = MainWindow._take_chromium_install_state
    _fail_chromium_installation = MainWindow._fail_chromium_installation
    _handle_chromium_install_error = MainWindow._handle_chromium_install_error
    _latest_install_output_line = staticmethod(MainWindow._latest_install_output_line)

    def __init__(self, process: _DummyProcess) -> None:
        self.chromium_install_process = process
        self.resume_scan_after_chromium_install = True
        self.chromium_install_canceled = False
        self.chromium_install_output = ""
        self.chromium_install_error = ""
        self.log_events: list[tuple[str, str, dict]] = []
        self.status_updates: list[tuple[str, str, int]] = []

    def _read_chromium_install_output(self) -> None:
        return

    def add_log_event(self, message_key: str, tag: str, params=None) -> None:
        self.log_events.append((message_key, tag, dict(params or {})))

    def set_chromium_install_status(self, state: str, detail: str = "", auto_hide_ms: int = 0) -> None:
        self.status_updates.append((state, detail, auto_hide_ms))

    def text(self, key: str, **params) -> str:
        if key == "browser_install_failed_message":
            return params["error"]
        return key


class MainWindowInstallFlowTests(unittest.TestCase):
    def test_failed_to_start_process_cleans_up_install_state(self) -> None:
        process = _DummyProcess("installer missing")
        window = _FakeInstallWindow(process)

        with mock.patch("gmail_ai_qt_app.ui.main_window.QMessageBox.warning") as warning:
            window._handle_chromium_install_error(QProcess.ProcessError.FailedToStart)

        self.assertIsNone(window.chromium_install_process)
        self.assertFalse(window.resume_scan_after_chromium_install)
        self.assertFalse(window.chromium_install_canceled)
        self.assertEqual(window.chromium_install_output, "")
        self.assertEqual(window.chromium_install_error, "")
        self.assertTrue(process.deleted)
        self.assertEqual(
            window.log_events[-1],
            ("log_browser_install_failed", "error", {"error": "installer missing"}),
        )
        self.assertEqual(window.status_updates[-1], ("failed", "installer missing", 8000))
        warning.assert_called_once()


if __name__ == "__main__":
    unittest.main()
