from __future__ import annotations

import sys

from PySide6.QtWidgets import QComboBox, QLineEdit, QListWidget, QTextEdit


class MainWindowRuntimePresenter:
    def __init__(self, window):
        self.window = window

    def change_language(self) -> None:
        language = self.window.language_combo.currentData()
        if not language or language == self.window.runtime_settings.language:
            return

        self.window.runtime_settings.language = language
        self.window.apply_translations()
        self.window.configure_plots()
        self.window.apply_snapshot(self.window.last_snapshot)
        self.window.refresh_seed_summary()
        self.window.refresh_request_status()
        self.window.refresh_runtime_panel(self.window.current_note_key)
        self.window.render_log_entries()

    def update_auto_review_timer(self) -> None:
        should_run = (
            self.window.runtime_settings.provider == "manual"
            and self.window.runtime_settings.manual_auto_enabled
            and self.window.runtime_state == "running"
            and self.window.current_request_state == "reviewing"
            and bool(self.window.current_review_candidate)
        )

        if should_run:
            self.window.auto_review_timer.start(self.window.AUTO_REVIEW_DELAY_MS)
            return

        self.window.auto_review_timer.stop()

    def run_auto_review_action(self) -> None:
        if not self.manual_actions_enabled(ignore_focus=True):
            return

        action = self.window.runtime_settings.manual_auto_action
        if action == "skip":
            self.window.skip_manual_candidate(bypass_focus_guard=True)
            return

        self.window.submit_manual_decision(action, bypass_focus_guard=True)

    def update_request_status(self, state: str, params=None) -> None:
        self.window.current_request_state = state
        self.window.current_request_params = dict(params or {})
        if state == "reviewing":
            self.window.current_review_candidate = self.window.current_request_params.get("name", "")
        else:
            self.window.current_review_candidate = ""
        self.window.refresh_request_status()
        self.window.refresh_review_panel()
        self.window.update_auto_review_timer()

    def start(self) -> None:
        self.window.runtime_state = "running"
        self.window.worker.start_scanning()
        self.window.refresh_runtime_panel("runtime_note_started")
        self.window.update_auto_review_timer()
        self.window.add_log_event("log_scanner_started", "info")

    def pause(self) -> None:
        self.window.runtime_state = "paused"
        self.window.auto_review_timer.stop()
        if self.window.runtime_settings.provider == "manual":
            self.window.current_request_state = "idle"
            self.window.current_review_candidate = ""
            self.window.refresh_request_status()
        self.window.worker.pause_scanning()
        self.window.refresh_runtime_panel("runtime_note_paused_manual")
        self.window.add_log_event("log_scanner_paused", "info")

    def stop(self) -> None:
        self.window.runtime_state = "stopped"
        self.window.auto_review_timer.stop()
        if self.window.runtime_settings.provider == "manual":
            self.window.current_request_state = "idle"
            self.window.current_review_candidate = ""
            self.window.refresh_request_status()
        self.window.worker.stop_scanning()
        self.window.refresh_runtime_panel("runtime_note_stopped_manual")
        self.window.add_log_event("log_scanner_stopped", "info")

    def close_event(self, event) -> None:
        self.window.auto_review_timer.stop()
        self.window._log_flush_timer.stop()
        self.window.flush_log_entries()
        self.window.worker.shutdown()
        self.window.scanner_thread.quit()
        self.window.scanner_thread.wait(1000)
        saved, path, error = self.window.settings_store.save(self.window.runtime_settings)
        if not saved and error:
            print(f"Failed to save settings to {path}: {error}", file=sys.stderr)
        self._auto_save_review_records()
        super(type(self.window), self.window).closeEvent(event)

    def _auto_save_review_records(self) -> None:
        import csv
        from pathlib import Path
        from PySide6.QtCore import QDateTime
        records = self.window.review_records
        if not records:
            return
        settings_path = self.window.settings_store.path
        save_dir = settings_path.parent
        try:
            save_dir.mkdir(parents=True, exist_ok=True)
            filename = f"review_{QDateTime.currentDateTime().toString('yyyyMMdd_HHmmss')}.csv"
            out_path = save_dir / filename
            with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["timestamp", "candidate", "decision", "provider"])
                writer.writeheader()
                writer.writerows(records)
        except Exception as exc:
            print(f"Failed to auto-save review records: {exc}", file=sys.stderr)

    def manual_actions_enabled(self, ignore_focus: bool = False) -> bool:
        focused = self.window.focusWidget()
        if not ignore_focus and isinstance(focused, (QLineEdit, QTextEdit, QComboBox, QListWidget)):
            return False
        return (
            self.window.runtime_settings.provider == "manual"
            and self.window.runtime_state == "running"
            and self.window.current_request_state == "reviewing"
            and bool(self.window.current_review_candidate)
        )
