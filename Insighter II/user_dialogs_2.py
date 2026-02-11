from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class TelegramControlDialog(QDialog):
    def __init__(self, db_classes, bot_service, parent=None):
        super().__init__(parent)
        self.db_classes = db_classes
        self.bot_service = bot_service

        self.setWindowTitle("Управление телеграм-ботом")
        self.setMinimumWidth(520)

        layout = QVBoxLayout(self)

        self.send_text_button = QPushButton("Отправить текст/файлы классу")
        self.register_button = QPushButton("Регистрация учеников")
        self.send_results_button = QPushButton("Отправить результаты генерации")

        self.send_text_button.clicked.connect(self.open_send_text_dialog)
        self.register_button.clicked.connect(self.open_registration_dialog)
        self.send_results_button.clicked.connect(self.open_send_results_dialog)

        layout.addWidget(self.send_text_button)
        layout.addWidget(self.register_button)
        layout.addWidget(self.send_results_button)

    def open_send_text_dialog(self):
        dialog = SendToClassDialog(self.db_classes, self.bot_service, parent=self)
        dialog.exec()

    def open_registration_dialog(self):
        dialog = RegistrationDialog(self.db_classes, self.bot_service, parent=self)
        dialog.exec()

    def open_send_results_dialog(self):
        dialog = SendGenerationResultsDialog(self.db_classes, self.bot_service, parent=self)
        dialog.exec()


class SendToClassDialog(QDialog):
    def __init__(self, classes, bot_service, parent=None):
        super().__init__(parent)
        self.classes = classes
        self.bot_service = bot_service
        self.selected_files = []

        self.setWindowTitle("Отправить текст/файлы классу")
        self.setMinimumSize(700, 500)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Введите текст:"))
        self.text_edit = QTextEdit()
        self.text_edit.textChanged.connect(self.update_send_button_state)
        layout.addWidget(self.text_edit)

        files_layout = QHBoxLayout()
        self.choose_files_button = QPushButton("Выбрать файл(ы)")
        self.choose_files_button.clicked.connect(self.choose_files)
        files_layout.addWidget(self.choose_files_button)
        layout.addLayout(files_layout)

        self.files_list = QListWidget()
        layout.addWidget(self.files_list)

        class_layout = QHBoxLayout()
        class_layout.addWidget(QLabel("Выберите класс:"))
        self.class_combo = QComboBox()
        self.class_combo.addItem("-- выберите класс --")
        self.class_combo.addItems(self.classes)
        self.class_combo.currentIndexChanged.connect(self.update_send_button_state)
        class_layout.addWidget(self.class_combo)
        layout.addLayout(class_layout)

        self.send_button = QPushButton("Отправить")
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send_payload)
        layout.addWidget(self.send_button)

    def choose_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите файл(ы)")
        if not files:
            return

        for file_path in files:
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                self.files_list.addItem(file_path)
        self.update_send_button_state()

    def update_send_button_state(self):
        has_class = self.class_combo.currentIndex() > 0
        has_text = bool(self.text_edit.toPlainText().strip())
        has_files = bool(self.selected_files)
        self.send_button.setEnabled(has_class and (has_text or has_files))

    def send_payload(self):
        class_name = self.class_combo.currentText()
        text = self.text_edit.toPlainText().strip()

        sent_count = self.bot_service.send_to_class(
            class_name=class_name,
            text=text,
            file_paths=self.selected_files,
        )

        if sent_count == 0:
            QMessageBox.information(
                self,
                "Нет telegram_id",
                "У учеников выбранного класса не найдено telegram_id. Возврат в начальное меню.",
            )
            parent_dialog = self.parent()
            if parent_dialog:
                parent_dialog.close()
            self.close()
            return

        print(f"Данные отправлены {sent_count} ученикам класса {class_name}.")
        QMessageBox.information(self, "Успех", "Данные успешно отправлены.")
        self.close()


class RegistrationDialog(QDialog):
    def __init__(self, classes, bot_service, parent=None):
        super().__init__(parent)
        self.classes = classes
        self.bot_service = bot_service

        self.setWindowTitle("Регистрация учеников")
        self.setMinimumSize(520, 280)

        layout = QGridLayout(self)

        layout.addWidget(QLabel("Выберите класс:"), 0, 0)
        self.class_combo = QComboBox()
        self.class_combo.addItems(self.classes)
        layout.addWidget(self.class_combo, 0, 1)

        self.code_label = QLabel("")
        self.code_label.setStyleSheet("font-size: 36px; font-weight: bold;")
        layout.addWidget(self.code_label, 1, 0, 1, 2)

        self.refresh_code_button = QPushButton("Создать код")
        self.refresh_code_button.clicked.connect(self.activate_registration)
        layout.addWidget(self.refresh_code_button, 2, 1)

        self.finish_button = QPushButton("Завершить регистрацию")
        self.finish_button.clicked.connect(self.finish_registration)
        layout.addWidget(self.finish_button, 2, 0)

        self.class_combo.currentIndexChanged.connect(self.activate_registration)
        self.activate_registration()

    def activate_registration(self):
        class_name = self.class_combo.currentText()
        room_code = self.bot_service.enable_registration(class_name)
        self.code_label.setText(room_code)

    def finish_registration(self):
        self.bot_service.disable_registration()
        QMessageBox.information(self, "Готово", "Регистрация завершена.")


class SendGenerationResultsDialog(QDialog):
    def __init__(self, classes, bot_service, parent=None):
        super().__init__(parent)
        self.classes = classes
        self.bot_service = bot_service
        self.folder_path = ""

        self.setWindowTitle("Отправить результаты генерации")
        self.setMinimumSize(650, 260)

        layout = QVBoxLayout(self)

        class_row = QHBoxLayout()
        class_row.addWidget(QLabel("Выберите класс:"))
        self.class_combo = QComboBox()
        self.class_combo.addItems(self.classes)
        class_row.addWidget(self.class_combo)
        layout.addLayout(class_row)

        folder_row = QHBoxLayout()
        self.folder_label = QLabel("Папка не выбрана")
        self.choose_folder_button = QPushButton("Выбрать папку")
        self.choose_folder_button.clicked.connect(self.choose_folder)
        folder_row.addWidget(self.folder_label)
        folder_row.addWidget(self.choose_folder_button)
        layout.addLayout(folder_row)

        self.send_button = QPushButton("Отправить")
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send_results)
        layout.addWidget(self.send_button)

    def choose_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if not folder_path:
            return
        self.folder_path = folder_path
        self.folder_label.setText(folder_path)
        self.send_button.setEnabled(True)

    def send_results(self):
        class_name = self.class_combo.currentText()
        sent_count, sent_names, invalid_files = self.bot_service.send_generation_results(
            class_name=class_name,
            folder_path=self.folder_path,
        )

        if invalid_files:
            print("Следующие файлы были проигнорированы:")
            for file_name in invalid_files:
                print(file_name)

        if sent_count == 0:
            QMessageBox.information(
                self,
                "Нет подходящих файлов",
                "Ни один файл не подошел под условия или не найдено совпадений в базе.",
            )
            return

        print(f"Отправлено файлов: {sent_count}. Список: {', '.join(sent_names)}")
        QMessageBox.information(self, "Успех", "Результаты успешно отправлены.")
        self.close()
