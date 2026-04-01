import random
import sys
import time
from pathlib import Path

import pyqtgraph as pg
import requests
from PySide6.QtCore import QThread, QTimer, Signal
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

SRC_ROOT = Path(__file__).resolve().parent / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from gmail_ai_qt_app.services.providers import parse_legacy_http_response


stats = {"checked": 0, "hit": 0, "error": 0}
history_checked, history_hit, history_rate = [], [], []
names = ["james", "alex"]

running = False
paused = False


class Worker(QThread):
    log_signal = Signal(str, str)
    stat_signal = Signal(dict)

    def __init__(self, proxy_check, proxy_input):
        super().__init__()
        self.proxy_check = proxy_check
        self.proxy_input = proxy_input

    def run(self):
        global running, paused

        while True:
            if not running or paused:
                time.sleep(0.3)
                continue

            base = random.choice(names)
            suffix = "".join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(6 - len(base)))
            name = (base + suffix)[:6]

            try:
                proxies = None
                if self.proxy_check.isChecked():
                    proxy_url = self.proxy_input.text().strip()
                    if proxy_url:
                        proxies = {"http": proxy_url, "https": proxy_url}

                response = requests.get(
                    "https://accounts.google.com/_/signup/usernameavailability",
                    params={"username": name},
                    timeout=10,
                    proxies=proxies,
                )

                outcome = parse_legacy_http_response(
                    provider="google",
                    name=name,
                    status_code=response.status_code,
                    response_text=response.text,
                )

                stats["checked"] += outcome.checked_delta
                stats["hit"] += outcome.hit_delta
                stats["error"] += outcome.error_delta

                if outcome.message_key == "log_name_available":
                    self.log_signal.emit(f"✔ {name}@gmail.com", "hit")
                elif outcome.message_key == "log_name_taken":
                    self.log_signal.emit(f"• {name}", "taken")
                elif outcome.message_key == "log_provider_forbidden":
                    self.log_signal.emit(f"✖ {name} HTTP {response.status_code} forbidden", "error")
                else:
                    self.log_signal.emit(f"✖ {name} HTTP {response.status_code}", "error")

            except Exception as exc:
                stats["error"] += 1
                self.log_signal.emit(f"✖ {name} {exc}", "error")

            history_checked.append(stats["checked"])
            history_hit.append(stats["hit"])

            rate = (stats["hit"] / stats["checked"] * 100) if stats["checked"] else 0
            history_rate.append(rate)

            if len(history_checked) > 100:
                history_checked.pop(0)
                history_hit.pop(0)
                history_rate.pop(0)

            self.stat_signal.emit(stats.copy())
            time.sleep(0.5)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Legacy Scanner Demo")
        self.resize(1200, 760)

        splitter_root = QWidget()
        self.setCentralWidget(splitter_root)
        root = QHBoxLayout(splitter_root)

        left = QWidget()
        left_layout = QVBoxLayout(left)

        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")
        self.proxy_check = QCheckBox("Use Proxy")
        self.proxy_input = QLineEdit("http://127.0.0.1:7897")
        self.name_input = QLineEdit()
        self.add_btn = QPushButton("Add")
        self.name_list = QListWidget()
        self.name_list.addItems(names)

        left_layout.addWidget(self.start_btn)
        left_layout.addWidget(self.pause_btn)
        left_layout.addWidget(self.stop_btn)
        left_layout.addWidget(self.proxy_check)
        left_layout.addWidget(self.proxy_input)
        left_layout.addWidget(QLabel("Add Name"))
        left_layout.addWidget(self.name_input)
        left_layout.addWidget(self.add_btn)
        left_layout.addWidget(self.name_list)
        left_layout.addStretch()

        right = QWidget()
        right_layout = QVBoxLayout(right)
        cards = QHBoxLayout()
        self.checked = self.card("Checked")
        self.hit = self.card("Hit")
        self.error = self.card("Error")
        cards.addWidget(self.checked)
        cards.addWidget(self.hit)
        cards.addWidget(self.error)

        self.plot = pg.PlotWidget()
        self.curve1 = self.plot.plot(pen=pg.mkPen("#3b82f6", width=2))
        self.curve2 = self.plot.plot(pen=pg.mkPen("#22c55e", width=2))
        self.curve3 = self.plot.plot(pen=pg.mkPen("#ef4444", width=2))

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        right_layout.addLayout(cards)
        right_layout.addWidget(self.plot)
        right_layout.addWidget(self.log)

        root.addWidget(left)
        root.addWidget(right, 1)

        self.worker = Worker(self.proxy_check, self.proxy_input)
        self.worker.log_signal.connect(self.add_log)
        self.worker.stat_signal.connect(self.update_stats)
        self.worker.start()

        self.start_btn.clicked.connect(self.start)
        self.pause_btn.clicked.connect(self.pause)
        self.stop_btn.clicked.connect(self.stop)
        self.add_btn.clicked.connect(self.add_name)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chart)
        self.timer.start(300)

    def card(self, title):
        frame = QFrame()
        layout = QVBoxLayout(frame)
        value = QLabel("0")
        title_label = QLabel(title)
        layout.addWidget(value)
        layout.addWidget(title_label)
        frame.label = value
        return frame

    def update_stats(self, snapshot):
        self.checked.label.setText(str(snapshot["checked"]))
        self.hit.label.setText(str(snapshot["hit"]))
        self.error.label.setText(str(snapshot["error"]))

    def update_chart(self):
        self.curve1.setData(history_checked)
        self.curve2.setData(history_hit)
        self.curve3.setData(history_rate)

    def add_log(self, message, tag):
        colors = {"hit": "green", "error": "red", "taken": "gray"}
        self.log.append(f"<span style='color:{colors.get(tag, 'black')}'>{message}</span>")

    def add_name(self):
        new_name = self.name_input.text().strip()
        if new_name and new_name not in names:
            names.append(new_name)
            self.name_list.addItem(new_name)
            self.name_input.clear()

    def start(self):
        global running, paused
        running = True
        paused = False

    def pause(self):
        global paused
        paused = True

    def stop(self):
        global running
        running = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
