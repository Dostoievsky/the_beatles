import csv
import os
import shutil
import sys
from datetime import datetime
import json
from collections import namedtuple
import tkinter as tk
from tkinter import filedialog
import json
import re
import signal
from pathlib import Path
import random
import time
from abc import ABC, abstractmethod
import statistics as stat
import matplotlib.pyplot as plt
from collections import Counter



# noinspection PyGlobalUndefined
def on_submit():
    global result
    class_value = class_entry.get()
    work_value = work_entry.get()
    date_value = date_entry.get()
    answer_file = answer_entry.get()
    marks_file = criteria_entry.get()
    students_file = students_entry.get()
    missings_file = absent_entry.get()
    students_folder = students_folder_entry.get()
    result = (class_value, work_value, date_value, answer_file, marks_file, students_file, missings_file, students_folder)
    root.destroy()

def browse_file(entry):
    file_path = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def browse_folder(entry):
    folder_path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, folder_path)


class StudentJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Student):
            return o.to_json()
        return super().default(o)


def student_decoder(dct):
    if '__class__' in dct and dct['__class__'] == 'Student':
        instance = Student(dct['_name'], dct['_surname'])
        instance._file = dct.get('_file')
        instance._list_answers = dct.get('_list_answers')
        instance._correct_answers = dct.get('_correct_answers')
        instance._response_status = dct.get('_response_status')
        instance._mark = dct.get('_mark')
        instance._missings = dct.get('_missings')
        instance._flag_not_all = dct.get('_flag_not_all')
        return instance
    return dct


def handle_stop_signal(signum, frame):
    print("\nПрограмма остановлена.")
    dev.write_to_file('KeyboardInterrapt', True)
    dev.write_to_file('datetime_kill', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    exit(0)


class StudentJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Student):
            return {'__student__': True,
                   'name': obj.name,
                   'surname': obj.surname,
                   'file': obj.file,
                   'list_answers': obj.list_answers,
                   'correct_answers': obj.correct_answers,
                   'mark': obj.mark}
        return super().default(obj)


# noinspection PyShadowingNames
class FileManager:
    def __init__(self, dct=None):
        self.dct = dct

    def write_to_csv(self, filename, puples_dct, main_dct):
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow([f"Класс: {main_dct['klass']}"])
            writer.writerow([f"Название работы: {main_dct['name_work']}"])
            writer.writerow([f"Дата работы: {main_dct['date']}"])
            writer.writerow([])

            for k, v in puples_dct:
                if v.missings:
                    writer.writerow([f'{k}  -  отсутствовал(а)'])
                else:
                    star = '*' if v.flag_not_all else ''
                    writer.writerow([f'{k}:    {v.mark}{star}'])

    @staticmethod
    def copy_directory(source_path, destination_path):
        try:
            shutil.copytree(source_path, destination_path)
            print(f"Папка успешно скопирована из {source_path} в {destination_path}.")
        except FileExistsError:
            pass
        except OSError as err:
            print(f"Ошибка при копировании: {err}")
            sys.exit()


    def create_json_filename(self):
        fullpath = os.path.join(os.getcwd(), f'archive/{self.dct["klass"]}')
        os.makedirs(fullpath, exist_ok=True)
        filenamestat = f"sysfile_{self.dct['klass'].lower().strip()}_{self.dct['name_work'].lower().strip()}_{self.dct['date']}.json"
        fullfilepath = os.path.join(fullpath, filenamestat)
        return fullfilepath

    def create_text_file_path(self):
        halfpath = os.path.join('archive', self.dct["klass"])
        fullpath = os.path.join(os.getcwd(), halfpath)
        os.makedirs(fullpath, exist_ok=True)
        fullnamework = f'{self.dct["klass"]}_{self.dct["name_work"].lower().strip()}_{self.dct["date"]}.txt'
        return os.path.join(fullpath, fullnamework)

    def create_csv_file_path(self):
        halfpath = os.path.join('archive', self.dct["klass"])
        fullpath = os.path.join(os.getcwd(), halfpath)
        os.makedirs(fullpath, exist_ok=True)
        fullnamework = f'{self.dct["klass"]}_{self.dct["name_work"].lower().strip()}_{self.dct["date"]}.csv'
        return os.path.join(fullpath, fullnamework)


