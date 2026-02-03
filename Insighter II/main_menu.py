import os
import os.path
import sys
import json
import random
import traceback
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QDateEdit,
                             QFileDialog, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QDate
from window_for_rewrite import WindowForRewrite
from settings import SettingsWindow
from parser_and_validator_classes import *
from database_and_settings_classes import *
from checking import *
from logger import *
from clearmodes import *
from users_dialogs import *
from generation_classes import *
from tg_bot import *
from user_dialogs_2 import *
import threading


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

        self.first_run_dialog = None
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
        self.generation_button.clicked.connect(self.run_generation)
        self.bot_control_button.clicked.connect(self.run_bot_control)

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
            
            QLineEdit {
            background-color: #262626;
            border: 1px solid #444444;
            border-radius: 3px;
            }
            
            QCheckBox {
                spacing: 8px;
                color: #ffffff;
                font-weight: bold;
            }
    
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #444444;
                background-color: #303b3d;
            }
    
            QCheckBox::indicator:hover {
                border: 2px solid #557A95;
            }
    
            QCheckBox::indicator:checked {
                background-color: #557A95;
                border: 2px solid #557A95;
            }
    
            QCheckBox::indicator:checked:hover {
                background-color: #6fa3c6;
            }
    
            QCheckBox:disabled {
                color: #888888;
            }
    
            QCheckBox::indicator:disabled {
                background-color: #222222;
                border: 2px solid #333333;
            }
            
                QRadioButton {
            spacing: 8px;
            color: #ffffff;
            font-weight: bold;
            }
            
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 10px; 
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
                border: 2px solid #6fa3c6;
            }
            
            QRadioButton:disabled {
                color: #888888;
            }
            
            QRadioButton::indicator:disabled {
                background-color: #222222;
                border: 2px solid #333333;
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
                    self.show()
                    return

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
            data['absents_file'] = 'auto'
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

        dbclr = Database()
        dbclr.connect()
        cdb = DatabaseChecking(dbclr)

        dialog = ClearDatabaseDialog(dbclr, cdb, parent=self)

        if dialog.exec() != QDialog.Accepted:
            self.show()
            return

        data = dialog.data
        clear = Clear(dbclr)

        try:
            if data["mode"] == "Сброс до начальной конфигурации":
                clear.delete_system_files()
                print('Программа сброшена. Перезапустите программу.')
                self.close()
                return

            elif data["mode"] == "Очистить все данные в базе":
                clear.delete_database_file()
                print("База данных полностью очищена.")
                self.show()
                return

            table = data["table"]

            if data["scope"] == "Очистить все данные в таблице":
                clear.delete_by_field(table)
                print("Таблица успешно очищена.")

            else:
                if table == "classes":
                    clear.delete_by_field(table, "class_name", data["class"])
                    print("Класс удалён.")


                elif table == "works":
                    class_name = data["class"]
                    work_name = data["work"]
                    class_id = cdb.get_class_id_by_name(class_name)
                    if class_id is None:
                        print(f"Класс '{class_name}' не найден")
                        self.show()
                        return
                    clear.delete_work(class_id, work_name)
                    print("Работа удалена.")

        except Exception as e:
            log.log("clear_error", e)
            print("Ошибка при очистке.")
            if Settings().show_warnings:
                raise

        log.log_date('end_function_run_clear_database')
        self.show()


    def run_generation(self):
        self.hide()

        dbg = Database()
        dbg.connect()
        gen_db = DatabaseChecking(dbg)
        list_of_classes = gen_db.get_classes()

        data_from_patterns = read_pattern()

        dialog = GenerationModeDialog(
            classes=([] if not list_of_classes else list_of_classes),
            manual_dialog_cls=ManualGenerationDialog,
            fast_dialog_cls=FastGenerationDialog,
            pattern_dialog_cls=PatternGenerationDialog,
            patterns=data_from_patterns,
            parent=self
        )

        if dialog.exec() != QDialog.Accepted:
            self.show()
            return

        data = dialog.data
        print(data)

        if data['mode'] == 'use_pattern':
            generator = Generator(data)
            generator.run_generation()
            print(f'Генерация успешно завершена. Все файлы и папки сохранены в рабочей директории.')
            dbg.close()
            self.show()
            return

        parseui = ParserUIData(data, dbg)

        if parseui.mode == 'manual':
            parseui.parse_dict_manual()

        elif parseui.mode == 'fast':
            parseui.parse_dict_fast()

        elif parseui.mode == 'new_pattern':
            parseui.parse_dict_manual()
            parsed_gen_data = parseui.get_data()
            save_pattern(data["pattern_name"], parsed_gen_data)
            print('Шаблон успешно сохранен, теперь он доступен в меню.')
            self.show()
            return


        parsed_gen_data = parseui.get_data()
        generator = Generator(parsed_gen_data)
        generator.run_generation()
        print(f'Генерация успешно завершена. Все файлы и папки сохранены в рабочей директории.')
        dbg.close()
        self.show()
        return


    def run_bot_control(self):
        BOT_TOKEN = '8529361701:AAHNWQ0KZDRHOr2-0GfdmMNhAsrO8bFe_sM'

        self.hide()

        if is_tg_first_launch():

            code = str(random.randint(10000, 99999))

            dialog = FirstRunTelegramSetupDialog(code, self)
            dialog.exec()

            from telegram.bot_service import TelegramBotService

            self.bot_service = TelegramBotService(
                token=BOT_TOKEN,
                auth_code=code
            )

            import threading
            self.bot_thread = threading.Thread(
                target=self.bot_service.run,
                daemon=True
            )
            self.bot_thread.start()



