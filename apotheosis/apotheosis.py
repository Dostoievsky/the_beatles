import datetime
import json
import os
import shutil
import statistics
import sys
import collections
import time
from pathlib import Path
from random import randint
from typing import List, Tuple, Dict, Any, Union
import tracemalloc
import matplotlib.pyplot as plt

print(f'Алгоритм проверки работ и получения статистики для них. Запуск {datetime.datetime.now().time().strftime("%H:%M:%S")}. Версия 0.7 BETA.')
print()
tracemalloc.start()
start = time.monotonic()

#Объявление функций
def deep_stat(lst_of_module, statfile):

    print(f'Средняя оценка по классу: {round(statistics.mean(lst_of_module), 2)}', file=statfile)
    print(f'Медианное значние всех оценок: {round(statistics.median(lst_of_module), 2)}', file=statfile)
    print(f'Больше всего оценок "{collections.Counter(lst_of_module).most_common()[0][0]}"', file=statfile)
    print(file=statfile)
    print("Количество оценок:", file=statfile)
    for k, v in collections.Counter(lst_of_module).items():
        print(f'Оценок "{k}": {v}', file=statfile)
    print(collections.Counter(lst_of_module))
    print(file=statfile)
    print("Оценка сложности заданий: ", file=statfile)
    print(file=statfile)
    perfectly_solved = filter_tasks(result, 100, 101)
    if perfectly_solved:
        print(
            f"Задания [{', '.join(map(str, perfectly_solved))}] решили абсолютно все ученики. Вам стоит проверить, не слишком ли легкие эти задания.", file=statfile)
    else:
        print("Нет заданий, которые решили абсолютно все ученики.", file=statfile)
    easy_solved = filter_tasks(result, 80, 100)
    if easy_solved:
        print(
            f"Задания [{', '.join(map(str, easy_solved))}] решили большинство учеников. Вероятно, эта темы была хорошо отработана.",
            file=statfile)
    else:
        print("Нет заданий, которые решили большинство учеников.", file=statfile)
    moderately_solved = filter_tasks(result, 60, 80)
    if moderately_solved:
        print(
            f"Задания [{', '.join(map(str, moderately_solved))}] вызвали средние затруднения у учеников. Возможно, стоит уделить больше внимания этим темам.",
            file=statfile)
    else:
        print("Нет заданий, вызвавших средние затруднения у учеников.", file=statfile)
    hard_solved = filter_tasks(result, 40, 60)
    if hard_solved:
        print(
            f"Задания [{', '.join(map(str, hard_solved))}] оказались сложными для многих учеников. Рекомендуем повторно разобрать соответствующие темы.",
            file=statfile)
    else:
        print("Нет заданий, оказавшихся сложными для многих учеников.", file=statfile)
    very_hard_solved = filter_tasks(result, 20, 40)
    if very_hard_solved:
        print(
            f"Задания [{', '.join(map(str, very_hard_solved))}] показали низкую успеваемость. Эти темы требуют особого внимания и проработки.",
            file=statfile)
    else:
        print("Нет заданий с низкой успеваемостью.", file=statfile)

    failed_solved = filter_tasks(result, 1, 20)
    if failed_solved:
        print(
            f"Задания [{', '.join(map(str, failed_solved))}] практически не были выполнены. Проверьте правильность понимания учениками соответствующих тем.",
            file=statfile)
    else:
        print("Нет заданий, которые практически не были выполнены.", file=statfile)

    pizza_tower = filter_tasks(result, 0, 1)
    if pizza_tower:
        print(
            f"Задания [{', '.join(map(str, pizza_tower))}] не решил ни один ученик. Возможно, это ошибка в ответах или задания оказались чересчур сложными.",
            file=statfile)
    else:
        print("Нет заданий, которые никто не решил.", file=statfile)

def filter_tasks(result: Dict[str, float], lower_bound: float, upper_bound: float) -> List[str]:
    return [task for task, percent in result.items() if lower_bound <= percent < upper_bound]

def give_short_stat(lstforstat: List[int], lst_tup_files_stat: List[Tuple[str]]) -> None:
    with open("statisticsfile.txt", "w", encoding="utf-8") as statfile:
        print(f'Статитсика для класса {statchoose} по работе "{lst_tup_files_stat[0][1]}".', file=statfile)
        print(file=statfile)
        print(f'Средняя оценка по классу: {round(statistics.mean(lstforstat), 2)}', file=statfile)
        print(f'Медианное значние всех оценок: {round(statistics.median(lstforstat), 2)}', file=statfile)
        print(f'Больше всего оценок "{round(statistics.mode(lstforstat), 2)}"', file=statfile)
        print(file=statfile)
        print("Количество оценок:", file=statfile)
        statmark = collections.Counter(lstforstat)
        for k, v in sorted(statmark.items()):
            print(f'Оценок "{k}": {v}', file=statfile)

