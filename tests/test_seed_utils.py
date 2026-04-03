from __future__ import annotations

import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.services.seed_utils import normalize_seed_value, sanitize_seed_values


class SeedUtilsTests(unittest.TestCase):
    def test_normalize_seed_value_strips_non_alnum_and_lowercases(self) -> None:
        self.assertEqual(normalize_seed_value(" Jun Chen! "), "junchen")

    def test_sanitize_seed_values_deduplicates_and_drops_empty_entries(self) -> None:
        self.assertEqual(
            sanitize_seed_values([" Jun Chen! ", "junchen", "***", "alex"]),
            ["junchen", "alex"],
        )


if __name__ == "__main__":
    unittest.main()
