import sys
from tkinter.ttk import Progressbar
import threading
import time
import os.path
import tkinter as tk
from tkinter import filedialog
import requests

class LoadingWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Programm Install")
        self.geometry("400x150")
        self.resizable(False, False)

        # Элементы интерфейса
        self.label_status = tk.Label(self, text="Подготовка к установке...")
        self.label_status.pack(pady=10)

        self.progress_bar = Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        # Начальные значения
        self.current_progress = 0
        self.total_steps = 100

        # Запускаем фоновую задачу загрузки
        thread = threading.Thread(target=self.simulate_loading)
        thread.start()

    def simulate_loading(self):
        stages = [
            "Распаковка архивов...",
            "Установка программных файлов...",
            "Настройка конфигурации...",
            "Оптимизация производительности..."
        ]

        for stage in stages:
            self.update_label(stage)
            for _ in range(25):
                self.update_progress()
                time.sleep(0.1)

        self.update_label("Завершено!")
        time.sleep(1)
        self.quit()

    def update_progress(self):
        self.current_progress += 1
        self.progress_bar["value"] = self.current_progress
        self.update_idletasks()

    def update_label(self, text):
        self.label_status.config(text=text)
        self.update_idletasks()



def select_directory():
    global selected_dir_path
    dir_path = filedialog.askdirectory(title="Выберите папку")
    entry.delete(0, tk.END)  # Очищаем текущее содержимое поля ввода
    entry.insert(0, dir_path)  # Заполняем выбранным путём
    selected_dir_path = dir_path
    return selected_dir_path

def close_window():
    root.destroy()

root = tk.Tk()
root.title("Выбор папки")
root.geometry("600x300")

label = tk.Label(root, text="Укажите путь к папке:", font=("Montserrat", 12))
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack(padx=10, pady=5)

button_browse = tk.Button(root, text="Обзор...", font=("Montserrat", 9), command=select_directory)
button_browse.pack(side=tk.LEFT, padx=(10, 0))

button_done = tk.Button(root, text="Готово", font=("Montserrat", 9), command=close_window)
button_done.pack(side=tk.RIGHT, padx=(0, 10))


selected_dir_path = ""

root.mainloop()
github_url = "https://raw.githubusercontent.com/Dostoievsky/Project_/refs/heads/main/apotheosischeking.py?token=GHSAT0AAAAAADDJNBGLEANTUIQFVTK66OZQ2AXY43Q"
local_filename = os.path.join(selected_dir_path, "programm.py")
response = requests.get(github_url)
if response.status_code == 200:
    with open(local_filename, 'wb') as file:
        file.write(response.content)
    if __name__ == "__main__":
        app = LoadingWindow()
        app.mainloop()

else:
    print(f"Ошибка при скачивании файла: {response.status_code}")
    sys.exit()


