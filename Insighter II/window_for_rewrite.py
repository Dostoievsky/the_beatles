import os
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QDateEdit,
                             QFileDialog, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtCore import pyqtSignal
import json


def load_sys_json():
    if not os.path.exists(r'system_files/sys.json'):
        return {}

    try:
        with open(r'system_files/sys.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


class WindowForRewrite(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.result_data = {}
        self.setWindowTitle('Ввод данных')
        self.resize(700, 330)


        self.label = QLabel('Введите необходимые данные')


        self.class_name_line = QLineEdit()
        self.class_name_line.setMinimumHeight(32)
        self.class_name_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        sys_data_for_lines = load_sys_json()

        self.class_name_label = QLabel('Напишите название класса')

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setFixedSize(300, 32)

        self.button_open_answer_file = QPushButton('Добавить файл')
        self.button_open_answer_file.setFixedSize(200, 32)
        self.button_open_answer_file.clicked.connect(self.choose_file_answers)

        self.answer_choose_line = QLineEdit()
        self.answer_choose_line.setMinimumHeight(32)
        self.answer_choose_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.answer_choose_line.setDisabled(True)

        self.answer_label = QLabel('Выберите файл с ответами')


        self.button_open_grades_file = QPushButton('Добавить файл')
        self.button_open_grades_file.setFixedSize(200, 32)
        self.button_open_grades_file.clicked.connect(self.choose_file_grades)

        self.grade_choose_line = QLineEdit()
        self.grade_choose_line.setMinimumHeight(32)
        self.grade_choose_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.grade_choose_line.setDisabled(True)

        self.grade_label = QLabel('Выберите файл с критерями')


        self.button_open_works_folder = QPushButton('Добавить папку')
        self.button_open_works_folder.setFixedSize(200, 32)
        self.button_open_works_folder.clicked.connect(self.choose_folder_works_folder)

        self.works_folder_line = QLineEdit()
        self.works_folder_line.setMinimumHeight(32)
        self.works_folder_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.works_folder_line.setDisabled(True)
        self.works_folder_label = QLabel('Выберите папку с работами')


        self.button_open_absents_file = QPushButton('Добавить файл')
        self.button_open_absents_file.setFixedSize(200, 32)
        self.button_open_absents_file.clicked.connect(self.choose_file_absents)

        self.absents_choose_line = QLineEdit()
        self.absents_choose_line.setMinimumHeight(32)
        self.absents_choose_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.absents_choose_line.setDisabled(True)

        self.class_name_line.setPlaceholderText(sys_data_for_lines.get('class_name', ''))
        self.answer_choose_line.setPlaceholderText(sys_data_for_lines.get('answers_file', ''))
        self.grade_choose_line.setPlaceholderText(sys_data_for_lines.get('grades_file', ''))
        self.works_folder_line.setPlaceholderText(sys_data_for_lines.get('works_folder', ''))
        self.absents_choose_line.setPlaceholderText('auto')
        self.absents_label = QLabel('Выберите файл с отсутствующими')


        self.submit_button = QPushButton('Подтвердить')
        self.submit_button.setFixedSize(200, 32)
        self.submit_button.clicked.connect(self.get_data)


        grid = QGridLayout()
        grid.setSpacing(10)

        self.label.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.label, 0, 0, 1, 3)

        grid.addWidget(self.class_name_label, 1, 0)
        grid.addWidget(self.class_name_line, 1, 1)

        grid.addWidget(self.button_open_answer_file, 2, 2)
        grid.addWidget(self.answer_label, 2, 0)
        grid.addWidget(self.answer_choose_line, 2, 1)

        grid.addWidget(self.button_open_grades_file, 3, 2)
        grid.addWidget(self.grade_label, 3, 0)
        grid.addWidget(self.grade_choose_line, 3, 1)

        grid.addWidget(self.button_open_works_folder, 4, 2)
        grid.addWidget(self.works_folder_label, 4, 0)
        grid.addWidget(self.works_folder_line, 4, 1)

        grid.addWidget(self.button_open_absents_file, 5, 2)
        grid.addWidget(self.absents_label, 5, 0)
        grid.addWidget(self.absents_choose_line, 5, 1)

        grid.addWidget(self.date_edit, 6, 1)

        grid.setColumnStretch(0, 0)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 0)

        grid.addWidget(self.submit_button, 6, 2)

        self.setLayout(grid)

        self.setStyleSheet("""           
                    QWidget {
                        background-color: #595e5b;
                        color: white;
                        font-size: 14px;
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
                    
                    QLineEdit {
                        background-color: #262626;
                        border: 1px solid #444444;
                        border-radius: 3px;
                    }
                """)


    def choose_file_answers(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'txt files (*.txt)')
        if file:
            self.answer_choose_line.setText(file)

    def choose_file_absents(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'txt files (*.txt)')
        if file:
            self.absents_choose_line.setText(file)

    def choose_file_grades(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'txt files (*.txt)')
        if file:
            self.grade_choose_line.setText(file)

    def choose_folder_works_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Выберите папку', '')
        if folder:
            self.works_folder_line.setText(folder)

    def get_data(self):
        self.result_data = {
            'class_name': self.class_name_line.text(),
            'answers_file': self.answer_choose_line.text(),
            'grades_file': self.grade_choose_line.text(),
            'works_folder': self.works_folder_line.text(),
            'absents_file': self.absents_choose_line.text(),
            'date': self.date_edit.date().toString('dd.MM.yyyy')
        }
        try:
            self.finished.emit()
        except Exception as e:
            print(e)
        self.close()








