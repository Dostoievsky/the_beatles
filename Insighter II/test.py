import os
import time
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np


class GraphBuilder:
    """
    Класс для построения и сохранения графиков статистики.
    Методы сохраняют PDF, содержащий по одной странице на каждый график для режима.
    """

    def __init__(self, dpi: int = 150, figsize: Tuple[float, float] = (10, 6)) -> None:
        """
        :param dpi: разрешение сохраняемых изображений
        :param figsize: размер фигур matplotlib (ширина, высота)
        """
        self.dpi = dpi
        self.figsize = figsize

        # цвета для индексов силы (0..5). Можно поменять под стиль.
        self.strength_colors = {
            0: "#d62728",  # красный
            1: "#ff7f0e",  # оранжевый
            2: "#bcbd22",  # желто-зелёный
            3: "#2ca02c",  # зелёный
            4: "#1f77b4",  # синий
            5: "#9467bd",  # фиолетовый
        }

    # ---------- Helpers ----------

    @staticmethod
    def _ensure_dir(path: str) -> None:
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def _normalize_percent_dict(data: Dict[int, float]) -> Dict[int, float]:
        """
        Приводит значения к диапазону 0..1 (если обнаружены 0..100 преобразует).
        """
        if not data:
            return {}
        vals = list(data.values())
        maxv = max(vals)
        if maxv > 1.0:
            # считаем, что это проценты 0..100
            return {k: float(v) / 100.0 for k, v in data.items()}
        else:
            return {k: float(v) for k, v in data.items()}

    @staticmethod
    def _difficulty_color(p: float) -> str:
        """Цвет столбца по доле правильных (p в 0..1)."""
        if p < 0.4:
            return "#d62728"  # red
        if p < 0.7:
            return "#ffbb33"  # yellow/orange
        return "#2ca02c"  # green

    # ---------- Основные графики ----------

    def plot_task_difficulty(
        self,
        difficulty: Dict[int, float],
        pdf_pages: PdfPages,
        title: Optional[str] = None
    ) -> None:
        """
        Строит bar-chart: по X — номера заданий, по Y — доля решивших (0..1).
        Добавляет страницу в переданный PdfPages.
        :param difficulty: dict {task_number: percent_solved} (percent 0..1 or 0..100)
        :param pdf_pages: открытый PdfPages (файл будет записан туда)
        :param title: заголовок (опционально)
        """
        if not difficulty:
            raise ValueError("difficulty пустой")

        data = self._normalize_percent_dict(difficulty)
        tasks = sorted(data.keys())
        values = [data[t] for t in tasks]

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        colors = [self._difficulty_color(v) for v in values]

        ax.bar(tasks, values, color=colors, edgecolor="black")
        ax.set_xlabel("Номер задания")
        ax.set_ylabel("Доля решивших (0—1)")
        ax.set_ylim(0, 1.0)
        ax.set_xticks(tasks)
        ax.set_xticklabels([str(t) for t in tasks], rotation=0)
        ax.set_title(title or "Сложность заданий (доля решивших)")

        # подписи значений сверху столбиков
        for x, y in zip(tasks, values):
            ax.text(x, y + 0.02, f"{y:.0%}", ha="center", va="bottom", fontsize=9)

        fig.tight_layout()
        pdf_pages.savefig(fig)
        plt.close(fig)

    def plot_grade_distribution(
        self,
        grades: Dict[int, int],
        absent_count: int,
        pdf_pages: PdfPages,
        title: Optional[str] = None,
        include_range: Optional[Tuple[int, int]] = None
    ) -> None:
        """
        Гистограмма распределения оценок. Если какие-то оценки отсутствуют — добавляются с 0.
        В конец добавляется отдельный столбец "Отсутств." с числом отсутствующих.
        :param grades: {grade_value: count}
        :param absent_count: количество отсутствующих
        :param pdf_pages: PdfPages для записи страницы
        :param include_range: опционально (min_grade, max_grade) — чтобы всегда отображать фиксированный ряд оценок
        """
        # определяем диапазон оценок, который хотим показать
        if include_range:
            min_g, max_g = include_range
        else:
            if grades:
                min_g = min(grades.keys())
                max_g = max(grades.keys())
            else:
                min_g, max_g = 1, 5  # разумный дефолт

        grades_full = {g: int(grades.get(g, 0)) for g in range(min_g, max_g + 1)}
        labels = [str(g) for g in range(min_g, max_g + 1)]
        counts = [grades_full[int(l)] for l in labels]

        # добавляем отсутствующих как отдельный столбец
        labels.append("Отсутств.")
        counts.append(int(absent_count))

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        bars = ax.bar(range(len(labels)), counts, color="#1f77b4", edgecolor="black")

        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=0)
        ax.set_xlabel("Оценка")
        ax.set_ylabel("Количество учеников")
        ax.set_title(title or "Распределение оценок")

        # подписи над столбиками
        for rect, val in zip(bars, counts):
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2.0, height + max(counts) * 0.02, str(val),
                    ha='center', va='bottom', fontsize=9)

        fig.tight_layout()
        pdf_pages.savefig(fig)
        plt.close(fig)

    def plot_strength_stacked(
        self,
        strength_data: Dict[int, Dict[int, int]],
        pdf_pages: PdfPages,
        title: Optional[str] = None
    ) -> None:
        """
        Строит stacked bar chart по заданиям: для каждого задания показываются сегменты,
        соответствующие индексам силы (0..5). Нулевые по всей задаче индексы пропускаются визуально.
        :param strength_data: {task_number: {strength_index: count, ...}, ...}
        :param pdf_pages: PdfPages для записи
        :param title: заголовок
        """
        if not strength_data:
            raise ValueError("strength_data пустой")

        tasks = sorted(strength_data.keys())
        # список индексов, которые встречаются хотя бы в одном задании
        present_indices = sorted({idx for td in strength_data.values() for idx in td.keys() if td[idx] > 0})
        if not present_indices:
            raise ValueError("Нет ненулевых индексов в strength_data")

        # подготовка матрицы высот: rows = индексы по порядку present_indices, cols = задачи
        matrix = []
        for idx in present_indices:
            row = [strength_data[t].get(idx, 0) for t in tasks]
            matrix.append(row)
        matrix = np.array(matrix)  # shape (K, T)

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        bottoms = np.zeros(len(tasks), dtype=float)
        for row_idx, idx in enumerate(present_indices):
            values = matrix[row_idx]
            color = self.strength_colors.get(idx, None)
            if color is None:
                # fallback to a colormap if index > known
                cmap = plt.get_cmap("tab20")
                color = cmap(row_idx % 20)
            ax.bar(tasks, values, bottom=bottoms, color=color, edgecolor="black", label=f"Сила {idx}")
            bottoms += values

        ax.set_xlabel("Номер задания")
        ax.set_ylabel("Количество учеников")
        ax.set_title(title or "Распределение по индексам силы (stacked)")
        ax.set_xticks(tasks)
        ax.set_xticklabels([str(t) for t in tasks], rotation=0)
        ax.legend(title="Индексы силы", bbox_to_anchor=(1.02, 1), loc='upper left')
        for i, t in enumerate(tasks):
            total = int(np.sum(matrix[:, i]))
            ax.text(t, int(bottoms[i]) + max(1, int(bottoms.max()) * 0.02), str(total),
                    ha="center", va="bottom", fontsize=8)

        fig.tight_layout(rect=[0, 0, 0.85, 1])  # оставляем место под легенду справа
        pdf_pages.savefig(fig)
        plt.close(fig)


    def build_mode1_pdf(
        self,
        difficulty: Dict[int, float],
        grades: Dict[int, int],
        absent_count: int,
        output_pdf_path: str,
        title_prefix: Optional[str] = None
    ) -> str:
        """
        Режим 1: два графика (сложность заданий + распределение оценок).
        Сохраняет один PDF файл по пути output_pdf_path.
        :return: путь к сохранённому PDF
        """
        self._ensure_dir(os.path.dirname(output_pdf_path) or ".")
        with PdfPages(output_pdf_path) as pdf:
            self.plot_task_difficulty(difficulty, pdf, title=f"{title_prefix or ''} — Сложность заданий")
            self.plot_grade_distribution(grades, absent_count, pdf, title=f"{title_prefix or ''} — Распределение оценок")
        return output_pdf_path

    def build_mode2_pdf(
        self,
        difficulty: Dict[int, float],
        grades: Dict[int, int],
        absent_count: int,
        strength_data: Dict[int, Dict[int, int]],
        output_pdf_path: str,
        title_prefix: Optional[str] = None
    ) -> str:

        self._ensure_dir(os.path.dirname(output_pdf_path) or ".")
        with PdfPages(output_pdf_path) as pdf:
            self.plot_task_difficulty(difficulty, pdf, title=f"{title_prefix or ''} — Сложность заданий")
            self.plot_grade_distribution(grades, absent_count, pdf, title=f"{title_prefix or ''} — Распределение оценок")
            self.plot_strength_stacked(strength_data, pdf, title=f"{title_prefix or ''} — Силовой состав решающих")
        return output_pdf_path

    def plot_avg_timeline(
            self,
            avg_data: Dict[str, Tuple[float, str]],  # name -> (avg, date)
            pdf_pages: PdfPages,
            title: Optional[str] = None
    ) -> None:
        """
        Строит линейный график изменения среднего балла по работам.
        Ось Y всегда от 2 до 5 (стандартный диапазон школьных оценок).
        :param avg_data: Словарь {название работы: (средний балл, дата)}
        :param pdf_pages: PdfPages для записи
        :param title: заголовок
        """
        if not avg_data:
            raise ValueError("avg_data пустой")

        # Сортируем работы по дате
        sorted_items = sorted(avg_data.items(), key=lambda x: x[1][1])
        names = [item[0] for item in sorted_items]
        avgs = [item[1][0] for item in sorted_items]

        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        ax.plot(range(len(names)), avgs, marker='o', linestyle='-',
                color='#1f77b4', linewidth=2, markersize=8)
        ax.set_xlabel("Работы в хронологическом порядке")
        ax.set_ylabel("Средний балл")
        ax.set_title(title or "Динамика среднего балла по работам")

        # Фиксируем ось Y от 2 до 5 (стандартный диапазон оценок)
        ax.set_ylim(2, 5)
        ax.set_yticks([2, 2.5, 3, 3.5, 4, 4.5, 5])
        ax.set_yticklabels(['2', '2.5', '3', '3.5', '4', '4.5', '5'])

        ax.set_xticks(range(len(names)))
        ax.set_xticklabels(names, rotation=45, ha='right', fontsize=8)

        ax.grid(True, linestyle='--', alpha=0.7)

        # Подписи значений над точками
        for i, (avg, name) in enumerate(zip(avgs, names)):
            ax.text(i, avg + 0.1, f"{avg:.2f}", ha='center', va='bottom', fontsize=8)

        fig.tight_layout()
        pdf_pages.savefig(fig)
        plt.close(fig)

    def build_mode3_pdf(
            self,
            difficulty: Dict[int, float],
            grades: Dict[int, int],
            absent_count: int,
            avg_timeline: Dict[str, Tuple[float, str]],  # данные для динамики
            output_pdf_path: str,
            title_prefix: Optional[str] = None
    ) -> str:
        """
        Режим 3: три графика (сложность заданий + распределение оценок + динамика среднего балла).
        Сохраняет один PDF файл по пути output_pdf_path.
        :return: путь к сохранённому PDF
        """
        self._ensure_dir(os.path.dirname(output_pdf_path) or ".")
        with PdfPages(output_pdf_path) as pdf:
            self.plot_task_difficulty(difficulty, pdf, title=f"{title_prefix or ''} — Сложность заданий")
            self.plot_grade_distribution(grades, absent_count, pdf,
                                         title=f"{title_prefix or ''} — Распределение оценок")
            self.plot_avg_timeline(avg_timeline, pdf, title=f"{title_prefix or ''} — Динамика среднего балла")
        return output_pdf_path







