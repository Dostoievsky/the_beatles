import os
import random

def generate_test_data(answers, foldername, puples):
    with open(puples, 'r', encoding='utf-8') as file:
        pupils = [line.strip() for line in file]

    # Чтение ответов
    with open(answers, 'r', encoding='utf-8') as file:
        answers_list = [line.strip() for line in file]

    # Создание папки
    os.makedirs(foldername, exist_ok=True)

    # Заполнение файлов
    for pupil in pupils:
        first_name, last_name = pupil.split()
        filename = f'{first_name.lower()}_{last_name.lower()}.txt'
        file_path = os.path.join(foldername, filename)

        with open(file_path, 'w', encoding='utf-8') as file:
            for i, answer in enumerate(answers_list, start=1):
                if random.choice([0, 1, 2]):
                    file.write(f"{answer}\n")
                else:
                    file.write(f"{i}) 0\n")

    print(f"Тестовые данные успешно созданы в папке {foldername}.")

answers = 'answers.txt'
foldername = 'Провальная работа 4'
puples = 'puples8v.txt'


generate_test_data(answers, foldername, puples)

