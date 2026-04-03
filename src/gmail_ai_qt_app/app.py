import os
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def _setup_playwright_browsers_path() -> None:
    """Point Playwright to a browsers folder beside the exe when frozen."""
    if not getattr(sys, "frozen", False):
        return
    exe_dir = os.environ.get("NUITKA_ONEFILE_PARENT", os.path.dirname(sys.executable))
    browsers_path = os.path.join(exe_dir, "playwright-browsers")
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = browsers_path


def _app_icon() -> QIcon:
    icon_path = Path(__file__).parent / "assets" / "icon.ico"
    if icon_path.exists():
        return QIcon(str(icon_path))
    return QIcon()


def main() -> int:
    _setup_playwright_browsers_path()
    app = QApplication(sys.argv)
    app.setWindowIcon(_app_icon())
    window = MainWindow()
    window.show()
    return app.exec()
