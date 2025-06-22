import os
import sys
from datetime import datetime
import json
import statistics
from collections import namedtuple
import tkinter as tk
from tkinter import filedialog
import json
import re


def on_submit():
    global result
    class_value = class_entry.get()
    work_value = work_entry.get()
    date_value = date_entry.get()
    answer_file = answer_entry.get()
    marks_file = criteria_entry.get()
    students_file = students_entry.get()
    missings_file = absent_entry.get()
    students_folder = students_folder_entry.get()
    result = (class_value, work_value, date_value, answer_file, marks_file, students_file, missings_file, students_folder)
    root.destroy()

def browse_file(entry):
    file_path = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def browse_folder(entry):
    folder_path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, folder_path)


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


class FileManager:
    def __init__(self, dct):
        self.dct = dct

    def create_json_filename(self):
        fullpath = os.path.join(os.getcwd(), f'archive/{self.dct["klass"]}')
        os.makedirs(fullpath, exist_ok=True)
        filenamestat = f"sysfile_{self.dct['klass'].lower().strip()}_{self.dct['name_work'].lower().strip()}_{self.dct['date']}.json"
        fullfilepath = os.path.join(fullpath, filenamestat)
        return fullfilepath

    def create_text_file_path(self):
        halfpath = os.path.join('archive', self.dct["klass"])
        fullpath = os.path.join(os.getcwd(), halfpath)
        os.makedirs(fullpath, exist_ok=True)
        fullnamework = f'{self.dct["klass"]}_{self.dct["name_work"].lower().strip()}_{self.dct["date"]}.txt'
        return os.path.join(fullpath, fullnamework)


class Answers:

    def __init__(self, file):
        self.file = file
        self.answers_lst = []

    def get_right_answers(self):
        with open(self.file, 'r', encoding='utf-8') as file:
            for line in file:
                _, answer = line.split(') ')
                self.answers_lst.append(answer.strip())
        return self.answers_lst


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


class FormatChecking:
    def __init__(self, results):
        self.results = results
        self.errors = []

    def format_klass(self):
        klass_pattern = r'^(?:[1-9]|10|11)\w?$'
        if re.match(klass_pattern, self.results.klass, flags=re.IGNORECASE):
            return True
        else:
            self.errors.append('Формат класса неверен.')
            return False

    def format_name_work(self):
        if len(self.results.name_work) > 50:
            self.errors.append('Название работы должно быть короче 50 символов.')
            return False
        elif re.search(r'[a-zA-Z]', self.results.name_work):
            self.errors.append('Название работы не должно содержать латинские буквы.')
            return False
        else:
            return True

    def format_date(self):
        date_pattern = r'^(0[1-9]|[12][0-9]|3[01])[-./](0[1-9]|1[012])[-./](19|20)\d\d$'
        if re.match(date_pattern, self.results.date):
            return True
        else:
            self.errors.append('Формат даты неверен.')
            return False

    def format_any_file(self):
        global flag_auto
        flag_auto = False
        files_to_check = [self.results.answer, self.results.marks, self.results.students, self.results.missings]
        if self.results.missings == 'auto':
            flag_auto = True
            files_to_check = [self.results.answer, self.results.marks, self.results.students]
        for filename in files_to_check:
            base_filename, extension = os.path.splitext(filename)
            if extension != '.txt':
                self.errors.append(f'Файл "{filename}" имеет неправильное расширение. Должно быть ".txt".')
                continue
            full_path = os.path.join(os.getcwd(), filename)
            if not os.path.isfile(full_path):
                self.errors.append(f'Файл "{filename}" не найден.')

        return len(self.errors) == 0

    def format_students_folder(self):
        path = os.path.join(os.getcwd(), self.results.students_folder)
        if os.path.isdir(path):
            return True
        else:
            self.errors.append('Указанная папка не найдена.')
            return False

    def check_all(self):
        checks = [
            self.format_klass(),
            self.format_name_work(),
            self.format_date(),
            self.format_any_file(),
            self.format_students_folder()
        ]
        if all(checks):
            return True
        else:
            return self.errors


