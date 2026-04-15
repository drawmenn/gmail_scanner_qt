from __future__ import annotations

import os
import sys
from pathlib import Path
import tempfile
from unittest import mock
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.services.playwright_installer import (
    browser_channel_metadata,
    browser_executable_path,
    chromium_executable_path,
    chromium_install_command,
    compiled_exe_directory,
    installed_browser_revisions,
    is_chromium_ready,
    is_chromium_installed,
    normalize_browser_channel,
    parse_playwright_install_progress,
    playwright_browser_install_state,
    playwright_browser_metadata,
    playwright_browsers_path,
    provider_requires_chromium,
    required_browser_names,
)


class PlaywrightInstallerTests(unittest.TestCase):
    def test_provider_requires_chromium_for_browser_providers(self) -> None:
        self.assertTrue(provider_requires_chromium("playwright"))
        self.assertTrue(provider_requires_chromium("google_browser"))
        self.assertFalse(provider_requires_chromium("manual"))

    def test_normalize_browser_channel_accepts_supported_value(self) -> None:
        self.assertEqual(normalize_browser_channel("chrome"), "chrome")
        self.assertEqual(normalize_browser_channel(" Chrome "), "chrome")
        self.assertEqual(normalize_browser_channel("edge"), "")

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

    def test_headless_shell_path_uses_explicit_browser_directory(self) -> None:
        browsers_path = ROOT / "tests" / "_tmp_browsers"

        with mock.patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(browsers_path)}, clear=False):
            executable_path = browser_executable_path("chromium-headless-shell")

        self.assertIsNotNone(executable_path)
        assert executable_path is not None
        self.assertTrue(str(executable_path).startswith(str(browsers_path)))

    def test_compiled_runtime_prefers_exe_local_browser_directory(self) -> None:
        exe_dir = ROOT / "dist"

        with mock.patch.dict(
            os.environ,
            {
                "NUITKA_ONEFILE_DIRECTORY": str(exe_dir),
                "PLAYWRIGHT_BROWSERS_PATH": "",
            },
            clear=False,
        ):
            self.assertEqual(compiled_exe_directory(), exe_dir)
            self.assertEqual(playwright_browsers_path(), exe_dir / "playwright-browsers")

    def test_missing_browser_directory_reports_not_installed(self) -> None:
        browsers_path = ROOT / "tests" / "_missing_browsers"

        with mock.patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(browsers_path)}, clear=False):
            self.assertFalse(is_chromium_installed())

    def test_google_browser_requires_full_chromium(self) -> None:
        def fake_path(browser_name: str):
            if browser_name == "chromium":
                return None
            return mock.Mock(exists=mock.Mock(return_value=True))

        with mock.patch(
            "gmail_ai_qt_app.services.playwright_installer.browser_executable_path",
            side_effect=fake_path,
        ):
            self.assertFalse(is_chromium_ready("google_browser"))

    def test_headed_playwright_requires_full_chromium(self) -> None:
        def fake_path(browser_name: str):
            if browser_name == "chromium":
                return mock.Mock(exists=mock.Mock(return_value=True))
            return None

        with mock.patch(
            "gmail_ai_qt_app.services.playwright_installer.browser_executable_path",
            side_effect=fake_path,
        ):
            self.assertTrue(is_chromium_ready("playwright", browser_headless=False))
            self.assertFalse(is_chromium_ready("playwright", browser_headless=True))

    def test_chrome_channel_uses_system_browser_instead_of_playwright_downloads(self) -> None:
        self.assertEqual(required_browser_names("playwright", browser_headless=True, browser_channel="chrome"), ())
        fake_path = ROOT / "README.md"
        with mock.patch(
            "gmail_ai_qt_app.services.playwright_installer.browser_channel_executable_path",
            return_value=fake_path,
        ):
            self.assertTrue(is_chromium_ready("playwright", browser_headless=True, browser_channel="chrome"))

    def test_browser_channel_metadata_reports_missing_chrome(self) -> None:
        with mock.patch(
            "gmail_ai_qt_app.services.playwright_installer.browser_channel_executable_path",
            return_value=None,
        ):
            metadata = browser_channel_metadata("chrome")

        self.assertIsNotNone(metadata)
        assert metadata is not None
        self.assertEqual(metadata.title, "Google Chrome")
        self.assertFalse(metadata.installed)
        self.assertIsNone(metadata.executable_path)

    def test_browser_metadata_includes_version_and_revision(self) -> None:
        metadata = playwright_browser_metadata("chromium")

        self.assertIsNotNone(metadata)
        assert metadata is not None
        self.assertEqual(metadata.name, "chromium")
        self.assertTrue(bool(metadata.revision))
        self.assertTrue(bool(metadata.browser_version))

    def test_parse_install_progress_uses_latest_percentage(self) -> None:
        output = "Downloading Chromium 10%\rDownloading Chromium 64%\rDownloading Chromium 100%"

        self.assertEqual(parse_playwright_install_progress(output), 100)

    def test_parse_install_progress_returns_none_without_percentage(self) -> None:
        self.assertIsNone(parse_playwright_install_progress("Downloading Chromium..."))

    def test_installed_browser_revisions_discovers_local_versions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chromium-1208").mkdir()
            (root / "chromium-1194").mkdir()
            (root / "chromium_headless_shell-1208").mkdir()

            with mock.patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(root)}, clear=False):
                self.assertEqual(installed_browser_revisions("chromium"), ("1208", "1194"))

    def test_browser_install_state_detects_reinstall_needed_for_stale_revision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chromium-1194").mkdir()

            with mock.patch.dict(os.environ, {"PLAYWRIGHT_BROWSERS_PATH": str(root)}, clear=False):
                state = playwright_browser_install_state("chromium")

            self.assertTrue(state.has_any_installed)
            self.assertFalse(state.target_installed)
            self.assertTrue(state.needs_reinstall)


if __name__ == "__main__":
    unittest.main()
