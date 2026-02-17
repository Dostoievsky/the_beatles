import random
from typing import Dict, List

from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve
from PyQt5.QtGui import QColor, QMouseEvent
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget
)


class RandomCallDialog(QDialog):

    def __init__(self, classes_students: Dict[str, List[str]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка случайного вызова")
        self.resize(400, 180)

        self.classes_students = classes_students or {}

        self.class_combo = QComboBox()
        self.class_combo.addItems(list(self.classes_students.keys()))

        self.show_next_checkbox = QCheckBox("Показывать следующего")
        self.drama_mode_checkbox = QCheckBox("Добавить драмы")
        self.drama_mode_checkbox.setChecked(True)  # По умолчанию включено

        self.next_button = QPushButton("Начать опрос")
        self.next_button.setMinimumHeight(40)
        self.next_button.clicked.connect(self._open_names_window)

        # Комновка
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(QLabel("Выберите класс:"))
        main_layout.addWidget(self.class_combo)

        main_layout.addWidget(self.show_next_checkbox)
        main_layout.addWidget(self.drama_mode_checkbox)

        main_layout.addStretch()
        main_layout.addWidget(self.next_button)

        if not self.classes_students:
            QMessageBox.warning(self, "Ошибка", "Список классов пуст!")
            self.reject()

        self.names_window = None

    def _open_names_window(self) -> None:
        class_name = self.class_combo.current_text() if hasattr(self.class_combo,
                                                                'current_text') else self.class_combo.currentText()
        students = list(self.classes_students.get(class_name, []))

        if not students:
            QMessageBox.warning(self, "Пустой класс", "В выбранном классе нет учеников")
            return

        random.shuffle(students)

        if self.drama_mode_checkbox.isChecked():
            window_class = _DramaCallWindow
        else:
            window_class = _StandardCallWindow

        self.names_window = window_class(
            students=students,
            show_next=self.show_next_checkbox.isChecked(),
            parent=self
        )
        self.names_window.exec_()


class _DramaCallWindow(QDialog):
    """Драматичный режим: красный фон, клики по экрану, страшные надписи."""

    def __init__(self, students: List[str], show_next: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Судный час")
        self.resize(500, 350)

        # Цвет из вашего запроса #595e5b
        self.default_color = QColor("#595e5b")
        self._color = self.default_color

        # Настройка затяжной анимации
        self.animation = QPropertyAnimation(self, b"backgroundColor")
        self.animation.setDuration(3500)  # 3.5 секунды общее время
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.students = students
        self.show_next = show_next
        self.current_index = 0
        self.finished = False

        self._build_ui()
        self._show_current()

    @pyqtProperty(QColor)
    def backgroundColor(self):
        return self._color

    @backgroundColor.setter
    def backgroundColor(self, color):
        self._color = color
        self.setStyleSheet(f"background-color: {color.name()};")

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and not self.finished:
            self._handle_next()
        super().mousePressEvent(event)

    def _handle_next(self):
        self.current_index += 1
        self.animation.stop()
        self.animation.setStartValue(QColor(180, 0, 0))
        self.animation.setKeyValueAt(0.5, QColor(180, 0, 0))
        self.animation.setEndValue(self.default_color)
        self.animation.start()
        self._show_current()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {self.default_color.name()};")
        layout = QVBoxLayout(self)

        self.slabel = QLabel('На верную смерть идет:')
        self.slabel.setStyleSheet("color: #d1d1d1; font-size: 18px; background: transparent;")

        self.current_label = QLabel("")
        self.current_label.setAlignment(Qt.AlignCenter)
        self.current_label.setStyleSheet(
            "font-weight: bold; color: white; font-size: 24pt; font-family: 'Consolas'; background: transparent;")

        self.next_preview_label = QLabel("")
        self.next_preview_label.setAlignment(Qt.AlignCenter)
        self.next_preview_label.setStyleSheet("color: #d1d1d1; font-size: 14px; background: transparent;")

        self.exit_btn = QPushButton("Закончить")
        self.exit_btn.hide()
        self.exit_btn.clicked.connect(self.accept)

        layout.addWidget(self.slabel)
        layout.addStretch()
        layout.addWidget(self.current_label)
        layout.addWidget(self.next_preview_label)
        layout.addStretch()
        layout.addWidget(self.exit_btn, alignment=Qt.AlignRight)

    def _show_current(self):
        if self.current_index >= len(self.students):
            self.finished = True
            self.current_label.setText("Все опрошены...")
            self.next_preview_label.setText("Выживших не осталось.")
            self.exit_btn.show()
            return

        self.current_label.setText(self.students[self.current_index])
        if self.show_next:
            if self.current_index + 1 < len(self.students):
                self.next_preview_label.setText(f"Следующая жертва: {self.students[self.current_index + 1]}")
            else:
                self.next_preview_label.setText("Это последний выживший.")


class _StandardCallWindow(QDialog):
    def __init__(self, students: List[str], show_next: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Список вызова")
        self.resize(460, 250)

        self.students = students
        self.show_next = show_next
        self.current_index = 0

        self._build_ui()
        self._show_current()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.info_label = QLabel("Текущий учащийся:")
        self.name_label = QLabel("")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setStyleSheet("font-size: 20pt; font-weight: bold; border: 1px solid #ccc; padding: 20px;")

        self.next_label = QLabel("")
        self.next_label.setStyleSheet("color: gray;")

        self.btn_next = QPushButton("Следующий")
        self.btn_next.clicked.connect(self._handle_next)

        layout.addWidget(self.info_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.next_label)
        layout.addStretch()
        layout.addWidget(self.btn_next)

    def _handle_next(self):
        self.current_index += 1
        self._show_current()

    def _show_current(self):
        if self.current_index >= len(self.students):
            self.name_label.setText("Опрос завершен")
            self.next_label.clear()
            self.btn_next.setText("Закрыть")
            self.btn_next.clicked.disconnect()
            self.btn_next.clicked.connect(self.accept)
            return

        self.name_label.setText(self.students[self.current_index])
        if self.show_next and self.current_index + 1 < len(self.students):
            self.next_label.setText(f"Далее: {self.students[self.current_index + 1]}")
        else:
            self.next_label.clear()
