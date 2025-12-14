import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QProgressBar, QPushButton
)
from PyQt5.QtCore import Qt, QTimer


COLORS = {
    "bg_main": "#1e1e1e",
    "bg_block": "#2b2b2b",
    "bg_button": "#2d2d2d",
    "bg_hover": "#3a3a3a",
    "bg_pressed": "#1f1f1f",

    "border_main": "#3a3a3a",
    "border_button": "#555555",

    "text_main": "#dddddd",
    "text_label": "#e4e4e4",

    "accent": "#f0c75e",
    "accent_soft": "#d18904",
}

class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insighter — первый запуск")
        self.resize(500, 260)

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['bg_main']};
                color: {COLORS['text_main']};
                font-size: 14px;
                border-radius: 15px;
            }}

            QLabel {{
                font-size: 15px;
                color: {COLORS['text_label']};
            }}

            QProgressBar {{
                border: 2px solid {COLORS['border_main']};
                border-radius: 10px;
                text-align: center;
                height: 20px;
                background-color: {COLORS['bg_block']};
            }}

            QProgressBar::chunk {{
                background-color: {COLORS['accent_soft']};
                border-radius: 10px;
            }}

            QPushButton {{
                background-color: {COLORS['bg_button']};
                border: 1px solid {COLORS['border_button']};
                border-radius: 10px;
                padding: 6px 14px;
                color: {COLORS['text_main']};
                font-size: 14px;
            }}

            QPushButton:hover {{
                background-color: {COLORS['bg_hover']};
            }}

            QPushButton:pressed {{
                background-color: {COLORS['accent_soft']};
            }}
        """)

        text = (
            "Добро пожаловать в Insighter!\n\n"
            "Так как это первый запуск, программа создаёт\n"
            "все необходимые файлы, папки и базу данных.\n"
            "Пожалуйста, подождите пару секунд.\n\n"
            "После этого прочитайте инструкцию — и можно начинать!"
        )

        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)

        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(100)

        self.ok_button = QPushButton("Продолжить")
        self.ok_button.clicked.connect(self.close)
        self.ok_button.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addSpacing(15)
        layout.addWidget(self.progress)
        layout.addSpacing(10)
        layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(100)

    def update_progress(self):
        value = self.progress.value()

        if value < 100:
            self.progress.setValue(value + 1)
        else:
            self.timer.stop()
            self.ok_button.setVisible(True)



app = QApplication(sys.argv)
window = WelcomeWindow()
window.show()
sys.exit(app.exec_())