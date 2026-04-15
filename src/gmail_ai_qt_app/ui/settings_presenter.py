from __future__ import annotations


class MainWindowSettingsPresenter:
    def __init__(self, window):
        self.window = window

    def sync_provider_settings(self) -> None:
        provider = self.window.provider_combo.currentData()
        if not provider:
            return

        self.window.runtime_settings.provider = provider
        self.window.worker.set_provider(provider)
        self.window.refresh_metric_labels()
        self.window.refresh_custom_provider_panel()
        self.window.refresh_browser_provider_panel()
        self.window.refresh_chromium_install_banner()
        self.window.refresh_review_panel()
        self.window.update_auto_review_timer()

    def sync_custom_provider_settings(self) -> None:
        settings = self.window.runtime_settings
        settings.custom_url = self.window.custom_url_input.text().strip()
        settings.custom_method = str(self.window.custom_method_combo.currentData() or "GET")
        settings.custom_param_name = self.window.custom_param_input.text().strip() or "username"
        settings.custom_status_codes = self.window.custom_status_input.text().strip()
        settings.custom_headers = self.window.custom_headers_input.toPlainText()
        settings.custom_body_template = self.window.custom_body_input.toPlainText()
        settings.custom_available_keyword = self.window.custom_available_input.text().strip()
        settings.custom_taken_keyword = self.window.custom_taken_input.text().strip()
        settings.custom_available_regex = self.window.custom_available_regex_input.text().strip()
        settings.custom_taken_regex = self.window.custom_taken_regex_input.text().strip()

        self.window.worker.set_custom_config(
            {
                "url": settings.custom_url,
                "method": settings.custom_method,
                "param_name": settings.custom_param_name,
                "status_codes": settings.custom_status_codes,
                "headers": settings.custom_headers,
                "body_template": settings.custom_body_template,
                "available_keyword": settings.custom_available_keyword,
                "taken_keyword": settings.custom_taken_keyword,
                "available_regex": settings.custom_available_regex,
                "taken_regex": settings.custom_taken_regex,
            }
        )
        self.window.refresh_custom_provider_panel()

    def sync_browser_provider_settings(self) -> None:
        settings = self.window.runtime_settings
        settings.browser_url = self.window.browser_url_input.text().strip()
        settings.browser_input_selector = self.window.browser_input_input.text().strip()
        settings.browser_value_template = self.window.browser_value_input.text() or "{username}"
        settings.browser_submit_selector = self.window.browser_submit_input.text().strip()
        settings.browser_channel = str(self.window.browser_runtime_combo.currentData() or "").strip()
        settings.browser_headers = self.window.browser_headers_input.toPlainText()
        settings.browser_available_selector = self.window.browser_available_selector_input.text().strip()
        settings.browser_available_text = self.window.browser_available_text_input.text().strip()
        settings.browser_available_regex = self.window.browser_available_regex_input.text().strip()
        settings.browser_taken_selector = self.window.browser_taken_selector_input.text().strip()
        settings.browser_taken_text = self.window.browser_taken_text_input.text().strip()
        settings.browser_taken_regex = self.window.browser_taken_regex_input.text().strip()
        settings.browser_timeout_ms = self.window.browser_timeout_spin.value()
        settings.browser_delay_ms = self.window.browser_delay_spin.value()
        settings.browser_headless = self.window.browser_headless_check.isChecked()

        self.window.worker.set_browser_config(
            {
                "url": settings.browser_url,
                "input_selector": settings.browser_input_selector,
                "value_template": settings.browser_value_template,
                "submit_selector": settings.browser_submit_selector,
                "channel": settings.browser_channel,
                "headers": settings.browser_headers,
                "available_selector": settings.browser_available_selector,
                "available_text": settings.browser_available_text,
                "available_regex": settings.browser_available_regex,
                "taken_selector": settings.browser_taken_selector,
                "taken_text": settings.browser_taken_text,
                "taken_regex": settings.browser_taken_regex,
                "timeout_ms": settings.browser_timeout_ms,
                "delay_ms": settings.browser_delay_ms,
                "headless": settings.browser_headless,
            }
        )
        self.window.refresh_browser_provider_panel()
        self.window.refresh_chromium_install_banner()

    def sync_auto_review_settings(self) -> None:
        action = self.window.auto_review_action_combo.currentData()
        if not action:
            action = self.window.runtime_settings.manual_auto_action

        self.window.runtime_settings.manual_auto_enabled = self.window.auto_review_check.isChecked()
        self.window.runtime_settings.manual_auto_action = action
        self.window.refresh_review_panel()
        self.window.update_auto_review_timer()

    def sync_proxy_settings(self) -> None:
        self.window.runtime_settings.proxy_enabled = self.window.proxy_check.isChecked()
        self.window.runtime_settings.proxy_url = self.window.proxy_input.text().strip()
        self.window.worker.set_proxy_config(
            self.window.runtime_settings.proxy_enabled,
            self.window.runtime_settings.proxy_url,
        )
        self.window.refresh_runtime_panel()
