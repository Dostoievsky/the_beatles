import tkinter as tk
from tkinter import filedialog
from .CONFIG_classes_checking import Student



def browse_file(entry):
    file_path = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path)


def browse_folder(entry):
    folder_path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, folder_path)


def student_decoder(dct):
    if '__class__' in dct and dct['__class__'] == 'Student':
        instance = Student(dct['_name'], dct['_surname'])
        instance._file = dct.get('_file')
        instance._list_answers = dct.get('_list_answers')
        instance._correct_answers = dct.get('_correct_answers')
        instance._response_status = dct.get('_response_status')
        instance._mark = dct.get('_mark')
        instance._missings = dct.get('_missings')
        instance._flag_not_all = dct.get('_flag_not_all')
        return instance
    return dct


