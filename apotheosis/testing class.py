



from statonly import *
import statistics as stat
from mathplotlib import *
from datetime import datetime
import re

class DateValidator:
    def __init__(self):
        self._month_periods = {
            1: ("01.01", "31.01"),
            2: ("01.02", "28.02"),
            3: ("01.03", "31.03"),
            4: ("01.04", "30.04"),
            5: ("01.05", "31.05"),
            6: ("01.06", "30.06"),
            7: ("01.07", "31.07"),
            8: ("01.08", "31.08"),
            9: ("01.09", "30.09"),
            10: ("01.10", "31.10"),
            11: ("01.11", "30.11"),
            12: ("01.12", "31.12")
        }

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        current_year = datetime.now().year
        regex_period = r'^\d{2}\.\d{2}\.\d{4} - \d{2}\.\d{2}\.\d{4}$'
        regex_month = r'^(1[0-2]|0?[1-9])$'
        regex_month_range = r'^(1[0-2]|0?[1-9])-(1[0-2]|0?[1-9])$'

        if not (
            re.fullmatch(regex_period, value) or
            re.fullmatch(regex_month, value) or
            re.fullmatch(regex_month_range, value)
        ):
            print('Дата не соответствует формату дд.мм.гггг - дд.мм.гггг, номеру месяца или диапазону месяцев')
            sys.exit()

        # Если это диапазон дат
        if re.fullmatch(regex_period, value):
            try:
                start_date_str, end_date_str = value.split(" - ")
                start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
                end_date = datetime.strptime(end_date_str, '%d.%m.%Y')

                if start_date > end_date:
                    print('Дата начала должна быть раньше даты конца')
                    sys.exit()
                instance.__dict__[self.name] = (start_date, end_date)
                return
            except Exception:
                print(f'Некорректная дата')
                sys.exit()

        # Если это месяц
        elif re.fullmatch(regex_month, value):
            month = int(value)
            start_str, end_str = self._month_periods[month]
            try:
                start_date = datetime.strptime(f"{start_str}.{current_year}", "%d.%m.%Y")
                end_date = datetime.strptime(f"{end_str}.{current_year}", "%d.%m.%Y")
                instance.__dict__[self.name] = (start_date, end_date)
                return
            except ValueError:
                print(f"Ошибка при парсинге даты")
                sys.exit()

        # Если это диапазон месяцев
        elif re.fullmatch(regex_month_range, value):
            start_month_str, end_month_str = value.split('-')
            start_month = int(start_month_str)
            end_month = int(end_month_str)

            if not (1 <= start_month <= 12 and 1 <= end_month <= 12):
                print('Месяцы должны быть в диапазоне от 1 до 12')
                sys.exit()

            if start_month > end_month:
                print('Начальный месяц должен быть меньше или равен конечному')
                sys.exit()

            start_str, end_str = self._month_periods[start_month]
            start_date = datetime.strptime(f"{start_str}.{current_year}", "%d.%m.%Y")

            end_str_last, end_str_last_day = self._month_periods[end_month]
            end_date = datetime.strptime(f"{end_str_last_day}.{current_year}", "%d.%m.%Y")

            instance.__dict__[self.name] = (start_date, end_date)
            return

        else:
            print('Неизвестный формат даты')
            sys.exit()




class Periods:
    period = DateValidator()

    def filtered_by_date(self, filtered_files):
        start_date, end_date = self.period
        list_filtered_by_date = []
        for _, json in filtered_files:
            jsonname = Path(json).name
            jsonname = jsonname.replace('.json', '')
            _, klass, namework, date = jsonname.split('_')
            date = datetime.strptime(date, '%d.%m.%Y')
            if start_date <= date <= end_date:
                 list_filtered_by_date.append(json)
        return list_filtered_by_date

    @staticmethod
    def sorted_by_date(list_filtered_by_date):
        def key_func(x):
            x = Path(x).name
            x = x.replace('.json', '')
            _, klass, namework, date = x.split('_')
            date = datetime.strptime(date, '%d.%m.%Y')
            return date

        return sorted(list_filtered_by_date, key=key_func)



