import json
from .CONFIG_classes_checking import Student
import sys

class StudentJSONEncoder(json.JSONEncoder):
    """
    Кастомный JSON-энкодер для сериализации объектов класса Student.
    """

    def default(self, o):
        if isinstance(o, Student):
            return o.to_json()
        return super().default(o)


class RangeKey:
    """
    Представляет диапазон чисел как хешируемый ключ.
    Поддерживает сравнение, проверку вхождения и создание строкового представления.
    """

    def __init__(self, start, stop, step=1):
        self.range_obj = range(start, stop + 1, step)

    def __eq__(self, other):
        if isinstance(other, RangeKey):
            return (
                self.range_obj.start == other.range_obj.start and
                self.range_obj.stop == other.range_obj.stop and
                self.range_obj.step == other.range_obj.step
            )
        return NotImplemented

    def __hash__(self):
        return hash((self.range_obj.start, self.range_obj.stop, self.range_obj.step))

    def __contains__(self, item):
        return item in self.range_obj

    def __repr__(self):
        return f"RangeKey({self.range_obj.start}-{self.range_obj.stop-1})"


class Questions:
    """
    Утилита для создания вопросов с пользовательским вводом.
    """

    def __init__(self, question, tuple_of_variants=('1', 'lf', 'да', True)):
        self.question = question
        self.tuple_of_variants = tuple_of_variants

    def make_question(self):
        if input(self.question).strip().lower() in self.tuple_of_variants:
            return True
        else:
            return False



class DebugMode:
    """
    Обеспечивает запись логов в файл syslog.json при включенном режиме отладки.
    Используется для хранения временных данных, состояния и ошибок программы.
    """

    def __init__(self, debug):
        self.debug = debug

    def write_to_file(self, attr, value):
        try:
            if self.debug:
                with open('syslog.json', 'r', encoding='utf-8') as file:
                    data = json.load(file)

                data[attr] = value

                with open('syslog.json', 'w', encoding='utf-8') as file:
                    json.dump(data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f'Вы не должны видеть это сообщение. Если вы не трогали исходный код и файлы, то сообщите на почту, указанную в инструкции. Если вы видете это сообщение, то программа будет выдывать ошибку при следующем запуске. Вручную удалите файл syslog.json для продолжения пользования.\n Во время выполнения программы возникла ошибка: {e}')
            sys.exit(1)