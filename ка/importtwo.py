import random

class Cipher:
    def __init__(self, text):
        self.text = text

    def encode(self):
        result = ''
        random_shift = random.randint(1, 26)
        shift = ord(self.text.strip()[-1]) + random_shift
        for char in self.text:
            result += str(ord(char) + shift)
            result += '%'
        result += '&' + str(shift)
        result += '@'
        return result

    def decode(self):
        result = ''
        for wr in self.text.split('@'):
            if wr:
                need_to_decode, shift = wr.split('&')
                for char in need_to_decode.split('%'):
                    if char:
                        result += chr(int(char) - int(shift))
            result += '\n'
        return result



mode = input('enter mode: ').strip().lower()
if mode == 'encode':
    with open('readable.txt', 'r', encoding='utf-8') as file, open('encoded.txt', 'w', encoding='utf-8') as file1:
        file_content = file.read()
        ciper = Cipher(file_content)
        encoded = ciper.encode()
        file1.write(encoded)

elif mode == 'decode':
    with open('readable.txt', 'w', encoding='utf-8') as file, open('encoded.txt', 'r', encoding='utf-8') as file1:
        file_content = file1.read()
        ciper = Cipher(file_content)
        decoded = ciper.decode()
        file.write(decoded.strip())
else:
    print('Unknown mode!')

