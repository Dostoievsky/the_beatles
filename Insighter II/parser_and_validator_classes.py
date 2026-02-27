import os.path
import os
import json
import re
from pathlib import Path
from settings_class import Settings




def load_sys_json():
    path = r'system_files/sys.json'
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return None


def merge_with_sys_json(input_data: dict, sys_data: dict | None) -> dict:
    result = {}

    for key, value in input_data.items():
        if value:
            result[key] = value
        elif sys_data and key in sys_data:
            result[key] = sys_data[key]
        else:
            result[key] = ''

    return result



class Validator:
    def __init__(self, data_dict):
        self.class_name = data_dict['class_name']
        self.answers_file = data_dict['answers_file']
        self.grades_file = data_dict['grades_file']
        self.works_folder = data_dict['works_folder']
        self.absents_file = ('auto' if not data_dict['absents_file'] else data_dict['absents_file'])
        self.date = data_dict['date']
        self.errors = []

    def validate_answers_file(self):
        if not self.answers_file:
            self.errors.append('Не передан файл с ответами')
            return {}

        lst_of_answ = []
        try:
            with open(self.answers_file, 'r', encoding='utf-8') as answfile:
                for line_num, line in enumerate(answfile, 1):
                    stripped_line = line.strip()
                    if not stripped_line:
                        continue
                    try:
                        _, answ = stripped_line.split(') ')
                        lst_of_answ.append(answ.strip())
                    except Exception as e:
                        msg = f'Ошибка в файле с ответами в строке {line_num}'
                        if Settings.show_warnings:
                            msg += f': {e}'
                        self.errors.append(msg)
        except FileNotFoundError:
            self.errors.append('Файл с ответами не найден')

        return dict(enumerate(lst_of_answ, 1))

    def validate_grades_file(self):
        if not self.grades_file:
            self.errors.append('Не передан файл с критериями оценивания')
            return {}

        grades_dict = {}
        pattern = r'^оценка \d+ от \d+ до \d+ баллов$'

        try:
            with open(self.grades_file, 'r', encoding='utf-8') as gradesfile:
                for line in gradesfile:
                    stripped_line = line.strip()
                    if not stripped_line:
                        continue
                    if not re.fullmatch(pattern, stripped_line):
                        self.errors.append(
                            'Ошибка в файле с критериями: неверный формат строки'
                        )
                        continue
                    _, grade, _, down, _, up, _ = stripped_line.split()
                    for i in range(int(down), int(up) + 1):
                        grades_dict[i] = int(grade)
        except FileNotFoundError:
            self.errors.append('Файл с критериями не найден')

        return grades_dict

    def validate(self):
        self.validate_answers_file()
        self.validate_grades_file()

        if not self.works_folder:
            self.errors.append('Не выбрана папка с работами')

        if not self.class_name:
            self.errors.append('Не указано название класса')

        if not self.date:
            self.errors.append('Не указана дата')

        return not bool(self.errors), self.errors



class Parser:
    def __init__(self, validated_answers_dict, validated_grades_dict,
                 absent_file, works_folder, date, class_name):
        self.answers_dict = validated_answers_dict or {}
        self.grades_dict = validated_grades_dict or {}
        self.absents_file = absent_file
        self.works_folder = works_folder
        self.date = date
        self.class_name = class_name

    def parse_absents_file(self):
        with open(self.absents_file, 'r', encoding='utf-8') as absent_file:
            return [x.strip() for x in absent_file.readlines()]

    def parse_answers_dict(self):
        return ','.join(self.answers_dict.values())

    def parse_grades_dict(self):
        return ','.join(f'{k}-{v}' for k, v in self.grades_dict.items())

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
        if not self.works_folder:
            return '', {}, []

        students_list = []
        dct_of_students_answers = {}
        folder_name = Path(self.works_folder).name

        for student_file in list(filter(lambda x: x.endswith('.txt'), os.listdir(self.works_folder))):
            full_path = os.path.join(self.works_folder, student_file)
            fullname = Path(full_path).stem
            try:
                name, surname = fullname.split('_')
            except ValueError:
                continue

            cleaned = f'{surname.capitalize()} {name.capitalize()}'
            answers = self.get_data_from_students_file(full_path)

            dct_of_students_answers[cleaned] = answers
            students_list.append(cleaned)

        return folder_name, dct_of_students_answers, students_list

    def parse_class_name(self):
        return self.class_name or ''

    def parse_date(self):
        return self.date or ''




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
# sys_data = load_sys_json()
# print(merge_with_sys_json(data_dict_, sys_data))