class Compare:
    def __init__(self, chosen_dir):
        self.chosen_dir = chosen_dir
        self.filtered_files = []
        self.json_files_not_rep = set()

    def filter_files(self, pairs):
        for pair in pairs:
            if pair[1] is not None:
                pair = (os.path.join(self.chosen_dir, pair[0]), os.path.join(self.chosen_dir, pair[1]))
                self.filtered_files.append(pair)

    def split_chosen(self, files_str, compdct):
        for num in files_str.split():
            try:
                num = int(num)
            except:
                print('Некорректный ввод, введите только числа')
                sys.exit()

            try:
                json = compdct[num][1]
                self.json_files_not_rep.add(json)
            except KeyError:
                print('Некорректный ввод, вы ввели номер несуществующего файла')
                sys.exit()

    @staticmethod
    def compare_works(json_files):
        dict_to_graph_distr = {}
        dict_to_graph_avrg = {}
        dict_to_graph_miss = {}
        dict_to_graph_avrg_answ = {}

        for json in json_files:
            processed_data = DeepStatistics.process_file(json)
            processed_dict = DeepStatistics.process_to_dict(processed_data)
            processed_list = DeepStatistics.process_to_list(processed_data)
            processed_avrg_answers = DeepStatistics.process_to_average_answ(processed_data)
            processed_distribution = DeepStatistics.process_to_distribution(processed_data)
            distribution = DeepStatistics.get_distribution(processed_distribution)
            percentage_to_graph = DeepStatistics.convert_to_percentage(distribution)

            json = Path(json).name
            json = json.replace('.json', '')
            _, klass, namework, date = json.split('_')
            good_name = f'{namework.capitalize().strip()} {date.strip()}'

            dict_to_graph_distr[good_name] = round(stat.mean(percentage_to_graph.values()))
            deep = DeepStatistics(lst_marks=processed_list)
            dict_to_graph_avrg[good_name] = deep.get_average()
            am_miss = deep.get_amount_missings(processed_dict)
            dict_to_graph_miss[good_name] = am_miss
            avrg_answ = DeepStatistics.get_average_answ(processed_avrg_answers)
            dict_to_graph_avrg_answ[good_name] = round(avrg_answ, 1)

        return dict_to_graph_distr, dict_to_graph_avrg, dict_to_graph_miss, dict_to_graph_avrg_answ

    @staticmethod
    def compare_works_pup(json_files, name):
        compare_pup_dict_mark = {}
        compare_pup_dict_answ = {}

        for json in json_files:
            processed_data = DeepStatistics.process_file(json)
            pupstats = PupleDeepStatistics(name, processed_data)
            mark = pupstats.mark()
            amount_cor_answ = pupstats.correct_answers_am()

            json = Path(json).name
            json = json.replace('.json', '')
            _, klass, namework, date = json.split('_')
            good_name = f'{namework.capitalize().strip()} {date.strip()}'

            compare_pup_dict_mark[good_name] = mark
            compare_pup_dict_answ[good_name] = amount_cor_answ

        return compare_pup_dict_mark, compare_pup_dict_answ

chosen_dir = r'D:\pythonProject\apotheosis\archive\8в'
statcomp = BriefStatistics(chosen_dir)
statcomp.set_pairs(chosen_dir)
print(*statcomp.pairs, sep='\n')
print()
comp = Compare(chosen_dir)
comp.filter_files(statcomp.pairs)

method_to_comp = input('Сравнить работы:\n'
                        'по классу [1]\n'
                        'по конкретному ученику[2]\n').strip()

choose_method_to_comp  = input('Как хотите получить статистику?\n'
                                'по конкрентым работам[1]\n'
                                'за период[2]\n').strip()

res = method_to_comp+choose_method_to_comp

dct_of_methods = {
    '11': lambda: 'classsplit',
    '12': lambda: 'classperiod',
    '21': lambda: 'studentsplit',
    '22': lambda: 'studentperiod'
}

