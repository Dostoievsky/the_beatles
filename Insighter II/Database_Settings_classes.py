import sqlite3
import os
from pathlib import Path
import json
from checking import *

SYSTEM_DIR = 'system_files'
DB_PATH = os.path.join(SYSTEM_DIR, 'insighter.db')

list_of_json_files = [
    'sys.json',
    'log.json',
    'patterns.json',
    'settings.json'
]

def print_menu(strings, text=None, message='Папка пуста.'):
    if not strings:
        print(message)
        print()
        return None, None
    if text:
        print(text)
    dct = {}
    for i, string in enumerate(strings, 1):
        print(f"{string}[{i}]")
        dct[i] = string
    chose = input('Введите номер: ')
    print()
    try:
        return dct[int(chose)], chose
    except:
        print('Такого значения не существует.')
        return None, None

def is_first_launch():
    if not os.path.exists(SYSTEM_DIR):
        return True

    if not os.path.exists(DB_PATH):
        return True

    files = set(os.listdir(SYSTEM_DIR))
    return not set(list_of_json_files).issubset(files)


class Database:
    def __init__(self, db_path = r"system_files/insighter.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")

    def close(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY,
                class_name TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                class_id INTEGER NOT NULL,
                name TEXT,
                surname TEXT,
                telegram_id INTEGER,
                FOREIGN KEY (class_id)
                    REFERENCES classes(id)
                    ON DELETE CASCADE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS works (
                id INTEGER PRIMARY KEY,
                work_name TEXT,
                work_date TEXT,
                class_id INTEGER NOT NULL,
                answer_data TEXT,
                grades_data TEXT,
                status TEXT,
                absents TEXT,
                FOREIGN KEY (class_id)
                    REFERENCES classes(id)
                    ON DELETE CASCADE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY,
                work_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                student_answer TEXT,
                FOREIGN KEY (work_id)
                    REFERENCES works(id)
                    ON DELETE CASCADE,
                FOREIGN KEY (student_id)
                    REFERENCES students(id)
                    ON DELETE CASCADE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY,
                submission_id INTEGER NOT NULL,
                grade INTEGER,
                FOREIGN KEY (submission_id)
                    REFERENCES submissions(id)
                    ON DELETE CASCADE
            )
        """)

        self.conn.commit()

    def initialize(self):
        self.connect()
        self.create_tables()
        self.close()



    def get_or_create_class(self, class_name):
        self.cursor.execute(
            "SELECT id FROM classes WHERE class_name = ?",
            (class_name,)
        )
        result = self.cursor.fetchone()

        if result:
            return result[0]

        self.cursor.execute(
            "INSERT INTO classes (class_name) VALUES (?)",
            (class_name,)
        )
        self.conn.commit()

        return self.cursor.lastrowid

    def save_work(self, work_name, work_date, class_name, answer_data, grades_data, status):
        class_id = self.get_or_create_class(class_name)

        self.cursor.execute("""
            INSERT INTO works (
                work_name, work_date, class_id,
                answer_data, grades_data, status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            work_name,
            work_date,
            class_id,
            answer_data,
            grades_data,
            status
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    @staticmethod
    def parse_name(full_name: str):
        parts = full_name.strip().split()
        if len(parts) >= 2:
            return parts[0], parts[1]
        else:
            return parts[0], ""

    def add_student(self, class_id, name, surname):
        self.cursor.execute("""
            INSERT INTO students (class_id, name, surname)
            VALUES (?, ?, ?)
        """, (class_id, name, surname))

    def add_students_from_list(self, class_name, students_list):
        class_id = self.get_or_create_class(class_name)

        for full_name in students_list:
            name, surname = self.parse_name(full_name)

            self.cursor.execute("""
                SELECT id FROM students
                WHERE class_id = ? AND name = ? AND surname = ?
            """, (class_id, name, surname))

            if self.cursor.fetchone() is None:
                self.add_student(class_id, name, surname)

        self.conn.commit()

    def add_submission(self, work_id, student_id, student_answer):
        self.cursor.execute("""
            INSERT INTO submissions (work_id, student_id, student_answer)
            VALUES (?, ?, ?)
        """, (work_id, student_id, student_answer))

    def add_submissions_from_answers(self, class_name, work_id, answers):
        class_id = self.get_or_create_class(class_name)

        for full_name, answer in answers.items():
            name, surname = self.parse_name(full_name)
            answer_str  = ",".join(answer)

            self.cursor.execute("""
                SELECT id FROM students
                WHERE class_id = ? AND name = ? AND surname = ?
            """, (class_id, name, surname))

            row = self.cursor.fetchone()
            if row is None:
                continue

            student_id = row[0]

            self.add_submission(work_id, student_id, answer_str)

        self.conn.commit()

    def get_students_of_class(self, class_name, flag='id'):
        class_id = self.get_or_create_class(class_name)
        if flag == 'id':
            self.cursor.execute("""
                SELECT id FROM students
                WHERE class_id = ?
            """, (class_id,))
            return {row[0] for row in self.cursor.fetchall()}
        elif flag == 'names':
            self.cursor.execute("""
                SELECT name, surname FROM students
                WHERE class_id = ?
            """, (class_id,))
            return {f"{row[0]} {row[1]}" for row in self.cursor.fetchall()}


    def get_students_with_submission(self, work_id):
        self.cursor.execute("""
            SELECT student_id FROM submissions
            WHERE work_id = ?
        """, (work_id,))

        return {row[0] for row in self.cursor.fetchall()}

    def set_absents_for_work(self, work_id, class_name, absents):

        if not absents:
            self.cursor.execute("""
                UPDATE works
                SET absents = NULL
                WHERE id = ?
            """, (work_id,))
            self.conn.commit()
            return

        class_id = self.get_or_create_class(class_name)
        absent_ids = set()
        if isinstance(list(absents)[0], str):
            for full_name in absents:
                name, surname = self.parse_name(full_name)

                self.cursor.execute("""
                    SELECT id FROM students
                    WHERE class_id = ? AND name = ? AND surname = ?
                """, (class_id, name, surname))

                row = self.cursor.fetchone()

                if row is None:
                    self.cursor.execute("""
                        INSERT INTO students (class_id, name, surname)
                        VALUES (?, ?, ?)
                    """, (class_id, name, surname))
                    student_id = self.cursor.lastrowid
                else:
                    student_id = row[0]

                absent_ids.add(student_id)
        else:
            absent_ids = absents
        absents_value = ",".join(map(str, sorted(absent_ids)))

        self.cursor.execute("""
            UPDATE works
            SET absents = ?
            WHERE id = ?
        """, (absents_value, work_id))

        self.conn.commit()


class Settings:
    def __init__(self, path=r'system_files\settings.json'):
        self._path = os.path.join(os.getcwd(), path)
        self._data = self._load()

    def _load(self):
        with open(self._path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @property
    def show_warnings(self):
        return self._data.get('show_warnings', False)

    @property
    def automatically_file_opening(self):
        return self._data.get('automatically_file_opening', False)

    @property
    def saving_all_files_in_one_folder(self):
        return self._data.get('saving_all_files_in_one_folder', False)

    @property
    def developer_mode(self):
        return self._data.get('developer_mode', False)

    @property
    def saving_statistics_in_unque_files(self):
        return self._data.get('saving_statistics_in_unque_files', False)

    @property
    def format_by_default(self):
        return self._data.get('format_by_default', 'txt')

    @property
    def alsways_build_the_graphics(self):
        return self._data.get('alsways_build_the_graphics', False)

    @property
    def encoding(self):
        return self._data.get('encoding', ["utf-8", "utf-8-sig"])



class DatabaseChecking:
    def __init__(self, root_db):
        self.root_db = root_db

    def get_classes(self):
        self.root_db.cursor.execute('''
            SELECT * FROM classes
        ''')
        data_class = self.root_db.cursor.fetchall()
        if data_class:
            return list(map(lambda x: x[1], data_class))
        return

    def get_class_id_by_name(self, class_name: str) -> int | None:
        cur = self.root_db.conn.cursor()
        cur.execute(
            "SELECT id FROM classes WHERE class_name = ?",
            (class_name,)
        )
        row = cur.fetchone()
        return row[0] if row else None

    def get_works_by_class(self, class_name, status='raw'):
        if status == '*':
            self.root_db.cursor.execute('''
                SELECT *
                FROM classes JOIN works ON classes.id = works.class_id
                WHERE classes.class_name = ?
            ''', (class_name,))
        else:
            self.root_db.cursor.execute('''
                SELECT *
                FROM classes JOIN works ON classes.id = works.class_id
                WHERE classes.class_name = ? and works.status = ?
            ''', (class_name, status))
        return self.root_db.cursor.fetchall()

    def get_work_id_by_class_and_name(self, class_name, work_name):
        self.root_db.cursor.execute("""
            SELECT works.id
            FROM works
            JOIN classes ON works.class_id = classes.id
            WHERE classes.class_name = ?
              AND works.work_name = ?
        """, (class_name, work_name))

        row = self.root_db.cursor.fetchone()
        if not row:
            raise ValueError(
                f"Работа '{work_name}' не найдена в классе '{class_name}'"
            )

        return row[0]

    def set_work_status_by_name(self, class_name, work_name, status):
        class_id = self.get_class_id(class_name)
        if class_id is None:
            raise ValueError(f"Класс '{class_name}' не найден")

        work_id = self.get_work_id(class_id, work_name)
        if work_id is None:
            raise ValueError(f"Работа '{work_name}' не найдена")

        self.root_db.cursor.execute("""
            UPDATE works
            SET status = ?
            WHERE id = ?
        """, (status, work_id))

        self.root_db.conn.commit()

    @staticmethod
    def parse_names(data_tuple):
        lst = []
        for row_tpl in data_tuple:
            lst.append(f'{row_tpl[3]} за {row_tpl[4]}')
        return lst

    def get_all_data(self, class_name, work_name_entered, status='raw'):
        self.root_db.cursor.execute('''
            SELECT id
            FROM classes
            WHERE class_name = ?
        ''', (class_name,))
        row = self.root_db.cursor.fetchone()
        print('CLASS ROW:', row)
        class_id = row[0]

        self.root_db.cursor.execute('''
            SELECT *
            FROM works
            JOIN submissions ON works.id = submissions.work_id
            JOIN students ON submissions.student_id = students.id
            WHERE works.class_id = ?
              AND works.work_name = ?
              AND works.status = ?
        ''', (class_id, work_name_entered, status))

        rows = self.root_db.cursor.fetchall()

        self.root_db.cursor.execute('''
            SELECT absents
            FROM works
            WHERE class_id = ?
              AND work_name = ?
              AND status = ?
        ''', (class_id, work_name_entered, status))

        return rows

    def get_class_id(self, class_name):
        self.root_db.cursor.execute("""
            SELECT id
            FROM classes
            WHERE class_name = ?
        """, (class_name,))
        row = self.root_db.cursor.fetchone()
        return row[0] if row else None

    def get_work_id(self, class_id: int, work_name: str) -> int | None:
        self.root_db.cursor.execute("""
            SELECT id
            FROM works
            WHERE class_id = ? AND work_name = ?
        """, (class_id, work_name))
        row = self.root_db.cursor.fetchone()
        return row[0] if row else None

    def save_final_results(self, class_name: str, work_name: str, final_dict: dict):
        # 1. получаем class_id
        class_id = self.get_class_id(class_name)
        if class_id is None:
            raise ValueError(f"Класс '{class_name}' не найден")

        # 2. получаем work_id
        work_id = self.get_work_id(class_id, work_name)
        if work_id is None:
            raise ValueError(f"Работа '{work_name}' не найдена для класса '{class_name}'")

        # 3. пишем результаты
        for student_id, info in final_dict.items():
            grade = info.get('grade')

            self.root_db.cursor.execute("""
                SELECT id
                FROM submissions
                WHERE work_id = ? AND student_id = ?
            """, (work_id, student_id))

            row = self.root_db.cursor.fetchone()
            if row is None:
                print(f"⚠ Нет submission для student_id={student_id}")
                continue

            submission_id = row[0]

            self.root_db.cursor.execute("""
                INSERT OR REPLACE INTO results (submission_id, grade)
                VALUES (?, ?)
            """, (submission_id, grade))

        self.root_db.conn.commit()

# db = Database()
# db.connect()
#
# dbc = DatabaseChecking(db)
# print(dbc.parse_names(dbc.get_works_by_class('9в')))
# print(dbc.get_classes())
# data, absents = dbc.get_all_data('9в', 'Тканая работа 2')
# print(data)
# checking = Checking(data, absents)
# checking.parse_big_data()
# print(checking.students_dct)
# print(checking.date_work_name)
# print(checking.absents)
# print(checking.right_answers)
# print(checking.grades)
# print(checking.checking_works())
# dct = {'Муратова Аиша': (6, None), 'Беляева Александра': (7, None), 'Большакова Алина': (7, None), 'Герасимова Анна': (7, None), 'Еремин Владимир': (7, None), 'Басов Григорий': (9, None), 'Иванов Даниил': (8, None), 'Кондратов Даниил': (9, None), 'Королева Дарья': (8, None), 'Никонова Ева': (6, None), 'Федорова Елизавета': (9, None), 'Воробьева Кира': (6, None), 'Максимова Ксения': (4, None), 'Никифорова Ксения': (8, None), 'Калинин Лев': (7, None), 'Назаров Леонид': (6, None), 'Евдокимов Максим': (9, None), 'Кузнецов Максим': (7, None), 'Белова Мария': (8, None), 'Соколова Мария': (10, None), 'Лебедева Марьям': (10, None), 'Литвинова Милана': (8, None), 'Савельева Мирослава': (6, None), 'Смирнов Михаил': (8, None), 'Второй Николай': (9, None), 'Сергеева Таисия': (4, None), 'Аксенов Тимур': (8, None), 'Филатов Фёдор': (9, None), 'Яковлев Фёдор': (7, None)}
# checking.absents = 'Муратова Аиша,Вася Пупкин'
# print(checking.add_absents(dct, db, '9в'))
# db.close()