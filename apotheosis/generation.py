import os
import random


file_puples = "students_9v.txt"
names_of_work = ["Тестовая работа 1", "Контрольная работа 5", "Каторжная работа 3"]
len_answers = 10
make_files_bool = True
dct ={2: [1, 2, 3, 4, 0, 0, 0, 0, 0, 0],
      3: [1, 2, 3, 4, 5, 6, 0, 0, 0, 0],
      4: [1, 2, 3, 4, 5, 6, 7, 8, 0, 0],
      5: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}

try:
    for li in names_of_work:
        path = os.path.join(os.getcwd(), li)
        os.makedirs(path, exist_ok=True)
        with open(file_puples, "r", encoding="utf-8") as file_puples_obj:
            for pup in file_puples_obj:
                pupfilename = pup.strip().split()[0].lower() + '_' + pup.strip().split()[1].lower() + ".txt"
                pupfilename = os.path.join(path, pupfilename)
                with open(pupfilename, "w", encoding="utf-8") as file_of_puple:
                    mark = dct[random.randint(2, 5)]
                    for n, answ in enumerate(mark, 1):
                        print(f"{n}) {answ}", file=file_of_puple)

    if make_files_bool:
        with open("answers.txt", "w", encoding="utf-8") as answfile:
            for k, v in enumerate(range(1, 11), 1):
                print(f"{k}) {v}", file=answfile)

        with open("marks.txt", "w", encoding="utf-8") as marksfile:
            print("5 от 10 до 10\n4 от 8 до 9\n3 от 5 до 7\n2 от 0 до 4", file=marksfile)

        with open("missings.txt", "w", encoding="utf-8") as missfile:
            pass
    print("Все готово")
except Exception as e:
    print("Что-то пошло не так", e)