class Finding:

    def __init__(self, name):
        self.name = name
        self.lst_found = []

    @staticmethod
    def txt_to_columns(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            for _ in range(4):
                next(file)
            return map(lambda x: x.strip(), file.readlines())


    @staticmethod
    def csv_to_columns(file_path):
        plain_list = []
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            for _ in range(4):
                next(csvfile)
            for line in csvfile:
                plain_list.append(line.strip())
        return plain_list

    def find_from_dir(self, dirpath):
        for file in os.listdir(dirpath):
            filepath = os.path.join(dirpath, file)
            if os.path.isfile(filepath) and not file.endswith('.json'):
                if file.endswith('.csv'):
                    lines = Finding.csv_to_columns(filepath)
                else:
                    lines = Finding.txt_to_columns(filepath)
                for line in lines:
                    if line.strip().lower().startswith(self.name.lower()):
                        self.lst_found.append((line, filepath))
                        continue
        if self.lst_found:
            return self.lst_found
        return 0


    def find_from_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as filefind:
            if file.endswith('.csv'):
                lines = Finding.csv_to_columns(filepath)
            else:
                lines = Finding.txt_to_columns(filepath)
            for line in lines:
                if line.strip().lower().startswith(self.name.lower()):
                    self.lst_found.append((line, filepath))
                    return self.lst_found

        return 0


class Answers:

    def __init__(self, file):
        self.file = file
        self.answers_lst = []

    def get_right_answers(self):
        with open(self.file, 'r', encoding='utf-8') as file:
            for line in file:
                _, answer = line.split(') ')
                self.answers_lst.append(answer.strip())
        return self.answers_lst


class Missings:
    def __init__(self, string, puple_file, puples_dict):
        self.string = string
        self.puple_file = puple_file
        self.puples_dict = puples_dict

    def get_missings(self):
        lst = []
        if self.string.lower().strip() == 'auto':
            with open(self.puple_file, 'r', encoding='utf-8') as pup_file:
                puples = map(lambda x: x.strip(), pup_file.readlines())
                for puple in puples:
                    if puple not in self.puples_dict.keys():
                        lst.append(puple)
                return lst
        else:
            with open(self.string, 'r', encoding='utf-8') as miss_file:
                for line in miss_file.readlines():
                    lst.append(line.strip())
                return lst


class FormatChecking:
    def __init__(self, results):
        self.results = results
        self.errors = []

    def format_klass(self):
        klass_pattern = r'^(?:[1-9]|10|11)\w?$'
        if re.match(klass_pattern, self.results.klass, flags=re.IGNORECASE):
            return True
        else:
            self.errors.append('Формат класса неверен.')
            return False

    def format_name_work(self):
        if len(self.results.name_work) > 50:
            self.errors.append('Название работы должно быть короче 50 символов.')
            return False
        elif re.search(r'[a-zA-Z]', self.results.name_work):
            self.errors.append('Название работы не должно содержать латинские буквы.')
            return False
        else:
            return True

    def format_date(self):
        date_pattern = r'^(0[1-9]|[12][0-9]|3[01])[-./](0[1-9]|1[012])[-./](19|20)\d\d$'
        if re.match(date_pattern, self.results.date):
            return True
        else:
            self.errors.append('Формат даты неверен.')
            return False

    def format_any_file(self):
        global flag_auto
        flag_auto = False
        files_to_check = [self.results.answer, self.results.marks, self.results.students, self.results.missings]
        if self.results.missings == 'auto':
            flag_auto = True
            files_to_check = [self.results.answer, self.results.marks, self.results.students]
        for filename in files_to_check:
            base_filename, extension = os.path.splitext(filename)
            if extension != '.txt':
                self.errors.append(f'Файл "{filename}" имеет неправильное расширение. Должно быть ".txt".')
                continue
            full_path = os.path.join(os.getcwd(), filename)
            if not os.path.isfile(full_path):
                self.errors.append(f'Файл "{filename}" не найден.')

        return len(self.errors) == 0

    def format_students_folder(self):
        path = os.path.join(os.getcwd(), self.results.students_folder)
        if os.path.isdir(path):
            return True
        else:
            self.errors.append('Указанная папка не найдена.')
            return False

    def check_all(self):
        checks = [
            self.format_klass(),
            self.format_name_work(),
            self.format_date(),
            self.format_any_file(),
            self.format_students_folder()
        ]
        if all(checks):
            return True
        else:
            return self.errors


class Questions:
    def __init__(self, question, tuple_of_variants=('1', 'lf', 'да', True)):
        self.question = question
        self.tuple_of_variants = tuple_of_variants

    def make_question(self):
        if input(self.question) in self.tuple_of_variants:
            return True
        else:
            return False

    def make_variants_question(self, variants):
        answ = input(self.question)


class Sorted:
    def __init__(self, dct):
        self.dct = dct

    def sort_by_default(self):
        return self.dct.items()

    def sort_by_name(self):
        sort_dct_items = sorted(self.dct.items(), key=lambda x: x[0])
        return sort_dct_items

    def sort_by_mark_best(self):
        return sorted(self.dct.items(), key=lambda item: float('-inf') if item[1].mark is None else item[1].mark, reverse=True)

    def sort_by_mark_worst(self):
        return sorted(self.dct.items(), key=lambda item: float('+inf') if item[1].mark is None else item[1].mark)


class Student:
    def __init__(self, name, surname):
        self._name = name
        self._surname = surname
        self._file = None
        self._list_answers = None
        self._correct_answers = None
        self._response_status = None
        self._mark = None
        self._missings = False
        self._flag_not_all = False


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def surname(self):
        return self._surname

    @surname.setter
    def surname(self, new_surname):
        self._surname = new_surname

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, new_file):
        self._file = new_file

    @property
    def list_answers(self):
        return self._list_answers

    @list_answers.setter
    def list_answers(self, new_list_answers):
        self._list_answers = new_list_answers

    @property
    def correct_answers(self):
        return self._correct_answers

    @correct_answers.setter
    def correct_answers(self, new_correct_answers):
        self._correct_answers = new_correct_answers

    @property
    def response_status(self):
        return self._response_status

    @response_status.setter
    def response_status(self, new_response_status):
        self._response_status = new_response_status


    @property
    def mark(self):
        return self._mark

    @mark.setter
    def mark(self, new_mark):
        self._mark = new_mark

    @property
    def flag_not_all(self):
        return self._flag_not_all

    @flag_not_all.setter
    def flag_not_all(self, value):
        self._flag_not_all = value

    @property
    def missings(self):
        return self._missings

    @missings.setter
    def missings(self, value):
        self._missings = value

    def to_json(self):
        return {
            "__class__": "Student",
            "_name": self._name,
            "_surname": self._surname,
            "_file": self._file,
            "_list_answers": self._list_answers,
            "_correct_answers": self._correct_answers,
            "_response_status": self._response_status,
            "_mark": self._mark,
            "_missings": self._missings,
            "_flag_not_all": self._flag_not_all
        }


class Generator:
    def __init__(self, puples_file, name_work):
        self.puples_file = puples_file
        self.name_work = name_work
        self.lst_files = []

    def generate_dir_students(self):
        path = os.path.join(os.getcwd(), self.name_work)
        os.makedirs(path, exist_ok=True)

    def generate_file_students(self):
        if self.puples_file is not None:
            with open(self.puples_file, 'r', encoding='utf-8') as kfile:
                for fullname in kfile:
                    name, surname = fullname.lower().strip().split()
                    filename = f'{name}_{surname}.txt'
                    with open(os.path.join(self.name_work, filename), 'a', encoding='utf-8') as f:
                        pass
        else:
            pass
        path = os.path.join(os.getcwd(), self.name_work)
        self.lst_files = os.listdir(path)

    def fill_files_students(self, count_strings):
        for file in self.lst_files:
            fullpath = os.path.join(self.name_work, file)
            with open(fullpath, 'w', encoding='utf-8') as filepuple:
                if count_strings is not None:
                    for i in range(1, count_strings + 1):
                        print(f'{i}) ', file=filepuple)
                else:
                    pass

    @staticmethod
    def create_answers_file(count_strings, filename='answers.txt'):
        if filename is not None:
            with open(filename, 'w', encoding='utf-8') as fileansw:
                if count_strings is not None:
                    for i in range(1, count_strings + 1):
                        print(f'{i}) ', file=fileansw)

    @staticmethod
    def create_marks_file(filename='marks.txt', grade=5):
        if filename is not None:
            with open(filename, 'w', encoding='utf-8') as filemarks:
                if grade is not None:
                    for _ in range(grade - 1):
                        print('оценка _ от _ до _ баллов', file=filemarks)

    @staticmethod
    def checking_setings(puples_file, count_strings):
        lst_errors = []
        if not os.path.exists(os.path.join(os.getcwd(), puples_file)):
            lst_errors.append(f'Файл {puples_file} не найден.')
        if not count_strings.isdigit():
            lst_errors.append(f'Количество строк должно быть целым числом.')
        if lst_errors:
            return lst_errors
        return False

    @staticmethod
    def create_missings_file(filename='missing.txt'):
        if filename is not None:
            with open(filename, 'w', encoding='utf-8') as filemiss:
                pass


class DebugMode:
    def __init__(self, debug):
        self.debug = debug

    def write_to_file(self, attr, value):
        if self.debug:
            with open('syslog.json', 'r', encoding='utf-8') as file:
                data = json.load(file)

            data[attr] = value

            with open('syslog.json', 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)


class RandomCall:
    @staticmethod
    def process_path(value):
        with open(value, 'r', encoding='utf-8') as file:
            return map(lambda x: x.strip(), file.readlines())

    @staticmethod
    def process_miss():
        with open('sys.json', 'r', encoding='utf-8') as sys_file_perf:
            dct_perf = json.load(sys_file_perf)
            try:
                trex = dct_perf['students']
            except KeyError:
                print('Файл sys.json не содержит информации о списке учеников. Только ручной ввод')
                sys.exit()
            with open(trex, 'r', encoding='utf-8') as file:
                return map(lambda x: x.strip(), file.readlines())

    @staticmethod
    def process_number(value):
        return range(1, value + 1)

    @staticmethod
    def process_input(user_input):
        path = Path(user_input)
        if path.is_file() and path.suffix == '.txt':
            return RandomCall.process_path(user_input)
        else:
            if user_input == '':
                return RandomCall.process_miss()
            try:
                number = int(user_input)
                return RandomCall.process_number(number)
            except ValueError:
                return False


