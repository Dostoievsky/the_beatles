import os
import statistics as stat
from abc import ABC, abstractmethod
from pathlib import Path
from .CONFIG_classes_others import *
import matplotlib.pyplot as plt
from collections import Counter
from .CONFIG_functions import student_decoder

class Statistics(ABC):
    """
    Абстрактный класс для работы со статистикой.
    Поддерживает подсчёт среднего, медианы, частоты оценок и другие методы анализа.
    """

    def __init__(self, lst_marks=None, tuple_info=None):
        if lst_marks is None:
            lst_marks = []
        if tuple_info is None:
            tuple_info = {}
        self.pairs = []
        self.yet_added = []
        self.lst_marks = lst_marks

    def set_pairs(self, dirpath):
        """
        Создаёт пары файлов: текстовые/CSV-файлы с результатами и JSON-файлы с данными.
        Помогает связать файлы по названию и дате.
        """
        files = list(filter(lambda x: os.path.isfile(os.path.join(dirpath, x)), os.listdir(dirpath)))
        files_json = list(filter(lambda x: x.endswith('.json'), files))
        files_txt_csv = list(filter(lambda x: x.endswith('.txt') or x.endswith('.csv'), files))
        for file_def in files_txt_csv:
            file_without_ext = Path(file_def).stem
            try:
                _, namework, date = file_without_ext.split('_')
            except ValueError:
                pass
            for file_json in files_json:
                file_json_without_ext = Path(file_json).stem
                try:
                    _, _, namework_json, date_json = file_json_without_ext.split('_')
                except ValueError:
                    pass
                if namework == namework_json and date == date_json:
                    self.pairs.append((file_def, file_json))
                    self.yet_added.append(file_def)

        alone = (item for item in files_txt_csv if item not in self.yet_added)
        for file in alone:
            self.pairs.append((file, None))

    def get_average(self):
        """
        Возвращает среднее значение из списка оценок.
        """
        self.lst_marks = list(filter(lambda x: isinstance(x, int), self.lst_marks))
        if not self.lst_marks:
            print('Нет оценок!')
            sys.exit()
        avr = stat.mean(self.lst_marks)
        return round(avr, 2)

    def get_most_common(self):
        """
        Возвращает наиболее часто встречающуюся оценку.
        """
        return self.__class__.get_counter(self).most_common(1)[0][0]

    def get_counter(self):
        """
        Считает количество каждой оценки в списке.
        """
        return Counter(self.lst_marks)

    def get_median(self):
        """
        Возвращает медиану из списка оценок.
        """
        self.lst_marks = list(filter(lambda x: isinstance(x, int), self.lst_marks))
        if not self.lst_marks:
            print('Нет оценок!')
            sys.exit()
        med = stat.median(self.lst_marks)
        return round(med, 2)

    @abstractmethod
    def get_amount_missings(self, tuple_info):
        """
        Абстрактный метод: должен возвращать количество отсутствующих учеников.
        Реализуется в дочерних классах.
        """
        pass

    @abstractmethod
    def get_amount_notfilled(self, tuple_info):
        """
        Абстрактный метод: должен возвращать количество учеников, не заполнивших работу.
        Реализуется в дочерних классах.
        """
        pass


