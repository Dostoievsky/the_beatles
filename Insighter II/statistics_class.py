import statistics
from collections import Counter, defaultdict
import pandas as pd
import re


class StatisticsParser:
    def __init__(self, tasks_dict, grades_dict, file_name=None):
        self.tasks_dict = {k: v for k, v in tasks_dict.items() if v is not None}
        self.grades_dict = {k: v for k, v in grades_dict.items() if v is not None}
        self.file_name = file_name

    @staticmethod
    def normalize_name(name):
        parts = name.strip().split()
        parts.sort()
        return " ".join(parts)

    def fix_fio_spacing(self, text):
        fixed_text = re.sub(r'([а-яё])(?=[А-ЯЁ])', r'\1 ', text)
        return self.normalize_name(fixed_text.strip())

    def get_file_results(self):
        if not self.file_name:
            return None
        students_dict = self.get_students_dict()
        return {self.fix_fio_spacing(k): v for k, v in students_dict.items()}


    def get_students_dict(self):
        df = pd.read_excel(self.file_name, header=None, engine='openpyxl')
        students_data = {}
        print('rfrf')

        for _, row in df.iterrows():
            line = [str(val).strip() for val in row.values]

            if len(line) > 1 and line[0].isdigit() and re.match(r'^[А-ЯЁ]', line[1]):
                fio = line[1]

                grades = []
                for cell in line[2:]:
                    if cell == 'nan' or not cell: continue
                    found = re.findall(r'[2-5]', cell)
                    grades.extend([int(g) for g in found])

                if grades:
                    students_data[fio] = {
                        'avg_score': round(sum(grades) / len(grades), 2),
                        'total_grades': len(grades)
                    }

        return students_data


    def get_average(self):
        grades = [g for g in self.grades_dict.values() if g is not None]
        if not grades:
            return 0
        return round(statistics.mean(grades), 2)


    def get_median(self):
        grades = [g for g in self.grades_dict.values() if g is not None]
        if not grades:
            return 0
        return round(statistics.median(grades), 2)


    def get_grades_distribution(self):
        counter = Counter(list(self.grades_dict.values()))
        return dict(counter)


    @staticmethod
    def get_first_group(sorted_dict):
        if not sorted_dict:
            return {}

        it = iter(sorted_dict.items())
        first_key, first_value = next(it)

        result = {first_key: first_value}

        for key, value in it:
            if value == first_value:
                result[key] = value
            else:
                break

        return result


    def get_task_distribution(self):
        task_stats = {}
        for task in self.tasks_dict.values():
            for task_num, is_correct in task.items():
                if is_correct:
                    task_stats[task_num] = task_stats.get(task_num, 0) + 1
                else:
                    task_stats[task_num] = task_stats.get(task_num, 0)
        return task_stats


    def convertage_to_percentages(self, total_students):
        results_dict = self.get_task_distribution()
        return {task: round(((correct / total_students) * 100), 2) for task, correct in results_dict.items()}


    def get_student_distribution(self):
        result_dict = {}
        for student, tasks in self.tasks_dict.items():
            result_dict[student] = sum(tasks.values())

        return result_dict

    def get_best_worst_results(self):
        best = (max(self.get_student_distribution().values()), max(self.grades_dict.values()))
        worst = (min(self.get_student_distribution().values()), min(self.grades_dict.values()))
        return best, worst


    def get_the_best_the_worst_students_results(self):
        distbt = self.get_student_distribution()
        sorted_dict_best = dict(sorted(distbt.items(), key=lambda item: item[1], reverse=True))
        best_students = self.get_first_group(sorted_dict_best)
        sorted_dict_worst = dict(sorted(distbt.items(), key=lambda item: item[1]))
        worst_students = self.get_first_group(sorted_dict_worst)
        return best_students, worst_students


    def get_strong_weak_students(self):
        journal_indices = {}
        students_avg_dict = self.get_file_results()
        for student, data in students_avg_dict.items():
            strong_index = data['avg_score']
            total_grades = data['total_grades'] if data['total_grades'] < 6 else 6

            if strong_index >= 4.85 and total_grades == 6:
                journal_indices[student] = 5
            elif strong_index >= 4.5 and total_grades in [3, 4, 5, 6]:
                journal_indices[student] = 4
            elif strong_index >= 3.7 and total_grades in [3, 4, 5, 6]:
                journal_indices[student] = 3
            elif strong_index >= 3.0 and total_grades in [3, 4, 5, 6]:
                journal_indices[student] = 2
            elif strong_index >= 2.0 and total_grades in [3, 4, 5, 6]:
                journal_indices[student] = 1
            else:
                journal_indices[student] = 0

        # Добавляем всех учеников из работы, для неизвестных ставим 0
        all_indices = {}
        for student in self.tasks_dict.keys():
            norm_student = self.fix_fio_spacing(student)  # нормализуем имя для поиска
            if norm_student in journal_indices:
                all_indices[student] = journal_indices[norm_student]
            else:
                all_indices[student] = 0  # ученик не найден в журнале

        counts = Counter(all_indices.values())
        total_distr = {i: counts.get(i, 0) for i in range(6)}
        return all_indices, total_distr


    def get_distribution_tasks_strong_weak_students(self):
        students_avg_distr = self.get_strong_weak_students()[0]
        task_distr = self.tasks_dict
        if task_distr:
            _ = next(iter(task_distr.values()))
        any_student_tasks = next(iter(task_distr.values())).keys()

        result = {}

        for task_id in any_student_tasks:
            distr = {i: 0 for i in range(6)}

            for student_name, tasks in task_distr.items():
                if student_name in students_avg_distr:
                    strength_index = students_avg_distr[student_name]
                    if tasks.get(task_id):
                        distr[strength_index] += 1
            result[task_id] = distr
        return result


    @staticmethod
    def get_recomdendations_standart(percentage_dict):
        groups = defaultdict(list)

        for task_id, percent in percentage_dict.items():
            if percent == 0:
                groups['не решил никто, обязательно разберите теорию заново или упростите задачи'].append(task_id)
            elif 0 < percent <= 20:
                groups['не решил почти никто, вероятно, задачи были слишком сложными или тема не усвоена'].append(
                    task_id)
            elif 20 < percent <= 40:
                groups['вызвали серьезные затруднения у большинства учеников'].append(task_id)
            elif 40 < percent <= 60:
                groups['решены на среднем уровне, стоит закрепить материал'].append(task_id)
            elif 60 < percent <= 85:
                groups['решены хорошо большинством учеников'].append(task_id)
            elif 85 <= percent < 100:
                groups['решены почти всеми, отличный результат'].append(task_id)
            elif percent == 100:
                groups['решили абсолютно все, тема усвоена идеально или задания были слишком простые'].append(task_id)

        recommendations = []
        for text, ids in groups.items():
            if ids:
                formatted_ids = sorted(ids)
                recommendations.append(f"Задания {formatted_ids} {text}")

        return recommendations


    @staticmethod
    def get_recomdendations_deep(tasks_stats, group_counts):
        """
        :param tasks_stats: dict {номер_задания: {группа: количество_решивших}}
        :param group_counts: dict {группа: общее_количество_учеников}
        """
        total_all = sum(group_counts.values())
        if total_all == 0:
            return ["Нет данных об учениках"]

        weak_groups = [1, 2]
        med_groups = [3]
        strong_groups = [4, 5]
        unknown_group = [0]

        count_weak = sum(group_counts.get(g, 0) for g in weak_groups)
        count_med = sum(group_counts.get(g, 0) for g in med_groups)
        count_strong = sum(group_counts.get(g, 0) for g in strong_groups)
        count_unknown = sum(group_counts.get(g, 0) for g in unknown_group)

        recommendations = []

        for task_id, stats in tasks_stats.items():
            solved_weak = sum(stats.get(g, 0) for g in weak_groups)
            solved_med = sum(stats.get(g, 0) for g in med_groups)
            solved_strong = sum(stats.get(g, 0) for g in strong_groups)
            solved_unknown = sum(stats.get(g, 0) for g in unknown_group)

            solved_total = solved_weak + solved_med + solved_strong + solved_unknown

            rate_weak = solved_weak / count_weak if count_weak > 0 else 0
            rate_med = solved_med / count_med if count_med > 0 else 0
            rate_strong = solved_strong / count_strong if count_strong > 0 else 0

            p_total = round((solved_total / total_all) * 100)
            p_weak = round((solved_weak / total_all) * 100)
            p_med = round((solved_med / total_all) * 100)
            p_strong = round((solved_strong / total_all) * 100)
            p_unknown = round((solved_unknown / total_all) * 100)

            stats_parts = []
            if count_weak > 0:
                stats_parts.append(f"слабые – {solved_weak}/{count_weak} ({p_weak}%)")
            if count_med > 0:
                stats_parts.append(f"средние – {solved_med}/{count_med} ({p_med}%)")
            if count_strong > 0:
                stats_parts.append(f"сильные – {solved_strong}/{count_strong} ({p_strong}%)")
            if count_unknown > 0:
                stats_parts.append(f"мало данных – {solved_unknown}/{count_unknown} ({p_unknown}%)")

            stats_str = f"Решили всего: {solved_total}/{total_all} ({p_total}%). " + "Из них: " + ", ".join(stats_parts) + "."


            if rate_weak > rate_strong + 0.3 and rate_weak > 0.5 and count_weak > 0 and count_strong > 0:
                rec = "Подозрение на списывание или некорректную формулировку: слабые ученики справились значительно лучше сильных."

            elif rate_strong < rate_med - 0.2 and count_med > 0 and count_strong > 0:
                rec = "Задание 'с подвохом': сильные ученики ошибаются чаще средних. Проверьте формулировку."

            elif p_total > 85:
                rec = "Задание слишком лёгкое: почти все справились. Не подходит для дифференциации."

            elif p_total < 15:
                rec = "Задание практически нерешаемое: требуется разбор темы с нуля."

            elif rate_strong > 0.7 and rate_weak < 0.3 and rate_med < 0.6:
                rec = "Отличное задание: чётко разделяет сильных и слабых. Рекомендуется для контрольных."

            elif rate_strong > 0.4 and rate_weak < 0.2 and rate_med < 0.5:
                rec = "Задание повышенной сложности: подходит для отбора претендентов на '5'."

            elif 30 <= p_total <= 75:
                rec = "Стандартное задание средней сложности. Хорошо подходит для текущей проверки знаний."

            elif max(rate_weak, rate_med, rate_strong) - min(rate_weak, rate_med, rate_strong) < 0.2:
                rec = "Задание со слабой дифференциацией: все группы справились примерно одинаково."

            elif solved_total == 0:
                rec = "Данных по решению задания нет."

            else:
                rec = "Задание со специфическим распределением. Требуется ручной просмотр."

            recommendations.append(f"Задание {task_id}: {stats_str} {rec}")

        return recommendations


    @staticmethod
    def get_brief_conclusion(grades, task_percentages):
        if not grades or not task_percentages:
            return "Данные для анализа отсутствуют."

        avg_grade = sum(grades.values()) / len(grades)
        bad_tasks_count = sum(1 for p in task_percentages.values() if p < 40)

        if avg_grade >= 4.2:
            grade_summary = "Ученики продемонстрировали отличный уровень подготовки и успешно справились с предложенной работой."
        elif avg_grade >= 3.6:
            grade_summary = "Класс показал стабильные и уверенные результаты, в целом успешно освоив материал."
        elif avg_grade >= 3.0:
            grade_summary = "Работа выполнена на среднем уровне; основные темы усвоены, но есть пространство для роста."
        else:
            grade_summary = "Результаты работы вызывают беспокойство; большая часть класса столкнулась с серьезными трудностями при выполнении."

        if bad_tasks_count == 0:
            task_summary = "Все предложенные задания были решены на достаточном уровне, системных ошибок не выявлено."
        elif bad_tasks_count <= 2:
            task_summary = "При этом пара заданий вызвала точечные затруднения, их стоит разобрать вкратце на следующем занятии."
        else:
            task_summary = "Ряд заданий оказался слишком сложным для большинства учеников, что указывает на необходимость повторного разбора ключевых тем."

        return f"{grade_summary} {task_summary}"


    @staticmethod
    def get_extended_analysis(grades, task_stats, student_indices, student_solutions, group_counts):
        """
        Аргументы:
        :param grades: dict {имя: оценка} — итоговые оценки за работу
        :param task_stats: dict {номер_задания: {индекс_силы: кол-во_решивших}} — статистика успехов по группам
        :param student_indices: dict {имя: индекс_силы} — изначальный уровень подготовки каждого ученика
        :param student_solutions: dict {имя: [список_решенных_задач]} — список решенных номеров задач каждым учеником
        :param group_counts: dict {индекс: общее_кол-во_учеников} — сколько всего человек в каждой группе (1-5)
        """

        if not grades:
            return "Данные для формирования полного отчета отсутствуют."

        # 1. Синхронизированная статистика по оценкам
        total_students = len(grades)
        avg_grade = round(sum(grades.values()) / total_students, 2)

        # Тот же порог, что в кратком выводе
        if avg_grade >= 4.2:
            work_status = "отлично"
        elif avg_grade >= 3.6:
            work_status = "хорошо"
        elif avg_grade >= 3.0:
            work_status = "удовлетворительно (на среднем уровне)"
        else:
            work_status = "неудовлетворительно (ниже ожидаемого уровня)"

        # 2. Поиск аномальных и сложных заданий
        hard_tasks = []
        anomalous_tasks = []
        total_class_size = sum(group_counts.values())

        for t_id, stats in task_stats.items():
            c_weak = sum(group_counts.get(i, 0) for i in [1, 2])
            c_strong = sum(group_counts.get(i, 0) for i in [4, 5])

            s_weak = sum(stats.get(i, 0) for i in [1, 2])
            s_strong = sum(stats.get(i, 0) for i in [4, 5])

            rate_weak = s_weak / c_weak if c_weak > 0 else 0
            rate_strong = s_strong / c_strong if c_strong > 0 else 0

            total_solved = sum(stats.values())
            p_total = (total_solved / total_class_size) * 100

            if p_total < 15:
                hard_tasks.append(t_id)
            if rate_weak > rate_strong + 0.3 and rate_weak > 0.5:
                anomalous_tasks.append(t_id)

        # 3. Анализ учеников
        better_than_usual = []
        worse_than_usual = []
        cheating_suspects = []

        for name, grade in grades.items():
            idx = student_indices.get(name, 0)
            if grade > idx != 0:
                better_than_usual.append(name)
            if idx >= 4 and grade <= 3:
                worse_than_usual.append(name)
            if idx <= 2 and any(task in anomalous_tasks for task in student_solutions.get(name, [])):
                cheating_suspects.append(name)

        # 4. Сборка итоговой строки
        res = f"Работа выполнена {work_status}, средний балл класса — {avg_grade}. "

        # Блок заданий (теперь с проверкой на "все в норме")
        if not hard_tasks and not anomalous_tasks:
            res += "Все задания подобраны корректно, критических сложностей или системных аномалий не выявлено. "
        else:
            if hard_tasks:
                res += f"Стоит обратить внимание на задания {hard_tasks}, которые оказались критически сложными. "
            if anomalous_tasks:
                res += f"В заданиях {anomalous_tasks} выявлено аномальное распределение, возможно массовое списывание. "

        # Списки учеников
        if better_than_usual:
            res += f"Результаты выше ожидаемых показали: [{', '.join(better_than_usual)}]. "
        if worse_than_usual:
            res += f"Ниже своего уровня справились: [{', '.join(worse_than_usual)}]. "
        if cheating_suspects:
            res += f"Подозрение в использовании сторонней помощи из-за решения аномальных задач: [{', '.join(cheating_suspects)}]."

        return res.strip()


