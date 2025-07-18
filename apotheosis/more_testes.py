import re
from datetime import datetime
from pathlib import Path
import sys
import matplotlib.pyplot as plt


class CompareGraphs:
    def __init__(self, dict_to_graph_distr, dict_to_graph_avrg, dict_to_graph_miss, dict_to_graph_avrg_answ):
        self.dict_to_graph_distr = dict_to_graph_distr
        self.dict_to_graph_avrg = dict_to_graph_avrg
        self.dict_to_graph_miss = dict_to_graph_miss
        self.dict_to_graph_avrg_answ = dict_to_graph_avrg_answ

    def show(self):
        # Первый график
        fig1, ax1 = plt.subplots()
        dict_to_graph_distr_keys = list(self.dict_to_graph_distr.keys())
        dict_to_graph_distr_values = list(self.dict_to_graph_distr.values())
        ax1.plot(dict_to_graph_distr_keys, dict_to_graph_distr_values, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
        ax1.set_ylabel('Средний процент правильных ответов')
        ax1.set_ylim(0, 100)
        ax1.set_xticks(range(len(dict_to_graph_distr_keys)))
        ax1.set_xticklabels(dict_to_graph_distr_keys, rotation=60, ha='right', fontsize=10)
        ax1.set_title('Средний процент правильных ответов')

        # Второй график
        fig2, ax2 = plt.subplots()
        dict_to_graph_avrg_keys = list(self.dict_to_graph_avrg.keys())
        dict_to_graph_avrg_values = list(self.dict_to_graph_avrg.values())
        ax2.plot(dict_to_graph_avrg_keys, dict_to_graph_avrg_values, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
        ax2.set_ylabel('Средняя оценка по классу')
        ax2.set_ylim(0, 5)
        ax2.set_xticks(range(len(dict_to_graph_avrg_keys)))
        ax2.set_xticklabels(dict_to_graph_avrg_keys, rotation=60, ha='right', fontsize=10)
        ax2.set_title('Средняя оценка по классу')

        # Третий график
        fig3, ax3 = plt.subplots()
        dict_to_graph_miss_keys = list(self.dict_to_graph_miss.keys())
        dict_to_graph_miss_values = list(self.dict_to_graph_miss.values())
        ax3.plot(dict_to_graph_miss_keys, dict_to_graph_miss_values, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
        ax3.set_ylabel('Количество отсутствующих учеников')
        ax3.set_xticks(range(len(dict_to_graph_miss_keys)))
        ax3.set_xticklabels(dict_to_graph_miss_keys, rotation=60, ha='right', fontsize=10)
        ax3.set_title('Количество отсутствующих учеников')

        # Четвёртый график
        fig4, ax4 = plt.subplots()
        dict_to_graph_avrg_answ_keys = list(self.dict_to_graph_avrg_answ.keys())
        dict_to_graph_avrg_answ_values = list(self.dict_to_graph_avrg_answ.values())
        ax4.plot(dict_to_graph_avrg_answ_keys, dict_to_graph_avrg_answ_values, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
        ax4.set_ylabel('Среднее количество правильных ответов')
        ax4.set_xticks(range(len(dict_to_graph_avrg_answ_keys)))
        ax4.set_xticklabels(dict_to_graph_avrg_answ_keys, rotation=60, ha='right', fontsize=10)
        ax4.set_title('Среднее количество правильных ответов')

        # Показ всех окон
        plt.show()



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

period = input('Введите период, по которому хотите сравнить работы в формате: дд.мм.гггг - дд.мм.гггг\n').strip()
per = Periods()
per.period = period
filtered = per.filtered_by_date([('D:\\pythonProject\\apotheosis\\archive\\8в\\8в_великая работа 7_16.07.2025.txt', 'D:\\pythonProject\\apotheosis\\archive\\8в\\sysfile_8в_великая работа 7_16.07.2025.json'), ('D:\\pythonProject\\apotheosis\\archive\\8в\\8в_катожная работа 3_06.07.2025.txt', 'D:\\pythonProject\\apotheosis\\archive\\8в\\sysfile_8в_катожная работа 3_06.07.2025.json'), ('D:\\pythonProject\\apotheosis\\archive\\8в\\8в_паршивая работа 4_09.09.2025.txt', 'D:\\pythonProject\\apotheosis\\archive\\8в\\sysfile_8в_паршивая работа 4_09.09.2025.json'), ('D:\\pythonProject\\apotheosis\\archive\\8в\\8в_паршивая работа 4_17.07.2025.txt', 'D:\\pythonProject\\apotheosis\\archive\\8в\\sysfile_8в_паршивая работа 4_17.07.2025.json'), ('D:\\pythonProject\\apotheosis\\archive\\8в\\8в_тканая работа 2_18.09.2025.csv', 'D:\\pythonProject\\apotheosis\\archive\\8в\\sysfile_8в_тканая работа 2_18.09.2025.json')])
print(filtered)
sorted_by_date = per.sorted_by_date(filtered)
print(sorted_by_date)