class BriefStatistics(Statistics):
    """
    Реализует базовые методы для обработки файлов с результатами и подсчёта статистики.
    Включает методы: чтения данных, их преобразования в словарь или список, а также подсчёта количества отсутствующих и незаполненных учеников.
    """

    @staticmethod
    def process_file(filename):
        """
        Читает содержимое файла, пропуская первые 4 строки.
        Поддерживает текстовые и CSV-файлы.
        """
        with open(filename, 'r', encoding='utf-8') as file:
            if filename.endswith('.txt'):
                iterator_lines = map(lambda x: x.strip(), file.readlines())
                for _ in range(4):
                    next(iterator_lines)
                return list(iterator_lines)
            elif filename.endswith('.csv'):
                plain_list = []
                for _ in range(4):
                    next(file)
                for line in file:
                    plain_list.append(line.strip())
                return plain_list

    @staticmethod
    def process_to_dict(namemarks_lst):
        """
        Преобразует список строк вида "Имя: оценка" в словарь.
        Также выделяет отсутствующих и незаполненных учеников.
        """
        dct, lst_of_missings, lst_of_notfulled = {}, [], []
        for namemark in namemarks_lst:
            name, mark = map(lambda x: x.strip(), namemark.split(':'))
            try:
                mark = int(mark)
            except ValueError:
                if mark.startswith('отсутствовал'):
                    lst_of_missings.append(name)
                    mark = None
                else:
                    mark = int(mark[0])
                    lst_of_notfulled.append(name)
            dct[name] = mark
        return dct, lst_of_missings, lst_of_notfulled

    @staticmethod
    def process_to_list(namemarks_lst):
        """
        Преобразует список строк вида "Имя: оценка" в список оценок.
        Пропускает отсутствующих учеников.
        """
        lst = []
        for namemark in namemarks_lst:
            name, mark = map(lambda x: x.strip(), namemark.split(':'))
            try:
                lst.append(int(mark))
            except ValueError:
                if mark.startswith('отсутствовал'):
                    continue
                else:
                    lst.append(int(mark[0]))
        return lst

    def get_amount_missings(self, tuple_info):
        """
        Возвращает количество отсутствующих учеников из переданного кортежа.
        """
        return len(tuple_info[1])

    def get_amount_notfilled(self, tuple_info):
        """
        Возвращает количество учеников, которые не заполнили работу.
        """
        return len(tuple_info[2])


class DeepStatistics(Statistics):
    """
    Расширенный класс для работы со статистикой.
    Обрабатывает JSON-файлы, подсчитывает средние значения, анализирует распределение ответов и выявляет лучших/худших учеников.
    """

    @staticmethod
    def process_file(filename):
        """
        Читает JSON-файл и загружает данные в виде объектов.
        Использует кастомный декодер `student_decoder`.
        """
        with open(filename, 'r', encoding='utf-8') as file:
            json_data = json.load(file, object_hook=student_decoder)
            return json_data

    @staticmethod
    def process_to_list(json_data):
        """
        Собирает список оценок из JSON-данных.
        """
        lst = []
        for student in json_data.values():
            lst.append(student.mark)
        return lst

    @staticmethod
    def process_to_dict(json_data):
        """
        Преобразует JSON-данные в словарь с оценками, списком отсутствующих и незаполненных учеников.
        """
        dct_marks, lst_of_missings, lst_of_notfulled = {}, [], []
        for student, info in json_data.items():
            dct_marks[student] = info.mark
            if info.missings:
                lst_of_missings.append(student)
            if info.flag_not_all:
                lst_of_notfulled.append(student)
        return dct_marks, lst_of_missings, lst_of_notfulled

    @staticmethod
    def process_to_distribution(json_data):
        """
        Собирает информацию о правильности ответов по каждому вопросу.
        """
        lst = []
        for info in json_data.values():
            if info.response_status is None:
                continue
            lst.append(info.response_status)
        return lst

    @staticmethod
    def procces_to_best_worst(json_data):
        """
        Создаёт словарь с оценками и количеством правильных ответов для каждого ученика.
        """
        dct = {}
        for student, info in json_data.items():
            if info.mark is None:
                continue
            dct[student] = (info.mark, info.correct_answers)
        return dct

    @staticmethod
    def process_to_average_answ(json_data):
        """
        Собирает список количества правильных ответов у каждого ученика.
        """
        lst = []
        for info in json_data.values():
            if info.correct_answers is None:
                continue
            lst.append(info.correct_answers)
        return lst

    def get_amount_missings(self, tuple_info):
        """
        Возвращает количество отсутствующих учеников.
        """
        return len(tuple_info[1])

    def get_amount_notfilled(self, tuple_info):
        """
        Возвращает количество учеников, которые не заполнили работу.
        """
        return tuple_info[2]

    @staticmethod
    def get_the_best_puples(dct_best_worst):
        """
        Возвращает топ-3 учеников с самыми высокими оценками.
        """
        return sorted(dct_best_worst, key=lambda x: dct_best_worst[x][0], reverse=True)[:3]

    @staticmethod
    def get_the_worst_puples(dct_best_worst):
        """
        Возвращает топ-3 учеников с самыми низкими оценками.
        """
        return sorted(dct_best_worst, key=lambda x: dct_best_worst[x][0], reverse=False)[:3]

    @staticmethod
    def convert_to_percentage(stats_dict):
        """
        Преобразует количество правильных/неправильных ответов в проценты.
        """
        result = {}
        for question_num, (true_count, false_count) in stats_dict.items():
            total_count = true_count + false_count
            if total_count == 0:
                percent = 0
            else:
                percent = (true_count / total_count) * 100
            result[question_num] = round(percent, 2)
        return result

    @staticmethod
    def get_distribution(lst_distribution):
        """
        Анализирует распределение правильных и неправильных ответов по каждому вопросу.
        """
        result = {}
        for student in lst_distribution:
            for question_num, is_correct in student:
                if question_num not in result:
                    result[question_num] = [0, 0]
                if is_correct:
                    result[question_num][0] += 1
                else:
                    result[question_num][1] += 1
        return {q: tuple(ans) for q, ans in result.items()}

    @staticmethod
    def get_average_answ(lst_average_answ):
        """
        Возвращает среднее количество правильных ответов.
        """
        return round(stat.mean(lst_average_answ), 1)


