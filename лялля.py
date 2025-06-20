a, b = int(input()), int(input())

with open('file.txt', 'w') as file:
    print(a+b, file=file)