def find_pairs(lst):
    jsons = list(filter(lambda x: x.startswith("sysfile_") and x.endswith(".json"), lst))
    txts = list(filter(lambda x: x.endswith(".txt"), lst))
    result = []
    for li in jsons:
        for v in txts:
            string = li.split("_")[1]
            date = li.split("_")[2].split(".")[0]
            string1 = v.split(" за ")[0]
            date1 = v.split(" за ")[1].split(".")[0]
            if string == string1 and date1 == date:
                result.append((li, v))
                txts.remove(v)
    for k in txts:
        result.append((k, ))
    return result


def search(folder_path: str, search_string: str) -> dict:
    result = {}
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith(search_string):
                            result[file_path] = line.strip()
            except UnicodeDecodeError:
                pass

    return result or None

def makedirs(folder_name: str, dct: Dict[str, str]) -> str:
    base_directory = os.path.dirname(os.path.abspath(__file__))
    new_folder_path = os.path.join(base_directory, folder_name)
    os.makedirs(new_folder_path, exist_ok=True)
    klassfolder = os.path.join(new_folder_path, dct["klass"])
    os.makedirs(klassfolder, exist_ok=True)
    return klassfolder

def flatten_tuples(d: Dict[str, Any]) -> Dict[str, Tuple]:
    result: Dict[str, Tuple] = {}
    for key, value in d.items():
        flattened_value: List[Any] = []
        stack: List[Any] = [value]
        while stack:
            current = stack.pop()
            if isinstance(current, tuple):
                stack.extend(reversed(current))
            else:
                flattened_value.append(current)
        result[key] = tuple(flattened_value)
    return result

def merge_dictionaries(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Tuple[Any, Any]]:
    merged_dict: Dict[str, Tuple[Any, Any]] = {key: (value1, value2) for (key, value1), (_, value2) in zip(dict1.items(), dict2.items())}
    return merged_dict

def makeexfile(file: str) -> None:
    with open(file, "w+", encoding="UTF-8") as f:
        f.seek(0)
        lst = ["класс", "название работы", "файл с ответами", "файл с критериями оценивания",
               "дата работы", "список учеников(для генерации)", "список отсутствующих",
               "название папки с работами"]
        print("ВАЖНО! Не удаляйте символы | в файле. Без них программа будет работать некорректно. Обязательно сохраните файл!", file=f)
        print(file=f)
        for w in lst:
            print(f"{w:{len(max(lst, key=len)) + 1}}|  ", file=f)

def make_question(message: str, tuple_of_variants: Union[Tuple[str, ...], List[str]] = ("да", "lf", "1"), add: bool = False) -> bool:
    default = ("да", "lf", "1")
    q = input(message + ' ').lower().strip()
    if add:
        fin_tuple = tuple_of_variants + default
    else:
        fin_tuple = tuple_of_variants
    if q in fin_tuple:
        return True
    else:
        return False