class CompareParser:
    def __init__(self, this_work_dict, comare_work_dict):
        self.this_work_dict = this_work_dict
        self.comare_work_dict = comare_work_dict

    def compare_avg(self):
        this_avg = self.this_work_dict['avg']
        list_avg = [v['avg'] for v in self.comare_work_dict.values()]
        other_avg = round(statistics.mean(list_avg), 2)

        diff = this_avg - other_avg
        rounded_diff = round(abs(diff), 2)

        if this_avg > other_avg:
            return f"Средняя оценка стала выше на {rounded_diff} по сравнению с предыдущими работами"
        elif this_avg < other_avg:
            return f"Средняя оценка стала ниже на {rounded_diff} по сравнению с предыдущими работами"
        else:
            return "Средняя оценка не изменилась по сравнению с предыдущими работами"


    @staticmethod
    def get_count(distr, keys):
        return sum(distr.get(k, 0) for k in keys)


    def compare_grades(self):
        d_this = self.this_work_dict['grades_distribution']
        total_this = sum(d_this.values())
        this_bad = self.get_count(d_this, [2, 3])
        this_good = self.get_count(d_this, [4, 5])

        if total_this == 0:
            this_bad_percent = 0
            this_good_percent = 0
        else:
            this_bad_percent = (this_bad / total_this) * 100
            this_good_percent = (this_good / total_this) * 100

        total_bad_other = 0
        total_good_other = 0
        total_other_all = 0

        for work in self.comare_work_dict.values():
            d_other = work['grades_distribution']
            total_other = sum(d_other.values())

            if total_other > 0:
                total_bad_other += self.get_count(d_other, [2, 3])
                total_good_other += self.get_count(d_other, [4, 5])
                total_other_all += total_other

        if total_other_all == 0:
            other_bad_percent = 0
            other_good_percent = 0
        else:
            other_bad_percent = (total_bad_other / total_other_all) * 100
            other_good_percent = (total_good_other / total_other_all) * 100

        if total_this == 0:
            good_message = "В текущей работе нет оценок для сравнения"
        else:
            diff_good = this_good_percent - other_good_percent
            rounded_diff = round(abs(diff_good))

            if diff_good > 0:
                good_message = f"Количество хороших оценок в этой работе на {rounded_diff}% больше по сравнению с предыдущими работами"
            elif diff_good < 0:
                good_message = f"Количество хороших оценок в этой работе на {rounded_diff}% меньше по сравнению с предыдущими работами"
            else:
                good_message = "Количество хороших оценок такое же, какое было в среднем за предыдущие работы"

        if total_this == 0:
            bad_message = "В текущей работе нет оценок для сравнения"
        else:
            diff_bad = this_bad_percent - other_bad_percent
            rounded_diff = round(abs(diff_bad))

            if diff_bad > 0:
                bad_message = f"Количество плохих оценок в этой работе на {rounded_diff}% больше по сравнению с предыдущими работами"
            elif diff_bad < 0:
                bad_message = f"Количество плохих оценок в этой работе на {rounded_diff}% меньше по сравнению с предыдущими работами"
            else:
                bad_message = "Количество плохих оценок такое же, какое было в среднем за предыдущие работы"

        return good_message, bad_message


    def compare_absents(self):
        this_absents = self.this_work_dict['absents']
        avg_other_absents = statistics.mean(work['absents'] for work in self.comare_work_dict.values())
        if this_absents > round(avg_other_absents):
            return 'Отсутствующих больше, чем обычно'
        elif this_absents < avg_other_absents:
            return 'Отсутствующих меньше, чем обычно'
        else:
            return 'Отсутствущих примерно столько же, сколько и обычно'


    def compare_best_worst(self):
        this_best = set(self.this_work_dict['best_students'].keys())
        this_worst = set(self.this_work_dict['worst_students'].keys())

        all_previous_best = []
        all_previous_worst = []

        for work in self.comare_work_dict.values():
            all_previous_best.extend(work['best_students'].keys())
            all_previous_worst.extend(work['worst_students'].keys())

        total_previous_works = len(self.comare_work_dict)

        if total_previous_works > 0 and this_best:
            best_students_count = {}
            for student in this_best:
                count = all_previous_best.count(student)
                best_students_count[student] = count

            consistent_best = [student for student, count in best_students_count.items() if count >= total_previous_works * 0.5]

            if consistent_best:
                if len(consistent_best) == 1:
                    best_message = f"Ученик {consistent_best[0]} остается лучшим в большинстве последних работ"
                else:
                    students_list = ", ".join(consistent_best)
                    best_message = f"Ученики {students_list} остаются лучшими в большинстве последних работ"
            else:
                best_message = "Нет явно выраженных лучших учеников в предыдущих работах"
        else:
            best_message = "Нет явно выраженных лучших учеников в предыдущих работах"

        if total_previous_works > 0 and this_worst:
            worst_students_count = {}
            for student in this_worst:
                count = all_previous_worst.count(student)
                worst_students_count[student] = count

            consistent_worst = [student for student, count in worst_students_count.items() if count >= total_previous_works * 0.5]

            if consistent_worst:
                if len(consistent_worst) == 1:
                    worst_message = f"Ученик {consistent_worst[0]} остается худшим в большинстве последних работ"
                else:
                    students_list = ", ".join(consistent_worst)
                    worst_message = f"Ученики {students_list} остаются худшими в большинстве последних работ"
            else:
                worst_message = "Нет явно выраженных худших учеников в предыдущих работах"
        else:
            worst_message = "Нет явно выраженных худших учеников в предыдущих работах"

        return best_message, worst_message


