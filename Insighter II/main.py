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
app.setStyleSheet('''
        QWidget {
            background-color: #595e5b;
            color: #ffffff;
            font-size: 14px;
            font-weight: bold;
            font-family: "Consolas", monospace;
        }
        
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #262626;
            border: 1px solid #444444;
            border-radius: 4px;
            padding: 4px;
            selection-background-color: #557A95;
        }
        
        QLineEdit:focus {
            border: 1px solid #557A95;
        }
        
        QPushButton {
            background-color: #303b3d;
            border: 1px solid #444444;
            border-radius: 10px;
            
            width: 200px;
            height: 30px;
            
        }
        
        QPushButton:hover {
            background-color: #557A95;
        }
        
        QPushButton:pressed {
            background-color: #303b3d;
            border: 1px solid #557A95;
        }
        
        QPushButton:disabled {
            background-color: #444444;
            color: #888888;
        }
        
        QComboBox {
            background-color: #303b3d;
            border: 2px solid #444444;
            border-radius: 4px;
            padding: 3px 10px;
        }
        
        QComboBox:hover {
            border: 2px solid #557A95;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid #444444;
        }
        
        QComboBox QAbstractItemView {
            background-color: #303b3d;
            border: 1px solid #557A95;
            selection-background-color: #557A95;
        }
        
        QCheckBox {
            spacing: 8px;
        }
        
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            border: 2px solid #444444;
            background-color: #303b3d;
        }
        
        QCheckBox::indicator:hover {
            border: 2px solid #557A95;
        }
        
        QCheckBox::indicator:checked {
            background-color: #557A95;
            border: 2px solid #557A95;
            image: url(check.png); /* Если есть иконка галочки */
        }
        
        QRadioButton {
            spacing: 8px;
        }
        
        QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border-radius: 10px;
            border: 2px solid #444444;
            background-color: #303b3d;
        }
        
        QRadioButton::indicator:hover {
            border: 2px solid #557A95;
        }
        
        QRadioButton::indicator:checked {
            background-color: #557A95;
            border: 2px solid #557A95;
        }
        
        QScrollBar:vertical {
            background: #262626;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #444444;
            min-height: 20px;
            border-radius: 4px;
            margin: 2px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #557A95;
        }
        
        QWidget:disabled {
            color: #888888;
            
        }''')


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

