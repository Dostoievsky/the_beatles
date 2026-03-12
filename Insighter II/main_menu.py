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
from settings_class import Settings, is_first_launch
from checking import *
from logger import *
from clearmodes import *
from users_dialogs import *
from generation_classes import *
from tg_bot import *
from tg_dialogs import *
from random_call_dialog import *
import threading
from database_class import Database
from settings_class import Settings
from statistics_dialogs import *
from statistics_class import StatisticsParser

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
        self.bot_service = None
        self.bot_thread = None
        self.setWindowTitle("Main Menu")
        self.resize(550, 340)

        label = QLabel("Выберите режим:", self)

        grid = QGridLayout()
        grid.setSpacing(10)

        self.check_works_button = QPushButton("Проверка работ", self)
        self.rewrite_button = QPushButton("Перезапись данных", self)
        self.generation_button = QPushButton("Генерация", self)
        self.search_button = QPushButton("Поиск по работам", self)
        self.statistics_class_button = QPushButton("Статистика по работам", self)
        self.statistics_student_button = QPushButton("Статистика по ученику", self)
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
        self.statistics_class_button.setFixedSize(230, 60)
        self.statistics_student_button.setFixedSize(230, 60)
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
        self.random_call_button.clicked.connect(self.run_random_call)
        self.statistics_class_button.clicked.connect(self.run_statistics)

        grid.addWidget(self.check_works_button, 1, 0)
        grid.addWidget(self.rewrite_button, 1, 1)
        grid.addWidget(self.generation_button, 1, 2)
        grid.addWidget(self.search_button, 2, 0)
        grid.addWidget(self.statistics_class_button, 2, 1)
        grid.addWidget(self.statistics_student_button, 2, 2)
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

        db = Database()
        db.connect()

        dialog = CheckWorksDialog(db, parent=self)

        if dialog.exec() != QDialog.Accepted:
            self.setEnabled(True)
            self.show()
            log.log_date('dialog_rejected')
            db.close()
            return

        chosen_class_name = dialog.data["class"]
        chosen_work = dialog.data["work"]
        chosed_sort_mode = dialog.data["sort_mode"]

        log.log('chosen_class_name', chosen_class_name)
        log.log('chosen_work', chosen_work)
        log.log('chosed_sort_mode', chosed_sort_mode)

        big_data = db.get_all_data(
            chosen_class_name,
            chosen_work.split(' за ')[0]
        )

        chck = Checking(big_data)
        chck.parse_big_data()
        parsed_data = chck.checking_works()
        log.log('parsed_data', parsed_data)

        list_of_absents_names = chck.get_absents(db)
        final_dict = chck.get_grades(parsed_data)
        log.log('final_dict', final_dict)

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
        db.connect()
        db.save_final_results(chosen_class_name, chosen_work.split(' за ')[0].strip(), final_dict)

        work_name = chosen_work.split(' за ')[0].strip()
        work_id = db.get_work_id_by_class_and_name(chosen_class_name, work_name)
        db.save_statistics_results(work_id, final_dict)

        db.set_work_status_by_name(chosen_class_name, chosen_work.split(' за ')[0].strip(),'checked')

        wonderful_sorted_dict = chck.sort_data(dict_for_write, chosed_sort_mode)

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
            db.close()
            return

        print(f'Файл успешно сохранен по пути: {full_path}.')

        if open_file:
            os.startfile(full_path)

        db.close()
        self.setEnabled(True)
        self.show()


    def run_clear_database(self):
        self.hide()
        log = Logger(Settings().developer_mode)
        log.log_date('start_function_run_clear_database')

        db = Database()
        db.connect()

        dialog = ClearDatabaseDialog(db, parent=self)

        if dialog.exec() != QDialog.Accepted:
            self.show()
            db.close()
            return

        data = dialog.data
        clear = Clear(db)

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

                    class_id = db.get_class_id(class_name)
                    if class_id is None:
                        print(f"Класс '{class_name}' не найден")
                        self.show()
                        db.close()
                        return

                    clear.delete_work(class_id, work_name)
                    print("Работа удалена.")

        except Exception as e:
            log.log("clear_error", e)
            print("Ошибка при очистке.")
            if Settings().show_warnings:
                raise

        db.close()
        log.log_date('end_function_run_clear_database')
        self.show()


    def run_generation(self):
        self.hide()
        log = Logger(Settings.developer_mode)
        log.log_date('start_function_run_generation')
        dbg = Database()
        dbg.connect()
        list_of_classes = dbg.get_classes()
        log.log('list_of_classes', list_of_classes)
        data_from_patterns = read_pattern()
        log.log('data_from_patterns', data_from_patterns)
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
        log.log('dialog_data', data)

        if data['mode'] == 'use_pattern':
            log.log('mode', 'use_pattern')
            generator = Generator(data)
            generator.run_generation()
            print(f'Генерация успешно завершена. Все файлы и папки сохранены в рабочей директории.')
            dbg.close()
            self.show()
            return

        parseui = ParserUIData(data, dbg)

        if parseui.mode == 'manual':
            log.log('mode', 'manual')
            parseui.parse_dict_manual()

        elif parseui.mode == 'fast':
            log.log('mode', 'fast')
            parseui.parse_dict_fast()

        elif parseui.mode == 'new_pattern':
            log.log('mode', 'new_pattern')
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
        log.log_date('end_function_run_generation')
        return


    def run_bot_control(self):
        self.hide()
        log = Logger(Settings().developer_mode)
        log.log_date('start_function_run_bot_control')
        db = Database()
        db.connect()
        classes = db.get_classes() or []
        log.log('classes', classes)

        if not classes:
            db.close()
            QMessageBox.information(
                self,
                "Нет классов",
                "У вас нет добавленных классов. Добавьте класс с помощью режима перезаписи"
            )
            log.log('no_classes_error', True)
            return
        try:
            bot_token = '8529361701:AAHNWQ0KZDRHOr2-0GfdmMNhAsrO8bFe_sM'
            if self.bot_service is None:
                self.bot_service = TelegramBotService(token=bot_token, db_path=db.db_path)
                self.bot_service.start()

            db.close()

            dialog = TelegramControlDialog(classes, self.bot_service, parent=self)
            dialog.exec()
        except Exception as e:
            print('Вероятно, бот потерял соединение с сервером. Проверьте интернет.')
            log.log('error', e)
        finally:
            log.log_date('end_function_run_bot_control')
            self.show()


    def run_random_call(self):
        self.hide()
        log = Logger(Settings().developer_mode)
        log.log_date('start_function_run_random_call')
        db = Database()
        db.connect()
        all_classes = db.get_classes()
        log.log('all_classes', all_classes)
        classes_students = {}

        for class_name in all_classes:
            students_of_class = db.get_students_of_class(class_name, mode='names')
            log.log('students_of_class', students_of_class)
            classes_students[str(class_name)] = list(students_of_class)
            log.log('classes_students', classes_students)


        if not classes_students:
            QMessageBox.warning(self, "Нет классов", "У вас нет классов")
            log.log_date('no_classes_error', True)
            return

        dialog = RandomCallDialog(classes_students, self)
        dialog.exec_()
        log.log_date('end_function_run_random_call')

        self.show()


    def run_statistics(self):
        self.hide()
        log = Logger(Settings.developer_mode)
        log.log_date('start_function_statistics')
        db = Database()
        db.connect()

        classes = db.get_classes()
        log.log('classes', classes)
        works_dict = {}
        for class_name in classes:
            list_of_works = [l[3] for l in db.get_works_by_class(class_name, status='checked')]
            dct = {}
            for work in list_of_works:
                dct[work] = db.get_date_of_work(class_name, work)
            works_dict[class_name] = dct
        log.log('works_dict', works_dict)


        dialog = SelectionDialog(self, classes, works_dict)
        if dialog.exec_():
            dialog_data = dialog.get_data()
        log.log('dialog_data', dialog_data)

        klass = dialog_data['class']
        works = dialog_data['works']
        file_name = dialog_data['journal_path']
        flag_format = dialog_data['same_format']
        flag_plots = dialog_data['build_plots']
        total_students = db.get_total_students(klass)

        log.log('klass', klass)
        log.log('works', works)
        log.log('file_name', file_name)
        log.log('flag_format', flag_format)
        log.log('flag_plots', flag_plots)
        log.log('total_students', total_students)

        res_dct, grades_dct = db.get_data_for_statistics(work, klass)


        if len(works) == 1 and not file_name:
            stats = StatisticsParser(res_dct, grades_dct)
            log.log('res_dct', res_dct)
            log.log('grades_dct', grades_dct)

            avg = stats.get_average()
            log.log('avg', avg)
            median = stats.get_median()
            log.log('median', median)
            grades_distribution = stats.get_grades_distribution()
            log.log('grades_distribution', grades_distribution)
            best_students, worst_students = stats.get_the_best_the_worst_students_results()
            log.log('best_students', best_students)
            log.log('worst_students', worst_students)
            tasks_distribution = stats.convertage_to_percentages(total_students)
            log.log('tasks_distribution', tasks_distribution)
            recomendations = stats.get_recomdendations_standart(tasks_distribution)
            log.log('recomendations', recomendations)
            concp1, concp2 = stats.grades_dict, tasks_distribution
            log.log('concp1', concp1)
            log.log('concp2', concp2)
            conclusion = stats.get_brief_conclusion(concp1, concp2)
            log.log('conclusion', conclusion)
            absents_not_parsed = db.get_absents(klass, work)
            best_result, worst_results = stats.get_best_worst_results()
            log.log('best_results', best_result)
            log.log('worst_results', worst_results)
            absents = 0 if not absents_not_parsed else len(absents_not_parsed.split(','))
            log.log('absents', absents)

            if Settings().saving_statistics_in_unque_files:
                file_name = f'Статистика (без журнала) по классу {klass} по работе {work}.txt'
            else:
                file_name = 'Статистика.txt'
            path = os.path.join(os.getcwd(), file_name) if not Settings().saving_all_files_in_one_folder else (
                os.path.join(Settings().saving_all_files_in_one_folder, file_name))
            log.log('path', path)

            with open(path, 'w', encoding='utf-8') as stat_file:
                print(f'Статистика (без журнала) по классу {klass} по работе "{work}"', file=stat_file)
                print(file=stat_file)
                print(f'Средний балл по классу: {avg}', file=stat_file)
                print(f'Медианный балл по классу: {median}', file=stat_file)
                print(f'Отсутствоваших учеников: {absents}', file=stat_file)
                print(file=stat_file)
                print('Распределение оценок по классу:', file=stat_file)
                for k, v in grades_distribution.items():
                    print(f'Оценок {k}: {v}', file=stat_file)
                print(f'Больше всего оценок: {max(grades_distribution, key=grades_distribution.get)}', file=stat_file)
                print(file=stat_file)
                print(f'Лучшие ученики по классу: {", ".join(list(best_students.keys()))}', file=stat_file)
                print(f'Худшие ученики по классу: {", ".join(list(worst_students.keys()))}', file=stat_file)
                print(f'Лучший результат по классу: оценка {best_result[1]} за [{best_result[0]}] правильных ответов', file=stat_file)
                print(f'Худший результат по классу: оценка {worst_results[1]} за [{worst_results[0]}] правильных ответов', file=stat_file)
                print(file=stat_file)
                print('Вы не загружали файл журнала, программа дает краткие рекомендации по заданиям, основываясь только на результатах этой работы', file=stat_file)
                for k, v in tasks_distribution.items():
                    print(f'В {k} задании {v}% правильных ответов', file=stat_file)
                print(file=stat_file)
                for rec in recomendations:
                    print(rec, file=stat_file)
                print(file=stat_file)
                print(conclusion, file=stat_file)
            print(f'Файл успешно сгенерирован по пути: {path}')

            if Settings().automatically_file_opening:
                os.startfile(path)



        elif len(works) == 1 and file_name:
            stats = StatisticsParser(res_dct, grades_dct, file_name)
            log.log('res_dct', res_dct)
            log.log('grades_dct', grades_dct)
            avg = stats.get_average()
            log.log('avg', avg)
            median = stats.get_median()
            log.log('median', median)
            grades_distribution = stats.get_grades_distribution()
            log.log('grades_distribution', grades_distribution)
            best_students, worst_students = stats.get_the_best_the_worst_students_results()
            log.log('best_students', best_students)
            log.log('worst_students', worst_students)
            tasks_distribution = stats.convertage_to_percentages(total_students)
            log.log('tasks_distribution', tasks_distribution)
            absents_not_parsed = db.get_absents(klass, work)
            log.log('absents_not_parsed', absents_not_parsed)
            best_result, worst_results = stats.get_best_worst_results()
            log.log('best_result', best_result)
            log.log('worst_results', worst_results)
            absents = 0 if not absents_not_parsed else len(absents_not_parsed.split(','))
            log.log('absents', absents)
            pr1 = {int(k): {int(ik): iv for ik, iv in v.items()} for k, v in stats.get_distribution_tasks_strong_weak_students().items()}
            pr2 = {int(k): v for k, v in stats.get_strong_weak_students()[1].items()}
            log.log('pr1', pr1)
            log.log('pr2', pr2)
            recomedations = stats.get_recomdendations_deep(pr1, pr2)
            log.log('recomedations', recomedations)
            p1, p2, p3 = stats.grades_dict, stats.get_distribution_tasks_strong_weak_students(), stats.get_strong_weak_students()[0]
            log.log('p1', p1)
            log.log('p2', p2)
            log.log('p3', p3)
            p4, p5 = stats.tasks_dict, stats.get_strong_weak_students()[1]
            log.log('p4', p4)
            log.log('p5', p5)
            conclusion = stats.get_extended_analysis(p1, p2, p3, p4, p5)
            log.log('conclusion', conclusion)


            if Settings().saving_statistics_in_unque_files:
                file_name = f'Статистика (c журналом) по классу {klass} по работе {work}.txt'
            else:
                file_name = 'Статистика.txt'
            path = os.path.join(os.getcwd(), file_name) if not Settings().saving_all_files_in_one_folder else (
                os.path.join(Settings().saving_all_files_in_one_folder, file_name))
            log.log('path', path)

            with open(path, 'w', encoding='utf-8') as stat_file:
                print(f'Статистика (с журналом) по классу {klass} по работе "{work}"', file=stat_file)
                print(file=stat_file)
                print(f'Средний балл по классу: {avg}', file=stat_file)
                print(f'Медианный балл по классу: {median}', file=stat_file)
                print(f'Отсутствоваших учеников: {absents}', file=stat_file)
                print(file=stat_file)
                print('Распределение оценок по классу:', file=stat_file)
                for k, v in grades_distribution.items():
                    print(f'Оценок {k}: {v}', file=stat_file)
                print(f'Больше всего оценок: {max(grades_distribution, key=grades_distribution.get)}', file=stat_file)
                print(file=stat_file)
                print(f'Лучшие ученики по классу: {", ".join(list(best_students.keys()))}', file=stat_file)
                print(f'Худшие ученики по классу: {", ".join(list(worst_students.keys()))}', file=stat_file)
                print(f'Лучший результат по классу: оценка {best_result[1]} за [{best_result[0]}] правильных ответов', file=stat_file)
                print(f'Худший результат по классу: оценка {worst_results[1]} за [{worst_results[0]}] правильных ответов', file=stat_file)
                print(file=stat_file)
                print('Вы загрузили файл журнала, поэтому программа дает подробные рекомендации по заданиям, основываясь на предыдущей успеваемости учеников', file=stat_file)
                for k, v in tasks_distribution.items():
                    print(f'В {k} задании {v}% правильных ответов', file=stat_file)
                print(file=stat_file)
                for rec in recomedations:
                    print(rec, file=stat_file)
                print(file=stat_file)
                print(conclusion, file=stat_file)
                if Settings().developer_mode:
                    print(file=stat_file)
                    print('Вы видите распределение ниже, потому что у вас включен режим разработчика.', file=stat_file)
                    distr_student_strength = stats.get_strong_weak_students()[0]
                    print('Программа определила такие индексы силы у учеников. 5 - максимальный, 1 - минимальный, 0 - слишком мало данных для корректного оценивания.' , file=stat_file)
                    for k, v in distr_student_strength.items():
                        print(f'{k}: {v}', file=stat_file)
            print(f'Файл успешно сгенерирован по пути: {path}')
            if Settings().automatically_file_opening:
                os.startfile(path)

        db.close()

        self.show()
        return
