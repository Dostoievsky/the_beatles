# import os
# from datetime import datetime
# import json
# import statistics
# from collections import namedtuple
# import tkinter as tk
# from tkinter import filedialog
# import json
# import re
#
#
# class StatisticForPuple:
#
#     def __init__(self, name, surname, json_file=None):
#         self.name = name
#         self.surname = surname
#         self.json_file = json_file
#         self.mark = 0
#         self.answers = []
#         self.correct_answers = 0
#
#     def get_stat(self):
#         if self.json_file is None:
#             return -1
#         else:
#             with open(self.json_file, 'r', encoding='utf-8') as file:
#                 dct = json.load(file)
#                 return dct[f'{self.name} {self.surname}']
#
#     def get_mark(self):
#         if self.get_stat() == -1:
#             return -1
#         else:
#             self.mark = self.get_stat()[2]
#             return self.get_stat()[2]
#
#     def get_answers(self):
#         if self.get_stat() == -1:
#             return -1
#         else:
#             self.answers = self.get_stat()[0]
#             return self.get_stat()[0]
#
#     def get_correct_answers(self):
#         if self.get_stat() == -1:
#             return -1
#         else:
#             self.correct_answers = self.get_stat()[1]
#             return self.get_stat()[1]
#
#
# '''
# json_file = 'sysfile_контрольная работа 5_09.09.25.json'
# with open(json_file, 'r', encoding='utf-8') as file:
#     data = json.load(file)
#     with open('test.txt', 'w', encoding='utf-8') as f:
#         for k in data.keys():
#             puple = StatisticForPuple(k.split()[0], k.split()[1], json_file)
#             print(puple.name, puple.surname, file=f)
#             print(puple.get_mark(), file=f)
#             print(puple.get_answers(), file=f)
#             print(puple.get_correct_answers(), file=f)
#             print(f'----------------------------------------------', file=f)
# '''
import json
import random
import sys


class Questions:
    def __init__(self, question, tuple_of_variants=('1', 'lf', 'да', True)):
        self.question = question
        self.tuple_of_variants = tuple_of_variants

    def make_question(self):
        if input(self.question) in self.tuple_of_variants:
            return True
        else:
            return False

    # def make_variants_question(self, variants, digits):
    #     print(self.question)
    #     for var, digit in zip(variants, digits):
    #         print(f'{var}[{digit}]')
    #     answ = input().strip().lower()
    #
    #     if answ in list(zip(variants, digits))[0]:
    #         return 0
    #
    #     elif answ in list(zip(variants, digits))[1]:
    #         return 1
    #
    #     elif answ in list(zip(variants, digits))[2]:
    #         return 2
    #
    #     else:
    #         return -1

#
# class Sorted:
#     def __init__(self, dct):
#         self.dct = dct
#
#     def sort_by_default(self):
#         return self.dct
#
#     def sort_by_name(self):
#         sort_dct_items = sorted(self.dct.items(), key=lambda x: x[0])
#         return sort_dct_items
#
#     def sort_by_mark_best(self):
#         sort_dct_items = sorted(self.dct.items(), key=lambda x: -x[1])
#         return sort_dct_items
#
#     def sort_by_mark_worst(self):
#         sort_dct_items = sorted(self.dct.items(), key=lambda x: x[1])
#         return sort_dct_items
#
# dct = {'Вася Пупкин': 5, 'Петя Сидоров': 4, 'Маша Иванова': 3, 'Саша Петров': 2, 'Даша Сидорова': 3, 'Ваня Петров': 4, 'Маша Петрова': 5, 'Даша Петрова': 4, 'Ваня Сидоров': 3, 'Саша Иванов': 2, 'Вася Сидоров': 5, 'Петя Иванов': 4, 'Маша Сидорова': 3, 'Даша Иванова': 2, 'Ваня Иванов': 3, 'Саша Пупкин': 4,}
# sorted_dct = Sorted(dct)
# print(sorted_dct.sort_by_name())
# print(sorted_dct.sort_by_mark())
# print(sorted_dct.sort_by_default())
#
#
#
#
# qst2 = input('Выберите режим сортировки:\n'
#                      '1. По умолчанию[0]\n'
#                      '2. По именам[1]\n'
#                      '3. По оценкам[2]\n')
import re