# # пример данных
# difficulty = {1: 87, 2: 64, 3: 41, 4: 20, 5: 80}
# grades = {5: 4, 4: 6, 3: 3, 2: 1}
# absent_count = 2
# strength_data = {
#     1: {0: 2, 1: 3, 2: 4},
#     2: {1: 5, 3: 2},
#     3: {0: 1, 2: 3, 5: 1},
# }
#
# gb = GraphBuilder()
# out1 = gb.build_mode1_pdf(difficulty, grades, absent_count, "graphs/mode1_example.pdf", title_prefix="Работа #123")
# out2 = gb.build_mode2_pdf(difficulty, grades, absent_count, strength_data, "graphs/mode2_example.pdf")
# print("Saved:", out1, out2)

avg_timeline_data = {
    "Контрольная 1": (3.5, "2025-02-01"),
    "Контрольная 2": (3.8, "2025-02-15"),
    "Контрольная 3": (3.2, "2025-03-01")
}

builder = GraphBuilder()
builder.build_mode3_pdf(
    difficulty={1: 0.8, 2: 0.45, 3: 0.9},
    grades={2: 5, 3: 10, 4: 12, 5: 3},
    absent_count=2,
    avg_timeline=avg_timeline_data,
    output_pdf_path="mode3_report.pdf",
    title_prefix="9А класс"
)