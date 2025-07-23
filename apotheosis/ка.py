from math import sqrt

class Vector:
    def __init__(self, *args):
        self.coords = list(args)

    def __str__(self):
        return f'{tuple(self.coords)}'

    def __add__(self, other):
        if len(self.coords) != len(other.coords):
            raise ValueError('Векторы должны иметь равную длину')
        added = []
        for s, o in zip(self.coords, other.coords):
            added.append(s + o)
        return Vector(*added)

    def __sub__(self, other):
        if len(self.coords) != len(other.coords):
            raise ValueError('Векторы должны иметь равную длину')
        subbed = []
        for s, o in zip(self.coords, other.coords):
            subbed.append(s - o)
        return Vector(*subbed)

    def __mul__(self, other):
        if len(self.coords) != len(other.coords):
            raise ValueError('Векторы должны иметь равную длину')
        mulled = []
        for s, o in zip(self.coords, other.coords):
            mulled.append(s * o)
        return sum(mulled)

    def norm(self):
        normed = []
        for coord in self.coords:
            normed.append(coord ** 2)
        summ = sum(normed)
        return sqrt(summ)

    def __eq__(self, other):
        if len(self.coords) != len(other.coords):
            raise ValueError('Векторы должны иметь равную длину')
        return self.coords == other.coords

    def __ne__(self, other):
        if len(self.coords) != len(other.coords):
            raise ValueError('Векторы должны иметь равную длину')
        return self.coords != other.coords


vector1 = Vector(1, 2, 3)
vector2 = Vector(5, 6, 7, 8)

try:
    print(vector1 == vector2)
except ValueError as e:
    print(e)