class Questions:
    def __init__(self, question, tuple_of_variants=('1', 'lf', 'да', True)):
        self.question = question
        self.tuple_of_variants = tuple_of_variants

    def make_question(self):
        if input(self.question) in self.tuple_of_variants:
            return True
        else:
            return False

    def make_variants_question(self, variants):
        answ = input(self.question)


class Sorted:
    def __init__(self, dct):
        self.dct = dct

    def sort_by_default(self):
        return self.dct.items()

    def sort_by_name(self):
        sort_dct_items = sorted(self.dct.items(), key=lambda x: x[0])
        return sort_dct_items

    def sort_by_mark_best(self):
        return sorted(self.dct.items(), key=lambda item: float('-inf') if item[1].mark is None else item[1].mark, reverse=True)

    def sort_by_mark_worst(self):
        return sorted(self.dct.items(), key=lambda item: float('+inf') if item[1].mark is None else item[1].mark)


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
    def default(self, o):
        if isinstance(o, Student):
            return o.to_json()
        return super().default(o)


def student_decoder(dct):
    if '__class__' in dct and dct['__class__'] == 'Student':
        instance = Student(dct['_name'], dct['_surname'])
        instance._file = dct.get('_file')
        instance._list_answers = dct.get('_list_answers')
        instance._correct_answers = dct.get('_correct_answers')
        instance._mark = dct.get('_mark')
        instance._missings = dct.get('_missings')
        instance._flag_not_all = dct.get('_flag_not_all')
        return instance
    return dct


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

#начало программы


if os.path.isfile('sys.json') and len(json.load(open('sys.json'))) == 8:
        with open('sys.json', 'r', encoding='utf-8') as sys_file:
            main_dct = json.load(sys_file)
#форма заполнения данных через tkinter
else:
    root = tk.Tk()
    root.title("Форма заполнения данных")
    root.geometry("700x500")
    font_style = ("Montserrat", 10, "bold")

    header_label = tk.Label(root, text="Заполните все поля для начала работы.", font=("Montserrat", 12, "bold"))
    header_label.grid(row=0, column=0, columnspan=3, pady=(10, 20))

    class_label = tk.Label(root, text="Класс:", font=font_style)
    class_label.grid(row=1, column=0, pady=(10, 5))
    class_entry = tk.Entry(root, font=font_style)
    class_entry.grid(row=1, column=1, pady=(10, 5))

    work_label = tk.Label(root, text="Название работы:", font=font_style)
    work_label.grid(row=2, column=0, pady=5)
    work_entry = tk.Entry(root, font=font_style)
    work_entry.grid(row=2, column=1, pady=5)

    date_label = tk.Label(root, text="Дата работы:", font=font_style)
    date_label.grid(row=3, column=0, pady=5)
    date_entry = tk.Entry(root, font=font_style)
    date_entry.grid(row=3, column=1, pady=5)

    answer_label = tk.Label(root, text="Файл с ответами:", font=font_style)
    answer_label.grid(row=4, column=0, pady=5)
    answer_entry = tk.Entry(root, font=font_style)
    answer_entry.grid(row=4, column=1, pady=5)
    answer_button = tk.Button(root, text="Выбрать файл", command=lambda: browse_file(answer_entry), font=font_style)
    answer_button.grid(row=4, column=2, padx=5, pady=5)

    criteria_label = tk.Label(root, text="Файл с критериями:", font=font_style)
    criteria_label.grid(row=5, column=0, pady=5)
    criteria_entry = tk.Entry(root, font=font_style)
    criteria_entry.grid(row=5, column=1, pady=5)
    criteria_button = tk.Button(root, text="Выбрать файл", command=lambda: browse_file(criteria_entry), font=font_style)
    criteria_button.grid(row=5, column=2, padx=5, pady=5)

    students_label = tk.Label(root, text="Список учеников:", font=font_style)
    students_label.grid(row=6, column=0, pady=5)
    students_entry = tk.Entry(root, font=font_style)
    students_entry.grid(row=6, column=1, pady=5)
    students_button = tk.Button(root, text="Выбрать файл", command=lambda: browse_file(students_entry), font=font_style)
    students_button.grid(row=6, column=2, padx=5, pady=5)

    absent_label = tk.Label(root, text="Список отсутствующих:", font=font_style)
    absent_label.grid(row=7, column=0, pady=5)
    absent_entry = tk.Entry(root, font=font_style)
    absent_entry.grid(row=7, column=1, pady=5)
    absent_button = tk.Button(root, text="Выбрать файл", command=lambda: browse_file(absent_entry), font=font_style)
    absent_button.grid(row=7, column=2, padx=5, pady=5)

    students_folder_label = tk.Label(root, text="Папка с работами:", font=font_style)
    students_folder_label.grid(row=8, column=0, pady=5)
    students_folder_entry = tk.Entry(root, font=font_style)
    students_folder_entry.grid(row=8, column=1, pady=5)
    students_folder_button = tk.Button(root, text="Выбрать папку", command=lambda: browse_folder(students_folder_entry), font=font_style)
    students_folder_button.grid(row=8, column=2, padx=5, pady=5)

    submit_button = tk.Button(root, text="Отправить", command=on_submit, font=font_style)
    submit_button.grid(row=9, column=1, columnspan=3, pady=(10, 20))

    root.mainloop()

    Results = namedtuple('Results', ['klass', 'name_work', 'date', 'answer', 'marks', 'students', 'missings', 'students_folder'])
    results = Results(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[7])