#Часть с проверкой работ
variants_of_check = ("проверку", "проверка", "проверку работ", "проверка работ", "1")
mainchoose = input("Что вы хотите сделать?\nПроверка работ(1)\nПоиск по имени(2)\nГенерация директорий и файлов(3)\nПомощь(4)\nСтатистика(5)\nCброс(6)\nВыход(0)\n")
if mainchoose in variants_of_check:
    with open("example.txt", "a+", encoding="UTF-8") as file:
        file.seek(0)
        try:
            cv = file.readlines()
            if cv[4].split(" |  ")[1] == "\n" or cv[3].split(" |  ")[1] == "\n" or cv[5].split(" |  ")[1] == "\n" or cv[6].split(" |  ")[1] == "\n" or cv[7].split(" |  ")[1] == "\n" or cv[8].split(" |  ")[1] == "\n" or cv[2].split(" |  ")[1] == "\n" or cv[9].split(" |  ")[1] == "\n":
                os.startfile(os.path.join(os.getcwd(), 'example.txt'))
            else:
                print("В файле уже есть некоторые данные. Программа будет запущена, используя их.")
                file.seek(0)
                next(file)
                next(file)
                lstt = ["klass", "name_of_work", "file_answers", "file_marks", "date", "list_of_puples", "list_of_the_missing", "folder_name"]
                dct = {k: v for k, v in zip(lstt, map(lambda x: x.split(" |  ")[1].strip(), file.readlines()))}
        except IndexError:
            makeexfile("example.txt")
            print("Перезапустите программу.")

    try:
        try:
            folder_name = dct["folder_name"]
            puple_dct = []
            current_directory = os.path.dirname(os.path.abspath(__file__))
            folder_path = os.path.join(current_directory, folder_name)
            files_in_folder = os.listdir(folder_path)
            files_dict = {filename: os.path.join(folder_path, filename) for filename in files_in_folder}
            dct_of_pup_answers = {}
        except NameError:
            sys.exit()
        for k, v in files_dict.items():
            with open(v, encoding="UTF-8") as filepuple:
                g = os.path.basename(v).split(".")[0].split("_")
                fullname = f'{g[0]} {g[1]}'.title()
                lastpupansw = list(map(lambda x: x.strip().split()[1], filter(lambda x: ' ' in x, filepuple.readlines())))
                dct_of_pup_answers[fullname] = lastpupansw

        statflag = False
        marksflag = False
        if make_question("Вам нужны подробные отчеты по ученику или классу? Для подробной статистики будет создан дополнительный системны json-файл."):
            statflag = True

        if make_question("В файле marks.txt записаны в форме баллов?"):
            marksflag = True

        sort_mode = input("Выберите режим сортировки(enter, чтобы не сортировать):\nпо оценкам(1)\nпо именам(2)\n").strip().lower()

        with open(dct["file_answers"], encoding="UTF-8") as fileanswers:
            lstansw = list(map(lambda x: x.strip().split()[1], fileanswers.readlines()))
        counter_right = 0
        dct_of_counter_aswers = {}
        for k, v in dct_of_pup_answers.items():
            counter_right = 0
            for i in range(len(lstansw)):
                try:
                    if v[i].strip() == lstansw[i].strip():
                        counter_right += 1
                except IndexError:
                    pass
            dct_of_counter_aswers[k] = counter_right

        if statflag:
            dct_stat = merge_dictionaries(dct_of_pup_answers, dct_of_counter_aswers)

        with open(dct["file_marks"], encoding="UTF-8") as filemarks:
            marks = {}
            dct_of_pup_marks = {}

            if marksflag:
                for line in filemarks.readlines():
                    try:
                        point, percents = line.strip().split("\t")
                        marks[int(point)] = int(percents)
                    except ValueError:
                        print("Похоже, что в файлe marks.txt расписаны не баллы, а оценки. Свертьесь с инструкцией.")
                        sys.exit()

                try:
                    dct_of_pup_marks = {k: marks[v] for k, v in dct_of_counter_aswers.items()}

                except KeyError:
                    print("В системе разбалловки допущена ошибка. Выполнение программы прервано. Провертье файл marks.txt. ")
                    sys.exit()
            else:
                try:
                    for line in filemarks.readlines():
                        mark, f, st, h, end = line.strip().split()
                        for i in range(int(st), int(end) + 1):
                            marks[i] = int(mark)
                except ValueError:
                    print("Похоже, что в файлe marks.txt расписаны не баллы, а оценки. Свертьесь с инструкцией.")
                    sys.exit()
                try:
                    dct_of_pup_marks = {k: marks[v] for k, v in dct_of_counter_aswers.items()}

                except KeyError:
                    print("В системе разбалловки допущена ошибка. Выполнение программы прервано. Провертье файл marks.txt. ")
                    sys.exit()


        if statflag:
            dct_stat_to_write = flatten_tuples(merge_dictionaries(dct_stat, dct_of_pup_marks))

        dct_of_missings = {}
        filenaming = dct["list_of_the_missing"]
        with open(filenaming, encoding="UTF-8") as filemiss:
            file_miss = list(map(lambda x: x.strip(), filemiss.readlines()))
            for li in file_miss:
                try:
                    name_, sername_, status = li.split()
                    dct_of_missings[(name_ + " " + sername_).title()] = status
                except ValueError:
                    if li.split()[1].endswith("а") is True:
                        dct_of_missings[li] = "отсутствовала"
                    else:
                        dct_of_missings[li] = "отсутствовал"
        dct_of_pup_marks.update(dct_of_missings)


        print()
        print("Проверка завершена. Программа запишет результаты в файл и положит его в архив. Папка с работами также будет перемещена в архив. Вы можете удалить ее.")

        s = makedirs("archive", dct)
        folder_name = dct['folder_name']
        current_directory = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.join(current_directory, folder_name)
        source_folder = folder_path  # Папка, которую нужно перенести
        target_folder = s  # Куда переносим
        if os.path.exists(source_folder):
            try:
                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)
                shutil.copytree(source_folder, os.path.join(target_folder, os.path.basename(source_folder)))
            except OSError as e:
                pass
        else:
            print(f"Папка {source_folder} не найдена.")
        decname = f'{dct["name_of_work"].lower().strip()} за {dct["date"]}.txt'
        filepath = os.path.join(s, decname)

        if statflag:
            dct_stat_to_write["miss"] = len(dct_of_missings)
            dct_stat_to_write["answers"] = lstansw
            jsonname = f'sysfile_{dct["name_of_work"].lower().strip()}_{dct["date"]}.json'
            path_to_json = os.path.join(s, jsonname)
            with open(path_to_json, "w", encoding="utf-8") as jsonstatfile:
                json.dump(dct_stat_to_write, jsonstatfile, ensure_ascii=False)

        with open(filepath, "w", encoding="UTF-8") as file:
            try:
                print(dct["klass"], file=file)
                print(f'{dct["name_of_work"]} за {dct["date"]}', file=file)
                print(file=file)
                #сортировка


                if sort_mode == "2" or sort_mode == "по именам":
                    for k, v in sorted(dct_of_pup_marks.items()):
                        print(f'{k:{len(max(dct_of_pup_marks.keys(), key=len))}} {v}', file=file)

                elif sort_mode == "1" or sort_mode == "по оценкам":
                    for k, v in sorted(dct_of_pup_marks.items(), key=lambda x: float('inf') if isinstance(x[1], str) else x[1]):
                        print(f'{k:{len(max(dct_of_pup_marks.keys(), key=len))}} {v}', file=file)
                else:
                    for k, v in dct_of_pup_marks.items():
                        print(f'{k:{len(max(dct_of_pup_marks.keys(), key=len))}} {v}', file=file)

            except ValueError:
                print("Непредвиденная ошибка.")
                sys.exit()

        if statflag:
            print(f"Все готово. Результаты проверки записаны в файл '{decname}'. Теперь для этой работы доступна подробная статистика. Вы можете открыть ее из главного меню.")
        else:
            print(f"Все готово. Результаты записаны в файл '{decname}'.")
        print()

        if make_question(f"Открыть файл '{decname}'?"):
            os.startfile(filepath)

    except FileNotFoundError as e:
        print("Папка или файл не найдены.", e)
        if make_question("Открыть example.txt для изменения данных?"):
            try:
                os.startfile(os.path.join(os.getcwd(), "example.txt"))
            except FileNotFoundError:
                print("Что-то пошло не так. Попробуйте перезапустить программу, проверьте данные в файлах. Если не помогает, сделайте сброс из главного меню.")
        else:
            sys.exit()

