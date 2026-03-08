import statistics
from collections import Counter, defaultdict
import pandas as pd
import re


class StatisticsParser:
    def __init__(self, tasks_dict, grades_dict, file_name=None):
        self.tasks_dict = tasks_dict
        self.grades_dict = grades_dict
        self.file_name = file_name

    @staticmethod
    def fix_fio_spacing(text):
        fixed_text = re.sub(r'([а-яё])(?=[А-ЯЁ])', r'\1 ', text)
        return fixed_text.strip()

    def get_file_results(self):
        if not self.file_name:
            return None
        students_dict = self.get_students_dict()
        return {self.fix_fio_spacing(k): v for k, v in students_dict.items()}


    def get_students_dict(self):
        df = pd.read_excel(self.file_name, header=None, engine='openpyxl')
        students_data = {}

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
        return round(statistics.mean(list(self.grades_dict.values())), 2)


    def get_median(self):
        return statistics.median(list(self.grades_dict.values()))


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


    def get_the_best_the_worst_students_results(self):
        distbt = self.get_student_distribution()
        sorted_dict_best = dict(sorted(distbt.items(), key=lambda item: item[1], reverse=True))
        best_students = self.get_first_group(sorted_dict_best)
        sorted_dict_worst = dict(sorted(distbt.items(), key=lambda item: item[1]))
        worst_students = self.get_first_group(sorted_dict_worst)
        return best_students, worst_students


    def get_strong_weak_students(self):
        dct = {}
        students_avg_dict = self.get_file_results()

        for student, data in students_avg_dict.items():
            strong_index = data['avg_score']
            total_grades = data['total_grades'] if data['total_grades'] < 6 else 6

            if strong_index >= 4.85 and total_grades == 6:
                dct[student] = 5
            elif strong_index >= 4.5 and total_grades in [3, 4, 5, 6]:
                dct[student] = 4
            elif strong_index >= 3.7 and total_grades in [3, 4, 5, 6]:
                dct[student] = 3
            elif strong_index >= 3.0 and total_grades in [3, 4, 5, 6]:
                dct[student] = 2
            elif strong_index >= 2.0 and total_grades in [3, 4, 5, 6]:
                dct[student] = 1
            else:
                dct[student] = 0

        counts = Counter(dct.values())
        total_distr = {i: counts.get(i, 0) for i in range(6)}

        return dct, total_distr


    def get_distribution_tasks_strong_weak_students(self):
        students_avg_distr = self.get_strong_weak_students()[0]
        task_distr = self.tasks_dict
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
        total_all = sum(group_counts.values())

        if total_all == 0:
            return ["Нет данных об учениках"]

        if group_counts.get(0, 0) > total_all / 2:
            return None

        weak_groups = [1, 2]
        med_groups = [3]
        strong_groups = [4, 5]

        count_weak = sum(group_counts.get(g, 0) for g in weak_groups)
        count_med = sum(group_counts.get(g, 0) for g in med_groups)
        count_strong = sum(group_counts.get(g, 0) for g in strong_groups)

        recommendations = []

        for task_id, stats in tasks_stats.items():
            solved_0 = stats.get(0, 0)
            solved_weak = sum(stats.get(g, 0) for g in weak_groups)
            solved_med = sum(stats.get(g, 0) for g in med_groups)
            solved_strong = sum(stats.get(g, 0) for g in strong_groups)

            solved_total = solved_0 + solved_weak + solved_med + solved_strong

            p_total = round((solved_total / total_all) * 100)
            p_weak_med = round(((solved_weak + solved_med) / total_all) * 100)
            p_strong = round((solved_strong / total_all) * 100)

            stats_str = f"Решили: {p_total}% класса, из которых {p_weak_med}% слабых и средних и {p_strong}% сильных."

            rate_weak = (solved_weak / count_weak) if count_weak > 0 else 0
            rate_med = (solved_med / count_med) if count_med > 0 else 0
            rate_strong = (solved_strong / count_strong) if count_strong > 0 else 0

            # 1. Аномалия (Списывание)
            if rate_weak > rate_strong + 0.3 and rate_weak > 0.5:
                rec = "Внимание: подозрение на списывание или некорректную формулировку. Сильные ученики справились хуже слабых."
            # 2. Аномалия (Подвох)
            elif rate_strong < rate_med - 0.2:
                rec = "Внимание: задание 'с подвохом'. Самые сильные ученики ошибаются чаще средних. Проверьте формулировку."
            # 3. Слишком легкое
            elif (solved_total / total_all) > 0.85:
                rec = "Задание слишком легкое. Почти все группы справились. Не подходит для дифференциации."
            # 4. Слишком сложное
            elif (solved_total / total_all) < 0.1:
                rec = "Задание практически нерешаемое для текущего состава. Требуется разбор темы с нуля."
            # 5. Идеальное дифференцирующее
            elif rate_strong > 0.7 and rate_weak < 0.3:
                rec = "Отличное задание. Четко разделяет сильных и слабых учеников. Рекомендуется для контрольных."
            # 6. Сложное, но качественное
            elif rate_strong > 0.4 and rate_weak < 0.15:
                rec = "Задание повышенной сложности. Подходит для отбора претендентов на '5'."
            # 7. Среднее задание
            elif 0.3 <= (solved_total / total_all) <= 0.75:
                rec = "Стандартное задание средней сложности. Хорошо подходит для текущей проверки знаний."
            # 8. Нет данных
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
        print(avg_grade, 'rrnfekljnerjof')
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
            if grade > idx and idx != 0:
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


