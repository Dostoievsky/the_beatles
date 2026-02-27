import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QRadioButton, QButtonGroup,
                             QPushButton, QCheckBox, QMessageBox, QWidget,
                             QStackedWidget, QHBoxLayout, QLabel)

import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QRadioButton, QButtonGroup,
                             QPushButton, QCheckBox, QMessageBox, QWidget,
                             QStackedWidget, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt


class SelectionDialog(QDialog):
    def __init__(self, parent, classes_list, works_dict):
        super().__init__(parent)
        self.work_group = None
        self.layout2 = None
        self.page2 = None
        self.btn_next = None
        self.plot_checkbox = None
        self.class_group = None
        self.stack = None
        self.main_layout = None
        self.btn_done = None
        self.setWindowTitle("Мастер настройки")
        self.setMinimumSize(400, 350)  # Увеличил высоту для простора

        self.classes_list = classes_list
        self.works_dict = works_dict
        self.result_data = {}

        if not self.classes_list:
            QMessageBox.warning(self, "Ошибка", "Список классов пуст!")
            self.reject()
            return

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.stack = QStackedWidget()

        page1 = QWidget()
        layout1 = QVBoxLayout(page1)

        lbl1 = QLabel("Выберите класс:")
        lbl1.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout1.addWidget(lbl1)
        layout1.addSpacing(10)  # Небольшой отступ сверху

        self.class_group = QButtonGroup(self)
        for i, class_name in enumerate(self.classes_list):
            rb = QRadioButton(class_name)
            self.class_group.addButton(rb, i)
            layout1.addWidget(rb)


        layout1.addStretch(1)

        self.plot_checkbox = QCheckBox("Строить графики")
        layout1.addWidget(self.plot_checkbox)
        layout1.addSpacing(10)  # Отступ между чекбоксом и кнопкой

        self.btn_next = QPushButton("Далее")
        self.btn_next.setFixedWidth(100)
        self.btn_next.setEnabled(False)
        self.btn_next.clicked.connect(self.go_to_page2)

        footer1 = QHBoxLayout()
        footer1.addStretch()  # Кнопку в правый угол
        footer1.addWidget(self.btn_next)
        layout1.addLayout(footer1)

        self.class_group.buttonClicked.connect(lambda: self.btn_next.setEnabled(True))

        # --- СТРАНИЦА 2: Выбор работы ---
        self.page2 = QWidget()
        self.layout2 = QVBoxLayout(self.page2)

        # Элементы будут добавляться динамически в go_to_page2

        self.stack.addWidget(page1)
        self.stack.addWidget(self.page2)
        self.main_layout.addWidget(self.stack)

    def go_to_page2(self):
        selected_class = self.class_group.checkedButton().text()
        self.result_data['class'] = selected_class
        self.result_data['build_plots'] = self.plot_checkbox.isChecked()

        while self.layout2.count():
            item = self.layout2.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        lbl2 = QLabel(f"Выберите работу:")
        lbl2.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout2.addWidget(lbl2)
        self.layout2.addSpacing(10)

        self.work_group = QButtonGroup(self)
        works = self.works_dict.get(selected_class, [])

        if not works:
            lbl_err = QLabel("Работ не найдено для этого класса.")
            self.layout2.addWidget(lbl_err)
        else:
            for i, work_name in enumerate(works):
                rb = QRadioButton(work_name)
                self.work_group.addButton(rb, i)
                self.layout2.addWidget(rb)

        self.layout2.addStretch(1)  # Прижимает список работ вверх

        self.btn_done = QPushButton("Готово")
        self.btn_done.setFixedWidth(100)
        self.btn_done.clicked.connect(self.finish)

        footer2 = QHBoxLayout()
        footer2.addStretch()
        footer2.addWidget(self.btn_done)
        self.layout2.addLayout(footer2)

        self.stack.setCurrentIndex(1)

    def finish(self):
        selected_work_btn = self.work_group.checkedButton()
        if selected_work_btn:
            self.result_data['work'] = selected_work_btn.text()
            self.accept()
        else:
            QMessageBox.warning(self, "Внимание", "Выберите работу из списка!")

    def get_data(self):
        return self.result_data
