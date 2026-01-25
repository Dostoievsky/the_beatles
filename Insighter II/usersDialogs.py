from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup,
    QScrollArea, QWidget, QSizePolicy, QMessageBox, QCheckBox
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

