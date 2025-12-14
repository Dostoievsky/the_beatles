import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QDateEdit,
                             QFileDialog, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QDate

COLORS = {
    # Фоны
    "bg_main": "#1e1e1e",
    "bg_block": "#2b2b2b",
    "bg_button": "#2d2d2d",
    "bg_hover": "#3a3a3a",
    "bg_pressed": "#1f1f1f",

    # Инпуты
    "bg_input": "#262626",
    "bg_input_focus": "#2f2f2f",

    # Границы
    "border_main": "#3a3a3a",
    "border_button": "#555555",
    "border_input": "#444444",

    # Текст
    "text_main": "#dddddd",
    "text_label": "#e4e4e4",
    "text_placeholder": "#888888",
    "text_on_accent": "#1e1e1e",

    # Акцент
    "accent_soft": "#d18904",  # горчичный, как ты и хотел
}



class WindowForRewrite(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Ввод данных')
        self.resize(700, 330)


        self.label = QLabel('Введите необходимые данные')


        self.class_name_line = QLineEdit()
        self.class_name_line.setMinimumHeight(32)
        self.class_name_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

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

        self.answer_label = QLabel('Выберите файл с ответами')


        self.button_open_grades_file = QPushButton('Добавить файл')
        self.button_open_grades_file.setFixedSize(200, 32)
        self.button_open_grades_file.clicked.connect(self.choose_file_grades)

        self.grade_choose_line = QLineEdit()
        self.grade_choose_line.setMinimumHeight(32)
        self.grade_choose_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.grade_label = QLabel('Выберите файл с критерями')


        self.button_open_works_folder = QPushButton('Добавить папку')
        self.button_open_works_folder.setFixedSize(200, 32)
        self.button_open_works_folder.clicked.connect(self.choose_folder_works_folder)

        self.works_folder_line = QLineEdit()
        self.works_folder_line.setMinimumHeight(32)
        self.works_folder_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.works_folder_label = QLabel('Выберите папку с работами')


        self.button_open_absents_file = QPushButton('Добавить файл')
        self.button_open_absents_file.setFixedSize(200, 32)
        self.button_open_absents_file.clicked.connect(self.choose_file_absents)

        self.absents_choose_line = QLineEdit()
        self.absents_choose_line.setMinimumHeight(32)
        self.absents_choose_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
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


    def choose_file_answers(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'All files (*.*)')
        if file:
            self.answer_choose_line.setText(file)

    def choose_file_absents(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'All files (*.*)')
        if file:
            self.absents_choose_line.setText(file)

    def choose_file_grades(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'All files (*.*)')
        if file:
            self.grade_choose_line.setText(file)

    def choose_folder_works_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Выберите папку', '')
        if folder:
            self.works_folder_line.setText(folder)

    def get_data(self):
        data = {
            'class_name': self.class_name_line.text(),
            'answers_file': self.answer_choose_line.text(),
            'grades_file': self.grade_choose_line.text(),
            'works_folder': self.works_folder_line.text(),
            'absents_file': self.absents_choose_line.text(),
            'date': self.date_edit.date().toString('dd.MM.yyyy')
        }

        self.close()
        print(data)

app = QApplication(sys.argv)
window = WindowForRewrite()
window.show()
sys.exit(app.exec())