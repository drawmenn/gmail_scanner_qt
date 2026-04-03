from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.services.providers import parse_google_browser_content


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
        )

        self.assertEqual(outcome.error_delta, 1)
        self.assertEqual(outcome.message_key, "log_browser_result_unknown")


if __name__ == "__main__":
    unittest.main()
