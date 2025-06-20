# class Student:
#
#     def __init__(self, name, surname):
#         self.name = name
#         self.surname = surname
#         self.file = None
#         self.list_answers = None
#         self.correct_answers = None
#         self.mark = None
#
# dct = {
#     'John Michael': 'john.txt',
#     'Bob Christian': 'bob.txt',
#     'Mike Victor': 'mike.txt',
#     'Jane Rose': 'jane.txt',
#     'Joe Kevin': 'joe.txt',
#     'Mary Jane': 'mary.txt'
# }
# bdic = {}
#
# for k, v in dct.items():
#     bdic[k] = Student(k.split()[0], k.split()[1])
#
# for k, v in bdic.items():
#     v.file = dct[k]
#
# print(bdic)
#
# # for k, v in bdic.items():
# #     print(v.name, v.surname, v.file, v.list_answers)

import json

class Student:
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname
        self.file = None
        self.list_answers = None
        self.correct_answers = None
        self.mark = None


class StudentJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Student):
            return {'__student__': True,
                   'name': obj.name,
                   'surname': obj.surname,
                   'file': obj.file,
                   'list_answers': obj.list_answers,
                   'correct_answers': obj.correct_answers,
                   'mark': obj.mark}
        return super().default(obj)


def object_hook(dct):
    if '__student__' in dct:
        return Student(dct['name'], dct['surname'])
    return dct


# Исходные данные
dct = {
    'John Michael': 'john.txt',
    'Bob Christian': 'bob.txt',
    'Mike Victor': 'mike.txt',
    'Jane Rose': 'jane.txt',
    'Joe Kevin': 'joe.txt',
    'Mary Jane': 'mary.txt'
}


bdic = {}
for k, v in dct.items():
    bdic[k] = Student(*k.split())
    bdic[k].file = v
print(bdic['John Michael'].__dict__)

# Сериализуем в JSON
json_data = json.dumps(bdic, cls=StudentJSONEncoder, indent=4)

# Сохраняем в файл
with open('students.json', 'w') as f:
    f.write(json_data)

#
# with open('students.json', 'r') as f:
#     raw_json_data = f.read()
#
# # Восстанавливаем объекты
# loaded_bdic = json.loads(raw_json_data, object_hook=object_hook)
#
# # Проверяем восстановленный словарь
# for k, v in loaded_bdic.items():
#     print(f'{k}: {v.__dict__}')