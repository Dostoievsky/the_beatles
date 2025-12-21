import os.path
import os
import json
import re
from pathlib import Path
from something_classes_and_funcs import Settings


# flag_take_from_json = False
# with open(r'system_files/sys.json', 'r', encoding='utf-8') as f:
#     json_data = json.load(f)
#     if json_data:
#         flag_take_from_json = True



class Validator:
    def __init__(self, data_dict):
        self.class_name = data_dict['class_name']
        self.answers_file = data_dict['answers_file']
        self.grades_file = data_dict['grades_file']
        self.works_folder = data_dict['works_folder']
        self.absents_file = data_dict['absents_file']
        self.date = data_dict['date']
        self.errors = []
        self.previous_data = {}


    def validate_answers_file(self):
        if not self.answers_file and flag_take_from_json:
            self.answers_file = json_data.get('answers_file', )
        lst_of_answ = []
        with open(self.answers_file, 'r', encoding='utf-8') as answfile:
            for line_num, line in enumerate(answfile, 1):
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                try:
                    num_str, answ = stripped_line.split(') ')
                    lst_of_answ.append(answ.strip())
                except Exception as e:
                    if Settings.show_warnings:
                        error = f'Ошибка в файле с ответами в строчке {line_num}. Проверьте правильность заполнения файла. Ошибка: {e}'
                    else:
                        error = f'Ошибка в файле с ответами в строчке {line_num}. Проверьте правильность заполнения файла.'
                    self.errors.append(error)
        dict_of_answ = dict(enumerate(lst_of_answ, 1))
        return dict_of_answ


    def validate_grades_file(self):
        if not self.grades_file:
            return False
        grades_dict = {}
        with open(self.grades_file, 'r', encoding='utf-8') as gradesfile:
            pattern = r'^оценка \d+ от \d+ до \d+ баллов$'
            for line in gradesfile:
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                if not re.fullmatch(pattern, stripped_line):
                    self.errors.append(f'Ошибка в файле с оценками, одна из строк не удовлетворяет формату. Проверьте правильность заполнения файла.')
                    return False
                _, grade, _, down, _, up, _ = stripped_line.split()
                for i in range(int(down), int(up) + 1):
                    grades_dict[i] = int(grade)
            return grades_dict





    def validate(self):
        self.validate_grades_file()
        self.validate_answers_file()
        return not bool(self.errors), self.errors


class Parser:
    def __init__(self, validated_answers_dict, validated_grades_dict, absent_file, works_folder, date, class_name):
        self.answers_dict = validated_answers_dict
        self.grades_dict = validated_grades_dict
        self.absents_file = absent_file
        self.works_folder = works_folder
        self.date = date
        self.class_name = class_name

    def parse_answers_dict(self):
        return ','.join(list(self.answers_dict.values()))

    def parse_grades_dict(self):
        lst = []
        for k, v in self.grades_dict.items():
            lst.append(f'{k}-{v}')
        return ','.join(lst)


    @staticmethod
    def get_data_from_students_file(path):
        lst_of_smth_student = []
        with open(path, 'r', encoding='utf-8') as student_file:
            for line in student_file:
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                try:
                    num_str, answ = stripped_line.split(') ')
                    lst_of_smth_student.append(answ.strip())
                except Exception:
                    continue
        return lst_of_smth_student


    def parse_works_folder(self):
        print('Парсируем папку с работами')
        if not self.works_folder:
            return False
        students_list = []
        dct_of_students_answers = {}
        folder = self.works_folder
        folder_name = Path(folder).name
        for student_file in os.listdir(folder):
            full_path = os.path.join(folder, student_file)
            fullname = Path(full_path).stem
            name, surname = fullname.split('_')
            cleaned_fullname = f'{surname.capitalize()} {name.capitalize()}'
            lst_of_student_answers = self.get_data_from_students_file(full_path)
            dct_of_students_answers[cleaned_fullname] = lst_of_student_answers
            students_list.append(cleaned_fullname)
        return folder_name, dct_of_students_answers, students_list


    def parse_absents_file(self):
        if not self.absents_file:
            return 'auto'
        with open(self.absents_file, 'r', encoding='utf-8') as absentsfile:
            return ','.join(list(map(lambda x: x.strip(), absentsfile.readlines())))


    def parse_class_name(self):
        if not self.class_name:
            return False
        return self.class_name


    def parse_date(self):
        if not self.date:
            return False
        return self.date




# data_dict_ = {'class_name': '9в', 'answers_file': 'D:/pythonProject/apotheosis/answers.txt', 'grades_file':
#     'D:/pythonProject/apotheosis/marks.txt', 'works_folder': 'D:/pythonProject/apotheosis/Провальная работа 4', 'absents_file': 'D:/pythonProject/apotheosis/my_missings.txt', 'date': '18.12.2025'}
# validator = Validator(data_dict_)
# print(validator.validate_answers_file())
# print(validator.validate_grades_file())
# print(validator.errors)
# parser = Parser(validator.validate_answers_file(), validator.validate_grades_file(), validator.absents_file,
#                 validator.works_folder, validator.date, validator.class_name)
# print(parser.parse_absents_file())
# print(parser.parse_works_folder())
# print(parser.parse_date())
# print(parser.parse_class_name())
# print(parser.parse_grades_dict())
# print(parser.parse_answers_dict())
