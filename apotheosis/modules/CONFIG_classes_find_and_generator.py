import os
import sys

class Generator:
    """
    Генерирует структуру файлов и папок для новой работы.
    Создаёт директории, шаблонные файлы (ответы, оценки, отсутствующие) и заполняет их.
    """

    def __init__(self, puples_file, name_work):
        self.puples_file = puples_file
        self.name_work = name_work
        self.lst_files = []

    def generate_dir_students(self):
        path = os.path.join(os.getcwd(), self.name_work)
        os.makedirs(path, exist_ok=True)

    def generate_file_students(self):
        if self.puples_file is not None:
            with open(self.puples_file, 'r', encoding='utf-8') as kfile:
                for fullname in kfile:
                    name, surname = fullname.lower().strip().split()
                    filename = f'{name}_{surname}.txt'
                    with open(os.path.join(self.name_work, filename), 'a', encoding='utf-8') as f:
                        pass
        else:
            pass
        path = os.path.join(os.getcwd(), self.name_work)
        self.lst_files = os.listdir(path)

    def fill_files_students(self, count_strings):
        for file in self.lst_files:
            fullpath = os.path.join(self.name_work, file)
            with open(fullpath, 'w', encoding='utf-8') as filepuple:
                if count_strings is not None:
                    for i in range(1, count_strings + 1):
                        print(f'{i}) ', file=filepuple)
                else:
                    pass

    @staticmethod
    def create_answers_file(count_strings, filename='answers.txt'):
        if filename is not None:
            with open(filename, 'w', encoding='utf-8') as fileansw:
                if count_strings is not None:
                    for i in range(1, count_strings + 1):
                        print(f'{i}) ', file=fileansw)

    @staticmethod
    def create_marks_file(filename='marks.txt', grade=5):
        if filename is not None:
            with open(filename, 'w', encoding='utf-8') as filemarks:
                if grade is not None:
                    for _ in range(grade - 1):
                        print('оценка _ от _ до _ баллов', file=filemarks)

    @staticmethod
    def checking_setings(puples_file, count_strings):
        lst_errors = []
        if not os.path.exists(os.path.join(os.getcwd(), puples_file)):
            lst_errors.append(f'Файл {puples_file} не найден.')
        if not count_strings.isdigit():
            lst_errors.append(f'Количество строк должно быть целым числом.')
        if lst_errors:
            return lst_errors
        return False

    @staticmethod
    def create_missings_file(filename='missing.txt'):
        if filename is not None:
            with open(filename, 'w', encoding='utf-8') as filemiss:
                pass


class Finding:
    """
    Позволяет искать строки, начинающиеся с определённого имени, в файлах или папках.
    """
    def __init__(self, name):
        self.name = name
        self.lst_found = []

    @staticmethod
    def txt_to_columns(file_path):
        """
        Читает текстовый файл, пропуская первые 4 строки.
        Возвращает строки без лишних символов.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                for _ in range(4):
                    next(file)
            except StopIteration:
                print(f'Файл по пути {file_path} не удовлетворяет формату')
                sys.exit()
            return map(lambda x: x.strip(), file.readlines())

    @staticmethod
    def csv_to_columns(file_path):
        """
        Читает CSV-файл, пропуская первые 4 строки.
        Возвращает список строк без лишних символов.
        """
        plain_list = []
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            try:
                for _ in range(4):
                    next(csvfile)
            except StopIteration:
                print(f'Файл по пути {file_path} не удовлетворяет формату')
                sys.exit()

            for line in csvfile:
                plain_list.append(line.strip())
        return plain_list

    def find_from_dir(self, dirpath):
        """
        Ищет имя в всех файлах указанной директории (кроме .json).
        """
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

    def find_from_file(self, filepath):
        """
        Ищет имя в указанном файле.
        """
        with open(filepath, 'r', encoding='utf-8') as filefind:
            if filepath.endswith('.csv'):
                lines = Finding.csv_to_columns(filepath)
            else:
                lines = Finding.txt_to_columns(filepath)
            for line in lines:
                if line.strip().lower().startswith(self.name.lower()):
                    self.lst_found.append((line, filepath))
                    return self.lst_found

        return 0


