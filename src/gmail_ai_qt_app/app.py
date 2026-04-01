import os
import sys

from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def _setup_playwright_browsers_path() -> None:
    """Point Playwright to a browsers folder beside the exe when frozen."""
    if not getattr(sys, "frozen", False):
        return
    exe_dir = os.environ.get("NUITKA_ONEFILE_PARENT", os.path.dirname(sys.executable))
    browsers_path = os.path.join(exe_dir, "playwright-browsers")
    os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", browsers_path)


def main() -> int:
    _setup_playwright_browsers_path()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
