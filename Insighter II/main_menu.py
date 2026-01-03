import os.path
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QDateEdit,
                             QFileDialog, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QDate
from window_for_rewrite import WindowForRewrite
from settings import SettingsWindow
from Parser_Validator_classes import *
from Database_Settings_classes import *
from checking import *
import json

def save_sys_json(data: dict):
    path = r'system_files/sys.json'
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e)


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
        self.check_works_button.clicked.connect(self.run_check_works)


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

        input_data = self.rewrite_window.result_data
        sys_data = load_sys_json()
        data = merge_with_sys_json(input_data, sys_data)

        validator = Validator(data)
        ok, errors = validator.validate()

        if ok:
            parser = Parser(validator.validate_answers_file(), validator.validate_grades_file(), validator.absents_file,
                validator.works_folder, validator.date, validator.class_name)
            class_name = parser.parse_class_name()
            date = parser.parse_date()
            answers_string = parser.parse_answers_dict()
            grades_string = parser.parse_grades_dict()
            try:
                work_name, dict_with_student_answers, students_list = parser.parse_works_folder()
            except Exception as e:
                print('Возникла ошибка при парсинге папки с работами.')
                if Settings().show_warnings:
                    print(f'Ошибка:{e}')

            dtb = Database()
            dtb.connect()
            work_id = dtb.save_work(work_name, date, class_name, answers_string, grades_string, 'raw')
            dtb.add_students_from_list(class_name, students_list)
            dtb.add_submissions_from_answers(class_name, work_id, dict_with_student_answers)

            absents_ids = set()

            if validator.absents_file is not None and validator.absents_file != "auto":
                absent_names = parser.parse_absents_file()
                absents_ids = set(absent_names)

            elif validator.absents_file == "auto":
                all_students = dtb.get_students_of_class(class_name)
                submitted_students = dtb.get_students_with_submission(work_id)
                absents_ids = all_students - submitted_students
            class_name = parser.parse_class_name()
            dtb.set_absents_for_work(work_id, class_name, absents_ids)




            dtb.close()
            save_sys_json(data)
            print('Данные успешно сохранены.')
            self.show()
            return

        self.handle_errors(errors)


    def handle_errors(self, errors):
        self.rewrite_window.hide()

        print("\nОбнаружены ошибки:\n")
        for err in errors:
            print(err)

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



    def run_check_works(self):
        try:
            self.hide()
            database_for_func = Database()
            cdb = DatabaseChecking(database_for_func)
            database_for_func.connect()
            chosen_class_name, _ = print_menu(cdb.get_classes(), 'Выберите класс:', 'У вас нет добавленных классов. Используйте режим перезаписи, чтобы добавить классы')
            if chosen_class_name is None:
                self.show()
                return

            works = cdb.get_works_by_class(chosen_class_name)
            parsed = cdb.parse_names(works)

            if not parsed:
                self.show()
                return

            chosen_work, _ = print_menu(cdb.parse_names(cdb.get_works_by_class(chosen_class_name)), 'Выберите работу:', 'У вас нет непроверенных работ.')
            if not chosen_work:
                self.show()
                return

            print(chosen_work)
            big_data = cdb.get_all_data(chosen_class_name, chosen_work.split(' за ')[0])
            print(*big_data, sep='\n')
            chck = Checking(big_data)
            chck.parse_big_data()
            parsed_data = chck.checking_works()
            print(parsed_data)
            sdb = Database()
            list_of_absents_names = chck.get_absents(sdb)
            print(list_of_absents_names)
            final_dict = chck.get_grades(parsed_data)

            dict_for_write = {}
            absents_dict = {}
            for student_data in final_dict.values():
                key = f'{student_data['surname']} {student_data['name']}'
                dict_for_write[key] = student_data['grade']
            for student in list_of_absents_names:
                key = f'{student[2]} {student[1]}'
                absents_dict[key] = 'отсутствовал(а)'
                final_dict[student[0]] = {'score': None, 'tg_id': student[3], 'name': student[1], 'surname': student[2], 'grade': None}
            dict_for_write.update(absents_dict)
            print('Final dict:', final_dict)
            #final_dict - словарь для записи в БД и для tg-бота, dict_for_write - словарь для записи в файл, wonderful_sorted_dict - отсортированный словарь для записи в файл
            cdb.save_final_results(chosen_class_name, chosen_work.split(' за ')[0].strip(), final_dict)
            cdb.set_work_status_by_name(chosen_class_name, chosen_work.split(' за ')[0].strip(), 'checked')
            print(dict_for_write)
            print('Работы проверены и результат успешно записан в базу данных.')
            lst = ['По умолчанию', 'По оценкам, сначала лучшие', 'По оценкам, сначала худшие', 'По фамилиям']
            _, chosed_sort_mode = print_menu(lst, 'Выберите режим сортировки:')
            wonderful_sorted_dict = chck.sort_data(dict_for_write, chosed_sort_mode)
            if Settings().format_by_default == 'спрашивать каждый раз':
                chosed_format, _ = print_menu(['.txt', '.csv'], 'Выберите формат файла')
            else:
                chosed_format = Settings().format_by_default

            if not chosed_format:
                self.show()
                return

            work_filename = f'{chosen_work} класса {chosen_class_name}{chosed_format}'
            full_path = os.path.join(os.getcwd(), work_filename)
            if Settings().saving_all_files_in_one_folder:
                full_path = os.path.join(Settings().saving_all_files_in_one_folder, work_filename)

            if chosed_format == '.txt':
                chck.save_file_txt(full_path, wonderful_sorted_dict)
            elif chosed_format == '.csv':
                chck.save_file_csv(full_path, wonderful_sorted_dict)
            else:
                if Settings().show_warnings:
                    print('Неправильный формат файла.')
                self.show()
                return
            print(f'Файл успешно сохранен по пути: {full_path}.')
            if Settings().automatically_file_opening:
                os.startfile(full_path)
            elif input(f'Открыть файл {full_path}?').lower().strip() in ('lf', 'да', '1'):
                os.startfile(full_path)


            database_for_func.close()
            self.show()

        except Exception as e:
            print(e)


