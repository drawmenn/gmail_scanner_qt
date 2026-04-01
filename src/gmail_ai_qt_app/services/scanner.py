import random
from threading import Lock
from typing import Iterable

from PySide6.QtCore import QByteArray, QObject, QTimer, QUrl, QUrlQuery, Signal, Slot
from PySide6.QtNetwork import (
    QNetworkAccessManager,
    QNetworkProxy,
    QNetworkReply,
    QNetworkRequest,
)

from ..models.state import RuntimeSettings, ScanHistory, ScanStats
from .providers import ScanOutcome, normalize_provider, parse_network_response, prepare_scan, run_local_scan


class ScannerWorker(QObject):
    log_signal = Signal(str, str, object)
    snapshot_signal = Signal(dict)
    request_state_signal = Signal(str, object)

    _set_names_requested = Signal(list)
    _set_proxy_requested = Signal(bool, str)
    _set_provider_requested = Signal(str)
    _set_custom_config_requested = Signal(dict)
    _set_browser_config_requested = Signal(dict)
    _submit_manual_decision_requested = Signal(str)
    _skip_manual_candidate_requested = Signal()
    _start_requested = Signal()
    _pause_requested = Signal()
    _stop_requested = Signal()
    _shutdown_requested = Signal()

    def __init__(self, settings: RuntimeSettings):
        super().__init__()
        self._lock = Lock()
        self._settings = RuntimeSettings.from_dict(settings.to_dict())
        self._running = False
        self._paused = False
        self._generation = 0
        self._stats = ScanStats()
        self._history = ScanHistory()
        self._network_manager: QNetworkAccessManager | None = None
        self._request_timer: QTimer | None = None
        self._current_reply: QNetworkReply | None = None
        self._pending_candidate: str | None = None
        self._request_interval_ms = 500
        self._candidate_index = 0
        self._pool_exhausted = False
        self._explicit_candidates: list[str] = []
        self._short_seeds: list[str] = []
        self._rebuild_name_pool_locked(self._settings.seeds)

        self._set_names_requested.connect(self._set_names)
        self._set_proxy_requested.connect(self._set_proxy_config)
        self._set_provider_requested.connect(self._set_provider)
        self._set_custom_config_requested.connect(self._set_custom_config)
        self._set_browser_config_requested.connect(self._set_browser_config)
        self._submit_manual_decision_requested.connect(self._submit_manual_decision)
        self._skip_manual_candidate_requested.connect(self._skip_manual_candidate)
        self._start_requested.connect(self._start_scanning)
        self._pause_requested.connect(self._pause_scanning)
        self._stop_requested.connect(self._stop_scanning)
        self._shutdown_requested.connect(self._shutdown)

    @Slot()
    def initialize(self) -> None:
        self._network_manager = QNetworkAccessManager(self)
        self._network_manager.finished.connect(self._handle_reply_finished)

        self._request_timer = QTimer(self)
        self._request_timer.setSingleShot(True)
        self._request_timer.timeout.connect(self._start_next_request)
        self._emit_request_state("idle")

    def set_names(self, names: Iterable[str]) -> None:
        self._set_names_requested.emit(list(names))

    def set_proxy_config(self, enabled: bool, proxy_url: str) -> None:
        self._set_proxy_requested.emit(enabled, proxy_url)

    def set_provider(self, provider: str) -> None:
        self._set_provider_requested.emit(provider)

    def set_custom_config(self, config: dict[str, str]) -> None:
        self._set_custom_config_requested.emit(dict(config))

    def set_browser_config(self, config: dict) -> None:
        self._set_browser_config_requested.emit(dict(config))

    def submit_manual_decision(self, decision: str) -> None:
        self._submit_manual_decision_requested.emit(decision)

    def skip_manual_candidate(self) -> None:
        self._skip_manual_candidate_requested.emit()

    def start_scanning(self) -> None:
        self._start_requested.emit()

    def pause_scanning(self) -> None:
        self._pause_requested.emit()

    def stop_scanning(self) -> None:
        self._stop_requested.emit()

    def shutdown(self) -> None:
        self._shutdown_requested.emit()

    def snapshot(self) -> dict:
        with self._lock:
            return self._snapshot_payload_locked()

    @Slot(list)
    def _set_names(self, names: list[str]) -> None:
        with self._lock:
            self._settings.seeds = list(names)
            self._generation += 1
            self._pending_candidate = None
            self._candidate_index = 0
            self._pool_exhausted = False
            self._rebuild_name_pool_locked(self._settings.seeds)

        self._stop_request_timer()
        self._abort_current_reply()
        self._emit_request_state("idle")
        self._schedule_next_request(0)

    @Slot(bool, str)
    def _set_proxy_config(self, enabled: bool, proxy_url: str) -> None:
        with self._lock:
            self._settings.proxy_enabled = enabled
            self._settings.proxy_url = proxy_url.strip()

    @Slot(str)
    def _set_provider(self, provider: str) -> None:
        with self._lock:
            self._settings.provider = normalize_provider(provider)
            self._generation += 1
            self._pending_candidate = None
            self._candidate_index = 0
            self._pool_exhausted = False
            self._rebuild_name_pool_locked(self._settings.seeds)

        self._stop_request_timer()
        self._abort_current_reply()
        self._emit_request_state("idle")
        self._schedule_next_request(0)

    @Slot(dict)
    def _set_custom_config(self, config: dict) -> None:
        with self._lock:
            self._settings.custom_url = str(config.get("url", "")).strip()
            self._settings.custom_method = str(config.get("method", "GET")).strip().upper() or "GET"
            self._settings.custom_param_name = str(config.get("param_name", "username")).strip() or "username"
            self._settings.custom_headers = str(config.get("headers", ""))
            self._settings.custom_body_template = str(config.get("body_template", ""))
            self._settings.custom_status_codes = str(config.get("status_codes", "")).strip()
            self._settings.custom_available_keyword = str(config.get("available_keyword", "available")).strip()
            self._settings.custom_taken_keyword = str(config.get("taken_keyword", "taken")).strip()
            self._settings.custom_available_regex = str(config.get("available_regex", "")).strip()
            self._settings.custom_taken_regex = str(config.get("taken_regex", "")).strip()
            if self._settings.provider == "custom":
                self._generation += 1
                self._pending_candidate = None

        if self._settings.provider == "custom":
            self._stop_request_timer()
            self._abort_current_reply()
            self._emit_request_state("idle")
            self._schedule_next_request(0)

    @Slot(dict)
    def _set_browser_config(self, config: dict) -> None:
        with self._lock:
            self._settings.browser_url = str(config.get("url", "")).strip()
            self._settings.browser_input_selector = str(config.get("input_selector", "")).strip()
            self._settings.browser_value_template = str(config.get("value_template", "{username}"))
            self._settings.browser_submit_selector = str(config.get("submit_selector", "")).strip()
            self._settings.browser_headers = str(config.get("headers", ""))
            self._settings.browser_available_selector = str(config.get("available_selector", "")).strip()
            self._settings.browser_available_text = str(config.get("available_text", "")).strip()
            self._settings.browser_available_regex = str(config.get("available_regex", "")).strip()
            self._settings.browser_taken_selector = str(config.get("taken_selector", "")).strip()
            self._settings.browser_taken_text = str(config.get("taken_text", "")).strip()
            self._settings.browser_taken_regex = str(config.get("taken_regex", "")).strip()
            self._settings.browser_timeout_ms = int(config.get("timeout_ms", 10_000) or 10_000)
            self._settings.browser_delay_ms = int(config.get("delay_ms", 800) or 800)
            self._settings.browser_headless = bool(config.get("headless", True))
            if self._settings.provider == "playwright":
                self._generation += 1
                self._pending_candidate = None

        if self._settings.provider == "playwright":
            self._stop_request_timer()
            self._abort_current_reply()
            self._emit_request_state("idle")
            self._schedule_next_request(0)

    @Slot()
    def _start_scanning(self) -> None:
        with self._lock:
            self._running = True
            self._paused = False
            self._generation += 1
            self._pending_candidate = None
            self._candidate_index = 0
            self._pool_exhausted = False
        self._emit_request_state("idle")
        self._schedule_next_request(0)

    @Slot()
    def _pause_scanning(self) -> None:
        with self._lock:
            if self._running:
                self._paused = True
                self._generation += 1
                self._pending_candidate = None
        self._stop_request_timer()
        if self._abort_current_reply():
            self._emit_request_state("canceled")
        else:
            self._emit_request_state("idle")

    @Slot()
    def _stop_scanning(self) -> None:
        with self._lock:
            self._running = False
            self._paused = False
            self._generation += 1
            self._pending_candidate = None
            self._candidate_index = 0
            self._pool_exhausted = False
        self._stop_request_timer()
        if self._abort_current_reply():
            self._emit_request_state("canceled")
        else:
            self._emit_request_state("idle")

    @Slot()
    def _shutdown(self) -> None:
        self._stop_scanning()

    @Slot()
    def _start_next_request(self) -> None:
        if self._network_manager is None or self._current_reply is not None:
            return

        with self._lock:
            if not self._running or self._paused or not self._settings.seeds:
                return
            generation = self._generation
            provider = self._settings.provider
            proxy_enabled = self._settings.proxy_enabled
            proxy_url = self._settings.proxy_url
            seed_count = len(self._settings.seeds)
            name = self._build_candidate_locked()

        if not name:
            self.log_signal.emit(
                "log_candidate_pool_exhausted",
                "info",
                {"count": seed_count},
            )
            self._emit_request_state("idle")
            return
        prepared = prepare_scan(provider, name, self._settings)

        if provider == "manual":
            with self._lock:
                self._pending_candidate = name
            self._emit_request_state("reviewing", {"name": name})
            return

        if prepared.mode == "local":
            self._emit_request_state("requesting", {"name": name})
            self._complete_outcome(run_local_scan(provider, name, self._settings))
            self._emit_request_state("idle")
            self._schedule_next_request(self._request_interval_ms)
            return

        self._apply_proxy(proxy_enabled, proxy_url)

        url = QUrl(prepared.url)
        query = QUrlQuery()
        for key, value in prepared.query.items():
            query.addQueryItem(key, value)
        url.setQuery(query)

        request = QNetworkRequest(url)
        request.setTransferTimeout(prepared.timeout_ms)
        for key, value in prepared.headers.items():
            request.setRawHeader(key.encode("utf-8"), value.encode("utf-8"))

        if prepared.method == "POST":
            reply = self._network_manager.post(request, QByteArray(prepared.body.encode("utf-8")))
        else:
            reply = self._network_manager.get(request)
        reply.setProperty("generation", generation)
        reply.setProperty("candidate_name", name)
        reply.setProperty("provider", provider)
        self._current_reply = reply
        self._emit_request_state("requesting", {"name": name})

    @Slot(QNetworkReply)
    def _handle_reply_finished(self, reply: QNetworkReply) -> None:
        if reply is self._current_reply:
            self._current_reply = None

        generation = int(reply.property("generation") or -1)
        name = str(reply.property("candidate_name") or "")
        provider = str(reply.property("provider") or "mock")

        with self._lock:
            is_current = self._generation == generation and self._running and not self._paused

        # Ignore stale or manually aborted requests after stop/pause/restart.
        if not is_current:
            reply.deleteLater()
            self._schedule_next_request(0)
            return

        if reply.error() != QNetworkReply.NetworkError.NoError:
            if reply.error() == QNetworkReply.NetworkError.OperationCanceledError:
                self._emit_request_state("canceled")
                reply.deleteLater()
                self._schedule_next_request(0)
                return

            status_code = int(reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute) or 0)
            outcome = parse_network_response(
                provider,
                name,
                status_code,
                "",
                reply.errorString(),
                self._settings,
            )
            self._complete_outcome(outcome)
            self._emit_request_state("error", {"error": reply.errorString()})
            reply.deleteLater()
            self._schedule_next_request(self._request_interval_ms)
            return

        response_text = bytes(reply.readAll()).decode("utf-8", errors="ignore")
        status_code = int(reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute) or 0)
        outcome = parse_network_response(
            provider,
            name,
            status_code,
            response_text,
            reply.errorString(),
            self._settings,
        )
        self._complete_outcome(outcome)
        self._emit_request_state("idle")
        reply.deleteLater()
        self._schedule_next_request(self._request_interval_ms)

    @Slot(str)
    def _submit_manual_decision(self, decision: str) -> None:
        with self._lock:
            provider = self._settings.provider
            candidate = self._pending_candidate
            is_active = self._running and not self._paused
            if provider != "manual" or not is_active or not candidate:
                return
            self._pending_candidate = None

        outcome = self._manual_outcome(candidate, decision)
        self._complete_outcome(outcome)
        self._emit_request_state("idle")
        self._schedule_next_request(0)

    @Slot()
    def _skip_manual_candidate(self) -> None:
        with self._lock:
            provider = self._settings.provider
            candidate = self._pending_candidate
            is_active = self._running and not self._paused
            if provider != "manual" or not is_active or not candidate:
                return
            self._pending_candidate = None

        self.log_signal.emit("log_name_skipped", "info", {"name": candidate})
        self._emit_request_state("idle")
        self._schedule_next_request(0)

    def _schedule_next_request(self, delay_ms: int) -> None:
        if self._request_timer is None or self._current_reply is not None:
            return

        with self._lock:
            can_schedule = (
                self._running
                and not self._paused
                and bool(self._settings.seeds)
                and self._pending_candidate is None
                and not self._pool_exhausted
            )

        if can_schedule:
            self._request_timer.start(max(0, delay_ms))

    def _stop_request_timer(self) -> None:
        if self._request_timer is not None and self._request_timer.isActive():
            self._request_timer.stop()

    def _abort_current_reply(self) -> bool:
        if self._current_reply is not None and self._current_reply.isRunning():
            self._current_reply.abort()
            return True
        return False

    def _apply_proxy(self, enabled: bool, proxy_url: str) -> None:
        if self._network_manager is None:
            return

        proxy_url = proxy_url.strip()
        if not enabled or not proxy_url:
            self._network_manager.setProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))
            return

        parsed = QUrl(proxy_url if "://" in proxy_url else f"http://{proxy_url}")
        if not parsed.isValid() or not parsed.host():
            self._network_manager.setProxy(QNetworkProxy(QNetworkProxy.ProxyType.NoProxy))
            return

        proxy_type = QNetworkProxy.ProxyType.Socks5Proxy
        if parsed.scheme().lower() not in {"socks5", "socks"}:
            proxy_type = QNetworkProxy.ProxyType.HttpProxy

        proxy = QNetworkProxy(proxy_type)
        proxy.setHostName(parsed.host())
        proxy.setPort(parsed.port(0))
        if parsed.userName():
            proxy.setUser(parsed.userName())
        if parsed.password():
            proxy.setPassword(parsed.password())
        self._network_manager.setProxy(proxy)

    def _snapshot_payload_locked(self) -> dict:
        return {
            "stats": self._stats.to_payload(),
            "history": self._history.to_payload(),
        }

    def _complete_outcome(self, outcome) -> None:
        with self._lock:
            self._stats.checked += outcome.checked_delta
            self._stats.hit += outcome.hit_delta
            self._stats.taken += outcome.taken_delta
            self._stats.hold += outcome.hold_delta
            self._stats.error += outcome.error_delta
            if (
                outcome.checked_delta
                or outcome.hit_delta
                or outcome.taken_delta
                or outcome.hold_delta
                or outcome.error_delta
            ):
                self._history.append(self._stats)
            payload = self._snapshot_payload_locked()

        if outcome.message_key:
            self.log_signal.emit(outcome.message_key, outcome.tag, outcome.params)
        self.snapshot_signal.emit(payload)

    def _emit_request_state(self, state: str, params: dict | None = None) -> None:
        self.request_state_signal.emit(state, params or {})

    def _rebuild_name_pool_locked(self, names: Iterable[str]) -> None:
        self._explicit_candidates = [
            item.strip().lower()
            for item in names
            if self._is_explicit_candidate(item)
        ]
        self._short_seeds = [
            item.strip().lower() for item in names if item and item.strip()
        ]

    def _build_candidate_locked(self) -> str | None:
        if self._explicit_candidates:
            if self._candidate_index >= len(self._explicit_candidates):
                self._pool_exhausted = True
                return None
            candidate = self._explicit_candidates[self._candidate_index]
            self._candidate_index += 1
            return candidate

        if not self._short_seeds:
            return None

        base = random.choice(self._short_seeds)
        suffix_length = max(0, 6 - len(base))
        suffix = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(suffix_length))
        return (base + suffix)[:6]

    @staticmethod
    def _is_explicit_candidate(value: str) -> bool:
        candidate = (value or "").strip().lower()
        return 6 <= len(candidate) <= 30 and candidate.isalnum()

    @staticmethod
    def _manual_outcome(name: str, decision: str) -> ScanOutcome:
        decision = (decision or "").lower()
        if decision == "available":
            return ScanOutcome(
                checked_delta=1,
                hit_delta=1,
                tag="hit",
                message_key="log_name_available",
                params={"name": name},
            )
        if decision == "taken":
            return ScanOutcome(
                checked_delta=1,
                taken_delta=1,
                tag="taken",
                message_key="log_name_taken",
                params={"name": name},
            )
        if decision == "hold":
            return ScanOutcome(
                checked_delta=1,
                hold_delta=1,
                tag="info",
                message_key="log_name_hold",
                params={"name": name},
            )
        return ScanOutcome(
            error_delta=1,
            tag="error",
            message_key="log_manual_decision_error",
            params={"name": name, "decision": decision or "unknown"},
        )