class DeleteManager:
    def __init__(self, list_of_elements):
        self.list_of_elements = list_of_elements

    def delete_files(self):
        for filename in self.list_of_elements:
            file_path = os.path.join(os.getcwd(), filename)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Файл {filename} успешно удалён.")
                else:
                    pass
            except Exception as e:
                print(f"Ошибка при удалении файла {filename}: {e}")

    def delete_files_and_folders(self):
        for entry in self.list_of_elements:
            entry_path = os.path.join(os.getcwd(), entry)
            try:
                if os.path.isfile(entry_path):
                    os.remove(entry_path)
                    print(f"Файл {entry} успешно удалён.")
                elif os.path.isdir(entry_path):
                    shutil.rmtree(entry_path)
                    print(f"Папка {entry} успешно удалена.")
                else:
                    pass
            except Exception as e:
                print(f"Ошибка при удалении {entry}: {e}")

    @staticmethod
    def deep_delete():
        current_dir = os.getcwd()
        for entry in os.listdir(current_dir):
            entry_path = os.path.join(current_dir, entry)
            try:
                if os.path.isfile(entry_path) and not entry.endswith(".py"):
                    os.remove(entry_path)
                    print(f"Файл {entry} успешно удалён.")
                elif os.path.isdir(entry_path):
                    shutil.rmtree(entry_path)
                    print(f"Папка {entry} успешно удалена.")
            except Exception as e:
                print(f"Ошибка при удалении {entry}: {e}")

    def create_elements_test(self, dirs):
        for dir in dirs:
            os.makedirs(dir, exist_ok=True)
            print(f"Папка {dir} успешно создана.")
        for file in self.list_of_elements:
            with open(file, 'w') as f:
                print(f"Файл {file} успешно создан.")

    @staticmethod
    def create_file_delete():
        psw = random.randint(1000, 9999)
        with open('delete.txt', 'w') as f:
            print(f'Пароль для удаления: {psw}', file=f)
        return psw


class Marks:

    def __init__(self, file, marks_flag):
        self.file = file
        self.marks_flag = marks_flag

    def check_marks(self):
        parser_b = lambda x: re.fullmatch(r'\d+\t\d+', x.strip())
        parser_m = lambda x: re.fullmatch(r'\w{6}\W\d+\W\w{2}\W\d+\W\w{2}\W\d+\W\w{6}', x.strip())

        with open(self.file, 'r', encoding='utf-8') as file:
            content = file.read().strip()

            if not content:
                raise ValueError(f"Файл {self.file} пустой. Проверьте файл.")

            lines = content.splitlines()

            if self.marks_flag and all(map(parser_b, lines)):
                return 'points'
            elif not self.marks_flag and all(map(parser_m, lines)):
                return 'marks'
            elif self.marks_flag and any(map(parser_m, lines)):
                raise ValueError("Указано, что формат файла в баллах, но найдены записи в формате оценок!")
            elif not self.marks_flag and any(map(parser_b, lines)):
                raise ValueError("Указано, что формат файла в оценках, но найдены записи в формате баллов!")
            else:
                raise ValueError(f"Формат файла {self.file} не соответствует ожидаемым критериям.")

    def get_marks(self):
        marks_dict = {}

        try:
            format_type = self.check_marks()
        except ValueError as err:
            raise ValueError(str(err))

        with open(self.file, 'r', encoding='utf-8') as file_marks:
            if format_type == 'points':
                for line in file_marks.readlines():
                    primary, secondary = line.strip().split('\t')
                    marks_dict[primary] = int(secondary)
                return marks_dict
            elif format_type == 'marks':
                for line in file_marks.readlines():
                    _, mark, _, down, _, up, _ = line.strip().split()
                    for i in range(int(down), int(up) + 1):
                        marks_dict[i] = int(mark)
                return marks_dict
            else:
                return 'Непредвиденная ошибка в процессе компиляции оценок. Сверьтесь с инструкцией.'


# noinspection PyTypedDict
class SettingsGeneration:
    def __init__(self):
        self.inputs = {
            "name_of_work": None,
            "pupe_file": None,
            "count_strings_pup": None,
            "answers_file": None,
            "template_lines": None,
            "criteria_file": None,
            "grading_scale": None,
            "absentees_file": None
        }

    class Questions:
        def __init__(self, question, tuple_of_variants=('1', 'lf', 'да')):
            self.question = question
            self.tuple_of_variants = tuple_of_variants

        def make_question(self):
            if input(self.question).strip().lower() in self.tuple_of_variants:
                return True
            else:
                return False

    @staticmethod
    def validate_integer(prompt):
        while True:
            try:
                return abs(int(input(prompt)))
            except ValueError:
                print("Введите корректное целое число.")

    def step_get_name_of_work(self):
        self.inputs["name_of_work"] = input("Введите название работы: ").strip()

    def step_get_pupe_file(self):
        sm = self.Questions("Нужны ли файлы учеников? ")
        if sm.make_question():
            pupe_file = input("Введите название файла учеников: ").strip()
            if not os.path.exists(pupe_file):
                print(f"Файл {pupe_file} не найден.")
                sys.exit()
            self.inputs["pupe_file"] = pupe_file

            sm = self.Questions("Нужны ли строки для ответов в файлах учеников? ")
            if sm.make_question():
                self.inputs["count_strings_pup"] = self.validate_integer("Введите количество строк для ответов: ")

    def step_get_answers_file(self):
        sm = self.Questions("Нужен ли файл с ответами? ")
        if sm.make_question():
            self.inputs["answers_file"] = input("Введите название файла с ответами: ").strip()

            sm = self.Questions("Создать файл по шаблону? ")
            if sm.make_question():
                self.inputs["template_lines"] = self.validate_integer("Введите количество строк для шаблона: ")

    def step_get_criteria_file(self):
        sm = self.Questions("Нужен ли файл с критериями оценивания? ")
        if sm.make_question():
            self.inputs["criteria_file"] = input("Введите название файла с критериями: ").strip()

            sm = self.Questions("Создать файл по шаблону? ")
            if sm.make_question():
                self.inputs["grading_scale"] = self.validate_integer("Введите шкалу оценивания: ")

    def step_get_absentees_file(self):
        sm = self.Questions("Нужен ли файл с отсутствующими? ")
        if sm.make_question():
            self.inputs["absentees_file"] = input("Введите название файла с отсутствующими: ").strip()

    def run_survey(self):
        self.step_get_name_of_work()
        self.step_get_pupe_file()
        self.step_get_answers_file()
        self.step_get_criteria_file()
        self.step_get_absentees_file()
        return self.inputs


class Statistics(ABC):
    def __init__(self, lst_marks=None, tuple_info=None):
        if lst_marks is None:
            lst_marks = []
        if tuple_info is None:
            tuple_info = {}
        self.pairs = []
        self.yet_added = []
        self.lst_marks = lst_marks

    def set_pairs(self, dirpath):
        files = list(filter(lambda x: os.path.isfile(os.path.join(dirpath, x)), os.listdir(dirpath)))
        files_json = list(filter(lambda x: x.endswith('.json'), files))
        files_txt_csv = list(filter(lambda x: x.endswith('.txt') or x.endswith('.csv'), files))
        for file_def in files_txt_csv:
            file_without_ext = Path(file_def).stem
            try:
                _, namework, date = file_without_ext.split('_')
            except ValueError:
                pass
            for file_json in files_json:
                file_json_without_ext = Path(file_json).stem
                try:
                    _, _, namework_json, date_json = file_json_without_ext.split('_')
                except ValueError:
                    pass
                if namework == namework_json and date == date_json:
                    self.pairs.append((file_def, file_json))
                    self.yet_added.append(file_def)

        alone = (item for item in files_txt_csv if item not in self.yet_added)
        for file in alone:
            self.pairs.append((file, None))

    def get_average(self):
        self.lst_marks = list(filter(lambda x: isinstance(x, int), self.lst_marks))
        avr = stat.mean(self.lst_marks)
        return round(avr, 2)

    def get_most_common(self):
        return self.__class__.get_counter(self).most_common(1)[0][0]

    def get_counter(self):
        return Counter(self.lst_marks)

    def get_median(self):
        self.lst_marks = list(filter(lambda x: isinstance(x, int), self.lst_marks))
        med = stat.median(self.lst_marks)
        return round(med, 2)

    @abstractmethod
    def get_amount_missings(self, tuple_info):
        pass

    @abstractmethod
    def get_amount_notfilled(self, tuple_info):
        pass


