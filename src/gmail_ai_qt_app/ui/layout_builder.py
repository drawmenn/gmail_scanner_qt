from __future__ import annotations

import pyqtgraph as pg
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..i18n import available_languages
from ..services.providers import available_providers


class CollapsiblePanel(QFrame):
    def __init__(self, title: str = "", collapsed: bool = True):
        super().__init__()
        self.setObjectName("Panel")
        self._collapsed = collapsed

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(0)

        toggle_row = QHBoxLayout()
        toggle_row.setContentsMargins(0, 0, 0, 0)
        toggle_row.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("PanelTitle")
        self.arrow_label = QLabel()
        self.arrow_label.setObjectName("PanelTitle")
        self.arrow_label.setFixedWidth(18)

        toggle_row.addWidget(self.title_label, 1)
        toggle_row.addWidget(self.arrow_label)

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("PanelSubtitle")
        self.subtitle_label.setWordWrap(True)

        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self.body_layout = QVBoxLayout(self.content_widget)
        self.body_layout.setContentsMargins(0, 10, 0, 0)
        self.body_layout.setSpacing(10)

        outer.addLayout(toggle_row)
        outer.addWidget(self.subtitle_label)
        outer.addWidget(self.content_widget)

        self._update_arrow()
        self.content_widget.setVisible(not collapsed)
        self.subtitle_label.setVisible(not collapsed)

        self.title_label.mousePressEvent = lambda _: self.toggle()
        self.arrow_label.mousePressEvent = lambda _: self.toggle()

    def toggle(self) -> None:
        self._collapsed = not self._collapsed
        self.content_widget.setVisible(not self._collapsed)
        self.subtitle_label.setVisible(not self._collapsed)
        self._update_arrow()

    def _update_arrow(self) -> None:
        self.arrow_label.setText("\u25b6" if self._collapsed else "\u25bc")

    def body(self) -> QVBoxLayout:
        return self.body_layout


