from __future__ import annotations

from dataclasses import dataclass, field
import re
import time
from threading import Event
from typing import Literal

from ..models.state import RuntimeSettings


@dataclass(frozen=True)
class ProviderOption:
    code: str
    label_key: str
    subtitle_key: str


@dataclass(frozen=True)
class PreparedScan:
    mode: Literal["local", "network"]
    url: str = ""
    method: Literal["GET", "POST"] = "GET"
    query: dict[str, str] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    timeout_ms: int = 10_000


@dataclass(frozen=True)
class ScanOutcome:
    checked_delta: int = 0
    hit_delta: int = 0
    taken_delta: int = 0
    hold_delta: int = 0
    error_delta: int = 0
    tag: str = "info"
    message_key: str = ""
    params: dict[str, str] = field(default_factory=dict)


class ScanCanceledError(Exception):
    pass


PROVIDER_OPTIONS = [
    ProviderOption(
        code="manual",
        label_key="provider_manual_label",
        subtitle_key="provider_manual_subtitle",
    ),
    ProviderOption(
        code="mock",
        label_key="provider_mock_label",
        subtitle_key="provider_mock_subtitle",
    ),
    ProviderOption(
        code="custom",
        label_key="provider_custom_label",
        subtitle_key="provider_custom_subtitle",
    ),
    ProviderOption(
        code="playwright",
        label_key="provider_playwright_label",
        subtitle_key="provider_playwright_subtitle",
    ),
    ProviderOption(
        code="google_browser",
        label_key="provider_google_browser_label",
        subtitle_key="provider_google_browser_subtitle",
    ),
]


def available_providers() -> list[ProviderOption]:
    return PROVIDER_OPTIONS.copy()


_PROVIDER_CODES: frozenset[str] = frozenset(item.code for item in PROVIDER_OPTIONS)


def normalize_provider(provider: str) -> str:
    if provider in _PROVIDER_CODES:
        return provider
    return "manual"


def prepare_scan(provider: str, name: str, settings: RuntimeSettings | None = None) -> PreparedScan:
    provider = normalize_provider(provider)
    if provider == "custom":
        if settings is None or not settings.custom_url.strip():
            return PreparedScan(mode="local")

        custom_url = settings.custom_url.strip()
        custom_method = normalize_custom_method(settings.custom_method)
        custom_headers = build_custom_headers(settings.custom_headers, name)
        custom_body = settings.custom_body_template.replace("{username}", name)

        if "{username}" in custom_url:
            return PreparedScan(
                mode="network",
                url=custom_url.replace("{username}", name),
                method=custom_method,
                headers=custom_headers,
                body=custom_body,
                timeout_ms=10_000,
            )

        param_name = settings.custom_param_name.strip() or "username"
        return PreparedScan(
            mode="network",
            url=custom_url,
            method=custom_method,
            query={param_name: name} if custom_method == "GET" else {},
            headers=custom_headers,
            body=custom_body,
            timeout_ms=10_000,
        )

    return PreparedScan(mode="local")


def run_local_scan(
    provider: str,
    name: str,
    settings: RuntimeSettings | None = None,
    cancel_event: Event | None = None,
) -> ScanOutcome:
    provider = normalize_provider(provider)
    if provider == "playwright":
        return run_playwright_scan(name, settings, cancel_event)
    if provider == "google_browser":
        return run_google_browser_scan(name, settings, cancel_event)
    if provider == "custom":
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_custom_url_missing",
            params={},
        )
    if provider != "mock":
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_provider_unavailable",
            params={"provider": provider},
        )

    # Deterministic mock result so the demo feels stable across runs.
    score = sum(ord(ch) for ch in name) % 12
    if score == 0:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_mock_error",
            params={"name": name},
        )
    if score in {2, 5, 9}:
        return ScanOutcome(
            checked_delta=1,
            hit_delta=1,
            tag="hit",
            message_key="log_name_available",
            params={"name": name},
        )
    return ScanOutcome(
        checked_delta=1,
        taken_delta=1,
        tag="taken",
        message_key="log_name_taken",
        params={"name": name},
    )