class BriefStatistics(Statistics):
    @staticmethod
    def process_file(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            if filename.endswith('.txt'):
                iterator_lines =  map(lambda x: x.strip(), file.readlines())
                for _ in range(4):
                    next(iterator_lines)
                return list(iterator_lines)
            elif filename.endswith('.csv'):
                plain_list = []
                for _ in range(4):
                    next(file)
                for line in file:
                    plain_list.append(line.strip())
                return plain_list

    @staticmethod
    def process_to_dict(namemarks_lst):
        dct, lst_of_missings, lst_of_notfulled = {}, [], []
        for namemark in namemarks_lst:
            name, mark = map(lambda x: x.strip(), namemark.split(':'))
            try:
                mark = int(mark)
            except ValueError:
                if mark.startswith('отсутствовал'):
                    lst_of_missings.append(name)
                    mark = None
                else:
                    mark = int(mark[0])
                    lst_of_notfulled.append(name)
            dct[name] = mark
        return dct, lst_of_missings, lst_of_notfulled

    @staticmethod
    def process_to_list(namemarks_lst):
        lst = []
        for namemark in namemarks_lst:
            name, mark = map(lambda x: x.strip(), namemark.split(':'))
            try:
                lst.append(int(mark))
            except ValueError:
                if mark.startswith('отсутствовал'):
                    continue
                else:
                    lst.append(int(mark[0]))
        return lst

    def get_amount_missings(self, tuple_info):
        return len(tuple_info[1])

    def get_amount_notfilled(self, tuple_info):
        return len(tuple_info[2])


class DeepStatistics(Statistics):

    @staticmethod
    def process_file(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            json_data = json.load(file, object_hook=student_decoder)
            return json_data

    @staticmethod
    def process_to_list(json_data):
        lst = []
        for student in json_data.values():
            lst.append(student.mark)
        return lst

    @staticmethod
    def process_to_dict(json_data):
        dct_marks, lst_of_missings, lst_of_notfulled = {}, [], []
        for student, info in json_data.items():
            dct_marks[student] = info.mark
            if info.missings:
                lst_of_missings.append(student)
            if info.flag_not_all:
                lst_of_notfulled.append(student)
        return dct_marks, lst_of_missings, lst_of_notfulled

    @staticmethod
    def process_to_distribution(json_data):
        lst = []
        for info in json_data.values():
            if info.response_status is None:
                continue
            lst.append(info.response_status)
        return lst

    @staticmethod
    def procces_to_best_worst(json_data):
        dct = {}
        for student, info in json_data.items():
            if info.mark is None:
                continue
            dct[student] = (info.mark, info.correct_answers)
        return dct

    @staticmethod
    def process_to_average_answ(json_data):
        lst = []
        for info in json_data.values():
            if info.correct_answers is None:
                continue
            lst.append(info.correct_answers)
        return lst


    def get_amount_missings(self, tuple_info):
        return len(tuple_info[2])

    def get_amount_notfilled(self, tuple_info):
        return tuple_info[1]

    @staticmethod
    def get_the_best_puples(dct_best_worst):
        return sorted(dct_best_worst, key=lambda x: dct_best_worst[x][0], reverse=True)[:3]

    @staticmethod
    def get_the_worst_puples(dct_best_worst):
        return sorted(dct_best_worst, key=lambda x: dct_best_worst[x][0], reverse=False)[:3]

    @staticmethod
    def convert_to_percentage(stats_dict):
        result = {}
        for question_num, (true_count, false_count) in stats_dict.items():
            total_count = true_count + false_count
            if total_count == 0:
                percent = 0
            else:
                percent = (true_count / total_count) * 100
            result[question_num] = round(percent, 2)
        return result


    @staticmethod
    def get_distribution(lst_distribution):
        result = {}
        for student in lst_distribution:
            for question_num, is_correct in student:
                if question_num not in result:
                    result[question_num] = [0, 0]
                if is_correct:
                    result[question_num][0] += 1
                else:
                    result[question_num][1] += 1
        return {q: tuple(ans) for q, ans in result.items()}

    @staticmethod
    def get_average_answ(lst_average_answ):
        return stat.mean(lst_average_answ)


class RangeKey:
    def __init__(self, start, stop, step=1):
        self.range_obj = range(start, stop + 1, step)

    def __eq__(self, other):
        if isinstance(other, RangeKey):
            return (
                self.range_obj.start == other.range_obj.start and
                self.range_obj.stop == other.range_obj.stop and
                self.range_obj.step == other.range_obj.step
            )
        return NotImplemented

    def __hash__(self):
        return hash((self.range_obj.start, self.range_obj.stop, self.range_obj.step))

    def __contains__(self, item):
        return item in self.range_obj

    def __repr__(self):
        return f"RangeKey({self.range_obj.start}-{self.range_obj.stop-1})"


class StatisticsRecommendations:
    def __init__(self, converted_to_percentage):
        self.converted_to_percentage = converted_to_percentage
        self.counter = 0

    def group_tasks_by_percent(self):
        grouped_tasks = {}
        for task, percent in self.converted_to_percentage.items():
            if percent not in grouped_tasks:
                grouped_tasks[percent] = []
            grouped_tasks[percent].append(task)
        return grouped_tasks


    def get_recommendations(self):
        DICT_RECOMMENDATIONS = {
            RangeKey(0, 0): f'Задания [{{numbers}}] не решил ни один ученик. Похоже, что задания чересчур сложные.',
            RangeKey(1, 10): f'Задания [{{numbers}}] очень плохо усвоены, меньше 10% учеников ответили верно',
            RangeKey(11, 20): f'Задания [{{numbers}}] ученики выполнили плохо, похоже, что тема усвоена не очень хорошо',
            RangeKey(21, 35): f'Задания [{{numbers}}] выполнила небольшая часть учеников, стоит проработать эту тему',
            RangeKey(36, 45): f'Задания [{{numbers}}] выполнила почти половина учеников, если это были задания повышенной сложности, то это очень неплохо',
            RangeKey(46, 55): f'Задания [{{numbers}}] верно решили около половины учеников',
            RangeKey(56, 70): f'Задания [{{numbers}}] решили больше половины учеников, что очень неплохо',
            RangeKey(71, 90): f'Задания [{{numbers}}] решили большая часть ученики, тема отлично усвоена',
            RangeKey(91, 99): f'Задания [{{numbers}}] не решили всего пара ученников, отличный результат, возможно, задания были слишком простые',
            RangeKey(100, 100): f'Задания [{{numbers}}] решили абсолютно все ученики, тема идеально усвоена или, вероятно, задания были чересчур простые'}
        grouped_tasks = self.group_tasks_by_percent()
        recommendations = []

        for percent, tasks in grouped_tasks.items():
            numbers = ', '.join(map(str, tasks))
            for key, rec in DICT_RECOMMENDATIONS.items():
                if round(percent) in key:
                    recommendations.append(rec.format(numbers=numbers))

        return recommendations


    @staticmethod
    def get_final_conclusion(avrg):
        CONCLUSIONS_DICT = {RangeKey(0, 30): 'В срднем ученики не очень хорошо справились с работой, лучше повторить эту тему',
                            RangeKey(31, 60): 'В среднем ученики справились с работой, однако около половины учеников не усвоили тему',
                            RangeKey(61, 80): 'В среднем ученики хорошо справились с работой, однако некоторые задания вызвали у них сложности',
                            RangeKey(81, 99): 'В среднем ученики отлично справились, тема очень хорошо усвоена',
                            RangeKey(100, 100): f'Ни один ученик не совершил ни одной ошибки, вам стоит проверить критерии оцениквания, ответы или задания на сложность, так как такой исход очень маловероятен'}
        for key, conclusion in CONCLUSIONS_DICT.items():
            if round(avrg) in key:
                return conclusion


class PupleDeepStatistics:
    def __init__(self, name, processed_data):
        self.name = name
        self.processed_data = processed_data
        try:
            self.puple = self.processed_data[self.name]
        except:
            print(f'Ученик {self.name} не найден')
            sys.exit()

    def missings(self):
        return self.puple.missings

    def not_all(self):
        return self.puple.flag_not_all

    def mark(self):
        return self.puple.mark

    def response_status(self):
        not_list = self.puple.response_status
        return list(map(lambda x: 'Верно' if x[1] else 'Неверно', not_list))
        # return not_list

    def correct_answers_am(self):
        return self.puple.correct_answers


class DeepStatisticsGraphics:
    def __init__(self, data_distr, data_marks):
        self.data_distr = data_distr
        self.data_marks = data_marks

    def show(self):
        sorted_data = sorted(self.data_marks.items(), key=lambda x: (x[0] is None, -x[0] if x[0] is not None else float('inf')))
        counter_data = dict(sorted_data)
        labels = [label if label is not None else 'отсутствующие' for label in counter_data.keys()]
        values = list(counter_data.values())

        color = '#7a7a7a'

        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 7))

        colors_first = []
        for percent in self.data_distr.values():
            if percent < 40:
                colors_first.append('#c71d1d')
            elif percent < 70:
                colors_first.append('#eddc31')
            else:
                colors_first.append('#356a0c')

        axes[0].bar(self.data_distr.keys(), self.data_distr.values(), color=colors_first)
        axes[0].set_title('Процент правильных ответов по вопросам')
        axes[0].set_xlabel('Номер вопроса')
        axes[0].set_ylabel('Процент правильных ответов')
        axes[0].set_xticks(list(self.data_distr.keys()))

        positions = range(len(values))
        axes[1].bar(positions, values, color=color)
        axes[1].set_title('Распределение оценок')
        axes[1].set_xlabel('Оценка')
        axes[1].set_ylabel('Количество')
        axes[1].set_xticks(positions)
        axes[1].set_xticklabels(labels)

        plt.tight_layout()
        plt.show()


