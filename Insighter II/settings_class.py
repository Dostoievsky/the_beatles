import sqlite3
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


def is_first_launch():
    if not os.path.exists(SYSTEM_DIR):
        return True

    if not os.path.exists(DB_PATH):
        return True

    files = set(os.listdir(SYSTEM_DIR))
    return not set(list_of_json_files).issubset(files)


class Settings:
    def __init__(self, path=r'system_files\settings.json'):
        self._path = os.path.join(os.getcwd(), path)
        self._data = self._load()

    def _load(self):
        with open(self._path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @property
    def show_warnings(self):
        return self._data.get('show_warnings', False)

    @property
    def automatically_file_opening(self):
        return self._data.get('automatically_file_opening', False)

    @property
    def saving_all_files_in_one_folder(self):
        return self._data.get('saving_all_files_in_one_folder', False)

    @property
    def developer_mode(self):
        return self._data.get('developer_mode', False)

    @property
    def saving_statistics_in_unque_files(self):
        return self._data.get('saving_statistics_in_unque_files', False)

    @property
    def format_by_default(self):
        return self._data.get('format_by_default', 'txt')

    @property
    def alsways_build_the_graphics(self):
        return self._data.get('alsways_build_the_graphics', False)

    @property
    def encoding(self):
        return self._data.get('encoding', ["utf-8", "utf-8-sig"])





