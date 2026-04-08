import os
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from .ui.main_window import MainWindow


def _compiled_exe_directory() -> Path | None:
    onefile_directory = os.environ.get("NUITKA_ONEFILE_DIRECTORY", "").strip()
    if onefile_directory:
        return Path(onefile_directory)

    is_compiled = bool(getattr(sys, "frozen", False) or globals().get("__compiled__") is not None)
    executable = (getattr(sys, "executable", "") or "").strip()
    if is_compiled and executable:
        return Path(executable).resolve().parent
    return None


def _setup_playwright_browsers_path() -> None:
    """Point Playwright to a browsers folder beside the exe when frozen."""
    exe_dir = _compiled_exe_directory()
    if exe_dir is None:
        return

    browsers_path = Path(exe_dir) / "playwright-browsers"
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(browsers_path)


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