#Поиск по архиву
variants_of_find = ("поиск", "поиск по имени", "2")
if mainchoose in variants_of_find:
    search_string = input("Введите имя фамилию ученика. ").strip()
    folder = input("Поиск будет производится в папке 'archive'. Укажите полный путь к файлу с работой, в котором хотите выполнить поиск. Введите 'skip' чтобы искать по всему архиву. ").strip().lower()
    if folder == 'skip' or folder == "пропуск":
        folder_name = "archive"
        if make_question("Предупреждение: если в архиве слишком большое количество файлов, программа может работать слишком долго. Продолжить?"):
            current_directory = os.getcwd()
            folder_path = os.path.join(current_directory, folder_name)
            found_line = search(folder_path, search_string)
            if found_line is not None:
                for k, v in found_line.items():
                    print(f"В файле по пути {k} - {v}")
            else:
                print("Ученик не найден. Проверьте правильность написания данных.")
        else:
            sys.exit()
    else:
        filename = folder
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                for line in file:
                    if search_string in line:
                        print(line.strip())
                        break
                else:
                    print("Ученик не найден. Проверьте правильность написания данных.")
        except FileNotFoundError:
            print("Файл не найден.")


#Генерация
flaggg = False
variants_of_generation = ("3", "генерация", "генерацию", "генерация директорий и файлов", "генерацию директорий и файлов")
if mainchoose in variants_of_generation:
    print("Программа создаст пустые файлы в папке с программой и перезапишет их содержимое, если они уже созданы и имеют те же имена.")
    if make_question("Перезаписывать ли файлы answers.txt, marks.txt и missings.txt?"):
        flaggg = True
        try:
            if make_question("Нужны ли строки для ответов в файле 'answers.txt'?"):
                linesinansw = int(input("Cколько строк для ответов необходимо в файле 'answers.txt'? ").strip())
        except ValueError:
            print("Введите число.")
            sys.exit()
    sfsf = input("Укажите название файла с именами учеников. ")
    jgjg = input("Укажите, как назвать папку с файлами учеников. Совет: лучше называть папку по названию работы. ")
    linespup = make_question("Нужны ли строки для ответов в ученических файлах?")
    if linespup:
        rere = int(input("Сколько? "))
    passing = input("Нажмите enter для начала генерации. ")

    base_directory = os.path.dirname(os.path.abspath(__file__))
    new_folder_path = os.path.join(base_directory, jgjg)
    os.makedirs(new_folder_path, exist_ok=True)
    try:
        with open(sfsf, "r", encoding="utf-8") as file:
            for line in file:
                pupfilename = line.strip().split()[0].lower()+'_'+line.strip().split()[1].lower()+".txt"
                puppath = os.path.join(new_folder_path, pupfilename)
                with open(puppath, "w", encoding="utf-8") as surinamskay_pipa:
                    if linespup:
                        try:
                            for i in range(1, linesinansw+1):
                                print(f'{i})', file=surinamskay_pipa)
                        except NameError:
                            for i in range(1, rere+1):
                                print(f'{i})', file=surinamskay_pipa)
                    else:
                        pass
    except FileNotFoundError:
        print("Файл с именами учеников не найден.")
    if flaggg is True:
        with open("missings.txt", "w", encoding="utf-8") as f:
            pass
        with open("answers.txt", "w", encoding="utf-8") as f:
            for k in range(1, linesinansw+1):
                print(f'{k}) ', file=f)
        with open("marks.txt", "w", encoding="utf-8") as fl:
            for l in range(2, 6)[::-1]:
                fl.write(f'{l} от _ до _\n')
        print(f"Все готово, программа создала файлы: 'missings.txt', 'answers.txt' и 'marks.txt' и папку {jgjg}, внутри которой находятся файлы учеников. Файл 'example.txt' будет создан при выборе режима проверки работ.")
    print("Все готово.")

#Принудительный выход
if mainchoose == "0" or mainchoose == "выход":
    sys.exit(0)

