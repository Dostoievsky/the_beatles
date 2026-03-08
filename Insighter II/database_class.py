import sqlite3
from typing import Optional, List, Tuple, Dict, Set, Literal
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

class Database:
    def __init__(self, db_path: str = r"system_files/insighter.db") -> None:
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    @staticmethod
    def parse_name(full_name: str):
        parts = full_name.strip().split()
        if len(parts) >= 2:
            return parts[0], parts[1]
        else:
            return parts[0], ""


    def connect(self) -> None:
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")


    def close(self) -> None:
        if self.conn:
            self.conn.close()


    def create_tables(self) -> None:
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

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS task_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                submission_id INTEGER NOT NULL,
                task_id INTEGER NOT NULL,
                is_correct INTEGER NOT NULL,
                FOREIGN KEY (submission_id)
                    REFERENCES submissions(id)
                    ON DELETE CASCADE
            )
        """)

        self.conn.commit()


    def initialize(self) -> None:
        self.connect()
        self.create_tables()
        self.close()


    def get_class_id(self, class_name: str) -> Optional[int]:
        self.cursor.execute(
            "SELECT id FROM classes WHERE class_name = ?",
            (class_name,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None


    def get_or_create_class(self, class_name: str) -> int:
        class_id = self.get_class_id(class_name)
        if class_id:
            return class_id

        self.cursor.execute(
            "INSERT INTO classes (class_name) VALUES (?)",
            (class_name,)
        )
        self.conn.commit()
        return self.cursor.lastrowid


    def get_classes(self) -> List[str]:
        self.cursor.execute("SELECT class_name FROM classes")
        rows = self.cursor.fetchall()
        return [row[0] for row in rows]


    def get_work_id(self, class_id: int, work_name: str) -> Optional[int]:
        self.cursor.execute(
            "SELECT id FROM works WHERE class_id = ? AND work_name = ?",
            (class_id, work_name)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None


    def get_work_id_by_class_and_name(self, class_name: str, work_name: str) -> int:
        class_id = self.get_class_id(class_name)
        if class_id is None:
            raise ValueError(f"Класс '{class_name}' не найден")

        work_id = self.get_work_id(class_id, work_name)
        if work_id is None:
            raise ValueError(f"Работа '{work_name}' не найдена")

        return work_id


    def get_works_by_class(self, class_name: str, status: str = 'raw') -> List[Tuple]:

        if status == '*':
            self.cursor.execute("""
                SELECT *
                FROM classes
                JOIN works ON classes.id = works.class_id
                WHERE classes.class_name = ?
            """, (class_name,))
        else:
            self.cursor.execute("""
                SELECT *
                FROM classes
                JOIN works ON classes.id = works.class_id
                WHERE classes.class_name = ?
                  AND works.status = ?
            """, (class_name, status))

        return self.cursor.fetchall()


    def set_work_status_by_name(self, class_name: str, work_name: str, status: str) -> None:

        work_id = self.get_work_id_by_class_and_name(class_name, work_name)

        self.cursor.execute("""
            UPDATE works
            SET status = ?
            WHERE id = ?
        """, (status, work_id))

        self.conn.commit()


    @staticmethod
    def parse_names(data_tuple):
        lst = []
        for row_tpl in data_tuple:
            lst.append(f'{row_tpl[3]} за {row_tpl[4]}')
        return lst


    def find_student_id_by_name(self, class_name: str, name: str, surname: str) -> Optional[int]:

        class_id = self.get_class_id(class_name)
        if class_id is None:
            return None

        name_l = name.strip().lower()
        surname_l = surname.strip().lower()

        self.cursor.execute("""
            SELECT id
            FROM students
            WHERE class_id = ?
              AND (
                (LOWER(TRIM(name)) = ? AND LOWER(TRIM(surname)) = ?)
                OR (LOWER(TRIM(name)) = ? AND LOWER(TRIM(surname)) = ?)
              )
        """, (class_id, name_l, surname_l, surname_l, name_l))

        row = self.cursor.fetchone()
        return row[0] if row else None


    def get_students_of_class(self, class_name: str, mode: Literal['id', 'names'] = 'id') -> Set:

        class_id = self.get_or_create_class(class_name)

        if mode == 'id':
            self.cursor.execute(
                "SELECT id FROM students WHERE class_id = ?",
                (class_id,)
            )
            return {row[0] for row in self.cursor.fetchall()}

        self.cursor.execute(
            "SELECT name, surname FROM students WHERE class_id = ?",
            (class_id,)
        )
        return {f"{row[0]} {row[1]}" for row in self.cursor.fetchall()}


    def get_students_with_telegram_ids(self, class_name: str) -> List[Tuple[int, Optional[int]]]:

        class_id = self.get_or_create_class(class_name)

        self.cursor.execute("""
            SELECT id, telegram_id
            FROM students
            WHERE class_id = ?
        """, (class_id,))

        return self.cursor.fetchall()


    def save_final_results(self,class_name: str, work_name: str, final_dict: Dict[int, Dict]) -> None:

        work_id = self.get_work_id_by_class_and_name(class_name, work_name)

        for student_id, info in final_dict.items():
            grade = info.get("grade")

            self.cursor.execute("""
                SELECT id
                FROM submissions
                WHERE work_id = ? AND student_id = ?
            """, (work_id, student_id))

            row = self.cursor.fetchone()
            if row is None:
                continue

            submission_id = row[0]

            self.cursor.execute("""
                INSERT OR REPLACE INTO results (submission_id, grade)
                VALUES (?, ?)
            """, (submission_id, grade))

        self.conn.commit()


    def save_task_results(self, submission_id: int, tasks: List[bool]) -> None:

        for task_id, is_correct in enumerate(tasks, start=1):
            self.cursor.execute("""
                INSERT OR REPLACE INTO task_results
                (submission_id, task_id, is_correct)
                VALUES (?, ?, ?)
            """, (submission_id, task_id, int(is_correct)))

        self.conn.commit()


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


    def get_all_data(self, class_name, work_name_entered, status='raw'):
        self.cursor.execute('''
            SELECT id
            FROM classes
            WHERE class_name = ?
        ''', (class_name,))
        row = self.cursor.fetchone()
        class_id = row[0]

        self.cursor.execute('''
            SELECT *
            FROM works
            JOIN submissions ON works.id = submissions.work_id
            JOIN students ON submissions.student_id = students.id
            WHERE works.class_id = ?
              AND works.work_name = ?
              AND works.status = ?
        ''', (class_id, work_name_entered, status))

        rows = self.cursor.fetchall()

        self.cursor.execute('''
            SELECT absents
            FROM works
            WHERE class_id = ?
              AND work_name = ?
              AND status = ?
        ''', (class_id, work_name_entered, status))

        return rows


    def save_statistics_results(self, work_id: int, final_dict: dict):
        self.cursor.execute("SELECT class_id FROM works WHERE id = ?", (work_id,))
        work_res = self.cursor.fetchone()
        if not work_res:
            return
        class_id = work_res[0]

        for student_key, data in final_dict.items():
            name = data.get("name")
            surname = data.get("surname")
            tg_id = data.get("tg_id")
            stats = data.get("stat", {})

            if tg_id:
                self.cursor.execute("SELECT id FROM students WHERE telegram_id = ?", (tg_id,))
            else:
                self.cursor.execute(
                    "SELECT id FROM students WHERE name = ? AND surname = ? AND class_id = ?",
                    (name, surname, class_id)
                )

            student_res = self.cursor.fetchone()
            if not student_res:
                continue
            student_id = student_res[0]

            self.cursor.execute(
                "SELECT id FROM submissions WHERE work_id = ? AND student_id = ?",
                (work_id, student_id)
            )
            submission_res = self.cursor.fetchone()

            if not submission_res:
                continue

            submission_id = submission_res[0]

            for task_id_str, is_correct in stats.items():
                self.cursor.execute(
                    "INSERT INTO task_results (submission_id, task_id, is_correct) VALUES (?, ?, ?)",
                    (submission_id, int(task_id_str), 1 if is_correct else 0)
                )

        self.conn.commit()


    def get_data_for_statistics(self, work_name: str, class_name: str):
        class_id = self.get_class_id(class_name)
        work_id = self.get_work_id(class_id, work_name)

        query = """
            SELECT s.name, s.surname, sub.id, r.grade
            FROM students s
            LEFT JOIN submissions sub ON s.id = sub.student_id AND sub.work_id = ?
            LEFT JOIN results r ON sub.id = r.submission_id
            WHERE s.class_id = ?
        """

        self.cursor.execute(query, (work_id, class_id))
        rows = self.cursor.fetchall()

        res_dct = {}
        grades_dct = {}

        for name, surname, sub_id, grade in rows:
            full_name = f"{name} {surname}"

            grades_dct[full_name] = grade

            if sub_id is not None:
                self.cursor.execute("""
                    SELECT task_id, is_correct FROM task_results
                    WHERE submission_id = ?
                """, (sub_id,))
                tasks = self.cursor.fetchall()
                res_dct[full_name] = {t_id: bool(corr) for t_id, corr in tasks}
            else:
                res_dct[full_name] = {}

        return res_dct, grades_dct


    def get_date_of_work(self, class_name, work_name):
        class_id = self.get_class_id(class_name)
        self.cursor.execute("""
            SELECT work_date FROM works
            WHERE class_id = ? AND work_name = ?
        """, (class_id, work_name))
        return self.cursor.fetchone()[0]


    def get_total_students(self, class_name):
        class_id = self.get_class_id(class_name)
        self.cursor.execute("""
            SELECT COUNT(*) AS total FROM STUDENTS
            WHERE class_id = ?
        """, (class_id,))
        return self.cursor.fetchone()[0]

    def get_absents(self, class_name, work_name):
        class_id = self.get_class_id(class_name)
        work_id = self.get_work_id(work_name)
        self.cursor.execute("""
            SELECT absents
            FROM classes JOIN works ON classes.id = works.class_id
            WHERE classes.id = ? and works.id = ?       
        """, class_id, work_id)
        return self.cursor.fetchone()[0]