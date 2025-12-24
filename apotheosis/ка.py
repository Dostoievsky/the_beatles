import sys
import time

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QFileDialog,
                             QComboBox, QCalendarWidget, QDateEdit, QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, QDate


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Meow')
        self.resize(500, 400)

        label = QLabel('Hello, world!')
        label1 = QLabel('Hello, world!!!')
        label2 = QLabel('Hello, world!!!!')

        label.setStyleSheet("""
                    color: white;
                    font-weight: bold;
                    font-size: 24px;
                    background-color: #2b2b2b;
                    padding: 8px;
                    border-radius: 6px;
                """)

        layout = QVBoxLayout()
        layout.addWidget(label, alignment=Qt.AlignCenter)
        layout.addWidget(label1, alignment=Qt.AlignRight)
        layout.addWidget(label2)

        button = QPushButton('Click me')
        layout.addWidget(button)
        button.clicked.connect(self.my_func)

        button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #505050;
                
            }
            QPushButton:pressed {
                background-color: red;
            }
        """)

        close_button = QPushButton('Close')
        layout.addWidget(close_button, alignment=Qt.AlignRight)
        close_button.clicked.connect(self.close)

        self.line = QLineEdit()
        layout.addWidget(self.line)
        self.line.setPlaceholderText('Enter your name')
        self.line.returnPressed.connect(lambda: print(self.line.text()))

        file_button = QPushButton('Choose file')
        layout.addWidget(file_button)
        file_button.clicked.connect(self.choose_file)

        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Перезапись",
            "Добавление",
            "Просмотр"
        ])
        layout.addWidget(self.mode_combo)

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())

        layout.addWidget(self.date_edit)


        self.setLayout(layout)
        self.check = QCheckBox('Check me')

        bar = QProgressBar()
        bar.setMaximum(100)
        bar.setMinimum(0)
        bar.setValue(50)
        layout.addWidget(bar)


        layout.addWidget(self.check)

    def my_func(self):
        print('Hello')
        print(self.line.text())
        print(self.mode_combo.currentText())
        print(self.date_edit.date().toString('dd.MM.yyyy'))
        print(self.check.isChecked())

    def choose_file(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'All files (*.*)')
        if file:
            self.line.setText(file)

    @staticmethod
    def on_mode_changed(text):
        print("Выбран режим:", text)



app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec_())

