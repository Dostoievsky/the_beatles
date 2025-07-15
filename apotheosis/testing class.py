# class Student:
#
#     def __init__(self, name, surname):
#         self.name = name
#         self.surname = surname
#         self.file = None
#         self.list_answers = None
#         self.correct_answers = None
#         self.mark = None
#
# dct = {
#     'John Michael': 'john.txt',
#     'Bob Christian': 'bob.txt',
#     'Mike Victor': 'mike.txt',
#     'Jane Rose': 'jane.txt',
#     'Joe Kevin': 'joe.txt',
#     'Mary Jane': 'mary.txt'
# }
# bdic = {}
#
# for k, v in dct.items():
#     bdic[k] = Student(k.split()[0], k.split()[1])
#
# for k, v in bdic.items():
#     v.file = dct[k]
#
# print(bdic)
#
# # for k, v in bdic.items():
# #     print(v.name, v.surname, v.file, v.list_answers)

# import json
#
# class Student:
#     def __init__(self, name, surname):
#         self.name = name
#         self.surname = surname
#         self.file = None
#         self.list_answers = None
#         self.correct_answers = None
#         self.mark = None
#
#
# class StudentJSONEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Student):
#             return {'__student__': True,
#                    'name': obj.name,
#                    'surname': obj.surname,
#                    'file': obj.file,
#                    'list_answers': obj.list_answers,
#                    'correct_answers': obj.correct_answers,
#                    'mark': obj.mark}
#         return super().default(obj)
#
#
# def object_hook(dct):
#     if '__student__' in dct:
#         return Student(dct['name'], dct['surname'])
#     return dct
#
#
# # Исходные данные
# dct = {
#     'John Michael': 'john.txt',
#     'Bob Christian': 'bob.txt',
#     'Mike Victor': 'mike.txt',
#     'Jane Rose': 'jane.txt',
#     'Joe Kevin': 'joe.txt',
#     'Mary Jane': 'mary.txt'
# }
#
#
# bdic = {}
# for k, v in dct.items():
#     bdic[k] = Student(*k.split())
#     bdic[k].file = v
# print(bdic['John Michael'].__dict__)
#
# # Сериализуем в JSON
# json_data = json.dumps(bdic, cls=StudentJSONEncoder, indent=4)
#
# # Сохраняем в файл
# with open('students.json', 'w') as f:
#     f.write(json_data)

#
# with open('students.json', 'r') as f:
#     raw_json_data = f.read()
#
# # Восстанавливаем объекты
# loaded_bdic = json.loads(raw_json_data, object_hook=object_hook)
#
# # Проверяем восстановленный словарь
# for k, v in loaded_bdic.items():
#     print(f'{k}: {v.__dict__}')

import os
# import json
#
#
# class Student:
#     def __init__(self, name, surname):
#         self._name = name
#         self._surname = surname
#         self._file = None
#         self._list_answers = None
#         self._correct_answers = None
#         self._mark = None
#         self._missings = False
#         self._flag_not_all = False
#
#     @property
#     def name(self):
#         return self._name
#
#     @name.setter
#     def name(self, new_name):
#         self._name = new_name
#
#     @property
#     def surname(self):
#         return self._surname
#
#     @surname.setter
#     def surname(self, new_surname):
#         self._surname = new_surname
#
#     @property
#     def file(self):
#         return self._file
#
#     @file.setter
#     def file(self, new_file):
#         self._file = new_file
#
#     @property
#     def list_answers(self):
#         return self._list_answers
#
#     @list_answers.setter
#     def list_answers(self, new_list_answers):
#         self._list_answers = new_list_answers
#
#     @property
#     def correct_answers(self):
#         return self._correct_answers
#
#     @correct_answers.setter
#     def correct_answers(self, new_correct_answers):
#         self._correct_answers = new_correct_answers
#
#     @property
#     def mark(self):
#         return self._mark
#
#     @mark.setter
#     def mark(self, new_mark):
#         self._mark = new_mark
#
#     @property
#     def flag_not_all(self):
#         return self._flag_not_all
#
#     @flag_not_all.setter
#     def flag_not_all(self, value):
#         self._flag_not_all = value
#
#     @property
#     def missings(self):
#         return self._missings
#
#     @missings.setter
#     def missings(self, value):
#         self._missings = value
#
#     def to_json(self):
#         return {
#             "__class__": "Student",
#             "_name": self._name,
#             "_surname": self._surname,
#             "_file": self._file,
#             "_list_answers": self._list_answers,
#             "_correct_answers": self._correct_answers,
#             "_mark": self._mark,
#             "_missings": self._missings,
#             "_flag_not_all": self._flag_not_all
#         }
#
#
# class StudentJSONEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Student):
#             return {'__student__': True,
#                     'name': obj.name,
#                     'surname': obj.surname,
#                     'file': obj.file,
#                     'list_answers': obj.list_answers,
#                     'correct_answers': obj.correct_answers,
#                     'mark': obj.mark}
#         return super().default(obj)
#
#
# main_dct = {'klass': '11в',
#             'name_work': 'Работа',
#             'date': '16.06.2025',
#             'answer': 'D:/pythonProject/apotheosis/answers.txt',
#             'marks': 'D:/pythonProject/apotheosis/marks.txt',
#             'students': 'D:/pythonProject/apotheosis/puples8v.txt',
#             'missings': 'auto',
#             'students_folder': 'D:/pythonProject/apotheosis/Каторжная работа 3'}
#

