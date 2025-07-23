import datetime
from collections import namedtuple
import signal
import time
from modules.CONFIG_classes_checking import *
from modules.CONFIG_functions import *
from modules.CONFIG_classes_compare import *
from modules.CONFIG_classes_find_and_generator import *
from modules.CONFIG_classes_rcall_and_delete import *


# noinspection PyGlobalUndefined
def handle_stop_signal(signum, frame):
    print("\nПрограмма остановлена.")
    dev.write_to_file('KeyboardInterrapt', True)
    dev.write_to_file('datetime_kill', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    exit(0)


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

# noinspection PyTypedDict
class SettingsGeneration:
    """
    Обрабатывает процесс ввода параметров для генерации файлов.
    Содержит набор шагов для сбора информации от пользователя: название работы, файлы учеников, ответов, критериев и т.д.
    """

    def __init__(self):
        self.inputs = {
            "name_of_work": None,
            "pupe_file": None,
            "count_strings_pup": None,
            "answers_file": None,
            "template_lines": None,
            "criteria_file": None,
            "grading_scale": None,
            "absentees_file": None
        }

    class Questions:
        """
        Вспомогательный класс для создания вопросов с пользовательским вводом.
        Поддерживает выбор из заданных вариантов.
        """

        def __init__(self, question, tuple_of_variants=('1', 'lf', 'да')):
            self.question = question
            self.tuple_of_variants = tuple_of_variants

        def make_question(self):
            """
            Задаёт вопрос пользователю и проверяет, попал ли ответ в список допустимых вариантов.
            """
            if input(self.question).strip().lower() in self.tuple_of_variants:
                return True
            else:
                return False

    @staticmethod
    def validate_integer(prompt):
        """
        Получает от пользователя целое число.
        Повторяет запрос, пока не будет введено корректное значение.
        """
        while True:
            try:
                return abs(int(input(prompt)))
            except ValueError:
                print("Введите корректное целое число.")

    def step_get_name_of_work(self):
        """
        Спрашивает у пользователя название работы.
        """
        self.inputs["name_of_work"] = input("Введите название работы: ").strip()

    def step_get_pupe_file(self):
        """
        Спрашивает, нужны ли файлы учеников, и если да — запрашивает имя файла.
        Проверяет существование файла и количество строк для ответов.
        """
        sm = self.Questions("Нужны ли файлы учеников? ")
        if sm.make_question():
            pupe_file = input("Введите название файла учеников: ").strip()
            if not os.path.exists(pupe_file):
                print(f"Файл {pupe_file} не найден.")
                sys.exit()
            self.inputs["pupe_file"] = pupe_file

            sm = self.Questions("Нужны ли строки для ответов в файлах учеников? ")
            if sm.make_question():
                self.inputs["count_strings_pup"] = self.validate_integer("Введите количество строк для ответов: ")

    def step_get_answers_file(self):
        """
        Спрашивает, нужен ли файл с правильными ответами.
        Если да — запрашивает имя файла и создаёт шаблон при необходимости.
        """
        sm = self.Questions("Нужен ли файл с ответами? ")
        if sm.make_question():
            self.inputs["answers_file"] = input("Введите название файла с ответами: ").strip()

            sm = self.Questions("Создать файл по шаблону? ")
            if sm.make_question():
                self.inputs["template_lines"] = self.validate_integer("Введите количество строк для шаблона: ")

    def step_get_criteria_file(self):
        """
        Спрашивает, нужен ли файл с критериями оценивания.
        Если да — запрашивает имя файла и создаёт шаблон при необходимости.
        """
        sm = self.Questions("Нужен ли файл с критериями оценивания? ")
        if sm.make_question():
            self.inputs["criteria_file"] = input("Введите название файла с критериями: ").strip()

            sm = self.Questions("Создать файл по шаблону? ")
            if sm.make_question():
                self.inputs["grading_scale"] = self.validate_integer("Введите шкалу оценивания: ")

    def step_get_absentees_file(self):
        """
        Спрашивает, нужен ли файл с отсутствующими.
        Если да — запрашивает имя файла.
        """
        sm = self.Questions("Нужен ли файл с отсутствующими? ")
        if sm.make_question():
            self.inputs["absentees_file"] = input("Введите название файла с отсутствующими: ").strip()

    def run_survey(self):
        """
        Запускает весь опрос: собирает информацию по всем этапам.
        Возвращает заполненный словарь с данными.
        """
        self.step_get_name_of_work()
        self.step_get_pupe_file()
        self.step_get_answers_file()
        self.step_get_criteria_file()
        self.step_get_absentees_file()
        return self.inputs


print('Insighter 1.0 BETA. Система анализа, контроля и проверки ученических работ') #заголовок программы
print(f'Запуск: {datetime.now().strftime('%m.%d, %H:%M:%S')}' )
print()

#начало программы
debug = False


if os.path.exists('syslog.json'):
    with open('syslog.json', 'r', encoding='utf-8') as sys_file:
        logdct = json.load(sys_file)
        if logdct['debug']:
            debug = True

try:
    with open('syslog.json', 'w', encoding='utf-8') as sys_file:
        json.dump({'debug': False}, sys_file, indent=4, ensure_ascii=False)
except Exception:
    print('Ошибка записи в файл syslog.json')
    sys.exit()


dev = DebugMode(debug)


if os.path.isfile('sys.json') and len(json.load(open('sys.json'))) == 8:
    try:
        with open('sys.json', 'r', encoding='utf-8') as sys_file:
            main_dct = json.load(sys_file)
    except Exception:
        print('Основной системный файл sys.json повреждён или не найден. Сверьтесь с инструкцией')
        sys.exit()

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
            dev.write_to_file('errors', formatting.errors)
            for error in formatting.errors:
                print(error)
            sys.exit()
        elif isinstance(formatting.check_all(), bool):
            with open('sys.json', 'w', encoding='utf-8') as sys_json_file:
                json.dump(results._asdict(), sys_json_file, ensure_ascii=False, indent=4)
                print('Данные сохранены, перезапустите программу.')
                dev.write_to_file('data_saved', True)
                sys.exit()
        else:
            print('Непредвиденная ошибка при проверке формата данных.')
            dev.write_to_file('unknown_error', 'Непредвиденная ошибка при проверке формата данных.')
            sys.exit()
    else:
        print('Вы оставили какое-то поле не заполненным. Программа остановлена.')
        dev.write_to_file('empty_field', True)
        sys.exit()


dct_variants = {
    'check_works': ('1', 'проверка', 'проверка работ'),
    'redact_data': ('2', 'редактирование', 'редактирование данных', 'перезапись', 'перезапись данных'),
    'find_puple': ('3', 'поиск по работам', 'поиск по работе', 'поиск'),
    'statistics': ('4', 'статистика', 'статистика работы', 'статистика работ'),
    'generate': ('5', 'генерация', 'генерация директорий и файлов'),
    'performance': ('6', 'случайный вызов'),
    'clear': ('7', 'сброс', 'сбросить', 'сбросить данные'),
    'compare': ('8', 'сравнить', 'сравнить работы'),
    'help': ('9', 'помощь', 'помощь по работе', 'помощь с программой')
}

if debug:
    print('Вы вошли в режим разработчика. Включен режим отладки.')
    print()


dev.write_to_file('datetime_start', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


signal.signal(signal.SIGINT, handle_stop_signal)
signal.signal(signal.SIGTERM, handle_stop_signal)


mainchoose = input('Выберите режим работы:\n'
                   '1. Проверка работ[1]\n'
                   '2. Перезапись данных[2]\n'
                   '3. Поиск по работам[3]\n'
                   '4. Статистика по работам[4]\n'
                   '5. Генерация директорий и файлов[5]\n'
                   '6. Случайный вызов[6]\n'
                   '7. Сброс данных[7]\n'
                   '8. Сравнить работы[8]\n'
                   '9. Помощь[9]\n').strip().lower()
dev.write_to_file('mainchoose', mainchoose)


if mainchoose in dct_variants['check_works']: #проверка работ
    print('Программа работает со следующими данными, если вы хотите измеенить их, то выберите режим измения данных:')
    for k, v in main_dct.items():
        print(f'{k}: {v}')

    print()

    stat_flag = False
    csv_flag = False

    qst = Questions('Вам нужны подробные отчеты по ученику или классу? Для подробной статистики будет создан дополнительный системный json-файл.\n')
    if qst.make_question():
        stat_flag = True



    qst0 = Questions('Записать результаты проверки в csv-файл? (при отрицательном ответе результаты будут записаны в txt-файл)\n')
    if qst0.make_question():
        csv_flag = True

    dev.write_to_file('stat_flag', stat_flag)
    dev.write_to_file('csv_flag', csv_flag)

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
        dev.write_to_file(k+'0', puples_dct[k].__dict__)

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
        dev.write_to_file(k+'1', puples_dct[k].__dict__)

    right_answers = Answers(main_dct['answer']) #создание экземпляра класса Answers
    lst_of_right_answers = right_answers.get_right_answers()


    for k, v in puples_dct.items(): #заполнение экземпляров класса Student количеством правильных ответов
        counter_right = 0
        response_list = []
        if len(v.list_answers) != len(lst_of_right_answers):
            v.flag_not_all = True
        for index, pupright in enumerate(zip(v.list_answers, lst_of_right_answers), 1):
            pup, right = pupright
            if pup == right:
                counter_right += 1
                response_list.append((index, True))
            else:
                response_list.append((index, False))
        v.correct_answers = counter_right
        v.response_status = response_list
        dev.write_to_file(k + '2', puples_dct[k].__dict__)

    m = Marks(main_dct['marks']) #создание экземпляра класса Marks

    try: #проверка корректности файла marks.txt
        marks_dct = m.get_marks()
    except ValueError as e:
        print(e)
        sys.exit()

    for k, v in puples_dct.items(): #заполнение экземпляров класса Student оценками
        try:
            mark = marks_dct[v.correct_answers]
            v.mark = mark
            dev.write_to_file(k + '3', puples_dct[k].__dict__)
        except KeyError:
            print('Возникла ошибка при получении оценки ученика. Проверьте файл с оценками.')
            dev.write_to_file('error_mark', True)
            sys.exit()


    string, puple_file = main_dct['missings'], main_dct['students'] #создание экземпляра класса Missings
    missings_puple = Missings(string, puple_file, puples_dct)
    print()

    for miss in missings_puple.get_missings(): #заполнение экземпляров класса Student отсутствующими учениками
        puples_dct[miss] = Student(*miss.split())
        puples_dct[miss].missings = True

    fm = FileManager(main_dct)
    smthpath = os.path.join(os.getcwd(), 'archive', main_dct['klass'], main_dct['name_work'])
    fm.copy_directory(main_dct['students_folder'], smthpath)
    filepath = fm.create_text_file_path()

    if stat_flag: #создание системного json-файла для статистики по флагу stat_flag
        halfpath = f'archive/{main_dct["klass"]}'
        fullpath = os.path.join(os.getcwd(), halfpath)
        filenamestat = f"sysfile_{main_dct['klass'].lower().strip()}_{main_dct['name_work'].lower().strip()}_{main_dct['date']}.json"
        fullfilepath = os.path.join(fullpath, filenamestat)
        with open(fullfilepath, 'w', encoding='utf-8') as f:
            json.dump(puples_dct, f, cls=StudentJSONEncoder, ensure_ascii=False, indent=4)
        dev.write_to_file('happy_end_stat', True)

    qst2 = input('Выберите режим сортировки:\n'
                     'По умолчанию[0]\n'
                     'По именам[1]\n'
                     'По оценкам(сначала лучшие)[2]\n'
                     'По оценкам(сначала худшие)[3]\n').lower().strip()

    dev.write_to_file('sorted_mode', qst2)

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
        dev.write_to_file('unknown_sort_mode', True)
        sys.exit()

    if not csv_flag:
        with open(filepath, 'w', encoding='utf-8') as file: #запись в итоговый файл
            print(f"Класс: {main_dct['klass']}", file=file)
            print(f"Название работы: {main_dct['name_work']}", file=file)
            print(f"Дата работы: {main_dct['date']}", file=file)
            print(file=file)
            for k, v in puples_dct:
                if v.missings:
                    print(f'{k}:    отсутствовал(а)', file=file)
                    dev.write_to_file(k+'4', 'miss')
                    continue
                star = ('*' if v.flag_not_all else '')
                print(f'{k}:    {v.mark}{star}', file=file)
    else:

        fm = FileManager(main_dct)
        filepath = fm.create_csv_file_path()
        fm.write_to_csv(filepath, puples_dct, main_dct)

    print(f'Проверка прошла успешно. Результаты проверки записаны в файл {filepath}.') #конец работы

    dev.write_to_file('happy_end', True)

    qst3 = Questions('Открыть файл?\n')
    dev.write_to_file('open_file', True)
    if qst3.make_question():
        os.startfile(filepath)
    dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


elif mainchoose in dct_variants['redact_data']: #перезапись данных, повторное открытие диалогового окна посредством удаления файла sys.json
    qst = Questions('Вы хотите перезаписать данные?\n')
    if qst.make_question():
        os.remove('sys.json')
        print('Файл данных удален. Перезапустите программу.')
        dev.write_to_file('happy_end', True)


elif mainchoose in dct_variants['find_puple']:
    print('Вы можете ввести имя интересующего вас файла или папки и имя ученика. Программа найдет оценки ученика в указанной папке или файле.')
    pupname = input('Введите имя ученика: ')
    dev.write_to_file('pupname', pupname)

    archivepath = os.path.join(os.getcwd(), 'archive')
    dct_find_dirs = {}
    for index, dir in enumerate(os.listdir(archivepath), 1): #генерация меню выбора и запись в словарь
        print(f'{dir}[{index}]')
        dct_find_dirs[index] = dir
        dev.write_to_file(dct_find_dirs[index], dir)
    try:    #ввод папки и проверка корректности
        input_dir = int(input('Введите номер папки, в которой хотите произвести поиск:\n'))
        dev.write_to_file('input_dir', input_dir)
    except Exception:
        print('Введите номер папки, а не название папки.')
        dev.write_to_file('error_input_dir', True)
        sys.exit()
    try:
        hghg = dct_find_dirs[int(input_dir)]
    except KeyError:
        print('Нет папки с таким номером.')
        dev.write_to_file('error_number_dir', True)
        sys.exit()

    dct_find_files = {}
    fullpathfind = os.path.join(archivepath, hghg)
    qst4 = input(f'Искать по папке {hghg}[1] или конкретному файлу?[0]\n')

    #основной блок с инициализацией экземпляров классов (директории)
    if qst4 in ('1', 'по папке'):
        dev.write_to_file('from_dir', True)
        fnd = Finding(pupname)
        found = fnd.find_from_dir(fullpathfind)
        if not found:
            print(f'Ученик {pupname} не найден в папке {hghg}')
            dev.write_to_file('pupname_not_found', True)
            sys.exit()
        else:
            dev.write_to_file('found', found)
            for line, filepath in found:
                print(f"В работе '{os.path.basename(filepath)}' - {line}")


    elif qst4 in ('0', 'по файлу'):#проверка корректности файла
        dev.write_to_file('from_file', True)
        filtered_list_dir = filter(lambda file: os.path.isfile(os.path.join(fullpathfind, file)) and (file.endswith('.txt') or file.endswith('.csv')) , os.listdir(fullpathfind))
        for index, file in enumerate(filtered_list_dir, 1):
            dct_find_files[index] = file
            print(f'{file}[{index}]')
        try:
            input_file = int(input('Введите номер файла, в которой хотите произвести поиск:\n'))
            dev.write_to_file('input_file', input_file)
        except Exception:
            print('Введите номер файла, а не название файла')
            dev.write_to_file('error_input_file', True)
            sys.exit()
        try:
            fgfg = dct_find_files[int(input_file)]
        except KeyError:
            print('Нет файла с таким номером')
            dev.write_to_file('error_number_file', True)
            dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            sys.exit()


        #основной блок с инициализацией экземпляров классов (файлы)
        found_file = Finding(pupname)
        found = found_file.find_from_file(os.path.join(fullpathfind, fgfg))
        if not found:
            print(f'Ученик {pupname} не найден в папке {hghg}')
            dev.write_to_file('pupname_not_found', True)
            sys.exit()
        else:
            dev.write_to_file('found', found)
            for line, filepath in found:
                print(f"В работе '{os.path.basename(filepath)}' - {line}")
        dev.write_to_file('happy_end', True)
        dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        sys.exit()


elif mainchoose in dct_variants['statistics']: #режим статистики по работам
    print('Вы в режиме статистики. Выберите папку') #генерация меню выбора папки, а затем файла, проврека корректности данных до следущего комментария
    dct_stat_chose = {}
    for index, dir in enumerate(os.listdir('archive'), 1):
        print(f'{dir}[{index}]')
        filepathrem = os.path.join(os.getcwd(), 'archive', dir)
        dct_stat_chose[index] = filepathrem
    chose_stat = input('Введите номер папки, по которой хотите получить статистику:\n')
    dev.write_to_file('chose_stat', chose_stat)
    try:
        chose_stat = int(chose_stat)
    except Exception:
        print('Введите номер папки')
        dev.write_to_file('error_chose_stat', True)
        sys.exit()
    try:
        chose_stat_p = dct_stat_chose[chose_stat]
    except KeyError:
        print('Нет папки с таким номером')
        dev.write_to_file('error_number_chose_stat', True)
        sys.exit()

    if not any(os.path.isfile(os.path.join(chose_stat_p, x)) for x in os.listdir(chose_stat_p)):
        print('Папка пуста') #проверка на пустоту папки
        dev.write_to_file('empty_chose_stat', True)
        sys.exit()

    brief_st = BriefStatistics()
    brief_st.set_pairs(chose_stat_p)

    dct_stat_choose_file = {}
    print('Выберите работу, статистику по которой хотите получить:')
    for index, pair in enumerate(brief_st.pairs, 1):
        print(f'{pair[0]}[{index}] {"<только краткая статистика>" if pair[1] is None else ""}')
        dct_stat_choose_file[index] = pair

    dev.write_to_file('dct_stat_choose_file', dct_stat_choose_file)

    try:
        choose_stat_work = int(input('Введите номер работы:\n'))
        dev.write_to_file('choose_stat_work', choose_stat_work)
    except Exception:
        print('Введите номер работы')
        dev.write_to_file('error_choose_stat_work', True)
        sys.exit()
    try:
        chosen_file = dct_stat_choose_file[choose_stat_work]
    except KeyError:
        print('Нет работы с таким номером')
        dev.write_to_file('error_number_choose_stat_work', True)
        sys.exit()

    chosen_pair = list(map(lambda x: x if x is None else os.path.join(chose_stat_p, x), chosen_file))
    dev.write_to_file('chosen_pair', chosen_pair)

    if chosen_pair[1] is None: #если доступна ТОЛЬКО краткая статистика, то не спрашиваем
        try:
            processed_data = BriefStatistics.process_file(chosen_pair[0])
            dev.write_to_file('processed_data', processed_data)
        except Exception:
            print('Формат файла не корректен')
            dev.write_to_file('error_format_file', True)
            sys.exit()

        processed_list = BriefStatistics.process_to_list(processed_data)
        dev.write_to_file('processed_list', processed_list)
        processed_dict = BriefStatistics.process_to_dict(processed_data)
        dev.write_to_file('processed_dict', processed_dict)
        brief = BriefStatistics(processed_list, processed_dict)


        with open('statistics.txt', 'w', encoding='utf-8') as statfile: #запись статистики в файл
            filename = Path(chosen_pair[0]).stem
            klass, name_work, date = filename.split('_')
            print(f'Краткая статистика по работе "{name_work}" класса {klass} за {date}:\n', file=statfile)
            print(f'Средняя оценка по классу: {brief.get_average()}', file=statfile)
            dev.write_to_file('average', brief.get_average())
            print(f'Медианное по классу: {brief.get_median()}', file=statfile)
            dev.write_to_file('median', brief.get_median())
            print(f'Отсутствующих учеников: {brief.get_amount_missings(processed_dict)}', file=statfile)
            dev.write_to_file('missings', brief.get_amount_missings(processed_dict))
            print(f'Учеников, давших ответы не на все вопросы: {brief.get_amount_notfilled(processed_dict)}', file=statfile)
            dev.write_to_file('notfilled', brief.get_amount_notfilled(processed_dict))
            print(file=statfile)
            print('Распределение оценок по классу:', file=statfile)
            for k, v in brief.get_counter().items():
                print(f'Оценок {k}: {v}', file=statfile)
            print(f'Больше всего оценок: {brief.get_most_common()}', file=statfile)
            dev.write_to_file('most_common', brief.get_most_common())
            print('Статистика успешно сгенерирована и записана в одноразовый файл statistics.txt')
            qst8 = Questions('Открыть файл?\n')
            dev.write_to_file('success', True)
            if qst8.make_question():
                os.startfile('statistics.txt')
                dev.write_to_file('happy_end', True)
            else:
                sys.exit()
                dev.write_to_file('happy_end', True)

        dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    else: #если доступна и та, и другая статистика
        secondary_choose_stat = input('Выберите режим статистики:\n'
                                      '1. Краткая статистика[1]\n'
                                      '2. Полная статистика по классу[2]\n'
                                      '3. Полная статистика по ученику[3]\n').lower().strip()

        dev.write_to_file('secondary_choose_stat', secondary_choose_stat)

        if secondary_choose_stat in ('1', 'краткая статистика'): #краткая статистика
            processed_data = BriefStatistics.process_file(chosen_pair[0])
            dev.write_to_file('processed_data', processed_data)
            processed_list = BriefStatistics.process_to_list(processed_data)
            dev.write_to_file('processed_list', processed_list)
            processed_dict = BriefStatistics.process_to_dict(processed_data)
            dev.write_to_file('processed_dict', processed_dict)
            brief = BriefStatistics(processed_list, processed_dict)

            with open('statistics.txt', 'w', encoding='utf-8') as statfile:  # запись статистики в файл
                filename = Path(chosen_pair[0]).stem
                klass, name_work, date = filename.split('_')
                print(f'Краткая статистика по работе "{name_work}" класса {klass} за {date}:\n', file=statfile)
                print(f'Средняя оценка по классу: {brief.get_average()}', file=statfile)
                dev.write_to_file('average', brief.get_average())
                print(f'Медианное по классу: {brief.get_median()}', file=statfile)
                dev.write_to_file('median', brief.get_median())
                print(f'Отсутствующих учеников: {brief.get_amount_missings(processed_dict)}', file=statfile)
                dev.write_to_file('missings', brief.get_amount_missings(processed_dict))
                print(f'Учеников, давших ответы не на все вопросы: {brief.get_amount_notfilled(processed_dict)}', file=statfile)
                dev.write_to_file('notfilled', brief.get_amount_notfilled(processed_dict))
                print(file=statfile)
                print('Распределение оценок по классу:', file=statfile)
                for k, v in brief.get_counter().items():
                    print(f'Оценок {k}: {v}', file=statfile)
                print(f'Больше всего оценок: {brief.get_most_common()}', file=statfile)
                dev.write_to_file('most_common', brief.get_most_common())
                print('Статистика успешно сгенерирована и записана в одноразовый файл statistics.txt')
                dev.write_to_file('success', True)
                qst8 = Questions('Открыть файл?\n')
                if qst8.make_question():
                    os.startfile('statistics.txt')
                    dev.write_to_file('happy_end', True)
                else:
                    sys.exit()
                    dev.write_to_file('happy_end', True)
            dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        elif secondary_choose_stat in ('2', 'полная статистика по классу'): #полная статистики по классу
            processed_data = DeepStatistics.process_file(chosen_pair[1])

            processed_list = DeepStatistics.process_to_list(processed_data)
            dev.write_to_file('processed_list', processed_list)
            processed_dict = DeepStatistics.process_to_dict(processed_data)
            dev.write_to_file('processed_dict', processed_dict)
            processed_distribution = DeepStatistics.process_to_distribution(processed_data)
            dev.write_to_file('processed_distribution', processed_distribution)
            processed_best_worst = DeepStatistics.procces_to_best_worst(processed_data)
            dev.write_to_file('processed_best_worst', processed_best_worst)
            processed_average_answ = DeepStatistics.process_to_average_answ(processed_data)
            dev.write_to_file('processed_average_answ', processed_average_answ)

            deep = DeepStatistics(processed_list, processed_dict)

            with open('statistics.txt', 'w', encoding='utf-8') as statfile: #запись полной статистики в файл
                filename = Path(chosen_pair[0]).stem
                klass, name_work, date = filename.split('_')
                print(f'Полная статистика по работе "{name_work}" класса {klass} за {date}:\n', file=statfile)
                print(f'Средняя оценка по классу: {deep.get_average()}', file=statfile)
                dev.write_to_file('average', deep.get_average())
                print(f'Медианное по классу: {deep.get_median()}', file=statfile)
                dev.write_to_file('median', deep.get_median())
                print(f'Среднее количество правильных ответов(подробнее см. Инструкцию): {deep.get_average_answ(processed_average_answ)}', file=statfile)
                dev.write_to_file('average_answ', deep.get_average_answ(processed_average_answ))
                print(f'Отсутствующих учеников: {deep.get_amount_missings(processed_dict)}', file=statfile)
                dev.write_to_file('missings', deep.get_amount_missings(processed_dict))
                print(f'Учеников, давших ответы не на все вопросы: {len(deep.get_amount_notfilled(processed_dict))}', file=statfile)
                dev.write_to_file('notfilled', deep.get_amount_notfilled(processed_dict))
                print(file=statfile)
                print('Распределение оценок по классу:', file=statfile)
                for k, v in deep.get_counter().items():
                    print(f'Оценок {k}: {v}', file=statfile)
                print(f'Больше всего оценок: {deep.get_most_common()}', file=statfile)
                dev.write_to_file('most_common', deep.get_most_common())
                print(file=statfile)
                print(f'Лучшие ученики по классу:', file=statfile)
                print(', '.join(deep.get_the_best_puples(processed_best_worst)), file=statfile)
                dev.write_to_file('the_best_puples', deep.get_the_best_puples(processed_best_worst))
                print(file=statfile)
                print(f'Худшие ученики по классу:', file=statfile)
                print(', '.join(deep.get_the_worst_puples(processed_best_worst)), file=statfile)
                dev.write_to_file('the_worst_puples', deep.get_the_worst_puples(processed_best_worst))
                print(file=statfile)
                stats_dict_deep_distr = deep.get_distribution(processed_distribution)
                dev.write_to_file('stats_dict_deep_distr', stats_dict_deep_distr)
                percentage_dict = deep.convert_to_percentage(stats_dict_deep_distr)
                dev.write_to_file('percentage_dict', percentage_dict)
                for num, percent in percentage_dict.items():
                    print(f'На вопрос {num} правильно ответили {percent}% учеников', file=statfile)
                print(file=statfile)

                statsrec = StatisticsRecommendations(deep.convert_to_percentage(stats_dict_deep_distr))
                print('Рекомендации по работе:', file=statfile)
                print(*statsrec.get_recommendations(), sep='\n', file=statfile)
                dev.write_to_file('recommendations', statsrec.get_recommendations())
                print(file=statfile)
                dek = deep.convert_to_percentage(stats_dict_deep_distr)
                mean_to_colcl = stat.mean(list(dek.values()))
                dev.write_to_file('mean_to_colcl', mean_to_colcl)
                print(statsrec.get_final_conclusion(mean_to_colcl), file=statfile)
                dev.write_to_file('final_conclusion', statsrec.get_final_conclusion(mean_to_colcl))

                print('Подробная статистика успешно сгенерирована и записана в одноразовый файл statistics.txt')
                dev.write_to_file('success', True)

            qst9 = Questions('Сгенерировать графики по статистике?\n')
            if qst9.make_question():
                dev.write_to_file('generate_graphs', True)
                dsg = DeepStatisticsGraphics(dek, deep.get_counter())
                print('Генерация графиков...')
                time.sleep(0.7)
                dsg.show()
                os.startfile('statistics.txt')
                print('Графики успешно сгенерированы')
                dev.write_to_file('happy_end', True)
            else:
                qst10 = Questions('Открыть файл?\n')
                if qst10.make_question():
                    dev.write_to_file('open_file', True)
                    os.startfile('statistics.txt')
                    dev.write_to_file('happy_end', True)
                else:
                    sys.exit()
                    dev.write_to_file('happy_end', True)

            dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        elif secondary_choose_stat in ('3', 'полная статистика по ученику'): #полная статистика по ученику
            name = input('Введите имя ученика(с учетом регистра): ')
            dev.write_to_file('name', name)

            processed_data = DeepStatistics.process_file(chosen_pair[1])
            pds = PupleDeepStatistics(name, processed_data)
            filename = Path(chosen_pair[0]).stem
            klass, name_work, date = filename.split('_')

            with open('statistics.txt', 'w', encoding='utf-8') as statfile: #запись в файл
                if pds.missings():
                    print(f'Ученик {name} отсутствовал', file=statfile)
                    dev.write_to_file('missings', True)
                    print(f'Статистика по ученику {name} успешно записана в одноразовый файл statistics.txt')
                    dev.write_to_file('success', True)
                else:
                    print(f'Статистика для ученика {name} по работе "{name_work}" за {date}', file=statfile)
                    print(file=statfile)
                    print(f'Оценка за работу: {pds.mark()}', file=statfile)
                    dev.write_to_file('mark', pds.mark())
                    print('Ученик дал ответы не на все задания' if not pds.not_all() else "Ученик дал ответы на все задания", file=statfile)
                    dev.write_to_file('not_all', pds.not_all())
                    print(file=statfile)
                    print('Ответы ученика:', file=statfile)
                    for num, status in enumerate(pds.response_status(), 1):
                        print(f'{num} - {status}', file=statfile)
                    dev.write_to_file('response_status', pds.response_status())
                    print(f'Всего правильных ответов: {pds.correct_answers_am()}', file=statfile)
                    dev.write_to_file('correct_answers_am', pds.correct_answers_am())
                    print(f'Статистика по ученику {name} успешно записана в одноразовый файл statistics.txt')
                    dev.write_to_file('success', True)
            dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


elif mainchoose in dct_variants['generate']:
    genchoose = input('Выберите режим генерации:\n'
          'Генерация по умолчанию(без точной настройки)[0]\n'
          'Генерация с ручной настройкой[1]\n').lower().strip()

    if genchoose in ('0', 'генерация по умолчанию'):
        name_of_work = input('Введите название работы: ')
        file_puples = input('Введите имя файла с именами учеников: ')
        count_strings = input('Введите количество необходимых полей для ответов: ')

        ch = Generator.checking_setings(file_puples, count_strings) #проверка корректности файлов
        if ch:
            print('Ошибки при введении данных:')
            for error in ch:
                print(error)
            sys.exit()
        else: #генерация файлов, см. docstrings
            g = Generator(file_puples, name_of_work)
            g.generate_dir_students()
            g.generate_file_students()
            g.fill_files_students(int(count_strings))
            g.create_answers_file(int(count_strings))
            g.create_marks_file()
            g.create_missings_file()


        print(f'Генерация файлов прошла успешно. Создана папка {name_of_work} с файлами учеников, файлы marks.txt, missings.txt и answers.txt с шаблонами.')

    elif genchoose in ('1', 'генерация с ручной настройкой'):
        print('Вы находитесь в режиме ручной настройки генерации. ')

        settings = SettingsGeneration()
        results = settings.run_survey() #запуск выбора настроек

        print('Настройки сохранены. Дождитесь завершения генерации.')

        #генерация файлов и папок по настройкам
        manset = Generator(name_work=results['name_of_work'], puples_file=results['pupe_file'])
        manset.generate_dir_students()
        manset.generate_file_students()
        manset.fill_files_students(results['count_strings_pup'])
        manset.create_answers_file(results['template_lines'], results['answers_file'])
        manset.create_marks_file(results['criteria_file'], results['grading_scale'])
        manset.create_missings_file(results['absentees_file'])

        print('Генерация прошла успешно.')


elif mainchoose in dct_variants['performance']:
    #режим случайно вызывает учеников либо по номерам, либо по именно через while
    print('Это режим, который вызывает учеников к доске в случайном порядке. ("stop" для остановки цикла) Подробнее см. инструкцию')
    user_input = input("Введите файл, число, или пропустите ввод: ")
    dev.write_to_file('user_input', user_input)
    iterable = RandomCall.process_input(user_input)

    if not iterable:
        print("Введённое значение не является числом или путём к файлу, или файл не существует")
        dev.write_to_file('error_input', True)
    else:
        ind = 0
        items = list(iterable)
        dev.write_to_file('items', items)
        random.shuffle(items)

        print(f'Ученик {items[ind]} идет первый:( ', end='')
        inputting = input().lower().strip()

        while inputting != 'stop':
            if ind == len(items) - 1:
                print('Вы всех спросили!')
                dev.write_to_file('happy_end', True)
                sys.exit()
            ind += 1
            print(f'Ученик {items[ind]} идет к доске ', end='')
            inputting = input().lower().strip()
            dev.write_to_file(f'inputting{ind}', inputting)
    dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


elif mainchoose in dct_variants['clear']:
    clearchoose = input('Выберите режим для сброса:\n'
                        'Сброс файлов[0]\n'
                        'Сброс файлов и папок[1]\n'
                        'Сброс до начальной конфигурации[2]\n').lower().strip()
    dev.write_to_file('clearchoose', clearchoose)


    with open('sys.json', 'r', encoding='utf-8') as f: #получение данных по умолчанию из sys.json
        smdct = json.load(f)
        files_to_delete_custom = {Path(smdct['answer']), Path(smdct['marks']), Path(smdct['missings'])}
    lst_of_files = ['answers.txt', 'marks.txt', 'missings.txt', 'sys.json', 'syslog.json']
    mapped_list_of_files = list(map(lambda x: Path(os.path.join(os.getcwd(), x)), lst_of_files))
    files_to_delete_default = set(mapped_list_of_files)
    files_to_delete = files_to_delete_default.union(files_to_delete_custom) #объединение множеств файлов по умолчанию и пользовательских


    if clearchoose in ('0', 'сброс файлов'):
        #несколько проверок на миссклик
        qst_sure = Questions('Вы уверены, что хотите удалить файлы? (если вы понятия не имеете, какие файлы будут удалены, рекомендуется прочесть инструкцию)\n')
        if qst_sure.make_question():
            sure2 = input('Для проверки на миссклик, введите любое натуральное число\n')
            if sure2.isdigit() and len(sure2) >= 2:
                dev.write_to_file('correct_check', True)
                delete = DeleteManager(files_to_delete)
                delete.delete_files() #удаление файлов
                dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            else:
                print('Проверка для удаления необходима, так что перезапустите режим, если все еще хотите удалить файлы')
                dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


    elif clearchoose in ('1', 'сброс файлов и папок'):
        #несколько проверок на миссклик и файл с паролем
        qst_sure = Questions('Вы уверены, что хотите сбросить файлы и папку archive? (если вы понятия не имеете, какие файлы будут удалены, рекомендуется прочесть инструкцию)\n')
        if qst_sure.make_question():
            dev.write_to_file('sure', True)
            right_psw = DeleteManager.create_file_delete()
            dev.write_to_file('right_psw', right_psw)
            print('Для проверки на миссклик программа создала в рабочей директории файл delete.txt с паролем для удаления. Пожалуйста, введите его.')
            user_psw = input('Введите пароль из файла\n').strip()
            dev.write_to_file('user_psw', user_psw)
            if user_psw == str(right_psw):
                files_to_delete.add('delete.txt') #добавление файла для удаления в множество
                files_to_delete.add(os.path.join(os.getcwd(), 'archive')) #добавление папки для удаления в множество
                delete = DeleteManager(files_to_delete)
                delete.delete_files_and_folders() #удаление файлов и папок
                print('Файлы и папка arhcive были удалены.')
                sys.exit()
            else:
                print('Неверный пароль. Попробуйте снова, если все еще хотите удалить файлы')
                dev.write_to_file('wrong_psw', True)
                dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                sys.exit()


    elif clearchoose in ('2', 'сброс до начальной конфигурации'):
        if not debug:
            #проверка прав доступа, режим доступен только в режиме разработчика
            print('У вас недостаточно прав для совершения этого действия. (подробнее см. инструкцию)')
            dev.write_to_file('rules_error', True)
        if debug:
            #проверка на миссклик, пароль и обратный отсчет для безопасности
            dev.write_to_file('password', random.randint(10000, 99999))
            with open('syslog.json', 'r', encoding='utf-8') as logfile:
                logdctdel = json.load(logfile)
                right_psw = logdctdel['password']
                user_psw = input('Введите пароль\n').strip()
                dev.write_to_file('user_psw', user_psw)
                if user_psw == str(right_psw):
                    dev.write_to_file('correct_psw', True)
                    for i in reversed(list(range(1, 6))):
                        print(f'Удаление всех файлов и папок рабочей директории через {i}')
                        time.sleep(1)
                    dev.write_to_file('au revour', True)
                    dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    DeleteManager.deep_delete() #удаление всего в рабочей директории, кроме py-файлов


elif mainchoose in dct_variants['compare']:

    print('Вы в режиме сравнения работ. Выберите папку, работы из которой хотите сравнить')
    dct_stat_chose = {}
    for index, dir in enumerate(os.listdir('archive'), 1):
        print(f'{dir}[{index}]')
        filepathrem = os.path.join(os.getcwd(), 'archive', dir)
        dct_stat_chose[index] = filepathrem
    chose_comp = input('Введите номер папки, по которой хотите получить статистику:\n')
    dev.write_to_file('chose_comp', chose_comp)
    try:
        chosen_comp = int(chose_comp)
    except Exception:
        print('Введите номер папки')
        dev.write_to_file('error_input', True)
        sys.exit()
    try:
        chosen_dir_comp = dct_stat_chose[chosen_comp]
    except KeyError:
        print('Нет папки с таким номером')
        dev.write_to_file('error_input', True)
        sys.exit()

    if not any(os.path.isfile(os.path.join(chosen_dir_comp, x)) for x in os.listdir(chosen_dir_comp)):
        print('Папка пуста')  # проверка на пустоту папки
        dev.write_to_file('empty_dir', True)
        sys.exit()

    statcomp = BriefStatistics(chosen_dir_comp)
    statcomp.set_pairs(chosen_dir_comp)
    dev.write_to_file('pairs', statcomp.pairs)
    comp = Compare(chosen_dir_comp)
    comp.filter_files(statcomp.pairs)
    dev.write_to_file('filtered_files', comp.filtered_files)

    method_to_comp = input('Сравнить работы:\n'
                           'по классу [1]\n'
                           'по конкретному ученику[2]\n').strip()
    dev.write_to_file('method_to_comp', method_to_comp)

    choose_method_to_comp = input('Как хотите получить статистику?\n'
                                  'по конкрентым работам[1]\n'
                                  'за период[2]\n').strip()
    dev.write_to_file('choose_method_to_comp', choose_method_to_comp)

    res = method_to_comp + choose_method_to_comp
    dev.write_to_file('res', res)

    dct_of_methods = {
        '11': lambda: 'classsplit',
        '12': lambda: 'classperiod',
        '21': lambda: 'studentsplit',
        '22': lambda: 'studentperiod'
    }

    try:
        res_choose = dct_of_methods[res]()
        dev.write_to_file('res_choose', res_choose)
    except KeyError:
        print('Неверный режим')
        dev.write_to_file('error_method', True)
        sys.exit()

    if res_choose == 'classsplit':
        compdct = {}
        for index, compfile in enumerate(comp.filtered_files, 1):
            print(f'{Path(compfile[0]).stem}[{index}]')
            compdct[index] = compfile

        files = input('Введите номера файлов:\n').strip()
        if files == 'all' or files == 'все':
            files = ' '.join(list(map(str, compdct.keys())))
            dev.write_to_file('all_files', True)
        comp.split_chosen(files, compdct)
        if len(comp.json_files_not_rep) < 2:
            print("Для сравнения требуется как минимум две работы.")
            dev.write_to_file('error_less_two', True)
            sys.exit()

        json_files = comp.json_files_not_rep
        dict_to_graph_distr, dict_to_graph_avrg, dict_to_graph_miss, dict_to_graph_avrg_answ = Compare.compare_works(json_files)
        dev.write_to_file('dict_to_graph_distr', dict_to_graph_distr)
        dev.write_to_file('dict_to_graph_avrg', dict_to_graph_avrg)
        dev.write_to_file('dict_to_graph_miss', dict_to_graph_miss)
        dev.write_to_file('dict_to_graph_avrg_answ', dict_to_graph_avrg_answ)
        compare_graph = CompareGraphs(dict_to_graph_distr, dict_to_graph_avrg, dict_to_graph_miss, dict_to_graph_avrg_answ)
        print('Генерация графиков...')
        time.sleep(0.7)
        compare_graph.show()
        dev.write_to_file('happy_end', True)
        print('Графики успешно сгенерированы')
        dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    elif res_choose == 'classperiod':
        period = input('Введите период, по которому хотите сравнить работы в одном из допустимых форматов(см. инструкцию)\n').strip()
        dev.write_to_file('period', period)
        per = Periods()
        per.period = period
        filtered_by_date = per.filtered_by_date(comp.filtered_files)
        dev.write_to_file('filtered_by_date', filtered_by_date)
        sorted_by_date = per.sorted_by_date(filtered_by_date)
        dev.write_to_file('sorted_by_date', sorted_by_date)
        if len(sorted_by_date) < 2:
            print("В введеном вами периоде одна или ни одной работы. Для сравнения требуется как минимум две работы")
            dev.write_to_file('error_less_two', True)
            sys.exit()
        print('В введеном периоде найдены следующие работы:')
        for work in sorted_by_date:
            print(Path(work).stem[8:])
        dict_to_graph_distr, dict_to_graph_avrg, dict_to_graph_miss, dict_to_graph_avrg_answ = comp.compare_works(sorted_by_date)
        dev.write_to_file('dict_to_graph_distr', dict_to_graph_distr)
        dev.write_to_file('dict_to_graph_avrg', dict_to_graph_avrg)
        dev.write_to_file('dict_to_graph_miss', dict_to_graph_miss)
        dev.write_to_file('dict_to_graph_avrg_answ', dict_to_graph_avrg_answ)
        comp_graph = CompareGraphs(dict_to_graph_distr, dict_to_graph_avrg, dict_to_graph_miss, dict_to_graph_avrg_answ)
        print('Генерация графиков...')
        time.sleep(0.7)
        comp_graph.show()
        dev.write_to_file('happy_end', True)
        print('Графики успешно сгенерированы')
        dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    elif res_choose == 'studentsplit':
        name = input('Введите имя ученика:\n').strip()
        dev.write_to_file('name', name)
        compdct = {}
        for index, compfile in enumerate(comp.filtered_files, 1):
            print(f'{compfile[0]}[{index}]')
            compdct[index] = compfile
        files = input('Введите номера файлов:\n').strip()
        dev.write_to_file('files', files)
        if files == 'all' or files == 'все':
            files = ' '.join(list(map(str, compdct.keys())))

        comp.split_chosen(files, compdct)

        if len(comp.json_files_not_rep) < 2:
            print("Для сравнения требуется как минимум две работы.")
            dev.write_to_file('error_less_two', True)
            sys.exit()

        dict_pup_mark_graph, dict_pup_answ_graph = comp.compare_works_pup(comp.json_files_not_rep, name)
        dev.write_to_file('dict_pup_mark_graph', dict_pup_mark_graph)
        dev.write_to_file('dict_pup_answ_graph', dict_pup_answ_graph)
        pup_graph = ComparePupleGraphs(dict_pup_answ_graph, dict_pup_mark_graph)
        print('Генерация графиков...')
        time.sleep(0.7)
        pup_graph.show()
        dev.write_to_file('happy_end', True)
        print('Графики успешно сгенерированы')
        dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    elif res_choose == 'studentperiod':
        period = input('Введите период, по которому хотите сравнить работы в одном из допустимых форматов(см. инструкцию)\n').strip()
        dev.write_to_file('period', period)
        name = input('Введите имя ученика: ').strip()
        dev.write_to_file('name', name)
        per = Periods()
        per.period = period
        filtered_by_date = per.filtered_by_date(comp.filtered_files)
        dev.write_to_file('filtered_by_date', filtered_by_date)
        sorted_by_date = per.sorted_by_date(filtered_by_date)
        dev.write_to_file('sorted_by_date', sorted_by_date)
        if len(sorted_by_date) < 2:
            print("В введеном вами периоде одна или ни одной работы. Для сравнения требуется как минимум две работы.")
            dev.write_to_file('error_less_two', True)
            sys.exit()
        print('В введеном периоде найдены следующие работы:')
        for work in sorted_by_date:
            print(Path(work).stem[8:])

        dict_pup_mark_graph, dict_pup_answ_graph = comp.compare_works_pup(sorted_by_date, name)
        dev.write_to_file('dict_pup_mark_graph', dict_pup_mark_graph)
        dev.write_to_file('dict_pup_answ_graph', dict_pup_answ_graph)
        pup_graph = ComparePupleGraphs(dict_pup_answ_graph, dict_pup_mark_graph)
        print('Генерация графиков...')
        time.sleep(0.7)
        pup_graph.show()
        dev.write_to_file('happy_end', True)
        print('Графики успешно сгенерированы')
        dev.write_to_file('datetime_end', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


elif mainchoose in dct_variants['help']:
    print('Инструкция:')