class MainWindowLayoutBuilder:
    def __init__(self, window):
        self.window = window

    def build(self) -> None:
        w = self.window
        settings = w.runtime_settings

        central = QWidget()
        w.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(18)

        sidebar_scroll = QScrollArea()
        sidebar_scroll.setObjectName("SidebarScroll")
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sidebar_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        sidebar_scroll.setFrameShape(QFrame.NoFrame)
        sidebar_scroll.setFixedWidth(356)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(18, 18, 18, 18)
        sidebar_layout.setSpacing(12)
        sidebar_layout.setSizeConstraint(QLayout.SetMinimumSize)

        brand = QFrame()
        brand.setObjectName("BrandPanel")
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(18, 18, 18, 18)
        brand_layout.setSpacing(6)

        w.eyebrow_label = QLabel()
        w.eyebrow_label.setObjectName("Eyebrow")
        w.sidebar_title_label = QLabel()
        w.sidebar_title_label.setObjectName("SidebarTitle")
        w.sidebar_subtitle_label = QLabel()
        w.sidebar_subtitle_label.setObjectName("SidebarSubtitle")
        w.sidebar_subtitle_label.setWordWrap(True)

        brand_layout.addWidget(w.eyebrow_label)
        brand_layout.addWidget(w.sidebar_title_label)
        brand_layout.addWidget(w.sidebar_subtitle_label)

        w.start_btn = QPushButton()
        w.start_btn.setProperty("variant", "success")
        w.pause_btn = QPushButton()
        w.pause_btn.setProperty("variant", "warning")
        w.stop_btn = QPushButton()
        w.stop_btn.setProperty("variant", "danger")

        display_panel, display_body, w.display_title_label, w.display_subtitle_label = self._create_panel()

        w.language_label = QLabel()
        w.language_label.setObjectName("HintLabel")
        w.language_combo = QComboBox()
        for language_code, native_name in available_languages():
            w.language_combo.addItem(native_name, language_code)
        current_language_index = w.language_combo.findData(settings.language)
        if current_language_index >= 0:
            w.language_combo.setCurrentIndex(current_language_index)

        display_body.addWidget(w.language_label)
        display_body.addWidget(w.language_combo)

        provider_panel = CollapsiblePanel(collapsed=True)
        provider_body = provider_panel.body()
        w.provider_title_label = provider_panel.title_label
        w.provider_subtitle_label = provider_panel.subtitle_label

        w.provider_label = QLabel()
        w.provider_label.setObjectName("HintLabel")
        w.provider_combo = QComboBox()
        for provider in available_providers():
            w.provider_combo.addItem("", provider.code)
        current_provider_index = w.provider_combo.findData(settings.provider)
        if current_provider_index >= 0:
            w.provider_combo.setCurrentIndex(current_provider_index)

        provider_body.addWidget(w.provider_label)
        provider_body.addWidget(w.provider_combo)

        custom_panel = CollapsiblePanel(collapsed=True)
        custom_body = custom_panel.body()
        w.custom_title_label = custom_panel.title_label
        w.custom_subtitle_label = custom_panel.subtitle_label
        w.custom_panel = custom_panel

        w.custom_url_label = QLabel()
        w.custom_url_label.setObjectName("HintLabel")
        w.custom_url_input = QLineEdit(settings.custom_url)

        custom_keywords_grid = QGridLayout()
        custom_keywords_grid.setContentsMargins(0, 0, 0, 0)
        custom_keywords_grid.setHorizontalSpacing(10)
        custom_keywords_grid.setVerticalSpacing(10)

        w.custom_method_label = QLabel()
        w.custom_method_label.setObjectName("HintLabel")
        w.custom_method_combo = QComboBox()
        w.custom_method_combo.addItem("", "GET")
        w.custom_method_combo.addItem("", "POST")
        current_method_index = w.custom_method_combo.findData(settings.custom_method)
        if current_method_index >= 0:
            w.custom_method_combo.setCurrentIndex(current_method_index)

        w.custom_param_label = QLabel()
        w.custom_param_label.setObjectName("HintLabel")
        w.custom_param_input = QLineEdit(settings.custom_param_name)
        w.custom_status_label = QLabel()
        w.custom_status_label.setObjectName("HintLabel")
        w.custom_status_input = QLineEdit(settings.custom_status_codes)
        w.custom_available_label = QLabel()
        w.custom_available_label.setObjectName("HintLabel")
        w.custom_available_input = QLineEdit(settings.custom_available_keyword)
        w.custom_taken_label = QLabel()
        w.custom_taken_label.setObjectName("HintLabel")
        w.custom_taken_input = QLineEdit(settings.custom_taken_keyword)
        w.custom_available_regex_label = QLabel()
        w.custom_available_regex_label.setObjectName("HintLabel")
        w.custom_available_regex_input = QLineEdit(settings.custom_available_regex)
        w.custom_taken_regex_label = QLabel()
        w.custom_taken_regex_label.setObjectName("HintLabel")
        w.custom_taken_regex_input = QLineEdit(settings.custom_taken_regex)
        w.custom_headers_label = QLabel()
        w.custom_headers_label.setObjectName("HintLabel")
        w.custom_headers_input = QTextEdit()
        w.custom_headers_input.setPlainText(settings.custom_headers)
        w.custom_headers_input.setMaximumHeight(74)
        w.custom_body_label = QLabel()
        w.custom_body_label.setObjectName("HintLabel")
        w.custom_body_input = QTextEdit()
        w.custom_body_input.setPlainText(settings.custom_body_template)
        w.custom_body_input.setMaximumHeight(90)

        custom_keywords_grid.addWidget(w.custom_method_label, 0, 0)
        custom_keywords_grid.addWidget(w.custom_method_combo, 0, 1)
        custom_keywords_grid.addWidget(w.custom_param_label, 1, 0)
        custom_keywords_grid.addWidget(w.custom_param_input, 1, 1)
        custom_keywords_grid.addWidget(w.custom_status_label, 2, 0)
        custom_keywords_grid.addWidget(w.custom_status_input, 2, 1)
        custom_keywords_grid.addWidget(w.custom_available_label, 3, 0)
        custom_keywords_grid.addWidget(w.custom_available_input, 3, 1)
        custom_keywords_grid.addWidget(w.custom_taken_label, 4, 0)
        custom_keywords_grid.addWidget(w.custom_taken_input, 4, 1)
        custom_keywords_grid.addWidget(w.custom_available_regex_label, 5, 0)
        custom_keywords_grid.addWidget(w.custom_available_regex_input, 5, 1)
        custom_keywords_grid.addWidget(w.custom_taken_regex_label, 6, 0)
        custom_keywords_grid.addWidget(w.custom_taken_regex_input, 6, 1)

        custom_body.addWidget(w.custom_url_label)
        custom_body.addWidget(w.custom_url_input)
        custom_body.addLayout(custom_keywords_grid)
        custom_body.addWidget(w.custom_headers_label)
        custom_body.addWidget(w.custom_headers_input)
        custom_body.addWidget(w.custom_body_label)
        custom_body.addWidget(w.custom_body_input)

        browser_panel = CollapsiblePanel(collapsed=True)
        browser_body = browser_panel.body()
        w.browser_title_label = browser_panel.title_label
        w.browser_subtitle_label = browser_panel.subtitle_label
        w.browser_panel = browser_panel

        w.browser_url_label = QLabel()
        w.browser_url_label.setObjectName("HintLabel")
        w.browser_url_input = QLineEdit(settings.browser_url)

        browser_selector_grid = QGridLayout()
        browser_selector_grid.setContentsMargins(0, 0, 0, 0)
        browser_selector_grid.setHorizontalSpacing(10)
        browser_selector_grid.setVerticalSpacing(10)

        w.browser_input_label = QLabel()
        w.browser_input_label.setObjectName("HintLabel")
        w.browser_input_input = QLineEdit(settings.browser_input_selector)
        w.browser_value_label = QLabel()
        w.browser_value_label.setObjectName("HintLabel")
        w.browser_value_input = QLineEdit(settings.browser_value_template)
        w.browser_submit_label = QLabel()
        w.browser_submit_label.setObjectName("HintLabel")
        w.browser_submit_input = QLineEdit(settings.browser_submit_selector)
        w.browser_timeout_label = QLabel()
        w.browser_timeout_label.setObjectName("HintLabel")
        w.browser_timeout_spin = QSpinBox()
        w.browser_timeout_spin.setRange(1000, 120000)
        w.browser_timeout_spin.setSingleStep(1000)
        w.browser_timeout_spin.setValue(settings.browser_timeout_ms)
        w.browser_delay_label = QLabel()
        w.browser_delay_label.setObjectName("HintLabel")
        w.browser_delay_spin = QSpinBox()
        w.browser_delay_spin.setRange(0, 60000)
        w.browser_delay_spin.setSingleStep(100)
        w.browser_delay_spin.setValue(settings.browser_delay_ms)
        w.browser_headless_check = QCheckBox()
        w.browser_headless_check.setChecked(settings.browser_headless)

        browser_selector_grid.addWidget(w.browser_input_label, 0, 0)
        browser_selector_grid.addWidget(w.browser_input_input, 0, 1)
        browser_selector_grid.addWidget(w.browser_value_label, 1, 0)
        browser_selector_grid.addWidget(w.browser_value_input, 1, 1)
        browser_selector_grid.addWidget(w.browser_submit_label, 2, 0)
        browser_selector_grid.addWidget(w.browser_submit_input, 2, 1)
        browser_selector_grid.addWidget(w.browser_timeout_label, 3, 0)
        browser_selector_grid.addWidget(w.browser_timeout_spin, 3, 1)
        browser_selector_grid.addWidget(w.browser_delay_label, 4, 0)
        browser_selector_grid.addWidget(w.browser_delay_spin, 4, 1)

        browser_result_grid = QGridLayout()
        browser_result_grid.setContentsMargins(0, 0, 0, 0)
        browser_result_grid.setHorizontalSpacing(10)
        browser_result_grid.setVerticalSpacing(10)

        w.browser_available_selector_label = QLabel()
        w.browser_available_selector_label.setObjectName("HintLabel")
        w.browser_available_selector_input = QLineEdit(settings.browser_available_selector)
        w.browser_available_text_label = QLabel()
        w.browser_available_text_label.setObjectName("HintLabel")
        w.browser_available_text_input = QLineEdit(settings.browser_available_text)
        w.browser_available_regex_label = QLabel()
        w.browser_available_regex_label.setObjectName("HintLabel")
        w.browser_available_regex_input = QLineEdit(settings.browser_available_regex)
        w.browser_taken_selector_label = QLabel()
        w.browser_taken_selector_label.setObjectName("HintLabel")
        w.browser_taken_selector_input = QLineEdit(settings.browser_taken_selector)
        w.browser_taken_text_label = QLabel()
        w.browser_taken_text_label.setObjectName("HintLabel")
        w.browser_taken_text_input = QLineEdit(settings.browser_taken_text)
        w.browser_taken_regex_label = QLabel()
        w.browser_taken_regex_label.setObjectName("HintLabel")
        w.browser_taken_regex_input = QLineEdit(settings.browser_taken_regex)

        browser_result_grid.addWidget(w.browser_available_selector_label, 0, 0)
        browser_result_grid.addWidget(w.browser_available_selector_input, 0, 1)
        browser_result_grid.addWidget(w.browser_available_text_label, 1, 0)
        browser_result_grid.addWidget(w.browser_available_text_input, 1, 1)
        browser_result_grid.addWidget(w.browser_available_regex_label, 2, 0)
        browser_result_grid.addWidget(w.browser_available_regex_input, 2, 1)
        browser_result_grid.addWidget(w.browser_taken_selector_label, 3, 0)
        browser_result_grid.addWidget(w.browser_taken_selector_input, 3, 1)
        browser_result_grid.addWidget(w.browser_taken_text_label, 4, 0)
        browser_result_grid.addWidget(w.browser_taken_text_input, 4, 1)
        browser_result_grid.addWidget(w.browser_taken_regex_label, 5, 0)
        browser_result_grid.addWidget(w.browser_taken_regex_input, 5, 1)

        w.browser_headers_label = QLabel()
        w.browser_headers_label.setObjectName("HintLabel")
        w.browser_headers_input = QTextEdit()
        w.browser_headers_input.setPlainText(settings.browser_headers)
        w.browser_headers_input.setMaximumHeight(72)

        browser_body.addWidget(w.browser_url_label)
        browser_body.addWidget(w.browser_url_input)
        browser_body.addLayout(browser_selector_grid)
        browser_body.addWidget(w.browser_headless_check)
        browser_body.addLayout(browser_result_grid)
        browser_body.addWidget(w.browser_headers_label)
        browser_body.addWidget(w.browser_headers_input)

        proxy_panel = CollapsiblePanel(collapsed=True)
        proxy_body = proxy_panel.body()
        w.proxy_title_label = proxy_panel.title_label
        w.proxy_subtitle_label = proxy_panel.subtitle_label

        w.proxy_check = QCheckBox()
        w.proxy_input = QLineEdit(settings.proxy_url)

        proxy_body.addWidget(w.proxy_check)
        proxy_body.addWidget(w.proxy_input)

        names_panel, names_body, w.names_title_label, w.names_subtitle_label = self._create_panel()

        w.seed_count = QLabel()
        w.seed_count.setObjectName("HintLabel")

        names_row = QHBoxLayout()
        names_row.setContentsMargins(0, 0, 0, 0)
        names_row.setSpacing(10)

        w.name_input = QLineEdit()
        w.add_btn = QPushButton()
        w.add_btn.setProperty("variant", "neutral")
        w.remove_btn = QPushButton()
        w.remove_btn.setProperty("variant", "danger")

        names_row.addWidget(w.name_input, 1)
        names_row.addWidget(w.add_btn)
        names_row.addWidget(w.remove_btn)

        from PySide6.QtWidgets import QAbstractItemView
        w.name_list = QListWidget()
        w.name_list.addItems(settings.seeds)
        w.name_list.setMinimumHeight(150)
        w.name_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        names_body.addWidget(w.seed_count)
        names_body.addLayout(names_row)
        names_body.addWidget(w.name_list)

        generator_panel = CollapsiblePanel(collapsed=False)
        generator_body = generator_panel.body()
        w.generator_title_label = generator_panel.title_label
        w.generator_subtitle_label = generator_panel.subtitle_label

        w.generator_source_label = QLabel()
        w.generator_source_label.setObjectName("HintLabel")
        w.generator_source_input = QLineEdit()

        generator_options_row = QGridLayout()
        generator_options_row.setContentsMargins(0, 0, 0, 0)
        generator_options_row.setHorizontalSpacing(10)
        generator_options_row.setVerticalSpacing(10)

        w.generator_length_label = QLabel()
        w.generator_length_label.setObjectName("HintLabel")
        w.generator_length_combo = QComboBox()
        for value in range(6, 13):
            w.generator_length_combo.addItem(str(value), value)
        w.generator_length_combo.setCurrentIndex(0)

        w.generator_count_label = QLabel()
        w.generator_count_label.setObjectName("HintLabel")
        w.generator_count_spin = QSpinBox()
        w.generator_count_spin.setRange(20, 500)
        w.generator_count_spin.setSingleStep(10)
        w.generator_count_spin.setValue(80)

        w.generator_digits_check = QCheckBox()
        w.generate_candidates_btn = QPushButton()
        w.generate_candidates_btn.setProperty("variant", "neutral")

        generator_options_row.addWidget(w.generator_length_label, 0, 0)
        generator_options_row.addWidget(w.generator_length_combo, 0, 1)
        generator_options_row.addWidget(w.generator_count_label, 1, 0)
        generator_options_row.addWidget(w.generator_count_spin, 1, 1)

        generator_body.addWidget(w.generator_source_label)
        generator_body.addWidget(w.generator_source_input)
        generator_body.addLayout(generator_options_row)
        generator_body.addWidget(w.generator_digits_check)
        generator_body.addWidget(w.generate_candidates_btn)

        review_panel = CollapsiblePanel(collapsed=False)
        review_body = review_panel.body()
        w.review_title_label = review_panel.title_label
        w.review_subtitle_label = review_panel.subtitle_label

        w.review_candidate_label = QLabel()
        w.review_candidate_label.setObjectName("ReviewCandidate")
        w.review_candidate_label.setWordWrap(True)

        w.auto_review_check = QCheckBox()
        w.auto_review_check.setChecked(settings.manual_auto_enabled)

        auto_review_row = QHBoxLayout()
        auto_review_row.setContentsMargins(0, 0, 0, 0)
        auto_review_row.setSpacing(10)

        w.auto_review_action_label = QLabel()
        w.auto_review_action_label.setObjectName("HintLabel")
        w.auto_review_action_combo = QComboBox()
        for action in w.AUTO_REVIEW_ACTIONS:
            w.auto_review_action_combo.addItem("", action)
        current_auto_action_index = w.auto_review_action_combo.findData(settings.manual_auto_action)
        if current_auto_action_index >= 0:
            w.auto_review_action_combo.setCurrentIndex(current_auto_action_index)

        auto_review_row.addWidget(w.auto_review_action_label)
        auto_review_row.addWidget(w.auto_review_action_combo, 1)

        review_actions = QGridLayout()
        review_actions.setContentsMargins(0, 0, 0, 0)
        review_actions.setHorizontalSpacing(10)
        review_actions.setVerticalSpacing(10)

        w.mark_available_btn = QPushButton()
        w.mark_available_btn.setProperty("variant", "success")
        w.mark_taken_btn = QPushButton()
        w.mark_taken_btn.setProperty("variant", "danger")
        w.mark_hold_btn = QPushButton()
        w.mark_hold_btn.setProperty("variant", "neutral")
        w.skip_candidate_btn = QPushButton()
        w.skip_candidate_btn.setProperty("variant", "warning")

        review_actions.addWidget(w.mark_available_btn, 0, 0)
        review_actions.addWidget(w.mark_taken_btn, 0, 1)
        review_actions.addWidget(w.mark_hold_btn, 1, 0)
        review_actions.addWidget(w.skip_candidate_btn, 1, 1)

        review_tools = QGridLayout()
        review_tools.setContentsMargins(0, 0, 0, 0)
        review_tools.setHorizontalSpacing(10)
        review_tools.setVerticalSpacing(10)

        w.copy_candidate_btn = QPushButton()
        w.copy_candidate_btn.setProperty("variant", "neutral")
        w.open_review_page_btn = QPushButton()
        w.open_review_page_btn.setProperty("variant", "neutral")
        w.export_csv_btn = QPushButton()
        w.export_csv_btn.setProperty("variant", "neutral")

        review_tools.addWidget(w.copy_candidate_btn, 0, 0)
        review_tools.addWidget(w.open_review_page_btn, 0, 1)
        review_tools.addWidget(w.export_csv_btn, 1, 0, 1, 2)

        review_body.addWidget(w.review_candidate_label)
        review_body.addWidget(w.auto_review_check)
        review_body.addLayout(auto_review_row)
        review_body.addLayout(review_actions)
        review_body.addLayout(review_tools)

        sidebar_layout.addWidget(brand)
        sidebar_layout.addWidget(display_panel)
        sidebar_layout.addWidget(names_panel, 1)
        sidebar_layout.addWidget(generator_panel)
        sidebar_layout.addWidget(provider_panel)
        sidebar_layout.addWidget(custom_panel)
        sidebar_layout.addWidget(browser_panel)
        sidebar_layout.addWidget(proxy_panel)
        sidebar_layout.addWidget(review_panel)
        sidebar_scroll.setWidget(sidebar)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        header = QFrame()
        header.setObjectName("HeaderPanel")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(22, 20, 22, 20)
        header_layout.setSpacing(18)

        header_left = QVBoxLayout()
        header_left.setContentsMargins(0, 0, 0, 0)
        header_left.setSpacing(6)

        w.page_title = QLabel()
        w.page_title.setObjectName("PageTitle")
        w.page_note = QLabel()
        w.page_note.setObjectName("PageSubtitle")
        w.page_note.setWordWrap(True)

        header_left.addWidget(w.page_title)
        header_left.addWidget(w.page_note)

        header_right = QHBoxLayout()
        header_right.setContentsMargins(0, 0, 0, 0)
        header_right.setSpacing(10)

        w.state_badge = QLabel()
        w.state_badge.setObjectName("StateBadge")
        w.state_badge.setProperty("state", "stopped")

        w.proxy_badge = QLabel()
        w.proxy_badge.setObjectName("InfoBadge")

        w.request_badge = QLabel()
        w.request_badge.setObjectName("RequestBadge")
        w.request_badge.setProperty("status", "idle")

        w.seed_badge = QLabel()
        w.seed_badge.setObjectName("InfoBadge")

        w.rate_badge = QLabel()
        w.rate_badge.setObjectName("InfoBadge")

        header_right.addWidget(w.state_badge)
        header_right.addWidget(w.proxy_badge)
        header_right.addWidget(w.request_badge)
        header_right.addWidget(w.seed_badge)
        header_right.addWidget(w.rate_badge)

        header_controls = QGridLayout()
        header_controls.setContentsMargins(0, 0, 0, 0)
        header_controls.setHorizontalSpacing(8)
        header_controls.setVerticalSpacing(8)
        header_controls.addWidget(w.start_btn, 0, 0, 1, 2)
        header_controls.addWidget(w.pause_btn, 1, 0)
        header_controls.addWidget(w.stop_btn, 1, 1)

        header_right.addSpacing(6)
        header_right.addLayout(header_controls)

        header_layout.addLayout(header_left, 1)
        header_layout.addLayout(header_right)

        install_banner = QFrame()
        install_banner.setObjectName("InstallBanner")
        install_banner.setProperty("state", "hidden")
        install_banner_layout = QHBoxLayout(install_banner)
        install_banner_layout.setContentsMargins(16, 12, 16, 12)
        install_banner_layout.setSpacing(10)

        w.install_status_badge = QLabel()
        w.install_status_badge.setObjectName("InstallStatusBadge")

        w.install_status_label = QLabel()
        w.install_status_label.setObjectName("InstallStatusText")
        w.install_status_label.setWordWrap(True)

        w.install_cancel_btn = QPushButton()
        w.install_cancel_btn.setObjectName("InstallCancelButton")
        w.install_cancel_btn.setProperty("variant", "neutral")
        w.install_cancel_btn.setFixedHeight(34)

        install_banner_layout.addWidget(w.install_status_badge)
        install_banner_layout.addWidget(w.install_status_label, 1)
        install_banner_layout.addWidget(w.install_cancel_btn)

        w.install_banner = install_banner

        cards_row = QHBoxLayout()
        cards_row.setContentsMargins(0, 0, 0, 0)
        cards_row.setSpacing(14)

        w.checked_card = self._create_metric_card("#0f766e", "checked")
        w.hit_card = self._create_metric_card("#16a34a", "hit")
        w.error_card = self._create_metric_card("#dc2626", "error")
        w.rate_card = self._create_metric_card("#c2410c", "rate")

        cards_row.addWidget(w.checked_card)
        cards_row.addWidget(w.hit_card)
        cards_row.addWidget(w.error_card)
        cards_row.addWidget(w.rate_card)

        plots_row = QHBoxLayout()
        plots_row.setContentsMargins(0, 0, 0, 0)
        plots_row.setSpacing(14)

        activity_panel, activity_body, w.activity_panel_title_label, w.activity_panel_subtitle_label = (
            self._create_content_panel()
        )
        w.activity_plot = pg.PlotWidget()
        activity_body.addWidget(w.activity_plot)

        rate_panel, rate_body, w.rate_panel_title_label, w.rate_panel_subtitle_label = (
            self._create_content_panel()
        )
        w.rate_plot = pg.PlotWidget()
        rate_body.addWidget(w.rate_plot)

        plots_row.addWidget(activity_panel, 2)
        plots_row.addWidget(rate_panel, 1)

        log_panel, log_body, w.log_panel_title_label, w.log_panel_subtitle_label = self._create_content_panel()
        w.log = QTextEdit()
        w.log.setReadOnly(True)
        log_body.addWidget(w.log)

        content_layout.addWidget(header)
        content_layout.addWidget(install_banner)
        content_layout.addLayout(cards_row)
        content_layout.addLayout(plots_row, 1)
        content_layout.addWidget(log_panel, 1)

        root.addWidget(sidebar_scroll)
        root.addWidget(content, 1)

    @staticmethod
    def _create_panel():
        panel = QFrame()
        panel.setObjectName("Panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        heading = QLabel()
        heading.setObjectName("PanelTitle")
        note = QLabel()
        note.setObjectName("PanelSubtitle")
        note.setWordWrap(True)

        layout.addWidget(heading)
        layout.addWidget(note)

        body = QVBoxLayout()
        body.setContentsMargins(0, 2, 0, 0)
        body.setSpacing(10)
        layout.addLayout(body)
        return panel, body, heading, note

    @staticmethod
    def _create_content_panel():
        panel = QFrame()
        panel.setObjectName("ContentPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        heading = QLabel()
        heading.setObjectName("ContentTitle")
        note = QLabel()
        note.setObjectName("ContentSubtitle")
        note.setWordWrap(True)

        layout.addWidget(heading)
        layout.addWidget(note)

        body = QVBoxLayout()
        body.setContentsMargins(0, 2, 0, 0)
        body.setSpacing(0)
        layout.addLayout(body, 1)
        return panel, body, heading, note

    @staticmethod
    def _create_metric_card(accent: str, tone: str):
        card = QFrame()
        card.setObjectName("MetricCard")
        card.setProperty("tone", tone)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        accent_bar = QFrame()
        accent_bar.setFixedHeight(6)
        accent_bar.setStyleSheet(f"background: {accent}; border: none; border-radius: 3px;")

        title_label = QLabel()
        title_label.setObjectName("MetricTitle")

        value_label = QLabel("0")
        value_label.setObjectName("MetricValue")
        value_label.setStyleSheet(f"color: {accent};")

        subtitle_label = QLabel()
        subtitle_label.setObjectName("MetricSubtitle")
        subtitle_label.setWordWrap(True)

        layout.addWidget(accent_bar)
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)

        card.title_label = title_label
        card.value_label = value_label
        card.subtitle_label = subtitle_label
        return card
