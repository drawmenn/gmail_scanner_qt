import os
from pathlib import Path
import sys

from PySide6.QtCore import QDateTime, QProcess, QProcessEnvironment, QThread, QTimer
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox

if __package__ in (None, ""):
    SRC_ROOT = Path(__file__).resolve().parents[2]
    if str(SRC_ROOT) not in sys.path:
        sys.path.insert(0, str(SRC_ROOT))

    from gmail_ai_qt_app.i18n import translate
    from gmail_ai_qt_app.models.state import RuntimeSettings
    from gmail_ai_qt_app.services.playwright_installer import (
        normalize_browser_channel,
        chromium_install_command,
        is_chromium_ready,
        parse_playwright_install_progress,
        provider_requires_chromium,
    )
    from gmail_ai_qt_app.services.settings_store import RuntimeSettingsStore
    from gmail_ai_qt_app.services.seed_utils import sanitize_seed_values
    from gmail_ai_qt_app.ui.actions_presenter import MainWindowActionsPresenter
    from gmail_ai_qt_app.ui.chart_presenter import MainWindowChartPresenter
    from gmail_ai_qt_app.ui.layout_builder import MainWindowLayoutBuilder
    from gmail_ai_qt_app.ui.log_buffer import LogBuffer, LogEntry
    from gmail_ai_qt_app.ui.runtime_presenter import MainWindowRuntimePresenter
    from gmail_ai_qt_app.ui.settings_presenter import MainWindowSettingsPresenter
    from gmail_ai_qt_app.ui.state_presenter import MainWindowStatePresenter
    from gmail_ai_qt_app.ui.styles import main_window_qss
    from gmail_ai_qt_app.ui.translation_presenter import MainWindowTranslationPresenter
    from gmail_ai_qt_app.services.scanner import ScannerWorker
else:
    from ..i18n import translate
    from ..models.state import RuntimeSettings
    from ..services.playwright_installer import (
        normalize_browser_channel,
        chromium_install_command,
        is_chromium_ready,
        parse_playwright_install_progress,
        provider_requires_chromium,
    )
    from ..services.settings_store import RuntimeSettingsStore
    from ..services.seed_utils import sanitize_seed_values
    from .actions_presenter import MainWindowActionsPresenter
    from .chart_presenter import MainWindowChartPresenter
    from ..services.scanner import ScannerWorker
    from .layout_builder import MainWindowLayoutBuilder
    from .log_buffer import LogBuffer, LogEntry
    from .runtime_presenter import MainWindowRuntimePresenter
    from .settings_presenter import MainWindowSettingsPresenter
    from .state_presenter import MainWindowStatePresenter
    from .styles import main_window_qss
    from .translation_presenter import MainWindowTranslationPresenter


def _is_compiled_runtime() -> bool:
    return bool(
        getattr(sys, "frozen", False)
        or globals().get("__compiled__") is not None
        or os.environ.get("NUITKA_ONEFILE_DIRECTORY", "").strip()
    )


