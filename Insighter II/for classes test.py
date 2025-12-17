class Validator:
    def __init__(self, class_name, answers_file, grades_file, works_folder, absents_file, date):
        self.class_name = class_name
        self.answers_file = answers_file
        self.grades_file = grades_file
        self.works_folder = works_folder
        self.absents_file = absents_file
        self.date = date
        self.errors = []
        self.previous_data = {}
        self.flag = True

    def get_previous_data(self):
        path = os.path.join(os.getcwd(), 'system_files/sys.json')
        if not os.path.exists(path):
            print('Критическая ошибка. Перезапустите программу.')
            sys.exit()

        with open(path, 'r', encoding='utf-8') as sysfile:
            jsondata = json.load(sysfile)
            if json.load(sysfile):
                self.previous_data = jsondata
            else:
                self.flag = False

    def validate_answers_file(self):
        answers_dict = {}
        with open(self.answers_file, 'r', encoding='utf-8') as answfile:
            list_of_answ_lines = answfile.readlines()
            for line in list_of_answ_lines:
                num_of_question = list_of_answ_lines.index(line) + 1
                try:
                    num, answer = line.split(' ')
                except ValueError:
                    self.errors.append(f'Ошибка в файле с ответами. Строка {num_of_question} не соответствует формату.')
                clean_answer = answer.strip()
                if not clean_answer:
                    self.errors.append(f'Ошибка в файле с ответами. В строке {num_of_question} нет ответа.')
                else:
                    answers_dict[num_of_question] = clean_answer