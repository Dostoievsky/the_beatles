import asyncio
import random
from pathlib import Path
from aiogram import Bot
from aiogram.types import FSInputFile
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QWidget, QMessageBox, QFileDialog, QHBoxLayout,
    QStackedLayout, QTextEdit, QListWidget, QComboBox
)
from PyQt5.QtCore import Qt
from database_and_settings_classes import Settings, Database, DatabaseChecking




class TelegramControlDialog(QDialog):
    def __init__(self, db: Database, bot_token: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Telegram-бот: управление")
        self.setMinimumSize(500, 300)

        self.db = db
        self.bot_token = bot_token
        if self.db.conn is None:
            self.db.connect()
        self.db_check = DatabaseChecking(self.db)

        layout = QVBoxLayout(self)

        title = QLabel("Выберите режим")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        self.btn_send = QPushButton("Отправить сообщение/файл")
        self.btn_students = QPushButton("Управление учениками")

        self.btn_send.setFixedHeight(40)
        self.btn_students.setFixedHeight(40)

        layout.addWidget(self.btn_send)
        layout.addWidget(self.btn_students)

        self.btn_send.clicked.connect(self._open_send_dialog)
        self.btn_students.clicked.connect(self._open_students_dialog)

    def _open_send_dialog(self):
        dialog = TelegramSendMessageDialog(self.db, self.bot_token, parent=self)
        dialog.exec()

    def _open_students_dialog(self):
        classes = self.db_check.get_classes()
        if not classes:
            QMessageBox.information(
                self,
                "Нет классов",
                "В базе данных нет классов. Сначала добавьте класс."
            )
            return

        dialog = TelegramStudentsMenuDialog(self.db, parent=self)
        dialog.exec()


class TelegramSendMessageDialog(QDialog):
    def __init__(self, db: Database, bot_token: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Отправка сообщения")
        self.setMinimumSize(600, 400)

        self.db = db
        self.bot_token = bot_token
        if self.db.conn is None:
            self.db.connect()
        self.db_check = DatabaseChecking(self.db)

        self.selected_files = []

        layout = QVBoxLayout(self)

        label = QLabel("Текст сообщения:")
        layout.addWidget(label)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Введите текст сообщения...")
        layout.addWidget(self.text_edit)

        files_label = QLabel("Файлы:")
        layout.addWidget(files_label)

        self.files_list = QListWidget()
        layout.addWidget(self.files_list)

        btn_add_files = QPushButton("Добавить файлы")
        btn_add_files.clicked.connect(self._add_files)
        layout.addWidget(btn_add_files)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_next = QPushButton("Далее")
        btn_next.setFixedWidth(120)
        btn_next.clicked.connect(self._open_select_class)
        btn_layout.addWidget(btn_next)

        layout.addLayout(btn_layout)

    def _add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Выберите файлы",
            "",
            "Все файлы (*.*)"
        )
        if files:
            self.selected_files.extend(files)
            self.files_list.clear()
            self.files_list.addItems(self.selected_files)

    def _open_select_class(self):
        dialog = TelegramSelectClassDialog(
            self.db,
            self.bot_token,
            self.text_edit.toPlainText(),
            self.selected_files,
            parent=self
        )
        if dialog.exec() == QDialog.Accepted:
            self.accept()


class TelegramSelectClassDialog(QDialog):
    def __init__(self, db: Database, bot_token: str, message_text: str, files: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор класса")
        self.setMinimumSize(400, 200)

        self.db = db
        self.bot_token = bot_token
        self.message_text = message_text
        self.files = files

        if self.db.conn is None:
            self.db.connect()
        self.db_check = DatabaseChecking(self.db)

        classes = self.db_check.get_classes()
        if not classes:
            QMessageBox.information(
                self,
                "Нет классов",
                "В базе данных нет классов. Сначала добавьте класс."
            )
            self.reject()
            return

        layout = QVBoxLayout(self)

        label = QLabel("Выберите класс:")
        layout.addWidget(label)

        self.class_combo = QComboBox()
        self.class_combo.addItems(classes)
        layout.addWidget(self.class_combo)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_send = QPushButton("Отправить")
        btn_send.setFixedWidth(120)
        btn_send.clicked.connect(self._send_to_class)
        btn_layout.addWidget(btn_send)

        layout.addLayout(btn_layout)

    def _send_to_class(self):
        class_name = self.class_combo.currentText()
        students = self.db.get_students_with_telegram_ids(class_name)
        tg_ids = [row[1] for row in students if row[1]]

        if not tg_ids:
            print("Ошибка: у учеников выбранного класса нет Telegram ID.")
            self.reject()
            return

        async def _send():
            bot = Bot(token=self.bot_token)
            try:
                for tg_id in tg_ids:
                    if self.message_text:
                        await bot.send_message(tg_id, self.message_text)
                    for file_path in self.files:
                        await bot.send_document(tg_id, FSInputFile(file_path))
            finally:
                await bot.session.close()

        asyncio.run(_send())
        self.accept()


class TelegramStudentsMenuDialog(QDialog):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление учениками")
        self.setMinimumSize(500, 300)

        self.db = db
        if self.db.conn is None:
            self.db.connect()

        layout = QVBoxLayout(self)

        label = QLabel("Выберите действие:")
        label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(label)

        btn_remove = QPushButton("Удалить ученика")
        btn_add = QPushButton("Добавить ученика")

        btn_remove.setFixedHeight(40)
        btn_add.setFixedHeight(40)

        layout.addWidget(btn_remove)
        layout.addWidget(btn_add)

        btn_remove.clicked.connect(self._open_remove_dialog)
        btn_add.clicked.connect(self._open_add_dialog)

    def _open_remove_dialog(self):
        dialog = TelegramRemoveStudentDialog(self.db, parent=self)
        dialog.exec()

    def _open_add_dialog(self):
        dialog = TelegramAddStudentDialog(self.db, parent=self)
        dialog.exec()


class TelegramRemoveStudentDialog(QDialog):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Удаление ученика")
        self.setMinimumSize(500, 250)

        self.db = db
        if self.db.conn is None:
            self.db.connect()
        self.db_check = DatabaseChecking(self.db)

        layout = QVBoxLayout(self)

        self.class_combo = QComboBox()
        classes = self.db_check.get_classes() or []
        if not classes:
            QMessageBox.information(
                self,
                "Нет классов",
                "В базе данных нет классов. Сначала добавьте класс."
            )
            self.reject()
            return

        self.class_combo.addItems(classes)
        self.class_combo.currentTextChanged.connect(self._load_students)

        layout.addWidget(QLabel("Класс:"))
        layout.addWidget(self.class_combo)

        self.student_combo = QComboBox()
        layout.addWidget(QLabel("Ученик:"))
        layout.addWidget(self.student_combo)

        self._load_students(self.class_combo.currentText())

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_delete = QPushButton("Удалить")
        btn_delete.setFixedWidth(120)
        btn_delete.clicked.connect(self.accept)
        btn_layout.addWidget(btn_delete)

        layout.addLayout(btn_layout)

    def _load_students(self, class_name: str):
        self.student_combo.clear()
        students = self.db.get_students_of_class(class_name, flag='names') or []
        self.student_combo.addItems(sorted(students))


class TelegramAddStudentDialog(QDialog):
    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Добавление ученика")
        self.setMinimumSize(500, 300)

        self.db = db
        if self.db.conn is None:
            self.db.connect()
        self.db_check = DatabaseChecking(self.db)

        classes = self.db_check.get_classes()
        if not classes:
            QMessageBox.information(
                self,
                "Нет классов",
                "В базе данных нет классов. Сначала добавьте класс."
            )
            self.reject()
            return

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Выберите класс:"))
        self.class_combo = QComboBox()
        self.class_combo.addItems(classes)
        layout.addWidget(self.class_combo)

        self.code = str(random.randint(10000, 99999))

        code_label = QLabel(self.code)
        code_label.setAlignment(Qt.AlignCenter)
        code_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(QLabel("Код для регистрации ученика:"))
        layout.addWidget(code_label)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_finish = QPushButton("Завершить регистрацию")
        btn_finish.setFixedWidth(200)
        btn_finish.clicked.connect(self.accept)
        btn_layout.addWidget(btn_finish)

        layout.addLayout(btn_layout)
