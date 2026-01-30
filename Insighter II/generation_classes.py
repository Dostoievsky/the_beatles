from pathlib import Path
import re
from Database_Settings_classes import Database

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
        print('call')
        regex = r'[А-Яа-я]+ [А-Яа-я]+'
        lst = []
        with open(class_file, 'r', encoding='utf_8') as file:
            for line in [row.strip() for row in file.readlines()]:
                print(line)
                if re.fullmatch(regex, line):
                    lst.append(line)
        return lst





dct = {'mode': 'Ручная генерация', 'work_name': 'попа знатная', 'class': '9j',
  'fill_students': True, 'students_lines': '12', 'answers': True, 'answers_name': 'Попа', 'answers_lines': '12', 'criteria': True, 'criteria_name': 'Попа жесткая', 'criteria_scale': '5', 'absents': False, 'absents_name': 'Плошкот'}

dct1 = {'mode': 'fast', 'work_name': 'f', 'class': 'D:/pythonProject/Insighter II/delete.txt', 'fill_students': True, 'students_lines': 8, 'answers': False, 'answers_name': None, 'answers_lines': 8, 'criteria': False, 'criteria_name': None, 'criteria_scale': None, 'absents': False, 'absents_name': None}


db = Database()
db.connect()
parserui = ParserUIData(dct1, db)
parserui.parse_dict_fast()
for k, v in parserui.__dict__.items():
    print(k, v)