res_choose = dct_of_methods[res]()
if res_choose == 'classsplit':
    compdct = {}
    for index, compfile in enumerate(comp.filtered_files, 1):
        print(f'{compfile[0]}[{index}]')
        compdct[index] = compfile
    print()
    print(compdct)
    files = input('Введите номера файлов: ').strip()
    if files == 'all' or files == 'все':
        files = ' '.join(list(map(str, compdct.keys())))
    comp.split_chosen(files, compdct)
    if len(comp.json_files_not_rep) < 2:
        print("Для сравнения требуется как минимум две работы.")
        sys.exit()

    print(*comp.json_files_not_rep, sep='\n')

    json_files = comp.json_files_not_rep

    dict_to_graph_distr, dict_to_graph_avrg, dict_to_graph_miss, dict_to_graph_avrg_answ = Compare.compare_works(json_files)

    compare_graph = CompareGraphs(dict_to_graph_distr, dict_to_graph_avrg, dict_to_graph_miss, dict_to_graph_avrg_answ)
    compare_graph.show()


elif res_choose == 'classperiod':
    period = input('Введите период, по которому хотите сравнить работы в формате: дд.мм.гггг - дд.мм.гггг\n').strip()
    per = Periods()
    per.period = period
    filtered_by_date = per.filtered_by_date(comp.filtered_files)
    sorted_by_date = per.sorted_by_date(filtered_by_date)
    if len(sorted_by_date) < 2:
        print("В введеном вами периоде одна или ни одной работы. Для сравнения требуется как минимум две работы.")
        sys.exit()
    print(*sorted_by_date, sep='\n') #написать, что будут проверны такие то работы и вывести .stem через цикл
    dict_to_graph_distr, dict_to_graph_avrg, dict_to_graph_miss, dict_to_graph_avrg_answ = comp.compare_works(sorted_by_date)
    comp_graph = CompareGraphs(dict_to_graph_distr, dict_to_graph_avrg, dict_to_graph_miss, dict_to_graph_avrg_answ)
    comp_graph.show()


elif res_choose == 'studentsplit':
    name = input('Введите имя ученика: ').strip()
    compdct = {}
    for index, compfile in enumerate(comp.filtered_files, 1):
        print(f'{compfile[0]}[{index}]')
        compdct[index] = compfile
    print()
    print(compdct)
    files = input('Введите номера файлов: ').strip()
    if files == 'all' or files == 'все':
        files = ' '.join(list(map(str, compdct.keys())))
    comp.split_chosen(files, compdct)
    if len(comp.json_files_not_rep) < 2:
        print("Для сравнения требуется как минимум две работы.")
        sys.exit()
    print(*comp.json_files_not_rep, sep='\n')
    print(name)

    dict_pup_mark_graph, dict_pup_answ_graph = comp.compare_works_pup(comp.json_files_not_rep, name)
    print(dict_pup_answ_graph, dict_pup_mark_graph)

    pup_graph = ComparePupleGraphs(dict_pup_answ_graph, dict_pup_mark_graph)
    pup_graph.show()


elif res_choose == 'studentperiod':
    period = input('Введите период, по которому хотите сравнить работы в формате: дд.мм.гггг - дд.мм.гггг\n').strip()
    name = input('Введите имя ученика: ').strip()
    per = Periods()
    per.period = period
    filtered_by_date = per.filtered_by_date(comp.filtered_files)
    sorted_by_date = per.sorted_by_date(filtered_by_date)
    if len(sorted_by_date) < 2:
        print("В введеном вами периоде одна или ни одной работы. Для сравнения требуется как минимум две работы.")
        sys.exit()
    print(*sorted_by_date, sep='\n')
    print(name)

    dict_pup_mark_graph, dict_pup_answ_graph = comp.compare_works_pup(sorted_by_date, name)
    print(dict_pup_answ_graph, dict_pup_mark_graph)

    pup_graph = ComparePupleGraphs(dict_pup_answ_graph, dict_pup_mark_graph)
    pup_graph.show()