def run_playwright_scan(
    name: str,
    settings: RuntimeSettings | None,
    cancel_event: Event | None = None,
) -> ScanOutcome:
    if settings is None:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_config_missing",
            params={"detail": "settings"},
        )

    config_error = validate_browser_settings(settings)
    if config_error:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_config_missing",
            params={"detail": config_error},
        )

    regex_error = (
        validate_regex_pattern(settings.browser_available_regex)
        or validate_regex_pattern(settings.browser_taken_regex)
    )
    if regex_error is not None:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_regex_invalid",
            params={"pattern": regex_error},
        )

    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_dependency_missing",
            params={},
        )

    page_url = resolve_template(settings.browser_url, name)
    input_value = resolve_template(settings.browser_value_template, name)
    timeout_ms = max(1000, int(settings.browser_timeout_ms or 10_000))
    delay_ms = max(0, int(settings.browser_delay_ms or 0))
    headers = build_custom_headers(settings.browser_headers, name)
    browser = None

    try:
        ensure_scan_not_canceled(cancel_event)
        with sync_playwright() as playwright:
            ensure_scan_not_canceled(cancel_event)
            launch_kwargs = {"headless": bool(settings.browser_headless)}
            if settings.proxy_enabled and settings.proxy_url.strip():
                proxy_server = settings.proxy_url.strip()
                if "://" not in proxy_server:
                    proxy_server = f"http://{proxy_server}"
                launch_kwargs["proxy"] = {"server": proxy_server}

            try:
                browser = playwright.chromium.launch(**launch_kwargs)
            except Exception as exc:
                if "Executable doesn't exist" in str(exc) or "playwright install" in str(exc).lower():
                    return ScanOutcome(
                        error_delta=1,
                        tag="error",
                        message_key="log_browser_chromium_missing",
                        params={},
                    )
                raise
            page = browser.new_page()
            ensure_scan_not_canceled(cancel_event)
            if headers:
                page.set_extra_http_headers(headers)

            page.goto(page_url, wait_until="domcontentloaded", timeout=timeout_ms)
            ensure_scan_not_canceled(cancel_event)

            if settings.browser_input_selector.strip():
                page.locator(settings.browser_input_selector.strip()).first.fill(input_value, timeout=timeout_ms)
                ensure_scan_not_canceled(cancel_event)

            submit_selector = settings.browser_submit_selector.strip()
            if submit_selector:
                page.locator(submit_selector).first.click(timeout=timeout_ms)
            elif settings.browser_input_selector.strip():
                page.locator(settings.browser_input_selector.strip()).first.press("Enter")
            ensure_scan_not_canceled(cancel_event)

            if delay_ms:
                wait_for_cancellation(delay_ms, cancel_event)

            ensure_scan_not_canceled(cancel_event)
            page_html = page.content()
            return parse_browser_response(name, page, page_html, settings)
    except ScanCanceledError:
        raise
    except PlaywrightTimeoutError:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_timeout",
            params={"name": name},
        )
    except PlaywrightError as exc:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_failed",
            params={"name": name, "error": str(exc)},
        )
    except Exception as exc:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_failed",
            params={"name": name, "error": str(exc)},
        )
    finally:
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass


def run_google_browser_scan(
    name: str,
    settings: RuntimeSettings | None,
    cancel_event: Event | None = None,
) -> ScanOutcome:
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
        from playwright.sync_api import sync_playwright
    except ImportError:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_dependency_missing",
            params={},
        )

    proxy_kwargs = {}
    if settings is not None and settings.proxy_enabled and settings.proxy_url.strip():
        proxy_server = settings.proxy_url.strip()
        if "://" not in proxy_server:
            proxy_server = f"http://{proxy_server}"
        proxy_kwargs["proxy"] = {"server": proxy_server}

    browser = None
    try:
        ensure_scan_not_canceled(cancel_event)
        with sync_playwright() as playwright:
            ensure_scan_not_canceled(cancel_event)
            try:
                browser = playwright.chromium.launch(headless=True, **proxy_kwargs)
            except Exception as exc:
                if "Executable doesn't exist" in str(exc) or "playwright install" in str(exc).lower():
                    return ScanOutcome(
                        error_delta=1,
                        tag="error",
                        message_key="log_browser_chromium_missing",
                        params={},
                    )
                raise
            page = browser.new_page()
            ensure_scan_not_canceled(cancel_event)
            page.goto(
                "https://accounts.google.com/signin/v2/identifier",
                wait_until="domcontentloaded",
                timeout=15_000,
            )
            ensure_scan_not_canceled(cancel_event)
            page.locator('input[type="email"]').first.fill(f"{name}@gmail.com", timeout=10_000)
            ensure_scan_not_canceled(cancel_event)
            page.locator("#identifierNext").first.click(timeout=10_000)
            wait_for_cancellation(3000, cancel_event)
            ensure_scan_not_canceled(cancel_event)

            return parse_google_browser_content(name, page.content())
    except ScanCanceledError:
        raise
    except PlaywrightTimeoutError:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_timeout",
            params={"name": name},
        )
    except PlaywrightError as exc:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_failed",
            params={"name": name, "error": str(exc)},
        )
    except Exception as exc:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_failed",
            params={"name": name, "error": str(exc)},
        )
    finally:
        if browser is not None:
            try:
                browser.close()
            except Exception:
                pass


