from __future__ import annotations


class MainWindowStatePresenter:
    def __init__(self, window):
        self.window = window

    def refresh_custom_provider_panel(self) -> None:
        is_custom = self.window.runtime_settings.provider == "custom"
        is_post = self.window.runtime_settings.custom_method == "POST"
        self.window.custom_panel.setEnabled(is_custom)
        for widget in (
            self.window.custom_title_label,
            self.window.custom_subtitle_label,
            self.window.custom_url_label,
            self.window.custom_url_input,
            self.window.custom_method_label,
            self.window.custom_method_combo,
            self.window.custom_param_label,
            self.window.custom_param_input,
            self.window.custom_status_label,
            self.window.custom_status_input,
            self.window.custom_available_label,
            self.window.custom_available_input,
            self.window.custom_taken_label,
            self.window.custom_taken_input,
            self.window.custom_available_regex_label,
            self.window.custom_available_regex_input,
            self.window.custom_taken_regex_label,
            self.window.custom_taken_regex_input,
            self.window.custom_headers_label,
            self.window.custom_headers_input,
            self.window.custom_body_label,
            self.window.custom_body_input,
        ):
            widget.setEnabled(is_custom)

        self.window.custom_param_label.setEnabled(is_custom and not is_post)
        self.window.custom_param_input.setEnabled(is_custom and not is_post)
        self.window.custom_body_label.setEnabled(is_custom and is_post)
        self.window.custom_body_input.setEnabled(is_custom and is_post)

    def refresh_browser_provider_panel(self) -> None:
        is_browser = self.window.runtime_settings.provider == "playwright"
        self.window.browser_panel.setEnabled(is_browser)
        for widget in (
            self.window.browser_title_label,
            self.window.browser_subtitle_label,
            self.window.browser_url_label,
            self.window.browser_url_input,
            self.window.browser_input_label,
            self.window.browser_input_input,
            self.window.browser_value_label,
            self.window.browser_value_input,
            self.window.browser_submit_label,
            self.window.browser_submit_input,
            self.window.browser_timeout_label,
            self.window.browser_timeout_spin,
            self.window.browser_delay_label,
            self.window.browser_delay_spin,
            self.window.browser_headless_check,
            self.window.browser_available_selector_label,
            self.window.browser_available_selector_input,
            self.window.browser_available_text_label,
            self.window.browser_available_text_input,
            self.window.browser_available_regex_label,
            self.window.browser_available_regex_input,
            self.window.browser_taken_selector_label,
            self.window.browser_taken_selector_input,
            self.window.browser_taken_text_label,
            self.window.browser_taken_text_input,
            self.window.browser_taken_regex_label,
            self.window.browser_taken_regex_input,
            self.window.browser_headers_label,
            self.window.browser_headers_input,
        ):
            widget.setEnabled(is_browser)

    def refresh_metric_labels(self) -> None:
        if self.window.runtime_settings.provider == "manual":
            self.window.checked_card.title_label.setText(self.window.text("metric_reviewed_title"))
            self.window.checked_card.subtitle_label.setText(self.window.text("metric_reviewed_subtitle"))
            self.window.hit_card.title_label.setText(self.window.text("metric_available_title"))
            self.window.hit_card.subtitle_label.setText(self.window.text("metric_available_subtitle"))
            self.window.error_card.title_label.setText(self.window.text("metric_taken_title"))
            self.window.error_card.subtitle_label.setText(self.window.text("metric_taken_subtitle"))
            self.window.rate_card.title_label.setText(self.window.text("metric_hold_title"))
            self.window.rate_card.subtitle_label.setText(self.window.text("metric_hold_subtitle"))
            return

        self.window.checked_card.title_label.setText(self.window.text("metric_checked_title"))
        self.window.checked_card.subtitle_label.setText(self.window.text("metric_checked_subtitle"))
        self.window.hit_card.title_label.setText(self.window.text("metric_hit_title"))
        self.window.hit_card.subtitle_label.setText(self.window.text("metric_hit_subtitle"))
        self.window.error_card.title_label.setText(self.window.text("metric_taken_title"))
        self.window.error_card.subtitle_label.setText(self.window.text("metric_taken_subtitle"))
        self.window.rate_card.title_label.setText(self.window.text("metric_error_title"))
        self.window.rate_card.subtitle_label.setText(self.window.text("metric_error_subtitle"))

    def refresh_review_panel(self) -> None:
        is_manual = self.window.runtime_settings.provider == "manual"
        is_reviewing = (
            self.window.current_request_state == "reviewing"
            and bool(self.window.current_review_candidate)
        )

        if is_reviewing:
            self.window.review_candidate_label.setText(self.window.current_review_candidate)
        elif is_manual and self.window.runtime_settings.manual_auto_enabled:
            self.window.review_candidate_label.setText(self.window.text("review_waiting_auto"))
        elif is_manual:
            self.window.review_candidate_label.setText(self.window.text("review_waiting"))
        else:
            self.window.review_candidate_label.setText(self.window.text("review_disabled"))

        buttons_enabled = is_manual and is_reviewing and self.window.runtime_state == "running"
        self.window.mark_available_btn.setEnabled(buttons_enabled)
        self.window.mark_taken_btn.setEnabled(buttons_enabled)
        self.window.mark_hold_btn.setEnabled(buttons_enabled)
        self.window.skip_candidate_btn.setEnabled(buttons_enabled)
        self.window.copy_candidate_btn.setEnabled(is_manual and bool(self.window.current_review_candidate))
        self.window.open_review_page_btn.setEnabled(is_manual)
        self.window.export_csv_btn.setEnabled(bool(self.window.review_records))
        self.window.auto_review_check.setEnabled(is_manual)
        auto_enabled = is_manual and self.window.runtime_settings.manual_auto_enabled
        self.window.auto_review_action_label.setEnabled(auto_enabled)
        self.window.auto_review_action_combo.setEnabled(auto_enabled)

    def refresh_request_status(self) -> None:
        key_map = {
            "idle": "request_status_idle",
            "requesting": "request_status_requesting",
            "reviewing": "request_status_reviewing",
            "canceled": "request_status_canceled",
            "error": "request_status_error",
        }
        translation_key = key_map.get(self.window.current_request_state, "request_status_idle")
        self.window.request_badge.setText(
            self.window.text(translation_key, **self.window.current_request_params)
        )
        self.window.request_badge.setProperty("status", self.window.current_request_state)
        self.window.request_badge.style().unpolish(self.window.request_badge)
        self.window.request_badge.style().polish(self.window.request_badge)

    def refresh_runtime_panel(self, note_key: str | None = None) -> None:
        state_key_map = {
            "running": "state_running",
            "paused": "state_paused",
            "stopped": "state_stopped",
        }
        default_note_key_map = {
            "running": "runtime_note_running",
            "paused": "runtime_note_paused",
            "stopped": "runtime_note_stopped",
        }

        self.window.current_note_key = note_key or default_note_key_map[self.window.runtime_state]

        self.window.state_badge.setText(self.window.text(state_key_map[self.window.runtime_state]))
        self.window.state_badge.setProperty("state", self.window.runtime_state)
        self.window.state_badge.style().unpolish(self.window.state_badge)
        self.window.state_badge.style().polish(self.window.state_badge)

        proxy_enabled = (
            self.window.runtime_settings.proxy_enabled
            and bool(self.window.runtime_settings.proxy_url)
        )
        proxy_badge_key = "proxy_badge_on" if proxy_enabled else "proxy_badge_off"
        self.window.proxy_badge.setText(self.window.text(proxy_badge_key))
        self.window.page_note.setText(self.window.text(self.window.current_note_key))

        self.window.start_btn.setEnabled(self.window.runtime_state != "running")
        self.window.pause_btn.setEnabled(self.window.runtime_state == "running")
        self.window.stop_btn.setEnabled(self.window.runtime_state in {"running", "paused"})
        self.refresh_review_panel()
