from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup,
    QScrollArea, QWidget, QSizePolicy, QMessageBox, QCheckBox, QLineEdit, QFileDialog, QSpinBox, QHBoxLayout,
    QVBoxLayout
)
from PyQt5.QtCore import Qt, QRegularExpression
from PyQt5.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import Qt
from database_and_settings_classes import Settings
import random
from clearmodes import *
from pathlib import Path

class CheckWorksDialog(QDialog):
    def __init__(self, cdb, parent=None):
        super().__init__(parent)

        self.cdb = cdb
        self.step = 0
        self.data = {}
        self.group = None

        self.setWindowTitle("Проверка работ")
        self.setStyleSheet('''
                    QRadioButton {
                    spacing: 8px;
                    color: #ffffff;
                    font-weight: bold;
                }
                
                QRadioButton::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 9px;          /* круг */
                    border: 2px solid #444444;
                    background-color: #303b3d;
                }
                
                QRadioButton::indicator:hover {
                    border: 2px solid #557A95;
                }
                
                QRadioButton::indicator:checked {
                    background-color: #557A95;
                    border: 2px solid #557A95;
                }
                
                QRadioButton::indicator:checked:hover {
                    background-color: #6fa3c6;
                }
                
                QRadioButton:disabled {
                    color: #888888;
                }
                
                QRadioButton::indicator:disabled {
                    background-color: #222222;
                    border: 2px solid #333333;
                }
        ''')

        self.setMinimumWidth(520)
        self.setMinimumHeight(300)
        self.outer_layout = QVBoxLayout(self)
        self.outer_layout.setContentsMargins(17, 17, 17, 17)
        self.outer_layout.setSpacing(20)

        self.settings = Settings()
        self.need_format_step = self.settings.format_by_default in ('ask', 'спрашивать каждый раз')
        self.need_open_step = not self.settings.automatically_file_opening

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setMaximumHeight(500)

        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setSpacing(6)
        self.layout.setAlignment(Qt.AlignTop)

        self.scroll.setWidget(self.container)
        self.outer_layout.addWidget(self.scroll)

        self.next_button = QPushButton("Далее")
        self.next_button.setFixedHeight(32)
        self.next_button.setMinimumWidth(200)
        self.next_button.clicked.connect(self.on_next)

        self.outer_layout.addWidget(self.next_button, alignment=Qt.AlignCenter)

        self.show_step()


    def clear(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()


    def step_choose_class(self):
        self.layout.addWidget(QLabel("Выберите класс:"))

        classes = self.cdb.get_classes()
        if not classes:
            self.layout.addWidget(QLabel("У вас нет добавленных классов. Испоользуйте режим перезапси для добавления данных."))
            self.reject()
            return

        self.group = QButtonGroup(self)

        for cls in classes:
            rb = QRadioButton(cls)
            self.group.addButton(rb)
            self.layout.addWidget(rb)

    def step_choose_work(self):
        self.layout.addWidget(QLabel("Выберите работу:"))

        works = self.cdb.get_works_by_class(self.data["class"])
        parsed = self.cdb.parse_names(works)

        if not parsed:
            self.reject()
            print("У вас нет непроверенных работ.")
            return

        self.group = QButtonGroup(self)

        for work in parsed:
            rb = QRadioButton(work)
            self.group.addButton(rb)
            self.layout.addWidget(rb)

    def step_choose_sort(self):
        self.layout.addWidget(QLabel("Выберите режим сортировки:"))

        self.group = QButtonGroup(self)

        modes = [
            'По умолчанию',
            'По оценкам, сначала лучшие',
            'По оценкам, сначала худшие',
            'По фамилиям'
        ]

        for mode in modes:
            rb = QRadioButton(mode)
            self.group.addButton(rb)
            self.layout.addWidget(rb)

        self.next_button.setText("Готово")

    def show_step(self):
        self.clear()

        if self.step == 0:
            self.step_choose_class()
        elif self.step == 1:
            self.step_choose_work()
        elif self.step == 2:
            self.step_choose_sort()
        elif self.step == 3:
            self.step_choose_format()
        elif self.step == 4:
            self.step_choose_open()

        self.container.adjustSize()
        self.adjustSize()

    def on_next(self):
        checked = self.group.checkedButton()
        if not checked:
            return

        value = checked.text()

        if self.step == 0:
            self.data["class"] = value

        elif self.step == 1:
            self.data["work"] = value

        elif self.step == 2:
            self.data["sort_mode"] = value

            if self.need_format_step:
                self.step += 1
                self.show_step()
                return
            else:
                self.data["format"] = self.settings.format_by_default

                if self.need_open_step:
                    self.step = 4
                    self.show_step()
                    return
                else:
                    self.data["open_file"] = self.settings.automatically_file_opening
                    self.accept()
                    return

        elif self.step == 3:
            self.data["format"] = value

            if self.need_open_step:
                self.step += 1
                self.show_step()
                return
            else:
                self.data["open_file"] = self.settings.automatically_file_opening
                self.accept()
                return

        elif self.step == 4:
            self.data["open_file"] = (value == "Да")
            self.accept()
            return

        self.step += 1
        self.show_step()


    def step_choose_format(self):
        self.layout.addWidget(QLabel("Выберите формат файла:"))

        self.group = QButtonGroup(self)

        for fmt in ('.txt', '.csv'):
            rb = QRadioButton(fmt)
            self.group.addButton(rb)
            self.layout.addWidget(rb)

    def step_choose_open(self):
        self.layout.addWidget(QLabel("Открыть файл после сохранения?"))

        self.group = QButtonGroup(self)

        yes = QRadioButton("Да")
        no = QRadioButton("Нет")

        self.group.addButton(yes)
        self.group.addButton(no)

        self.layout.addWidget(yes)
        self.layout.addWidget(no)



class ClearDatabaseDialog(QDialog):

    RESET_MODE = "Сброс до начальной конфигурации"

    def __init__(self, db, cdb, parent=None):
        super().__init__(parent)

        self.timer_label = None
        self.db = db
        self.cdb = cdb

        self.step = 0
        self.data = {}

        self.group = None
        self.confirm_checkbox = None

        self.timer = None
        self.time_left = 10

        self.setWindowTitle("Очистка базы данных")
        self.setMinimumSize(500, 270)

        self.setStyleSheet('''
            QRadioButton {
                spacing: 8px;
                color: #ffffff;
                font-weight: bold;
            }

            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #444444;
                background-color: #303b3d;
            }

            QRadioButton::indicator:hover {
                border: 2px solid #557A95;
            }

            QRadioButton::indicator:checked {
                background-color: #557A95;
                border: 2px solid #557A95;
            }

            QRadioButton::indicator:checked:hover {
                background-color: #6fa3c6;
            }

            QRadioButton:disabled {
                color: #888888;
            }

            QRadioButton::indicator:disabled {
                background-color: #222222;
                border: 2px solid #333333;
            }
            
            
                    QLabel {
                color: #ffffff;
                font-size: 15px;
            }
        
            QCheckBox {
                color: #ffffff;
                font-size: 13px;
            }
        
            QPushButton {
                color: #ffffff;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
        
            
                    QMessageBox {
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 13px;
            }
        
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 13px;
            }
        
            QRadioButton {
                spacing: 8px;
                color: #ffffff;
                font-weight: bold;
            }

            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #444444;
                background-color: #303b3d;
            }

            QRadioButton::indicator:hover {
                border: 2px solid #557A95;
            }

            QRadioButton::indicator:checked {
                background-color: #557A95;
                border: 2px solid #557A95;
            }

            QRadioButton::indicator:checked:hover {
                background-color: #6fa3c6;
            }

            QRadioButton:disabled {
                color: #888888;
            }

            QRadioButton::indicator:disabled {
                background-color: #222222;
                border: 2px solid #333333;
            }
            
            
                    QLabel {
                color: #ffffff;
                font-size: 15px;
            }
        
            QCheckBox {
                color: #ffffff;
                font-size: 13px;
            }
        
            QPushButton {
                color: #ffffff;
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: bold;
            }
        
            
                    QMessageBox {
                background-color: #1e1e1e;
                color: #ffffff;
                font-size: 13px;
            }
        
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 13px;
            }
        
            
        ''')

        self.main_layout = QVBoxLayout(self)
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        self.next_button = QPushButton("Далее")
        self.next_button.setFixedHeight(32)
        self.next_button.clicked.connect(self.on_next)

        self.main_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        self.show_step()


    def clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def rebuild(self):
        self.adjustSize()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)


    def step_choose_mode(self):
        self.group = QButtonGroup(self)

        label = QLabel(
            "Выберите режим очистки.\n"
            "Удалённые данные не могут быть восстановлены."
        )
        label.setWordWrap(True)
        self.content_layout.addWidget(label)

        for m in [
            "Очистка данных таблиц",
            "Очистить все данные в базе",
            self.RESET_MODE
        ]:
            rb = QRadioButton(m)
            self.group.addButton(rb)
            self.content_layout.addWidget(rb)

    def step_choose_table(self):
        self.group = QButtonGroup(self)
        self.content_layout.addWidget(QLabel("Выберите таблицу:"))

        for table in Clear(self.db).ALLOWED_TABLES:
            rb = QRadioButton(table)
            self.group.addButton(rb)
            self.content_layout.addWidget(rb)

    def step_choose_scope(self):
        self.group = QButtonGroup(self)
        self.content_layout.addWidget(QLabel("Как очистить таблицу?"))

        for opt in [
            "Очистить все данные в таблице",
            "Очистить конкретные данные"
        ]:
            rb = QRadioButton(opt)
            self.group.addButton(rb)
            self.content_layout.addWidget(rb)

    def step_choose_class(self):
        classes = self.cdb.get_classes()
        if not classes:
            QMessageBox.information(self, "Очистка", "Классов нет.")
            self.reject()
            return

        self.group = QButtonGroup(self)
        self.content_layout.addWidget(QLabel("Выберите класс:"))

        for cls in classes:
            rb = QRadioButton(cls)
            self.group.addButton(rb)
            self.content_layout.addWidget(rb)

    def step_choose_work(self):
        works = self.cdb.get_works_by_class(self.data["class"], status='*')
        if not works:
            QMessageBox.information(self, "Очистка", "Работ нет.")
            self.reject()
            return

        self.group = QButtonGroup(self)
        self.content_layout.addWidget(QLabel("Выберите работу:"))

        for w in works:
            rb = QRadioButton(w[3])
            self.group.addButton(rb)
            self.content_layout.addWidget(rb)

    def step_confirm(self):
        title = QLabel("Подтверждение действия")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.content_layout.addWidget(title)

        info = QLabel(
            "Вы собираетесь удалить данные.\n"
            "Это действие необратимо."
        )
        info.setWordWrap(True)
        self.content_layout.addWidget(info)

        self.confirm_checkbox = QCheckBox(
            "Я осознаю последствия удаления данных"
        )
        self.confirm_checkbox.stateChanged.connect(
            lambda s: self.next_button.setEnabled(bool(s))
        )

        self.content_layout.addWidget(self.confirm_checkbox)

        self.next_button.setText("Удалить")
        self.next_button.setEnabled(False)

    def step_reset_timer(self):
        title = QLabel("Сброс")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.content_layout.addWidget(title)

        self.timer_label = QLabel()
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 14px;")
        self.content_layout.addWidget(self.timer_label)

        stop_button = QPushButton("СТОП")
        stop_button.setFixedHeight(36)
        stop_button.clicked.connect(self.cancel_reset)
        self.content_layout.addWidget(stop_button)

        self.next_button.hide()

        self.time_left = 10
        self.update_timer_label()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)


    def update_timer_label(self):
        self.timer_label.setText(
            f"До полного сброса осталось: <b>{self.time_left}</b> секунд"
        )

    def tick(self):
        self.time_left -= 1
        self.update_timer_label()

        if self.time_left <= 0:
            self.timer.stop()
            self.accept()

    def cancel_reset(self):
        if self.timer:
            self.timer.stop()
        self.reject()


    def show_step(self):
        self.clear_content()

        if self.step == 0:
            self.step_choose_mode()
        elif self.step == 1:
            self.step_choose_table()
        elif self.step == 2:
            self.step_choose_scope()
        elif self.step == 3:
            self.step_choose_class()
        elif self.step == 4:
            self.step_choose_work()
        elif self.step == 5:
            self.step_confirm()
        elif self.step == 6:
            self.step_reset_timer()

        self.content_layout.addStretch()
        self.rebuild()

    def on_next(self):
        if self.step <= 4:
            checked = self.group.checkedButton()
            if not checked:
                return

            value = checked.text()

            if self.step == 0:
                self.data["mode"] = value

                if value == "Очистка данных таблиц":
                    self.step = 1
                else:
                    self.step = 5

            elif self.step == 1:
                self.data["table"] = value
                self.step = 2

            elif self.step == 2:
                self.data["scope"] = value
                self.step = 5 if "все данные" in value else 3

            elif self.step == 3:
                self.data["class"] = value
                self.step = 4 if self.data.get("table") == "works" else 5

            elif self.step == 4:
                self.data["work"] = value
                self.step = 5

            self.show_step()

        elif self.step == 5:
            if self.data.get("mode") == self.RESET_MODE:
                self.step = 6
                self.show_step()
            else:
                self.accept()



