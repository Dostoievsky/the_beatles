#
# from pathlib import Path
# import re
# import os
#
# class Statistics:
#     def __init__(self, dir):
#         self.dir = dir
#         self.pairs = {}
#         self.printlist = []
#
#     @staticmethod
#     def extract_core_name(file_path):
#         stem = file_path.stem  # Имя файла без расширения
#         core_name = re.sub(r'^sysfile_', '', stem)  # Убираем приставку sysfile_
#         return core_name
#
#     def gen_pairs(self):
#         files = [Path(self.dir) / file for file in os.listdir(self.dir) if (Path(self.dir) / file).is_file()]
#         for file in files:
#             if file.suffix == '.txt':
#                 core_name = self.extract_core_name(file)
#                 matching_json = next((jf for jf in files if jf.suffix == '.json' and self.extract_core_name(jf) == core_name), None)
#                 self.pairs[file] = matching_json
#         return self.pairs
#
# dctchosenstat = {}
# st = Statistics(r'D:\pythonProject\apotheosis\archive\8в')
# pairs = st.gen_pairs()
#
# for index, (txt_file, json_file) in enumerate(pairs.items(), 1):
#     dctchosenstat[index] = (txt_file, json_file)
#
#
#
# for index, (txt_file, json_file) in dctchosenstat.items():
#     print(f"{txt_file.name}[{index}] ({'подробная статистика доступна' if json_file is not None else 'подробная статистика недоступна'})")
# ind = input('Выберите файл ')
# print(dctchosenstat[int(ind)])



# def csv_to_columns(file_path):
#     plain_list = []
#     with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
#         for _ in range(4):
#             next(csvfile)
#         for line in csvfile:
#             plain_list.append(line.strip())
#     return plain_list
#
# print(csv_to_columns(r'D:\pythonProject\apotheosis\archive\8в\8в_контрольная работа 5_30.06.2025.csv'))

import os
import csv

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

fd = Finding('Аиша Муратова')

dirpath = r'D:\pythonProject\apotheosis\archive\8в'
found_lst = fd.find_from_dir(dirpath)
for line, filepath in found_lst:
    print(f"В работе '{os.path.basename(filepath)}' - {line}")