import os

if 5 == 8:
    pass

else:
    folder_path = r'C:\Users\79103\Desktop\apotheosis\Каторжная работа'

    answers_for_2 = [1, 2, 3, 4, 0, 0, 0, 0, 0, 0]
    answers_for_3 = [1, 2, 3, 4, 5, 6, 0, 0, 0, 0]
    answers_for_4 = [1, 2, 3, 4, 5, 6, 7, 8, 0, 0]
    answers_for_5 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    num_students_for_2 = 10
    num_students_for_3 = 10
    num_students_for_4 = 10
    num_students_for_5 = 0

    files = os.listdir(folder_path)

    for index, file in enumerate(files):
        file_path = os.path.join(folder_path, file)

        if index < num_students_for_5:
            answers = answers_for_5
        elif index < num_students_for_5 + num_students_for_4:
            answers = answers_for_4
        elif index < num_students_for_5 + num_students_for_4 + num_students_for_3:
            answers = answers_for_3
        else:
            answers = answers_for_2

        try:
            with open(file_path, 'w') as f:
                for answer_index, answer in enumerate(answers):
                    f.write(f"{answer_index + 1}) {answer}\n")
        except IOError as e:
            print(f'Ошибка при работе с файлом {file}: {e}')
    print("Готово")