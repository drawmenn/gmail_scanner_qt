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

from gmail_ai_qt_app.services.playwright_installer import (
    chromium_executable_path,
    chromium_install_command,
    is_chromium_installed,
    provider_requires_chromium,
)


class PlaywrightInstallerTests(unittest.TestCase):
    def test_provider_requires_chromium_for_browser_providers(self) -> None:
        self.assertTrue(provider_requires_chromium("playwright"))
        self.assertTrue(provider_requires_chromium("google_browser"))
        self.assertFalse(provider_requires_chromium("manual"))

    def test_install_command_points_to_playwright_driver(self) -> None:
        command = chromium_install_command()

        self.assertIsNotNone(command)
        assert command is not None
        self.assertTrue(Path(command.program).exists())
        self.assertTrue(Path(command.arguments[0]).exists())
        self.assertEqual(command.arguments[1:], ("install", "chromium"))

    def test_chromium_path_uses_explicit_browser_directory(self) -> None:
        browsers_path = ROOT / "tests" / "_tmp_browsers"

        with mock.patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(browsers_path)}, clear=False):
            executable_path = chromium_executable_path()

        self.assertIsNotNone(executable_path)
        assert executable_path is not None
        self.assertTrue(str(executable_path).startswith(str(browsers_path)))

    def test_missing_browser_directory_reports_not_installed(self) -> None:
        browsers_path = ROOT / "tests" / "_missing_browsers"

        with mock.patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(browsers_path)}, clear=False):
            self.assertFalse(is_chromium_installed())


if __name__ == "__main__":
    unittest.main()
