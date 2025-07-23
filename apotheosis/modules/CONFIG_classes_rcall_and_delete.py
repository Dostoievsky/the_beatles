import os
import json
import shutil
from pathlib import Path
import random
import sys

class RandomCall:
    """
    Реализует случайный вызов учеников к доске.
    Поддерживает разные источники данных: файл, ввод с клавиатуры, список из sys.json.
    """

    @staticmethod
    def process_path(value):
        with open(value, 'r', encoding='utf-8') as file:
            return map(lambda x: x.strip(), file.readlines())

    @staticmethod
    def process_miss():
        with open('sys.json', 'r', encoding='utf-8') as sys_file_perf:
            dct_perf = json.load(sys_file_perf)
            try:
                trex = dct_perf['students']
            except KeyError:
                print('Файл sys.json не содержит информации о списке учеников. Только ручной ввод')
                sys.exit()
            with open(trex, 'r', encoding='utf-8') as file:
                return map(lambda x: x.strip(), file.readlines())

    @staticmethod
    def process_number(value):
        return range(1, value + 1)

    @staticmethod
    def process_input(user_input):
        path = Path(user_input)
        if path.is_file() and path.suffix == '.txt':
            return RandomCall.process_path(user_input)
        else:
            if user_input == '':
                return RandomCall.process_miss()
            try:
                number = int(user_input)
                return RandomCall.process_number(number)
            except ValueError:
                return False


class DeleteManager:
    """
    Управляет удалением файлов и папок.
    Предоставляет методы для удаления отдельных элементов, а также глубокого удаления всего содержимого директории.
    """

    def __init__(self, list_of_elements):
        self.list_of_elements = list_of_elements

    def delete_files(self):
        """
        Удаляет указанные файлы из текущей директории.
        Выводит сообщение об успехе или ошибке.
        """
        for filename in self.list_of_elements:
            file_path = os.path.join(os.getcwd(), filename)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Файл {filename} успешно удалён.")
                else:
                    pass
            except Exception as e:
                print(f"Ошибка при удалении файла {filename}: {e}")

    def delete_files_and_folders(self):
        """
        Удаляет файлы и папки из списка.
        Поддерживает удаление как файлов, так и директорий.
        """
        for entry in self.list_of_elements:
            entry_path = os.path.join(os.getcwd(), entry)
            try:
                if os.path.isfile(entry_path):
                    os.remove(entry_path)
                    print(f"Файл {entry} успешно удалён.")
                elif os.path.isdir(entry_path):
                    shutil.rmtree(entry_path)
                    print(f"Папка {entry} успешно удалена.")
                else:
                    pass
            except Exception as e:
                print(f"Ошибка при удалении {entry}: {e}")

    @staticmethod
    def deep_delete():
        """
        Глубоко удаляет всё содержимое текущей директории, кроме файлов .py.
        Удаляет и файлы, и папки.
        """
        current_dir = os.getcwd()
        for entry in os.listdir(current_dir):
            entry_path = os.path.join(current_dir, entry)
            try:
                if os.path.isfile(entry_path) and not entry.endswith(".py"):
                    os.remove(entry_path)
                    print(f"Файл {entry} успешно удалён.")
                elif os.path.isdir(entry_path) and not Path(entry_path).name == 'modules':
                    shutil.rmtree(entry_path)
                    print(f"Папка {entry} успешно удалена.")
            except Exception as e:
                print(f"Ошибка при удалении {entry}: {e}")

    def create_elements_test(self, dirs):
        """
        Создаёт тестовые файлы и папки для проверки функции удаления.
        """
        for dir in dirs:
            os.makedirs(dir, exist_ok=True)
            print(f"Папка {dir} успешно создана.")
        for file in self.list_of_elements:
            with open(file, 'w') as f:
                print(f"Файл {file} успешно создан.")

    @staticmethod
    def create_file_delete():
        """
        Создаёт файл `delete.txt` со случайным 4-значным паролем.
        Используется для защиты от случайного удаления.
        """
        psw = random.randint(1000, 9999)
        with open('delete.txt', 'w') as f:
            print(f'Пароль для удаления: {psw}', file=f)
        return psw