class Answers:

    def __init__(self, file):
        self.file = file
        self.answers_dct = {}

    def get_right_answers(self):
        with open(self.file, 'r', encoding='utf-8') as file:
            for line in file:
                index, answer = line.split(') ')
                self.answers_dct[index.strip()] = answer.strip()
        return self.answers_dct


answers = Answers('answers.txt')
# print(answers.get_right_answers())

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

m = Marks('marks.txt', 0)

# try:
#     print(m.get_marks())
# except ValueError as e:
#     print(e)
#
    #def get_marks(self):
    #     if self.check_marks() == 1:
    #         print('Файл прописан в баллах.')
    #     elif self.check_marks() == 2:
    #         print('Файл прописан в оценках.')
    #     else:
    #         print('Файл не прописан в баллах и в оценках.')
# m = Marks('marks.txt', False)
#
# try:
#     g = m.check_marks()
#     print(g)
#     # print(m.get_marks())
# except ValueError as e:
#     print(e)


# оценка 5 от 10 до 10 баллов
# оценка 4 от 7 до 9 баллов
# оценка 3 от 5 до 6 баллов
# оценка 2 от 0 до 4 баллов


# class Missings:
#     def __init__(self, string, puple_file, puples_dict):
#         self.string = string
#         self.puple_file = puple_file
#         self.puples_dict = puples_dict
#
#     def get_missings(self):
#         res_lst = []
#         if self.string.lower().strip() == 'auto':
#             with open(self.puple_file, 'r', encoding='utf-8') as pup_file:
#                 puples = map(lambda x: x.strip(), pup_file.readlines())
#                 for puple in puples:
#                     if puple not in self.puples_dict.keys():
#                         res_lst.append(puple)
#                 return res_lst
#         else:
#             with open(self.string, 'r', encoding='utf-8') as miss_file:
#                 for line in miss_file.readlines():
#                     res_lst.append(line.strip())
#                 return res_lst
#
#
#
# rep = Missings('auto', '.txt', {'Вася Пупкин': 5, 'Петя Сидоров': 4, 'Маша Иванова': 3, 'Саша Петров': 2, 'Даша Сидорова': 3, 'Ваня Петров': 3, 'Аиша Муратова': 5})
# print(rep.get_missings())
#

#D:/pythonProject/apotheosis/missings.txt

