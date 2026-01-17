from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QPushButton, QRadioButton, QButtonGroup,
    QScrollArea, QWidget
)
from PyQt5.QtCore import Qt
from Database_Settings_classes import Settings

class CheckWorksDialog(QDialog):
    def __init__(self, cdb, parent=None):
        super().__init__(parent)

        self.cdb = cdb
        self.step = 0
        self.data = {}
        self.group = None

        self.setWindowTitle("Проверка работ")

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

# def run_check_works(self):
#     self.hide()
#     log = Logger(Settings().developer_mode)
#     log.log_date('start_function_run_check_works')
#     database_for_func = Database()
#     cdb = DatabaseChecking(database_for_func)
#     database_for_func.connect()
#     chosen_class_name, _ = print_menu(cdb.get_classes(), 'Выберите класс:', 'У вас нет добавленных классов. Используйте режим перезаписи, чтобы добавить классы')
#     log.log('chosen_class_name', chosen_class_name)
#     if not chosen_class_name:
#         self.show()
#         log.log_date('there_are_no_classes_error')
#         return
#
#     works = cdb.get_works_by_class(chosen_class_name)
#     log.log('works', works)
#     parsed = cdb.parse_names(works)
#     log.log('parsed', parsed)
#
#     chosen_work, _ = print_menu(parsed, 'Выберите работу:', 'У вас нет непроверенных работ.')
#     log.log('chosen_work', chosen_work)
#     if not chosen_work:
#         log.log_date('there_are_no_works_error')
#         self.show()
#         return
#
#     big_data = cdb.get_all_data(chosen_class_name, chosen_work.split(' за ')[0])
#     log.log('big_data', big_data)
#     chck = Checking(big_data)
#     chck.parse_big_data()
#     parsed_data = chck.checking_works()
#     log.log('parsed_data', parsed_data)
#     list_of_absents_names = chck.get_absents(database_for_func)
#     log.log('list_of_absents_names', list_of_absents_names)
#     final_dict = chck.get_grades(parsed_data)
#     log.log('final_dict', final_dict)
#
#     dict_for_write = {}
#     absents_dict = {}
#     for student_data in final_dict.values():
#         key = f"{student_data['surname']} {student_data['name']}" #если нужно помнять местами имя и фамилию
#         dict_for_write[key] = student_data['grade']
#     log.log('dict_for_write', dict_for_write)
#     for student in list_of_absents_names:
#         key = f'{student[2]} {student[1]}'
#         absents_dict[key] = 'отсутствовал(а)'
#         final_dict[student[0]] = {'score': None, 'tg_id': student[3], 'name': student[1], 'surname': student[2], 'grade': None}
#     dict_for_write.update(absents_dict)
#     log.log('updated_dict_for_write', dict_for_write)
#     database_for_func.connect()
#     cdb.save_final_results(chosen_class_name, chosen_work.split(' за ')[0].strip(), final_dict)
#     cdb.set_work_status_by_name(chosen_class_name, chosen_work.split(' за ')[0].strip(), 'checked')
#     print('Работы проверены и результат успешно записан в базу данных.')
#
#     lst = ['По умолчанию', 'По оценкам, сначала лучшие', 'По оценкам, сначала худшие', 'По фамилиям']
#     _, chosed_sort_mode = print_menu(lst, 'Выберите режим сортировки:')
#     log.log('chosed_sort_mode', chosed_sort_mode)
#     wonderful_sorted_dict = chck.sort_data(dict_for_write, chosed_sort_mode)
#     log.log('wonderful_sorted_dict', wonderful_sorted_dict)
#     if Settings().format_by_default == 'ask' or Settings().format_by_default == 'спрашивать каждый раз':
#         chosed_format, _ = print_menu(['.txt', '.csv'], 'Выберите формат файла')
#         log.log('chosed_format', chosed_format)
#     else:
#         chosed_format = Settings().format_by_default
#
#     if not chosed_format:
#         log.log_date('format_error')
#         self.show()
#         return
#
#     work_filename = f'{chosen_work} класса {chosen_class_name}{chosed_format}'
#     log.log('work_filename', work_filename)
#     full_path = os.path.join(os.getcwd(), work_filename)
#     if Settings().saving_all_files_in_one_folder:
#         full_path = os.path.join(Settings().saving_all_files_in_one_folder, work_filename)
#     log.log('full_path', full_path)
#     if chosed_format == '.txt':
#         chck.save_file_txt(full_path, wonderful_sorted_dict)
#     elif chosed_format == '.csv':
#         chck.save_file_csv(full_path, wonderful_sorted_dict)
#     else:
#         log.log_date('file_format_error')
#         if Settings().show_warnings:
#             print('Неправильный формат файла.')
#         self.show()
#         return
#     print(f'Файл успешно сохранен по пути: {full_path}.')
#     if Settings().automatically_file_opening:
#         os.startfile(full_path)
#     elif input(f'Открыть файл {full_path}? ').lower().strip() in ('lf', 'да', '1'):
#         os.startfile(full_path)
#
#     log.log_date('end_function_run_check_works')
#     database_for_func.close()
#     self.show()