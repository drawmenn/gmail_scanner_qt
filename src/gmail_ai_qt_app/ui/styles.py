from __future__ import annotations


def main_window_qss() -> str:
    return """
QMainWindow {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #f0f7ff, stop:0.45 #e0edff, stop:1 #d0e3ff
    );
}

        QWidget {
            color: #152536;
            font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC";
            font-size: 12px;
        }

        QScrollArea#PageScrollArea {
            background: transparent;
            border: none;
        }

        QScrollArea#PageScrollArea > QWidget > QWidget {
            background: transparent;
        }

        QFrame#Sidebar {
            background: transparent;
            border: none;
        }

        QFrame#QuickPanel {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #eef5f5, stop:1 #e5efec
            );
            border: 1px solid #cfdee1;
            border-radius: 20px;
        }

        QFrame#QuickPanel QLabel#Eyebrow {
            color: #5b7680;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
        }

        QFrame#QuickPanel QLabel#SidebarTitle {
            color: #173043;
            font-size: 19px;
            font-weight: 700;
        }

        QFrame#QuickPanel QLabel#SidebarSubtitle {
            color: #5d7384;
            font-size: 13px;
            line-height: 1.3;
        }

        QFrame#BrandPanel {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #17384a, stop:0.55 #1d5661, stop:1 #2d746f
            );
            border: 1px solid rgba(20, 55, 74, 0.18);
            border-radius: 20px;
        }

        QLabel#Eyebrow {
            color: rgba(236, 247, 247, 0.78);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
        }

        QLabel#SidebarTitle {
            color: #f6fbfb;
            font-size: 17px;
            font-weight: 700;
        }

        QLabel#SidebarSubtitle {
            color: rgba(235, 245, 246, 0.85);
            font-size: 13px;
            line-height: 1.3;
        }

        QFrame#Panel {
            background: rgba(255, 255, 255, 0.96);
            border: none;
            border-radius: 16px;
        }

QLabel#PanelTitle {
    color: #183247;
    font-size: 14px;
    font-weight: 700;
}

QLabel#PanelTitle[compactTopCard="true"] {
    font-size: 13px;
}

QLabel#PanelTitle:hover {
    color: #1d6a78;
}

        QLabel#PanelSubtitle {
            color: #5c7085;
            font-size: 11px;
            font-weight: 600;
            line-height: 1.35;
        }

        QLabel#PanelSubtitle[compactTopCard="true"] {
            font-size: 10px;
        }

        QLabel#HintLabel {
            color: #4f6477;
            font-size: 11px;
            font-weight: 700;
        }

        QLabel#HintLabel[compactTopCard="true"] {
            font-size: 10px;
        }

        QLabel#ReviewCandidate {
            background: #fcfbf6;
            color: #173043;
            border: 1px solid #d9e1d2;
            border-radius: 10px;
            padding: 5px 10px;
            font-size: 13px;
            font-weight: 700;
        }

        QFrame#HeaderPanel {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid #d7e0e4;
            border-radius: 20px;
        }

        QFrame#ContentPanel {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid #d7e0e4;
            border-radius: 20px;
        }

        QTabWidget::pane {
            border: none;
            background: transparent;
        }

        QWidget#MainTabShell {
            background: transparent;
        }

        QStackedWidget#MainTabs {
            background: transparent;
        }

        QTabBar#MainTabBar {
            background: transparent;
            border: none;
        }

        QTabBar#MainTabBar::tab {
            background: rgba(255, 255, 255, 0.72);
            color: #5e7185;
            border: 1px solid #d7e2ec;
            border-radius: 13px;
            padding: 8px 18px;
            margin-right: 6px;
            min-width: 74px;
            font-size: 13px;
            font-weight: 700;
        }

        QTabBar#MainTabBar::tab:hover:!selected {
            background: rgba(255, 255, 255, 0.82);
            color: #27495f;
        }

        QTabBar#MainTabBar::tab:selected {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #ebfaf3, stop:1 #d9efe8
            );
            color: #125d63;
            border: 1px solid #b7d8d1;
        }

        QTabBar#MainTabBar::tab:first {
            margin-left: 0;
        }

        QTabWidget#InsightsTabs::pane {
            top: 10px;
        }

        QTabBar#InsightsTabBar {
            background: transparent;
            border: none;
        }

        QTabBar#InsightsTabBar::tab {
            background: #eef3f6;
            color: #607789;
            border: 1px solid #d8e3e7;
            border-radius: 10px;
            padding: 6px 14px;
            margin-right: 6px;
            min-width: 78px;
            font-size: 12px;
            font-weight: 700;
        }

        QTabBar#InsightsTabBar::tab:hover:!selected {
            background: rgba(255, 255, 255, 0.72);
            color: #2a5065;
        }

        QTabBar#InsightsTabBar::tab:selected {
            background: #ffffff;
            color: #165a6f;
            border: 1px solid #cddfe5;
        }

        QTabBar {
            border: none;
            background: transparent;
        }


QFrame#MetricCard {
    border: none;
    border-radius: 10px;
}

QFrame#MetricCard[tone="checked"] {
    background: #2196f3;
}

QFrame#MetricCard[tone="hit"] {
    background: #4caf50;
}

QFrame#MetricCard[tone="error"] {
    background: #f44336;
}

QFrame#MetricCard[tone="rate"] {
    background: #616161;
}

QFrame#ProgressSegment[color="blue"] {
    background: #2196f3;
    color: white;
    font-weight: bold;
}

QFrame#ProgressSegment[color="green"] {
    background: #4caf50;
    color: white;
    font-weight: bold;
}

QFrame#ProgressSegment[color="red"] {
    background: #f44336;
    color: white;
    font-weight: bold;
}

QFrame#ProgressSegment[color="gray"] {
    background: #616161;
    color: white;
    font-weight: bold;
}

QFrame#RateBar {
    background: #4caf50;
    border-radius: 4px;
}

QLabel#RateLabel {
    color: white;
    font-weight: bold;
}

        QLabel#PageTitle {
            font-size: 18px;
            font-weight: 700;
            color: #13283d;
        }

        QWidget#ChromiumStatusCorner {
            background: transparent;
        }

        QFrame#InstallBanner {
            border-radius: 13px;
            border: 1px solid #d7e2ec;
            background: rgba(255, 255, 255, 0.82);
        }

        QFrame#InstallBanner[state="hidden"] {
            background: transparent;
            border: none;
        }

        QFrame#InstallBanner[state="neutral"] {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid #d7e2ec;
        }

        QFrame#InstallBanner[state="missing"] {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #fff8e9, stop:1 #fff0d6
            );
            border: 1px solid #e7cb90;
        }

        QFrame#InstallBanner[state="partial"] {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #fff6df, stop:1 #feecd1
            );
            border: 1px solid #e5c17e;
        }

        QFrame#InstallBanner[state="running"] {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #eef7e8, stop:1 #e4f2df
            );
            border: 1px solid #bad7aa;
        }

        QFrame#InstallBanner[state="finished"] {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #edf9f2, stop:1 #e4f5ea
            );
            border: 1px solid #a7d8ba;
        }

        QFrame#InstallBanner[state="failed"] {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #fff0eb, stop:1 #fde7e2
            );
            border: 1px solid #e4b1a5;
        }

        QFrame#InstallBanner[state="canceled"] {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #fff4df, stop:1 #fceaca
            );
            border: 1px solid #e8c37b;
        }

        QLabel#InstallStatusBadge {
            border-radius: 8px;
            padding: 1px 5px;
            font-size: 9px;
            font-weight: 700;
        }

        QLabel#ChromiumStripTitle {
            color: #17364b;
            font-size: 10px;
            font-weight: 700;
        }

        QFrame#InstallBanner[state="running"] QLabel#InstallStatusBadge {
            background: #d9efe0;
            color: #14532d;
            border: 1px solid #9fd0a4;
        }

        QFrame#InstallBanner[state="finished"] QLabel#InstallStatusBadge {
            background: #dff7e8;
            color: #166534;
            border: 1px solid #9dd6b4;
        }

        QFrame#InstallBanner[state="failed"] QLabel#InstallStatusBadge {
            background: #fde4df;
            color: #9f1239;
            border: 1px solid #ebb0a6;
        }

        QFrame#InstallBanner[state="canceled"] QLabel#InstallStatusBadge {
            background: #fff0d4;
            color: #92400e;
            border: 1px solid #e8c276;
        }

        QFrame#InstallBanner[state="missing"] QLabel#InstallStatusBadge,
        QFrame#InstallBanner[state="partial"] QLabel#InstallStatusBadge {
            background: #ffefc8;
            color: #8a530c;
            border: 1px solid #e6c171;
        }

        QFrame#InstallBanner[state="neutral"] QLabel#InstallStatusBadge {
            background: #edf2f7;
            color: #45566b;
            border: 1px solid #d4dde7;
        }

        QLabel#InstallStatusText {
            color: #334556;
            line-height: 1.35;
            font-size: 10px;
            font-weight: 600;
        }

        QLabel#ChromiumStripMeta {
            color: #617588;
            font-size: 9px;
        }

        QLabel#ChromiumStripPercent {
            color: #486072;
            font-size: 9px;
            font-weight: 700;
            min-width: 22px;
        }

        QProgressBar#ChromiumStripProgress {
            background: rgba(214, 225, 232, 0.88);
            border: none;
            border-radius: 3px;
        }

        QProgressBar#ChromiumStripProgress::chunk {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #2b8a72, stop:1 #36b67b
            );
            border-radius: 3px;
        }

        QLabel#PageSubtitle, QLabel#ContentSubtitle, QLabel#MetricSubtitle {
            color: #5c7085;
            line-height: 1.35;
        }

        QLabel#ContentTitle, QLabel#MetricTitle {
            font-size: 15px;
            font-weight: 700;
            color: #183247;
        }

QLabel#MetricValue {
    color: white;
    font-size: 14px;
    font-weight: 700;
}

QLabel#MetricTitle {
    color: white;
    font-size: 11px;
}

QLabel#MetricSubtitle {
    color: rgba(255,255,255,0.85);
    font-size: 9px;
}

QLabel#StateBadge, QLabel#InfoBadge, QLabel#RequestBadge {
    border-radius: 10px;
    padding: 3px 7px;
    font-size: 10px;
    font-weight: 700;
}

        QLabel#StateBadge[state="running"] {
            background: #dcfce7;
            color: #166534;
            border: 1px solid #86efac;
        }

        QLabel#StateBadge[state="paused"] {
            background: #ffedd5;
            color: #9a3412;
            border: 1px solid #fdba74;
        }

        QLabel#StateBadge[state="stopped"] {
            background: #e2e8f0;
            color: #334155;
            border: 1px solid #cbd5e1;
        }

        QLabel#InfoBadge {
            background: #edf2f5;
            color: #40586b;
            border: 1px solid #d4dde3;
        }

        QLabel#RequestBadge[status="idle"] {
            background: #eef2f6;
            color: #44576a;
            border: 1px solid #d2dae1;
        }

        QLabel#RequestBadge[status="requesting"] {
            background: #dcf6ef;
            color: #126c60;
            border: 1px solid #97d8ca;
        }

        QLabel#RequestBadge[status="reviewing"] {
            background: #fff0d2;
            color: #8a5607;
            border: 1px solid #e5c16f;
        }

        QLabel#RequestBadge[status="canceled"] {
            background: #fff0d2;
            color: #8b5a10;
            border: 1px solid #ecc671;
        }

        QLabel#RequestBadge[status="error"] {
            background: #fde6e2;
            color: #9a3029;
            border: 1px solid #efb1a9;
        }

        QPushButton {
            min-height: 32px;
            border-radius: 10px;
            padding: 0 12px;
            font-size: 13px;
            font-weight: 600;
            border: none;
        }

QPushButton[variant="success"] {
    background: #1976d2;
    color: white;
}

        QPushButton[variant="success"]:hover {
            background: #18715f;
        }

        QPushButton[variant="warning"] {
            background: #e7b451;
            color: #432d10;
        }

        QPushButton[variant="warning"]:hover {
            background: #d8a03a;
        }

QPushButton[variant="danger"] {
    background: #d32f2f;
    color: white;
}

        QPushButton[variant="danger"]:hover {
            background: #b84c3f;
        }

        QPushButton[variant="neutral"] {
            background: #e9f0ee;
            color: #244052;
            border: 1px solid #d5dfe3;
        }

        QPushButton[variant="neutral"]:hover {
            background: #dde8e5;
        }

        QPushButton:disabled {
            background: #d9e0de;
            color: #93a29c;
            border: none;
        }

        QPushButton#InstallCancelButton {
            min-height: 20px;
            padding: 0 7px;
            border-radius: 7px;
            font-size: 10px;
        }

        QLineEdit, QListWidget, QTextEdit, QComboBox, QSpinBox {
            background: #fbfcfd;
            color: #152536;
            border: 1px solid #c8d5db;
            border-radius: 9px;
            padding: 6px 9px;
            selection-background-color: #cfe5dc;
        }

        QSpinBox {
            padding-right: 14px;
        }

        QLineEdit:focus, QListWidget:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {
            border: 1px solid #2a7d73;
        }

        QComboBox::drop-down, QSpinBox::up-button, QSpinBox::down-button {
            border: none;
            width: 20px;
        }

        QListWidget::item {
            padding: 6px;
            border-radius: 8px;
        }

        QListWidget::item:selected {
            background: #dcefe7;
            color: #214756;
        }

        QCheckBox {
            color: #274050;
            font-weight: 700;
            spacing: 6px;
        }

        QCheckBox::indicator {
            width: 14px;
            height: 14px;
            border-radius: 4px;
            border: 1px solid #bcccd2;
            background: #fbfcfd;
        }

        QCheckBox::indicator:checked {
            background: #2a7d73;
            border: 1px solid #2a7d73;
        }

        QTextEdit {
            font-family: "Consolas", "Microsoft YaHei UI";
            line-height: 1.45;
        }

        QScrollBar:vertical, QScrollBar:horizontal {
            background: transparent;
            width: 4px;
            height: 4px;
        }

        QScrollBar:vertical:hover, QScrollBar:horizontal:hover {
            width: 10px;
            height: 10px;
            background: rgba(27, 50, 64, 0.08);
        }

        QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
            background: rgba(41, 114, 123, 0.45);
            border-radius: 5px;
            min-height: 20px;
            min-width: 20px;
        }

        QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {
            background: rgba(41, 114, 123, 0.68);
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            background: transparent;
            border: none;
            width: 0;
            height: 0;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical,
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
            background: transparent;
        }
        """
