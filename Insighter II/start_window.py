import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout,
    QProgressBar, QPushButton
)
from PyQt5.QtCore import Qt, QTimer



class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Insighter — первый запуск")
        self.resize(550, 300)

        self.setStyleSheet("""
            QWidget {
                background-color: #595e5b;
                color: white;
                font-size: 14px;
                border-radius: 15px;
                font-weight: bold;
                font-family: "Consolas";
            }

            QProgressBar {
                border: 2px solid #303b3d;
                border-radius: 10px;
                text-align: center;
                height: 20px;
                background-color: #303b3d;
            }

            QProgressBar::chunk {
                background-color: #557A95;
                border-radius: 10px;
            }

            QPushButton {
                background-color: #303b3d;
                border-radius: 10px;
                padding: 6px 14px;
            }

            QPushButton:hover {
                background-color: #557A95;
            }
            
            QPushButton:pressed {
                background-color: #303b3d;
            }
        """)

        text = (
            "Добро пожаловать в Insighter!\n\n"
            "Так как это первый запуск(либо програмные файлы были повреждены и программа пересоздает все заново), "
            "программа создаёт\n"
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
        self.ok_button.setFixedSize(170, 35)
        self.ok_button.clicked.connect(self.close)
        self.ok_button.setVisible(False)

        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addSpacing(10)
        layout.addWidget(self.progress)
        layout.addSpacing(10)
        layout.addWidget(self.ok_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(20)

    def update_progress(self):
        value = self.progress.value()

        if value < 100:
            self.progress.setValue(value + 1)
        else:
            self.timer.stop()
            self.ok_button.setVisible(True)



