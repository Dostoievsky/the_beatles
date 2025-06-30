
from pathlib import Path
import re
import os

class Statistics:
    def __init__(self, dir):
        self.dir = dir
        self.pairs = {}
        self.printlist = []

    @staticmethod
    def extract_core_name(file_path):
        stem = file_path.stem  # Имя файла без расширения
        core_name = re.sub(r'^sysfile_', '', stem)  # Убираем приставку sysfile_
        return core_name

    def gen_pairs(self):
        files = [Path(self.dir) / file for file in os.listdir(self.dir) if (Path(self.dir) / file).is_file()]
        for file in files:
            if file.suffix == '.txt':
                core_name = self.extract_core_name(file)
                matching_json = next((jf for jf in files if jf.suffix == '.json' and self.extract_core_name(jf) == core_name), None)
                self.pairs[file] = matching_json
        return self.pairs

dctchosenstat = {}
st = Statistics(r'D:\pythonProject\apotheosis\archive\8в')
pairs = st.gen_pairs()

for index, (txt_file, json_file) in enumerate(pairs.items(), 1):
    dctchosenstat[index] = (txt_file, json_file)



for index, (txt_file, json_file) in dctchosenstat.items():
    print(f"{txt_file.name}[{index}] ({'подробная статистика доступна' if json_file is not None else 'подробная статистика недоступна'})")
ind = input('Выберите файл ')
print(dctchosenstat[int(ind)])