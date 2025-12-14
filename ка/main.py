import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout,
    QLabel, QLineEdit, QPushButton
)

SETTINGS_FILE = "settings.json"


def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(data):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = load_settings()

        layout = QGridLayout()

        # ----- Поля ввода -----
        self.date_input = QLineEdit()
        self.topic_input = QLineEdit()

        # ----- Последние значения -----
        self.prev_date = QLabel(self.settings.get("date", "(нет данных)"))
        self.prev_topic = QLabel(self.settings.get("topic", "(нет данных)"))

        # ----- Размещение в сетке -----
        layout.addWidget(QLabel("Дата:"), 0, 0)
        layout.addWidget(self.date_input, 0, 1)
        layout.addWidget(QLabel("Предыдущее:"), 0, 2)
        layout.addWidget(self.prev_date, 0, 3)

        layout.addWidget(QLabel("Тема:"), 1, 0)
        layout.addWidget(self.topic_input, 1, 1)
        layout.addWidget(QLabel("Предыдущее:"), 1, 2)
        layout.addWidget(self.prev_topic, 1, 3)

        # Кнопка
        self.btn = QPushButton("Отправить")
        self.btn.clicked.connect(self.on_submit)
        layout.addWidget(self.btn, 2, 1)

        self.setLayout(layout)

    def on_submit(self):
        # если поле пустое → берём предыдущее
        date = self.date_input.text() or self.settings.get("date", "")
        topic = self.topic_input.text() or self.settings.get("topic", "")

        # сохраняем
        self.settings["date"] = date
        self.settings["topic"] = topic
        save_settings(self.settings)

        print("\n=== Значения, с которыми запускаем ===")
        print("Дата:", date)
        print("Тема:", topic)
        print("======================================\n")

        self.close()  # закрываем окно


app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())