class ManualGenerationDialog(QDialog):

    MODE_MANUAL = "manual"

    def __init__(self, classes: list[str], parent=None):
        super().__init__(parent)

        self.classes = classes.copy()
        self.step = 0
        self.data = {}

        self.setWindowTitle("Генерация работы")
        self.setMinimumSize(520, 350)

        self.main_layout = QVBoxLayout(self)
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        # --- Кнопка перехода ---
        self.next_button = QPushButton("Далее")
        self.next_button.setFixedHeight(32)
        self.next_button.clicked.connect(self.on_next)
        self.main_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        # --- Валидаторы ---
        self.int_validator = QIntValidator(1, 10_000, self)

        # --- Общий стиль ---
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
                padding: 4px;
            }
        """)

        self.show_step()

    # --------------------------------------------------

    def clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def rebuild(self):
        self.adjustSize()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

    # --------------------------------------------------

    def update_next_button_state(self):
        if self.step == 0:
            self.next_button.setEnabled(True)

        elif self.step == 1:
            if self.answers_cb.isChecked():
                self.next_button.setEnabled(
                    bool(self.answers_name_input.text().strip()) and
                    bool(self.answers_lines_input.text().strip())
                )
            else:
                self.next_button.setEnabled(True)

        elif self.step == 2:
            if self.criteria_cb.isChecked():
                self.next_button.setEnabled(
                    bool(self.criteria_name_input.text().strip()) and
                    bool(self.criteria_scale_input.text().strip())
                )
            else:
                self.next_button.setEnabled(True)

        elif self.step == 3:
            if self.absents_cb.isChecked():
                self.next_button.setEnabled(
                    bool(self.absents_name_input.text().strip())
                )
            else:
                self.next_button.setEnabled(True)

    # --------------------------------------------------

    def add_class_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выберите файл класса")
        if not filename:
            return

        class_name = filename.split("/")[-1].split(".")[0]

        for btn in self.class_group.buttons():
            if btn.text() == class_name:
                QMessageBox.information(
                    self, "Генерация",
                    f"Класс «{class_name}» уже существует"
                )
                return

        rb = QRadioButton(class_name)
        rb.setProperty("value", filename)
        self.class_group.addButton(rb)

        insert_pos = 0
        for i in range(self.content_layout.count()):
            w = self.content_layout.itemAt(i).widget()
            if isinstance(w, QRadioButton):
                insert_pos = i
                break

        self.content_layout.insertWidget(insert_pos, rb)

    # --------------------------------------------------
    # ------------------- ШАГИ -------------------------
    # --------------------------------------------------

    def step_students(self):
        title = QLabel("Ученики и работа")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.content_layout.addWidget(title)

        self.content_layout.addWidget(QLabel("Название работы:"))
        self.work_name_input = QLineEdit()
        self.work_name_input.textChanged.connect(self.update_next_button_state)
        self.content_layout.addWidget(self.work_name_input)

        self.content_layout.addWidget(QLabel("Выберите класс:"))
        self.class_group = QButtonGroup(self)

        for cls in self.classes:
            rb = QRadioButton(cls)
            rb.setProperty("value", cls)
            rb.toggled.connect(self.update_next_button_state)
            self.class_group.addButton(rb)
            self.content_layout.addWidget(rb)

        add_btn = QPushButton("Добавить класс из файла")
        add_btn.clicked.connect(self.add_class_from_file)
        self.content_layout.addWidget(add_btn)

        self.fill_students_cb = QCheckBox("Заполнить файлы учеников")
        self.content_layout.addWidget(self.fill_students_cb)

        self.content_layout.addWidget(QLabel("Количество строк (если заполнять):"))
        self.students_lines_input = QLineEdit()
        self.students_lines_input.setValidator(self.int_validator)
        self.students_lines_input.textChanged.connect(self.update_next_button_state)
        self.content_layout.addWidget(self.students_lines_input)

        self.students_lines_input.setVisible(False)
        self.content_layout.itemAt(self.content_layout.count() - 2).widget().setVisible(False)

        self.fill_students_cb.stateChanged.connect(
            lambda s: self.toggle_widget_visibility(self.students_lines_input, s)
        )

        self.update_next_button_state()

    def step_answers(self):
        title = QLabel("Файл с ответами")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.content_layout.addWidget(title)

        self.answers_cb = QCheckBox("Создать файл с ответами")
        self.content_layout.addWidget(self.answers_cb)

        self.content_layout.addWidget(QLabel("Имя файла:"))
        self.answers_name_input = QLineEdit()
        self.content_layout.addWidget(self.answers_name_input)

        self.content_layout.addWidget(QLabel("Количество строк:"))
        self.answers_lines_input = QLineEdit()
        self.answers_lines_input.setValidator(self.int_validator)
        self.content_layout.addWidget(self.answers_lines_input)

        for w in [
            self.answers_name_input,
            self.answers_lines_input,
            self.content_layout.itemAt(self.content_layout.indexOf(self.answers_name_input) - 1).widget(),
            self.content_layout.itemAt(self.content_layout.indexOf(self.answers_lines_input) - 1).widget()
        ]:
            w.setVisible(False)

        self.answers_cb.stateChanged.connect(self.toggle_answers_visibility)
        self.answers_name_input.textChanged.connect(self.update_next_button_state)
        self.answers_lines_input.textChanged.connect(self.update_next_button_state)

        self.update_next_button_state()

    def step_criteria(self):
        title = QLabel("Критерии оценки")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.content_layout.addWidget(title)

        self.criteria_cb = QCheckBox("Создать файл с критериями")
        self.content_layout.addWidget(self.criteria_cb)

        self.content_layout.addWidget(QLabel("Имя файла:"))
        self.criteria_name_input = QLineEdit()
        self.content_layout.addWidget(self.criteria_name_input)

        self.content_layout.addWidget(QLabel("Шкала оценки:"))
        self.criteria_scale_input = QLineEdit()
        self.criteria_scale_input.setValidator(self.int_validator)
        self.content_layout.addWidget(self.criteria_scale_input)

        for w in [
            self.criteria_name_input,
            self.criteria_scale_input,
            self.content_layout.itemAt(self.content_layout.indexOf(self.criteria_name_input) - 1).widget(),
            self.content_layout.itemAt(self.content_layout.indexOf(self.criteria_scale_input) - 1).widget()
        ]:
            w.setVisible(False)

        self.criteria_cb.stateChanged.connect(self.toggle_criteria_visibility)
        self.criteria_name_input.textChanged.connect(self.update_next_button_state)
        self.criteria_scale_input.textChanged.connect(self.update_next_button_state)

        self.update_next_button_state()

    def step_absents(self):
        title = QLabel("Отсутствующие")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.content_layout.addWidget(title)

        self.absents_cb = QCheckBox("Создать файл с отсутствующими")
        self.content_layout.addWidget(self.absents_cb)

        self.content_layout.addWidget(QLabel("Имя файла:"))
        self.absents_name_input = QLineEdit()
        self.content_layout.addWidget(self.absents_name_input)

        for w in [
            self.absents_name_input,
            self.content_layout.itemAt(self.content_layout.indexOf(self.absents_name_input) - 1).widget()
        ]:
            w.setVisible(False)

        self.absents_cb.stateChanged.connect(self.toggle_absents_visibility)
        self.absents_name_input.textChanged.connect(self.update_next_button_state)

        self.next_button.setText("Готово")
        self.update_next_button_state()

    # --------------------------------------------------

    def toggle_widget_visibility(self, widget, state):
        visible = bool(state)
        widget.setVisible(visible)
        idx = self.content_layout.indexOf(widget)
        if idx > 0:
            self.content_layout.itemAt(idx - 1).widget().setVisible(visible)
        self.update_next_button_state()

    def toggle_answers_visibility(self, state):
        for w in [
            self.answers_name_input,
            self.answers_lines_input,
            self.content_layout.itemAt(self.content_layout.indexOf(self.answers_name_input) - 1).widget(),
            self.content_layout.itemAt(self.content_layout.indexOf(self.answers_lines_input) - 1).widget()
        ]:
            w.setVisible(bool(state))
        self.update_next_button_state()

    def toggle_criteria_visibility(self, state):
        for w in [
            self.criteria_name_input,
            self.criteria_scale_input,
            self.content_layout.itemAt(self.content_layout.indexOf(self.criteria_name_input) - 1).widget(),
            self.content_layout.itemAt(self.content_layout.indexOf(self.criteria_scale_input) - 1).widget()
        ]:
            w.setVisible(bool(state))
        self.update_next_button_state()

    def toggle_absents_visibility(self, state):
        for w in [
            self.absents_name_input,
            self.content_layout.itemAt(self.content_layout.indexOf(self.absents_name_input) - 1).widget()
        ]:
            w.setVisible(bool(state))
        self.update_next_button_state()

    # --------------------------------------------------

    def show_step(self):
        self.clear_content()

        if self.step == 0:
            self.step_students()
        elif self.step == 1:
            self.step_answers()
        elif self.step == 2:
            self.step_criteria()
        elif self.step == 3:
            self.step_absents()

        self.content_layout.addStretch()
        self.rebuild()

    # --------------------------------------------------

    def on_next(self):
        if self.step == 0:
            checked = self.class_group.checkedButton()

            self.data["mode"] = self.MODE_MANUAL
            self.data["work_name"] = self.work_name_input.text().strip()
            self.data["class"] = checked.property("value") if checked else None
            self.data["fill_students"] = self.fill_students_cb.isChecked()
            self.data["students_lines"] = self.students_lines_input.text().strip()

            self.step = 1

        elif self.step == 1:
            self.data["answers"] = self.answers_cb.isChecked()
            self.data["answers_name"] = self.answers_name_input.text().strip()
            self.data["answers_lines"] = self.answers_lines_input.text().strip()
            self.step = 2

        elif self.step == 2:
            self.data["criteria"] = self.criteria_cb.isChecked()
            self.data["criteria_name"] = self.criteria_name_input.text().strip()
            self.data["criteria_scale"] = self.criteria_scale_input.text().strip()
            self.step = 3

        elif self.step == 3:
            self.data["absents"] = self.absents_cb.isChecked()
            self.data["absents_name"] = self.absents_name_input.text().strip()
            self.accept()
            return

        self.show_step()



class FastGenerationDialog(QDialog):

    def __init__(self, classes: list[str], parent=None):
        super().__init__(parent)

        self.classes = list(classes)
        self.data = {}

        self.setWindowTitle("Быстрая генерация")
        self.setMinimumSize(450, 360)

        self.main_layout = QVBoxLayout(self)

        # --- Название работы ---
        self.main_layout.addWidget(QLabel("Название работы:"))

        self.work_name_input = QLineEdit()
        self.work_name_input.setPlaceholderText("Например: Контрольная №3")
        self.work_name_input.setMaxLength(60)

        name_regex = QRegularExpression(r"[A-Za-zА-Яа-я0-9 №_\-]+")
        self.work_name_input.setValidator(
            QRegularExpressionValidator(name_regex, self)
        )

        self.work_name_input.textChanged.connect(self.update_state)
        self.main_layout.addWidget(self.work_name_input)

        # --- Классы ---
        self.main_layout.addWidget(QLabel("Выберите класс:"))

        self.class_layout = QVBoxLayout()
        self.main_layout.addLayout(self.class_layout)

        self.group = QButtonGroup(self)
        self._build_class_list()

        self.add_class_btn = QPushButton("Добавить класс из файла")
        self.add_class_btn.clicked.connect(self.add_class_from_file)
        self.main_layout.addWidget(self.add_class_btn)

        # --- Количество строк ---
        self.main_layout.addWidget(QLabel("Количество строк в файле ответов:"))

        self.answers_lines = QSpinBox()
        self.answers_lines.setRange(1, 500)
        self.answers_lines.setValue(10)
        self.answers_lines.valueChanged.connect(self.update_state)

        self.main_layout.addWidget(self.answers_lines)

        # --- Кнопки ---
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addStretch()

        self.ok_button = QPushButton("Готово")
        self.ok_button.setEnabled(False)
        self.ok_button.clicked.connect(self.on_accept)

        self.buttons_layout.addWidget(self.ok_button)
        self.main_layout.addLayout(self.buttons_layout)


    def _build_class_list(self):
        for i in reversed(range(self.class_layout.count())):
            w = self.class_layout.takeAt(i).widget()
            if w:
                w.deleteLater()

        for cls in self.classes:
            rb = QRadioButton(cls)
            rb.toggled.connect(self.update_state)
            self.group.addButton(rb)
            self.class_layout.addWidget(rb)

    def add_class_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Файл с классом")
        if not filename:
            return

        name = os.path.splitext(os.path.basename(filename))[0]

        for btn in self.group.buttons():
            if btn.text() == name:
                QMessageBox.information(self, "Генерация", "Такой класс уже есть")
                return

        rb = QRadioButton(name)

        rb.setProperty("value", filename)
        rb.setProperty("source", "file")

        self.group.addButton(rb)

        self.class_layout.insertWidget(0, rb)


    def update_state(self):
        has_name = bool(self.work_name_input.text().strip())
        has_class = self.group.checkedButton() is not None
        has_lines = self.answers_lines.value() > 0

        self.ok_button.setEnabled(has_name and has_class and has_lines)

    def on_accept(self):
        checked = self.group.checkedButton()
        class_value = checked.property("value") if checked else None

        self.data = {
            'mode': 'fast',
            'work_name': self.work_name_input.text().strip(),
            'class': class_value,

            'fill_students': True,
            'students_lines': self.answers_lines.value(),

            'answers': False,
            'answers_name': None,
            'answers_lines': self.answers_lines.value(),

            'criteria': False,
            'criteria_name': None,
            'criteria_scale': None,

            'absents': False,
            'absents_name': None
        }

        self.accept()


class PatternGenerationDialog(QDialog):
    MODE_PATTERN = "pattern"

    def __init__(self, patterns: dict, classes: list[str], manual_dialog_cls, parent=None):
        super().__init__(parent)

        if not isinstance(classes, (list, tuple)):
            raise TypeError("classes must be list or tuple")

        self.patterns = patterns          # {name: data_dict}
        self.classes = list(classes)
        self.manual_dialog_cls = manual_dialog_cls
        self.data = None                  # итоговый словарь

        self.setWindowTitle("Генерация по паттерну")
        self.setMinimumWidth(420)

        self.layout = QVBoxLayout(self)
        self.group = QButtonGroup(self)

        self._build_ui()


    def _build_ui(self):
        title = QLabel("Выберите паттерн генерации")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.layout.addWidget(title)

        if not self.patterns:
            empty = QLabel(
                "У вас нет сохранённых паттернов.\n"
                "Создайте новый — он появится здесь."
            )
            empty.setWordWrap(True)
            self.layout.addWidget(empty)
        else:
            for name in self.patterns.keys():
                rb = QRadioButton(name)
                self.group.addButton(rb)
                self.layout.addWidget(rb)

        self.rb_new = QRadioButton("Создать новый паттерн")
        self.group.addButton(self.rb_new)
        self.layout.addWidget(self.rb_new)

        self.layout.addStretch()

        btn = QPushButton("Готово")
        btn.setFixedHeight(32)
        btn.clicked.connect(self.on_accept)
        self.layout.addWidget(btn, alignment=Qt.AlignRight)


    def on_accept(self):
        checked = self.group.checkedButton()
        if not checked:
            QMessageBox.information(self, "Паттерны", "Выберите вариант")
            return

        # Логика создания нового паттерна
        if checked is self.rb_new:
            dlg = self.manual_dialog_cls(self.classes, self)

            if dlg.exec():
                data = dlg.data.copy()
                data["mode"] = self.MODE_PATTERN
                self.data = data
                self.accept()
            return

        # Если паттерн уже существует
        name = checked.text()
        data = self.patterns[name].copy()
        data["mode"] = self.MODE_PATTERN
        self.data = data
        self.accept()






class GenerationModeDialog(QDialog):
    def __init__(self, classes: list, manual_dialog_cls, fast_dialog_cls, pattern_dialog_cls, patterns, parent=None):
        super().__init__(parent)

        self.classes = list(classes)
        self.manual_dialog_cls = manual_dialog_cls
        self.fast_dialog_cls = fast_dialog_cls
        self.pattern_dialog_cls = pattern_dialog_cls
        self.patterns = patterns or {}

        self.data = None

        self.setWindowTitle("Выбор режима генерации")
        self.setMinimumWidth(420)

        self._build_ui()


    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Выберите режим генерации")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        layout.addWidget(title)

        self.group = QButtonGroup(self)

        self.rb_manual = QRadioButton("Ручная генерация")
        self.rb_fast = QRadioButton("Быстрая генерация")
        self.rb_pattern = QRadioButton("Генерация по паттерну")

        self.group.addButton(self.rb_manual)
        self.group.addButton(self.rb_fast)
        self.group.addButton(self.rb_pattern)

        layout.addWidget(self.rb_manual)
        layout.addWidget(self.rb_fast)
        layout.addWidget(self.rb_pattern)

        layout.addStretch()

        btn = QPushButton("Далее")
        btn.setFixedHeight(32)
        btn.clicked.connect(self.on_accept)
        layout.addWidget(btn, alignment=Qt.AlignRight)


    def on_accept(self):
        checked = self.group.checkedButton()
        if not checked:
            QMessageBox.information(
                self,
                "Генерация",
                "Выберите режим генерации"
            )
            return

        if checked is self.rb_manual:
            dlg = self.manual_dialog_cls(
                classes=self.classes,
                parent=self
            )

        elif checked is self.rb_fast:
            dlg = self.fast_dialog_cls(
                classes=self.classes,
                parent=self
            )

        elif checked is self.rb_pattern:
            dlg = self.pattern_dialog_cls(
                patterns=self.patterns,
                classes=self.classes,
                manual_dialog_cls=self.manual_dialog_cls,
                parent=self
            )
        else:
            return

        if dlg.exec() == QDialog.Accepted:
            self.data = dlg.data
            self.accept()


