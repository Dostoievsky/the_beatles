import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Демо меню")
        self.setFixedSize(300, 150)

        self.btn_sum = QPushButton("Сумма")
        self.btn_avg = QPushButton("Среднее арифметическое")
        self.btn_exit = QPushButton("Выход")

        layout = QVBoxLayout()
        layout.addWidget(self.btn_sum)
        layout.addWidget(self.btn_avg)
        layout.addWidget(self.btn_exit)
        self.setLayout(layout)

        self.btn_sum.clicked.connect(self.run_sum)
        self.btn_avg.clicked.connect(self.run_avg)
        self.btn_exit.clicked.connect(self.close)

    def run_sum(self):
        self.hide()
        run_sum_mode()
        self.show()

    def run_avg(self):
        self.hide()
        run_avg_mode()
        self.show()


def run_sum_mode():
    print("\n=== РЕЖИМ СУММЫ ===")
    numbers = []

    for i in range(1, 4):
        n = float(input(f"Введите число {i}: "))
        numbers.append(n)

    result = sum(numbers)
    print(f"Сумма: {result}")
    input("Нажмите Enter для возврата в меню...")


def run_avg_mode():
    print("\n=== РЕЖИМ СРЕДНЕГО ===")
    numbers = []

    for i in range(1, 4):
        n = float(input(f"Введите число {i}: "))
        numbers.append(n)

    result = sum(numbers) / len(numbers)
    print(f"Среднее арифметическое: {result}")
    input("Нажмите Enter для возврата в меню...")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec_())
