import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QDateEdit,
                             QFileDialog, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QDate
from window_for_rewrite import WindowForRewrite
from settings import SettingsWindow
from for_classes_test import Validator, Parser
from something_classes_and_funcs import Database, Settings


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.settings_window = None
        self.rewrite_window = None
        self.setWindowTitle("Main Menu")
        self.resize(550, 340)

        label = QLabel("Выберите режим:", self)

        grid = QGridLayout()
        grid.setSpacing(10)

        self.check_works_button = QPushButton("Проверка работ", self)
        self.rewrite_button = QPushButton("Перезапись данных", self)
        self.generation_button = QPushButton("Генерация", self)
        self.search_button = QPushButton("Поиск по работам", self)
        self.statistics_button = QPushButton("Статистика по работам", self)
        self.comparison_button = QPushButton("Сравнение работ", self)
        self.import_button = QPushButton("Импорт данных", self)
        self.export_button = QPushButton("Экспорт данных", self)
        self.bot_control_button = QPushButton("Управление телеграм-ботом", self)
        self.random_call_button = QPushButton("Случайный вызов", self)
        self.help_button = QPushButton("Помощь", self)
        self.close_button = QPushButton("Выход", self)
        self.settings_button = QPushButton("Настройки", self)

        self.close_button.clicked.connect(self.close)

        self.settings_button.setFixedSize(230, 30)
        self.check_works_button.setFixedSize(230, 60)
        self.rewrite_button.setFixedSize(230, 60)
        self.generation_button.setFixedSize(230, 60)
        self.search_button.setFixedSize(230, 60)
        self.statistics_button.setFixedSize(230, 60)
        self.comparison_button.setFixedSize(230, 60)
        self.import_button.setFixedSize(230, 60)
        self.export_button.setFixedSize(230, 60)
        self.bot_control_button.setFixedSize(230, 60)
        self.random_call_button.setFixedSize(230, 60)
        self.help_button.setFixedSize(230, 60)
        self.close_button.setFixedSize(230, 60)

        self.rewrite_button.clicked.connect(self.run_rewrite)
        self.settings_button.clicked.connect(self.run_settings)

        grid.addWidget(self.check_works_button, 1, 0)
        grid.addWidget(self.rewrite_button, 1, 1)
        grid.addWidget(self.generation_button, 1, 2)
        grid.addWidget(self.search_button, 2, 0)
        grid.addWidget(self.statistics_button, 2, 1)
        grid.addWidget(self.comparison_button, 2, 2)
        grid.addWidget(self.import_button, 3, 0)
        grid.addWidget(self.export_button, 3, 1)
        grid.addWidget(self.bot_control_button, 3, 2)
        grid.addWidget(self.random_call_button, 4, 0)
        grid.addWidget(self.help_button, 4, 1)
        grid.addWidget(self.close_button, 4, 2)
        grid.addWidget(self.settings_button, 0, 2)

        grid.addWidget(label, 0, 0)

        self.setLayout(grid)

        self.setStyleSheet("""           
            
            QWidget {
                background-color: #595e5b;
                color: white;
                font-size: 14px;
                border-radius: 15px;
                font-weight: bold;
                font-family: "Consolas";
            }
            
            QPushButton {
                border-radius: 10px;
                background-color: #303b3d;
            }
            
            QPushButton:hover {
                background-color: #557A95;
            }
            
            QPushButton:pressed {
                background-color: #303b3d;
            }
        """)

        self.settings_button.setStyleSheet("""
            QPushButton {
        background: transparent;
        border: none;
        color: white;
        font-size: 14px;
        }
        QPushButton:hover {
            text-decoration: underline;
        }
        QPushButton:pressed {
            color: #557A95;
        }
        """)

    def on_rewrite_finished(self):
        data = self.rewrite_window.result_data

        validator = Validator(data)
        ok, errors = validator.validate()

        if ok:
            print('Сработало условие')
            parser = Parser(validator.validate_answers_file(), validator.validate_grades_file(), validator.absents_file,
                validator.works_folder, validator.date, validator.class_name)
            class_name = parser.parse_class_name()
            date = parser.parse_date()
            answers_string = parser.parse_answers_dict()
            grades_string = parser.parse_grades_dict()
            work_name = parser.parse_works_folder()[0]
            dict_with_student_answers = parser.parse_works_folder()[1]
            students_list = parser.parse_works_folder()[2]
            print('Все отпарсили')
            db = Database()

            db.connect()
            work_id = db.save_work(work_name, date, class_name, answers_string, grades_string, 'raw')
            print(1)
            db.add_students_from_list(class_name, students_list)
            print(2)
            try:
                db.add_submissions_from_answers(class_name, work_id, dict_with_student_answers)
            except Exception as e:
                print(e)
            db.close()
            print(3)

            self.show()
            return

        self.handle_errors(errors)

    def handle_errors(self, errors):
        self.rewrite_window.hide()

        print("\nОбнаружены ошибки:\n")
        for err in errors:
            print(err)
        if Settings.take_data_from_previous_load:
            print('Корректные данные сохранены, потому что включена эта опция.')
        input("\nНажмите Enter, чтобы вернуться в меню...\n")

        self.show()


    def on_settings_finished(self):
        self.show()

    def run_rewrite(self):
        self.hide()
        self.rewrite_window = WindowForRewrite()
        self.rewrite_window.finished.connect(self.on_rewrite_finished)
        self.rewrite_window.show()

    def run_settings(self):
        self.hide()
        self.settings_window = SettingsWindow()
        self.settings_window.finished.connect(self.on_settings_finished)
        self.settings_window.show()





