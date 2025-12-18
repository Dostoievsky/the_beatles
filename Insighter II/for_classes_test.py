import os.path
import os
import json
import re
from pathlib import Path

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
        self.flag = True


    @staticmethod
    def get_settings():
        with open(os.path.join(os.getcwd(), r'system_files/settings.json'), 'r', encoding='utf-8') as settingsfile:
            return json.load(settingsfile)['show_warnings']


    def validate_answers_file(self):
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
                    if self.get_settings():
                        error = f'Ошибка в файле с ответами в строчке {line_num}. Проверьте правильность заполнения файла. Ошибка: {e}'
                    else:
                        error = f'Ошибка в файле с ответами в строчке {line_num}. Проверьте правильность заполнения файла.'
                    self.errors.append(error)
        dict_of_answ = dict(enumerate(lst_of_answ, 1))
        return dict_of_answ


    def validate_grades_file(self):
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


    def validate_works_folder(self):
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
        return folder_name, dct_of_students_answers


    def validate(self):
        self.validate_grades_file()
        self.validate_answers_file()
        return not bool(self.errors), self.errors


# data_dict_ = {'class_name': '9в', 'answers_file': 'D:/pythonProject/apotheosis/answers.txt', 'grades_file':
#     'D:/pythonProject/apotheosis/marks.txt', 'works_folder': 'D:/pythonProject/apotheosis/Провальная работа 4', 'absents_file': 'D:/pythonProject/apotheosis/my_missings.txt', 'date': '18.12.2025'}
# validator = Validator(data_dict_)
# print(validator.validate_answers_file())
# print(validator.validate_grades_file())
# print(validator.errors)
# print(validator.validate_works_folder())