def parse_google_browser_content(name: str, page_html: str) -> ScanOutcome:
    page_text = (page_html or "").lower()

    not_found_patterns = [
        "couldn't find your google account",
        "\u627e\u4e0d\u5230\u60a8\u7684 google \u8d26\u53f7",
        "find your google account",
        "no account found",
        "that google account doesn't exist",
        "couldn\u2019t find your google account",
    ]
    if any(pattern in page_text for pattern in not_found_patterns):
        return ScanOutcome(
            checked_delta=1,
            hit_delta=1,
            tag="hit",
            message_key="log_name_available",
            params={"name": name},
        )

    taken_patterns = [
        "wrong password",
        "enter your password",
        "welcome",
        "hi,",
    ]
    if any(pattern in page_text for pattern in taken_patterns):
        return ScanOutcome(
            checked_delta=1,
            taken_delta=1,
            tag="taken",
            message_key="log_name_taken",
            params={"name": name},
        )

    return ScanOutcome(
        error_delta=1,
        tag="error",
        message_key="log_browser_result_unknown",
        params={"name": name},
    )


def parse_browser_response(name: str, page, page_html: str, settings: RuntimeSettings) -> ScanOutcome:
    page_text = page_html.lower()

    available_selector_match = bool(
        settings.browser_available_selector.strip()
        and page.locator(settings.browser_available_selector.strip()).first.count() > 0
        and page.locator(settings.browser_available_selector.strip()).first.is_visible()
    )
    taken_selector_match = bool(
        settings.browser_taken_selector.strip()
        and page.locator(settings.browser_taken_selector.strip()).first.count() > 0
        and page.locator(settings.browser_taken_selector.strip()).first.is_visible()
    )

    available_text_match = bool(
        settings.browser_available_text.strip()
        and settings.browser_available_text.strip().lower() in page_text
    )
    taken_text_match = bool(
        settings.browser_taken_text.strip()
        and settings.browser_taken_text.strip().lower() in page_text
    )

    available_regex_match = bool(
        settings.browser_available_regex.strip()
        and re.search(settings.browser_available_regex.strip(), page_html, re.IGNORECASE)
    )
    taken_regex_match = bool(
        settings.browser_taken_regex.strip()
        and re.search(settings.browser_taken_regex.strip(), page_html, re.IGNORECASE)
    )

    available_match = available_selector_match or available_text_match or available_regex_match
    taken_match = taken_selector_match or taken_text_match or taken_regex_match

    if available_match and taken_match:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_browser_result_ambiguous",
            params={"name": name},
        )

    if available_match:
        return ScanOutcome(
            checked_delta=1,
            hit_delta=1,
            tag="hit",
            message_key="log_name_available",
            params={"name": name},
        )

    if taken_match:
        return ScanOutcome(
            checked_delta=1,
            taken_delta=1,
            tag="taken",
            message_key="log_name_taken",
            params={"name": name},
        )

    return ScanOutcome(
        error_delta=1,
        tag="error",
        message_key="log_browser_result_unknown",
        params={"name": name},
    )


