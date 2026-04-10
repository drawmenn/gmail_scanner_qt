from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest import mock
import unittest

from PySide6.QtCore import QProcess
from PySide6.QtWidgets import QApplication, QTextEdit


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.ui.main_window import MainWindow
from gmail_ai_qt_app.ui import main_window as main_window_module
from gmail_ai_qt_app.models.state import RuntimeSettings


class _DummyProcess:
    def __init__(self, error_text: str) -> None:
        self._error_text = error_text
        self.deleted = False

    def errorString(self) -> str:
        return self._error_text

    def deleteLater(self) -> None:
        self.deleted = True


class _ReadableProcess:
    def __init__(self, output_text: str) -> None:
        self._output_text = output_text.encode("utf-8")

    def readAll(self) -> bytes:
        return self._output_text


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


class _FakeInstallReadWindow:
    _read_chromium_install_output = MainWindow._read_chromium_install_output
    _latest_install_output_line = staticmethod(MainWindow._latest_install_output_line)

    def __init__(self, process: _ReadableProcess) -> None:
        self.chromium_install_process = process
        self.chromium_install_output = ""
        self.chromium_install_progress = None
        self.status_updates: list[tuple[str, str, int]] = []

    def set_chromium_install_status(self, state: str, detail: str = "", auto_hide_ms: int = 0) -> None:
        self.status_updates.append((state, detail, auto_hide_ms))


class _FakePromptWindow:
    _handle_runtime_browser_missing = MainWindow._handle_runtime_browser_missing

    def __init__(self, provider: str = "playwright", runtime_state: str = "running") -> None:
        self.runtime_settings = mock.Mock(provider=provider)
        self.runtime_state = runtime_state
        self.pause_calls = 0
        self.install_requests: list[tuple[bool, bool]] = []

    def pause(self) -> None:
        self.pause_calls += 1

    def request_chromium_install(self, *, resume_scan: bool, skip_installed_check: bool = False) -> bool:
        self.install_requests.append((resume_scan, skip_installed_check))
        return False


class _FakeStartupPromptWindow:
    maybe_request_chromium_on_launch = MainWindow.maybe_request_chromium_on_launch

    def __init__(self, provider: str = "playwright") -> None:
        self.runtime_settings = mock.Mock(provider=provider)
        self.install_requests: list[tuple[bool, bool]] = []

    def request_chromium_install(self, *, resume_scan: bool, skip_installed_check: bool = False) -> bool:
        self.install_requests.append((resume_scan, skip_installed_check))
        return False


class _FakeDelegatingWindow:
    start = MainWindow.start
    pause = MainWindow.pause
    stop = MainWindow.stop
    closeEvent = MainWindow.closeEvent

    def __init__(self) -> None:
        self.runtime_presenter = mock.Mock()


class MainWindowInstallFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

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

    def test_runtime_missing_browser_error_pauses_and_prompts_install(self) -> None:
        window = _FakePromptWindow()

        window._handle_runtime_browser_missing("log_browser_chromium_missing")

        self.assertEqual(window.pause_calls, 1)
        self.assertEqual(window.install_requests, [(True, True)])

    def test_runtime_missing_browser_error_ignored_for_non_browser_provider(self) -> None:
        window = _FakePromptWindow(provider="manual")

        window._handle_runtime_browser_missing("log_browser_chromium_missing")

        self.assertEqual(window.pause_calls, 0)
        self.assertEqual(window.install_requests, [])

    def test_frozen_launch_prompts_install_for_browser_provider(self) -> None:
        window = _FakeStartupPromptWindow()

        with mock.patch("gmail_ai_qt_app.ui.main_window.sys.frozen", True, create=True):
            window.maybe_request_chromium_on_launch()

        self.assertEqual(window.install_requests, [(False, False)])

    def test_non_frozen_launch_does_not_prompt_install(self) -> None:
        window = _FakeStartupPromptWindow()

        with mock.patch("gmail_ai_qt_app.ui.main_window.sys.frozen", False, create=True):
            window.maybe_request_chromium_on_launch()

        self.assertEqual(window.install_requests, [])

    def test_nuitka_launch_prompts_install_without_sys_frozen(self) -> None:
        window = _FakeStartupPromptWindow()

        with mock.patch("gmail_ai_qt_app.ui.main_window.sys.frozen", False, create=True):
            with mock.patch.dict(
                main_window_module.os.environ,
                {"NUITKA_ONEFILE_DIRECTORY": str(ROOT / "dist")},
                clear=False,
            ):
                window.maybe_request_chromium_on_launch()

        self.assertEqual(window.install_requests, [(False, False)])

    def test_read_install_output_tracks_latest_progress_percent(self) -> None:
        process = _ReadableProcess("Downloading Chromium 14%\rDownloading Chromium 67%")
        window = _FakeInstallReadWindow(process)

        window._read_chromium_install_output()

        self.assertEqual(window.chromium_install_progress, 67)
        self.assertEqual(window.status_updates[-1], ("running", "Downloading Chromium 67%", 0))

    def test_main_window_initializes_multiline_inputs_and_option_combos(self) -> None:
        settings = RuntimeSettings(
            seeds=["james", "alex"],
            language="zh_CN",
            provider="manual",
            manual_auto_enabled=True,
            manual_auto_action="hold",
            custom_headers="Authorization: Bearer demo-token",
            custom_body_template='{"username":"{username}"}',
            browser_headers="X-User: {username}",
            browser_timeout_ms=10_000,
            browser_delay_ms=800,
        )

        with mock.patch.object(main_window_module.RuntimeSettingsStore, "load", return_value=(settings, None)):
            with mock.patch.object(
                main_window_module.RuntimeSettingsStore,
                "save",
                return_value=(True, ROOT / "settings.json", None),
            ):
                window = MainWindow()
                try:
                    self.assertIsInstance(window.custom_headers_input, QTextEdit)
                    self.assertIsInstance(window.custom_body_input, QTextEdit)
                    self.assertIsInstance(window.browser_headers_input, QTextEdit)
                    self.assertEqual(window.language_combo.currentData(), "zh_CN")
                    self.assertEqual(window.provider_combo.currentData(), "manual")
                    self.assertEqual(window.auto_review_action_combo.currentData(), "hold")
                    self.assertEqual(window.custom_headers_input.toPlainText(), settings.custom_headers)
                    self.assertEqual(window.browser_headers_input.toPlainText(), settings.browser_headers)
                    self.assertEqual(window.browser_timeout_spin.value(), settings.browser_timeout_ms)
                    self.assertEqual(window.browser_delay_spin.value(), settings.browser_delay_ms)
                    self.assertTrue(hasattr(window, "chromium_status_meta_label"))
                    self.assertTrue(hasattr(window, "chromium_status_progress"))
                    self.assertEqual(window.name_list.count(), len(settings.seeds))
                finally:
                    window.close()
                    self.app.processEvents()

    def test_main_window_lifecycle_methods_delegate_to_runtime_presenter(self) -> None:
        window = _FakeDelegatingWindow()
        event = mock.Mock()

        window.start()
        window.pause()
        window.stop()
        window.closeEvent(event)

        window.runtime_presenter.start.assert_called_once_with()
        window.runtime_presenter.pause.assert_called_once_with()
        window.runtime_presenter.stop.assert_called_once_with()
        window.runtime_presenter.close_event.assert_called_once_with(event)


if __name__ == "__main__":
    unittest.main()
