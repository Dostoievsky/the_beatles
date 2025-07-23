from datetime import datetime
import re
from .CONFIG_classes_statistics import  *
from matplotlib.ticker import MaxNLocator

class DateValidator:
    """
    Дескриптор для валидации даты или диапазона дат.
    Поддерживает форматы:
    - Диапазон дат: "дд.мм.гггг - дд.мм.гггг"
    - Номер месяца: "01"–"12"
    - Диапазон месяцев: "01-03", "05-12"
    """

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
        """
        Сохраняет имя атрибута, к которому привязан дескриптор.
        """
        self.name = name

    def __get__(self, instance, owner):
        """
        Возвращает значение атрибута из словаря экземпляра.
        """
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        """
        Проверяет и устанавливает значение даты/диапазона дат.
        Выполняет валидацию формата и корректности даты.
        """
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
    """
    Класс для фильтрации и сортировки файлов по дате.
    Использует валидатор даты `DateValidator` для установки диапазона дат.
    """

    period = DateValidator()

    def filtered_by_date(self, filtered_files):
        """
        Фильтрует список файлов, оставляя только те, которые попадают в указанный период.
        """
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
        """
        Сортирует отфильтрованные файлы по дате (по возрастанию).
        """
        def key_func(x):
            x = Path(x).name
            x = x.replace('.json', '')
            _, klass, namework, date = x.split('_')
            date = datetime.strptime(date, '%d.%m.%Y')
            return date

        return sorted(list_filtered_by_date, key=key_func)


class Compare:
    """
    Класс для сравнения нескольких работ.
    Позволяет фильтровать файлы, выбирать нужные работы и сравнивать их по различным метрикам (средние оценки, процент правильных ответов, количество отсутствующих и т.д.).
    """

    def __init__(self, chosen_dir):
        self.chosen_dir = chosen_dir
        self.filtered_files = []
        self.json_files_not_rep = set()

    def filter_files(self, pairs):
        """
        Фильтрует пары файлов, оставляя только те, у которых есть JSON-файл.
        """
        for pair in pairs:
            if pair[1] is not None:
                pair = (os.path.join(self.chosen_dir, pair[0]), os.path.join(self.chosen_dir, pair[1]))
                self.filtered_files.append(pair)

    def split_chosen(self, files_str, compdct):
        """
        Обрабатывает введённые номера файлов и добавляет соответствующие JSON-файлы в множество.
        """
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
        """
        Сравнивает несколько работ и формирует данные для графиков:
        - Средний процент правильных ответов.
        - Средние оценки.
        - Количество отсутствующих учеников.
        - Среднее количество правильных ответов.
        """
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
        """
        Сравнивает результаты конкретного ученика по нескольким работам.
        Возвращает средние оценки и количество правильных ответов.
        """
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


class CompareGraphs:
    """
    Визуализирует результаты сравнения нескольких работ в виде графиков.
    Отображает 4 графика:
    - Средний процент правильных ответов
    - Средняя оценка по классу
    - Количество отсутствующих учеников
    - Среднее количество правильных ответов
    """

    def __init__(self, dict_to_graph_distr, dict_to_graph_avrg, dict_to_graph_miss, dict_to_graph_avrg_answ):
        self.dict_to_graph_distr = dict_to_graph_distr
        self.dict_to_graph_avrg = dict_to_graph_avrg
        self.dict_to_graph_miss = dict_to_graph_miss
        self.dict_to_graph_avrg_answ = dict_to_graph_avrg_answ

    def show(self):
        """
        Отображает все графики в отдельных окнах.
        """
        # Первый график: Средний процент правильных ответов
        fig1, ax1 = plt.subplots()
        dict_to_graph_distr_keys = list(self.dict_to_graph_distr.keys())
        dict_to_graph_distr_values = list(self.dict_to_graph_distr.values())
        ax1.plot(dict_to_graph_distr_keys, dict_to_graph_distr_values, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
        ax1.set_ylabel('Средний процент правильных ответов')
        ax1.set_ylim(0, 100)
        ax1.set_xticks(range(len(dict_to_graph_distr_keys)))
        ax1.set_xticklabels(dict_to_graph_distr_keys, rotation=60, ha='right', fontsize=10)
        ax1.set_title('Средний процент правильных ответов')

        # Второй график: Средняя оценка по классу
        fig2, ax2 = plt.subplots()
        dict_to_graph_avrg_keys = list(self.dict_to_graph_avrg.keys())
        dict_to_graph_avrg_values = list(self.dict_to_graph_avrg.values())
        ax2.plot(dict_to_graph_avrg_keys, dict_to_graph_avrg_values, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
        ax2.set_ylabel('Средняя оценка по классу')
        ax2.set_ylim(0, 5)
        ax2.set_xticks(range(len(dict_to_graph_avrg_keys)))
        ax2.set_xticklabels(dict_to_graph_avrg_keys, rotation=60, ha='right', fontsize=10)
        ax2.set_title('Средняя оценка по классу')

        # Третий график: Количество отсутствующих учеников
        fig3, ax3 = plt.subplots()
        dict_to_graph_miss_keys = list(self.dict_to_graph_miss.keys())
        dict_to_graph_miss_values = list(self.dict_to_graph_miss.values())
        ax3.plot(dict_to_graph_miss_keys, dict_to_graph_miss_values, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
        ax3.set_ylabel('Количество отсутствующих учеников')
        ax3.set_xticks(range(len(dict_to_graph_miss_keys)))
        ax3.set_xticklabels(dict_to_graph_miss_keys, rotation=60, ha='right', fontsize=10)
        ax3.set_title('Количество отсутствующих учеников')
        ax3.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Четвёртый график: Среднее количество правильных ответов
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


class ComparePupleGraphs:
    """
    Визуализирует результаты ученика по нескольким работам.
    Отображает два графика:
    - Количество правильных ответов
    - Оценки за работы
    """

    def __init__(self, dict_pup_answ, dict_pup_mark):
        self.dict_pup_answ = dict_pup_answ  # Словарь: {название_работы: количество_правильных_ответов}
        self.dict_pup_mark = dict_pup_mark    # Словарь: {название_работы: оценка}

    def show(self):
        """
        Отображает два графика в одной фигуре:
        1. Количество правильных ответов по каждой работе.
        2. Оценки ученика по каждой работе.
        """
        # Создаем фигуру с 2 подграфиками (1 строка, 2 столбца)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Первый график: среднее количество правильных ответов
        keys_answ = list(self.dict_pup_answ.keys())
        values_answ = list(self.dict_pup_answ.values())

        ax1.plot(keys_answ, values_answ, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
        ax1.set_ylabel('Количество правильных ответов')
        ax1.set_xticks(range(len(keys_answ)))
        ax1.set_xticklabels(keys_answ, rotation=60, ha='right', fontsize=10)
        ax1.set_title('Количество правильных ответов')
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Второй график: средняя оценка
        keys_mark = list(self.dict_pup_mark.keys())
        values_mark = list(self.dict_pup_mark.values())

        ax2.plot(keys_mark, values_mark, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
        ax2.set_ylabel('Оценка за каждую работу')
        ax2.set_xticks(range(len(keys_mark)))
        ax2.set_xticklabels(keys_mark, rotation=60, ha='right', fontsize=10)
        ax2.set_title('Оценка за каждую работу')
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Показываем графики
        plt.tight_layout()
        plt.show()