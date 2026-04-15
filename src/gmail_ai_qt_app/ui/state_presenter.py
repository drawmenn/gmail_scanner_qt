from __future__ import annotations

from ..services.playwright_installer import (
    browser_channel_metadata,
    normalize_browser_channel,
    playwright_browser_install_state,
    playwright_browser_metadata,
    provider_requires_chromium,
    required_browser_names,
)


class MainWindowStatePresenter:
    def __init__(self, window):
        self.window = window

    def refresh_custom_provider_panel(self) -> None:
        is_custom = self.window.runtime_settings.provider == "custom"
        is_post = self.window.runtime_settings.custom_method == "POST"
        for widget in (
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
        provider = self.window.runtime_settings.provider
        is_browser = provider == "playwright"
        supports_browser_runtime = provider_requires_chromium(provider)
        for widget in (
            self.window.browser_runtime_label,
            self.window.browser_runtime_combo,
        ):
            widget.setEnabled(supports_browser_runtime)
        for widget in (
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

    def refresh_chromium_install_banner(self) -> None:
        state = getattr(self.window, "chromium_install_status_state", "hidden")
        detail = getattr(self.window, "chromium_install_status_detail", "").strip()
        progress = getattr(self.window, "chromium_install_progress", None)
        provider = self.window.runtime_settings.provider
        browser_headless = self.window.runtime_settings.browser_headless
        browser_channel = normalize_browser_channel(self.window.runtime_settings.browser_channel)
        uses_system_browser = bool(browser_channel)
        runtime_requires_chromium = provider_requires_chromium(provider)
        runtime_browser_names = required_browser_names(provider, browser_headless, browser_channel)
        runtime_update_states = []
        stale_revision_text = ""

        if uses_system_browser:
            display_metadata = browser_channel_metadata(browser_channel)
            runtime_title_text = (
                display_metadata.title
                if display_metadata is not None
                else self.window.text("browser_runtime_option_chrome")
            )
            runtime_ready = bool(display_metadata is not None and display_metadata.installed)
            runtime_installed_count = 1 if runtime_ready else 0
            runtime_needs_update = False
        else:
            runtime_metadata = [playwright_browser_metadata(name) for name in runtime_browser_names]
            runtime_install_states = [playwright_browser_install_state(name) for name in runtime_browser_names]
            chromium_metadata = playwright_browser_metadata("chromium")
            fallback_metadata = next((item for item in runtime_metadata if item is not None), None)
            display_metadata = chromium_metadata or fallback_metadata
            runtime_titles = [item.title if item is not None else name for name, item in zip(runtime_browser_names, runtime_metadata)]
            runtime_title_text = ", ".join(runtime_titles)
            runtime_ready = bool(runtime_browser_names) and all(item is not None and item.installed for item in runtime_metadata)
            runtime_installed_count = sum(1 for item in runtime_metadata if item is not None and item.installed)
            runtime_update_states = [item for item in runtime_install_states if item.needs_reinstall]
            runtime_needs_update = bool(runtime_update_states)
            stale_revisions = tuple(
                revision
                for install_state in runtime_update_states
                for revision in install_state.installed_revisions[:1]
            )
            stale_revision_text = ", ".join(f"r{revision}" for revision in stale_revisions)

        badge_key_map = {
            "running": "browser_install_badge_running",
            "finished": "browser_install_badge_finished",
            "failed": "browser_install_badge_failed",
            "canceled": "browser_install_badge_canceled",
            "update": "browser_runtime_badge_update",
            "missing": "browser_runtime_badge_missing",
            "partial": "browser_runtime_badge_partial",
            "neutral": "browser_runtime_badge_optional",
        }
        view_state = state

        if view_state == "hidden":
            if display_metadata is None:
                view_state = "neutral"
            elif runtime_requires_chromium:
                if runtime_ready:
                    view_state = "finished"
                elif runtime_needs_update:
                    view_state = "update"
                elif runtime_installed_count > 0:
                    view_state = "partial"
                else:
                    view_state = "missing"
            else:
                view_state = "finished" if display_metadata.installed else "neutral"

        if state == "running" and detail:
            status_text = self.window.text("browser_install_status_running_detail", detail=detail)
        elif state == "running":
            status_text = self.window.text("browser_install_status_running")
        elif state == "failed" and detail:
            status_text = self.window.text("browser_install_status_failed_detail", error=detail)
        elif state == "failed":
            status_text = self.window.text("browser_install_status_failed")
        elif state == "canceled":
            status_text = self.window.text("browser_install_status_canceled")
        elif state == "finished":
            status_text = self.window.text("browser_install_status_finished")
        elif display_metadata is None:
            status_text = self.window.text("browser_runtime_dependency_missing")
        elif runtime_requires_chromium:
            if runtime_ready:
                status_text = self.window.text("browser_runtime_ready", runtime=runtime_title_text)
            elif runtime_needs_update:
                status_text = self.window.text(
                    "browser_runtime_update",
                    runtime=runtime_title_text,
                    revisions=stale_revision_text or "?",
                )
            elif runtime_installed_count > 0:
                status_text = self.window.text("browser_runtime_partial", runtime=runtime_title_text)
            else:
                status_text = self.window.text("browser_runtime_missing", runtime=runtime_title_text)
        elif display_metadata.installed:
            status_text = self.window.text("browser_runtime_optional_installed")
        else:
            status_text = self.window.text("browser_runtime_optional")

        if state == "running":
            compact_status_text = self.window.text("browser_runtime_strip_installing")
        elif state == "failed":
            compact_status_text = self.window.text("browser_runtime_strip_failed")
        elif state == "canceled":
            compact_status_text = self.window.text("browser_runtime_strip_canceled")
        elif display_metadata is None:
            compact_status_text = self.window.text("browser_runtime_strip_dependency_missing")
        elif runtime_requires_chromium:
            if runtime_ready:
                compact_status_text = self.window.text("browser_runtime_strip_ready")
            elif runtime_needs_update:
                compact_status_text = self.window.text("browser_runtime_strip_update")
            elif runtime_installed_count > 0:
                compact_status_text = self.window.text("browser_runtime_strip_partial")
            else:
                compact_status_text = self.window.text("browser_runtime_strip_missing")
        elif display_metadata.installed:
            compact_status_text = self.window.text("browser_runtime_strip_ready")
        else:
            compact_status_text = self.window.text("browser_runtime_strip_optional")

        show_progress = state == "running"
        meta_parts = []
        if display_metadata is not None and display_metadata.browser_version:
            meta_parts.append(
                self.window.text("browser_runtime_version_meta", version=display_metadata.browser_version)
            )
        if display_metadata is not None and display_metadata.revision:
            meta_parts.append(
                self.window.text("browser_runtime_revision_meta", revision=display_metadata.revision)
            )
        if not show_progress and runtime_needs_update and stale_revision_text:
            meta_parts.append(self.window.text("browser_runtime_stale_meta", revisions=stale_revision_text))
        if not show_progress and runtime_requires_chromium and runtime_title_text:
            meta_parts.append(self.window.text("browser_runtime_required_meta", runtime=runtime_title_text))
        elif not show_progress:
            meta_parts.append(self.window.text("browser_runtime_not_required_meta"))
        if display_metadata is not None and not show_progress:
            policy_key = "browser_runtime_policy_system" if uses_system_browser else "browser_runtime_policy_locked"
            meta_parts.append(self.window.text(policy_key))
        meta_text = " | ".join(part for part in meta_parts if part)

        self.window.install_banner.setVisible(True)
        self.window.install_banner.setProperty("state", view_state)
        self.window.install_status_badge.setText(self.window.text(badge_key_map.get(view_state, "browser_runtime_badge_optional")))
        self.window.install_status_label.setText(compact_status_text)
        self.window.install_status_label.setToolTip(status_text)
        self.window.chromium_status_meta_label.setText(meta_text)
        self.window.chromium_status_meta_label.setToolTip(meta_text)
        self.window.install_cancel_btn.setVisible(show_progress)
        self.window.install_cancel_btn.setEnabled(show_progress)
        self.window.chromium_status_progress.setVisible(show_progress)
        self.window.chromium_status_progress_label.setVisible(show_progress)

        if show_progress and progress is None:
            self.window.chromium_status_progress.setRange(0, 0)
            self.window.chromium_status_progress_label.setText(self.window.text("browser_runtime_progress_pending"))
        elif show_progress:
            self.window.chromium_status_progress.setRange(0, 100)
            self.window.chromium_status_progress.setValue(progress)
            self.window.chromium_status_progress_label.setText(
                self.window.text("browser_runtime_progress_percent", percent=progress)
            )
        else:
            self.window.chromium_status_progress.setRange(0, 100)
            self.window.chromium_status_progress.setValue(0)
            self.window.chromium_status_progress_label.setText("")

        self.window.install_banner.style().unpolish(self.window.install_banner)
        self.window.install_banner.style().polish(self.window.install_banner)
        self.window.install_status_badge.style().unpolish(self.window.install_status_badge)
        self.window.install_status_badge.style().polish(self.window.install_status_badge)

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