# others_dict = {'Журнальная работа 0': {'avg': 2.67, 'median': 3.0, 'grades_distribution': {3: 14, 2: 9, 4: 1}, 'best_students': {'Надежда Попцова': 8}, 'worst_students': {'Рауль Масимов': 4, 'Анастасия Хромова': 4, 'Андрей Цветков': 4}, 'absents': 0}, 'Работа имени шишкина-мышкина': {'avg': 3.46, 'median': 3.5, 'grades_distribution': {2: 3, 4: 10, 3: 9, 5: 2}, 'best_students': {'Тимофей Гусев': 10, 'Татьяна Левкович': 10}, 'worst_students': {'Матвей Некрасов': 4}, 'absents': 0}}
# this_dict = {'avg': 3.17, 'median': 3.0, 'grades_distribution': {3: 8, 4: 10, 2: 6}, 'best_students': {'Дмитрий Афанасов': 9, 'Маргарита Горовая': 9, 'Никита Корсаков': 9, 'Татьяна Левкович': 9, 'Матвей Некрасов': 9, 'Михаил Соколов': 9, 'Анастасия Хромова': 9}, 'worst_students': {'Рауль Масимов': 3}, 'recomendations': ['Задания [1, 3, 4, 5, 6, 7, 8, 9] решены хорошо большинством учеников', 'Задания [2, 10] решены на среднем уровне, стоит закрепить материал'], 'conclusion': 'Работа выполнена на среднем уровне; основные темы усвоены, но есть пространство для роста. Все предложенные задания были решены на достаточном уровне, системных ошибок не выявлено.', 'best_results': (9, 4), 'worst_results': (3, 2), 'absents': 0}
#
# compare = CompareParser(this_dict, others_dict)
# print(compare.compare_avg())
# print(compare.compare_grades())
# print(compare.compare_absents())
# print(compare.compare_best_worst())