class MainWindow(QMainWindow):
    MANUAL_REVIEW_URL = "https://accounts.google.com/signin"
    AUTO_REVIEW_DELAY_MS = 350
    AUTO_REVIEW_ACTIONS = ("available", "taken", "hold", "skip")
    LOG_FLUSH_INTERVAL_MS = 200

    def __init__(self):
        super().__init__()
        self.settings_store = RuntimeSettingsStore()
        self.runtime_settings, _load_error = self.settings_store.load()
        self.runtime_settings.seeds = sanitize_seed_values(self.runtime_settings.seeds)
        if _load_error:
            import sys
            print(f"[gmail-ai-qt] Failed to load settings: {_load_error}", file=sys.stderr)
        self.runtime_state = "stopped"
        self.current_note_key = "runtime_note_stopped"
        self.current_request_state = "idle"
        self.current_request_params: dict = {}
        self.current_review_candidate = ""
        self.review_records: list[dict] = []
        self.chromium_install_process: QProcess | None = None
        self.chromium_install_output = ""
        self.chromium_install_error = ""
        self.chromium_install_canceled = False
        self.resume_scan_after_chromium_install = False
        self.chromium_install_status_state = "hidden"
        self.chromium_install_status_detail = ""
        self.chromium_install_progress = None
        self.last_snapshot = {
            "stats": {"checked": 0, "hit": 0, "error": 0, "rate": 0.0},
            "history": {"checked": [], "hit": [], "rate": []},
        }

        self.resize(1240, 800)
        self.setMinimumSize(960, 660)
        self.setStyleSheet(main_window_qss())

        self.build_ui()
        self._sync_insights_panel_height()

        # 初始化presenters
        self.actions_presenter = MainWindowActionsPresenter(self)
        self.chart_presenter = MainWindowChartPresenter(self)
        self.runtime_presenter = MainWindowRuntimePresenter(self)
        self.settings_presenter = MainWindowSettingsPresenter(self)
        self.state_presenter = MainWindowStatePresenter(self)
        self.translation_presenter = MainWindowTranslationPresenter(self)
        self.load_runtime_settings_into_controls()

        # 假设layout_builder定义了self.log
        self.log_buffer = LogBuffer(
            self.log,
            self._translate_log_message,
            self._translate_log_tag,
        )

        self.apply_translations()
        self.configure_plots()

        self.auto_review_timer = QTimer(self)
        self.auto_review_timer.setSingleShot(True)
        self.auto_review_timer.timeout.connect(self.run_auto_review_action)

        self.chromium_install_status_timer = QTimer(self)
        self.chromium_install_status_timer.setSingleShot(True)
        self.chromium_install_status_timer.timeout.connect(self.clear_chromium_install_status)

        self._log_flush_timer = QTimer(self)
        self._log_flush_timer.setInterval(self.LOG_FLUSH_INTERVAL_MS)
        self._log_flush_timer.timeout.connect(self.flush_log_entries)
        self._log_flush_timer.start()

        self.scanner_thread = QThread(self)
        self.worker = ScannerWorker(self.runtime_settings)
        self.worker.moveToThread(self.scanner_thread)
        self.scanner_thread.started.connect(self.worker.initialize)
        self.worker.log_signal.connect(self.add_log_event)
        self.worker.snapshot_signal.connect(self.apply_snapshot)
        self.worker.request_state_signal.connect(self.update_request_status)
        self.scanner_thread.finished.connect(self.worker.deleteLater)
        self.scanner_thread.start()

        self._connect_ui_signals()

        self.refresh_seed_summary()
        self.sync_provider_settings()
        self.sync_custom_provider_settings()
        self.sync_browser_provider_settings()
        self.sync_auto_review_settings()
        self.sync_proxy_settings()
        self.apply_snapshot(self.worker.snapshot())
        self.refresh_request_status()
        self.refresh_chromium_install_banner()
        self.refresh_review_panel()
        self.refresh_runtime_panel("runtime_note_stopped")
        self.add_log_event("log_dashboard_ready", "info")
        QTimer.singleShot(0, self.maybe_request_chromium_on_launch)

    def text(self, key: str, **params) -> str:
        return translate(self.runtime_settings.language, key, **params)

    def _translate_log_message(self, key: str, params: dict[str, str]) -> str:
        return self.text(key, **params)

    def _translate_log_tag(self, tag: str) -> str:
        return self.text(f"log_tag_{tag}")

    def build_ui(self) -> None:
        builder = MainWindowLayoutBuilder(self)
        central_widget = builder.build()
        self.setCentralWidget(central_widget)

    def _sync_insights_panel_height(self) -> None:
        panel = getattr(self, "insights_panel", None)
        if panel is None:
            return

        panel.setMaximumHeight(max(360, self.height() - 355))

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._sync_insights_panel_height()

    def load_runtime_settings_into_controls(self) -> None:
        settings = self.runtime_settings
        self.name_list.clear()
        self.name_list.addItems(settings.seeds)

        self.proxy_check.setChecked(settings.proxy_enabled)
        self.proxy_input.setText(settings.proxy_url)

        self.custom_url_input.setText(settings.custom_url)
        self.custom_param_input.setText(settings.custom_param_name)
        self.custom_status_input.setText(settings.custom_status_codes)
        self.custom_headers_input.setPlainText(settings.custom_headers)
        self.custom_body_input.setPlainText(settings.custom_body_template)
        self.custom_available_input.setText(settings.custom_available_keyword)
        self.custom_taken_input.setText(settings.custom_taken_keyword)
        self.custom_available_regex_input.setText(settings.custom_available_regex)
        self.custom_taken_regex_input.setText(settings.custom_taken_regex)

        self.browser_headless_check.setChecked(settings.browser_headless)
        self.browser_url_input.setText(settings.browser_url)
        self.browser_input_input.setText(settings.browser_input_selector)
        self.browser_value_input.setText(settings.browser_value_template or "{username}")
        self.browser_submit_input.setText(settings.browser_submit_selector)
        runtime_index = self.browser_runtime_combo.findData(settings.browser_channel)
        if runtime_index >= 0:
            self.browser_runtime_combo.setCurrentIndex(runtime_index)
        self.browser_timeout_spin.setValue(int(settings.browser_timeout_ms or 10_000))
        self.browser_delay_spin.setValue(int(settings.browser_delay_ms or 800))
        self.browser_available_selector_input.setText(settings.browser_available_selector)
        self.browser_available_text_input.setText(settings.browser_available_text)
        self.browser_available_regex_input.setText(settings.browser_available_regex)
        self.browser_taken_selector_input.setText(settings.browser_taken_selector)
        self.browser_taken_text_input.setText(settings.browser_taken_text)
        self.browser_taken_regex_input.setText(settings.browser_taken_regex)
        self.browser_headers_input.setPlainText(settings.browser_headers)

        self.auto_review_check.setChecked(settings.manual_auto_enabled)

    def _connect_ui_signals(self) -> None:
        self.name_list.installEventFilter(self)

        self.start_btn.clicked.connect(self.start)
        self.pause_btn.clicked.connect(self.pause)
        self.stop_btn.clicked.connect(self.stop)

        self.language_combo.currentIndexChanged.connect(self.change_language)
        self.provider_combo.currentIndexChanged.connect(self.change_provider)
        self.browser_runtime_combo.currentIndexChanged.connect(self.sync_browser_provider_settings)

        self.add_btn.clicked.connect(self.add_name)
        self.remove_btn.clicked.connect(self.remove_selected_name)
        self.generate_candidates_btn.clicked.connect(self.generate_name_pool)
        self.name_input.returnPressed.connect(self.add_name)

        self.mark_available_btn.clicked.connect(lambda: self.submit_manual_decision("available"))
        self.mark_taken_btn.clicked.connect(lambda: self.submit_manual_decision("taken"))
        self.mark_hold_btn.clicked.connect(lambda: self.submit_manual_decision("hold"))
        self.skip_candidate_btn.clicked.connect(self.skip_manual_candidate)
        self.copy_candidate_btn.clicked.connect(self.copy_current_candidate)
        self.open_review_page_btn.clicked.connect(self.open_manual_review_page)
        self.export_csv_btn.clicked.connect(self.export_review_records)

        self.auto_review_check.toggled.connect(self.sync_auto_review_settings)
        self.auto_review_action_combo.currentIndexChanged.connect(self.sync_auto_review_settings)

        self.proxy_check.toggled.connect(self.sync_proxy_settings)
        self.proxy_input.editingFinished.connect(self.sync_proxy_settings)

        self.custom_method_combo.currentIndexChanged.connect(self.sync_custom_provider_settings)
        for widget in (
            self.custom_url_input,
            self.custom_param_input,
            self.custom_status_input,
            self.custom_available_input,
            self.custom_taken_input,
            self.custom_available_regex_input,
            self.custom_taken_regex_input,
        ):
            widget.editingFinished.connect(self.sync_custom_provider_settings)
        self.custom_headers_input.textChanged.connect(self.sync_custom_provider_settings)
        self.custom_body_input.textChanged.connect(self.sync_custom_provider_settings)

        self.browser_headless_check.toggled.connect(self.sync_browser_provider_settings)
        self.browser_timeout_spin.valueChanged.connect(self.sync_browser_provider_settings)
        self.browser_delay_spin.valueChanged.connect(self.sync_browser_provider_settings)
        for widget in (
            self.browser_url_input,
            self.browser_input_input,
            self.browser_value_input,
            self.browser_submit_input,
            self.browser_available_selector_input,
            self.browser_available_text_input,
            self.browser_available_regex_input,
            self.browser_taken_selector_input,
            self.browser_taken_text_input,
            self.browser_taken_regex_input,
        ):
            widget.editingFinished.connect(self.sync_browser_provider_settings)
        self.browser_headers_input.textChanged.connect(self.sync_browser_provider_settings)

        self.install_cancel_btn.clicked.connect(self.cancel_chromium_installation)

    def apply_translations(self) -> None:
        self.translation_presenter.apply_translations()

    def configure_plots(self) -> None:
        self.chart_presenter.configure_plots()

    def apply_snapshot(self, payload: dict) -> None:
        self.chart_presenter.apply_snapshot(payload)

    def add_log_event(self, message_key: str, tag: str, params=None) -> None:
        entry = LogEntry(
            stamp=QDateTime.currentDateTime().toString("HH:mm:ss"),
            message_key=message_key,
            tag=tag,
            params=dict(params or {}),
        )
        self.log_buffer.add_entry(entry)
        self._handle_runtime_browser_missing(message_key)

    def _handle_runtime_browser_missing(self, message_key: str) -> None:
        if message_key != "log_browser_chromium_missing":
            return
        if not provider_requires_chromium(self.runtime_settings.provider):
            return

        resume_scan = self.runtime_state == "running"
        if resume_scan:
            self.pause()
        self.request_chromium_install(resume_scan=resume_scan, skip_installed_check=True)

    def maybe_request_chromium_on_launch(self) -> None:
        if not _is_compiled_runtime():
            return
        if not provider_requires_chromium(self.runtime_settings.provider):
            return
        if normalize_browser_channel(self.runtime_settings.browser_channel):
            return
        self.request_chromium_install(resume_scan=False)

    def set_chromium_install_status(
        self,
        state: str,
        detail: str = "",
        auto_hide_ms: int = 0,
    ) -> None:
        self.chromium_install_status_timer.stop()
        self.chromium_install_status_state = state
        self.chromium_install_status_detail = detail.strip()
        self.refresh_chromium_install_banner()
        if auto_hide_ms > 0:
            self.chromium_install_status_timer.start(auto_hide_ms)

    def clear_chromium_install_status(self) -> None:
        self.chromium_install_status_timer.stop()
        self.chromium_install_status_state = "hidden"
        self.chromium_install_status_detail = ""
        self.chromium_install_progress = None
        self.refresh_chromium_install_banner()

    def ensure_chromium_ready(self) -> bool:
        if not provider_requires_chromium(self.runtime_settings.provider):
            return True

        return self.request_chromium_install(resume_scan=True)

    def request_chromium_install(
        self,
        *,
        resume_scan: bool,
        skip_installed_check: bool = False,
    ) -> bool:
        browser_channel = normalize_browser_channel(self.runtime_settings.browser_channel)
        if self.chromium_install_process is not None:
            self.resume_scan_after_chromium_install = self.resume_scan_after_chromium_install or resume_scan
            self.add_log_event("log_browser_install_running", "info")
            return False

        if not skip_installed_check and is_chromium_ready(
            self.runtime_settings.provider,
            self.runtime_settings.browser_headless,
            browser_channel,
        ):
            return True

        if browser_channel:
            provider_label = self.provider_combo.currentText() or self.runtime_settings.provider
            self.add_log_event("log_browser_channel_missing", "error")
            QMessageBox.warning(
                self,
                self.text("browser_runtime_title"),
                self.text("browser_runtime_system_missing_message", provider=provider_label),
            )
            return False

        install_command = chromium_install_command()
        if install_command is None:
            self.add_log_event("log_browser_dependency_missing", "error")
            QMessageBox.warning(
                self,
                self.text("browser_install_title"),
                self.text("browser_install_dependency_missing"),
            )
            return False

        provider_label = self.provider_combo.currentText() or self.runtime_settings.provider
        answer = QMessageBox.question(
            self,
            self.text("browser_install_title"),
            self.text("browser_install_missing_prompt", provider=provider_label),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self.add_log_event(
                "log_browser_install_declined",
                "info",
                {"provider": provider_label},
            )
            return False

        self.start_chromium_installation(install_command, resume_scan=resume_scan)
        return False

    def start_chromium_installation(self, install_command, resume_scan: bool) -> None:
        if self.chromium_install_process is not None:
            return

        self.resume_scan_after_chromium_install = resume_scan
        self.chromium_install_output = ""
        self.chromium_install_error = ""
        self.chromium_install_canceled = False
        self.chromium_install_progress = None

        process = QProcess(self)
        process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)

        environment = QProcessEnvironment.systemEnvironment()
        for key, value in install_command.env.items():
            environment.insert(key, value)
        browsers_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "").strip()
        if browsers_path:
            environment.insert("PLAYWRIGHT_BROWSERS_PATH", browsers_path)
        process.setProcessEnvironment(environment)

        process.readyRead.connect(self._read_chromium_install_output)
        process.errorOccurred.connect(self._handle_chromium_install_error)
        process.finished.connect(self._finish_chromium_installation)

        self.chromium_install_process = process

        self.add_log_event("log_browser_install_started", "info")
        self.set_chromium_install_status("running")
        process.start(install_command.program, list(install_command.arguments))

    def cancel_chromium_installation(self) -> None:
        if self.chromium_install_process is None:
            return
        self.chromium_install_canceled = True
        self.resume_scan_after_chromium_install = False
        self.set_chromium_install_status("running", self.text("browser_install_canceling"))
        self.chromium_install_process.kill()

    def shutdown_chromium_installation(self) -> None:
        if self.chromium_install_process is None:
            return
        self.chromium_install_status_timer.stop()
        self.resume_scan_after_chromium_install = False
        self.chromium_install_canceled = True
        self.chromium_install_process.kill()
        self.chromium_install_process.waitForFinished(1000)

    def _read_chromium_install_output(self) -> None:
        if self.chromium_install_process is None:
            return

        chunk = bytes(self.chromium_install_process.readAll()).decode("utf-8", errors="replace")
        if not chunk:
            return

        self.chromium_install_output += chunk
        self.chromium_install_progress = parse_playwright_install_progress(self.chromium_install_output)
        latest_line = self._latest_install_output_line(chunk)
        self.set_chromium_install_status("running", latest_line)

    def _handle_chromium_install_error(self, _error) -> None:
        if self.chromium_install_process is None:
            return
        self._read_chromium_install_output()
        self.chromium_install_error = self.chromium_install_process.errorString().strip()
        if _error == QProcess.ProcessError.FailedToStart:
            self._fail_chromium_installation()

    def _finish_chromium_installation(self, exit_code: int, exit_status) -> None:
        if self.chromium_install_process is None:
            return

        process, resume_scan, canceled, error_text, output_text = self._take_chromium_install_state()

        if process is not None:
            process.deleteLater()

        if canceled:
            self.add_log_event("log_browser_install_canceled", "info")
            self.set_chromium_install_status("canceled", auto_hide_ms=5000)
            return

        if (
            exit_status == QProcess.ExitStatus.NormalExit
            and exit_code == 0
            and is_chromium_ready(
                self.runtime_settings.provider,
                self.runtime_settings.browser_headless,
                self.runtime_settings.browser_channel,
            )
        ):
            self.add_log_event("log_browser_install_finished", "info")
            self.set_chromium_install_status("finished", auto_hide_ms=5000)
            if resume_scan:
                self.start()
            return

        detail = error_text or self._latest_install_output_line(output_text) or f"exit code {exit_code}"
        self._fail_chromium_installation(detail, process=process)

    def _take_chromium_install_state(self):
        process = self.chromium_install_process
        resume_scan = self.resume_scan_after_chromium_install
        canceled = self.chromium_install_canceled
        error_text = self.chromium_install_error
        output_text = self.chromium_install_output

        self.chromium_install_process = None
        self.resume_scan_after_chromium_install = False
        self.chromium_install_canceled = False
        self.chromium_install_output = ""
        self.chromium_install_error = ""
        self.chromium_install_progress = None
        return process, resume_scan, canceled, error_text, output_text

    def _fail_chromium_installation(self, detail: str = "", process=None) -> None:
        if process is None:
            process, _resume_scan, _canceled, error_text, output_text = self._take_chromium_install_state()
            detail = detail or error_text or self._latest_install_output_line(output_text)

        detail = detail.strip() or "Failed to start Chromium installer."
        if process is not None:
            process.deleteLater()

        self.add_log_event("log_browser_install_failed", "error", {"error": detail})
        self.set_chromium_install_status("failed", detail, auto_hide_ms=8000)
        QMessageBox.warning(
            self,
            self.text("browser_install_title"),
            self.text("browser_install_failed_message", error=detail),
        )

    @staticmethod
    def _latest_install_output_line(output: str) -> str:
        for line in reversed((output or "").replace("\r", "\n").split("\n")):
            cleaned = line.strip()
            if cleaned:
                return cleaned[:180]
        return ""

    def flush_log_entries(self) -> None:
        self.log_buffer.flush_pending()

    def render_log_entries(self) -> None:
        self.log_buffer.render_all()

    def add_name(self) -> None:
        self.actions_presenter.add_name()

    def remove_selected_name(self) -> None:
        self.actions_presenter.remove_selected_name()

    def generate_name_pool(self) -> None:
        self.actions_presenter.generate_name_pool()

    def refresh_seed_summary(self) -> None:
        count = len(self.runtime_settings.seeds)
        seed_count_key = "seed_count" if count == 1 else "seed_count_plural"
        self.seed_count.setText(self.text(seed_count_key, count=count))
        self.seed_badge.setText(self.text("seed_badge", count=count))

    def refresh_provider_options(self) -> None:
        self.translation_presenter.refresh_provider_options()

    def refresh_custom_method_options(self) -> None:
        self.translation_presenter.refresh_custom_method_options()

    def refresh_custom_provider_panel(self) -> None:
        self.state_presenter.refresh_custom_provider_panel()

    def refresh_browser_provider_panel(self) -> None:
        self.state_presenter.refresh_browser_provider_panel()

    def refresh_auto_review_options(self) -> None:
        self.translation_presenter.refresh_auto_review_options()

    def refresh_metric_labels(self) -> None:
        self.state_presenter.refresh_metric_labels()

    def refresh_review_panel(self) -> None:
        self.state_presenter.refresh_review_panel()

    def sync_provider_settings(self, *_) -> None:
        self.settings_presenter.sync_provider_settings()

    def sync_custom_provider_settings(self, *_) -> None:
        self.settings_presenter.sync_custom_provider_settings()

    def sync_browser_provider_settings(self, *_) -> None:
        self.settings_presenter.sync_browser_provider_settings()

    def sync_auto_review_settings(self, *_) -> None:
        self.settings_presenter.sync_auto_review_settings()

    def sync_proxy_settings(self, *_) -> None:
        self.settings_presenter.sync_proxy_settings()

    def change_language(self, *_) -> None:
        self.runtime_presenter.change_language()

    def change_provider(self, *_) -> None:
        self.actions_presenter.change_provider()

    def submit_manual_decision(self, decision: str, bypass_focus_guard: bool = False) -> None:
        self.actions_presenter.submit_manual_decision(decision, bypass_focus_guard)

    def skip_manual_candidate(self, bypass_focus_guard: bool = False) -> None:
        self.actions_presenter.skip_manual_candidate(bypass_focus_guard)

    def copy_current_candidate(self) -> None:
        self.actions_presenter.copy_current_candidate()

    def open_manual_review_page(self) -> None:
        self.actions_presenter.open_manual_review_page()

    def export_review_records(self) -> None:
        self.actions_presenter.export_review_records()

    def _manual_actions_enabled(self, ignore_focus: bool = False) -> bool:
        return self.runtime_presenter.manual_actions_enabled(ignore_focus)

    def update_auto_review_timer(self) -> None:
        self.runtime_presenter.update_auto_review_timer()

    def run_auto_review_action(self) -> None:
        self.runtime_presenter.run_auto_review_action()

    def update_request_status(self, state: str, params=None) -> None:
        self.runtime_presenter.update_request_status(state, params)

    def refresh_request_status(self) -> None:
        self.state_presenter.refresh_request_status()

    def refresh_chromium_install_banner(self) -> None:
        self.state_presenter.refresh_chromium_install_banner()

    def refresh_runtime_panel(self, note_key: str | None = None) -> None:
        self.state_presenter.refresh_runtime_panel(note_key)

    def start(self) -> None:
        self.runtime_presenter.start()

    def pause(self) -> None:
        self.runtime_presenter.pause()

    def stop(self) -> None:
        self.runtime_presenter.stop()

    def closeEvent(self, event) -> None:
        self.runtime_presenter.close_event(event)

    def eventFilter(self, obj, event) -> bool:
        from PySide6.QtCore import QEvent, Qt
        if obj is self.name_list and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Delete, Qt.Key_Backspace):
                self.remove_selected_name()
                return True
        return super().eventFilter(obj, event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
