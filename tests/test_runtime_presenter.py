from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.models.state import RuntimeSettings
from gmail_ai_qt_app.ui.runtime_presenter import MainWindowRuntimePresenter


class _DummyTimer:
    def __init__(self) -> None:
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True


class _DummyWorker:
    def __init__(self) -> None:
        self.pause_calls = 0
        self.stop_calls = 0

    def pause_scanning(self) -> None:
        self.pause_calls += 1

    def stop_scanning(self) -> None:
        self.stop_calls += 1


class _FakeWindow:
    def __init__(self) -> None:
        self.runtime_settings = RuntimeSettings(provider="playwright")
        self.runtime_state = "running"
        self.resume_scan_after_chromium_install = True
        self.auto_review_timer = _DummyTimer()
        self.worker = _DummyWorker()
        self.current_request_state = "requesting"
        self.current_review_candidate = ""
        self.refreshed_runtime_notes: list[str] = []
        self.log_events: list[tuple[str, str]] = []

    def refresh_runtime_panel(self, note_key: str) -> None:
        self.refreshed_runtime_notes.append(note_key)

    def add_log_event(self, message_key: str, tag: str, params=None) -> None:
        self.log_events.append((message_key, tag))


class RuntimePresenterTests(unittest.TestCase):
    def test_pause_clears_pending_resume_after_chromium_install(self) -> None:
        window = _FakeWindow()
        presenter = MainWindowRuntimePresenter(window)

        presenter.pause()

        self.assertEqual(window.runtime_state, "paused")
        self.assertFalse(window.resume_scan_after_chromium_install)
        self.assertTrue(window.auto_review_timer.stopped)
        self.assertEqual(window.worker.pause_calls, 1)
        self.assertIn("runtime_note_paused_manual", window.refreshed_runtime_notes)

    def test_stop_clears_pending_resume_after_chromium_install(self) -> None:
        window = _FakeWindow()
        presenter = MainWindowRuntimePresenter(window)

        presenter.stop()

        self.assertEqual(window.runtime_state, "stopped")
        self.assertFalse(window.resume_scan_after_chromium_install)
        self.assertTrue(window.auto_review_timer.stopped)
        self.assertEqual(window.worker.stop_calls, 1)
        self.assertIn("runtime_note_stopped_manual", window.refreshed_runtime_notes)


if __name__ == "__main__":
    unittest.main()
