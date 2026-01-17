import json
from datetime import datetime
import os
import sys

class Logger:
    def __init__(self, flag):
        self.flag = flag
        base_dir = self.get_base_path()
        self.file_path = os.path.join(base_dir, 'system_files', 'log.json')

    @staticmethod
    def get_base_path():
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        return os.path.dirname(os.path.abspath(__file__))


    def log(self, key, value):
        if not self.flag:
            return

        data = {}

        if os.path.exists(self.file_path) and os.path.getsize(self.file_path) > 0:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}

        try:
            json.dumps(value)
            data[key] = value
        except TypeError:
            data[key] = repr(value)

        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def log_date(self, message):
        if not self.flag:
            return
        current_time = datetime.now().strftime('%d.%m.%Y, %H.%M.%S')
        self.log(message, current_time)










