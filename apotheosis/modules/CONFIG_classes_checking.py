import re
import csv
import shutil
import os
import sys

class Student:
    """
    Представляет ученика с его данными: имя, фамилия, файл с ответами, список правильных ответов, статус, оценка и т.д.
    Поддерживает сериализацию в JSON через метод to_json().
    """

    def __init__(self, name, surname):
        self._name = name
        self._surname = surname
        self._file = None
        self._list_answers = None
        self._correct_answers = None
        self._response_status = None
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
    def response_status(self):
        return self._response_status

    @response_status.setter
    def response_status(self, new_response_status):
        self._response_status = new_response_status

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
            "_response_status": self._response_status,
            "_mark": self._mark,
            "_missings": self._missings,
            "_flag_not_all": self._flag_not_all
        }


class Marks:
    """
    Обрабатывает файл с критериями оценки.
    """

    def __init__(self, file):
        self.file = file

    def get_marks(self):
        """
        Строит словарь из файла с критериями и возвращает готовый словарь.
        """
        marks_dict = {}
        with open(self.file, 'r', encoding='utf-8') as file_marks:
            for line in file_marks.readlines():
                _, mark, _, down, _, up, _ = line.strip().split()
                for i in range(int(down), int(up) + 1):
                    marks_dict[i] = int(mark)
            return marks_dict



class Answers:
    """
    Читает файл с правильными ответами и сохраняет их в список.
    """

    def __init__(self, file):
        self.file = file
        self.answers_lst = []

    def get_right_answers(self):
        """
        Парсит файл с ответами, разбивает на номер вопроса и сам ответ.
        """
        with open(self.file, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    _, answer = line.split(') ')
                except ValueError:
                    print('Файл с ответами не удовлетворяет нужному формату')
                    sys.exit()
                self.answers_lst.append(answer.strip())
        return self.answers_lst


class Missings:
    """
    Определяет список отсутствующих учеников.
    Может работать в автоматическом режиме или по внешнему файлу.
    """

    def __init__(self, string, puple_file, puples_dict):
        self.string = string
        self.puple_file = puple_file
        self.puples_dict = puples_dict

    def get_missings(self):
        """
        Сравнивает учеников из файла с теми, что есть в словаре.
        Если файл содержит 'auto', то сравнивается автоматически.
        """
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


class Sorted:


    """
    Предоставляет разные способы сортировки словаря учеников.
    Поддерживает сортировку по умолчанию, по имени, по оценкам (лучшие и худшие).
    """

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


class FileManager:
    """
    Управляет файлами: создание путей, запись CSV, копирование директорий.
    """

    def __init__(self, dct=None):
        self.dct = dct

    @staticmethod
    def write_to_csv(filename, puples_dct, main_dct):
        """
        Записывает данные учеников в CSV-файл.
        Включает информацию о классе, названии работы, дате и оценках учеников.
        """
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow([f"Класс: {main_dct['klass']}"])
            writer.writerow([f"Название работы: {main_dct['name_work']}"])
            writer.writerow([f"Дата работы: {main_dct['date']}"])
            writer.writerow([])

            for k, v in puples_dct:
                if v.missings:
                    writer.writerow([f'{k}:    отсутствовал(а)'])
                else:
                    star = '*' if v.flag_not_all else ''
                    writer.writerow([f'{k}:    {v.mark}{star}'])

    @staticmethod
    def copy_directory(source_path, destination_path):
        """
        Копирует содержимое одной папки в другую.
        При ошибке выводит сообщение и завершает программу.
        """
        try:
            shutil.copytree(source_path, destination_path)
            print(f"Папка успешно скопирована из {source_path} в {destination_path}.")
        except FileExistsError:
            pass
        except OSError as err:
            print(f"Ошибка при копировании: {err}")
            sys.exit()

    def create_json_filename(self):
        """
        Создаёт полный путь к JSON-файлу результатов.
        Формирует имя файла из параметров класса, названия работы и даты.
        """
        fullpath = os.path.join(os.getcwd(), f'archive/{self.dct["klass"]}')
        os.makedirs(fullpath, exist_ok=True)
        filenamestat = f"sysfile_{self.dct['klass'].lower().strip()}_{self.dct['name_work'].lower().strip()}_{self.dct['date']}.json"
        fullfilepath = os.path.join(fullpath, filenamestat)
        return fullfilepath

    def create_text_file_path(self):
        """
        Создаёт путь к текстовому файлу с результатами.
        """
        halfpath = os.path.join('archive', self.dct["klass"])
        fullpath = os.path.join(os.getcwd(), halfpath)
        os.makedirs(fullpath, exist_ok=True)
        fullnamework = f'{self.dct["klass"]}_{self.dct["name_work"].lower().strip()}_{self.dct["date"]}.txt'
        return os.path.join(fullpath, fullnamework)

    def create_csv_file_path(self):
        """
        Создаёт путь к CSV-файлу с результатами.
        """
        halfpath = os.path.join('archive', self.dct["klass"])
        fullpath = os.path.join(os.getcwd(), halfpath)
        os.makedirs(fullpath, exist_ok=True)
        fullnamework = f'{self.dct["klass"]}_{self.dct["name_work"].lower().strip()}_{self.dct["date"]}.csv'
        return os.path.join(fullpath, fullnamework)


class FormatChecking:
    """
    Проверяет корректность формата входных данных перед запуском программы.
    Выполняет валидацию: класса, названия работы, даты, файлов и папки с учениками.
    """

    def __init__(self, results):
        self.results = results
        self.errors = []

    def format_klass(self):
        klass_pattern = r'^(?:[1-9]|10|11)\w?$'
        if re.match(klass_pattern, self.results.klass, flags=re.IGNORECASE):
            return True
        else:
            self.errors.append('Формат класса неверен')
            return False

    def format_name_work(self):
        if len(self.results.name_work) > 50:
            self.errors.append('Название работы должно быть короче 50 символов')
            return False
        elif re.search(r'[a-zA-Z]', self.results.name_work):
            self.errors.append('Название работы не должно содержать латинские буквы')
            return False
        else:
            return True

    def format_date(self):
        date_pattern = r'^(0[1-9]|[12][0-9]|3[01])[-./](0[1-9]|1[012])[-./](19|20)\d\d$'
        if re.match(date_pattern, self.results.date):
            return True
        else:
            self.errors.append('Формат даты неверен')
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
                self.errors.append(f'Файл "{filename}" имеет неправильное расширение. Должно быть ".txt"')
                continue
            full_path = os.path.join(os.getcwd(), filename)
            if not os.path.isfile(full_path):
                self.errors.append(f'Файл "{filename}" не найден')

        return len(self.errors) == 0

    def format_students_folder(self):
        path = os.path.join(os.getcwd(), self.results.students_folder)
        if os.path.isdir(path):
            return True
        else:
            self.errors.append('Указанная папка не найдена')
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