def parse_network_response(
    provider: str,
    name: str,
    status_code: int,
    response_text: str,
    error_string: str,
    settings: RuntimeSettings | None = None,
) -> ScanOutcome:
    provider = normalize_provider(provider)

    if provider == "custom":
        if settings is None:
            return ScanOutcome(
                error_delta=1,
                tag="error",
                message_key="log_custom_result_unknown",
                params={"name": name},
            )

        expected_statuses = parse_custom_status_codes(settings.custom_status_codes)
        if expected_statuses is None:
            return ScanOutcome(
                error_delta=1,
                tag="error",
                message_key="log_custom_status_invalid",
                params={"value": settings.custom_status_codes},
            )
        if expected_statuses and status_code not in expected_statuses:
            return ScanOutcome(
                error_delta=1,
                tag="error",
                message_key="log_custom_status_unexpected",
                params={"name": name, "status": str(status_code)},
            )
        if not expected_statuses and status_code >= 400:
            return ScanOutcome(
                error_delta=1,
                tag="error",
                message_key="log_request_failed",
                params={"name": name, "error": f"HTTP {status_code}: {error_string}"},
            )

        available_keyword = (settings.custom_available_keyword if settings else "available").strip().lower()
        taken_keyword = (settings.custom_taken_keyword if settings else "taken").strip().lower()
        available_regex = settings.custom_available_regex.strip()
        taken_regex = settings.custom_taken_regex.strip()
        response_text_lower = response_text.lower()

        regex_error = validate_regex_pattern(available_regex) or validate_regex_pattern(taken_regex)
        if regex_error is not None:
            return ScanOutcome(
                error_delta=1,
                tag="error",
                message_key="log_custom_regex_invalid",
                params={"pattern": regex_error},
            )

        available_match = bool(available_regex and re.search(available_regex, response_text, re.IGNORECASE))
        taken_match = bool(taken_regex and re.search(taken_regex, response_text, re.IGNORECASE))

        if available_keyword and available_keyword in response_text_lower:
            available_match = True
        if taken_keyword and taken_keyword in response_text_lower:
            taken_match = True

        if available_match and taken_match:
            return ScanOutcome(
                error_delta=1,
                tag="error",
                message_key="log_custom_result_ambiguous",
                params={"name": name},
            )

        if available_match:
            return ScanOutcome(
                checked_delta=1,
                hit_delta=1,
                tag="hit",
                message_key="log_name_available",
                params={"name": name},
            )

        if taken_match:
            return ScanOutcome(
                checked_delta=1,
                taken_delta=1,
                tag="taken",
                message_key="log_name_taken",
                params={"name": name},
            )

        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_custom_result_unknown",
            params={"name": name},
        )

    if status_code >= 400:
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_request_failed",
            params={"name": name, "error": f"HTTP {status_code}: {error_string}"},
        )

    if "available" in response_text.lower():
        return ScanOutcome(
            checked_delta=1,
            hit_delta=1,
            tag="hit",
            message_key="log_name_available",
            params={"name": name},
        )

    return ScanOutcome(
        checked_delta=1,
        taken_delta=1,
        tag="taken",
        message_key="log_name_taken",
        params={"name": name},
    )


def normalize_custom_method(method: str) -> Literal["GET", "POST"]:
    return "POST" if (method or "").strip().upper() == "POST" else "GET"


def resolve_template(value: str, name: str) -> str:
    return (value or "").replace("{username}", name)


def build_custom_headers(raw_headers: str, name: str) -> dict[str, str]:
    headers: dict[str, str] = {}
    for line in (raw_headers or "").splitlines():
        entry = line.strip()
        if not entry or ":" not in entry:
            continue
        key, value = entry.split(":", 1)
        key = key.strip()
        value = value.strip().replace("{username}", name)
        if key:
            headers[key] = value
    return headers


def parse_custom_status_codes(raw_value: str) -> set[int] | None:
    cleaned = (raw_value or "").strip()
    if not cleaned:
        return set()

    results: set[int] = set()
    for chunk in cleaned.split(","):
        part = chunk.strip()
        if not part:
            continue
        if not part.isdigit():
            return None
        results.add(int(part))
    return results


def validate_regex_pattern(pattern: str) -> str | None:
    pattern = (pattern or "").strip()
    if not pattern:
        return None
    try:
        re.compile(pattern, re.IGNORECASE)
    except re.error:
        return pattern
    return None


def ensure_scan_not_canceled(cancel_event: Event | None) -> None:
    if cancel_event is not None and cancel_event.is_set():
        raise ScanCanceledError()


def wait_for_cancellation(delay_ms: int, cancel_event: Event | None) -> None:
    remaining = max(0, int(delay_ms))
    while remaining > 0:
        ensure_scan_not_canceled(cancel_event)
        sleep_ms = min(remaining, 100)
        time.sleep(sleep_ms / 1000)
        remaining -= sleep_ms
    ensure_scan_not_canceled(cancel_event)


def validate_browser_settings(settings: RuntimeSettings) -> str | None:
    if not settings.browser_url.strip():
        return "url"
    if "{username}" not in settings.browser_url and not settings.browser_input_selector.strip():
        return "input selector"

    has_available_rule = any(
        (
            settings.browser_available_selector.strip(),
            settings.browser_available_text.strip(),
            settings.browser_available_regex.strip(),
        )
    )
    has_taken_rule = any(
        (
            settings.browser_taken_selector.strip(),
            settings.browser_taken_text.strip(),
            settings.browser_taken_regex.strip(),
        )
    )

    if not has_available_rule and not has_taken_rule:
        return "result rule"
    return None
