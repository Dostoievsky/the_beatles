import json
import os
import re

class ImportData:
    def __init__(self, filepath, work_name):
        self.filepath = filepath
        self.work_name = work_name

    def normalize_data(self):
        big_data = {}
        if not (os.path.exists(self.filepath) and os.path.isfile(self.filepath)):
            return None
        with open(self.filepath, 'r', encoding='utf-8') as file:
            filelist = json.load(file)
            for i in filelist:
                dct = dict(i)
                dct = {k.lower(): v for k, v in dct.items()}
                normalized_dict = {}
                for k, v in dct.items():
                    if re.search(r'баллы', k, re.IGNORECASE):
                        continue
                    if re.match(r'задача\s*(\d+)', k, re.IGNORECASE):
                        clean_k = re.sub(r'\s*\(ссылка \wа файл.*?\)', '', k, flags=re.IGNORECASE)
                        clean_k = re.sub(r'задача\s*', '', clean_k, flags=re.IGNORECASE).strip()
                        normalized_dict[clean_k] = v
                try:
                    puple_name = dct['фамилия имя'].strip()
                    if not puple_name:
                        puple_name = 'Пустое поле'
                except KeyError:
                    return
                big_data[puple_name] = normalized_dict
        return big_data

    def generate_data(self, normalized_data):
        fools_lst = []
        folder_path = os.path.join(os.getcwd(), self.work_name)
        os.makedirs(folder_path, exist_ok=True)

        for kq, vq in normalized_data.items():
            try:
                surname, name = kq.split()
            except ValueError:
                fools_lst.append(kq)
            filename = f'{name.lower()}_{surname.lower()}.txt'
            full_path = os.path.join(folder_path, filename)
            with open(full_path, 'w', encoding='utf-8') as file:
                for kq1, vq1 in vq.items():
                    print(f'{kq1.strip().lower()}) {vq1.strip().lower()}', file=file)
        return fools_lst