#
# import os
# import sys
#
#
# # noinspection PyTypedDict
# class SettingsGeneration:
#     def __init__(self):
#         self.inputs = {
#             "name_of_work": None,
#             "pupe_file": None,
#             "count_strings_pup": None,
#             "answers_file": None,
#             "template_lines": None,
#             "criteria_file": None,
#             "grading_scale": None,
#             "absentees_file": None
#         }
#
#     class Questions:
#         def __init__(self, question, tuple_of_variants=('1', 'lf', 'да')):
#             self.question = question
#             self.tuple_of_variants = tuple_of_variants
#
#         def make_question(self):
#             if input(self.question).strip().lower() in self.tuple_of_variants:
#                 return True
#             else:
#                 return False
#
#     @staticmethod
#     def validate_integer(prompt):
#         while True:
#             try:
#                 return abs(int(input(prompt)))
#             except ValueError:
#                 print("Введите корректное целое число.")
#
#     def step_get_name_of_work(self):
#         self.inputs["name_of_work"] = input("Введите название работы: ").strip()
#
#     def step_get_pupe_file(self):
#         sm = self.Questions("Нужны ли файлы учеников? ")
#         if sm.make_question():
#             pupe_file = input("Введите название файла учеников: ").strip()
#             if not os.path.exists(pupe_file):
#                 print(f"Файл {pupe_file} не найден.")
#                 sys.exit()
#             self.inputs["pupe_file"] = pupe_file
#
#             sm = self.Questions("Нужны ли строки для ответов в файлах учеников? ")
#             if sm.make_question():
#                 self.inputs["count_strings_pup"] = self.validate_integer("Введите количество строк для ответов: ")
#
#     def step_get_answers_file(self):
#         sm = self.Questions("Нужен ли файл с ответами? ")
#         if sm.make_question():
#             self.inputs["answers_file"] = input("Введите название файла с ответами: ").strip()
#
#             sm = self.Questions("Создать файл по шаблону? ")
#             if sm.make_question():
#                 self.inputs["template_lines"] = self.validate_integer("Введите количество строк для шаблона: ")
#
#     def step_get_criteria_file(self):
#         sm = self.Questions("Нужен ли файл с критериями оценивания? ")
#         if sm.make_question():
#             self.inputs["criteria_file"] = input("Введите название файла с критериями: ").strip()
#
#             sm = self.Questions("Создать файл по шаблону? ")
#             if sm.make_question():
#                 self.inputs["grading_scale"] = self.validate_integer("Введите шкалу оценивания: ")
#
#     def step_get_absentees_file(self):
#         sm = self.Questions("Нужен ли файл с отсутствующими? ")
#         if sm.make_question():
#             self.inputs["absentees_file"] = input("Введите название файла с отсутствующими: ").strip()
#
#     def run_survey(self):
#         self.step_get_name_of_work()
#         self.step_get_pupe_file()
#         self.step_get_answers_file()
#         self.step_get_criteria_file()
#         self.step_get_absentees_file()
#         return self.inputs
#
#
#
# settings = SettingsGeneration()
# results = settings.run_survey()
#
#
# for variable, value in results.items():
#     print(f"{variable}: {value}")


# def generate_grading_scale(num_tasks):
#     boundaries = []
#
#     percent_boundaries = [(90, 100), (75, 89), (60, 74), (0, 59)]
#
#     for lower_percent, upper_percent in percent_boundaries:
#         min_correct = int((lower_percent / 100) * num_tasks)
#         max_correct = int((upper_percent / 100) * num_tasks)
#         if max_correct >= num_tasks:
#             max_correct = num_tasks
#         boundaries.append((min_correct, max_correct))
#
#     with open('grading_scale.txt', 'w', encoding='utf-8') as gs_file:
#         for i, boundary in enumerate(boundaries):
#             low, high = boundary
#             grade = 5 - i
#             gs_file.write(f"оценка {grade} от {low} до {high} баллов\n")
#
#
# num_tasks = 20
# generate_grading_scale(num_tasks)
#

# import json
#
# class DebugMode:
#     def __init__(self, debug):
#         self.debug = debug
#
#     def write_to_file(self, attr, value):
#         if self.debug:
#             with open('syslog.json', 'r', encoding='utf-8') as file:
#                 data = json.load(file)
#
#             data[attr] = value
#
#             with open('syslog.json', 'w', encoding='utf-8') as file:
#                 json.dump(data, file, indent=4, ensure_ascii=False)
#
#
# debug_mode = DebugMode(debug=True)
# debug_mode.write_to_file('test_attr', 'test_value')
# debug_mode.write_to_file('test_attr2', 'test_value2')
# debug_mode.write_to_file('test_attr3', 'test_value3')
# debug_mode.write_to_file('debug', False)



import functools

# class RandomCall:
#     def __init__(self, arg):
#         if isinstance()
#
# rc = RandomCall()
# t0 = input('Введите что-нибудь: ')
#
#
#
# r1 = rc.random_call(t0)
# print(r1)
#
#

from pathlib import Path
import random

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




user_input = input("Введите значение: ")
iterable = RandomCall.process_input(user_input)

if not iterable:
   print("Введённое значение не является числом или путём к файлу, или файл не существует")
else:
    ind = 0
    items = list(iterable)
    random.shuffle(items)

    print(f'Ученик {items[ind]} идет первый:(', end='')
    inputting = input()

    while inputting != 'stop':
        if ind == len(items) - 1:
            print('Вы всех спросили!')
            sys.exit()
        ind += 1
        print(f'Ученик {items[ind]} идет к доске', end='')
        inputting = input()


