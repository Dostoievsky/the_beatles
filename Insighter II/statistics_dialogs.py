import datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QStackedWidget, QRadioButton,
                             QButtonGroup, QCheckBox, QMessageBox,
                             QListWidget, QListWidgetItem, QDateEdit, QWidget, QFileDialog)
from PyQt5.QtCore import Qt, QDate


class SelectionDialog(QDialog):
    def __init__(self, parent, classes_list, works_dict):
        super().__init__(parent)
        self._syncing = False
        self.btn_file = None
        self.btn_done = None
        self.cb_plots = None
        self.cb_same = None
        self.work_list_widget = None
        self.date_end = None
        self.date_start = None
        self.current_works = None
        self.layout2 = None
        self.page2 = None
        self.btn_next = None
        self.class_group = None
        self.page1 = None
        self.stack = None
        self.main_layout = None
        self.setWindowTitle("Мастер настройки Insighter")
        self.setMinimumSize(500, 500)

        self.classes_list = classes_list
        self.works_dict = works_dict  # {Класс: {Название: Дата}}
        self.result_data = {}
        self._syncing = False

        if not self.classes_list:
            QMessageBox.critical(self, "Ошибка", "Список классов пуст!")
            self.reject()
            return

        self.setStyleSheet('''
            QListWidget {
                background-color: #595e5b; 
                color: white;
                border: none;
                outline: none;
            }
            
            QListWidget::item {
                padding: 5px;
            }
            
            QListWidget::indicator {
                width: 18px;
                height: 18px;
                border: 1px solid #7a7a7a; 
                background-color: white;    
                border-radius: 2px;
            }
            
            QListWidget::indicator:hover {
                border: 1px solid #ffffff;
            }
            
            QListWidget::indicator:checked {
                background-color: #303b3d;
            }
            
            QListWidget::indicator:unchecked {
                background-color: white;
            }
''')


        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.stack = QStackedWidget()

        self.page1 = QWidget()
        layout1 = QVBoxLayout(self.page1)

        layout1.addWidget(QLabel("Выберите класс:"))

        self.class_group = QButtonGroup(self)
        for i, class_name in enumerate(self.classes_list):
            rb = QRadioButton(class_name)
            self.class_group.addButton(rb, i)
            layout1.addWidget(rb)

        layout1.addStretch(1)

        self.btn_next = QPushButton("Далее →")
        self.btn_next.setFixedSize(120, 35)
        self.btn_next.setEnabled(False)
        self.btn_next.clicked.connect(self.setup_page2)

        footer1 = QHBoxLayout()
        footer1.addStretch()
        footer1.addWidget(self.btn_next)
        layout1.addLayout(footer1)

        self.class_group.buttonClicked.connect(lambda: self.btn_next.setEnabled(True))

        self.page2 = QWidget()
        self.layout2 = QVBoxLayout(self.page2)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.main_layout.addWidget(self.stack)


    def setup_page2(self):
        selected_class = self.class_group.checkedButton().text()
        self.result_data['class'] = selected_class
        self.result_data['journal_path'] = None

        self.current_works = self.works_dict.get(selected_class, {})

        if not self.current_works:
            QMessageBox.warning(self, "Ошибка", "У этого класса нет проверенных работ")
            return

        while self.layout2.count():
            item = self.layout2.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        self.layout2.addWidget(QLabel(f"<b>Класс: {selected_class}</b>"))

        dates = []
        for d_str in self.current_works.values():
            d = datetime.datetime.strptime(d_str, "%d.%m.%Y")
            dates.append(QDate(d.year, d.month, d.day))

        min_d, max_d = min(dates), max(dates)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Начало периода:"))
        self.date_start = QDateEdit(calendarPopup=True)
        self.date_start.setDate(min_d)
        row1.addWidget(self.date_start)
        self.layout2.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Конец периода:"))
        self.date_end = QDateEdit(calendarPopup=True)
        self.date_end.setDate(max_d)
        row2.addWidget(self.date_end)
        self.layout2.addLayout(row2)

        self.layout2.addSpacing(10)
        self.layout2.addWidget(QLabel("Выберите работы:"))
        self.work_list_widget = QListWidget()
        for name, d_str in self.current_works.items():
            item = QListWidgetItem(f"{name} [{d_str}]")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, d_str)
            self.work_list_widget.addItem(item)
        self.layout2.addWidget(self.work_list_widget)

        self.layout2.addSpacing(10)
        self.cb_same = QCheckBox("Считать работы одинаковыми")
        self.cb_plots = QCheckBox("Строить графики")
        self.layout2.addWidget(self.cb_same)
        self.layout2.addWidget(self.cb_plots)

        self.layout2.addSpacing(15)
        info_label = QLabel("Вы можете загрузить отчет из электронного журнала, чтобы программа "
                            "дала более подробную статистику по заданиям.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #a0a0a0; font-size: 11px;")
        self.layout2.addWidget(info_label)

        self.btn_file = QPushButton("Выбрать файл журнала (.xlsx)")
        self.btn_file.clicked.connect(self.select_excel)
        self.layout2.addWidget(self.btn_file)

        self.layout2.addStretch(1)

        self.btn_done = QPushButton("Готово")
        self.btn_done.setFixedSize(120, 35)
        self.btn_done.setEnabled(False)
        self.btn_done.clicked.connect(self.finish)

        footer2 = QHBoxLayout()
        footer2.addStretch()
        footer2.addWidget(self.btn_done)
        self.layout2.addLayout(footer2)

        self.work_list_widget.itemChanged.connect(self.sync_dates)
        self.work_list_widget.itemChanged.connect(self.validate_done_button)
        self.date_start.dateChanged.connect(self.sync_works)
        self.date_end.dateChanged.connect(self.sync_works)

        self.validate_done_button()
        self.stack.setCurrentIndex(1)


    def select_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите отчет Сетевого Города", "", "Excel Files (*.xlsx)"
        )
        if file_path:
            self.result_data['journal_path'] = file_path
            self.btn_file.setText(f"Файл выбран")
            self.btn_file.setToolTip(file_path)


    def sync_dates(self):
        if self._syncing:
            return
        self._syncing = True

        self.date_start.blockSignals(True)
        self.date_end.blockSignals(True)

        selected_dates = []
        for i in range(self.work_list_widget.count()):
            it = self.work_list_widget.item(i)
            if it.checkState() == Qt.Checked:
                date_str = str(it.data(Qt.UserRole))
                qd = QDate.fromString(date_str, "dd.MM.yyyy")
                if qd.isValid():
                    selected_dates.append(qd)

        if selected_dates:
            self.date_start.setDate(min(selected_dates))
            self.date_end.setDate(max(selected_dates))

        self.date_start.blockSignals(False)
        self.date_end.blockSignals(False)
        self._syncing = False


    def sync_works(self):
        if self._syncing:
            return
        self._syncing = True

        self.work_list_widget.blockSignals(True)

        s_date = self.date_start.date()
        e_date = self.date_end.date()

        for i in range(self.work_list_widget.count()):
            it = self.work_list_widget.item(i)
            date_str = str(it.data(Qt.UserRole))
            dt = QDate.fromString(date_str, "dd.MM.yyyy")  # правильный формат

            if dt.isValid():
                it.setCheckState(Qt.Checked if s_date <= dt <= e_date else Qt.Unchecked)

        self.work_list_widget.blockSignals(False)
        self._syncing = False
        self.validate_done_button()


    def validate_done_button(self):
        count = 0
        for i in range(self.work_list_widget.count()):
            if self.work_list_widget.item(i).checkState() == Qt.Checked:
                count += 1
        self.btn_done.setEnabled(count > 0)


    def finish(self):
        selected_names = []
        for i in range(self.work_list_widget.count()):
            it = self.work_list_widget.item(i)
            if it.checkState() == Qt.Checked:
                selected_names.append(it.text().split(" [")[0])

        self.result_data.update({
            'works': selected_names,
            'same_format': self.cb_same.isChecked(),
            'build_plots': self.cb_plots.isChecked()
        })
        self.accept()


    def get_data(self):
        return self.result_data

