from __future__ import annotations

import json
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


_CHROMIUM_PROVIDERS = frozenset({"playwright", "google_browser"})
_SUPPORTED_BROWSER_CHANNELS = frozenset({"chrome"})
_INSTALL_PROGRESS_PERCENT_PATTERN = re.compile(r"(?<!\d)(100|[1-9]?\d)%")
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


@dataclass(frozen=True)
class PlaywrightBrowserMetadata:
    name: str
    title: str
    revision: str | None
    browser_version: str | None
    executable_path: Path | None
    installed: bool


@dataclass(frozen=True)
class PlaywrightBrowserInstallState:
    name: str
    target_revision: str | None
    installed_revisions: tuple[str, ...]

    @property
    def has_any_installed(self) -> bool:
        return bool(self.installed_revisions)

    @property
    def target_installed(self) -> bool:
        return bool(self.target_revision and self.target_revision in self.installed_revisions)

    @property
    def needs_reinstall(self) -> bool:
        return self.has_any_installed and not self.target_installed


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


def normalize_browser_channel(browser_channel: str) -> str:
    normalized = str(browser_channel or "").strip().lower()
    return normalized if normalized in _SUPPORTED_BROWSER_CHANNELS else ""


def browser_channel_executable_path(browser_channel: str) -> Path | None:
    normalized = normalize_browser_channel(browser_channel)
    if not normalized:
        return None

    if normalized == "chrome":
        for candidate in _browser_channel_candidates(normalized):
            if candidate.exists():
                return candidate
    return None


def browser_channel_metadata(browser_channel: str) -> PlaywrightBrowserMetadata | None:
    normalized = normalize_browser_channel(browser_channel)
    if not normalized:
        return None

    executable_path = browser_channel_executable_path(normalized)
    return PlaywrightBrowserMetadata(
        name=normalized,
        title=_browser_channel_title(normalized),
        revision=None,
        browser_version=_browser_channel_version(executable_path) if executable_path is not None else None,
        executable_path=executable_path,
        installed=bool(executable_path is not None and executable_path.exists()),
    )


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


def playwright_browser_metadata(browser_name: str) -> PlaywrightBrowserMetadata | None:
    browsers_json = _playwright_browsers_json()
    if not browsers_json:
        return None

    for browser in browsers_json.get("browsers", []):
        if browser.get("name") != browser_name:
            continue

        executable_path = browser_executable_path(browser_name)
        return PlaywrightBrowserMetadata(
            name=browser_name,
            title=str(browser.get("title") or browser_name.replace("-", " ").title()),
            revision=str(browser.get("revision", "")).strip() or None,
            browser_version=str(browser.get("browserVersion", "")).strip() or None,
            executable_path=executable_path,
            installed=bool(executable_path is not None and executable_path.exists()),
        )
    return None


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


def is_chromium_ready(
    provider: str,
    browser_headless: bool = True,
    browser_channel: str = "",
) -> bool:
    normalized_channel = normalize_browser_channel(browser_channel)
    if provider_requires_chromium(provider) and normalized_channel:
        executable_path = browser_channel_executable_path(normalized_channel)
        return executable_path is not None and executable_path.exists()

    required_browsers = _required_browser_names(provider, browser_headless, normalized_channel)
    if not required_browsers:
        return True

    for browser_name in required_browsers:
        executable_path = browser_executable_path(browser_name)
        if executable_path is None or not executable_path.exists():
            return False
    return True


def required_browser_names(
    provider: str,
    browser_headless: bool = True,
    browser_channel: str = "",
) -> tuple[str, ...]:
    return _required_browser_names(provider, browser_headless, normalize_browser_channel(browser_channel))


def playwright_browser_install_state(browser_name: str) -> PlaywrightBrowserInstallState:
    return PlaywrightBrowserInstallState(
        name=browser_name,
        target_revision=_browser_revision(browser_name),
        installed_revisions=installed_browser_revisions(browser_name),
    )


def installed_browser_revisions(browser_name: str) -> tuple[str, ...]:
    browsers_root = playwright_browsers_path()
    if browsers_root is None or not browsers_root.exists():
        return ()

    directory_prefix = f"{browser_name.replace('-', '_')}-"
    revisions: list[str] = []
    try:
        for entry in browsers_root.iterdir():
            if not entry.is_dir():
                continue
            name = entry.name.strip()
            if not name.startswith(directory_prefix):
                continue
            revision = name[len(directory_prefix) :].strip()
            if revision:
                revisions.append(revision)
    except OSError:
        return ()

    return tuple(sorted(set(revisions), key=_revision_sort_key, reverse=True))


def parse_playwright_install_progress(output: str) -> int | None:
    matches = _INSTALL_PROGRESS_PERCENT_PATTERN.findall(output or "")
    if not matches:
        return None
    return max(0, min(100, int(matches[-1])))


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


def _revision_sort_key(value: str) -> tuple[int, str]:
    normalized = (value or "").strip()
    return (0, normalized) if not normalized.isdigit() else (1, f"{int(normalized):020d}")


def _browser_channel_title(browser_channel: str) -> str:
    if normalize_browser_channel(browser_channel) == "chrome":
        return "Google Chrome"
    return browser_channel or "Browser"


def _browser_channel_candidates(browser_channel: str) -> tuple[Path, ...]:
    normalized = normalize_browser_channel(browser_channel)
    if normalized != "chrome":
        return ()

    if sys.platform == "win32":
        candidates: list[Path] = []
        for env_key in ("LOCALAPPDATA", "PROGRAMFILES", "PROGRAMFILES(X86)"):
            base_path = (os.environ.get(env_key) or "").strip()
            if not base_path:
                continue
            candidates.append(Path(base_path) / "Google" / "Chrome" / "Application" / "chrome.exe")
        return tuple(candidates)

    if sys.platform == "darwin":
        return (
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path.home() / "Applications" / "Google Chrome.app" / "Contents" / "MacOS" / "Google Chrome",
        )

    candidates = []
    for command_name in ("google-chrome", "google-chrome-stable"):
        resolved = shutil.which(command_name)
        if resolved:
            candidates.append(Path(resolved))
    return tuple(candidates)


def _browser_channel_version(executable_path: Path | None) -> str | None:
    if executable_path is None or not executable_path.exists():
        return None
    return _cached_browser_channel_version(str(executable_path))


@lru_cache(maxsize=8)
def _cached_browser_channel_version(executable_path: str) -> str | None:
    kwargs = {
        "args": [executable_path, "--version"],
        "capture_output": True,
        "timeout": 2,
        "check": False,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)

    try:
        result = subprocess.run(**kwargs)
    except (OSError, subprocess.SubprocessError, ValueError):
        return None

    version_bytes = result.stdout or result.stderr or b""
    if isinstance(version_bytes, bytes):
        version_text = version_bytes.decode("utf-8", errors="ignore").strip()
    else:
        version_text = str(version_bytes or "").strip()
    match = re.search(r"(\d+(?:\.\d+)+)", version_text)
    if not match:
        return None
    return match.group(1)


def _required_browser_names(provider: str, browser_headless: bool, browser_channel: str) -> tuple[str, ...]:
    normalized = (provider or "").strip()
    if browser_channel:
        return ()
    if normalized == "google_browser":
        return ("chromium",)
    if normalized == "playwright":
        return ("chromium-headless-shell",) if browser_headless else ("chromium",)
    return ()
