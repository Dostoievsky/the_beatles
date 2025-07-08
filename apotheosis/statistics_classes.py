import os
from pathlib import Path
from abc import ABC, abstractmethod
import statistics as stat
from collections import Counter

class Statistics(ABC):
    def __init__(self, lst_marks):
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
        avr = stat.mean(self.lst_marks)
        return round(avr, 2)

    def get_most_common(self):
        return self.__class__.get_counter(self).most_common(1)[0][0]

    def get_counter(self):
        return Counter(self.lst_marks)

    def get_median(self):
        med = stat.median(self.lst_marks)
        return round(med, 2)

    @abstractmethod
    def get_amount_missings(self):
        pass

    @abstractmethod
    def get_notfilled(self):
        pass

    @abstractmethod
    def get_the_best_puples(self):
        pass

    @abstractmethod
    def get_the_worst_puples(self):
        pass



class BriefStatistics(Statistics, ABC):
    def get_amount_missings(self):
        print('test')

    def get_notfilled(self):
        print('test')

    def get_the_best_puples(self):
        print('test')

    def get_the_worst_puples(self):
        print('test')



class DeepStatistics(Statistics, ABC):
    def get_amount_missings(self):
        print('test')

    def get_notfilled(self):
        print('test')

    def get_the_best_puples(self):
        print('test')

    def get_the_worst_puples(self):
        print('test')

    def get_distribution(self):
        pass

    def get_average_answ(self):
        pass

# st = Statistics()
# st.set_pairs(r'D:\pythonProject\apotheosis\archive\8в')
# for index, pair in enumerate(st.pairs, 1):
#     print(f'{pair[0]}[{index}] {"<только краткая статистика>" if pair[1] is None else ""}')

lst = [2, 3, 4, 5, 5, 4, 3, 2, 2, 3, 4, 5, 4, 3, 4, 3, 5, 4, 3, 2, 2, 3, 4, 5, 4, 3, 4, 3, 4, 5, 4, 3, 2, 2, 3, 4, 5, 3, 4, 4, 4, 4, 4, 4]
brief = BriefStatistics(lst)
print(brief.get_average())
print(brief.get_most_common())
print(brief.get_counter())
print(brief.get_median())

deep = DeepStatistics(lst)
print(deep.get_average())
print(deep.get_most_common())
print(deep.get_counter())
print(deep.get_median())
