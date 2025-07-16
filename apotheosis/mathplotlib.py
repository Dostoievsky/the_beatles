# import matplotlib.pyplot as plt
# from collections import Counter
#
#
#
#
#
# class DeepStatisticsGraphics:
#     def __init__(self, data_distr, data_marks):
#         self.data_distr = data_distr
#         self.data_marks = data_marks
#
#     def show(self):
#         sorted_data = sorted(self.data_marks.items(), key=lambda x: (x[0] is None, -x[0] if x[0] is not None else float('inf')))
#         counter_data = dict(sorted_data)
#         labels = [label if label is not None else 'отсутствующие' for label in counter_data.keys()]
#         values = list(counter_data.values())
#
#         color = '#7a7a7a'
#
#         fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 7))
#
#         colors_first = []
#         for percent in self.data_distr.values():
#             if percent < 40:
#                 colors_first.append('#c71d1d')
#             elif percent < 70:
#                 colors_first.append('#eddc31')
#             else:
#                 colors_first.append('#356a0c')
#
#         axes[0].bar(self.data_distr.keys(), self.data_distr.values(), color=colors_first)
#         axes[0].set_title('Процент правильных ответов по вопросам')
#         axes[0].set_xlabel('Номер вопроса')
#         axes[0].set_ylabel('Процент правильных ответов')
#         axes[0].set_xticks(list(self.data_distr.keys()))
#
#         positions = range(len(values))
#         axes[1].bar(positions, values, color=color)
#         axes[1].set_title('Распределение оценок')
#         axes[1].set_xlabel('Оценка')
#         axes[1].set_ylabel('Количество')
#         axes[1].set_xticks(positions)
#         axes[1].set_xticklabels(labels)
#
#         plt.tight_layout()
#         plt.show()
#
#
# counter_data = Counter({2: 13, 3: 11, 5: 9, 4: 6, None: 1})
# data_distr = {1: 100.0, 2: 100.0, 3: 100.0, 4: 96.43, 5: 81.48, 6: 81.48, 7: 55.56, 8: 55.56, 9: 33.33, 10: 33.33}
# dpg = DeepStatisticsGraphics(data_distr, counter_data)
# dpg.show()

#
# import matplotlib.pyplot as plt
#
#
#
#
# data1 = {
#     'Каторжная работа 3 06.07.2025': 74,
#     'Паршивая работа 4 09.09.2025': 71,
#     'Тканая работа 2 18.09.2025': 75,
#     'Великая работа 7 16.07.2025': 49
# }
#
# data2 = {'Великая работа 7 16.07.2025': 2.48, 'Катожная работа 3 06.07.2025': 3.39, 'Паршивая работа 4 09.09.2025': 4.34, 'Тканая работа 2 18.09.2025': 3.34}
#
# data3 = {'Великая работа 7 16.07.2025': 2.48, 'Катожная работа 3 06.07.2025': 3.39, 'Паршивая работа 4 09.09.2025': 4.34, 'Тканая работа 2 18.09.2025': 3.34}
#
# # Подготовка данных
# titles1 = list(data1.keys())
# values1 = list(data1.values())
#
# titles2 = list(data2.keys())
# values2 = list(data2.values())
#
# titles3 = list(data3.keys())
# values3 = list(data3.values())
#
# # Создание фигуры с двумя графиками
# fig, axs = plt.subplots(1, 3, figsize=(15, 6))
# fig.subplots_adjust(wspace=100)
#
# # Первый график
# axs[0].plot(titles1, values1, marker='o', linestyle='--', color = '#7a7a7a', linewidth=2)
# axs[0].set_title('Средний процент правильных ответов по работам (первая серия)')
# axs[0].set_ylabel('Средний процент правильных ответов')
# axs[0].set_ylim(0, 100)
# axs[0].set_xticks(range(len(titles1)))  # Указываем координаты тиков
# axs[0].set_xticklabels(titles1, rotation=75, ha='right')  # Подписи с поворотом
#
# # Второй график
# axs[1].plot(titles2, values2, marker='o', linestyle='--', color = '#7a7a7a', linewidth=2)
# axs[1].set_title('Средний процент правильных ответов по работам (вторая серия)')
# axs[1].set_ylabel('Средний процент правильных ответов')
# axs[1].set_ylim(1, 5)
# axs[1].set_xticks(range(len(titles2)))  # Указываем координаты тиков
# axs[1].set_xticklabels(titles2, rotation=75, ha='right')  # Подписи с поворотом
#
# axs[2].plot(titles3, values3, marker='o', linestyle='--', color = '#7a7a7a', linewidth=2)
#
# # Показ графика
# plt.tight_layout()
# plt.show()


import matplotlib.pyplot as plt

# Пример данных
data1 = {'worротуклатk1': 74, 'woвцвцrk2': 71, 'worуцвцвцувk3': 75, 'worувцвуцвk4': 49}
data2 = {'woвцвцццrk1': 60, 'woввцувувrk2': 70, 'wуцвцувork3': 80, 'workуцвцв4': 90}
data3 = {'wввцуццork1': 50, 'wвввуork2': 60, 'worвцуцвуцвцk3': 70, 'woцувцувуцrk4': 80}
data4 = {'wвцвувork1': 40, 'woвввrk2': 50, 'woвувцвуцвrk3': 60, 'woуцвуцвуцвrk4': 70}

# Подготовка данных
titles1 = list(data1.keys())
values1 = list(data1.values())

titles2 = list(data2.keys())
values2 = list(data2.values())

titles3 = list(data3.keys())
values3 = list(data3.values())

titles4 = list(data4.keys())
values4 = list(data4.values())

# Создание фигуры с четырьмя графиками
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

# Первый график
ax1.plot(titles1, values1, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
ax1.set_ylabel('Средний процент правильных ответов')
ax1.set_ylim(0, 100)
ax1.set_xticks(range(len(titles1)))
ax1.set_xticklabels(titles1, rotation=75, ha='right')

# Второй график
ax2.plot(titles2, values2, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
ax2.set_ylabel('Средний процент правильных ответов')
ax2.set_ylim(0, 100)
ax2.set_xticks(range(len(titles2)))
ax2.set_xticklabels(titles2, rotation=75, ha='right')

# Третий график
ax3.plot(titles3, values3, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
ax3.set_ylabel('Средний процент правильных ответов')
ax3.set_ylim(0, 100)
ax3.set_xticks(range(len(titles3)))
ax3.set_xticklabels(titles3, rotation=75, ha='right')

# Четвёртый график
ax4.plot(titles4, values4, marker='o', linestyle='--', color='#7a7a7a', linewidth=2)
ax4.set_ylabel('Средний процент правильных ответов')
ax4.set_ylim(0, 100)
ax4.set_xticks(range(len(titles4)))
ax4.set_xticklabels(titles4, rotation=75, ha='right')


# Показ графика
plt.tight_layout()
plt.show()