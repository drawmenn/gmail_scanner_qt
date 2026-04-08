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
    def test_frozen_app_uses_onefile_directory_for_playwright_browsers(self) -> None:
        exe_dir = str(ROOT / "dist")
        expected = os.path.join(exe_dir, "playwright-browsers")

        with mock.patch.object(app_module.sys, "frozen", True, create=True):
            with mock.patch.object(app_module.sys, "executable", os.path.join(exe_dir, "gmail-ai-qt.exe")):
                with mock.patch.dict(
                    app_module.os.environ,
                    {
                        "NUITKA_ONEFILE_DIRECTORY": exe_dir,
                        "NUITKA_ONEFILE_PARENT": "12345",
                        "PLAYWRIGHT_BROWSERS_PATH": "C:\\unexpected-location",
                    },
                    clear=False,
                ):
                    app_module._setup_playwright_browsers_path()

                    self.assertEqual(app_module.os.environ["PLAYWRIGHT_BROWSERS_PATH"], expected)

    def test_compiled_app_without_sys_frozen_uses_executable_directory(self) -> None:
        exe_dir = str(ROOT / "dist")
        executable_path = os.path.join(exe_dir, "gmail-ai-qt-fixed.exe")
        expected = os.path.join(exe_dir, "playwright-browsers")

        with mock.patch.dict(app_module.__dict__, {"__compiled__": object()}, clear=False):
            with mock.patch.object(app_module.sys, "frozen", False, create=True):
                with mock.patch.object(app_module.sys, "executable", executable_path):
                    with mock.patch.dict(
                        app_module.os.environ,
                        {
                            "NUITKA_ONEFILE_DIRECTORY": "",
                            "PLAYWRIGHT_BROWSERS_PATH": "C:\\unexpected-location",
                        },
                        clear=False,
                    ):
                        app_module._setup_playwright_browsers_path()

                        self.assertEqual(app_module.os.environ["PLAYWRIGHT_BROWSERS_PATH"], expected)


if __name__ == "__main__":
    unittest.main()
