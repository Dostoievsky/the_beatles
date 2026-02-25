import os
import random
from math import ceil

class Generator:
    def __init__(self, folder_path, puple_file_path, answers_file_path):
        self.folder_path = folder_path
        self.puple_file_path = puple_file_path
        self.answers_file_path = answers_file_path

    def generate_dir(self):
        """Создает директорию по указанному пути."""
        os.makedirs(self.folder_path, exist_ok=True)

    def generate_student_files(self):
        """Создает файлы учеников и назначает им случайные оценки."""
        with open(self.puple_file_path, 'r', encoding='utf-8') as puple_file:
            for line in puple_file:
                fullname = line.strip()
                name, surname = fullname.lower().split()
                filename = f'{name}_{surname}.txt'
                full_path = os.path.join(self.folder_path, filename)
                mark = random.choice([2, 3, 4, 5])
                self.fill_student_file(full_path, mark)

    def fill_student_file(self, filename, mark):
        """Заполняет файл ученика в зависимости от полученной оценки."""
        percentages = {
            2: 50,
            3: 60,
            4: 80,
            5: 100
        }
        percentage = percentages.get(mark)
        correct_answers = self.get_random_answers(percentage)
        self.write_answers_to_file(filename, correct_answers)

    def get_random_answers(self, percentage):
        """Возвращает список правильных ответов в зависимости от процента."""
        with open(self.answers_file_path, 'r', encoding='utf-8') as answers_file:
            answers = answers_file.readlines()
            num_answers = len(answers)
            num_correct = ceil(num_answers * percentage / 100)
            correct_indices = random.sample(range(num_answers), num_correct)
            correct_answers = [answers[idx].strip() for idx in correct_indices]
            incorrect_answers = ['0\n'] * (num_answers - num_correct)
            combined_answers = correct_answers + incorrect_answers
            random.shuffle(combined_answers)
            return combined_answers

    @staticmethod
    def write_answers_to_file(filename, answers):
        """Записывает ответы в файл ученика, сохраняя формат 'номер) число'. """
        with open(filename, 'w', encoding='utf-8') as file:
            for idx, answer in enumerate(answers, start=1):
                file.write(f"{idx}) {answer}\n")

# Пример использования
gen = Generator('Чтонибудь', 'students_9v.txt', 'answers.txt')
gen.generate_dir()
gen.generate_student_files()

print("Файлы созданы и заполнены.")