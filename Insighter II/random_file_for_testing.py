def save_final_results(self, work_id, class_name, final_dict):
    """
    Записывает оценки из словаря в таблицу results,
    предварительно сопоставляя студента и его работу.
    """
    # 1. Получаем ID класса
    class_id = self.get_or_create_class(class_name)

    for key, info in final_dict.items():
        name = info['name']
        surname = info['surname']
        grade = info['grade']

        # 2. Находим id студента в этом классе
        self.cursor.execute("""
            SELECT id FROM students 
            WHERE class_id = ? AND name = ? AND surname = ?
        """, (class_id, name, surname))

        student_row = self.cursor.fetchone()
        if not student_row:
            print(f"Студент {name} {surname} не найден в базе.")
            continue

        student_id = student_row[0]

        # 3. Находим id работы (submission) этого студента
        self.cursor.execute("""
            SELECT id FROM submissions 
            WHERE work_id = ? AND student_id = ?
        """, (work_id, student_id))

        submission_row = self.cursor.fetchone()
        if not submission_row:
            print(f"Работа (submission) для студента {name} {surname} не найдена.")
            continue

        submission_id = submission_row[0]


        self.cursor.execute("""
            INSERT OR REPLACE INTO results (submission_id, grade)
            VALUES (?, ?)
        """, (submission_id, grade))

    self.conn.commit()