# class FileManager:
#       def __init__(self, dct):
#             self.dct = dct
#
#       def create_json_filename(self):
#             fullpath = os.path.join(os.getcwd(), f'archive/{self.dct["klass"]}')
#             filenamestat = f"sysfile_{self.dct['klass'].lower().strip()}_{self.dct['name_work'].lower().strip()}_{self.dct['date']}.json"
#             fullfilepath = os.path.join(fullpath, filenamestat)
#             return fullfilepath
#
#       def create_directory(self):
#             halfpath = os.path.join('archive', self.dct["klass"])
#             fullpath = os.path.join(os.getcwd(), halfpath)
#
#             os.makedirs(fullpath, exist_ok=True)
#
#             fullnamework = f'{self.dct["klass"]}_{self.dct["name_work"].lower().strip()}_{self.dct["date"]}.txt'
#             return os.path.join(fullpath, fullnamework)
#
#
# stat = FileManager(main_dct)
# fullfilepath = stat.create_json_filename()
# with open(fullfilepath, 'w', encoding='utf-8') as f:
#       json.dump(main_dct, f, cls=StudentJSONEncoder, ensure_ascii=False, indent=4)
#
# filee = FileManager(main_dct)
# g = filee.create_directory()
# with open(g, 'w', encoding='utf-8') as file:
#       file.write('Работа')
#

# class FileManager:
#     def __init__(self, dct):
#         self.dct = dct
#
#     def create_json_filename(self):
#         fullpath = os.path.join(os.getcwd(), f'archive/{self.dct["klass"]}')
#         os.makedirs(fullpath, exist_ok=True)
#         filenamestat = f"sysfile_{self.dct['klass'].lower().strip()}_{self.dct['name_work'].lower().strip()}_{self.dct['date']}.json"
#         fullfilepath = os.path.join(fullpath, filenamestat)
#         return fullfilepath
#
#     def create_text_file_path(self):
#         halfpath = os.path.join('archive', self.dct["klass"])
#         fullpath = os.path.join(os.getcwd(), halfpath)
#         os.makedirs(fullpath, exist_ok=True)
#         fullnamework = f'{self.dct["klass"]}_{self.dct["name_work"].lower().strip()}_{self.dct["date"]}.txt'
#         return os.path.join(fullpath, fullnamework)
#
# fm = FileManager(main_dct)
#
# json_filepath = fm.create_json_filename()
# with open(json_filepath, 'w', encoding='utf-8') as f:
#     json.dump(main_dct, f, cls=StudentJSONEncoder, ensure_ascii=False, indent=4)
#
# text_filepath = fm.create_text_file_path()
# with open(text_filepath, 'w', encoding='utf-8') as file:
#     file.write('Работа')

# class Finding:
#
#     def __init__(self, name):
#         self.name = name
#         self.lst_found = []
#
#     def find_from_dir(self, dirpath):
#         for root, dirs, files in os.walk(dirpath):
#             for file in files:
#                 if file.endswith('.json'):
#                     continue
#                 filepath = os.path.join(root, file)
#                 with open(filepath, 'r', encoding='utf-8') as filefind:
#                     for line in filefind:
#                         if line.strip().lower().startswith(self.name.lower()):
#                             self.lst_found.append((line, os.path.basename(filepath)))
#                             continue
#         if self.lst_found:
#             return self.lst_found
#         return -1
#
#
#     def find_from_file(self, filepath):
#         with open(filepath, 'r', encoding='utf-8') as filefind:
#             for line in filefind:
#                 if line.strip().lower().startswith(self.name.lower()):
#                     return line, os.path.basename(filepath)
#         return -1
#
#
#
# f = Finding('аиша Муратова')
# print(f.find_from_dir(r'D:\pythonProject\apotheosis\archive\8в'))
# g = Finding('АИша МУРАТОВА')
# print(g.find_from_file(r'D:\pythonProject\apotheosis\archive\8в\каторжная работа 3 за 03.05.25.txt'))


