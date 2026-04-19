import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QPushButton, QListWidget,
                             QListWidgetItem, QComboBox, QRadioButton,
                             QGroupBox, QLabel, QFileDialog, QStackedWidget, QWidget)
from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import QMessageBox

class ExportDialog(QDialog):
    def __init__(self, parent, classes_list, table_names_list, works_dict):
        super().__init__(parent)
        self.setWindowTitle("Настройка экспорта")
        self.resize(420, 550)

        self.classes_list = classes_list
        self.table_names_list = table_names_list
        self.works_dict = works_dict

        self.export_path = os.getcwd()
        self.result_mode = None

        self.checkbox_style = """
            QListWidget::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #7a7a7a;
                border-radius: 3px;
                background-color: white;
            }
            QListWidget::indicator:checked {
                background-color: #557A95; 
                border: 1px solid #357abd;
                image: url(check.png);
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:selected {
                background-color: #e6f0ff;
                color: black;
            }
        """
        self.setup_ui()

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.create_main_page()
        self.create_tables_page()
        self.create_classes_page()
        self.create_works_page()

        self.stack.setCurrentIndex(0)

    def add_checkbox_items(self, list_widget, items):
        list_widget.clear()
        list_widget.setStyleSheet(self.checkbox_style)
        for text in items:
            item = QListWidgetItem(text)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Unchecked)
            list_widget.addItem(item)

    def get_selected_checkboxes(self, list_widget):
        return [list_widget.item(i).text() for i in range(list_widget.count())
                if list_widget.item(i).checkState() == Qt.Checked]

    # --- НОВЫЕ МЕТОДЫ-ОБРАБОТЧИКИ С ПРОВЕРКАМИ ---
    def on_tables_clicked(self):
        if not self.table_names_list:
            QMessageBox.warning(self, "Нет данных", "Список таблиц пуст. Нечего экспортировать.")
            return
        self.stack.setCurrentIndex(1)

    def on_classes_clicked(self):
        if not self.classes_list:
            QMessageBox.warning(self, "Нет данных", "Список классов пуст. Нечего экспортировать.")
            return
        self.stack.setCurrentIndex(2)

    def on_works_clicked(self):
        if not self.works_dict:
            QMessageBox.warning(self, "Нет данных", "Словарь работ пуст. Нет доступных классов или работ.")
            return
        self.stack.setCurrentIndex(3)

    # --- СТРАНИЦА 0: МЕНЮ (изменённая) ---
    def create_main_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(12)

        layout.addStretch()
        # Кнопка таблиц
        btn_tables = QPushButton("📊 Экспорт таблиц")
        btn_tables.setMinimumHeight(45)
        btn_tables.clicked.connect(self.on_tables_clicked)
        layout.addWidget(btn_tables)

        # Кнопка классов
        btn_classes = QPushButton("👥 Экспорт классов")
        btn_classes.setMinimumHeight(45)
        btn_classes.clicked.connect(self.on_classes_clicked)
        layout.addWidget(btn_classes)

        # Кнопка работ
        btn_works = QPushButton("📂 Экспорт работ")
        btn_works.setMinimumHeight(45)
        btn_works.clicked.connect(self.on_works_clicked)
        layout.addWidget(btn_works)

        layout.addStretch()
        self.btn_path = QPushButton(f"📁 Папка: ...{os.path.basename(self.export_path)}")
        self.btn_path.setToolTip(self.export_path)
        self.btn_path.clicked.connect(self.select_folder)
        layout.addWidget(self.btn_path)
        self.stack.addWidget(page)


    # --- СТРАНИЦА 1: ТАБЛИЦЫ ---
    def create_tables_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Выберите таблицы для выгрузки:"))

        self.table_list = QListWidget()
        self.add_checkbox_items(self.table_list, self.table_names_list)
        layout.addWidget(self.table_list)

        btn = QPushButton("Начать экспорт")
        btn.clicked.connect(lambda: self.finish_export("tables"))
        layout.addWidget(btn)
        self.stack.addWidget(page)

    # --- СТРАНИЦА 2: КЛАССЫ ---
    def create_classes_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("Выберите классы:"))
        self.class_list = QListWidget()
        self.add_checkbox_items(self.class_list, self.classes_list)
        layout.addWidget(self.class_list)

        group = QGroupBox()
        g_layout = QVBoxLayout()
        self.tlc = QLabel("Что экспортируем?")
        self.rb_c1 = QRadioButton("Список выбранных классов")
        self.rb_c2 = QRadioButton("Все работы по этим классам")
        self.rb_c3 = QRadioButton("Контакты учеников (с TG)")
        self.rb_c4 = QRadioButton("Список учеников (без TG)")
        self.rb_c1.setChecked(True)
        for rb in [self.tlc, self.rb_c1, self.rb_c2, self.rb_c3, self.rb_c4]: g_layout.addWidget(rb)
        group.setLayout(g_layout)
        layout.addWidget(group)

        btn = QPushButton("Подтвердить экспорт")
        btn.clicked.connect(lambda: self.finish_export("classes"))
        layout.addWidget(btn)
        self.stack.addWidget(page)

    # --- СТРАНИЦА 3: РАБОТЫ ---
    def create_works_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        layout.addWidget(QLabel("Выберите класс:"))
        self.combo_w = QComboBox()
        self.combo_w.addItems(self.works_dict.keys())
        self.combo_w.currentTextChanged.connect(self.update_works)
        layout.addWidget(self.combo_w)

        layout.addWidget(QLabel("Выберите работы:"))
        self.work_list = QListWidget()
        self.work_list.itemChanged.connect(self.handle_all_works)
        layout.addWidget(self.work_list)
        self.update_works(self.combo_w.currentText())

        group = QGroupBox()
        g_layout = QVBoxLayout()  # Исправлено: теперь вертикально и не плывет
        self.tl = QLabel("Что экспортируем?")
        self.rb_w1 = QRadioButton("Только названия")
        self.rb_w2 = QRadioButton("Исходные файлы (json/py)")
        self.rb_w3 = QRadioButton("Отчет в формате TXT")
        self.rb_w4 = QRadioButton("Таблица результатов CSV")
        self.rb_w1.setChecked(True)
        for rb in [self.tl, self.rb_w1, self.rb_w2, self.rb_w3, self.rb_w4]: g_layout.addWidget(rb)
        group.setLayout(g_layout)
        layout.addWidget(group)

        btn = QPushButton("Экспортировать работы")
        btn.clicked.connect(lambda: self.finish_export("works"))
        layout.addWidget(btn)
        self.stack.addWidget(page)

    def select_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку")
        if path:
            self.export_path = path
            # Обновляем текст на кнопке, чтобы было видно изменение
            display_path = (path[:25] + '...') if len(path) > 25 else path
            self.btn_path.setText(f"📁 Папка: {display_path}")

    def update_works(self, name):
        self.add_checkbox_items(self.work_list, ["все работы"] + self.works_dict.get(name, []))

    def handle_all_works(self, item):
        if item.text() == "все работы":
            self.work_list.blockSignals(True)
            state = item.checkState()
            if state == Qt.Checked:
                for i in range(self.work_list.count()):
                    it = self.work_list.item(i)
                    if it.text() != "все работы":
                        it.setCheckState(Qt.Unchecked)
                        it.setFlags(it.flags() & ~Qt.ItemIsEnabled)
            else:
                for i in range(self.work_list.count()):
                    self.work_list.item(i).setFlags(self.work_list.item(i).flags() | Qt.ItemIsEnabled)
            self.work_list.blockSignals(False)

    def finish_export(self, mode):
        selected = []
        if mode == "tables":
            selected = self.get_selected_checkboxes(self.table_list)
        elif mode == "classes":
            selected = self.get_selected_checkboxes(self.class_list)
        elif mode == "works":
            selected = self.get_selected_checkboxes(self.work_list)

        if not selected: return

        self.result_mode = mode
        self.accept()

    def get_results(self):
        p = self.export_path
        if self.result_mode == "tables":
            return ("tables", p, self.get_selected_checkboxes(self.table_list))
        elif self.result_mode == "classes":
            modes = ["list_of_classes", "all_works", "all_students_tg", "all_students_no_tg"]
            m = next(
                modes[i] for i, rb in enumerate([self.rb_c1, self.rb_c2, self.rb_c3, self.rb_c4]) if rb.isChecked())
            return ("classes", p, (self.get_selected_checkboxes(self.class_list), m))
        elif self.result_mode == "works":
            modes = ["names", "source_files", "results_txt", "results_csv"]
            m = next(
                modes[i] for i, rb in enumerate([self.rb_w1, self.rb_w2, self.rb_w3, self.rb_w4]) if rb.isChecked())
            return ("works", p, (self.combo_w.currentText(), self.get_selected_checkboxes(self.work_list), m))
        return None
