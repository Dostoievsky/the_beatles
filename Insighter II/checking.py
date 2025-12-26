class Checking:
    def __init__(self, big_data, absents):
        self.big_data = big_data
        self.absents = absents
        self.students_dct = {}
        self.right_answers = ''
        self.grades = ''
        self.date_work_name = ''


    def parse_big_data(self):
        for student_work in self.big_data:
            work_name = student_work[1]
            date = student_work[2]
            right_answers = student_work[4]
            grades = student_work[5]
            absents = student_work[7]
            puple_answers = student_work[11]
            name = student_work[14]
            surname = student_work[15]
            tg_id = student_work[16]
            self.students_dct[f'{name} {surname}'] = (puple_answers, tg_id)
            self.date_work_name = f'{work_name} за {date}'
            self.absents = absents
            self.right_answers = right_answers
            self.grades = grades
        return


