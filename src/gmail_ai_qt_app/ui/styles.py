from __future__ import annotations


def main_window_qss() -> str:
    return """
        QMainWindow {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #dce7df, stop:0.5 #eef2e5, stop:1 #d6e3df
            );
        }

        QWidget {
            color: #102033;
            font-family: "Segoe UI", "Microsoft YaHei UI", "PingFang SC";
            font-size: 13px;
        }

        QFrame#Sidebar {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #0d4150, stop:0.45 #103747, stop:1 #0b2231
            );
            border: 1px solid rgba(243, 200, 84, 0.16);
            border-radius: 24px;
        }

        QScrollArea#SidebarScroll {
            background: transparent;
            border: none;
        }

        QScrollArea#SidebarScroll > QWidget > QWidget {
            background: transparent;
        }

        QFrame#BrandPanel {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #f5d77e, stop:0.52 #efba49, stop:1 #d8891f
            );
            border: 1px solid rgba(124, 78, 15, 0.26);
            border-radius: 18px;
        }

        QLabel#Eyebrow {
            color: rgba(24, 24, 24, 0.84);
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1px;
        }

        QLabel#SidebarTitle {
            color: #0f2440;
            font-size: 24px;
            font-weight: 700;
        }

        QLabel#SidebarSubtitle {
            color: rgba(19, 33, 58, 0.88);
            line-height: 1.35;
        }

        QFrame#Panel {
            background: rgba(4, 22, 32, 0.46);
            border: 1px solid rgba(244, 203, 97, 0.22);
            border-radius: 18px;
        }

        QLabel#PanelTitle {
            color: #fff7dc;
            font-size: 17px;
            font-weight: 700;
            cursor: pointer;
        }

        QLabel#PanelTitle:hover {
            color: #f2c14d;
        }

        QLabel#PanelSubtitle {
            color: rgba(252, 247, 231, 0.97);
            font-size: 13px;
            font-weight: 700;
            line-height: 1.35;
        }

        QLabel#HintLabel {
            color: #ffe6a8;
            font-size: 12px;
            font-weight: 700;
        }

        QLabel#ReviewCandidate {
            background: rgba(255, 248, 230, 0.98);
            color: #112639;
            border: 1px solid rgba(249, 221, 132, 0.82);
            border-radius: 14px;
            padding: 12px 14px;
            font-size: 17px;
            font-weight: 700;
        }

        QFrame#HeaderPanel {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #f2f6ef, stop:1 #e6efe7
            );
            border: 1px solid #cfdacd;
            border-radius: 22px;
        }

        QFrame#ContentPanel {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #f8f4ea, stop:1 #eef3ea
            );
            border: 1px solid #d9dfcf;
            border-radius: 22px;
        }

        QFrame#MetricCard {
            border: 1px solid #d0dbd1;
            border-radius: 22px;
        }

        QFrame#MetricCard[tone="checked"] {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #e5f6f4, stop:1 #d9efe6
            );
        }

        QFrame#MetricCard[tone="hit"] {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #ecf8e3, stop:1 #dbf3d6
            );
        }

        QFrame#MetricCard[tone="error"] {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #fde9e6, stop:1 #f9ddd8
            );
        }

        QFrame#MetricCard[tone="rate"] {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #fff2d8, stop:1 #f7e5c2
            );
        }

        QLabel#PageTitle {
            font-size: 24px;
            font-weight: 700;
            color: #13253b;
        }

        QLabel#PageSubtitle, QLabel#ContentSubtitle, QLabel#MetricSubtitle {
            color: #425468;
            line-height: 1.35;
        }

        QLabel#ContentTitle, QLabel#MetricTitle {
            font-size: 15px;
            font-weight: 700;
            color: #1a2d42;
        }

        QLabel#MetricValue {
            font-size: 30px;
            font-weight: 700;
        }

        QLabel#StateBadge, QLabel#InfoBadge, QLabel#RequestBadge {
            border-radius: 14px;
            padding: 7px 12px;
            font-size: 12px;
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
            background: #dde7da;
            color: #233344;
            border: 1px solid #bfd0bf;
        }

        QLabel#RequestBadge[status="idle"] {
            background: #e7edf2;
            color: #3b4b5f;
            border: 1px solid #c8d2dc;
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
            min-height: 42px;
            border-radius: 14px;
            padding: 0 14px;
            font-size: 13px;
            font-weight: 700;
            border: none;
        }

        QPushButton[variant="success"] {
            background: #1d8f7a;
            color: white;
        }

        QPushButton[variant="success"]:hover {
            background: #167261;
        }

        QPushButton[variant="warning"] {
            background: #e4af3f;
            color: #41290d;
        }

        QPushButton[variant="warning"]:hover {
            background: #d49a28;
        }

        QPushButton[variant="danger"] {
            background: #b85243;
            color: white;
        }

        QPushButton[variant="danger"]:hover {
            background: #9d4337;
        }

        QPushButton[variant="neutral"] {
            background: #f3de9d;
            color: #3f2a13;
        }

        QPushButton[variant="neutral"]:hover {
            background: #e8cb78;
        }

        QPushButton:disabled {
            background: #d6ddd4;
            color: #90a29a;
        }

        QLineEdit, QListWidget, QTextEdit, QComboBox {
            background: #fbfcf7;
            color: #102033;
            border: 1px solid #b8c9bf;
            border-radius: 14px;
            padding: 10px 12px;
            selection-background-color: #bfdc9b;
        }

        QLineEdit:focus, QListWidget:focus, QTextEdit:focus, QComboBox:focus {
            border: 1px solid #6ca53c;
        }

        QComboBox::drop-down {
            border: none;
            width: 28px;
        }

        QFrame#Sidebar QLineEdit,
        QFrame#Sidebar QListWidget,
        QFrame#Sidebar QComboBox {
            background: rgba(255, 248, 230, 0.98);
            color: #112639;
            border: 1px solid rgba(249, 221, 132, 0.82);
            font-weight: 600;
        }

        QFrame#Sidebar QLineEdit:focus,
        QFrame#Sidebar QListWidget:focus,
        QFrame#Sidebar QComboBox:focus {
            border: 1px solid #f1b83f;
        }

        QListWidget::item {
            padding: 8px;
            border-radius: 10px;
        }

        QListWidget::item:selected {
            background: #f2d27a;
            color: #4a2f0e;
        }

        QCheckBox {
            color: #ffffff;
            font-weight: 700;
            spacing: 10px;
        }

        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 6px;
            border: 1px solid rgba(251, 224, 142, 0.55);
            background: rgba(255, 248, 223, 0.08);
        }

        QCheckBox::indicator:checked {
            background: #f2c14d;
            border: 1px solid #f2c14d;
        }

        QTextEdit {
            font-family: "Consolas", "Microsoft YaHei UI";
            line-height: 1.45;
        }

        QScrollBar:vertical {
            background: rgba(16, 37, 48, 0.08);
            width: 12px;
            border-radius: 6px;
            margin: 6px 0 6px 0;
        }

        QScrollBar::handle:vertical {
            background: rgba(242, 193, 77, 0.48);
            min-height: 28px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical:hover {
            background: rgba(242, 193, 77, 0.72);
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
            background: transparent;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: transparent;
        }
        """
