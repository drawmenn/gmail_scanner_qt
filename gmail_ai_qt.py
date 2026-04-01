from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gmail_ai_qt_app.app import main
from gmail_ai_qt_app.ui.main_window import MainWindow


__all__ = ["MainWindow", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
