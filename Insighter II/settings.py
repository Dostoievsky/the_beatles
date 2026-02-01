import os
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QDateEdit,
                             QFileDialog, QGridLayout, QSizePolicy, QCheckBox)

from PyQt5.QtCore import Qt, QDate
import json
from PyQt5.QtCore import pyqtSignal


SYSTEM_DIR = os.path.join(os.getcwd(), 'system_files')
SETTINGS_PATH = os.path.join(SYSTEM_DIR, 'settings.json')


DEFAULT_SETTINGS = {
    'automatically_file_opening': False,
    'saving_all_files_in_one_folder': False,
    'developer_mode': False,
    'saving_statistics_in_unque_files': False,
    'format_by_default': 'ask',
    'alsways_build_the_graphics': False,
    'encoding': ['utf-8', 'utf-8-sig'],
    'show_warnings': True,
    'take_data_from_previous_load': True
}


class SettingsWindow(QWidget):
    finished = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.resize(700, 500)

        self.settings = self.load_settings()

        grid = QGridLayout()
        grid.setSpacing(10)

        self.automatically_file_opening = QCheckBox("Автоматически открывать файлы")
        self.developer_mode = QCheckBox("Режим разработчика")
        self.saving_statistics_in_unque_files = QCheckBox("Сохранять статистику в уникальных файлах")
        self.alsways_build_the_graphics = QCheckBox("Всегда строить графики")
        self.show_warnings = QCheckBox("Показывать предупреждения")
        self.take_data_from_previous_load = QCheckBox("Брать данные из предыдущей загрузки")

        self.saving_all_files_in_one_folder = QCheckBox("Сохранять все файлы в одной папке")
        self.one_folder_line = QLineEdit()
        self.one_folder_line.setReadOnly(True)

        self.saving_all_files_in_one_folder.stateChanged.connect(self.handle_one_folder_checkbox)

        self.format_by_default = QComboBox()
        self.format_by_default.addItems(["спрашивать каждый раз", ".csv", ".txt"])

        self.encoding_txt = QLineEdit()
        self.encoding_csv = QLineEdit()

        self.reset_button = QPushButton("Сбросить по умолчанию")
        self.reset_button.setFixedSize(200, 50)
        self.apply_button = QPushButton("Применить")
        self.apply_button.setFixedSize(200, 50)


        self.reset_button.clicked.connect(self.reset_to_default)
        self.apply_button.clicked.connect(self.apply_settings)

        row = 0
        grid.addWidget(self.automatically_file_opening, row, 0); row += 1

        grid.addWidget(self.saving_all_files_in_one_folder, row, 0)
        grid.addWidget(self.one_folder_line, row, 1); row += 1

        grid.addWidget(self.developer_mode, row, 0); row += 1
        grid.addWidget(self.saving_statistics_in_unque_files, row, 0); row += 1

        grid.addWidget(QLabel("Формат файлов по умолчанию:"), row, 0)
        grid.addWidget(self.format_by_default, row, 1); row += 1

        grid.addWidget(self.alsways_build_the_graphics, row, 0); row += 1

        grid.addWidget(QLabel("Кодировка TXT:"), row, 0)
        grid.addWidget(self.encoding_txt, row, 1); row += 1

        grid.addWidget(QLabel("Кодировка CSV:"), row, 0)
        grid.addWidget(self.encoding_csv, row, 1); row += 1

        grid.addWidget(self.show_warnings, row, 0); row += 1
        grid.addWidget(self.take_data_from_previous_load, row, 0); row += 1

        grid.addWidget(self.reset_button, row, 0)
        grid.addWidget(self.apply_button, row, 1)

        self.setLayout(grid)

        self.apply_settings_to_ui()



    @staticmethod
    def load_settings():
        os.makedirs(SYSTEM_DIR, exist_ok=True)

        if not os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_SETTINGS, f, indent=4, ensure_ascii=False)
            return DEFAULT_SETTINGS.copy()

        try:
            with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4, ensure_ascii=False)

    def apply_settings_to_ui(self):
        s = self.settings

        self.automatically_file_opening.setChecked(s['automatically_file_opening'])
        self.developer_mode.setChecked(s['developer_mode'])
        self.saving_statistics_in_unque_files.setChecked(s['saving_statistics_in_unque_files'])
        self.alsways_build_the_graphics.setChecked(s['alsways_build_the_graphics'])
        self.show_warnings.setChecked(s['show_warnings'])
        self.saving_all_files_in_one_folder.blockSignals(True)

        value = s['saving_all_files_in_one_folder']
        if isinstance(value, str):
            self.saving_all_files_in_one_folder.setChecked(True)
            self.one_folder_line.setText(value)
        else:
            self.saving_all_files_in_one_folder.setChecked(False)
            self.one_folder_line.clear()

        self.saving_all_files_in_one_folder.blockSignals(False)

        self.format_by_default.setCurrentText(s['format_by_default'])
        self.encoding_txt.setText(s['encoding'][0])
        self.encoding_csv.setText(s['encoding'][1])

    def handle_one_folder_checkbox(self, state):
        if state == Qt.Checked:
            folder = QFileDialog.getExistingDirectory(self, "Выберите папку")
            if folder:
                self.one_folder_line.setText(folder)
            else:
                self.saving_all_files_in_one_folder.setChecked(False)
        else:
            self.one_folder_line.clear()

    def reset_to_default(self):
        self.settings = DEFAULT_SETTINGS.copy()
        self.apply_settings_to_ui()

    def apply_settings(self):
        self.settings = {
            'automatically_file_opening': self.automatically_file_opening.isChecked(),
            'saving_all_files_in_one_folder': (
                self.one_folder_line.text()
                if self.saving_all_files_in_one_folder.isChecked()
                else False
            ),
            'developer_mode': self.developer_mode.isChecked(),
            'saving_statistics_in_unque_files': self.saving_statistics_in_unque_files.isChecked(),
            'format_by_default': self.format_by_default.currentText(),
            'alsways_build_the_graphics': self.alsways_build_the_graphics.isChecked(),
            'encoding': [
                self.encoding_txt.text(),
                self.encoding_csv.text()
            ],
            'show_warnings': self.show_warnings.isChecked(),
            'take_data_from_previous_load': self.take_data_from_previous_load.isChecked()
        }

        self.save_settings()
        self.close()

    def closeEvent(self, event):
        self.finished.emit()
        super().closeEvent(event)

# app = QApplication(sys.argv)
# window = SettingsWindow()
# window.show()
# sys.exit(app.exec_())
print()