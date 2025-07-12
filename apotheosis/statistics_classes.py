import json
import os
from pathlib import Path
from abc import ABC, abstractmethod
import statistics as stat
from collections import Counter

class Student:
    def __init__(self, name, surname):
        self._name = name
        self._surname = surname
        self._file = None
        self._list_answers = None
        self._correct_answers = None
        self._response_status = None
        self._mark = None
        self._missings = False
        self._flag_not_all = False


    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @property
    def surname(self):
        return self._surname

    @surname.setter
    def surname(self, new_surname):
        self._surname = new_surname

    @property
    def file(self):
        return self._file

    @file.setter
    def file(self, new_file):
        self._file = new_file

    @property
    def list_answers(self):
        return self._list_answers

    @list_answers.setter
    def list_answers(self, new_list_answers):
        self._list_answers = new_list_answers

    @property
    def correct_answers(self):
        return self._correct_answers

    @correct_answers.setter
    def correct_answers(self, new_correct_answers):
        self._correct_answers = new_correct_answers

    @property
    def response_status(self):
        return self._response_status

    @response_status.setter
    def response_status(self, new_response_status):
        self._response_status = new_response_status


    @property
    def mark(self):
        return self._mark

    @mark.setter
    def mark(self, new_mark):
        self._mark = new_mark

    @property
    def flag_not_all(self):
        return self._flag_not_all

    @flag_not_all.setter
    def flag_not_all(self, value):
        self._flag_not_all = value

    @property
    def missings(self):
        return self._missings

    @missings.setter
    def missings(self, value):
        self._missings = value

    def to_json(self):
        return {
            "__class__": "Student",
            "_name": self._name,
            "_surname": self._surname,
            "_file": self._file,
            "_list_answers": self._list_answers,
            "_correct_answers": self._correct_answers,
            "_response_status": self._response_status,
            "_mark": self._mark,
            "_missings": self._missings,
            "_flag_not_all": self._flag_not_all
        }


def student_decoder(dct):
    if '__class__' in dct and dct['__class__'] == 'Student':
        instance = Student(dct['_name'], dct['_surname'])
        instance._file = dct.get('_file')
        instance._list_answers = dct.get('_list_answers')
        instance._correct_answers = dct.get('_correct_answers')
        instance._response_status = dct.get('_response_status')
        instance._mark = dct.get('_mark')
        instance._missings = dct.get('_missings')
        instance._flag_not_all = dct.get('_flag_not_all')
        return instance
    return dct


class Statistics(ABC):
    def __init__(self, lst_marks=None, tuple_info=None):
        if lst_marks is None:
            lst_marks = []
        if tuple_info is None:
            tuple_info = {}
        self.pairs = []
        self.yet_added = []
        self.lst_marks = lst_marks

    def set_pairs(self, dirpath):
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
        self.lst_marks = list(filter(lambda x: isinstance(x, int), self.lst_marks))
        avr = stat.mean(self.lst_marks)
        return round(avr, 2)

    def get_most_common(self):
        return self.__class__.get_counter(self).most_common(1)[0][0]

    def get_counter(self):
        return Counter(self.lst_marks)

    def get_median(self):
        self.lst_marks = list(filter(lambda x: isinstance(x, int), self.lst_marks))
        med = stat.median(self.lst_marks)
        return round(med, 2)

    @abstractmethod
    def get_amount_missings(self, tuple_info):
        pass

    @abstractmethod
    def get_notfilled(self, tuple_info):
        pass