# class Generator:
#     def __init__(self, puples_file, name_work):
#         self.puples_file = puples_file
#         self.name_work = name_work
#         self.lst_files = []
#
#     def generate_dir_students(self):
#         path = os.path.join(os.getcwd(), self.name_work)
#         os.makedirs(path, exist_ok=True)
#
#
#
#     def generate_file_students(self):
#         if self.puples_file is not None:
#             with open(self.puples_file, 'r', encoding='utf-8') as kfile:
#                 for fullname in kfile:
#                     name, surname = fullname.lower().strip().split()
#                     filename = f'{name}_{surname}.txt'
#                     with open(os.path.join(self.name_work, filename), 'a', encoding='utf-8') as f:
#                         pass
#         else:
#             pass
#         path = os.path.join(os.getcwd(), self.name_work)
#         self.lst_files = os.listdir(path)
#
#     def fill_files_students(self, count_strings):
#         for file in self.lst_files:
#             fullpath = os.path.join(self.name_work, file)
#             with open(fullpath, 'w', encoding='utf-8') as filepuple:
#                 if count_strings is not None:
#                     for i in range(1, count_strings + 1):
#                         print(f'{i}) ', file=filepuple)
#                 else:
#                     pass
#
#     @staticmethod
#     def create_answers_file(count_strings, filename='answers.txt'):
#         if filename is not None:
#             with open(filename, 'w', encoding='utf-8') as fileansw:
#                 if count_strings is not None:
#                     for i in range(1, count_strings + 1):
#                         print(f'{i}) ', file=fileansw)
#
#
#
#     @staticmethod
#     def create_marks_file(filename='marks.txt', grade=5):
#         if filename is not None:
#             with open(filename, 'w', encoding='utf-8') as filemarks:
#                 if grade is not None:
#                     for _ in range(grade-1):
#                         print('оценка _ от _ до _ баллов', file=filemarks)
#
#     @staticmethod
#     def checking_setings(puples_file, count_strings):
#         lst_errors = []
#         if not os.path.exists(os.path.join(os.getcwd(), puples_file)):
#             lst_errors.append(f'Файл {puples_file} не найден.')
#         if not count_strings.isdigit():
#             lst_errors.append(f'Количество строк должно быть целым числом.')
#         if lst_errors:
#             return lst_errors
#         return False
#
# name_of_work = input('Введите название работы: ')
# file_puples = input('Введите имя файла с именами учеников: ')
# count_strings = input('Введите количество необходимых полей для ответов: ')
#
# ch = Generator.checking_setings(file_puples, count_strings)
# if ch:
#     print('Ошибки при введении данных:')
#     for error in ch:
#         print(error)
# else:
#     g = Generator(file_puples, name_of_work)
#     g.generate_dir_students()
#     g.generate_file_students()
#     g.fill_files_students(int(count_strings))
#     g.create_answers_file(int(count_strings))
#     g.create_marks_file()





# import signal
#
#
# def handle_stop_signal(signum, frame):
#     print("\nПрограмма остановлена.")
#     exit(0)
#
# # Установка обработчика сигналов
# signal.signal(signal.SIGINT, handle_stop_signal)  # Ctrl+C
# signal.signal(signal.SIGTERM, handle_stop_signal)
#
# f = input('Введите что-нибудь и нажмите Enter: ')
# f1 = input('Введите что-нибудь еще раз и нажмите Enter: ')
# print(f+f1)

from abc import ABC, abstractmethod
from pathlib import Path
from collections import Counter
import statistics as stat
import sys

class Statistics:
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




class Compare:
    def __init__(self, chosen_dir):
        self.chosen_dir = chosen_dir
        self.filtered_files = []
        self.json_files_not_rep = set()

    def filter_files(self, pairs):
        for pair in pairs:
            if pair[1] is not None:
                pair = (os.path.join(self.chosen_dir, pair[0]), os.path.join(self.chosen_dir, pair[1]))
                self.filtered_files.append(pair)

    def split_chosen(self, files_str, compdct):
        for num in files_str.split():
            try:
                num = int(num)
            except:
                print('Некорректный ввод, введите только числа')
                sys.exit()

            try:
                json = compdct[num][1]
                self.json_files_not_rep.add(json)
            except KeyError:
                print('Некорректный ввод, вы ввели номер несуществующего файла')
                sys.exit()



chosen_dir = r'D:\pythonProject\apotheosis\archive\8в'
statcomp = Statistics(chosen_dir)
statcomp.set_pairs(chosen_dir)
print(*statcomp.pairs, sep='\n')
print()
comp = Compare(chosen_dir)
comp.filter_files(statcomp.pairs)

compdct = {}
for index, compfile in enumerate(comp.filtered_files, 1):
    print(f'{compfile[0]}[{index}]')
    compdct[index] = compfile
print()
print(compdct)
files = input('Введите номера файлов: ').strip()

comp.split_chosen(files, compdct)
print(*comp.json_files_not_rep, sep='\n')






