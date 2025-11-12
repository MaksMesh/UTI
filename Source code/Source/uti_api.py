from PIL.ImageQt import ImageQt
from PIL import Image
import struct
import numpy as np
from math import sqrt
from fractions import Fraction


class PasswordError(Exception):
    pass


def convert_password(password):
    nums = {'0': 157, '1': 14, '2': 578, '3': 4, '4': 879, '5': 74, '6': 582, '7': 1, '8': 856, '9': 234}
    fin = 0

    for i in range(len(password)):
        fin += nums.get(password[i], ord(password[i])) ** (i + 1)

    return fin


def ENCODE_WAY_1(image, path_to_img: str, width: int, height: int):
    pixels = np.array(image.image)

    with open(path_to_img, 'wb') as file:
        file.writelines([struct.pack(f'<2IB', width, height, 0)])

        for i in pixels:
            file.write(struct.pack(f'<{width * 4}B', *i.flatten()))


def PASSWORD_ENCODE(image, path_to_img: str, width: int, height: int, password: int):
    pixels = np.array(image.image, dtype=np.uint64)
    password %= 4294967295
    result = password ** 4 % 1234567 + password ** 3 % 1234567 + password * 3 % 1234567 + password % 1234567

    with open(path_to_img, 'wb') as file:
        file.write(struct.pack(f'<2IBI', width, height, 1, password))

        for i in pixels:
            file.write(struct.pack(f'<{width * 4}I', *(i.flatten() * result)))


def ENCODE_WAY_2(image, path_to_img: str, width: int, height: int):
    pixels = np.array(image.image, dtype=np.uint32)

    with open(path_to_img, 'wb') as file:
        file.writelines([struct.pack(f'<2IB', width, height, 2)])

        for i in pixels:
            file.write(struct.pack(f'<{width * 4}i', *((i.flatten() ** 2) - np.array([573] * width * 4))))


def ENCODE_WAY_3(image, path_to_img: str, width: int, height: int):
    pixels = np.array(image.image, dtype=np.uint32)

    with open(path_to_img, 'wb') as file:
        file.writelines([struct.pack(f'<2IB', width, height, 3)])

        for i in pixels:
            file.write(struct.pack(f'<{width * 4}i', *(((((i.flatten() + np.array([45] * width * 4)) * 42) ** 2) - np.array([12548] * width * 4)))))


def DECODE_WAY_1(data, width, height):
    content = struct.unpack(f'<{width * height * 4}B', data)
        
    image = Image.new('RGBA', (width, height))
    pixels = image.load()
    current = 0

    for i in range(height):
        for j in range(width):
            pixels[j, i] = content[current:current + 4]
            current += 4

    return ImageUti(image)


def DECODE_WAY_2(data, width, height):
    content = struct.unpack(f'<{width * height * 4}i', data)
        
    image = Image.new('RGBA', (width, height))
    pixels = image.load()
    current = 0

    for i in range(height):
        for j in range(width):
            r, g, b, a = content[current:current + 4]
            pixels[j, i] = int(sqrt(r + 573)), int(sqrt(g + 573)), int(sqrt(b + 573)), int(sqrt(a + 573))
            current += 4

    return ImageUti(image)


def DECODE_WAY_3(data, width, height):
    content = struct.unpack(f'<{width * height * 4}I', data)
        
    image = Image.new('RGBA', (width, height))
    pixels = image.load()
    current = 0

    for i in range(height):
        for j in range(width):
            r, g, b, a = content[current:current + 4]
            pixels[j, i] = int(sqrt(r + 12548)) // 42 - 45, int(sqrt(g + 12548)) // 42 - 45, int(sqrt(b + 12548)) // 42 - 45, int(sqrt(a + 12548)) // 42 - 45
            current += 4

    return ImageUti(image)


WAYS_TO_CONVERT = [(ENCODE_WAY_1, 'Default way'), (PASSWORD_ENCODE, 'Password way'), (ENCODE_WAY_2, 'Safe way'), (ENCODE_WAY_3, 'Infinity way')]
DECODE_WAYS = [DECODE_WAY_1, 'PASSWORD', DECODE_WAY_2, DECODE_WAY_3]


class ImageUti:
    def __init__(self, image):
        self.image = image
        self.width = image.width
        self.height = image.height

    def export(self, path_to_img: str, way_to_encode=ENCODE_WAY_1, password: int=None):
        '''Экспортирует изображение.'''
        if way_to_encode.__name__ == 'PASSWORD_ENCODE':
            way_to_encode(self, path_to_img, self.width, self.height, password)
        else:
            way_to_encode(self, path_to_img, self.width, self.height)

    @staticmethod
    def import_image(path_to_img: str):
        '''Загружает изображение из файла.'''
        with open(path_to_img, 'rb') as file:
            data = file.read(9)

            width, height, way = struct.unpack('<2IB', data)
            data = file.read()

        decode_way = DECODE_WAYS[way]

        if decode_way != 'PASSWORD':
            return decode_way(data, width, height)
        else:
            return 'PASSWORD'

    @staticmethod   
    def import_image_with_way(path_to_img: str):
        '''Загружает изображение из файла. Дополнительно возвращает вид его декодирования.'''
        with open(path_to_img, 'rb') as file:
            data = file.read(9)

            width, height, way = struct.unpack('<2IB', data)
            data = file.read()

        decode_way = DECODE_WAYS[way]

        if decode_way != 'PASSWORD':
            return decode_way(data, width, height), way
        else:
            return 'PASSWORD', way
        
    @staticmethod
    def import_image_with_password(path_to_img: str, password: int):
        '''Загружает запароленное изображение из файла.'''
        password %= 4294967295

        with open(path_to_img, 'rb') as file:
            data = file.read(9)

            width, height, way = struct.unpack('<2IB', data)
            file_password = file.read(4)
            data = file.read()

        decode_way = DECODE_WAYS[way]

        if decode_way != 'PASSWORD':
            raise PasswordError("File doesn't contain password.")
        
        file_password = struct.unpack('<I', file_password)[0]
        
        if file_password != password:
            return 'Incorrect password'
        
        content = struct.unpack(f'<{width * height * 4}I', data)
        
        image = Image.new('RGBA', (width, height))
        pixels = image.load()
        current = 0
        result = password ** 4 % 1234567 + password ** 3 % 1234567 + password * 3 % 1234567 + password % 1234567

        for i in range(height):
            for j in range(width):
                pixels[j, i] = tuple(map(lambda x: x // result, content[current:current + 4]))
                current += 4

        return ImageUti(image)
        
    def get_qimage(self) -> ImageQt:
        '''Возвращает изображение в виде ImageQt.'''
        return ImageQt(self.image)
    
    def show(self):
        self.image.show()


if __name__ == '__main__':
    image = ImageUti(Image.open('logo.png'))
    image.export('ad.uti', ENCODE_WAY_3)

    image = ImageUti.import_image('ad.uti')
    image.image.show()