import os
import shutil

from Database_Settings_classes import Database

class Clear:
    ALLOWED_TABLES = {"classes", "works"}
    def __init__(self, db):
        self.db = db

    def delete_by_field(self, table, field, value):
        self.db.cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """, (table,))
        if not self.db.cursor.fetchone():
            raise ValueError(f"Таблица '{table}' не найдена")

        self.db.cursor.execute(
            f"SELECT id FROM {table} WHERE {field} = ?",
            (value,)
        )
        row = self.db.cursor.fetchone()

        if not row:
            raise ValueError(
                f"Запись с {field} = '{value}' не найдена в таблице {table}"
            )

        self.db.cursor.execute(
            f"DELETE FROM {table} WHERE {field} = ?",
            (value,)
        )
        self.db.conn.commit()

    def delete_database_file(self):

        db_path = os.path.join('system_files', 'insighter.db')

        try:
            self.db.close()
        except Exception:
            pass

        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Файл базы данных '{db_path}' не найден")

        os.remove(db_path)

    def delete_system_files(self):
        folder_path = os.path.join(os.getcwd(), 'system_files')

        try:
            self.db.close()
        except Exception:
            pass

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Папка '{folder_path}' не найдена")

        shutil.rmtree(folder_path)

db = Database()
db.connect()
clear = Clear(db)
clear.delete_by_field('classes', 'class_name', '9в')
db.close()