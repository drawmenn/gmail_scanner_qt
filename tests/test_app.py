from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest import mock
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app import app as app_module


class AppSetupTests(unittest.TestCase):
    def test_frozen_app_always_uses_exe_local_playwright_browsers(self) -> None:
        exe_dir = str(ROOT / "dist")
        expected = os.path.join(exe_dir, "playwright-browsers")

        with mock.patch.object(app_module.sys, "frozen", True, create=True):
            with mock.patch.object(app_module.sys, "executable", os.path.join(exe_dir, "gmail-ai-qt.exe")):
                with mock.patch.dict(
                    app_module.os.environ,
                    {
                        "NUITKA_ONEFILE_PARENT": exe_dir,
                        "PLAYWRIGHT_BROWSERS_PATH": "C:\\unexpected-location",
                    },
                    clear=False,
                ):
                    app_module._setup_playwright_browsers_path()

                    self.assertEqual(app_module.os.environ["PLAYWRIGHT_BROWSERS_PATH"], expected)


if __name__ == "__main__":
    unittest.main()
