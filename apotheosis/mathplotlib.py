import matplotlib.pyplot as plt
from collections import Counter





class DeepStatisticsGraphics:
    def __init__(self, data_distr, data_marks):
        self.data_distr = data_distr
        self.data_marks = data_marks

    def show(self):
        sorted_data = sorted(self.data_marks.items(), key=lambda x: (x[0] is None, -x[0] if x[0] is not None else float('inf')))
        counter_data = dict(sorted_data)
        labels = [label if label is not None else 'отсутствующие' for label in counter_data.keys()]
        values = list(counter_data.values())

        color = '#7a7a7a'

        fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 7))

        colors_first = []
        for percent in self.data_distr.values():
            if percent < 40:
                colors_first.append('#c71d1d')
            elif percent < 70:
                colors_first.append('#eddc31')
            else:
                colors_first.append('#356a0c')

        axes[0].bar(self.data_distr.keys(), self.data_distr.values(), color=colors_first)
        axes[0].set_title('Процент правильных ответов по вопросам')
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

        plt.tight_layout()
        plt.show()


counter_data = Counter({2: 13, 3: 11, 5: 9, 4: 6, None: 1})
data_distr = {1: 100.0, 2: 100.0, 3: 100.0, 4: 96.43, 5: 81.48, 6: 81.48, 7: 55.56, 8: 55.56, 9: 33.33, 10: 33.33}
dpg = DeepStatisticsGraphics(data_distr, counter_data)
dpg.show()