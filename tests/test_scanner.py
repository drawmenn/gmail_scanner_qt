from __future__ import annotations

import sys
from pathlib import Path
from threading import Event
import unittest

from PySide6.QtCore import QCoreApplication


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.models.state import RuntimeSettings
from gmail_ai_qt_app.services.scanner import ScannerWorker


class ScannerWorkerCancellationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QCoreApplication.instance() or QCoreApplication([])

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


if __name__ == "__main__":
    unittest.main()