#начало программы
debug = False


if os.path.exists('syslog.json'):
    with open('syslog.json', 'r', encoding='utf-8') as sys_file:
        logdct = json.load(sys_file)
        if logdct['debug']:
            debug = True

with open('syslog.json', 'w', encoding='utf-8') as sys_file:
    json.dump({'debug': False}, sys_file, indent=4, ensure_ascii=False)

dev = DebugMode(debug)


if os.path.isfile('sys.json') and len(json.load(open('sys.json'))) == 8:
    with open('sys.json', 'r', encoding='utf-8') as sys_file:
        main_dct = json.load(sys_file)
#форма заполнения данных через tkinter
else:
    root = tk.Tk()
    root.title("Форма заполнения данных")
    root.geometry("700x500")
    font_style = ("Montserrat", 10, "bold")

    header_label = tk.Label(root, text="Заполните все поля для начала работы.", font=("Montserrat", 12, "bold"))
    header_label.grid(row=0, column=0, columnspan=3, pady=(10, 20))

    class_label = tk.Label(root, text="Класс:", font=font_style)
    class_label.grid(row=1, column=0, pady=(10, 5))
    class_entry = tk.Entry(root, font=font_style)
    class_entry.grid(row=1, column=1, pady=(10, 5))

    work_label = tk.Label(root, text="Название работы:", font=font_style)
    work_label.grid(row=2, column=0, pady=5)
    work_entry = tk.Entry(root, font=font_style)
    work_entry.grid(row=2, column=1, pady=5)

    date_label = tk.Label(root, text="Дата работы:", font=font_style)
    date_label.grid(row=3, column=0, pady=5)
    date_entry = tk.Entry(root, font=font_style)
    date_entry.grid(row=3, column=1, pady=5)

    answer_label = tk.Label(root, text="Файл с ответами:", font=font_style)
    answer_label.grid(row=4, column=0, pady=5)
    answer_entry = tk.Entry(root, font=font_style)
    answer_entry.grid(row=4, column=1, pady=5)
    answer_button = tk.Button(root, text="Выбрать файл", command=lambda: browse_file(answer_entry), font=font_style)
    answer_button.grid(row=4, column=2, padx=5, pady=5)

    criteria_label = tk.Label(root, text="Файл с критериями:", font=font_style)
    criteria_label.grid(row=5, column=0, pady=5)
    criteria_entry = tk.Entry(root, font=font_style)
    criteria_entry.grid(row=5, column=1, pady=5)
    criteria_button = tk.Button(root, text="Выбрать файл", command=lambda: browse_file(criteria_entry), font=font_style)
    criteria_button.grid(row=5, column=2, padx=5, pady=5)

    students_label = tk.Label(root, text="Список учеников:", font=font_style)
    students_label.grid(row=6, column=0, pady=5)
    students_entry = tk.Entry(root, font=font_style)
    students_entry.grid(row=6, column=1, pady=5)
    students_button = tk.Button(root, text="Выбрать файл", command=lambda: browse_file(students_entry), font=font_style)
    students_button.grid(row=6, column=2, padx=5, pady=5)

    absent_label = tk.Label(root, text="Список отсутствующих:", font=font_style)
    absent_label.grid(row=7, column=0, pady=5)
    absent_entry = tk.Entry(root, font=font_style)
    absent_entry.grid(row=7, column=1, pady=5)
    absent_button = tk.Button(root, text="Выбрать файл", command=lambda: browse_file(absent_entry), font=font_style)
    absent_button.grid(row=7, column=2, padx=5, pady=5)

    students_folder_label = tk.Label(root, text="Папка с работами:", font=font_style)
    students_folder_label.grid(row=8, column=0, pady=5)
    students_folder_entry = tk.Entry(root, font=font_style)
    students_folder_entry.grid(row=8, column=1, pady=5)
    students_folder_button = tk.Button(root, text="Выбрать папку", command=lambda: browse_folder(students_folder_entry), font=font_style)
    students_folder_button.grid(row=8, column=2, padx=5, pady=5)

    submit_button = tk.Button(root, text="Отправить", command=on_submit, font=font_style)
    submit_button.grid(row=9, column=1, columnspan=3, pady=(10, 20))

    root.mainloop()

    Results = namedtuple('Results', ['klass', 'name_work', 'date', 'answer', 'marks', 'students', 'missings', 'students_folder'])
    results = Results(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])

#проверка формата данных и формирование sys.json

    if all(results._asdict().values()):
        formatting = FormatChecking(results)
        if isinstance(formatting.check_all(), list):
            print('Возникли ошибки при проверке формата данных:')
            dev.write_to_file('errors', formatting.errors)
            for error in formatting.errors:
                print(error)
            sys.exit()
        elif isinstance(formatting.check_all(), bool):
            with open('sys.json', 'w', encoding='utf-8') as sys_json_file:
                json.dump(results._asdict(), sys_json_file, ensure_ascii=False, indent=4)
                print('Данные сохранены, перезапустите программу.')
                dev.write_to_file('data_saved', True)
                sys.exit()
        else:
            print('Непредвиденная ошибка при проверке формата данных.')
            dev.write_to_file('unknown_error', 'Непредвиденная ошибка при проверке формата данных.')
            sys.exit()
    else:
        print('Вы оставили какое-то поле не заполненным. Программа остановлена.')
        dev.write_to_file('empty_field', True)
        sys.exit()


