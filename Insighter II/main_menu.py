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
from random_file_for_testing import *
from clearmodes import *
import json
import random
import traceback
from usersDialogs import *


def excepthook(exc_type, exc_value, exc_tb):
    traceback.print_exception(exc_type, exc_value, exc_tb)
    sys.__excepthook__(exc_type, exc_value, exc_tb)

sys.excepthook = excepthook

def save_sys_json(data: dict):
    path = r'system_files/sys.json'
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e)


class MainMenu(QWidget):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

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
        self.clear_button = QPushButton("Очистка", self)
        self.settings_button = QPushButton("Настройки", self)


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
        self.clear_button.setFixedSize(230, 60)

        self.rewrite_button.clicked.connect(self.run_rewrite)
        self.settings_button.clicked.connect(self.run_settings)
        self.check_works_button.clicked.connect(self.run_check_works)
        self.clear_button.clicked.connect(self.run_clear_database)

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
        grid.addWidget(self.help_button, 4, 2)
        grid.addWidget(self.clear_button, 4, 1)
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
        log = Logger(Settings.developer_mode)
        log.log_date('start_function_on_rewrite_finished')
        input_data = self.rewrite_window.result_data
        log.log('input_data', input_data)
        sys_data = load_sys_json()
        log.log('sys_data', sys_data)
        data = merge_with_sys_json(input_data, sys_data)
        log.log('data', data)

        validator = Validator(data)
        ok, errors = validator.validate()
        log.log('ok', ok)
        log.log('errors', errors)

        if ok:
            parser = Parser(validator.validate_answers_file(), validator.validate_grades_file(), validator.absents_file,
                validator.works_folder, validator.date, validator.class_name)
            class_name = parser.parse_class_name()
            log.log('class_name', class_name)
            date = parser.parse_date()
            log.log('date', date)
            answers_string = parser.parse_answers_dict()
            log.log('answers_string', answers_string)
            grades_string = parser.parse_grades_dict()
            log.log('grades_string', grades_string)
            try:
                work_name, dict_with_student_answers, students_list = parser.parse_works_folder()
            except Exception as e:
                print('Возникла ошибка при парсинге папки с работами.')
                if Settings().show_warnings:
                    print(f'Ошибка:{e}')
                    log.log('error_parse_folder', e)

            dtb = Database()
            dtb.connect()
            work_id = dtb.save_work(work_name, date, class_name, answers_string, grades_string, 'raw')
            log.log('work_id', work_id)
            dtb.add_students_from_list(class_name, students_list)
            dtb.add_submissions_from_answers(class_name, work_id, dict_with_student_answers)

            absents_ids = set()

            if validator.absents_file is not None and validator.absents_file != "auto":
                absent_names = parser.parse_absents_file()
                log.log('absent_names', absent_names)
                absents_ids = set(absent_names)

            elif validator.absents_file == "auto":
                all_students = dtb.get_students_of_class(class_name)
                log.log('all_students', all_students)
                submitted_students = dtb.get_students_with_submission(work_id)
                log.log('submitted_students', submitted_students)
                absents_ids = all_students - submitted_students
                log.log('absents_ids', absents_ids)
            class_name = parser.parse_class_name()
            log.log('class_name', class_name)
            dtb.set_absents_for_work(work_id, class_name, absents_ids)


            dtb.close()
            save_sys_json(data)
            print('Данные успешно сохранены.')
            log.log_date('end_function_on_rewrite_finished')
            self.show()
            return

        self.handle_errors(errors)


    def handle_errors(self, errors):
        log = Logger(Settings().developer_mode)
        self.rewrite_window.hide()
        log.log_date('start_function_handle_errors')
        print("\nОбнаружены ошибки:\n")
        for err in errors:
            print(err)

        self.show()
        log.log_date('end_function_handle_errors')
        return


    def on_settings_finished(self):
        self.show()


    def run_rewrite(self):
        log = Logger(Settings().developer_mode)
        self.hide()
        log.log_date('start_function_run_rewrite')
        self.rewrite_window = WindowForRewrite()
        self.rewrite_window.finished.connect(self.on_rewrite_finished)
        self.rewrite_window.show()


    def run_settings(self):
        log = Logger(Settings().developer_mode)
        self.hide()
        log.log_date('start_function_run_settings')
        self.settings_window = SettingsWindow()
        self.settings_window.finished.connect(self.on_settings_finished)
        self.settings_window.show()

    def run_check_works(self):
        self.setEnabled(False)

        log = Logger(Settings().developer_mode)
        log.log_date('start_function_run_check_works')

        database_for_func = Database()
        cdb = DatabaseChecking(database_for_func)
        database_for_func.connect()

        dialog = CheckWorksDialog(cdb, parent=self)

        if dialog.exec() != QDialog.Accepted:
            self.setEnabled(True)
            self.show()
            log.log_date('dialog_rejected')
            return

        chosen_class_name = dialog.data["class"]
        chosen_work = dialog.data["work"]
        chosed_sort_mode = dialog.data["sort_mode"]

        log.log('chosen_class_name', chosen_class_name)
        log.log('chosen_work', chosen_work)
        log.log('chosed_sort_mode', chosed_sort_mode)

        big_data = cdb.get_all_data(
            chosen_class_name,
            chosen_work.split(' за ')[0]
        )

        chck = Checking(big_data)
        chck.parse_big_data()
        parsed_data = chck.checking_works()
        list_of_absents_names = chck.get_absents(database_for_func)
        final_dict = chck.get_grades(parsed_data)

        dict_for_write = {}
        absents_dict = {}

        for student_data in final_dict.values():
            key = f"{student_data['surname']} {student_data['name']}"
            dict_for_write[key] = student_data['grade']

        for student in list_of_absents_names:
            key = f'{student[2]} {student[1]}'
            absents_dict[key] = 'отсутствовал(а)'
            final_dict[student[0]] = {
                'score': None,
                'tg_id': student[3],
                'name': student[1],
                'surname': student[2],
                'grade': None
            }

        dict_for_write.update(absents_dict)

        database_for_func.connect()
        cdb.save_final_results(
            chosen_class_name,
            chosen_work.split(' за ')[0].strip(),
            final_dict
        )
        cdb.set_work_status_by_name(
            chosen_class_name,
            chosen_work.split(' за ')[0].strip(),
            'checked'
        )

        wonderful_sorted_dict = chck.sort_data(
            dict_for_write,
            chosed_sort_mode
        )

        chosed_format = dialog.data["format"]
        open_file = dialog.data["open_file"]

        work_filename = f'{chosen_work} класса {chosen_class_name}{chosed_format}'
        log.log('work_filename', work_filename)

        full_path = os.path.join(os.getcwd(), work_filename)
        if Settings().saving_all_files_in_one_folder:
            full_path = os.path.join(Settings().saving_all_files_in_one_folder, work_filename)

        log.log('full_path', full_path)

        if chosed_format == '.txt':
            chck.save_file_txt(full_path, wonderful_sorted_dict)
        elif chosed_format == '.csv':
            chck.save_file_csv(full_path, wonderful_sorted_dict)
        else:
            log.log_date('file_format_error')
            print('Неправильный формат файла.')
            self.setEnabled(True)
            self.show()
            return

        print(f'Файл успешно сохранен по пути: {full_path}.')

        if open_file:
            os.startfile(full_path)

        self.setEnabled(True)
        self.show()
        return

    def run_clear_database(self):
        self.hide()
        log = Logger(Settings().developer_mode)
        log.log_date('start_function_run_clear_database')
        modes_of_clear = ['Очистка данных таблиц', 'Очистить все данные в базе', 'Сборс до начальной конфигурации']
        chosen_clear_mode, _ = print_menu(modes_of_clear, 'Выберите режим для очистки. Если вы понятия не имеете, что будет удалено, прочитайте инструкцию, удаленные данные не могут быть восстановлены.')
        log.log('chosen clear mode', chosen_clear_mode)

        if not chosen_clear_mode:
            self.show()
            return

        db = Database()
        db.connect()
        clear = Clear(db)
        if chosen_clear_mode == 'Очистить все данные в базе':
            input('Вы в режиме полной очистки базы данных. После удаления данные не могут быть восстановлены. Нажмите Enter, чтобы продолжить. ')
            missclick_psw = random.randint(1000, 9999)
            log.log('missclick_psw', missclick_psw)
            clear.create_delete_file(missclick_psw)
            user_psw = input('Программа создала файл delete.txt в рабочей директории. Введите пароль оттуда для подтверждения очистки: ')
            log.log('user_psw', user_psw)
            if not user_psw == str(missclick_psw):
                print('Вы ввели неверный пароль. База данных не была очищена.')
                self.show()
                return
            input('Вы уверены? После нажатия Enter база данных будет очищена. ')
            try:
                clear.delete_database_file()
            except Exception as e:
                log.log('error_clear_db', e)
                print('Ошибка при удалении базы данных.', end='')
                if Settings().show_warnings:
                    print(e)
            print('База данных успешно удалена. Перезапустите программу.')
            log.log_date('end_function_run_clear_database')
            self.close()

        elif chosen_clear_mode == 'Очистка данных таблиц':
            chosen_table, _ = print_menu(clear.ALLOWED_TABLES, 'Вы в режиме очистки таблиц. Выберите таблицу для очистки.')

            if not chosen_table:
                self.show()
                return

            chosen_list_clear = ['Очистить все данные в таблице', 'Очистить конкретные данные в таблице']
            chosen_clear_second_mode, _ = print_menu(chosen_list_clear, 'Вы хотите очистить таблицу целиком или конкретные данные?')

            if not chosen_list_clear:
                self.show()
                return

            if chosen_clear_second_mode == 'Очистить все данные в таблице':
                user_input_clear_chck = input('Введите любое натуральное трехзначное число для подтвержения очистки.\n')
                if user_input_clear_chck.isdigit() and len(user_input_clear_chck) == 3:
                    input('Вы уверены? После нажатия Enter данные будут удалены. ')
                    clear.delete_by_field(chosen_table)
                    print('Данные успешно удалены.')
                    self.show()
                    return
                else:
                    print('Вы ввели неверное число.')
                    self.show()
                    return

            elif chosen_clear_second_mode == 'Очистить конкретные данные в таблице':
                database_clear = DatabaseChecking(db)
                if chosen_table == 'classes':
                    all_classes_for_clear = database_clear.get_classes()
                    chosen_class, _ = print_menu(all_classes_for_clear, 'Выберите класс для очистки:', 'У вас нет классов.')

                    if not chosen_class:
                        self.show()
                        return

                    user_input_clear_chck = input('Введите любое натуральное трехзначное число для подтвержения очистки.\n')
                    if user_input_clear_chck.isdigit() and len(user_input_clear_chck) == 3:
                        input('Вы уверены? После нажатия Enter данные будут удалены. ')
                        clear.delete_by_field(chosen_table, 'class_name', chosen_class)
                        print('Класс успешно удален.')
                        self.show()
                        return
                    else:
                        print('Вы ввели неверное число.')
                        self.show()
                        return

                elif chosen_table == 'works':
                    all_classes_for_clear = database_clear.get_classes()
                    chosen_class, _ = print_menu(all_classes_for_clear, 'Выберите класс, работы которого хотите очистить:', 'У вас нет классов.')

                    if not chosen_class:
                        self.show()
                        return

                    all_works_of_class = database_clear.get_works_by_class(chosen_class, status='*')
                    chosen_clear_work, _ = print_menu(all_works_of_class, 'Выберите работу для очистки:', 'Работ нет, удалять нечего.')

                    if not chosen_clear_work:
                        self.show()
                        return

                    user_input_clear_chck = input('Введите любое натуральное трехзначное число для подтвержения очистки.\n')
                    if user_input_clear_chck.isdigit() and len(user_input_clear_chck) == 3:
                        input('Вы уверены? После нажатия Enter данные будут удалены. ')
                        clear.delete_by_field(chosen_table, 'class_name', chosen_class)
                        print('Класс успешно удален.')
                        self.show()
                        return
                    else:
                        print('Вы ввели неверное число.')
                        self.show()
                        return








