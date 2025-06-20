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



rep = Missings('auto', 'puples8v.txt', {'Вася Пупкин': 5, 'Петя Сидоров': 4, 'Маша Иванова': 3, 'Саша Петров': 2, 'Даша Сидорова': 3, 'Ваня Петров': 3, 'Аиша Муратова': 5})
print(rep.get_missings())


#D:/pythonProject/apotheosis/missings.txt