dct_variants = {
    'check_works': ('1', 'проверка', 'проверка работ'),
    'redact_data': ('2', 'редактирование', 'редактирование данных', 'перезапись', 'перезапись данных'),
    'find_puple': ('3', 'поиск по работам', 'поиск по работе', 'поиск'),
    'statistics': ('4', 'статистика', 'статистика работы', 'статистика работ'),
    'generate': ('5', 'генерация', 'генерация директорий и файлов'),
    'performance': ('6', 'случайный вызов'),
    'clear': ('7', 'сброс', 'сбросить', 'сбросить данные')
}

if debug:
    print('Вы вошли в режим разработчика. Включен режим отладки.')
    print()


dev.write_to_file('datetime_start', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


signal.signal(signal.SIGINT, handle_stop_signal)
signal.signal(signal.SIGTERM, handle_stop_signal)


mainchoose = input('Выберите режим работы:\n'
                   '1. Проверка работ[1]\n'
                   '2. Перезапись данных[2]\n'
                   '3. Поиск по работам[3]\n'
                   '4. Статистика по работам[4]\n'
                   '5. Генерация директорий и файлов[5]\n'
                   '6. Случайный вызов[6]\n'
                   '7. Сброс данных[7]\n').strip().lower()

dev.write_to_file('mainchoose', mainchoose)

if mainchoose in dct_variants['check_works']: #проверка работ
    print('Программа работает со следующими данными, если вы хотите измеенить их, то выберите режим измения данных:')
    for k, v in main_dct.items():
        print(f'{k}: {v}')

    print()

    stat_flag = False
    marks_flag = False
    csv_flag = False

    qst = Questions('Вам нужны подробные отчеты по ученику или классу? Для подробной статистики будет создан дополнительный системный json-файл.\n')
    if qst.make_question():
        stat_flag = True

    qst1 = Questions('В файле с оценками критерии оценивания записаны в форме баллов?\n')
    if qst1.make_question():
        marks_flag = True

    qst0 = Questions('Записать результаты проверки в csv-файл? (при отрицательном ответе результаты будут записаны в txt-файл)\n')
    if qst0.make_question():
        csv_flag = True

    dev.write_to_file('stat_flag', stat_flag)
    dev.write_to_file('marks_flag', marks_flag)
    dev.write_to_file('csv_flag', csv_flag)

    files_of_puple = os.listdir(main_dct['students_folder']) #формирование словаря имя_ученика: путь_к_файлу
    dct_of_puple_files = {}
    for puple_file in files_of_puple:
        puple_file_name = puple_file.split('.')[0]
        name, surname = puple_file_name.split('_')
        full_name = f'{name} {surname}'.title()
        full_path = os.path.join(main_dct['students_folder'], puple_file)
        dct_of_puple_files[full_name] = full_path


    puples_dct = {}
    for k, v in dct_of_puple_files.items(): #создание экземпляров класса Student
        puples_dct[k] = Student(*k.split())
        puples_dct[k].file = v
        dev.write_to_file(k+'0', puples_dct[k].__dict__)

    for k, v in puples_dct.items(): #заполнение экземпляров класса Student списком ответов
        lst_of_answers = []
        with open(v.file, 'r', encoding='utf-8') as puple_file:
            for line in puple_file:
                try:
                    _, answer = line.strip().split(')')
                except ValueError:
                    continue
                lst_of_answers.append(answer.strip())
            v.list_answers = lst_of_answers
        dev.write_to_file(k+'1', puples_dct[k].__dict__)

    right_answers = Answers(main_dct['answer']) #создание экземпляра класса Answers
    lst_of_right_answers = right_answers.get_right_answers()


    for k, v in puples_dct.items(): #заполнение экземпляров класса Student количеством правильных ответов
        counter_right = 0
        response_list = []
        if len(v.list_answers) != len(lst_of_right_answers):
            v.flag_not_all = True
        for index, pupright in enumerate(zip(v.list_answers, lst_of_right_answers), 1):
            pup, right = pupright
            if pup == right:
                counter_right += 1
                response_list.append((index, True))
            else:
                response_list.append((index, False))
        v.correct_answers = counter_right
        v.response_status = response_list
        dev.write_to_file(k + '2', puples_dct[k].__dict__)

    m = Marks(main_dct['marks'], marks_flag) #создание экземпляра класса Marks

    try: #проверка корректности файла marks.txt
        marks_dct = m.get_marks()
    except ValueError as e:
        print(e)
        sys.exit()

    for k, v in puples_dct.items(): #заполнение экземпляров класса Student оценками
        try:
            mark = marks_dct[v.correct_answers]
            v.mark = mark
            dev.write_to_file(k + '3', puples_dct[k].__dict__)
        except KeyError:
            print('Возникла ошибка при получении оценки ученика. Проверьте файл с оценками.')
            dev.write_to_file('error_mark', True)
            sys.exit()


    string, puple_file = main_dct['missings'], main_dct['students'] #создание экземпляра класса Missings
    missings_puple = Missings(string, puple_file, puples_dct)
    print()

    for miss in missings_puple.get_missings(): #заполнение экземпляров класса Student отсутствующими учениками
        puples_dct[miss] = Student(*miss.split())
        puples_dct[miss].missings = True

    fm = FileManager(main_dct)
    smthpath = os.path.join(os.getcwd(), 'archive', main_dct['klass'], main_dct['name_work'])
    fm.copy_directory(main_dct['students_folder'], smthpath)
    filepath = fm.create_text_file_path()

    if stat_flag: #создание системного json-файла для статистики по флагу stat_flag
        halfpath = f'archive/{main_dct["klass"]}'
        fullpath = os.path.join(os.getcwd(), halfpath)
        filenamestat = f"sysfile_{main_dct['klass'].lower().strip()}_{main_dct['name_work'].lower().strip()}_{main_dct['date']}.json"
        fullfilepath = os.path.join(fullpath, filenamestat)
        with open(fullfilepath, 'w', encoding='utf-8') as f:
            json.dump(puples_dct, f, cls=StudentJSONEncoder, ensure_ascii=False, indent=4)
        dev.write_to_file('happy_end_stat', True)

    qst2 = input('Выберите режим сортировки:\n'
                     'По умолчанию[0]\n'
                     'По именам[1]\n'
                     'По оценкам(сначала лучшие)[2]\n'
                     'По оценкам(сначала худшие)[3]\n').lower().strip()

    dev.write_to_file('sorted_mode', qst2)

    sort = Sorted(puples_dct) #сортировка
    if qst2 in ('по умолчанию', '0'):
        puples_dct = sort.sort_by_default()
    elif qst2 in ('по именам', '1'):
        puples_dct = sort.sort_by_name()
    elif qst2 in ('по оценкам(сначала лучшие)', '2'):
        puples_dct = sort.sort_by_mark_best()
    elif qst2 in ('по оценкам(сначала худшие)', '3'):
        puples_dct = sort.sort_by_mark_worst()
    else:
        print('Неизвестный режим сортировки.')
        dev.write_to_file('unknown_sort_mode', True)
        sys.exit()

    if not csv_flag:
        with open(filepath, 'w', encoding='utf-8') as file: #запись в итоговый файл
            print(f"Класс: {main_dct['klass']}", file=file)
            print(f"Название работы: {main_dct['name_work']}", file=file)
            print(f"Дата работы: {main_dct['date']}", file=file)
            print(file=file)
            for k, v in puples_dct:
                if v.missings:
                    print(f'{k}:    отсутствовал(а)', file=file)
                    dev.write_to_file(k+'4', 'miss')
                    continue
                star = ('*' if v.flag_not_all else '')
                print(f'{k}:    {v.mark}{star}', file=file)
    else:

        fm = FileManager(main_dct)
        filepath = fm.create_csv_file_path()
        fm.write_to_csv(filepath, puples_dct, main_dct)

    print(f'Проверка прошла успешно. Результаты проверки записаны в файл {filepath}.') #конец работы

    dev.write_to_file('happy_end', True)

    qst3 = Questions('Открыть файл?\n')
    dev.write_to_file('open_file', True)
    if qst3.make_question():
        os.startfile(filepath)
    dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


elif mainchoose in dct_variants['redact_data']: #перезапись данных, повторное открытие диалогового окна посредством удаления файла sys.json
    qst = Questions('Вы хотите перезаписать данные?\n')
    if qst.make_question():
        os.remove('sys.json')
        print('Файл данных удален. Перезапустите программу.')
        dev.write_to_file('happy_end', True)


elif mainchoose in dct_variants['find_puple']:
    print('Вы можете ввести имя интересующего вас файла или папки и имя ученика. Программа найдет оценки ученика в указанной папке или файле.')
    pupname = input('Введите имя ученика: ')
    dev.write_to_file('pupname', pupname)

    archivepath = os.path.join(os.getcwd(), 'archive')
    dct_find_dirs = {}
    for index, dir in enumerate(os.listdir(archivepath), 1): #генерация меню выбора и запись в словарь
        print(f'{dir}[{index}]')
        dct_find_dirs[index] = dir
        dev.write_to_file(dct_find_dirs[index], dir)
    try:    #ввод папки и проверка корректности
        input_dir = int(input('Введите номер папки, в которой хотите произвести поиск:\n'))
        dev.write_to_file('input_dir', input_dir)
    except Exception:
        print('Введите номер папки, а не название папки.')
        dev.write_to_file('error_input_dir', True)
        sys.exit()
    try:
        hghg = dct_find_dirs[int(input_dir)]
    except KeyError:
        print('Нет папки с таким номером.')
        dev.write_to_file('error_number_dir', True)
        sys.exit()

    dct_find_files = {}
    fullpathfind = os.path.join(archivepath, hghg)
    qst4 = input(f'Искать по папке {hghg}[1] или конкретному файлу?[0]\n')

    #основной блок с инициализацией экземпляров классов (директории)
    if qst4 in ('1', 'по папке'):
        dev.write_to_file('from_dir', True)
        fnd = Finding(pupname)
        found = fnd.find_from_dir(fullpathfind)
        if not found:
            print(f'Ученик {pupname} не найден в папке {hghg}')
            dev.write_to_file('pupname_not_found', True)
            sys.exit()
        else:
            dev.write_to_file('found', found)
            for line, filepath in found:
                print(f"В работе '{os.path.basename(filepath)}' - {line}")


    elif qst4 in ('0', 'по файлу'):#проверка корректности файла
        dev.write_to_file('from_file', True)
        filtered_list_dir = filter(lambda file: os.path.isfile(os.path.join(fullpathfind, file)) and (file.endswith('.txt') or file.endswith('.csv')) , os.listdir(fullpathfind))
        for index, file in enumerate(filtered_list_dir, 1):
            dct_find_files[index] = file
            print(f'{file}[{index}]')
        try:
            input_file = int(input('Введите номер файла, в которой хотите произвести поиск:\n'))
            dev.write_to_file('input_file', input_file)
        except Exception:
            print('Введите номер файла, а не название файла')
            dev.write_to_file('error_input_file', True)
            sys.exit()
        try:
            fgfg = dct_find_files[int(input_file)]
        except KeyError:
            print('Нет файла с таким номером')
            dev.write_to_file('error_number_file', True)
            dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            sys.exit()


        #основной блок с инициализацией экземпляров классов (файлы)
        found_file = Finding(pupname)
        found = found_file.find_from_file(os.path.join(fullpathfind, fgfg))
        if not found:
            print(f'Ученик {pupname} не найден в папке {hghg}')
            dev.write_to_file('pupname_not_found', True)
            sys.exit()
        else:
            dev.write_to_file('found', found)
            for line, filepath in found:
                print(f"В работе '{os.path.basename(filepath)}' - {line}")
        dev.write_to_file('happy_end', True)
        dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        sys.exit()


elif mainchoose in dct_variants['statistics']: #режим статистики по работам
    print('Вы в режиме статистики. Выберите папку') #генерация меню выбора папки, а затем файла, проврека корректности данных до следущего комментария
    dct_stat_chose = {}
    for index, dir in enumerate(os.listdir('archive'), 1):
        print(f'{dir}[{index}]')
        filepathrem = os.path.join(os.getcwd(), 'archive', dir)
        dct_stat_chose[index] = filepathrem
    chose_stat = input('Введите номер папки, по которой хотите получить статистику:\n')
    try:
        chose_stat = int(chose_stat)
    except Exception:
        print('Введите номер папки')
        sys.exit()
    try:
        chose_stat_p = dct_stat_chose[chose_stat]
    except KeyError:
        print('Нет папки с таким номером')
        sys.exit()

    if not any(os.path.isfile(os.path.join(chose_stat_p, x)) for x in os.listdir(chose_stat_p)):
        print('Папка пуста') #проверка на пустоту папки
        sys.exit()

    brief_st = BriefStatistics()
    brief_st.set_pairs(chose_stat_p)

    dct_stat_choose_file = {}
    print('Выберите работу, статистику по которой хотите получить:')
    for index, pair in enumerate(brief_st.pairs, 1):
        print(f'{pair[0]}[{index}] {"<только краткая статистика>" if pair[1] is None else ""}')
        dct_stat_choose_file[index] = pair

    try:
        choose_stat_work = int(input('Введите номер работы:\n'))
    except Exception:
        print('Введите номер работы')
        sys.exit()
    try:
        chosen_file = dct_stat_choose_file[choose_stat_work]
    except KeyError:
        print('Нет работы с таким номером')
        sys.exit()

    chosen_pair = list(map(lambda x: x if x is None else os.path.join(chose_stat_p, x), chosen_file))
    print(chosen_pair)

    if chosen_pair[1] is None: #если доступна ТОЛЬКО краткая статистика, то не спрашиваем
        try:
            processed_data = BriefStatistics.process_file(chosen_pair[0])
        except Exception:
            print('Формат файла не корректен')
            sys.exit()

        processed_list = BriefStatistics.process_to_list(processed_data)
        processed_dict = BriefStatistics.process_to_dict(processed_data)
        brief = BriefStatistics(processed_list, processed_dict)

        with open('statistics.txt', 'w', encoding='utf-8') as statfile: #запись статистики в файл
            filename = Path(chosen_pair[0]).stem
            klass, name_work, date = filename.split('_')
            print(f'Краткая статистика по работе "{name_work}" класса {klass} за {date}:\n', file=statfile)
            print(f'Средняя оценка по классу: {brief.get_average()}', file=statfile)
            print(f'Медианное по классу: {brief.get_median()}', file=statfile)
            print(f'Отсутствующих учеников: {brief.get_amount_missings(processed_dict)}', file=statfile)
            print(f'Учеников, давших ответы не на все вопросы: {brief.get_amount_notfilled(processed_dict)}', file=statfile)
            print(file=statfile)
            print('Распределение оценок по классу:', file=statfile)
            for k, v in brief.get_counter().items():
                print(f'Оценок {k}: {v}', file=statfile)
            print(f'Больше всего оценок: {brief.get_most_common()}', file=statfile)
            print('Статистика успешно сгенерирована и записана в одноразовый файл statistics.txt')
            qst8 = Questions('Открыть файл?\n')
            if qst8.make_question():
                os.startfile('statistics.txt')
            else:
                sys.exit()


    else: #если доступна и та, и другая статистика
        pass





elif mainchoose in dct_variants['generate']:
    genchoose = input('Выберите режим генерации:\n'
          'Генерация по умолчанию(без точной настройки)[0]\n'
          'Генерация с ручной настройкой[1]\n').lower().strip()

    if genchoose in ('0', 'генерация по умолчанию'):
        name_of_work = input('Введите название работы: ')
        file_puples = input('Введите имя файла с именами учеников: ')
        count_strings = input('Введите количество необходимых полей для ответов: ')

        ch = Generator.checking_setings(file_puples, count_strings) #проверка корректности файлов
        if ch:
            print('Ошибки при введении данных:')
            for error in ch:
                print(error)
            sys.exit()
        else: #генерация файлов, см. docstrings
            g = Generator(file_puples, name_of_work)
            g.generate_dir_students()
            g.generate_file_students()
            g.fill_files_students(int(count_strings))
            g.create_answers_file(int(count_strings))
            g.create_marks_file()
            g.create_missings_file()


        print(f'Генерация файлов прошла успешно. Создана папка {name_of_work} с файлами учеников, файлы marks.txt, missings.txt и answers.txt с шаблонами.')

    elif genchoose in ('1', 'генерация с ручной настройкой'):
        print('Вы находитесь в режиме ручной настройки генерации. ')

        settings = SettingsGeneration()
        results = settings.run_survey() #запуск выбора настроек

        print('Настройки сохранены. Дождитесь завершения генерации.')

        #генерация файлов и папок по настройкам
        manset = Generator(name_work=results['name_of_work'], puples_file=results['pupe_file'])
        manset.generate_dir_students()
        manset.generate_file_students()
        manset.fill_files_students(results['count_strings_pup'])
        manset.create_answers_file(results['template_lines'], results['answers_file'])
        manset.create_marks_file(results['criteria_file'], results['grading_scale'])
        manset.create_missings_file(results['absentees_file'])

        print('Генерация прошла успешно.')


elif mainchoose in dct_variants['performance']:
    #режим случайно вызывает учеников либо по номерам, либо по именно через while
    print('Это режим, который вызывает учеников к доске в случайном порядке. ("stop" для остановки цикла) Подробнее см. инструкцию')
    user_input = input("Введите файл, число, или пропустите ввод: ")
    dev.write_to_file('user_input', user_input)
    iterable = RandomCall.process_input(user_input)

    if not iterable:
        print("Введённое значение не является числом или путём к файлу, или файл не существует")
        dev.write_to_file('error_input', True)
    else:
        ind = 0
        items = list(iterable)
        dev.write_to_file('items', items)
        random.shuffle(items)

        print(f'Ученик {items[ind]} идет первый:( ', end='')
        inputting = input().lower().strip()

        while inputting != 'stop':
            if ind == len(items) - 1:
                print('Вы всех спросили!')
                dev.write_to_file('happy_end', True)
                sys.exit()
            ind += 1
            print(f'Ученик {items[ind]} идет к доске ', end='')
            inputting = input().lower().strip()
            dev.write_to_file(f'inputting{ind}', inputting)
    dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


elif mainchoose in dct_variants['clear']:
    clearchoose = input('Выберите режим для сброса:\n'
                        'Сброс файлов[0]\n'
                        'Сброс файлов и папок[1]\n'
                        'Сброс до начальной конфигурации[2]\n').lower().strip()
    dev.write_to_file('clearchoose', clearchoose)


    with open('sys.json', 'r', encoding='utf-8') as f: #получение данных по умолчанию из sys.json
        smdct = json.load(f)
        files_to_delete_custom = {Path(smdct['answer']), Path(smdct['marks']), Path(smdct['missings'])}
    lst_of_files = ['answers.txt', 'marks.txt', 'missings.txt', 'sys.json', 'syslog.json']
    mapped_list_of_files = list(map(lambda x: Path(os.path.join(os.getcwd(), x)), lst_of_files))
    files_to_delete_default = set(mapped_list_of_files)
    files_to_delete = files_to_delete_default.union(files_to_delete_custom) #объединение множеств файлов по умолчанию и пользовательских


    if clearchoose in ('0', 'сброс файлов'):
        #несколько проверок на миссклик
        qst_sure = Questions('Вы уверены, что хотите удалить файлы? (если вы понятия не имеете, какие файлы будут удалены, рекомендуется прочесть инструкцию)\n')
        if qst_sure.make_question():
            sure2 = input('Для проверки на миссклик, введите любое натуральное число')
            if sure2.isdigit() and len(sure2) >= 2:
                dev.write_to_file('correct_check', True)
                delete = DeleteManager(files_to_delete)
                delete.delete_files() #удаление файлов
                dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            else:
                print('Проверка для удаления необходима, так что перезапустите режим, если все еще хотите удалить файлы')
                dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


    elif clearchoose in ('1', 'сброс файлов и папок'):
        #несколько проверок на миссклик и файл с паролем
        qst_sure = Questions('Вы уверены, что хотите сбросить файлы и папку archive? (если вы понятия не имеете, какие файлы будут удалены, рекомендуется прочесть инструкцию)\n')
        if qst_sure.make_question():
            dev.write_to_file('sure', True)
            right_psw = DeleteManager.create_file_delete()
            dev.write_to_file('right_psw', right_psw)
            print('Для проверки на миссклик программа создала в рабочей директории файл clear.txt с паролем для удаления. Пожалуйста, введите его.')
            user_psw = input('Введите пароль из файла: ').strip()
            dev.write_to_file('user_psw', user_psw)
            if user_psw == str(right_psw):
                files_to_delete.add('delete.txt') #добавление файла для удаления в множество
                files_to_delete.add(os.path.join(os.getcwd(), 'archive')) #добавление папки для удаления в множество
                delete = DeleteManager(files_to_delete)
                delete.delete_files_and_folders() #удаление файлов и папок
                print('Файлы и папка arhcive были удалены.')
                sys.exit()
            else:
                print('Неверный пароль. Попробуйте снова, если все еще хотите удалить файлы')
                dev.write_to_file('wrong_psw', True)
                dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                sys.exit()


    elif clearchoose in ('2', 'сброс до начальной конфигурации'):
        if not debug:
            #проверка прав доступа, режим доступен только в режиме разработчика
            print('У вас недостаточно прав для совершения этого действия. (подробнее см. инструкцию)')
            dev.write_to_file('rules_error', True)
        if debug:
            #проверка на миссклик, пароль и обратный отсчет для безопасности
            dev.write_to_file('password', random.randint(10000, 99999))
            with open('syslog.json', 'r', encoding='utf-8') as logfile:
                logdctdel = json.load(logfile)
                right_psw = logdctdel['password']
                user_psw = input('Введите пароль: ').strip()
                dev.write_to_file('user_psw', user_psw)
                if user_psw == str(right_psw):
                    dev.write_to_file('correct_psw', True)
                    for i in reversed(list(range(1, 6))):
                        print(f'Удаление всех файлов и папок рабочей директории через {i}')
                        time.sleep(1)
                    dev.write_to_file('au revour', True)
                    dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    DeleteManager.deep_delete() #удаление всего в рабочей директории, кроме py-файлов









# with open('students.json', 'r', encoding='utf-8') as f:
#     restored_students = json.load(f, object_hook=student_decoder)
#
# for key, student in restored_students.items():
#     print(key, student.__dict__)


