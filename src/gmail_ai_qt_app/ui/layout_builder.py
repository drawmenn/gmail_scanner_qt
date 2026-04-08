from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollBar
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class MainWindowLayoutBuilder:
    def __init__(self, main_window):
        self.main_window = main_window

    def build(self) -> QWidget:
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = _ViewportFillScrollArea()
        scroll_area.setObjectName("PageScrollArea")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        page = QWidget()
        page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(14, 10, 14, 10)
        page_layout.setSpacing(16)

        # 创建标签页控件
        tabs = QTabWidget()
        tabs.setObjectName("MainTabs")
        tabs.setDocumentMode(True)
        tabs.tabBar().setObjectName("MainTabBar")
        tabs.tabBar().setDrawBase(False)
        tabs.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)

        # 第一标签：设置
        settings_tab = QWidget()
        settings_layout = QVBoxLayout(settings_tab)
        settings_layout.setContentsMargins(0, 10, 0, 0)
        settings_layout.setSpacing(12)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)
        top_layout.addWidget(self._build_brand_card(), 1)
        top_layout.addWidget(self._build_names_card(), 1)
        top_layout.addWidget(self._build_generator_card(), 1)
        settings_layout.addLayout(top_layout)

        settings_layout.addWidget(self._build_custom_section())
        settings_layout.addWidget(self._build_browser_section())
        settings_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        tabs.addTab(settings_tab, "设置")

        # 第二标签：监控
        monitor_tab = QWidget()
        monitor_layout = QVBoxLayout(monitor_tab)
        monitor_layout.setContentsMargins(0, 10, 0, 0)
        monitor_layout.setSpacing(12)

        monitor_top_row = QHBoxLayout()
        monitor_top_row.setSpacing(12)
        monitor_top_row.addWidget(self._build_dashboard_panel(), 1)
        monitor_top_row.addWidget(self._build_review_panel(), 1)

        monitor_layout.addLayout(monitor_top_row)
        monitor_layout.addWidget(self._build_insights_panel())
        monitor_layout.addStretch(1)

        tabs.addTab(monitor_tab, "监控")

        page_layout.addWidget(tabs)

        scroll_area.setWidget(page)
        root_layout.addWidget(scroll_area)
        return central_widget

    def _build_brand_card(self) -> QFrame:
        card = self._panel()
        card.setFixedHeight(240)
        layout = self._panel_layout(card)
        layout.setContentsMargins(11, 11, 11, 11)
        layout.setSpacing(8)

        self.main_window.eyebrow_label = QLabel()
        self.main_window.eyebrow_label.setObjectName("HintLabel")
        self.main_window.eyebrow_label.hide()

        self.main_window.sidebar_title_label = QLabel()
        self.main_window.sidebar_title_label.setObjectName("PanelTitle")
        self.main_window.sidebar_title_label.setProperty("compactTopCard", True)

        self.main_window.sidebar_subtitle_label = QLabel()
        self.main_window.sidebar_subtitle_label.setObjectName("PanelSubtitle")
        self.main_window.sidebar_subtitle_label.setProperty("compactTopCard", True)

        header = self._build_top_card_header(
            icon_text="G",
            icon_background="#4f73ff",
            title_label=self.main_window.sidebar_title_label,
            subtitle_label=self.main_window.sidebar_subtitle_label,
        )
        layout.addWidget(header)

        self.main_window.language_label = QLabel()
        self.main_window.language_combo = QComboBox()
        self.main_window.language_combo.setFixedHeight(32)
        self.main_window.provider_label = QLabel()
        self.main_window.provider_combo = QComboBox()
        self.main_window.provider_combo.setFixedHeight(32)
        self.main_window.proxy_check = QCheckBox()
        self.main_window.proxy_input = QLineEdit()
        self.main_window.proxy_input.setFixedHeight(32)

        language_row = QHBoxLayout()
        language_row.setSpacing(8)
        language_row.addWidget(self._field_block(self.main_window.language_label, self.main_window.language_combo))
        language_row.addWidget(self._field_block(self.main_window.provider_label, self.main_window.provider_combo))
        layout.addLayout(language_row)

        self.main_window.proxy_check.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.main_window.proxy_check)
        layout.addWidget(self.main_window.proxy_input)
        return card

    def _build_names_card(self) -> QFrame:
        card = self._panel()
        card.setFixedHeight(240)
        layout = self._panel_layout(card)
        layout.setContentsMargins(11, 11, 11, 11)
        layout.setSpacing(8)

        self.main_window.names_title_label = QLabel()
        self.main_window.names_title_label.setObjectName("PanelTitle")
        self.main_window.names_title_label.setProperty("compactTopCard", True)
        self.main_window.names_subtitle_label = QLabel()
        self.main_window.names_subtitle_label.setObjectName("PanelSubtitle")
        self.main_window.names_subtitle_label.setProperty("compactTopCard", True)
        self.main_window.seed_count = QLabel("0")
        self.main_window.seed_count.setObjectName("HintLabel")
        self.main_window.seed_count.setProperty("compactTopCard", True)

        header = self._build_top_card_header(
            icon_text="@",
            icon_background="#bd4eff",
            title_label=self.main_window.names_title_label,
            subtitle_label=self.main_window.names_subtitle_label,
            trailing_label=self.main_window.seed_count,
        )
        layout.addWidget(header)

        self.main_window.name_input = QLineEdit()
        self.main_window.name_input.setFixedHeight(32)
        self.main_window.add_btn = QPushButton()
        self.main_window.add_btn.setProperty("variant", "success")
        self.main_window.add_btn.setFixedHeight(32)
        self.main_window.remove_btn = QPushButton()
        self.main_window.remove_btn.setProperty("variant", "danger")
        self.main_window.remove_btn.setFixedHeight(32)
        self.main_window.add_btn.setMinimumWidth(76)
        self.main_window.remove_btn.setMinimumWidth(66)

        controls = QHBoxLayout()
        controls.setSpacing(8)
        controls.addWidget(self.main_window.name_input, 1)
        controls.addWidget(self.main_window.add_btn)
        controls.addWidget(self.main_window.remove_btn)
        layout.addLayout(controls)

        self.main_window.name_list = QListWidget()
        self.main_window.name_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.main_window.name_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.main_window.name_list.setFixedHeight(88)
        layout.addWidget(self.main_window.name_list, 1)
        return card

    def _build_generator_card(self) -> QFrame:
        card = self._panel()
        card.setFixedHeight(240)
        layout = self._panel_layout(card)
        layout.setContentsMargins(11, 11, 11, 11)
        layout.setSpacing(8)

        self.main_window.generator_title_label = QLabel()
        self.main_window.generator_title_label.setObjectName("PanelTitle")
        self.main_window.generator_title_label.setProperty("compactTopCard", True)
        self.main_window.generator_subtitle_label = QLabel()
        self.main_window.generator_subtitle_label.setObjectName("PanelSubtitle")
        self.main_window.generator_subtitle_label.setProperty("compactTopCard", True)

        header = self._build_top_card_header(
            icon_text="#",
            icon_background="#13c293",
            title_label=self.main_window.generator_title_label,
            subtitle_label=self.main_window.generator_subtitle_label,
        )
        layout.addWidget(header)

        self.main_window.generator_source_label = QLabel()
        self.main_window.generator_source_input = QLineEdit()
        self.main_window.generator_source_input.setFixedHeight(32)
        layout.addWidget(self._field_block(self.main_window.generator_source_label, self.main_window.generator_source_input))

        self.main_window.generator_length_label = QLabel()
        self.main_window.generator_length_spin = QSpinBox()
        self.main_window.generator_length_spin.setFixedHeight(32)
        self.main_window.generator_length_spin.setRange(6, 30)
        self.main_window.generator_length_spin.setValue(6)

        self.main_window.generator_count_label = QLabel()
        self.main_window.generator_count_spin = QSpinBox()
        self.main_window.generator_count_spin.setFixedHeight(32)
        self.main_window.generator_count_spin.setRange(10, 500)
        self.main_window.generator_count_spin.setValue(80)

        row = QHBoxLayout()
        row.setSpacing(10)
        row.addWidget(self._field_block(self.main_window.generator_length_label, self.main_window.generator_length_spin))
        row.addWidget(self._field_block(self.main_window.generator_count_label, self.main_window.generator_count_spin))
        layout.addLayout(row)

        self.main_window.generator_digits_check = QCheckBox()
        self.main_window.generator_digits_check.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.main_window.generator_digits_check)

        self.main_window.generate_candidates_btn = QPushButton()
        self.main_window.generate_candidates_btn.setProperty("variant", "neutral")
        self.main_window.generate_candidates_btn.setFixedHeight(32)
        layout.addWidget(self.main_window.generate_candidates_btn)
        return card

    def _build_review_panel(self) -> QFrame:
        self.main_window.review_title_label = QLabel()
        self.main_window.review_title_label.setObjectName("PanelTitle")
        self.main_window.review_subtitle_label = QLabel()
        self.main_window.review_subtitle_label.setObjectName("PanelSubtitle")
        self.main_window.review_subtitle_label.setWordWrap(True)
        panel = self._panel()
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = self._panel_layout(panel)
        layout.setSpacing(8)

        header = QVBoxLayout()
        header.setSpacing(4)
        header.addWidget(self.main_window.review_title_label)
        header.addWidget(self.main_window.review_subtitle_label)
        layout.addLayout(header)

        self.main_window.review_candidate_label = QLabel()
        self.main_window.review_candidate_label.setObjectName("ReviewCandidate")
        self.main_window.review_candidate_label.setFixedHeight(46)
        self.main_window.review_candidate_label.setWordWrap(True)
        self.main_window.review_candidate_label.setAlignment(
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        )
        self.main_window.review_candidate_label.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Fixed,
        )
        layout.addWidget(self.main_window.review_candidate_label, 1)

        self.main_window.mark_available_btn = QPushButton()
        self.main_window.mark_available_btn.setStyleSheet(
            "QPushButton { background: #1fb76a; color: white; border-radius: 10px; min-height: 32px; font-weight: 700; }"
            "QPushButton:hover { background: #17a55d; }"
            "QPushButton:disabled { background: #b7e5cb; color: white; }"
        )
        self.main_window.mark_taken_btn = QPushButton()
        self.main_window.mark_taken_btn.setProperty("variant", "danger")
        self.main_window.mark_hold_btn = QPushButton()
        self.main_window.mark_hold_btn.setProperty("variant", "warning")
        self.main_window.skip_candidate_btn = QPushButton()
        self.main_window.skip_candidate_btn.setProperty("variant", "neutral")

        decision_row = QHBoxLayout()
        decision_row.setSpacing(6)
        decision_row.addWidget(self.main_window.mark_available_btn, 1)
        decision_row.addWidget(self.main_window.mark_taken_btn, 1)
        decision_row.addWidget(self.main_window.mark_hold_btn, 1)
        decision_row.addWidget(self.main_window.skip_candidate_btn, 1)
        layout.addLayout(decision_row)

        self.main_window.auto_review_check = QCheckBox()
        self.main_window.auto_review_check.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.main_window.auto_review_check)

        self.main_window.auto_review_action_label = QLabel()
        self.main_window.auto_review_action_combo = QComboBox()

        auto_row = QHBoxLayout()
        auto_row.setSpacing(6)
        auto_row.addWidget(self.main_window.auto_review_action_label)
        auto_row.addWidget(self.main_window.auto_review_action_combo, 1)
        layout.addLayout(auto_row)

        self.main_window.copy_candidate_btn = QPushButton()
        self.main_window.copy_candidate_btn.setProperty("variant", "neutral")
        self.main_window.open_review_page_btn = QPushButton()
        self.main_window.open_review_page_btn.setProperty("variant", "neutral")
        self.main_window.export_csv_btn = QPushButton()
        self.main_window.export_csv_btn.setProperty("variant", "neutral")

        utility_row = QHBoxLayout()
        utility_row.setSpacing(6)
        utility_row.addWidget(self.main_window.copy_candidate_btn, 1)
        utility_row.addWidget(self.main_window.open_review_page_btn, 1)
        utility_row.addWidget(self.main_window.export_csv_btn, 1)
        layout.addLayout(utility_row)
        return panel

    def _build_custom_section(self) -> QFrame:
        self.main_window.custom_title_label = QLabel()
        self.main_window.custom_subtitle_label = QLabel()
        self.main_window.custom_subtitle_label.setWordWrap(True)
        self.main_window.custom_url_label = QLabel()
        self.main_window.custom_method_label = QLabel()
        self.main_window.custom_param_label = QLabel()
        self.main_window.custom_status_label = QLabel()
        self.main_window.custom_headers_label = QLabel()
        self.main_window.custom_body_label = QLabel()
        self.main_window.custom_available_label = QLabel()
        self.main_window.custom_taken_label = QLabel()
        self.main_window.custom_available_regex_label = QLabel()
        self.main_window.custom_taken_regex_label = QLabel()

        self.main_window.custom_method_combo = QComboBox()
        self.main_window.custom_url_input = QLineEdit()
        self.main_window.custom_param_input = QLineEdit()
        self.main_window.custom_status_input = QLineEdit()
        self.main_window.custom_headers_input = QTextEdit()
        self.main_window.custom_headers_input.setFixedHeight(78)
        self.main_window.custom_body_input = QTextEdit()
        self.main_window.custom_body_input.setFixedHeight(78)
        self.main_window.custom_available_input = QLineEdit()
        self.main_window.custom_taken_input = QLineEdit()
        self.main_window.custom_available_regex_input = QLineEdit()
        self.main_window.custom_taken_regex_input = QLineEdit()

        def populate(content_layout: QVBoxLayout) -> None:
            content_layout.addWidget(self.main_window.custom_subtitle_label)
            content_layout.addWidget(self._field_block(self.main_window.custom_url_label, self.main_window.custom_url_input))

            row = QHBoxLayout()
            row.setSpacing(10)
            row.addWidget(self._field_block(self.main_window.custom_method_label, self.main_window.custom_method_combo))
            row.addWidget(self._field_block(self.main_window.custom_param_label, self.main_window.custom_param_input))
            row.addWidget(self._field_block(self.main_window.custom_status_label, self.main_window.custom_status_input))
            content_layout.addLayout(row)

            text_row = QHBoxLayout()
            text_row.setSpacing(10)
            text_row.addWidget(self._field_block(self.main_window.custom_headers_label, self.main_window.custom_headers_input))
            text_row.addWidget(self._field_block(self.main_window.custom_body_label, self.main_window.custom_body_input))
            content_layout.addLayout(text_row)

            match_row = QHBoxLayout()
            match_row.setSpacing(10)
            match_row.addWidget(self._field_block(self.main_window.custom_available_label, self.main_window.custom_available_input))
            match_row.addWidget(self._field_block(self.main_window.custom_taken_label, self.main_window.custom_taken_input))
            content_layout.addLayout(match_row)

            regex_row = QHBoxLayout()
            regex_row.setSpacing(10)
            regex_row.addWidget(self._field_block(self.main_window.custom_available_regex_label, self.main_window.custom_available_regex_input))
            regex_row.addWidget(self._field_block(self.main_window.custom_taken_regex_label, self.main_window.custom_taken_regex_input))
            content_layout.addLayout(regex_row)

        return self._collapsible_section(self.main_window.custom_title_label, populate, expanded=False)

    def _build_browser_section(self) -> QFrame:
        self.main_window.browser_title_label = QLabel()
        self.main_window.browser_subtitle_label = QLabel()
        self.main_window.browser_subtitle_label.setWordWrap(True)
        self.main_window.browser_url_label = QLabel()
        self.main_window.browser_input_label = QLabel()
        self.main_window.browser_value_label = QLabel()
        self.main_window.browser_submit_label = QLabel()
        self.main_window.browser_timeout_label = QLabel()
        self.main_window.browser_delay_label = QLabel()
        self.main_window.browser_available_selector_label = QLabel()
        self.main_window.browser_available_text_label = QLabel()
        self.main_window.browser_available_regex_label = QLabel()
        self.main_window.browser_taken_selector_label = QLabel()
        self.main_window.browser_taken_text_label = QLabel()
        self.main_window.browser_taken_regex_label = QLabel()
        self.main_window.browser_headers_label = QLabel()

        self.main_window.browser_headless_check = QCheckBox()
        self.main_window.browser_headless_check.setCursor(Qt.CursorShape.PointingHandCursor)
        self.main_window.browser_url_input = QLineEdit()
        self.main_window.browser_input_input = QLineEdit()
        self.main_window.browser_value_input = QLineEdit()
        self.main_window.browser_submit_input = QLineEdit()
        self.main_window.browser_timeout_spin = QSpinBox()
        self.main_window.browser_timeout_spin.setRange(1000, 120000)
        self.main_window.browser_timeout_spin.setSingleStep(500)
        self.main_window.browser_delay_spin = QSpinBox()
        self.main_window.browser_delay_spin.setRange(0, 60000)
        self.main_window.browser_delay_spin.setSingleStep(100)
        self.main_window.browser_available_selector_input = QLineEdit()
        self.main_window.browser_available_text_input = QLineEdit()
        self.main_window.browser_available_regex_input = QLineEdit()
        self.main_window.browser_taken_selector_input = QLineEdit()
        self.main_window.browser_taken_text_input = QLineEdit()
        self.main_window.browser_taken_regex_input = QLineEdit()
        self.main_window.browser_headers_input = QTextEdit()
        self.main_window.browser_headers_input.setFixedHeight(64)

        def populate(content_layout: QVBoxLayout) -> None:
            content_layout.addWidget(self.main_window.browser_subtitle_label)
            content_layout.addWidget(self._field_block(self.main_window.browser_url_label, self.main_window.browser_url_input))

            row = QHBoxLayout()
            row.setSpacing(10)
            row.addWidget(self._field_block(self.main_window.browser_input_label, self.main_window.browser_input_input))
            row.addWidget(self._field_block(self.main_window.browser_value_label, self.main_window.browser_value_input))
            row.addWidget(self._field_block(self.main_window.browser_submit_label, self.main_window.browser_submit_input))
            content_layout.addLayout(row)

            timing_row = QHBoxLayout()
            timing_row.setSpacing(10)
            timing_row.addWidget(self._field_block(self.main_window.browser_timeout_label, self.main_window.browser_timeout_spin))
            timing_row.addWidget(self._field_block(self.main_window.browser_delay_label, self.main_window.browser_delay_spin))
            timing_row.addWidget(self._checkbox_block(self.main_window.browser_headless_check))
            content_layout.addLayout(timing_row)

            available_row = QHBoxLayout()
            available_row.setSpacing(10)
            available_row.addWidget(self._field_block(self.main_window.browser_available_selector_label, self.main_window.browser_available_selector_input))
            available_row.addWidget(self._field_block(self.main_window.browser_available_text_label, self.main_window.browser_available_text_input))
            available_row.addWidget(self._field_block(self.main_window.browser_available_regex_label, self.main_window.browser_available_regex_input))
            content_layout.addLayout(available_row)

            taken_row = QHBoxLayout()
            taken_row.setSpacing(10)
            taken_row.addWidget(self._field_block(self.main_window.browser_taken_selector_label, self.main_window.browser_taken_selector_input))
            taken_row.addWidget(self._field_block(self.main_window.browser_taken_text_label, self.main_window.browser_taken_text_input))
            taken_row.addWidget(self._field_block(self.main_window.browser_taken_regex_label, self.main_window.browser_taken_regex_input))
            content_layout.addLayout(taken_row)

            content_layout.addWidget(self._field_block(self.main_window.browser_headers_label, self.main_window.browser_headers_input))

        return self._collapsible_section(self.main_window.browser_title_label, populate, expanded=False)

    def _build_dashboard_panel(self) -> QFrame:
        panel = self._panel()
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout = self._panel_layout(panel)
        layout.setSpacing(10)

        self.main_window.page_title = QLabel()
        self.main_window.page_title.setObjectName("PageTitle")
        self.main_window.page_note = QLabel()
        self.main_window.page_note.setObjectName("PageSubtitle")
        self.main_window.page_note.setWordWrap(True)

        title_column = QVBoxLayout()
        title_column.setSpacing(4)
        title_column.addWidget(self.main_window.page_title)
        title_column.addWidget(self.main_window.page_note)

        self.main_window.state_badge = QLabel()
        self.main_window.state_badge.setObjectName("StateBadge")
        self.main_window.request_badge = QLabel()
        self.main_window.request_badge.setObjectName("RequestBadge")
        self.main_window.proxy_badge = QLabel()
        self.main_window.proxy_badge.setObjectName("InfoBadge")
        self.main_window.seed_badge = QLabel()
        self.main_window.seed_badge.setObjectName("InfoBadge")
        self.main_window.rate_badge = QLabel()
        self.main_window.rate_badge.setObjectName("InfoBadge")

        badge_row = QHBoxLayout()
        badge_row.setSpacing(4)
        badge_row.addWidget(self.main_window.state_badge)
        badge_row.addWidget(self.main_window.proxy_badge)
        badge_row.addWidget(self.main_window.request_badge)
        badge_row.addWidget(self.main_window.seed_badge)
        badge_row.addWidget(self.main_window.rate_badge)

        header = QHBoxLayout()
        header.setSpacing(10)
        header.addLayout(title_column, 1)
        header.addLayout(badge_row)
        layout.addLayout(header)

        self.main_window.install_banner = QFrame()
        self.main_window.install_banner.setObjectName("InstallBanner")
        self.main_window.install_status_badge = QLabel()
        self.main_window.install_status_badge.setObjectName("InstallStatusBadge")
        self.main_window.install_status_label = QLabel()
        self.main_window.install_status_label.setObjectName("InstallStatusText")
        self.main_window.install_status_label.setWordWrap(True)
        self.main_window.install_cancel_btn = QPushButton()
        self.main_window.install_cancel_btn.setObjectName("InstallCancelButton")
        self.main_window.install_cancel_btn.setProperty("variant", "neutral")

        install_layout = QHBoxLayout(self.main_window.install_banner)
        install_layout.setContentsMargins(12, 8, 12, 8)
        install_layout.setSpacing(8)
        install_layout.addWidget(self.main_window.install_status_badge)
        install_layout.addWidget(self.main_window.install_status_label, 1)
        install_layout.addWidget(self.main_window.install_cancel_btn)
        self.main_window.install_banner.setVisible(False)
        layout.addWidget(self.main_window.install_banner)

        metrics = QGridLayout()
        metrics.setContentsMargins(0, 0, 0, 0)
        metrics.setHorizontalSpacing(5)
        metrics.setVerticalSpacing(5)
        self.main_window.checked_card = self._metric_card("checked")
        self.main_window.hit_card = self._metric_card("hit")
        self.main_window.error_card = self._metric_card("error")
        self.main_window.rate_card = self._metric_card("rate")
        metrics.addWidget(self.main_window.checked_card, 0, 0)
        metrics.addWidget(self.main_window.hit_card, 0, 1)
        metrics.addWidget(self.main_window.error_card, 1, 0)
        metrics.addWidget(self.main_window.rate_card, 1, 1)
        metrics.setColumnStretch(0, 1)
        metrics.setColumnStretch(1, 1)
        layout.addLayout(metrics)

        self.main_window.pause_btn = QPushButton()
        self.main_window.pause_btn.setProperty("variant", "neutral")
        self.main_window.pause_btn.setMinimumWidth(92)

        self.main_window.stop_btn = QPushButton()
        self.main_window.stop_btn.setProperty("variant", "neutral")
        self.main_window.stop_btn.setMinimumWidth(92)

        self.main_window.start_btn = QPushButton()
        self.main_window.start_btn.setMinimumHeight(36)
        self.main_window.start_btn.setStyleSheet(
            "QPushButton { background: #1fb76a; color: white; border-radius: 10px; "
            "font-size: 12px; font-weight: 700; padding: 0 16px; }"
            "QPushButton:hover { background: #18a85f; }"
            "QPushButton:pressed { background: #159451; }"
            "QPushButton:disabled { background: #9fd7b8; color: white; }"
        )

        controls = QHBoxLayout()
        controls.setSpacing(6)
        controls.addWidget(self.main_window.pause_btn)
        controls.addWidget(self.main_window.stop_btn)
        controls.addWidget(self.main_window.start_btn, 1)
        layout.addLayout(controls)
        return panel

    def _build_insights_panel(self) -> QFrame:
        panel = self._panel()
        self.main_window.insights_panel = panel
        panel.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout = self._panel_layout(panel)
        layout.setSpacing(12)

        self.main_window.insights_panel_title_label = QLabel()
        self.main_window.insights_panel_title_label.setObjectName("PanelTitle")
        self.main_window.insights_panel_subtitle_label = QLabel()
        self.main_window.insights_panel_subtitle_label.setObjectName("PanelSubtitle")
        self.main_window.insights_panel_subtitle_label.setWordWrap(True)

        header = QVBoxLayout()
        header.setSpacing(4)
        header.addWidget(self.main_window.insights_panel_title_label)
        header.addWidget(self.main_window.insights_panel_subtitle_label)
        layout.addLayout(header)

        self.main_window.insights_tabs = QTabWidget()
        self.main_window.insights_tabs.setObjectName("InsightsTabs")
        self.main_window.insights_tabs.setDocumentMode(True)
        self.main_window.insights_tabs.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.main_window.insights_tabs.tabBar().setObjectName("InsightsTabBar")
        self.main_window.insights_tabs.tabBar().setDrawBase(False)
        self.main_window.insights_tabs.tabBar().setCursor(Qt.CursorShape.PointingHandCursor)

        activity_tab = QWidget()
        activity_layout = QVBoxLayout(activity_tab)
        activity_layout.setContentsMargins(0, 4, 0, 0)
        self.main_window.activity_plot = pg.PlotWidget()
        self.main_window.activity_plot.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        activity_layout.addWidget(self.main_window.activity_plot)

        rate_tab = QWidget()
        rate_layout = QVBoxLayout(rate_tab)
        rate_layout.setContentsMargins(0, 4, 0, 0)
        self.main_window.rate_plot = pg.PlotWidget()
        self.main_window.rate_plot.setMinimumHeight(90)
        rate_layout.addWidget(self.main_window.rate_plot)

        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)
        log_layout.setContentsMargins(0, 4, 0, 0)
        self.main_window.log = QTextEdit()
        self.main_window.log.setReadOnly(True)
        self.main_window.log.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        log_layout.addWidget(self.main_window.log)

        self.main_window.insights_tabs.addTab(activity_tab, "")
        self.main_window.insights_tabs.addTab(rate_tab, "")
        self.main_window.insights_tabs.addTab(log_tab, "")
        layout.addWidget(self.main_window.insights_tabs, 1)
        return panel

    def _panel(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("Panel")
        return panel

    @staticmethod
    def _panel_layout(panel: QFrame) -> QVBoxLayout:
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        return layout

    def _build_card_header(
        self,
        *,
        icon_text: str,
        icon_background: str,
        title_label: QLabel,
        subtitle_label: QLabel,
        eyebrow_label: QLabel | None = None,
        badge_label: QLabel | None = None,
    ) -> QWidget:
        wrapper = QWidget()
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        icon = QLabel(icon_text)
        icon.setFixedSize(30, 30)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"background: {icon_background}; color: white; border-radius: 9px; "
            "font-size: 13px; font-weight: 800;"
        )
        layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignTop)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(2)

        if eyebrow_label is not None:
            eyebrow_label.setWordWrap(True)
            text_layout.addWidget(eyebrow_label)

        title_label.setWordWrap(True)
        subtitle_label.setWordWrap(True)
        text_layout.addWidget(title_label)
        text_layout.addWidget(subtitle_label)

        if badge_label is not None:
            badge_label.setWordWrap(True)
            text_layout.addWidget(badge_label)

        layout.addLayout(text_layout, 1)
        return wrapper

    def _build_top_card_header(
        self,
        *,
        icon_text: str,
        icon_background: str,
        title_label: QLabel,
        subtitle_label: QLabel,
        trailing_label: QLabel | None = None,
    ) -> QWidget:
        wrapper = QWidget()
        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(9)

        icon = QLabel(icon_text)
        icon.setFixedSize(28, 28)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(
            f"background: {icon_background}; color: white; border-radius: 8px; "
            "font-size: 12px; font-weight: 800;"
        )
        layout.addWidget(icon, 0, Qt.AlignmentFlag.AlignTop)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(6)

        title_label.setWordWrap(False)
        title_row.addWidget(title_label, 1)

        if trailing_label is not None:
            trailing_label.setWordWrap(False)
            title_row.addWidget(trailing_label, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        text_layout.addLayout(title_row)
        subtitle_label.setWordWrap(False)
        text_layout.addWidget(subtitle_label)

        layout.addLayout(text_layout, 1)
        return wrapper

    def _field_block(self, label_widget: QLabel, input_widget: QWidget) -> QWidget:
        label_widget.setObjectName("HintLabel")
        label_widget.setWordWrap(True)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(label_widget)
        layout.addWidget(input_widget)
        return container

    @staticmethod
    def _checkbox_block(checkbox: QCheckBox) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(checkbox)
        layout.addStretch(1)
        return container

    def _collapsible_section(
        self,
        title_label: QLabel,
        content_builder,
        *,
        expanded: bool,
    ) -> QFrame:
        panel = self._panel()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        title_label.setObjectName("PanelTitle")
        title_label.setWordWrap(True)

        header = QHBoxLayout()
        header.setSpacing(4)
        header.addWidget(title_label)
        header.addStretch(1)

        toggle_button = QToolButton()
        toggle_button.setCheckable(True)
        toggle_button.setChecked(expanded)
        toggle_button.setAutoRaise(True)
        toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        toggle_button.setStyleSheet("QToolButton { border: none; padding: 0px; color: #64748b; }")
        header.addWidget(toggle_button)
        layout.addLayout(header)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 2, 0, 0)
        content_layout.setSpacing(8)
        content_builder(content_layout)
        layout.addWidget(content)

        def apply_state(checked: bool) -> None:
            content.setVisible(checked)
            toggle_button.setArrowType(
                Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow
            )
            panel.setMaximumHeight(16777215 if checked else 52)

        toggle_button.toggled.connect(apply_state)
        apply_state(expanded)
        return panel

    def _metric_card(self, tone: str) -> QFrame:
        card = QFrame()
        card.setObjectName("MetricCard")
        card.setProperty("tone", tone)
        card.setFixedHeight(68)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(11, 6, 11, 6)
        layout.setSpacing(0)

        card.value_label = QLabel("0")
        card.value_label.setObjectName("MetricValue")

        card.title_label = QLabel()
        card.title_label.setObjectName("MetricTitle")
        card.title_label.setWordWrap(True)

        card.subtitle_label = QLabel()
        card.subtitle_label.setObjectName("MetricSubtitle")
        card.subtitle_label.setWordWrap(True)

        layout.addWidget(card.value_label)
        layout.addWidget(card.title_label)
        layout.addWidget(card.subtitle_label)
        layout.addStretch(1)
        return card


class _ViewportFillScrollArea(QScrollArea):
    def setWidget(self, widget: QWidget) -> None:
        super().setWidget(widget)
        self._sync_widget_min_height()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._sync_widget_min_height()

    def _sync_widget_min_height(self) -> None:
        widget = self.widget()
        if widget is not None:
            widget.setMinimumHeight(self.viewport().height())