#Статистика(.
variants_of_statistic = ("cтатистика", "5")
if mainchoose in variants_of_statistic:
    statchoose = input("Напишите название папки класса с работами из архива. ")
    diripathka = os.path.join(os.getcwd(), "archive", statchoose)

    lst_of_statfiles = []
    try:
        justfortrex = os.listdir(diripathka)
        for li in justfortrex:
            try:
                pp = li.split(".")[1]
                lst_of_statfiles.append(li)
            except IndexError:
                pass
    except FileNotFoundError:
        print("Папка не найдена. ")
    lst_tup_files_stat = find_pairs(lst_of_statfiles)




    if len(lst_tup_files_stat) == 1:
        if len(lst_tup_files_stat[0]) == 1:
            print("В архиве только один файл. По нему не доступна подробная статистика. Будет дана краткая статистика и записана в одноразовый файл.")
            fullpathtofilefromstat = os.path.join(os.getcwd(), "archive", statchoose, lst_tup_files_stat[0][1])
            with open(fullpathtofilefromstat, "r", encoding="utf-8") as filefromstat:
                lstforstat = []
                next(filefromstat)
                next(filefromstat)
                for li in filefromstat:
                    try:
                        lstforstat.append(int(li.split()[2]))

                    except:
                        pass
                give_short_stat(lstforstat, lst_tup_files_stat)
                print("Все готово. Краткая статистика записана в файл 'statisticsfile.txt'.")
                if make_question("Открыть файл?"):
                    os.startfile('statisticsfile.txt')
                else:
                    sys.exit()

        else:
            varianst_of_short = ("краткую", "краткую статистику", "краткая статистика", "краткая", "0")
            variants_of_long = ("подрбную", "подробную статистику", "подробная статистика", "подробная", "1")
            shortorlong = input("В архиве только один файл. По нему достпна краткая(0) и подробная(1) статистика. Какую статистику вы хотели бы получить? ")
            if shortorlong in varianst_of_short:
                fullpathtofilefromstat = os.path.join(os.getcwd(), "archive", statchoose, lst_tup_files_stat[0][1])
                with open(fullpathtofilefromstat, "r", encoding="utf-8") as filefromstat:
                    lstforstat = []
                    next(filefromstat)
                    next(filefromstat)

                    for li in filefromstat:
                        try:

                            lstforstat.append(int(li.split()[2]))
                        except ValueError:
                            pass
                        except IndexError:
                            pass
                    give_short_stat(lstforstat, lst_tup_files_stat)
                    print("Все готово. Краткая статистика записана в файл 'statisticsfile.txt'.")
                    if make_question("Открыть файл?"):
                        os.startfile('statisticsfile.txt')
                    else:
                        sys.exit()
            elif shortorlong in variants_of_long:
                jsonfile = os.path.join(os.getcwd(), "archive", statchoose, sorted(lst_tup_files_stat[0])[0])
                txtfile = os.path.join(os.getcwd(), "archive", statchoose, sorted(lst_tup_files_stat[0])[1])
                with open(jsonfile, "r", encoding="utf-8") as jsonfileobj:
                    jsonstatdct = json.load(jsonfileobj)
                    classorpup = input("Вам нужен отчет по целому классу(0) или по конкретному ученику(1)? ").lower().strip()
                    variants_of_class = ("по классу", "класс", "класс", "0")
                    variants_of_puples = ("по ученику", "ученику", "ученик", "1")
                    if classorpup in variants_of_puples:
                        statnamepup = input("Введите имя ученика. ")

                        try:
                            forexcept = jsonstatdct[statnamepup]
                        except KeyError:
                            print(f"Ученика {statnamepup} не найдено или он отсутствовал в момент написания работы.")
                            sys.exit()

                        with open("statisticsfile.txt", "w", encoding="utf-8") as statfile:
                            file_pathstat = Path(txtfile)
                            filenamestat = file_pathstat.stem
                            print(f"Отчет по ученику {statnamepup} по работе {filenamestat}", file=statfile)
                            print(file=statfile)

                            for i in range(len(jsonstatdct["answers"])):
                                try:
                                    if jsonstatdct["answers"][i] == jsonstatdct[statnamepup][0][i]:
                                            print(f"{i+1} - Верно", file=statfile)
                                    else:
                                        print(f"{i+1} - Неверно. Правильный ответ {jsonstatdct['answers'][i]}, ответ ученика {jsonstatdct[statnamepup][0][i]}", file=statfile)
                                except IndexError:
                                    pass
                            print(file=statfile)
                            print(f"Верных ответов: {jsonstatdct[statnamepup][1]}", file=statfile)
                            print(f"Оценка за работу: {jsonstatdct[statnamepup][2]}", file=statfile)

                            if make_question("Все готово. Отчет записан в одноразовый файл statisticsfile.txt. Открыть файл?"):
                                os.startfile("statisticsfile.txt")

                    elif classorpup in variants_of_class:
                        jsonfile = os.path.join(os.getcwd(), "archive", statchoose, sorted(lst_tup_files_stat[0])[0])
                        txtfile = os.path.join(os.getcwd(), "archive", statchoose, sorted(lst_tup_files_stat[0])[1])

                        with open(jsonfile, "r", encoding='utf-8') as json_file_class_stat:
                            jsonstatclassdct = json.load(json_file_class_stat)
                            total_students = len(jsonstatclassdct)-2
                            result = {}
                            for i, answer in enumerate(jsonstatclassdct['answers']):
                                correct_count = 0
                                for student_name, student_data in jsonstatclassdct.items():
                                    if isinstance(student_data, list) and student_name != 'miss' and student_name != 'answers':
                                        if len(student_data[0]) > i:
                                            if student_data[0][i] == answer:
                                                correct_count += 1
                                result[i + 1] = round(correct_count / (total_students) * 100, 2)

                        with open("statisticsfile.txt", "w", encoding="utf-8") as statfile:
                            file_pathstat = Path(txtfile)
                            filenamestat = file_pathstat.stem
                            print(f"Отчет по класcу {statchoose} по работе {filenamestat}.", file=statfile)
                            print(file=statfile)
                            print("Статистика по каждому заданию:", file=statfile)

                            for k, v in result.items():
                                print(f"{k}) {v}% правильных ответов", file=statfile)

                            print(file=statfile)

                            with open(txtfile, "r", encoding='utf-8') as filstatreadtxt:
                                next(filstatreadtxt)
                                next(filstatreadtxt)
                                next(filstatreadtxt)
                                lst_of = list(map(lambda x: x.split()[2], filstatreadtxt.readlines()))
                            lst_of_module = []
                            for li in lst_of:
                                try:
                                    lst_of_module.append(int(li))
                                except ValueError:
                                    pass
                            #запись в файл
                            deep_stat(statfile=statfile, lst_of_module=lst_of_module)
                        print("Подробная статистика записана в одноразовый файл 'statisticsfile.txt'. ")

                        if make_question("Открыть файл и визуализацию?"):
                            os.startfile("statisticsfile.txt")
                            plt.style.use("dark_background")

                            grades_count = collections.Counter(lst_of_module)

                            task_results = result

                            colors_grades = [
                                'green' if g == 5 else
                                'blue' if g == 4 else
                                'orange' if g == 3 else
                                'red' if g == 2 else
                                'black'
                                for g in grades_count.keys()
                            ]

                            fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

                            axs[0].bar(grades_count.keys(), grades_count.values(), color=colors_grades)
                            axs[0].set_title('Распределение оценок')
                            axs[0].set_xlabel('Оценки')
                            axs[0].set_ylabel('Количество')
                            axs[0].set_xticks(list(grades_count.keys()))

                            axs[1].bar(task_results.keys(), task_results.values(), color='skyblue')
                            axs[1].set_title('Процент правильных ответов по заданиям')
                            axs[1].set_xlabel('Номер задания')
                            axs[1].set_ylabel('% правильных ответов')
                            axs[1].set_xticks(list(task_results.keys()))

                            plt.tight_layout()
                            plt.show()
                            # конец записи
    else:
        if len(lst_tup_files_stat) > 0:
            dct_stat_self = {}
            dct_stat_num = {}
            print("В архиве несколько файлов:")
            for n, t in enumerate(sorted(lst_tup_files_stat), 1):
                print(n, t[1])
                dct_stat_self[t[1]] = t
                dct_stat_num[str(n)] = t
            qstat = input("Напишите название файла или его номер. ")
            path_to_statfile_need = collections.ChainMap(dct_stat_num, dct_stat_self)[qstat]
            if len(path_to_statfile_need) == 2:
                varianst_of_short = ("краткую", "краткую статистику", "краткая статистика", "краткая", "0")
                variants_of_long = ("подрбную", "подробную статистику", "подробная статистика", "подробная", "1")
                shortorlong = input("Для выбранного файла достпна краткая(0) и подробная(1) статистика. Какую статистику вы хотели бы получить? ")
                if shortorlong in varianst_of_short:
                    fullpathtofilefromstat = os.path.join(os.getcwd(), "archive", statchoose, lst_tup_files_stat[0][1])
                    with open(fullpathtofilefromstat, "r", encoding="utf-8") as filefromstat:
                        next(filefromstat)
                        next(filefromstat)
                        lstforstat = []
                        for li in filefromstat:
                            try:
                                lstforstat.append(int(li.split()[2]))
                            except ValueError:
                                pass
                            except IndexError:
                                pass
                        give_short_stat(lstforstat, lst_tup_files_stat)
                        print("Все готово. Краткая статистика записана в файл 'statisticsfile.txt'.")
                        if make_question("Открыть файл?"):
                            os.startfile('statisticsfile.txt')
                        else:
                            sys.exit()
                elif shortorlong in variants_of_long:
                    jsonfile = os.path.join(os.getcwd(), "archive", statchoose, sorted(lst_tup_files_stat[0])[0])
                    txtfile = os.path.join(os.getcwd(), "archive", statchoose, sorted(lst_tup_files_stat[0])[1])
                    with open(jsonfile, "r", encoding="utf-8") as jsonfileobj:
                        jsonstatdct = json.load(jsonfileobj)
                        classorpup = input("Вам нужен отчет по целому классу(0) или по конкретному ученику(1)? ").lower().strip()
                        variants_of_class = ("по классу", "класс", "класс", "0")
                        variants_of_puples = ("по ученику", "ученику", "ученик", "1")
                        if classorpup in variants_of_puples:
                            statnamepup = input("Введите имя ученика. ")

                            try:
                                forexcept = jsonstatdct[statnamepup]
                            except KeyError:
                                print(
                                    f"Ученика {statnamepup} не найдено или он отсутствовал в момент написания работы.")
                                sys.exit()

                            with open("statisticsfile.txt", "w", encoding="utf-8") as statfile:
                                file_pathstat = Path(txtfile)
                                filenamestat = file_pathstat.stem
                                print(f"Отчет по ученику {statnamepup} по работе {filenamestat}", file=statfile)
                                print(file=statfile)

                                for i in range(len(jsonstatdct["answers"])):
                                    try:
                                        if jsonstatdct["answers"][i] == jsonstatdct[statnamepup][0][i]:
                                            print(f"{i + 1} - Верно", file=statfile)
                                        else:
                                            print(
                                                f"{i + 1} - Неверно. Правильный ответ {jsonstatdct['answers'][i]}, ответ ученика {jsonstatdct[statnamepup][0][i]}",
                                                file=statfile)
                                    except IndexError:
                                        pass
                                print(file=statfile)
                                print(f"Верных ответов: {jsonstatdct[statnamepup][1]}", file=statfile)
                                print(f"Оценка за работу: {jsonstatdct[statnamepup][2]}", file=statfile)

                                if make_question(
                                        "Все готово. Отчет записан в одноразовый файл statisticsfile.txt. Открыть файл?"):
                                    os.startfile("statisticsfile.txt")

                        elif classorpup in variants_of_class:
                            jsonfile = os.path.join(os.getcwd(), "archive", statchoose, sorted(lst_tup_files_stat[0])[0])
                            txtfile = os.path.join(os.getcwd(), "archive", statchoose, sorted(lst_tup_files_stat[0])[1])

                            with open(jsonfile, "r", encoding='utf-8') as json_file_class_stat:
                                jsonstatclassdct = json.load(json_file_class_stat)
                                total_students = len(jsonstatclassdct) - 2
                                result = {}
                                for i, answer in enumerate(jsonstatclassdct['answers']):
                                    correct_count = 0
                                    for student_name, student_data in jsonstatclassdct.items():
                                        if isinstance(student_data, list) and student_name != 'miss' and student_name != 'answers':
                                            if len(student_data[0]) > i:
                                                if student_data[0][i] == answer:
                                                    correct_count += 1
                                    result[i + 1] = round(correct_count / (total_students) * 100, 2)

                            with open("statisticsfile.txt", "w", encoding="utf-8") as statfile:
                                file_pathstat = Path(txtfile)
                                filenamestat = file_pathstat.stem
                                print(f"Отчет по класcу {statchoose} по работе {filenamestat}.", file=statfile)
                                print(file=statfile)
                                print("Статистика по каждому заданию:", file=statfile)
                                for k, v in result.items():
                                    print(f"{k}) {v}% правильных ответов", file=statfile)
                                print(file=statfile)

                                with open(txtfile, "r", encoding='utf-8') as filstatreadtxt:
                                    next(filstatreadtxt)
                                    next(filstatreadtxt)
                                    next(filstatreadtxt)
                                    lst_of = list(map(lambda x: x.split()[2], filstatreadtxt.readlines()))
                                lst_of_module = []
                                for li in lst_of:
                                    try:
                                        lst_of_module.append(int(li))
                                    except ValueError:
                                        pass
                                #еще одна запись в файл
                                deep_stat(statfile=statfile, lst_of_module=lst_of_module)
                            print("Подробная статистика записана в одноразовый файл 'statisticsfile.txt'. ")
                            if make_question("Открыть файл и визуализацию?"):
                                os.startfile("statisticsfile.txt")
                                plt.style.use("dark_background")

                                grades_count = collections.Counter(lst_of_module)

                                task_results = result

                                colors_grades = [
                                    'green' if g == 5 else
                                    'blue' if g == 4 else
                                    'orange' if g == 3 else
                                    'red' if g == 2 else
                                    'black'
                                    for g in grades_count.keys()
                                ]

                                fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

                                axs[0].bar(grades_count.keys(), grades_count.values(), color=colors_grades)
                                axs[0].set_title('Распределение оценок')
                                axs[0].set_xlabel('Оценки')
                                axs[0].set_ylabel('Количество')
                                axs[0].set_xticks(list(grades_count.keys()))

                                axs[1].bar(task_results.keys(), task_results.values(), color='skyblue')
                                axs[1].set_title('Процент правильных ответов по заданиям')
                                axs[1].set_xlabel('Номер задания')
                                axs[1].set_ylabel('% правильных ответов')
                                axs[1].set_xticks(list(task_results.keys()))

                                plt.tight_layout()
                                plt.show()
                            #конец еще одной записи в файл
            else:
                print("Для выбранного файла не доступна подробная статистика. Будет дана краткая статистика и записана в одноразовый файл.")
                fullpathtofilefromstat = os.path.join(os.getcwd(), "archive", statchoose, lst_tup_files_stat[0][1])
                with open(fullpathtofilefromstat, "r", encoding="utf-8") as filefromstat:
                    next(filefromstat)
                    next(filefromstat)
                    lstforstat = []
                    for li in filefromstat:
                        try:
                            lstforstat.append(int(li.split()[2]))
                        except:
                            pass
                    give_short_stat(lstforstat, lst_tup_files_stat)
                    print("Все готово. Краткая статистика записана в файл 'statisticsfile.txt'.")
                    if make_question("Открыть файл?"):
                        os.startfile('statisticsfile.txt')
                    else:
                        sys.exit()
        else:
            print("Архив пуст. ")
