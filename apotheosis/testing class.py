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
import json


class Student:
    def __init__(self, name, surname):
        self._name = name
        self._surname = surname
        self._file = None
        self._list_answers = None
        self._correct_answers = None
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
            "_mark": self._mark,
            "_missings": self._missings,
            "_flag_not_all": self._flag_not_all
        }


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


main_dct = {'klass': '11в',
            'name_work': 'Работа',
            'date': '16.06.2025',
            'answer': 'D:/pythonProject/apotheosis/answers.txt',
            'marks': 'D:/pythonProject/apotheosis/marks.txt',
            'students': 'D:/pythonProject/apotheosis/puples8v.txt',
            'missings': 'auto',
            'students_folder': 'D:/pythonProject/apotheosis/Каторжная работа 3'}


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


class Generator:
    def __init__(self, puples_file, name_work):
        self.puples_file = puples_file
        self.name_work = name_work
        self.lst_files = []

    def generate_dir_students(self):
        path = os.path.join(os.getcwd(), self.name_work)
        os.makedirs(path, exist_ok=True)
        self.lst_files = os.listdir(path)


    def generate_file_students(self):
        with open(self.puples_file, 'r', encoding='utf-8') as kfile:
            for fullname in kfile:
                name, surname = fullname.lower().strip().split()
                filename = f'{name}_{surname}.txt'
                with open(os.path.join(self.name_work, filename), 'w', encoding='utf-8') as f:
                    pass


    def fill_files_students(self, count_strings):
        for file in self.lst_files:
            fullpath = os.path.join(self.name_work, file)
            with open(fullpath, 'w', encoding='utf-8') as filepuple:
                for i in range(1, count_strings + 1):
                    print(f'{i}) ', file=filepuple)

    @staticmethod
    def create_answers_file(count_strings, filename='answers.txt', flag=True):
        with open(filename, 'w', encoding='utf-8') as fileansw:
            if flag:
                for i in range(1, count_strings + 1):
                    print(f'{i}) ', file=fileansw)


    @staticmethod
    def create_marks_file(filename='marks.txt', grade=5, flag=True):
        with open(filename, 'w', encoding='utf-8') as filemarks:
            if flag:
                for _ in range(grade-1):
                    print('оценка _ от _ до _ баллов', file=filemarks)





g = Generator('puples8v.txt', 'Полукаторжная работа 3')
g.generate_dir_students()
g.generate_file_students()
g.fill_files_students(10)
g.create_answers_file(10)
g.create_marks_file()
#dd