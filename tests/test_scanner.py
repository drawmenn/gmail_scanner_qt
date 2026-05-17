from __future__ import annotations

import sys
import os
from pathlib import Path
from threading import Event
import unittest

from PySide6.QtWidgets import QApplication


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.models.state import RuntimeSettings
from gmail_ai_qt_app.services.providers import ScanOutcome
from gmail_ai_qt_app.services.scanner import LocalScanResult, ScannerWorker


class ScannerWorkerCancellationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def test_cancel_active_local_scan_clears_active_task_immediately(self) -> None:
        worker = ScannerWorker(RuntimeSettings())
        cancel_event = Event()
        worker._active_local_scan_id = 7
        worker._active_local_scan_generation = 3
        worker._active_local_scan_cancel_event = cancel_event

        canceled = worker._cancel_active_local_scan()

        self.assertTrue(canceled)
        self.assertTrue(cancel_event.is_set())
        self.assertIsNone(worker._active_local_scan_id)
        self.assertIsNone(worker._active_local_scan_generation)
        self.assertIsNone(worker._active_local_scan_cancel_event)

    def test_fatal_local_scan_result_pauses_worker(self) -> None:
        worker = ScannerWorker(RuntimeSettings(provider="google_browser"))
        logs = []
        states = []
        worker.log_signal.connect(lambda key, tag, params: logs.append((key, tag, params)))
        worker.request_state_signal.connect(lambda state, params: states.append((state, params)))
        worker._running = True
        worker._paused = False
        worker._generation = 3
        worker._active_local_scan_id = 9
        worker._active_local_scan_generation = 3

        worker._handle_local_scan_result(
            LocalScanResult(
                task_id=9,
                generation=3,
                outcome=ScanOutcome(
                    error_delta=1,
                    tag="error",
                    message_key="log_browser_connection_failed",
                    params={"name": "kitndt", "error": "net::ERR_CONNECTION_RESET"},
                    fatal=True,
                ),
            )
        )

        self.assertTrue(worker._running)
        self.assertTrue(worker._paused)
        self.assertEqual(worker._generation, 4)
        self.assertEqual(logs[0][0], "log_browser_connection_failed")
        self.assertEqual(states[-1], ("error", {"error": "net::ERR_CONNECTION_RESET"}))

    def test_repeated_local_scan_errors_pause_worker_at_threshold(self) -> None:
        worker = ScannerWorker(RuntimeSettings(provider="google_browser"))
        logs = []
        states = []
        worker.log_signal.connect(lambda key, tag, params: logs.append((key, tag, params)))
        worker.request_state_signal.connect(lambda state, params: states.append((state, params)))
        worker._running = True
        worker._paused = False
        worker._generation = 3

        for task_id in range(1, 4):
            worker._active_local_scan_id = task_id
            worker._active_local_scan_generation = 3
            worker._handle_local_scan_result(
                LocalScanResult(
                    task_id=task_id,
                    generation=3,
                    outcome=ScanOutcome(
                        error_delta=1,
                        tag="error",
                        message_key="log_google_browser_result_unknown",
                        params={"name": f"kitnd{task_id}"},
                    ),
                )
            )

        self.assertTrue(worker._running)
        self.assertTrue(worker._paused)
        self.assertEqual(worker._generation, 4)
        self.assertEqual(logs[-1][0], "log_scanner_auto_paused_repeated_errors")
        self.assertEqual(logs[-1][2]["count"], "3")
        self.assertEqual(logs[-1][2]["error"], "log_google_browser_result_unknown")
        self.assertEqual(states[-1], ("error", {"error": "log_google_browser_result_unknown"}))

    def test_connection_error_with_proxy_auto_disables_proxy_without_pause(self) -> None:
        worker = ScannerWorker(
            RuntimeSettings(
                provider="google_browser",
                proxy_enabled=True,
                proxy_url="127.0.0.1:7897",
            )
        )
        logs = []
        worker.log_signal.connect(lambda key, tag, params: logs.append((key, tag, params)))
        worker._running = True
        worker._paused = False
        worker._generation = 3
        worker._active_local_scan_id = 9
        worker._active_local_scan_generation = 3

        worker._handle_local_scan_result(
            LocalScanResult(
                task_id=9,
                generation=3,
                outcome=ScanOutcome(
                    error_delta=1,
                    tag="error",
                    message_key="log_browser_connection_failed",
                    params={"name": "kitndt", "error": "net::ERR_PROXY_CONNECTION_FAILED"},
                    fatal=True,
                ),
            )
        )

        self.assertTrue(worker._running)
        self.assertFalse(worker._paused)
        self.assertFalse(worker._settings.proxy_enabled)
        self.assertEqual(logs[-1][0], "log_scanner_auto_repair_proxy_disabled")
        self.assertEqual(logs[-1][2]["proxy"], "127.0.0.1:7897")

    def test_browser_timeout_auto_extends_timeout_without_pause(self) -> None:
        worker = ScannerWorker(RuntimeSettings(provider="google_browser", browser_timeout_ms=10_000))
        logs = []
        worker.log_signal.connect(lambda key, tag, params: logs.append((key, tag, params)))
        worker._running = True
        worker._paused = False
        worker._generation = 3
        worker._active_local_scan_id = 9
        worker._active_local_scan_generation = 3

        worker._handle_local_scan_result(
            LocalScanResult(
                task_id=9,
                generation=3,
                outcome=ScanOutcome(
                    error_delta=1,
                    tag="error",
                    message_key="log_browser_timeout",
                    params={"name": "kitndt"},
                ),
            )
        )

        self.assertTrue(worker._running)
        self.assertFalse(worker._paused)
        self.assertEqual(worker._settings.browser_timeout_ms, 20_000)
        self.assertEqual(logs[-1][0], "log_scanner_auto_repair_timeout_extended")
        self.assertEqual(logs[-1][2]["old_timeout"], "10000")
        self.assertEqual(logs[-1][2]["new_timeout"], "20000")

    def test_success_resets_repeated_error_counter(self) -> None:
        worker = ScannerWorker(RuntimeSettings(provider="google_browser"))

        error = ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_timeout",
            params={"name": "kitndt"},
        )
        success = ScanOutcome(
            checked_delta=1,
            hit_delta=1,
            tag="hit",
            message_key="log_name_available",
            params={"name": "kitndx"},
        )

        self.assertEqual(worker._complete_outcome(error), 1)
        self.assertEqual(worker._complete_outcome(error), 2)
        self.assertEqual(worker._complete_outcome(success), 0)
        self.assertEqual(worker._complete_outcome(error), 1)


if __name__ == "__main__":
    unittest.main()
