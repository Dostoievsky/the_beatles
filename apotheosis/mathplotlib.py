
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



