from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup,
    QScrollArea, QWidget, QSizePolicy, QMessageBox, QCheckBox, QLineEdit, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import Qt
from Database_Settings_classes import Settings
import random
from clearmodes import *

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



class GenerationDialog(QDialog):

    MODE_MANUAL = "Ручная генерация"
    MODE_FAST = "Быстрая генерация"
    MODE_PATTERN = "Генерация по паттерну"

    def __init__(self, classes: list[str], parent=None):
        super().__init__(parent)

        self.classes = classes.copy()  # чтобы можно было динамически добавлять
        self.step = 0
        self.data = {}
        self.group = None

        self.setWindowTitle("Генерация работы")
        self.setMinimumSize(520, 350)

        self.main_layout = QVBoxLayout(self)
        self.content_layout = QVBoxLayout()
        self.main_layout.addLayout(self.content_layout)

        self.next_button = QPushButton("Далее")
        self.next_button.setFixedHeight(32)
        self.next_button.clicked.connect(self.on_next)
        self.next_button.setEnabled(False)  # кнопка заблокирована до ввода
        self.main_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

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

        self.show_step()

    # ----------------- helpers -----------------

    def clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def rebuild(self):
        self.adjustSize()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

    def update_next_button_state(self):
        """Активируем кнопку Далее только если заполнены обязательные поля"""
        if self.step == 0:  # выбор режима — **не блокируем кнопку**
            self.next_button.setEnabled(True)
        elif self.step == 1:  # ученики и работа — **не блокируем кнопку**
            self.next_button.setEnabled(True)
        elif self.step == 2:  # ответы
            if self.answers_cb.isChecked():
                self.next_button.setEnabled(bool(self.answers_name_input.text().strip())
                                            and bool(self.answers_lines_input.text().strip()))
            else:
                self.next_button.setEnabled(True)
        elif self.step == 3:  # критерии
            if self.criteria_cb.isChecked():
                self.next_button.setEnabled(bool(self.criteria_name_input.text().strip())
                                            and bool(self.criteria_scale_input.text().strip()))
            else:
                self.next_button.setEnabled(True)
        elif self.step == 4:  # отсутствующие
            if self.absents_cb.isChecked():
                self.next_button.setEnabled(bool(self.absents_name_input.text().strip()))
            else:
                self.next_button.setEnabled(True)

    # ----------------- steps -----------------

    def step_choose_mode(self):
        text = QLabel('В скобках у необязательных полей указано, что будет, если оставите поле пустым.\n')

        title = QLabel("Выберите режим генерации")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.content_layout.addWidget(text)
        self.content_layout.addWidget(title)


        self.group = QButtonGroup(self)
        for mode in [self.MODE_MANUAL, self.MODE_FAST, self.MODE_PATTERN]:
            rb = QRadioButton(mode, self)
            self.group.addButton(rb)
            self.content_layout.addWidget(rb)
            rb.toggled.connect(self.update_next_button_state)

        self.update_next_button_state()

    def step_students(self):
        title = QLabel("Ученики и работа")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.content_layout.addWidget(title)

        # Название работы
        self.content_layout.addWidget(QLabel("Название работы:", self))
        self.work_name_input = QLineEdit(self)
        self.content_layout.addWidget(self.work_name_input)
        self.work_name_input.textChanged.connect(self.update_next_button_state)

        # Класс
        self.content_layout.addWidget(QLabel("Выберите класс:", self))
        self.group = QButtonGroup(self)
        for cls in self.classes:
            rb = QRadioButton(cls, self)
            self.group.addButton(rb)
            self.content_layout.addWidget(rb)
            rb.toggled.connect(self.update_next_button_state)

        # Кнопка "Добавить класс из файла"
        add_class_btn = QPushButton("Добавить класс из файла", self)
        self.content_layout.addWidget(add_class_btn)
        add_class_btn.clicked.connect(self.add_class_from_file)

        # Заполнить файлы учеников
        self.fill_students_cb = QCheckBox("Заполнить файлы учеников", self)
        self.content_layout.addWidget(self.fill_students_cb)
        self.fill_students_cb.stateChanged.connect(self.update_next_button_state)

        # Количество строк
        self.content_layout.addWidget(QLabel("Количество строк (если заполнять):", self))
        self.students_lines_input = QLineEdit(self)
        self.students_lines_input.setPlaceholderText("Например: 10")
        self.content_layout.addWidget(self.students_lines_input)

        # Сначала поле скрыто, пока галочка не выбрана
        self.students_lines_input.setVisible(False)
        self.content_layout.itemAt(self.content_layout.count() - 2).widget().setVisible(False)
        self.fill_students_cb.stateChanged.connect(
            lambda state: self.toggle_widget_visibility(self.students_lines_input, state)
        )

        self.update_next_button_state()

    def toggle_widget_visibility(self, widget, state):
        visible = bool(state)
        widget.setVisible(visible)
        # label перед widget
        idx = self.content_layout.indexOf(widget)
        if idx > 0:
            self.content_layout.itemAt(idx - 1).widget().setVisible(visible)
        self.update_next_button_state()

    def add_class_from_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Выберите файл класса")
        if filename:
            # Используем имя файла как имя класса для примера
            new_class_name = filename.split("/")[-1].split(".")[0]
            if new_class_name in self.classes:
                QMessageBox.information(self, "Генерация", f"Класс {new_class_name} уже есть")
                return
            self.classes.insert(0, new_class_name)  # вставляем в начало списка
            rb = QRadioButton(new_class_name, self)
            self.group.addButton(rb)

            # Вставляем виджет **перед всеми существующими радио-кнопками**
            first_rb_idx = 0
            for i in range(self.content_layout.count()):
                item = self.content_layout.itemAt(i)
                if item.widget() and isinstance(item.widget(), QRadioButton):
                    first_rb_idx = i
                    break
            self.content_layout.insertWidget(first_rb_idx, rb)
            rb.toggled.connect(self.update_next_button_state)

    def step_answers(self):
        title = QLabel("Файл с ответами")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.content_layout.addWidget(title)

        self.answers_cb = QCheckBox("Создать файл с ответами", self)
        self.content_layout.addWidget(self.answers_cb)
        self.answers_cb.stateChanged.connect(
            lambda state: self.toggle_widget_visibility_for_answers(state)
        )

        self.content_layout.addWidget(QLabel("Имя файла:", self))
        self.answers_name_input = QLineEdit(self)
        self.content_layout.addWidget(self.answers_name_input)

        self.content_layout.addWidget(QLabel("Количество строк:", self))
        self.answers_lines_input = QLineEdit(self)
        self.content_layout.addWidget(self.answers_lines_input)

        # Скрываем поля пока галочка не стоит
        for w in [self.answers_name_input,
                  self.content_layout.itemAt(self.content_layout.indexOf(self.answers_name_input) - 1).widget(),
                  self.answers_lines_input,
                  self.content_layout.itemAt(self.content_layout.indexOf(self.answers_lines_input) - 1).widget()]:
            w.setVisible(False)

        self.answers_name_input.textChanged.connect(self.update_next_button_state)
        self.answers_lines_input.textChanged.connect(self.update_next_button_state)

        self.update_next_button_state()

    def toggle_widget_visibility_for_answers(self, state):
        visible = bool(state)
        for widget in [self.answers_name_input,
                       self.answers_lines_input,
                       self.content_layout.itemAt(self.content_layout.indexOf(self.answers_name_input) - 1).widget(),
                       self.content_layout.itemAt(self.content_layout.indexOf(self.answers_lines_input) - 1).widget()]:
            widget.setVisible(visible)
        self.update_next_button_state()

    def step_criteria(self):
        title = QLabel("Критерии оценки")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.content_layout.addWidget(title)

        self.criteria_cb = QCheckBox("Создать файл с критериями", self)
        self.content_layout.addWidget(self.criteria_cb)
        self.criteria_cb.stateChanged.connect(
            lambda state: self.toggle_widget_visibility_for_criteria(state)
        )

        self.content_layout.addWidget(QLabel("Имя файла:", self))
        self.criteria_name_input = QLineEdit(self)
        self.content_layout.addWidget(self.criteria_name_input)

        self.content_layout.addWidget(QLabel("Шкала оценки:", self))
        self.criteria_scale_input = QLineEdit(self)
        self.criteria_scale_input.setPlaceholderText("Например: 5")
        self.content_layout.addWidget(self.criteria_scale_input)

        # Скрываем поля пока галочка не стоит
        for w in [self.criteria_name_input,
                  self.content_layout.itemAt(self.content_layout.indexOf(self.criteria_name_input) - 1).widget(),
                  self.criteria_scale_input,
                  self.content_layout.itemAt(self.content_layout.indexOf(self.criteria_scale_input) - 1).widget()]:
            w.setVisible(False)

        self.criteria_name_input.textChanged.connect(self.update_next_button_state)
        self.criteria_scale_input.textChanged.connect(self.update_next_button_state)

        self.update_next_button_state()

    def toggle_widget_visibility_for_criteria(self, state):
        visible = bool(state)
        for widget in [self.criteria_name_input,
                       self.content_layout.itemAt(self.content_layout.indexOf(self.criteria_name_input) - 1).widget(),
                       self.criteria_scale_input,
                       self.content_layout.itemAt(self.content_layout.indexOf(self.criteria_scale_input) - 1).widget()]:
            widget.setVisible(visible)
        self.update_next_button_state()

    def step_absents(self):
        title = QLabel("Отсутствующие")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.content_layout.addWidget(title)

        self.absents_cb = QCheckBox("Создать файл с отсутствующими", self)
        self.content_layout.addWidget(self.absents_cb)
        self.absents_cb.stateChanged.connect(
            lambda state: self.toggle_widget_visibility_for_absents(state)
        )

        self.content_layout.addWidget(QLabel("Имя файла:", self))
        self.absents_name_input = QLineEdit(self)
        self.content_layout.addWidget(self.absents_name_input)

        # Скрываем поле пока галочка не стоит
        for w in [self.absents_name_input,
                  self.content_layout.itemAt(self.content_layout.indexOf(self.absents_name_input) - 1).widget()]:
            w.setVisible(False)

        self.absents_name_input.textChanged.connect(self.update_next_button_state)
        self.update_next_button_state()

        self.next_button.setText("Готово")

    def toggle_widget_visibility_for_absents(self, state):
        visible = bool(state)
        for widget in [self.absents_name_input,
                       self.content_layout.itemAt(self.content_layout.indexOf(self.absents_name_input) - 1).widget()]:
            widget.setVisible(visible)
        self.update_next_button_state()

    # ----------------- dispatcher -----------------

    def show_step(self):
        self.clear_content()
        if self.step == 0:
            self.step_choose_mode()
        elif self.step == 1:
            self.step_students()
        elif self.step == 2:
            self.step_answers()
        elif self.step == 3:
            self.step_criteria()
        elif self.step == 4:
            self.step_absents()

        self.content_layout.addStretch()
        self.rebuild()

    # ----------------- navigation -----------------

    def on_next(self):
        # шаг 0 — выбор режима
        if self.step == 0:
            checked = self.group.checkedButton()
            mode = checked.text() if checked else None
            self.data["mode"] = mode
            if mode != self.MODE_MANUAL:
                QMessageBox.information(
                    self,
                    "Генерация",
                    "Этот режим пока не реализован."
                )
                return
            self.step = 1
            self.show_step()
            return

        # шаг 1 — ученики и работа
        if self.step == 1:
            checked = self.group.checkedButton()
            self.data["work_name"] = self.work_name_input.text().strip()
            self.data["class"] = checked.text() if checked else None
            self.data["fill_students"] = self.fill_students_cb.isChecked()
            self.data["students_lines"] = self.students_lines_input.text().strip()
            self.step = 2
            self.show_step()
            return

        # шаг 2 — ответы
        if self.step == 2:
            self.data["answers"] = self.answers_cb.isChecked()
            self.data["answers_name"] = self.answers_name_input.text().strip()
            self.data["answers_lines"] = self.answers_lines_input.text().strip()
            self.step = 3
            self.show_step()
            return

        # шаг 3 — критерии
        if self.step == 3:
            self.data["criteria"] = self.criteria_cb.isChecked()
            self.data["criteria_name"] = self.criteria_name_input.text().strip()
            self.data["criteria_scale"] = self.criteria_scale_input.text().strip()
            self.step = 4
            self.show_step()
            return

        # шаг 4 — отсутствующие → финал
        if self.step == 4:
            self.data["absents"] = self.absents_cb.isChecked()
            self.data["absents_name"] = self.absents_name_input.text().strip()
            self.accept()

