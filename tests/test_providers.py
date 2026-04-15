from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.models.state import RuntimeSettings
from gmail_ai_qt_app.services.providers import (
    browser_launch_kwargs,
    parse_browser_response,
    parse_google_browser_content,
)


class _FakeLocator:
    def __init__(self, present: bool = False, visible: bool = False) -> None:
        self._present = present
        self._visible = visible

    @property
    def first(self) -> "_FakeLocator":
        return self

    def count(self) -> int:
        return 1 if self._present else 0

    def is_visible(self) -> bool:
        return self._visible


class _FakePage:
    def __init__(
        self,
        *,
        text: str = "",
        title: str = "",
        url: str = "https://example.test/check",
        selectors: dict[str, tuple[bool, bool]] | None = None,
        evaluate_raises: bool = False,
    ) -> None:
        self._text = text
        self._title = title
        self.url = url
        self._selectors = dict(selectors or {})
        self._evaluate_raises = evaluate_raises

    def locator(self, selector: str) -> _FakeLocator:
        present, visible = self._selectors.get(selector, (False, False))
        return _FakeLocator(present=present, visible=visible)

    def evaluate(self, _script: str) -> str:
        if self._evaluate_raises:
            raise RuntimeError("evaluate failed")
        return self._text

    def title(self) -> str:
        return self._title


class ParseGoogleBrowserContentTests(unittest.TestCase):
    def test_marks_missing_account_as_available(self) -> None:
        outcome = parse_google_browser_content(
            "junchen",
            "<div>Couldn't find your Google Account</div>",
        )

        self.assertEqual(outcome.hit_delta, 1)
        self.assertEqual(outcome.message_key, "log_name_available")

    def test_marks_password_prompt_as_taken(self) -> None:
        outcome = parse_google_browser_content(
            "junchen",
            "<div>Enter your password</div>",
        )

        self.assertEqual(outcome.taken_delta, 1)
        self.assertEqual(outcome.message_key, "log_name_taken")

    def test_marks_unknown_page_as_error(self) -> None:
        outcome = parse_google_browser_content(
            "junchen",
            "<div>Try again later</div>",
            page_text="Try again later",
            page_url="https://accounts.google.com/v3/signin/challenge",
            page_title="Try again later",
        )

        self.assertEqual(outcome.error_delta, 1)
        self.assertEqual(outcome.message_key, "log_google_browser_result_unknown")
        self.assertEqual(outcome.params["url"], "https://accounts.google.com/v3/signin/challenge")
        self.assertEqual(outcome.params["title"], "Try again later")
        self.assertIn("Try again later", outcome.params["snippet"])

    def test_marks_google_secure_browser_rejection_as_specific_error(self) -> None:
        outcome = parse_google_browser_content(
            "kitqdv",
            "<div>Couldn’t sign you in</div>",
            page_text="Couldn’t sign you in This browser or app may not be secure",
            page_url="https://accounts.google.com/v3/signin/rejected?idnf=kitqdv@gmail.com",
            page_title="Sign in - Google Accounts",
        )

        self.assertEqual(outcome.error_delta, 1)
        self.assertEqual(outcome.message_key, "log_google_browser_rejected_secure_browser")
        self.assertIn("signin/rejected", outcome.params["url"])
        self.assertEqual(outcome.params["title"], "Sign in - Google Accounts")


class ParseBrowserResponseTests(unittest.TestCase):
    def test_launch_kwargs_include_system_chrome_channel(self) -> None:
        settings = RuntimeSettings(
            browser_channel="chrome",
            browser_headless=False,
        )

        launch_kwargs = browser_launch_kwargs(settings)

        self.assertEqual(launch_kwargs["channel"], "chrome")
        self.assertFalse(launch_kwargs["headless"])

    def test_launch_kwargs_preserve_proxy_and_google_args(self) -> None:
        settings = RuntimeSettings(
            proxy_enabled=True,
            proxy_url="127.0.0.1:7897",
            browser_channel="chrome",
        )

        launch_kwargs = browser_launch_kwargs(
            settings,
            headless=False,
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled"],
        )

        self.assertEqual(launch_kwargs["channel"], "chrome")
        self.assertEqual(launch_kwargs["proxy"], {"server": "http://127.0.0.1:7897"})
        self.assertEqual(launch_kwargs["ignore_default_args"], ["--enable-automation"])
        self.assertEqual(launch_kwargs["args"], ["--disable-blink-features=AutomationControlled"])

    def test_matches_regex_against_visible_page_text(self) -> None:
        settings = RuntimeSettings(
            browser_available_regex=r"available now",
        )
        page = _FakePage(
            text="Username is Available now",
            title="Availability Check",
        )

        outcome = parse_browser_response(
            "junchen",
            page,
            "<div>Username is <strong>Available</strong> now</div>",
            settings,
        )

        self.assertEqual(outcome.hit_delta, 1)
        self.assertEqual(outcome.message_key, "log_name_available")

    def test_unknown_result_includes_playwright_debug_context(self) -> None:
        settings = RuntimeSettings(
            browser_taken_text="already taken",
        )
        page = _FakePage(
            text="Please try another username later.",
            title="Check Result",
            url="https://example.test/result",
        )

        outcome = parse_browser_response(
            "kitndt",
            page,
            "<div>Please try another username later.</div>",
            settings,
        )

        self.assertEqual(outcome.error_delta, 1)
        self.assertEqual(outcome.message_key, "log_browser_result_unknown_debug")
        self.assertEqual(outcome.params["url"], "https://example.test/result")
        self.assertEqual(outcome.params["title"], "Check Result")
        self.assertEqual(outcome.params["rules"], "available[none], taken[text]")
        self.assertIn("Please try another username later.", outcome.params["snippet"])


if __name__ == "__main__":
    unittest.main()