class StatisticsRecommendations:
    """
    Формирует рекомендации на основе статистики по выполнению заданий.
    Позволяет группировать задания по проценту правильных ответов и выдавать заключения об уровне усвоения темы.
    """

    def __init__(self, converted_to_percentage):
        self.converted_to_percentage = converted_to_percentage
        self.counter = 0

    def group_tasks_by_percent(self):
        """
        Группирует задания по проценту правильных ответов.
        """
        grouped_tasks = {}
        for task, percent in self.converted_to_percentage.items():
            if percent not in grouped_tasks:
                grouped_tasks[percent] = []
            grouped_tasks[percent].append(task)
        return grouped_tasks

    def get_recommendations(self):
        """
        Формирует рекомендации для каждого диапазона процента правильных ответов.
        Возвращает список строк с советами по улучшению усвоения материала.
        """
        DICT_RECOMMENDATIONS = {
            RangeKey(0, 0): f'Задания [{{numbers}}] не решил ни один ученик. Похоже, что задания чересчур сложные.',
            RangeKey(1, 10): f'Задания [{{numbers}}] очень плохо усвоены, меньше 10% учеников ответили верно',
            RangeKey(11, 20): f'Задания [{{numbers}}] ученики выполнили плохо, похоже, что тема усвоена не очень хорошо',
            RangeKey(21, 35): f'Задания [{{numbers}}] выполнила небольшая часть учеников, стоит проработать эту тему',
            RangeKey(36, 45): f'Задания [{{numbers}}] выполнила почти половина учеников, если это были задания повышенной сложности, то это очень неплохо',
            RangeKey(46, 55): f'Задания [{{numbers}}] верно решили около половины учеников',
            RangeKey(56, 70): f'Задания [{{numbers}}] решили больше половины учеников, что очень неплохо',
            RangeKey(71, 90): f'Задания [{{numbers}}] решили большая часть учеников, тема отлично усвоена',
            RangeKey(91, 99): f'Задания [{{numbers}}] не решили всего пара учеников, отличный результат, возможно, задания были слишком простые',
            RangeKey(100, 100): f'Задания [{{numbers}}] решили абсолютно все ученики, тема идеально усвоена или, вероятно, задания были чересчур простые'
        }

        grouped_tasks = self.group_tasks_by_percent()
        recommendations = []

        recommendation_groups = {}
        for percent, tasks in grouped_tasks.items():
            rounded_percent = round(percent)
            for key, rec in DICT_RECOMMENDATIONS.items():
                if rounded_percent in key:
                    if rec not in recommendation_groups:
                        recommendation_groups[rec] = []
                    recommendation_groups[rec].extend(sorted(tasks))

        for rec, tasks in recommendation_groups.items():
            numbers = ', '.join(map(str, tasks))
            recommendations.append(rec.format(numbers=numbers))

        return recommendations

    @staticmethod
    def get_final_conclusion(avrg):
        """
        Возвращает общее заключение о работе на основе среднего процента правильных ответов.
        """
        CONCLUSIONS_DICT = {
            RangeKey(0, 30): 'В среднем ученики не очень хорошо справились с работой, лучше повторить эту тему',
            RangeKey(31, 60): 'В среднем ученики справились с работой, однако около половины учеников не усвоили тему',
            RangeKey(61, 80): 'В среднем ученики хорошо справились с работой, однако некоторые задания вызвали у них сложности',
            RangeKey(81, 99): 'В среднем ученики отлично справились, тема очень хорошо усвоена',
            RangeKey(100, 100): 'Ни один ученик не совершил ни одной ошибки, вам стоит проверить критерии оценивания, ответы или задания на сложность, так как такой исход очень маловероятен'
        }

        for key, conclusion in CONCLUSIONS_DICT.items():
            if round(avrg) in key:
                return conclusion


