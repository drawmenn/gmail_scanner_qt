from __future__ import annotations

import json
import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path


_CHROMIUM_PROVIDERS = frozenset({"playwright", "google_browser"})
_BROWSER_EXECUTABLE_TOKENS = {
    "chromium": {
        "linux-x64": ("chrome-linux64", "chrome"),
        "linux-arm64": ("chrome-linux", "chrome"),
        "mac-x64": (
            "chrome-mac-x64",
            "Google Chrome for Testing.app",
            "Contents",
            "MacOS",
            "Google Chrome for Testing",
        ),
        "mac-arm64": (
            "chrome-mac-arm64",
            "Google Chrome for Testing.app",
            "Contents",
            "MacOS",
            "Google Chrome for Testing",
        ),
        "win-x64": ("chrome-win64", "chrome.exe"),
    },
    "chromium-headless-shell": {
        "linux-x64": ("chrome-headless-shell-linux64", "chrome-headless-shell"),
        "linux-arm64": ("chrome-linux", "headless_shell"),
        "mac-x64": ("chrome-headless-shell-mac-x64", "chrome-headless-shell"),
        "mac-arm64": ("chrome-headless-shell-mac-arm64", "chrome-headless-shell"),
        "win-x64": ("chrome-headless-shell-win64", "chrome-headless-shell.exe"),
    },
}


@dataclass(frozen=True)
class PlaywrightInstallCommand:
    program: str
    arguments: tuple[str, ...]
    env: dict[str, str]


def compiled_exe_directory() -> Path | None:
    onefile_directory = os.environ.get("NUITKA_ONEFILE_DIRECTORY", "").strip()
    if onefile_directory:
        return Path(onefile_directory)

    is_compiled = bool(getattr(sys, "frozen", False) or globals().get("__compiled__") is not None)
    executable = (getattr(sys, "executable", "") or "").strip()
    if is_compiled and executable:
        return Path(executable).resolve().parent
    return None


def provider_requires_chromium(provider: str) -> bool:
    return (provider or "").strip() in _CHROMIUM_PROVIDERS


def chromium_install_command() -> PlaywrightInstallCommand | None:
    try:
        from playwright._impl._driver import compute_driver_executable, get_driver_env
    except ImportError:
        return None

    program, cli_path = compute_driver_executable()
    if not Path(program).exists() or not Path(cli_path).exists():
        return None

    return PlaywrightInstallCommand(
        program=program,
        arguments=(cli_path, "install", "chromium"),
        env=get_driver_env(),
    )


def chromium_executable_path() -> Path | None:
    return browser_executable_path("chromium")


def browser_executable_path(browser_name: str) -> Path | None:
    browsers_root = playwright_browsers_path()
    browser_revision = _browser_revision(browser_name)
    host_platform = _host_platform_key()
    tokens = _BROWSER_EXECUTABLE_TOKENS.get(browser_name, {}).get(host_platform)
    if browsers_root is None or not browser_revision or tokens is None:
        return None
    directory_name = browser_name.replace("-", "_")
    return browsers_root / f"{directory_name}-{browser_revision}" / Path(*tokens)


def is_chromium_installed() -> bool:
    executable_path = chromium_executable_path()
    return executable_path is not None and executable_path.exists()


def is_chromium_ready(provider: str, browser_headless: bool = True) -> bool:
    required_browsers = _required_browser_names(provider, browser_headless)
    if not required_browsers:
        return True

    for browser_name in required_browsers:
        executable_path = browser_executable_path(browser_name)
        if executable_path is None or not executable_path.exists():
            return False
    return True


def playwright_browsers_path() -> Path | None:
    package_root = _playwright_package_root()
    if package_root is None:
        return None

    env_value = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    if env_value == "0":
        result = package_root / ".local-browsers"
    elif env_value:
        result = Path(env_value)
    else:
        result = _bundled_browser_cache_dir() or _default_browser_cache_dir()
        if result is None:
            return None

    if not result.is_absolute():
        result = (Path(os.environ.get("INIT_CWD") or os.getcwd()) / result).resolve()
    return result


def _browser_revision(browser_name: str) -> str | None:
    browsers_json = _playwright_browsers_json()
    if not browsers_json:
        return None

    for browser in browsers_json.get("browsers", []):
        if browser.get("name") == browser_name:
            return str(browser.get("revision", "")).strip() or None
    return None


def _playwright_browsers_json() -> dict | None:
    browsers_json_path = _playwright_package_root()
    if browsers_json_path is None:
        return None

    path = browsers_json_path / "browsers.json"
    if not path.exists():
        return None

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _playwright_package_root() -> Path | None:
    try:
        import playwright
    except ImportError:
        return None

    return Path(playwright.__file__).resolve().parent / "driver" / "package"


def _bundled_browser_cache_dir() -> Path | None:
    exe_dir = compiled_exe_directory()
    if exe_dir is None:
        return None
    return exe_dir / "playwright-browsers"


def _default_browser_cache_dir() -> Path | None:
    if sys.platform.startswith("linux"):
        cache_dir = os.environ.get("XDG_CACHE_HOME")
        return (Path(cache_dir) if cache_dir else Path.home() / ".cache") / "ms-playwright"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Caches" / "ms-playwright"
    if sys.platform == "win32":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "ms-playwright"
        return Path.home() / "AppData" / "Local" / "ms-playwright"
    return None


def _host_platform_key() -> str | None:
    machine = platform.machine().lower()
    is_arm = machine in {"arm64", "aarch64"}

    if sys.platform == "win32":
        return "win-x64"
    if sys.platform == "darwin":
        return "mac-arm64" if is_arm else "mac-x64"
    if sys.platform.startswith("linux"):
        return "linux-arm64" if is_arm else "linux-x64"
    return None


def _required_browser_names(provider: str, browser_headless: bool) -> tuple[str, ...]:
    normalized = (provider or "").strip()
    if normalized == "google_browser":
        return ("chromium",)
    if normalized == "playwright":
        return ("chromium-headless-shell",) if browser_headless else ("chromium",)
    return ()
