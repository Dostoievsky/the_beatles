import os
import shutil

from Database_Settings_classes import Database

class Clear:
    ALLOWED_TABLES = {"classes", "works"}
    def __init__(self, db):
        self.db = db

    def delete_system_files(self):
        try:
            if hasattr(self.db, "conn") and self.db.conn:
                self.db.conn.close()
        except Exception:
            pass

        system_files_path = os.path.join(os.getcwd(), 'system_files')

        if os.path.exists(system_files_path):
            shutil.rmtree(system_files_path)

    def delete_by_field(self, table, field=None, value=None):
        self.db.cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name=?
        """, (table,))
        if not self.db.cursor.fetchone():
            raise ValueError(f"Таблица '{table}' не найдена")

        if field is None and value is None:
            self.db.cursor.execute(f"DELETE FROM {table}")
            self.db.conn.commit()
            return

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
        cur = self.db.conn.cursor()

        cur.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
              AND name NOT LIKE 'sqlite_%'
        """)

        tables = [row[0] for row in cur.fetchall()]
        if not tables:
            return

        try:
            self.db.conn.execute("BEGIN")

            for table in tables:
                self.db.conn.execute(f'DELETE FROM "{table}"')

            self.db.conn.commit()

        except Exception:
            self.db.conn.rollback()
            raise


    def delete_system_files(self):
        folder_path = os.path.join(os.getcwd(), 'system_files')

        try:
            self.db.close()
        except Exception:
            pass

        if not os.path.exists(folder_path):
            raise FileNotFoundError(f"Папка '{folder_path}' не найдена")

        shutil.rmtree(folder_path)

    def delete_work(self, class_id, work_name):
        cursor = self.db.cursor
        cursor.execute(
            "DELETE FROM works WHERE class_id = ? AND work_name = ?",
            (class_id, work_name)
        )
        self.db.conn.commit()

# db = Database()
# db.connect()
# clear = Clear(db)
# clear.delete_by_field('classes', 'class_name', '9в')
# db.close()
