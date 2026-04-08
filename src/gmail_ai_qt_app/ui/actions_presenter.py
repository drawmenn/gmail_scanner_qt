from __future__ import annotations

import csv

from PySide6.QtCore import QDateTime, Qt, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QApplication, QFileDialog

from ..services.name_generator import GeneratorOptions, generate_candidates
from ..services.seed_utils import normalize_seed_value


class MainWindowActionsPresenter:
    def __init__(self, window):
        self.window = window

    def add_name(self) -> None:
        new_name = normalize_seed_value(self.window.name_input.text())
        if not new_name:
            self.window.name_input.clear()
            self.window.add_log_event("log_seed_invalid", "error")
            return

        if new_name in self.window.runtime_settings.seeds:
            self.window.name_input.clear()
            self.window.add_log_event("log_seed_exists", "info", {"name": new_name})
            return

        self.window.runtime_settings.seeds.append(new_name)
        self.window.worker.set_names(self.window.runtime_settings.seeds)
        self.window.name_list.addItem(new_name)
        self.window.name_input.clear()
        self.window.refresh_seed_summary()
        self.window.add_log_event("log_seed_added", "info", {"name": new_name})

    def remove_selected_name(self) -> None:
        selected = self.window.name_list.selectedItems()
        if not selected:
            return
        for item in selected:
            name = item.text()
            row = self.window.name_list.row(item)
            self.window.name_list.takeItem(row)
            if name in self.window.runtime_settings.seeds:
                self.window.runtime_settings.seeds.remove(name)
        self.window.worker.set_names(self.window.runtime_settings.seeds)
        self.window.refresh_seed_summary()

    def generate_name_pool(self) -> None:
        source_text = self.window.generator_source_input.text().strip()
        if not source_text:
            source_text = ", ".join(self.window.runtime_settings.seeds[:8])

        if not source_text.strip():
            self.window.add_log_event("log_generator_source_missing", "info")
            return

        candidates = generate_candidates(
            GeneratorOptions(
                source_text=source_text,
                target_length=self.window.generator_length_spin.value() or 6,
                allow_digits=self.window.generator_digits_check.isChecked(),
                max_results=self.window.generator_count_spin.value(),
            )
        )
        if not candidates:
            self.window.add_log_event("log_generator_source_missing", "info")
            return

        self.window.runtime_settings.seeds = candidates
        self.window.worker.set_names(candidates)
        self.window.name_list.clear()
        self.window.name_list.addItems(candidates)
        self.window.refresh_seed_summary()
        self.window.add_log_event("log_candidates_generated", "info", {"count": len(candidates)})

    def change_provider(self) -> None:
        previous_provider = self.window.runtime_settings.provider
        self.window.sync_provider_settings()
        if previous_provider != self.window.runtime_settings.provider:
            self.window.add_log_event(
                "log_provider_switched",
                "info",
                {"provider": self.window.provider_combo.currentText()},
            )

    def submit_manual_decision(self, decision: str, bypass_focus_guard: bool = False) -> None:
        self.window.auto_review_timer.stop()
        if not self.window._manual_actions_enabled(ignore_focus=bypass_focus_guard):
            return
        candidate = self.window.current_review_candidate
        self.window.review_records.append(
            {
                "timestamp": QDateTime.currentDateTime().toString(Qt.ISODate),
                "candidate": candidate,
                "decision": decision,
                "provider": self.window.runtime_settings.provider,
            }
        )
        self.window.current_request_state = "idle"
        self.window.current_review_candidate = ""
        self.window.refresh_request_status()
        self.window.refresh_review_panel()
        self.window.worker.submit_manual_decision(decision)

    def skip_manual_candidate(self, bypass_focus_guard: bool = False) -> None:
        self.window.auto_review_timer.stop()
        if not self.window._manual_actions_enabled(ignore_focus=bypass_focus_guard):
            return
        self.window.current_request_state = "idle"
        self.window.current_review_candidate = ""
        self.window.refresh_request_status()
        self.window.refresh_review_panel()
        self.window.worker.skip_manual_candidate()

    def copy_current_candidate(self) -> None:
        if not self.window.current_review_candidate:
            return
        QApplication.clipboard().setText(self.window.current_review_candidate)
        self.window.add_log_event(
            "log_candidate_copied",
            "info",
            {"name": self.window.current_review_candidate},
        )

    def open_manual_review_page(self) -> None:
        QDesktopServices.openUrl(QUrl(self.window.MANUAL_REVIEW_URL))
        self.window.add_log_event("log_review_page_opened", "info", {})

    def export_review_records(self) -> None:
        if not self.window.review_records:
            return

        default_name = (
            f"manual_review_{QDateTime.currentDateTime().toString('yyyyMMdd_HHmmss')}.csv"
        )
        path, _ = QFileDialog.getSaveFileName(
            self.window,
            self.window.text("export_dialog_title"),
            default_name,
            self.window.text("export_dialog_filter"),
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=["timestamp", "candidate", "decision", "provider"],
            )
            writer.writeheader()
            writer.writerows(self.window.review_records)

        self.window.add_log_event("log_export_success", "info", {"path": path})