#Статистика конец слава Богу

#Сброс
variants_of_clear = ("сброс", "сбросить", "6")
if mainchoose in variants_of_clear:
    print("ВНИМАНИЕ! Действие необратимо. Программа удалит все файлы в папке archive, саму папку, а также файлы, указанные в файле example.txt и сам файл example.txt.\nЕсли вам нужны какие-то работы, скопируйте их в любую другую папку.")
    if make_question("Хотите выйти, чтобы скопировать файлы?"):
        sys.exit()
    else:
        with open("clear.txt", "w", encoding="utf-8") as clearfile:
            password = randint(1000, 10000)
            print(f"Код доступа для сброса файлов программы: {password}", file=clearfile)
        print("Для уверенности в том, что действие не случайно программа создала файл clear.txt в папке с программой, в котором сгенерирован код доступа.")
        if make_question("Открыть папку с программой в проводнике?"):
            os.startfile(os.path.dirname(__file__))
        justinput = input("Введите код доступа из файла clear.txt. ")

        try:
            justinput = int(justinput)
        except ValueError:
            print("Код доступа не верен. ")
        if justinput == password:
            if make_question("Очистить файлы?"):
                clearpathlast = os.path.join(os.getcwd(), "archive")
                if os.path.exists(clearpathlast):
                    shutil.rmtree(clearpathlast)
                    print(f"Папка 'archive' успешно удалена.")
                else:
                    pass

                with open("example.txt", "r", encoding='utf-8') as file_to_dct:
                    file_to_dct.seek(0)
                    next(file_to_dct)
                    next(file_to_dct)
                    lstt = ["klass", "name_of_work", "file_answers", "file_marks", "date", "list_of_puples", "list_of_the_missing", "folder_name"]
                    dct = {k: v for k, v in zip(lstt, map(lambda x: x.split(" |  ")[1].strip(), file_to_dct.readlines()))}
                    lst_to_clear = list(filter(lambda x: x.endswith(".txt"), list(dct.values())))
                    lst_to_clear.append("clear.txt")
                    lst_to_clear.append("example.txt")
                    lst_to_clear.append("statisticsfile.txt")
                    current_dir = os.getcwd()
                    full_paths = [os.path.join(current_dir, file_name) for file_name in lst_to_clear]

                for path in full_paths:
                    if os.path.exists(path):
                        os.remove(path)
                    else:
                        pass
                print("Все файлы сброшены. ")
        else:
            print("Код доступа не верен. ")

