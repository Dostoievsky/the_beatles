from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup,
    QScrollArea, QWidget, QSizePolicy, QMessageBox, QCheckBox, QLineEdit, QFileDialog, QSpinBox, QHBoxLayout,
    QVBoxLayout, QInputDialog, QStackedLayout
)
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import Qt
from database_and_settings_classes import Settings
import random
from clearmodes import *
from pathlib import Path

class FirstRunTelegramSetupDialog(QDialog):
    def __init__(self, auth_code: str, parent=None):
        super().__init__(parent)

        self.auth_code = auth_code

        self.setWindowTitle("Первичная настройка Telegram-бота")
        self.setMinimumSize(500, 300)

        self.layout = QVBoxLayout(self)

        self.stack = QStackedLayout()
        self.layout.addLayout(self.stack)

        self._build_step_instruction()
        self._build_step_code()

        self.stack.setCurrentIndex(0)


    def _build_step_instruction(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Первый запуск режима Telegram")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        instruction = QLabel(
            "Это первый запуск Telegram-режима.\n\n"
            "Чтобы назначить учителя (администратора системы), выполните следующие шаги:\n\n"
            "1. Откройте Telegram-бота\n"
            "2. Нажмите кнопку «Запустить»\n"
            "3. Введите код, который будет показан на следующем шаге\n\n"
            "После этого программа автоматически продолжит работу."
        )
        instruction.setWordWrap(True)
        instruction.setAlignment(Qt.AlignTop)
        layout.addWidget(instruction)

        layout.addStretch()

        btn = QPushButton("Далее")
        btn.setFixedHeight(32)
        btn.clicked.connect(self._go_to_code)
        layout.addWidget(btn, alignment=Qt.AlignRight)

        self.stack.addWidget(page)


    def _build_step_code(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("Код идентификации учителя")
        title.setStyleSheet("font-size: 16px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        code_label = QLabel(self.auth_code)
        code_label.setAlignment(Qt.AlignCenter)
        code_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            letter-spacing: 3px;
        """)
        layout.addWidget(code_label)

        hint = QLabel(
            "Введите этот код в Telegram-боте.\n"
            "Окно можно не закрывать — система ожидает подтверждение."
        )
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        layout.addWidget(hint)

        layout.addStretch()

        self.stack.addWidget(page)


    def _go_to_code(self):
        self.stack.setCurrentIndex(1)
