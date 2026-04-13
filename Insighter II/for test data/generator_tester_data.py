import os
import random

# ========== НАСТРОЙКИ ==========
students_file = "students_9v.txt"      # путь к файлу со списком учеников
num_answers = 20                    # количество ответов (n)
answers_file = "answers.txt"        # путь к файлу с правильными ответами
work_name = "вариант огэ 3"    # название работы (имя папки)
# =================================



def get_probability(power_index: int) -> float:
    if power_index == 1:
        return 0.10
    if power_index == 2:
        return 0.35
    if power_index == 3:
        return 0.5
    if power_index == 4:
        return 0.725
    if power_index == 5:
        return 0.95
    raise ValueError(f"Некорректный индекс силы: {power_index}")

def generate_responses(prob: float, correct_answers: list) -> list:
    responses = []
    for correct in correct_answers:
        if random.random() < prob:
            responses.append(correct)
        else:
            responses.append(0)
    return responses

def main():
    os.makedirs(work_name, exist_ok=True)

    # Проверяем и читаем файл с правильными ответами
    if not os.path.exists(answers_file):
        print(f"Ошибка: файл ответов {answers_file} не найден.")
        return

    correct_answers = []
    with open(answers_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if ') ' in line:
                answer = line.split(') ', 1)[1].strip()
                correct_answers.append(answer)
            else:
                # Если вдруг формат не с номером, используем всю строку как ответ
                correct_answers.append(line)

    # Проверяем количество ответов
    if len(correct_answers) != num_answers:
        print(f"Предупреждение: в файле ответов {len(correct_answers)} строк, "
              f"а ожидается {num_answers}. Будет использовано {min(len(correct_answers), num_answers)} ответов.")
        correct_answers = correct_answers[:num_answers]
        if len(correct_answers) < num_answers:
            # Если не хватает, дополняем нулями
            correct_answers.extend(['0'] * (num_answers - len(correct_answers)))

    # Читаем учеников
    if not os.path.exists(students_file):
        print(f"Ошибка: файл {students_file} не найден.")
        return

    with open(students_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if " - " not in line:
            print(f"Пропускаем строку (неверный формат): {line}")
            continue

        name_part, power_part = line.split(" - ", maxsplit=1)
        parts = name_part.split()
        if len(parts) < 2:
            print(f"Пропускаем строку (не хватает имени/фамилии): {line}")
            continue
        first_name, last_name = parts[0], parts[1]
        filename = f"{first_name.lower()}_{last_name.lower()}.txt"

        try:
            power = int(power_part.strip())
        except ValueError:
            print(f"Пропускаем строку (индекс силы не число): {line}")
            continue

        if power not in range(1, 6):
            print(f"Пропускаем строку (индекс силы вне диапазона 1..5): {line}")
            continue

        prob = get_probability(power)
        responses = generate_responses(prob, correct_answers)

        file_path = os.path.join(work_name, filename)
        with open(file_path, 'w', encoding='utf-8') as out_f:
            for i, ans in enumerate(responses, start=1):
                out_f.write(f"{i}) {ans}\n")

        print(f"Создан файл: {file_path}")

    print("Генерация завершена.")

if __name__ == "__main__":
    main()