tasks_dict1 = {
    'Андреева Софья': {1: True, 2: False, 3: True, 4: True, 5: False, 6: True, 7: False, 8: True, 9: False, 10: True},
    'Афанасов Дмитрий': {1: False, 2: True, 3: False, 4: True, 5: True, 6: False, 7: True, 8: False, 9: True, 10: False},
    'Гусев Тимофей': {1: True, 2: True, 3: False, 4: False, 5: True, 6: True, 7: False, 8: True, 9: False, 10: True},
    'Корсаков Никита': {1: False, 2: False, 3: True, 4: True, 5: False, 6: False, 7: True, 8: True, 9: True, 10: False},
    'Котлячкова Варвара': {1: True, 2: False, 3: True, 4: False, 5: True, 6: False, 7: True, 8: False, 9: True, 10: True},
    'Левкович Татьяна': {1: False, 2: True, 3: True, 4: True, 5: False, 6: True, 7: False, 8: False, 9: True, 10: False},
    'Нахина Виктория': {1: True, 2: False, 3: False, 4: True, 5: True, 6: True, 7: False, 8: True, 9: False, 10: True},
    'Некрасов Матвей': {1: False, 2: True, 3: True, 4: False, 5: False, 6: True, 7: True, 8: True, 9: False, 10: True},
    'Нечаева Елизавета': {1: True, 2: True, 3: False, 4: True, 5: False, 6: False, 7: True, 8: False, 9: True, 10: False},
    'Попцова Надежда': {1: False, 2: False, 3: True, 4: False, 5: True, 6: True, 7: True, 8: False, 9: False, 10: True},
    'Сироткин Матвей': {1: True, 2: True, 3: True, 4: False, 5: False, 6: False, 7: False, 8: True, 9: True, 10: True},
    'Смирнова Виктория': {1: False, 2: True, 3: False, 4: True, 5: True, 6: True, 7: False, 8: False, 9: False, 10: False},
    'Соколов Михаил': {1: True, 2: False, 3: True, 4: True, 5: False, 6: True, 7: True, 8: True, 9: False, 10: True},
    'Стулихин Дмитрий': {1: False, 2: True, 3: False, 4: False, 5: True, 6: False, 7: True, 8: True, 9: True, 10: False},
    'Сырова Ксения': {1: True, 2: False, 3: True, 4: True, 5: True, 6: False, 7: False, 8: False, 9: True, 10: True},
    'Цветков Андрей': {1: False, 2: True, 3: True, 4: False, 5: False, 6: True, 7: True, 8: True, 9: False, 10: False},
    'Чернова Василиса': {1: True, 2: False, 3: False, 4: True, 5: True, 6: False, 7: True, 8: False, 9: True, 10: True}
}
res_dict = {
    'Андреева Софья': 4,  # 6 True
    'Афанасов Дмитрий': 3,  # 5 True
    'Гусев Тимофей': 4,  # 6 True
    'Корсаков Никита': 3,  # 4 True
    'Котлячкова Варвара': 4,  # 6 True
    'Левкович Татьяна': 3,  # 4 True
    'Нахина Виктория': 4,  # 6 True
    'Некрасов Матвей': 3,  # 5 True
    'Нечаева Елизавета': 3,  # 4 True
    'Попцова Надежда': 3,  # 5 True
    'Сироткин Матвей': 4,  # 6 True
    'Смирнова Виктория': 3,  # 4 True
    'Соколов Михаил': 4,  # 7 True
    'Стулихин Дмитрий': 3,  # 5 True
    'Сырова Ксения': 4,  # 6 True
    'Цветков Андрей': 3,  # 5 True
    'Чернова Василиса': 4  # 6 True
}

path = r'D:\pythonProject\Insighter II\Распечатка КЖ 8а Информатика П1.xlsx'
total = 30

st = StatisticsParser(tasks_dict1, res_dict, path)
print(st.get_average())
print(st.get_median())
print(st.get_grades_distribution())
print(st.get_task_distribution())
print(st.convertage_to_percentages(total))
print(st.get_student_distribution())
print(st.get_the_best_the_worst_students_results())
print(st.get_file_results())
print(st.get_strong_weak_students())
print(st.get_distribution_tasks_strong_weak_students())
dctjh = {1: 90.0, 2: 40.0, 3: 13.33, 4: 100.00, 5: 30.0, 6: 30.0, 7: 78.33, 8: 30.0, 9: 3.0, 10: 55.33}
print(st.get_recomdendations_standart(dctjh))
print(*st.get_recomdendations_deep(st.get_distribution_tasks_strong_weak_students(), st.get_strong_weak_students()[1]), sep='\n')
print(st.get_brief_conclusion(st.grades_dict, st.convertage_to_percentages(total)))
p1 = st.grades_dict
p2 = st.get_distribution_tasks_strong_weak_students()
p3 = st.get_strong_weak_students()[0]
p4 = st.tasks_dict
p5 = st.get_strong_weak_students()[1]
print(st.get_extended_analysis(p1, p2, p3, p4, p5))