#инструкция
variants_of_help = ("помощь", "4", "инструкция")
if mainchoose in variants_of_help:
    jkjkl = input("Открыть в блокноте(0) или в облаке(1)? ")
    if jkjkl == "0":
        try:
            os.startfile("instruction.pdf")
        except FileNotFoundError:
            print("Файл с инструкцией не найден. Перейдите по этой ссылке для получения инструкции и желательно скачать ее, сохранив в паку с программой:", "https://drive.google.com/file/d/1srY94uqyID0YCxYZAoZkHI3htBNsrdJe/view?usp=sharing")
    elif jkjkl == "1":
        print("https://docs.google.com/document/d/1S9ieHxj4aoRAPVfbrDfXhy5ilpjWs64n3QJ6ZtwZpF0/edit?usp=sharing")
    else:
        print("Неизвестная команда.")


end = time.monotonic()

if mainchoose == "testmode":
    print("testmode actived")
    isitend = input("random(0) or debbaging(1)? ").strip()
    if isitend == "1":
        print(f"time: {end-start} сек.")
        print(f"main directory: {os.getcwd()}")
        version_info = sys.version_info
        print(f"Python: {version_info.major}.{version_info.minor}.{version_info.micro}")
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        for stat in top_stats:
            print(stat)
    elif isitend == "0":
        pupleslen = int(input("Сколько учеников? ").strip())
        inputing = "\n"
        lstofrandom = list(range(1, pupleslen+1))
        while inputing != "stop":
            if lstofrandom:
                numpup = randint(0, len(lstofrandom)-1)
                print(f"Ученик номер {lstofrandom[numpup]};")
                lstofrandom.pop(numpup)
                inputing = input()
            else:
                print("Вы всех спросили. ")
                break
    else:
        sys.exit()