#проверка формата данных и формирование sys.json

    if all(results._asdict().values()):
        formatting = FormatChecking(results)
        if isinstance(formatting.check_all(), list):
            print('Возникли ошибки при проверке формата данных:')
            for error in formatting.errors:
                print(error)
        elif isinstance(formatting.check_all(), bool):
            with open('sys.json', 'w', encoding='utf-8') as sys_json_file:
                json.dump(results._asdict(), sys_json_file, ensure_ascii=False, indent=4)
                print('Данные сохранены, перезапустите программу.')
                sys.exit()
        else:
            print('Непредвиденная ошибка при проверке формата данных.')
            sys.exit()
    else:
        print('Вы оставили какое-то поле не заполненным. Программа остановлена.')




dct_variants = {
    'check_works': ('1', 'проверка', 'проверка работ'),
    'redact_data': ('2', 'редактирование', 'редактирование данных', 'перезапись', 'перезапись данных')
}
mainchoose = input('Выберите режим работы:\n'
                   '1. Проверка работ[1]\n'
                   '2. Перезапись данных[2]\n')

if mainchoose in dct_variants['check_works']: #проверка работ
    print('Программа работает со следующими данными, если вы хотите измеенить их, то выберите режим измения данных:')
    for k, v in main_dct.items():
        print(f'{k}: {v}')

    print()

    stat_flag = False
    marks_flag = False

    qst = Questions('Вам нужны подробные отчеты по ученику или классу? Для подробной статистики будет создан дополнительный системный json-файл.\n')
    if qst.make_question():
        stat_flag = True

    qst1 = Questions('В файле с оценками критерии оценивания записаны в форме баллов?\n')
    if qst1.make_question():
        marks_flag = True

    files_of_puple = os.listdir(main_dct['students_folder']) #формирование словаря имя_ученика: путь_к_файлу
    dct_of_puple_files = {}
    for puple_file in files_of_puple:
        puple_file_name = puple_file.split('.')[0]
        name, surname = puple_file_name.split('_')
        full_name = f'{name} {surname}'.title()
        full_path = os.path.join(main_dct['students_folder'], puple_file)
        dct_of_puple_files[full_name] = full_path


    puples_dct = {}
    for k, v in dct_of_puple_files.items(): #создание экземпляров класса Student
        puples_dct[k] = Student(*k.split())
        puples_dct[k].file = v


    for k, v in puples_dct.items(): #заполнение экземпляров класса Student списком ответов
        lst_of_answers = []
        with open(v.file, 'r', encoding='utf-8') as puple_file:
            for line in puple_file:
                try:
                    _, answer = line.strip().split(')')
                except ValueError:
                    continue
                lst_of_answers.append(answer.strip())
            v.list_answers = lst_of_answers


    right_answers = Answers(main_dct['answer']) #создание экземпляра класса Answers
    lst_of_right_answers = right_answers.get_right_answers()


    for k, v in puples_dct.items(): #заполнение экземпляров класса Student количеством правильных ответов
        counter_right = 0
        if len(v.list_answers) != len(lst_of_right_answers):
            v.flag_not_all = True
        for pup, right in zip(v.list_answers, lst_of_right_answers):
            if pup == right:
                counter_right += 1
        v.correct_answers = counter_right

    m = Marks(main_dct['marks'], marks_flag) #создание экземпляра класса Marks

    try: #проверка корректности файла marks.txt
        marks_dct = m.get_marks()
    except ValueError as e:
        print(e)
        sys.exit()

    for k, v in puples_dct.items(): #заполнение экземпляров класса Student оценками
        try:
            mark = marks_dct[v.correct_answers]
            v.mark = mark
        except KeyError:
            print('Возникла ошибка при получении оценки ученика. Проверьте файл с оценками.')
            sys.exit()


    string, puple_file = main_dct['missings'], main_dct['students'] #создание экземпляра класса Missings
    missings_puple = Missings(string, puple_file, puples_dct)
    print()

    for miss in missings_puple.get_missings(): #заполнение экземпляров класса Student отсутствующими учениками
        puples_dct[miss] = Student(*miss.split())
        puples_dct[miss].missings = True

    fm = FileManager(main_dct)

    text_filepath = fm.create_text_file_path()

    if stat_flag: #создание системного json-файла для статистики по флагу stat_flag
        halfpath = f'archive/{main_dct["klass"]}'
        fullpath = os.path.join(os.getcwd(), halfpath)
        filenamestat = f"sysfile_{main_dct['klass'].lower().strip()}_{main_dct['name_work'].lower().strip()}_{main_dct['date']}.json"
        fullfilepath = os.path.join(fullpath, filenamestat)
        with open(fullfilepath, 'w', encoding='utf-8') as f:
            json.dump(puples_dct, f, cls=StudentJSONEncoder, ensure_ascii=False, indent=4)

    qst2 = input('Выберите режим сортировки:\n'
                     'По умолчанию[0]\n'
                     'По именам[1]\n'
                     'По оценкам(сначала лучшие)[2]\n'
                     'По оценкам(сначала худшие)[3]\n').lower().strip()

    sort = Sorted(puples_dct) #сортировка
    if qst2 in ('по умолчанию', '0'):
        puples_dct = sort.sort_by_default()
    elif qst2 in ('по именам', '1'):
        puples_dct = sort.sort_by_name()
    elif qst2 in ('по оценкам(сначала лучшие)', '2'):
        puples_dct = sort.sort_by_mark_best()
    elif qst2 in ('по оценкам(сначала худшие)', '3'):
        puples_dct = sort.sort_by_mark_worst()
    else:
        print('Неизвестный режим сортировки.')
        sys.exit()


    with open(text_filepath, 'w', encoding='utf-8') as file: #запись в итоговый файл
        print(f"Класс: {main_dct['klass']}", file=file)
        print(f"Название работы: {main_dct['name_work']}", file=file)
        print(f"Дата работы: {main_dct['date']}", file=file)
        print(file=file)
        for k, v in puples_dct:
            if v.missings:
                print(f'{k}  -  отсутствовал(а)', file=file)
                continue
            star = ('*' if v.flag_not_all else '')
            print(f'{k}:    {v.mark}{star}', file=file)

    print(f'Проверка прошла успешно. Результаты проверки записаны в файл {text_filepath}.') #конец работы
    qst3 = Questions('Открыть файл?\n')
    if qst3.make_question():
        os.startfile(text_filepath)



# with open('students.json', 'r', encoding='utf-8') as f:
    #     restored_students = json.load(f, object_hook=student_decoder)
    #
    # for key, student in restored_students.items():
    #     print(key, student.__dict__)













elif mainchoose in dct_variants['redact_data']:
    qst = Questions('Вы хотите перезаписать данные?\n')
    if qst.make_question():
        os.remove('sys.json')
        print('Файл данных удален. Перезапустите программу.')






