class BriefStatistics(Statistics):
    @staticmethod
    def process_file(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            iterator_lines =  map(lambda x: x.strip(), file.readlines())
            for _ in range(4):
                next(iterator_lines)
            return list(iterator_lines)

    @staticmethod
    def process_to_dict(namemarks_lst):
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
        return len(tuple_info[2])

    def get_notfilled(self, tuple_info):
        return tuple_info[1]




class DeepStatistics(Statistics):

    @staticmethod
    def process_file(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            json_data = json.load(file, object_hook=student_decoder)
            return json_data

    @staticmethod
    def process_to_list(json_data):
        lst = []
        for student in json_data.values():
            lst.append(student.mark)
        return lst

    @staticmethod
    def process_to_dict(json_data):
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
        lst = []
        for info in json_data.values():
            if info.response_status is None:
                continue
            lst.append(info.response_status)
        return lst

    @staticmethod
    def procces_to_best_worst(json_data):
        dct = {}
        for student, info in json_data.items():
            if info.mark is None:
                continue
            dct[student] = (info.mark, info.correct_answers)
        return dct

    @staticmethod
    def process_to_average_answ(json_data):
        lst = []
        for info in json_data.values():
            if info.correct_answers is None:
                continue
            lst.append(info.correct_answers)
        return lst


    def get_amount_missings(self, tuple_info):
        return len(tuple_info[2])

    def get_notfilled(self, tuple_info):
        return tuple_info[1]

    @staticmethod
    def get_the_best_puples(dct_best_worst):
        return sorted(dct_best_worst, key=lambda x: dct_best_worst[x][0], reverse=True)[:3]

    @staticmethod
    def get_the_worst_puples(dct_best_worst):
        return sorted(dct_best_worst, key=lambda x: dct_best_worst[x][0], reverse=False)[:3]

    @staticmethod
    def convert_to_percentage(stats_dict):
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
        return stat.mean(lst_average_answ)


# st = Statistics()
# st.set_pairs(r'D:\pythonProject\apotheosis\archive\8в')
# for index, pair in enumerate(st.pairs, 1):
#     print(f'{pair[0]}[{index}] {"<только краткая статистика>" if pair[1] is None else ""}')


# processed_data = BriefStatistics.process_file(r'D:\pythonProject\apotheosis\archive\8в\8в_каторжная работа 3_28.06.2025.txt)
# processed_list = BriefStatistics.process_to_list(processed_data)
# processed_dict = BriefStatistics.process_to_dict(processed_data)
# brief = BriefStatistics(processed_list, processed_dict)
# print(brief.get_counter())
# print(brief.get_average())
# print(brief.get_median())
# print(brief.get_most_common())
# print(brief.get_amount_missings(processed_dict))
# print(brief.get_notfilled(processed_dict))


processed_data = DeepStatistics.process_file(r'D:\pythonProject\apotheosis\archive\8в\sysfile_8в_катожная работа 3_06.07.2025.json')
processed_list = DeepStatistics.process_to_list(processed_data)
processed_dict = DeepStatistics.process_to_dict(processed_data)
processed_distribution = DeepStatistics.process_to_distribution(processed_data)
processed_best_worst = DeepStatistics.procces_to_best_worst(processed_data)
processed_average_answ = DeepStatistics.process_to_average_answ(processed_data)



deep = DeepStatistics(processed_list, processed_dict)
print(deep.get_counter())
print(deep.get_average())
print(deep.get_median())
print(deep.get_most_common())
print(deep.get_amount_missings(processed_dict))
print(deep.get_notfilled(processed_dict))
print(deep.get_the_best_puples(processed_best_worst))
print(deep.get_the_worst_puples(processed_best_worst))
print(deep.get_average_answ(processed_average_answ))

stats_dict = deep.get_distribution(processed_distribution)

dek = deep.convert_to_percentage(stats_dict)
# print(dek)
fr = stat.mean(list(dek.values()))
# print(fr)

# print(processed_list)

class RangeKey:
    def __init__(self, start, stop, step=1):
        self.range_obj = range(start, stop + 1, step)

    def __eq__(self, other):
        if isinstance(other, RangeKey):
            return (
                self.range_obj.start == other.range_obj.start and
                self.range_obj.stop == other.range_obj.stop and
                self.range_obj.step == other.range_obj.step
            )
        return NotImplemented

    def __hash__(self):
        return hash((self.range_obj.start, self.range_obj.stop, self.range_obj.step))

    def __contains__(self, item):
        return item in self.range_obj

    def __repr__(self):
        return f"RangeKey({self.range_obj.start}-{self.range_obj.stop-1})"




class StatisticsRecommendations:
    def __init__(self, converted_to_percentage):
        self.converted_to_percentage = converted_to_percentage
        self.counter = 0

    def group_tasks_by_percent(self):
        grouped_tasks = {}
        for task, percent in self.converted_to_percentage.items():
            if percent not in grouped_tasks:
                grouped_tasks[percent] = []
            grouped_tasks[percent].append(task)
        return grouped_tasks


    def get_recommendations(self):
        DICT_RECOMMENDATIONS = {
            RangeKey(0, 0): f'Задания [{{numbers}}] не решил ни один ученик. Похоже, что задания чересчур сложные.',
            RangeKey(1, 10): f'Задания [{{numbers}}] очень плохо усвоены, меньше 10% учеников ответили верно',
            RangeKey(11, 20): f'Задания [{{numbers}}] ученики выполнили плохо, похоже, что тема усвоена не очень хорошо',
            RangeKey(21, 35): f'Задания [{{numbers}}] выполнила небольшая часть учеников, стоит проработать эту тему',
            RangeKey(36, 45): f'Задания [{{numbers}}] выполнила почти половина учеников, если это были задания повышенной сложности, то это очень неплохо',
            RangeKey(46, 55): f'Задания [{{numbers}}] верно решили около половины учеников',
            RangeKey(56, 70): f'Задания [{{numbers}}] решили больше половины учеников, что очень неплохо',
            RangeKey(71, 90): f'Задания [{{numbers}}] решили большая часть ученики, тема отлично усвоена',
            RangeKey(91, 99): f'Задания [{{numbers}}] не решили всего пара ученников, отличный результат, возможно, задания были слишком простые',
            RangeKey(100, 100): f'Задания [{{numbers}}] решили абсолютно все ученики, тема идеально усвоена или, вероятно, задания были чересчур простые'}
        grouped_tasks = self.group_tasks_by_percent()
        recommendations = []

        for percent, tasks in grouped_tasks.items():
            numbers = ', '.join(map(str, tasks))
            for key, rec in DICT_RECOMMENDATIONS.items():
                if round(percent) in key:
                    recommendations.append(rec.format(numbers=numbers))

        return recommendations


    @staticmethod
    def get_final_conclusion(avrg):
        CONCLUSIONS_DICT = {RangeKey(0, 30): 'В срднем ученики не очень хорошо справились с работой, лучше повторить эту тему',
                            RangeKey(31, 60): 'В среднем ученики справились с работой, однако около половины учеников не усвоили тему',
                            RangeKey(61, 80): 'В среднем ученики хорошо справились с работой, однако некоторые задания вызвали у них сложности',
                            RangeKey(81, 99): 'В среднем ученики отлично справились, тема очень хорошо усвоена',
                            RangeKey(100, 100): f'Ни один ученик не совершил ни одной ошибки, вам стоит проверить критерии оцениквания, ответы или задания на сложность, так как такой исход очень маловероятен'}
        for key, conclusion in CONCLUSIONS_DICT.items():
            if round(avrg) in key:
                return conclusion




strec = StatisticsRecommendations(deep.convert_to_percentage(stats_dict))
print()
print(*strec.get_recommendations(), sep='\n')
print()
print(strec.get_final_conclusion(fr))


print()
print()
print()

class PupleDeepStatistics:
    def __init__(self, name, processed_data):
        self.name = name
        self.processed_data = processed_data
        try:
            self.puple = self.processed_data[self.name]
        except:
            print(f'Ученик {self.name} не найден')

    def missings(self):
        return self.puple.missings

    def not_all(self):
        return self.puple.flag_not_all

    def mark(self):
        return self.puple.mark

    def response_status(self):
        not_list = self.puple.response_status
        return list(map(lambda x: 'Верно' if x[1] else 'Неверно', not_list))
        # return not_list

    def correct_answers_am(self):
        return self.puple.correct_answers


pds = PupleDeepStatistics('dmkebh Второй', processed_data)
if pds.missings():
    print('Отсутствовал')
else:
    print(pds.name)
    print(*pds.response_status(), sep='\n')
    print(pds.correct_answers_am())
    print(pds.mark())
    print(pds.not_all())






