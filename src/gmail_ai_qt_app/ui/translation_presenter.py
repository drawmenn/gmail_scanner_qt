from __future__ import annotations

from ..services.providers import available_providers


class MainWindowTranslationPresenter:
    def __init__(self, window):
        self.window = window

    def apply_translations(self) -> None:
        w = self.window
        w.setWindowTitle(w.text("window_title"))

        w.eyebrow_label.setText(w.text("brand_eyebrow"))
        w.sidebar_title_label.setText(w.text("brand_title"))
        w.sidebar_subtitle_label.setText(w.text("brand_subtitle"))

        w.display_title_label.setText(w.text("display_title"))
        w.display_subtitle_label.setText(w.text("display_subtitle"))
        w.language_label.setText(w.text("display_label"))
        w.provider_title_label.setText(w.text("provider_title"))
        w.provider_subtitle_label.setText(w.text("provider_subtitle"))
        w.provider_label.setText(w.text("provider_label"))
        w.custom_title_label.setText(w.text("custom_title"))
        w.custom_subtitle_label.setText(w.text("custom_subtitle"))
        w.custom_url_label.setText(w.text("custom_url_label"))
        w.custom_method_label.setText(w.text("custom_method_label"))
        w.custom_param_label.setText(w.text("custom_param_label"))
        w.custom_status_label.setText(w.text("custom_status_label"))
        w.custom_headers_label.setText(w.text("custom_headers_label"))
        w.custom_body_label.setText(w.text("custom_body_label"))
        w.custom_available_label.setText(w.text("custom_available_label"))
        w.custom_taken_label.setText(w.text("custom_taken_label"))
        w.custom_available_regex_label.setText(w.text("custom_available_regex_label"))
        w.custom_taken_regex_label.setText(w.text("custom_taken_regex_label"))
        w.browser_title_label.setText(w.text("browser_title"))
        w.browser_subtitle_label.setText(w.text("browser_subtitle"))
        w.browser_url_label.setText(w.text("browser_url_label"))
        w.browser_input_label.setText(w.text("browser_input_label"))
        w.browser_value_label.setText(w.text("browser_value_label"))
        w.browser_submit_label.setText(w.text("browser_submit_label"))
        w.browser_timeout_label.setText(w.text("browser_timeout_label"))
        w.browser_delay_label.setText(w.text("browser_delay_label"))
        w.browser_available_selector_label.setText(w.text("browser_available_selector_label"))
        w.browser_available_text_label.setText(w.text("browser_available_text_label"))
        w.browser_available_regex_label.setText(w.text("browser_available_regex_label"))
        w.browser_taken_selector_label.setText(w.text("browser_taken_selector_label"))
        w.browser_taken_text_label.setText(w.text("browser_taken_text_label"))
        w.browser_taken_regex_label.setText(w.text("browser_taken_regex_label"))
        w.browser_headers_label.setText(w.text("browser_headers_label"))
        w.proxy_title_label.setText(w.text("connection_title"))
        w.proxy_subtitle_label.setText(w.text("connection_subtitle"))
        w.names_title_label.setText(w.text("name_pool_title"))
        w.names_subtitle_label.setText(w.text("name_pool_subtitle"))
        w.generator_title_label.setText(w.text("generator_title"))
        w.generator_subtitle_label.setText(w.text("generator_subtitle"))
        w.generator_source_label.setText(w.text("generator_source_label"))
        w.generator_length_label.setText(w.text("generator_length_label"))
        w.generator_count_label.setText(w.text("generator_count_label"))
        w.review_title_label.setText(w.text("review_title"))
        w.review_subtitle_label.setText(w.text("review_subtitle"))

        w.start_btn.setText(w.text("start_scan"))
        w.pause_btn.setText(w.text("pause"))
        w.stop_btn.setText(w.text("stop"))
        w.add_btn.setText(w.text("add_seed"))
        w.remove_btn.setText(w.text("remove_seed"))
        w.generator_digits_check.setText(w.text("generator_digits"))
        w.generate_candidates_btn.setText(w.text("generator_generate"))
        w.mark_available_btn.setText(w.text("review_available"))
        w.mark_taken_btn.setText(w.text("review_taken"))
        w.mark_hold_btn.setText(w.text("review_hold"))
        w.skip_candidate_btn.setText(w.text("review_skip"))
        w.auto_review_check.setText(w.text("review_auto_toggle"))
        w.auto_review_action_label.setText(w.text("review_auto_action_label"))
        w.copy_candidate_btn.setText(w.text("review_copy"))
        w.open_review_page_btn.setText(w.text("review_open"))
        w.export_csv_btn.setText(w.text("review_export"))

        w.proxy_check.setText(w.text("proxy_enabled"))
        w.proxy_input.setPlaceholderText(w.text("proxy_placeholder"))
        self.refresh_custom_method_options()
        w.custom_url_input.setPlaceholderText(w.text("custom_url_placeholder"))
        w.custom_param_input.setPlaceholderText(w.text("custom_param_placeholder"))
        w.custom_status_input.setPlaceholderText(w.text("custom_status_placeholder"))
        w.custom_headers_input.setPlaceholderText(w.text("custom_headers_placeholder"))
        w.custom_body_input.setPlaceholderText(w.text("custom_body_placeholder"))
        w.custom_available_input.setPlaceholderText(w.text("custom_available_placeholder"))
        w.custom_taken_input.setPlaceholderText(w.text("custom_taken_placeholder"))
        w.custom_available_regex_input.setPlaceholderText(w.text("custom_available_regex_placeholder"))
        w.custom_taken_regex_input.setPlaceholderText(w.text("custom_taken_regex_placeholder"))
        w.browser_headless_check.setText(w.text("browser_headless"))
        w.browser_url_input.setPlaceholderText(w.text("browser_url_placeholder"))
        w.browser_input_input.setPlaceholderText(w.text("browser_input_placeholder"))
        w.browser_value_input.setPlaceholderText(w.text("browser_value_placeholder"))
        w.browser_submit_input.setPlaceholderText(w.text("browser_submit_placeholder"))
        w.browser_available_selector_input.setPlaceholderText(w.text("browser_available_selector_placeholder"))
        w.browser_available_text_input.setPlaceholderText(w.text("browser_available_text_placeholder"))
        w.browser_available_regex_input.setPlaceholderText(w.text("browser_available_regex_placeholder"))
        w.browser_taken_selector_input.setPlaceholderText(w.text("browser_taken_selector_placeholder"))
        w.browser_taken_text_input.setPlaceholderText(w.text("browser_taken_text_placeholder"))
        w.browser_taken_regex_input.setPlaceholderText(w.text("browser_taken_regex_placeholder"))
        w.browser_headers_input.setPlaceholderText(w.text("browser_headers_placeholder"))
        w.name_input.setPlaceholderText(w.text("name_input_placeholder"))
        w.generator_source_input.setPlaceholderText(w.text("generator_source_placeholder"))
        self.refresh_provider_options()
        self.refresh_auto_review_options()
        w.refresh_custom_provider_panel()
        w.refresh_browser_provider_panel()

        w.page_title.setText(w.text("page_title"))

        w.checked_card.title_label.setText(w.text("metric_checked_title"))
        w.checked_card.subtitle_label.setText(w.text("metric_checked_subtitle"))
        w.hit_card.title_label.setText(w.text("metric_hit_title"))
        w.hit_card.subtitle_label.setText(w.text("metric_hit_subtitle"))
        w.error_card.title_label.setText(w.text("metric_error_title"))
        w.error_card.subtitle_label.setText(w.text("metric_error_subtitle"))
        w.rate_card.title_label.setText(w.text("metric_rate_title"))
        w.rate_card.subtitle_label.setText(w.text("metric_rate_subtitle"))

        w.activity_panel_title_label.setText(w.text("activity_panel_title"))
        w.activity_panel_subtitle_label.setText(w.text("activity_panel_subtitle"))
        w.rate_panel_title_label.setText(w.text("rate_panel_title"))
        w.rate_panel_subtitle_label.setText(w.text("rate_panel_subtitle"))
        w.log_panel_title_label.setText(w.text("log_panel_title"))
        w.log_panel_subtitle_label.setText(w.text("log_panel_subtitle"))
        w.log.setPlaceholderText(w.text("log_placeholder"))
        w.refresh_metric_labels()
        w.refresh_request_status()
        w.refresh_review_panel()

    def refresh_provider_options(self) -> None:
        current_provider = self.window.provider_combo.currentData()
        for index, provider in enumerate(available_providers()):
            self.window.provider_combo.setItemText(index, self.window.text(provider.label_key))

        restored_index = self.window.provider_combo.findData(current_provider)
        if restored_index >= 0:
            self.window.provider_combo.setCurrentIndex(restored_index)

    def refresh_custom_method_options(self) -> None:
        current_method = self.window.custom_method_combo.currentData()
        for index, method in enumerate(("GET", "POST")):
            self.window.custom_method_combo.setItemText(
                index,
                self.window.text(f"custom_method_{method.lower()}"),
            )

        restored_index = self.window.custom_method_combo.findData(current_method)
        if restored_index >= 0:
            self.window.custom_method_combo.setCurrentIndex(restored_index)

    def refresh_auto_review_options(self) -> None:
        current_action = self.window.auto_review_action_combo.currentData()
        for index, action in enumerate(self.window.AUTO_REVIEW_ACTIONS):
            self.window.auto_review_action_combo.setItemText(
                index,
                self.window.text(f"review_auto_action_{action}"),
            )

        restored_index = self.window.auto_review_action_combo.findData(current_action)
        if restored_index >= 0:
            self.window.auto_review_action_combo.setCurrentIndex(restored_index)
