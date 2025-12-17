import sqlite3
import os
from pathlib import Path

SYSTEM_DIR = 'system_files'
DB_PATH = os.path.join(SYSTEM_DIR, 'insighter.db')

list_of_json_files = [
    'sys.json',
    'log.json',
    'patterns.json',
    'settings.json'
]


class Database:
    def __init__(self, db_path = "insighter.db"):
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
                absents_data TEXT,
                status TEXT
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

def is_first_launch():
    if not os.path.exists(SYSTEM_DIR):
        return True

    if not os.path.exists(DB_PATH):
        return True

    files = set(os.listdir(SYSTEM_DIR))
    return not set(list_of_json_files).issubset(files)
