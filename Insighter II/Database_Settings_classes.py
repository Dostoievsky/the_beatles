import sqlite3
import os
from pathlib import Path
import json

SYSTEM_DIR = 'system_files'
DB_PATH = os.path.join(SYSTEM_DIR, 'insighter.db')

list_of_json_files = [
    'sys.json',
    'log.json',
    'patterns.json',
    'settings.json'
]

def print_menu(strings):
    dct = {}
    for i, string in enumerate(strings, 1):
        print(f"{string}[{i}]")
        dct[i] = string
    chose = input('Введите номер: ')
    try:
        return dct[int(chose)], chose
    except:
        print('Такого значения не существует.')


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

    def close(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY,
                class_name TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                class_id INTEGER,
                name TEXT,
                surname TEXT,
                telegram_id INTEGER
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS works (
            id INTEGER PRIMARY KEY,
            work_name TEXT,
            work_date TEXT,
            class_id INTEGER,
            answer_data TEXT,
            grades_data TEXT,
            status TEXT,
            absents TEXT
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY,
                submission_id INTEGER,
                grade INTEGER
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY,
                work_id INTEGER,
                student_id INTEGER,
                student_answer TEXT
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
        print('save_work')
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
        print('сработала save_work')
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

    def get_students_of_class(self, class_name):
        class_id = self.get_or_create_class(class_name)

        self.cursor.execute("""
            SELECT id FROM students
            WHERE class_id = ?
        """, (class_id,))

        return {row[0] for row in self.cursor.fetchall()}

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

        for full_name in absents:
            name, surname = self.parse_name(full_name)

            self.cursor.execute("""
                SELECT id FROM students
                WHERE class_id = ? AND name = ? AND surname = ?
            """, (class_id, name, surname))

            row = self.cursor.fetchone()

            if row is None:
                # ученика нет — добавляем
                self.cursor.execute("""
                    INSERT INTO students (class_id, name, surname)
                    VALUES (?, ?, ?)
                """, (class_id, name, surname))
                student_id = self.cursor.lastrowid
            else:
                student_id = row[0]

            absent_ids.add(student_id)

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

    def get_works_by_class(self, class_name):
        self.root_db.cursor.execute('''
            SELECT *
            FROM classes JOIN works ON classes.id = works.class_id
            WHERE classes.class_name = ?
        ''', (class_name,))
        return self.root_db.cursor.fetchall()

    @staticmethod
    def parse_names(data_tuple):
        lst = []
        for row in data_tuple:
            lst.append(f'{row[3]} за {row[4]}')
        return lst


db = Database()
db.connect()

dbc = DatabaseChecking(db)
print(dbc.parse_names(()))

db.close()