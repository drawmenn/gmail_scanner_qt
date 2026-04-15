from collections import deque
from dataclasses import dataclass, field


DEFAULT_SEEDS = ["james", "alex"]
DEFAULT_PROXY_URL = "http://127.0.0.1:7897"
DEFAULT_MANUAL_AUTO_ACTION = "skip"
DEFAULT_CUSTOM_METHOD = "GET"
DEFAULT_CUSTOM_PARAM_NAME = "username"
DEFAULT_CUSTOM_AVAILABLE_KEYWORD = "available"
DEFAULT_CUSTOM_TAKEN_KEYWORD = "taken"
DEFAULT_CUSTOM_HEADERS = ""
DEFAULT_CUSTOM_BODY_TEMPLATE = ""
DEFAULT_CUSTOM_STATUS_CODES = ""
DEFAULT_CUSTOM_AVAILABLE_REGEX = ""
DEFAULT_CUSTOM_TAKEN_REGEX = ""
DEFAULT_BROWSER_VALUE_TEMPLATE = "{username}"
DEFAULT_BROWSER_CHANNEL = ""
DEFAULT_BROWSER_TIMEOUT_MS = 10000
DEFAULT_BROWSER_DELAY_MS = 800
MAX_HISTORY_POINTS = 100


@dataclass
class RuntimeSettings:
    seeds: list[str] = field(default_factory=lambda: DEFAULT_SEEDS.copy())
    proxy_enabled: bool = False
    proxy_url: str = DEFAULT_PROXY_URL
    language: str = "en"
    provider: str = "manual"
    manual_auto_enabled: bool = False
    manual_auto_action: str = DEFAULT_MANUAL_AUTO_ACTION
    custom_url: str = ""
    custom_method: str = DEFAULT_CUSTOM_METHOD
    custom_param_name: str = DEFAULT_CUSTOM_PARAM_NAME
    custom_headers: str = DEFAULT_CUSTOM_HEADERS
    custom_body_template: str = DEFAULT_CUSTOM_BODY_TEMPLATE
    custom_status_codes: str = DEFAULT_CUSTOM_STATUS_CODES
    custom_available_keyword: str = DEFAULT_CUSTOM_AVAILABLE_KEYWORD
    custom_taken_keyword: str = DEFAULT_CUSTOM_TAKEN_KEYWORD
    custom_available_regex: str = DEFAULT_CUSTOM_AVAILABLE_REGEX
    custom_taken_regex: str = DEFAULT_CUSTOM_TAKEN_REGEX
    browser_url: str = ""
    browser_input_selector: str = ""
    browser_value_template: str = DEFAULT_BROWSER_VALUE_TEMPLATE
    browser_submit_selector: str = ""
    browser_channel: str = DEFAULT_BROWSER_CHANNEL
    browser_headers: str = ""
    browser_available_selector: str = ""
    browser_available_text: str = ""
    browser_available_regex: str = ""
    browser_taken_selector: str = ""
    browser_taken_text: str = ""
    browser_taken_regex: str = ""
    browser_timeout_ms: int = DEFAULT_BROWSER_TIMEOUT_MS
    browser_delay_ms: int = DEFAULT_BROWSER_DELAY_MS
    browser_headless: bool = True

    def to_dict(self) -> dict:
        return {
            "seeds": list(self.seeds),
            "proxy_enabled": self.proxy_enabled,
            "proxy_url": self.proxy_url,
            "language": self.language,
            "provider": self.provider,
            "manual_auto_enabled": self.manual_auto_enabled,
            "manual_auto_action": self.manual_auto_action,
            "custom_url": self.custom_url,
            "custom_method": self.custom_method,
            "custom_param_name": self.custom_param_name,
            "custom_headers": self.custom_headers,
            "custom_body_template": self.custom_body_template,
            "custom_status_codes": self.custom_status_codes,
            "custom_available_keyword": self.custom_available_keyword,
            "custom_taken_keyword": self.custom_taken_keyword,
            "custom_available_regex": self.custom_available_regex,
            "custom_taken_regex": self.custom_taken_regex,
            "browser_url": self.browser_url,
            "browser_input_selector": self.browser_input_selector,
            "browser_value_template": self.browser_value_template,
            "browser_submit_selector": self.browser_submit_selector,
            "browser_channel": self.browser_channel,
            "browser_headers": self.browser_headers,
            "browser_available_selector": self.browser_available_selector,
            "browser_available_text": self.browser_available_text,
            "browser_available_regex": self.browser_available_regex,
            "browser_taken_selector": self.browser_taken_selector,
            "browser_taken_text": self.browser_taken_text,
            "browser_taken_regex": self.browser_taken_regex,
            "browser_timeout_ms": self.browser_timeout_ms,
            "browser_delay_ms": self.browser_delay_ms,
            "browser_headless": self.browser_headless,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RuntimeSettings":
        defaults = cls()
        return cls(
            seeds=list(data.get("seeds", defaults.seeds)),
            proxy_enabled=bool(data.get("proxy_enabled", defaults.proxy_enabled)),
            proxy_url=str(data.get("proxy_url", defaults.proxy_url)),
            language=str(data.get("language", defaults.language)),
            provider=str(data.get("provider", defaults.provider)),
            manual_auto_enabled=bool(data.get("manual_auto_enabled", defaults.manual_auto_enabled)),
            manual_auto_action=str(data.get("manual_auto_action", defaults.manual_auto_action)),
            custom_url=str(data.get("custom_url", defaults.custom_url)),
            custom_method=str(data.get("custom_method", defaults.custom_method)),
            custom_param_name=str(data.get("custom_param_name", defaults.custom_param_name)),
            custom_headers=str(data.get("custom_headers", defaults.custom_headers)),
            custom_body_template=str(data.get("custom_body_template", defaults.custom_body_template)),
            custom_status_codes=str(data.get("custom_status_codes", defaults.custom_status_codes)),
            custom_available_keyword=str(data.get("custom_available_keyword", defaults.custom_available_keyword)),
            custom_taken_keyword=str(data.get("custom_taken_keyword", defaults.custom_taken_keyword)),
            custom_available_regex=str(data.get("custom_available_regex", defaults.custom_available_regex)),
            custom_taken_regex=str(data.get("custom_taken_regex", defaults.custom_taken_regex)),
            browser_url=str(data.get("browser_url", defaults.browser_url)),
            browser_input_selector=str(data.get("browser_input_selector", defaults.browser_input_selector)),
            browser_value_template=str(data.get("browser_value_template", defaults.browser_value_template)),
            browser_submit_selector=str(data.get("browser_submit_selector", defaults.browser_submit_selector)),
            browser_channel=str(data.get("browser_channel", defaults.browser_channel)),
            browser_headers=str(data.get("browser_headers", defaults.browser_headers)),
            browser_available_selector=str(data.get("browser_available_selector", defaults.browser_available_selector)),
            browser_available_text=str(data.get("browser_available_text", defaults.browser_available_text)),
            browser_available_regex=str(data.get("browser_available_regex", defaults.browser_available_regex)),
            browser_taken_selector=str(data.get("browser_taken_selector", defaults.browser_taken_selector)),
            browser_taken_text=str(data.get("browser_taken_text", defaults.browser_taken_text)),
            browser_taken_regex=str(data.get("browser_taken_regex", defaults.browser_taken_regex)),
            browser_timeout_ms=int(data.get("browser_timeout_ms", defaults.browser_timeout_ms)),
            browser_delay_ms=int(data.get("browser_delay_ms", defaults.browser_delay_ms)),
            browser_headless=bool(data.get("browser_headless", defaults.browser_headless)),
        )


@dataclass
class ScanStats:
    checked: int = 0
    hit: int = 0
    taken: int = 0
    hold: int = 0
    error: int = 0

    @property
    def rate(self) -> float:
        return (self.hit / self.checked * 100) if self.checked else 0.0

    def to_payload(self) -> dict[str, int | float]:
        return {
            "checked": self.checked,
            "hit": self.hit,
            "taken": self.taken,
            "hold": self.hold,
            "error": self.error,
            "rate": self.rate,
        }


@dataclass
class ScanHistory:
    checked: deque = field(default_factory=lambda: deque(maxlen=MAX_HISTORY_POINTS))
    hit: deque = field(default_factory=lambda: deque(maxlen=MAX_HISTORY_POINTS))
    rate: deque = field(default_factory=lambda: deque(maxlen=MAX_HISTORY_POINTS))

    def append(self, stats: ScanStats) -> None:
        self.checked.append(stats.checked)
        self.hit.append(stats.hit)
        self.rate.append(stats.rate)

    def to_payload(self) -> dict[str, list[int] | list[float]]:
        return {
            "checked": list(self.checked),
            "hit": list(self.hit),
            "rate": list(self.rate),
        }
