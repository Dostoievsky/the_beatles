import csv
from itertools import zip_longest

class Checking:
    def __init__(self, big_data):
        self.big_data = big_data
        self.absents = ''
        self.students_dct = {}
        self.right_answers = ''
        self.grades = ''
        self.date_work_name = ''

    def parse_big_data(self):
        for row in self.big_data:
            student_id = row[10]
            work_name = row[1]
            date = row[2]
            self.right_answers = row[4]
            self.absents = row[7]
            self.grades = row[5]
            answers = row[11]
            name = row[14]
            surname = row[15]
            tg_id = row[16]

            self.students_dct[student_id] = {
                "name": name,
                "surname": surname,
                "answers": answers,
                "tg_id": tg_id
            }

            self.date_work_name = f'{work_name} за {date}'

    def checking_works(self):
        result = {}
        right = self.right_answers.split(',')

        for student_id, data in self.students_dct.items():
            count = 0
            stat_dct = {}

            student_answers = data["answers"].split(',')

            for q_id, (st, rt) in enumerate(zip_longest(student_answers, right, fillvalue=""), 1):
                st_clean = st.strip()
                rt_clean = rt.strip()

                if st_clean == rt_clean:
                    count += 1
                    stat_dct[q_id] = True
                else:
                    stat_dct[q_id] = False

            result[student_id] = {
                "score": count,
                "tg_id": data["tg_id"],
                "name": data["name"],
                "surname": data["surname"],
                "stat": stat_dct
            }

        return result

    def get_absents(self, db):
        if not self.absents:
            return []

        absents_ids = list(map(int, self.absents.split(',')))

        placeholders = ','.join(['?'] * len(absents_ids))

        db.connect()
        db.cursor.execute(
            f'''
            SELECT id, name, surname, telegram_id
            FROM students
            WHERE id IN ({placeholders})
            ''',
            absents_ids
        )
        rows = db.cursor.fetchall()
        db.close()

        return list(rows)

    def get_grades(self, checked_data):
        dict_grades, students_dict_grades = {}, {}
        for pair in self.grades.split(','):
            key, value = map(lambda x: int(x.strip()), pair.split('-'))
            dict_grades[key] = value
        for student_id, data in checked_data.items():
            try:
                grade = dict_grades[data["score"]]
            except KeyError:
                raise ValueError(f"Оценка для количества правильных ответов {data['score']} не найдена.")
            students_dict_grades[student_id] = data | {"grade": grade}
        return students_dict_grades

    @staticmethod
    def sort_key_desc(item):
        key, value = item
        if isinstance(value, int):
            return 0, -value
        else:
            return 1, value

    @staticmethod
    def sort_key_asc(item):
        key, value = item
        if isinstance(value, int):
            return 0, value
        else:
            return 1, value

    def sort_data(self, dict_for_write, mode):
        if mode == '1':
            return dict_for_write
        elif mode == '2':
            return dict(sorted(dict_for_write.items(), key=self.sort_key_desc))
        elif mode == '3':
            return dict(sorted(dict_for_write.items(), key=self.sort_key_asc))
        else:
            return dict(sorted(dict_for_write.items(), key=lambda item: item[0]))

    def save_file_txt(self, path, sorted_dict_for_write):
        with open(path, 'w', encoding='utf-8') as file:
            print(self.date_work_name, file=file)
            print(file=file)
            for k, v in sorted_dict_for_write.items():
                print(f'{k} - {v}', file=file)

    def save_file_csv(self, path, sorted_dict_for_write):
        with open(path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.date_work_name])
            for k, v in sorted_dict_for_write.items():
                writer.writerow([k, v])