from Database_Settings_classes import *

def print_menu(strings):
    dct = {}
    for i, string in enumerate(strings, 1):
        print(f"{string}[{i}]")
        dct[i] = string
    chose = input('Введите номер: ')
    try:
        return dct[int(chose)], chose
    except:
        print('Такого значения не существует.')

d = ('gjgf', 'fjgtnrf', 'rfjnerf', 'jrfnkejlwjfr', 'foirjfn')
print(print_menu(d))