class PupleDeepStatistics:
    """
    Предоставляет подробную статистику по отдельному ученику.
    Позволяет получить информацию об отсутствии, заполнении работы, оценке, правильности ответов и количестве верных ответов.
    """

    def __init__(self, name, processed_data):
        self.name = name
        self.processed_data = processed_data
        try:
            self.puple = self.processed_data[self.name]
        except:
            print(f'Ученик {self.name} не найден')
            sys.exit()

    def missings(self):
        """
        Возвращает статус отсутствия ученика (True/False).
        """
        return self.puple.missings

    def not_all(self):
        """
        Возвращает статус "не всё заполнено" (True/False).
        """
        return self.puple.flag_not_all

    def mark(self):
        """
        Возвращает оценку ученика.
        """
        return self.puple.mark

    def response_status(self):
        """
        Возвращает список статусов ответов в виде 'Верно' или 'Неверно'.
        """
        not_list = self.puple.response_status
        return list(map(lambda x: 'Верно' if x[1] else 'Неверно', not_list))
        # return not_list

    def correct_answers_am(self):
        """
        Возвращает количество правильных ответов у ученика.
        """
        return self.puple.correct_answers


class DeepStatisticsGraphics:
    """
    Визуализирует статистику выполнения работы в виде графиков.
    Отображает процент правильных ответов по каждому вопросу и распределение оценок.
    """

    def __init__(self, data_distr, data_marks):
        self.data_distr = data_distr  # Словарь: {номер_вопроса: процент_правильных_ответов}
        self.data_marks = data_marks  # Словарь: {оценка: количество_учеников}

    def show(self):
        """
        Строит и отображает два графика:
        1. Процент правильных ответов по вопросам.
        2. Распределение оценок среди учеников.
        """
        sorted_data = sorted(self.data_marks.items(), key=lambda x: (x[0] is None, -x[0] if x[0] is not None else float('inf')))
        counter_data = dict(sorted_data)
        labels = [label if label is not None else 'отсутствующие' for label in counter_data.keys()]
        values = list(counter_data.values())

        color = '#7a7a7a'

        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 7))

        colors_first = []
        for percent in self.data_distr.values():
            if percent < 40:
                colors_first.append('#c71d1d')  # Красный — низкий процент
            elif percent < 70:
                colors_first.append('#eddc31')  # Жёлтый — средний процент
            else:
                colors_first.append('#356a0c')  # Зелёный — высокий процент

        axes[0].bar(self.data_distr.keys(), self.data_distr.values(), color=colors_first)
        axes[0].set_title('Процент правильных ответов по вопросам')
        axes[0].set_ylim(0, 100)
        axes[0].set_xlabel('Номер вопроса')
        axes[0].set_ylabel('Процент правильных ответов')
        axes[0].set_xticks(list(self.data_distr.keys()))

        positions = range(len(values))
        axes[1].bar(positions, values, color=color)
        axes[1].set_title('Распределение оценок')
        axes[1].set_xlabel('Оценка')
        axes[1].set_ylabel('Количество')
        axes[1].set_xticks(positions)
        axes[1].set_xticklabels(labels)
        max_val = int(max(values)) + 1
        axes[1].set_yticks(range(0, max_val))

        plt.tight_layout()
        plt.show()