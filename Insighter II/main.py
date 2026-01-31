import json
import os
import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from start_window import *
from database_and_settings_classes import *
from main_menu import *

SYSTEM_DIR = os.path.join(os.getcwd(), 'system_files')
DB_PATH = os.path.join(SYSTEM_DIR, 'insighter.db')

JSON_FILES = [
    'sys.json',
    'log.json',
    'patterns.json',
    'settings.json'
]

DEFAULT_SETTINGS = {
    'automatically_file_opening': False,
    'saving_all_files_in_one_folder': False,
    'developer_mode': False,
    'saving_statistics_in_unque_files': False,
    'format_by_default': 'ask',
    'alsways_build_the_graphics': False,
    'encoding': ['utf-8', 'utf-8-sig'],
    'show_warnings': True
}

app = QApplication(sys.argv)

if is_first_launch():
    os.makedirs(SYSTEM_DIR, exist_ok=True)

    db = Database(DB_PATH)
    db.initialize()

    for file in list_of_json_files:
        Path(SYSTEM_DIR, file).touch()

    settings_path = os.path.join(SYSTEM_DIR, 'settings.json')
    with open(settings_path, 'w', encoding='utf-8') as f:
        json.dump(DEFAULT_SETTINGS, f, indent=4)

    window = WelcomeWindow()
else:
    window = MainMenu()

window.show()
sys.exit(app.exec_())