# tasks_dict1 = {
#     'Андреева Софья': {1: True, 2: False, 3: True, 4: True, 5: False, 6: True, 7: False, 8: True, 9: False, 10: True},
#     'Афанасов Дмитрий': {1: False, 2: True, 3: False, 4: True, 5: True, 6: False, 7: True, 8: False, 9: True, 10: False},
#     'Гусев Тимофей': {1: True, 2: True, 3: False, 4: False, 5: True, 6: True, 7: False, 8: True, 9: False, 10: True},
#     'Корсаков Никита': {1: False, 2: False, 3: True, 4: True, 5: False, 6: False, 7: True, 8: True, 9: True, 10: False},
#     'Котлячкова Варвара': {1: True, 2: False, 3: True, 4: False, 5: True, 6: False, 7: True, 8: False, 9: True, 10: True},
#     'Левкович Татьяна': {1: False, 2: True, 3: True, 4: True, 5: False, 6: True, 7: False, 8: False, 9: True, 10: False},
#     'Нахина Виктория': {1: True, 2: False, 3: False, 4: True, 5: True, 6: True, 7: False, 8: True, 9: False, 10: True},
#     'Некрасов Матвей': {1: False, 2: True, 3: True, 4: False, 5: False, 6: True, 7: True, 8: True, 9: False, 10: True},
#     'Нечаева Елизавета': {1: True, 2: True, 3: False, 4: True, 5: False, 6: False, 7: True, 8: False, 9: True, 10: False},
#     'Попцова Надежда': {1: False, 2: False, 3: True, 4: False, 5: True, 6: True, 7: True, 8: False, 9: False, 10: True},
#     'Сироткин Матвей': {1: True, 2: True, 3: True, 4: False, 5: False, 6: False, 7: False, 8: True, 9: True, 10: True},
#     'Смирнова Виктория': {1: False, 2: True, 3: False, 4: True, 5: True, 6: True, 7: False, 8: False, 9: False, 10: False},
#     'Соколов Михаил': {1: True, 2: False, 3: True, 4: True, 5: False, 6: True, 7: True, 8: True, 9: False, 10: True},
#     'Стулихин Дмитрий': {1: False, 2: True, 3: False, 4: False, 5: True, 6: False, 7: True, 8: True, 9: True, 10: False},
#     'Сырова Ксения': {1: True, 2: False, 3: True, 4: True, 5: True, 6: False, 7: False, 8: False, 9: True, 10: True},
#     'Цветков Андрей': {1: False, 2: True, 3: True, 4: False, 5: False, 6: True, 7: True, 8: True, 9: False, 10: False},
#     'Чернова Василиса': {1: True, 2: False, 3: False, 4: True, 5: True, 6: False, 7: True, 8: False, 9: True, 10: True}
# }
# res_dict = {
#     'Андреева Софья': 4,  # 6 True
#     'Афанасов Дмитрий': 3,  # 5 True
#     'Гусев Тимофей': 4,  # 6 True
#     'Корсаков Никита': 3,  # 4 True
#     'Котлячкова Варвара': 4,  # 6 True
#     'Левкович Татьяна': 3,  # 4 True
#     'Нахина Виктория': 4,  # 6 True
#     'Некрасов Матвей': 3,  # 5 True
#     'Нечаева Елизавета': 3,  # 4 True
#     'Попцова Надежда': 3,  # 5 True
#     'Сироткин Матвей': 4,  # 6 True
#     'Смирнова Виктория': 3,  # 4 True
#     'Соколов Михаил': 4,  # 7 True
#     'Стулихин Дмитрий': 3,  # 5 True
#     'Сырова Ксения': 4,  # 6 True
#     'Цветков Андрей': 3,  # 5 True
#     'Чернова Василиса': 4  # 6 True
# }
#
# t = {'Софья Андреева': {1: False, 2: False, 3: True, 4: False, 5: True, 6: True, 7: True, 8: False, 9: True, 10: True}, 'Дмитрий Афанасов': {1: False, 2: True, 3: True, 4: True, 5: False, 6: False, 7: False, 8: True, 9: True, 10: True}, 'Матвей Бокарев': {1: False, 2: False, 3: False, 4: True, 5: False, 6: True, 7: True, 8: True, 9: True, 10: False}, 'Елисей Бугров': {1: True, 2: True, 3: True, 4: True, 5: False, 6: False, 7: True, 8: False, 9: True, 10: True}, 'Маргарита Горовая': {1: True, 2: False, 3: True, 4: True, 5: False, 6: True, 7: False, 8: True, 9: False, 10: False}, 'Тимофей Гусев': {1: False, 2: False, 3: True, 4: True, 5: True, 6: True, 7: True, 8: True, 9: True, 10: False}, 'Вячеслав Калашников': {1: True, 2: False, 3: True, 4: True, 5: False, 6: True, 7: True, 8: False, 9: True, 10: True}, 'Никита Корсаков': {1: False, 2: True, 3: True, 4: True, 5: False, 6: True, 7: True, 8: True, 9: False, 10: False}, 'Варвара Котлячкова': {1: False, 2: False, 3: True, 4: True, 5: True, 6: True, 7: True, 8: False, 9: False, 10: False}, 'Татьяна Левкович': {1: False, 2: False, 3: True, 4: True, 5: True, 6: True, 7: True, 8: True, 9: False, 10: True}, 'Рауль Масимов': {1: False, 2: True, 3: True, 4: False, 5: False, 6: False, 7: False, 8: False, 9: True, 10: True}, 'Виктория Нахина': {1: True, 2: False, 3: True, 4: False, 5: False, 6: True, 7: True, 8: False, 9: True, 10: True}, 'Матвей Некрасов': {1: False, 2: True, 3: True, 4: True, 5: True, 6: False, 7: False, 8: False, 9: True, 10: False}, 'Елизавета Нечаева': {1: False, 2: False, 3: True, 4: False, 5: True, 6: True, 7: True, 8: True, 9: False, 10: True}, 'Надежда Попцова': {1: True, 2: False, 3: False, 4: True, 5: True, 6: True, 7: True, 8: True, 9: True, 10: True}, 'Матвей Сироткин': {1: True, 2: True, 3: True, 4: False, 5: True, 6: False, 7: False, 8: True, 9: False, 10: False}, 'Виктория Смирнова': {1: False, 2: True, 3: False, 4: True, 5: False, 6: True, 7: True, 8: True, 9: True, 10: False}, 'Михаил Соколов': {1: True, 2: False, 3: False, 4: True, 5: False, 6: False, 7: True, 8: True, 9: True, 10: True}, 'Дмитрий Стулихин': {1: True, 2: True, 3: True, 4: False, 5: True, 6: False, 7: True, 8: False, 9: True, 10: True}, 'Ксения Сырова': {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: False, 8: False, 9: True, 10: False}, 'Лилия Трофимова': {1: True, 2: True, 3: False, 4: True, 5: True, 6: False, 7: True, 8: False, 9: False, 10: False}, 'Анастасия Хромова': {1: False, 2: False, 3: False, 4: True, 5: True, 6: False, 7: False, 8: True, 9: True, 10: False}, 'Андрей Цветков': {1: False, 2: False, 3: True, 4: True, 5: False, 6: False, 7: False, 8: True, 9: False, 10: True}, 'Василиса Чернова': {1: True, 2: False, 3: True, 4: False, 5: True, 6: True, 7: True, 8: False, 9: True, 10: True}}
# t1 = {'Софья Андреева': 3, 'Дмитрий Афанасов': 3, 'Матвей Бокарев': 2, 'Елисей Бугров': 3, 'Маргарита Горовая': 2, 'Тимофей Гусев': 3, 'Вячеслав Калашников': 3, 'Никита Корсаков': 3, 'Варвара Котлячкова': 2, 'Татьяна Левкович': 3, 'Рауль Масимов': 2, 'Виктория Нахина': 3, 'Матвей Некрасов': 2, 'Елизавета Нечаева': 3, 'Надежда Попцова': 4, 'Матвей Сироткин': 2, 'Виктория Смирнова': 3, 'Михаил Соколов': 3, 'Дмитрий Стулихин': 3, 'Ксения Сырова': 3, 'Лилия Трофимова': 2, 'Анастасия Хромова': 2, 'Андрей Цветков': 2, 'Василиса Чернова': 3}
#
#
#
# path = r'D:\pythonProject\Insighter II\Распечатка КЖ 8а Информатика П1.xlsx'
# total = 30
#
# st = StatisticsParser(tasks_dict1, res_dict, path)
# st = StatisticsParser(t, t1, path)

# print(st.get_average())
# print(st.get_median())
# print(st.get_grades_distribution())
# print(st.get_task_distribution())
# print(st.convertage_to_percentages(total))
# print(st.get_student_distribution())
# print(st.get_the_best_the_worst_students_results())
# print(st.get_file_results())
# print(st.get_strong_weak_students())
# print(st.get_distribution_tasks_strong_weak_students())
# dctjh = {1: 90.0, 2: 40.0, 3: 13.33, 4: 100.00, 5: 30.0, 6: 30.0, 7: 78.33, 8: 30.0, 9: 3.0, 10: 55.33}
# print(st.get_recomdendations_standart(dctjh))
# print(*st.get_recomdendations_deep(st.get_distribution_tasks_strong_weak_students(), st.get_strong_weak_students()[1]), sep='\n')
# print(st.get_brief_conclusion(st.grades_dict, st.convertage_to_percentages(total)))
# p1 = st.grades_dict
# p2 = st.get_distribution_tasks_strong_weak_students()
# p3 = st.get_strong_weak_students()[0]
# p4 = st.tasks_dict
# p5 = st.get_strong_weak_students()[1]
# print(st.get_extended_analysis(p1, p2, p3, p4, p5))

