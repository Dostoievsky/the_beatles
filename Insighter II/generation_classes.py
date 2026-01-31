import os
from pathlib import Path
import re
from database_and_settings_classes import Database
import json

class ParserUIData:
    def __init__(self, data_dict, gen_db):
        self._absents_file_create = None #True/False
        self._grade_file_fill = None #scale/False
        self._grade_file_create = None #name/False
        self._answers_file_fill = None #lines/False
        self._answers_file_create = None #name/False
        self._student_files_fill = None #True/False
        self._work_name = None #name/False
        self._class = []
        self.data_dict = data_dict
        self.gen_db = gen_db
        self.mode = data_dict['mode']


    def parse_dict_manual(self):
        self._work_name = (self.data_dict['work_name'] if self.data_dict['work_name'] else False)
        if Path(self.data_dict['class']).is_file():
            self._class = list(self.parse_class_file(self.data_dict['class']))
        else:
            self._class = self.gen_db.get_students_of_class(self.data_dict['class'], flag='names')
        self._student_files_fill = (self.data_dict['students_lines'] if self.data_dict['fill_students'] else False)
        self._answers_file_create = (self.data_dict['answers_name'] if self.data_dict['answers'] else False)
        self._answers_file_fill = (self.data_dict['answers_lines'] if self.data_dict['answers'] else False)
        self._grade_file_create = (self.data_dict['criteria_name'] if self.data_dict['criteria'] else False)
        self._grade_file_fill = (self.data_dict['criteria_scale'] if self.data_dict['criteria'] else False)
        self._absents_file_create = (self.data_dict['absents_name'] if self.data_dict['absents'] else False)


    def parse_dict_fast(self):
        self._work_name = (self.data_dict['work_name'] if self.data_dict['work_name'] else False)
        if Path(self.data_dict['class']).is_file():
            self._class = list(self.parse_class_file(self.data_dict['class']))
        else:
            self._class = self.gen_db.get_students_of_class(self.data_dict['class'], flag='names')
        self._student_files_fill = self.data_dict['students_lines']
        self._answers_file_create = 'answers.txt'
        self._answers_file_fill = self.data_dict['answers_lines']
        self._grade_file_create = 'grades.txt'
        self._grade_file_fill = 5
        self._absents_file_create = 'absents.txt'


    @staticmethod
    def parse_class_file(class_file):
        regex = r'[А-Яа-я]+ [А-Яа-я]+'
        lst = []
        with open(class_file, 'r', encoding='utf_8') as file:
            for line in [row.strip() for row in file.readlines()]:
                if re.fullmatch(regex, line):
                    lst.append(line)
        return lst


    def get_data(self):
        return self.__dict__


class Generator:
    def __init__(self, plan_data):
        self.plan_data = plan_data

    @staticmethod
    def parse_filename(filename):
        if filename.endswith('.txt'):
            return filename
        return f'{filename}.txt'

    def generate_answers_file(self):
        with open(self.parse_filename(self.plan_data['_answers_file_create']), 'w', encoding='utf_8') as file:
            if self.plan_data['_answers_file_fill']:
                for i in range(1, int(self.plan_data['_answers_file_fill']) + 1):
                    print(f'{i}) ', file=file)

    def generate_grades_file(self):
        with open(self.parse_filename(self.plan_data['_grade_file_create']), 'w', encoding='utf_8') as file:
            if self.plan_data['_grade_file_fill']:
                for i in list(range(2, int(self.plan_data['_grade_file_fill'])+1))[::-1]:
                    print(f'Оценка {i} от _ до _ баллов', file=file)

    def generate_absents_file(self):
        with open(self.parse_filename(self.plan_data['_absents_file_create']), 'w', encoding='utf_8') as _:
            pass

    def create_and_fill_students_folder(self):
        print('call')
        path = os.path.join(os.getcwd(), self.plan_data['_work_name'])
        os.makedirs(path, exist_ok=True)
        print('call1')
        for student in self.plan_data['_class']:
            name, surname = map(lambda x: x.strip().lower(), student.split(' '))
            student_file_path = os.path.join(path, f'{name}_{surname}.txt')
            with open(student_file_path, 'w', encoding='utf_8') as file:
                if self.plan_data['_student_files_fill']:
                    for i in range(1, int(self.plan_data['_student_files_fill']) + 1):
                        print(f'{i}) ', file=file)

    def run_generation(self):
        try:
            if self.plan_data['_answers_file_create']:
                self.generate_answers_file()
            if self.plan_data['_grade_file_create']:
                self.generate_grades_file()
            if self.plan_data['_absents_file_create']:
                self.generate_absents_file()
            if self.plan_data['_work_name']:
                self.create_and_fill_students_folder()
        except Exception as e:
            print(f'Ошибка при генерации {e}')


def read_pattern(filename='patterns.json'):
    try:
        fullpath = os.path.join(os.getcwd(), 'system_files', filename)
        with open(fullpath, 'r', encoding='utf_8') as file:
            data = json.load(file)
            return data
    except:
        return {}

dct = {'mode': 'Ручная генерация', 'work_name': 'попа знатная', 'class': '9j',
  'fill_students': True, 'students_lines': '12', 'answers': True, 'answers_name': 'Попа', 'answers_lines': '12', 'criteria': True, 'criteria_name': 'Попа жесткая', 'criteria_scale': '5', 'absents': False, 'absents_name': 'Плошкот'}

dct1 = {'mode': 'fast', 'work_name': 'f', 'class': 'D:/pythonProject/Insighter II/delete.txt', 'fill_students': True, 'students_lines': 8, 'answers': False, 'answers_name': None, 'answers_lines': 8, 'criteria': False, 'criteria_name': None, 'criteria_scale': None, 'absents': False, 'absents_name': None}


db = Database()
db.connect()
parserui = ParserUIData(dct, db)
parserui.parse_dict_manual()
gen_data = parserui.get_data()
gen = Generator(gen_data)
gen.run_generation()




