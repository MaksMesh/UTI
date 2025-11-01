from uti_api import ImageUti, WAYS_TO_CONVERT, convert_password
from PIL import Image, ImageDraw
from PyQt6 import uic
from PyQt6.QtWidgets import (QMainWindow, QApplication, QFileDialog, QMessageBox, QInputDialog, QColorDialog,
                             QPushButton, QSlider, QLabel)
from PyQt6.QtGui import QIcon, QPainter, QPixmap, QImage, QColor
from PyQt6.QtCore import QSize
import sys


class InstrumentParams(QMainWindow):
    def __init__(self, name, instrument, maximum_size):
        super().__init__()

        attributes_order = ['limit', 'size', 'transperency', 'fill']
        self.localization = {'limit': 'Порог', 'size': 'Размер', 'transperency': 'Непрозрачность', 'fill': 'Заливка',
                        'brush': 'Кисть', 'eraser': 'Ластик', 'bucket': 'Заливка', 'circle': 'Круг',
                        'rectangle': 'Прямоугольник', 'triangle': 'Треугольник', 'line': 'Линия'}
        self.maximum_size = maximum_size
        self.instrument = instrument
        
        self.setWindowTitle(self.localization[name])
        
        self.attributes_names = sorted([i for i in instrument], key=lambda x: attributes_order.index(x))

        self.initUI()

    def initUI(self):
        curr_height = 10
        for i in self.attributes_names:
            if i == 'size':
                label = QLabel(self)
                label.move(10, curr_height)
                label.setText(self.localization[i])

                slider = QSlider(self)
                slider.setMaximum(self.maximum_size)
                slider.setMinimum(1)
                slider.move(50, curr_height)

                if self.instrument[i] is not None:
                    slider.setValue(self.instrument[i])

                curr_height += 20
            elif i == 'transperency':
                label = QLabel(self)
                label.move(10, curr_height)
                label.setText(self.localization[i])

                slider = QSlider(self)
                slider.setMaximum(255)
                slider.setMinimum(0)
                slider.move(50, curr_height)
                slider.setValue(self.instrument[i])

                curr_height += 20
            elif i == 'limit':
                label = QLabel(self)
                label.move(10, curr_height)
                label.setText(self.localization[i])

                slider = QSlider(self)
                slider.setMaximum(300)
                slider.setMinimum(0)
                slider.move(50, curr_height)
                slider.setValue(self.instrument[i])

                curr_height += 20


    


class Painter(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'.\UI\painter.ui', self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Редактор')
        self.setMouseTracking(True)

        num = 0

        for i in self.buttonGroup.buttons():
            i.setIconSize(QSize(25, 25))
            i.num = num
            num += 1

        self.current_color = None

        self.make_palletes()

        self.prev_button_color = (self.pushButton_9, 0)

        self.buttonGroup.buttonClicked.connect(self.choose_color)
        self.buttonGroup_2.buttonClicked.connect(self.tool_change)

        self.make_menu()

        self.image = None
        self.pixmap = None
        self.tool = None
        self.tools = [i.objectName()[:-7] for i in self.buttonGroup_2.buttons()]
        self.drawing = False
        self.show_img_width = None
        self.show_img_height = None
        self.pre_image = None
        self.prev_point = None

        self.make_params_of_tools()

    def make_palletes(self):
        NUM_OF_PALLETES = 10

        self.palletes = []
        self.current_pallete = 0

        for _ in range(NUM_OF_PALLETES):
            self.palletes.append([None] * 12)

        self.choose_pallete.addItems([f'Палитра №{i + 1}' for i in range(NUM_OF_PALLETES)])
        self.choose_pallete.currentIndexChanged.connect(self.pallete_changed)

    def make_menu(self):
        self.open_file_act.triggered.connect(self.open_file)

    def make_params_of_tools(self):
        self.params = {'brush': {'size': None, 'transperency': 255}, 'eraser': {'size': None, 'transperency': 255},
                       'bucket': {'limit': 10, 'transperency': 255}, 'circle': {'size': None, 'transperency': 255, 'fill': None},
                       'rectangle': {'size': None, 'transperency': 255, 'fill': None},
                       'triangle': {'size': None, 'transperency': 255, 'fill': None}, 'line': {'size': None, 'transperency': 255}}

    def choose_color(self, button):
        if self.choosing_color.isChecked():
            color = QColorDialog.getColor(parent=self, title='Выбрать цвет')
            
            if color.isValid():
                button.setIcon(self.get_icon_with_colour(color))

                self.palletes[self.current_pallete][button.num] = color
        else:
            color = self.palletes[self.current_pallete][button.num]

            if color is not None:
                self.current_color = color
            
            self.prev_button_color = (button, self.current_pallete)

    def pallete_changed(self, index):
        self.current_pallete = index
        buttons = self.buttonGroup.buttons()

        for i in range(len(self.palletes[self.current_pallete])):
            color = self.palletes[self.current_pallete][i]

            if color is not None:
                buttons[i].setIcon(self.get_icon_with_colour(color))
            else:
                buttons[i].setIcon(QIcon())

    def tool_change(self, button):
        self.tool = button.objectName()[:-7]
        print(self.tools, self.tool)

    def get_icon_with_colour(self, color):
        image = QImage(35, 35, QImage.Format.Format_RGBA64)
        image.fill(color)
        pixmap = QPixmap.fromImage(image)
        
        return QIcon(pixmap)
    
    def open_file(self):
        name, _ = QFileDialog.getOpenFileName(self, 'Открыть файл', filter='Изображение (*.uti);;Изображение (*.png)')

        if name:  
            try:
                self.image = ImageUti(Image.open(name))
                self.pixmap = QPixmap.fromImage(self.image.get_qimage())
                self.width_of_img = self.pixmap.width()
                self.height_of_img = self.pixmap.height()

                prefer_size = round(self.width_of_img * self.height_of_img * 30 / 8699840)

                for i in self.params:
                    if 'size' in self.params[i]:
                        if self.params[i]['size'] is None:
                            self.params[i]['size'] = prefer_size
                self.update()
            except Exception:         
                try:
                    self.image = ImageUti.import_image(name)

                    if self.image == 'PASSWORD':
                        password, ok_pressed = QInputDialog.getText(self, 'Пароль', 'Изображение запаролено. Введите пароль:')

                        if ok_pressed:
                            self.image = ImageUti.import_image_with_password(name, convert_password(password))

                            if self.image == 'Incorrect password':
                                QMessageBox.critical(self, 'Ошибка', 'Неверный пароль.')
                                self.image = None
                        else:
                            self.image = None

                    if self.image is not None:
                        self.pixmap = QPixmap.fromImage(self.image.get_qimage())
                        self.width_of_img = self.pixmap.width()
                        self.height_of_img = self.pixmap.height()

                        prefer_size = round(self.width_of_img * self.height_of_img * 30 / 8699840)

                        for i in self.params:
                            if 'size' in self.params[i]:
                                if self.params[i]['size'] is None:
                                    self.params[i]['size'] = prefer_size

                        self.update()
                except Exception:
                    QMessageBox.critical(self, 'Ошибка', 'Не удалось открыть изображение')

    def paintEvent(self, event):
        if self.image is not None:
            if self.drawing:
                self.pixmap = QPixmap.fromImage(self.pre_image.get_qimage())
            else:
                self.pixmap = QPixmap.fromImage(self.image.get_qimage())
            painter = QPainter()

            painter.begin(self)
            pix = self.pixmap.scaledToWidth(self.width() - 85)
            p_h = pix.height()
            w_h = self.height()
            p_w = pix.width()

            if p_h > w_h - 125:
                pix = self.pixmap.scaledToHeight(w_h - 125)
                p_h = pix.height()
                p_w = pix.width()
                painter.drawPixmap(75, 115, p_w, p_h, pix)
            else:
                painter.drawPixmap(75, 115, p_w, p_h, pix)

            self.show_img_width = pix.width()
            self.show_img_height = pix.height()

            painter.end()

    def mousePressEvent(self, mouse):
        pos = mouse.pos()
        x, y = pos.x(), pos.y()

        if self.image is not None and self.pixmap is not None:
            width, height = self.show_img_width, self.show_img_height
            if 75 <= x <= 75 + width and 115 <= y <= 115 + height:
                if self.tool == 'bucket':
                    self.bucket_fill(x, y)
                elif self.tool == 'pipette':
                    self.pipette(x, y)
                else:
                    self.drawing = True
                    self.pre_image = ImageUti(self.image.image)
            
        return super().mouseMoveEvent(mouse)

    def mouseReleaseEvent(self, mouse):
        if self.drawing:
            if self.pre_image is not None:
                self.image = self.pre_image
                self.pre_image = None
        self.drawing = False
        self.prev_point = None
        self.update()
        return super().mouseMoveEvent(mouse)

    def mouseMoveEvent(self, mouse):
        pos = mouse.pos()
        self.preview_image(pos.x(), pos.y())
        return super().mouseMoveEvent(mouse)
    
    def preview_image(self, x, y):
        if self.image is not None and self.pixmap is not None:
            if self.drawing:
                if self.tool == 'brush':
                    if self.current_color is not None:
                        size = self.params[self.tool]['size']
                        transperency = self.params[self.tool]['transperency']

                        x -= 75
                        y -= 115

                        if 0 <= x <= self.show_img_width and 0 <= y <= self.show_img_height:
                            color = (self.current_color.red(), self.current_color.green(), self.current_color.blue(), transperency)
                            curr_point = (x / self.show_img_width * self.pre_image.image.width,
                                          y / self.show_img_height * self.pre_image.image.height)
                            
                            if self.prev_point is None:
                                self.prev_point = curr_point

                            ImageDraw.Draw(self.pre_image.image).line(self.prev_point + curr_point, color, size)
                            self.prev_point = curr_point
                            self.update()
                elif self.tool == 'eraser':
                    size = self.params[self.tool]['size']
                    transperency = self.params[self.tool]['transperency']

                    x -= 75
                    y -= 115

                    if 0 <= x <= self.show_img_width and 0 <= y <= self.show_img_height:
                        curr_point = (x / self.show_img_width * self.pre_image.image.width,
                                      y / self.show_img_height * self.pre_image.image.height)
                            
                        if self.prev_point is None:
                            self.prev_point = curr_point

                        ImageDraw.Draw(self.pre_image.image).line(self.prev_point + curr_point, (0, 0, 0, transperency), size)
                        self.prev_point = curr_point
                        self.update()
                elif self.tool == 'line':
                    if self.current_color is not None:
                        size = self.params[self.tool]['size']
                        transperency = self.params[self.tool]['transperency']

                        x -= 75
                        y -= 115

                        if 0 <= x <= self.show_img_width and 0 <= y <= self.show_img_height:
                            color = (self.current_color.red(), self.current_color.green(), self.current_color.blue(), transperency)
                            curr_point = (x / self.show_img_width * self.pre_image.image.width,
                                          y / self.show_img_height * self.pre_image.image.height)
                            
                            if self.prev_point is None:
                                self.prev_point = curr_point

                            self.pre_image = ImageUti(self.image.image.copy())

                            ImageDraw.Draw(self.pre_image.image).line(self.prev_point + curr_point, color, size)
                            self.update()
                elif self.tool == 'circle':
                    if self.current_color is not None:
                        size = self.params[self.tool]['size']
                        transperency = self.params[self.tool]['transperency']
                        fill = self.params[self.tool]['fill']

                        x -= 75
                        y -= 115

                        if 0 <= x <= self.show_img_width and 0 <= y <= self.show_img_height:
                            color = (self.current_color.red(), self.current_color.green(), self.current_color.blue(), transperency)
                            curr_point = (x / self.show_img_width * self.pre_image.image.width,
                                          y / self.show_img_height * self.pre_image.image.height)
                            
                            if self.prev_point is None:
                                self.prev_point = curr_point

                            self.pre_image = ImageUti(self.image.image.copy())

                            x0, y0, x1, y1 = self.prev_point + curr_point

                            x = sorted((x0, x1))
                            y = sorted((y0, y1))

                            ImageDraw.Draw(self.pre_image.image).ellipse((x[0], y[0], x[1], y[1]), fill, color, size)
                            self.update()
                elif self.tool == 'rectangle':
                    if self.current_color is not None:
                        size = self.params[self.tool]['size']
                        transperency = self.params[self.tool]['transperency']
                        fill = self.params[self.tool]['fill']

                        x -= 75
                        y -= 115

                        if 0 <= x <= self.show_img_width and 0 <= y <= self.show_img_height:
                            color = (self.current_color.red(), self.current_color.green(), self.current_color.blue(), transperency)
                            curr_point = (x / self.show_img_width * self.pre_image.image.width,
                                          y / self.show_img_height * self.pre_image.image.height)
                            
                            if self.prev_point is None:
                                self.prev_point = curr_point

                            self.pre_image = ImageUti(self.image.image.copy())

                            x0, y0, x1, y1 = self.prev_point + curr_point

                            x = sorted((x0, x1))
                            y = sorted((y0, y1))

                            ImageDraw.Draw(self.pre_image.image).rectangle((x[0], y[0], x[1], y[1]), fill, color, size)
                            self.update()
                elif self.tool == 'triangle':
                    if self.current_color is not None:
                        size = self.params[self.tool]['size']
                        transperency = self.params[self.tool]['transperency']
                        fill = self.params[self.tool]['fill']

                        x -= 75
                        y -= 115

                        if 0 <= x <= self.show_img_width and 0 <= y <= self.show_img_height:
                            color = (self.current_color.red(), self.current_color.green(), self.current_color.blue(), transperency)
                            curr_point = (x / self.show_img_width * self.pre_image.image.width,
                                          y / self.show_img_height * self.pre_image.image.height)
                            
                            if self.prev_point is None:
                                self.prev_point = curr_point

                            self.pre_image = ImageUti(self.image.image.copy())

                            height = curr_point[1] - self.prev_point[1]
                            width = curr_point[0] - self.prev_point[0]

                            ImageDraw.Draw(self.pre_image.image).polygon(((self.prev_point[0], self.prev_point[1]),
                                                                          (self.prev_point[0] + width // 2, self.prev_point[1] + height),
                                                                          (curr_point[0], curr_point[1] - height)), fill, color, size)
                            self.update()

    def bucket_fill(self, x, y):
        limit = self.params['bucket']['limit'] # От 0 до 300? (включительно).
        transperency = self.params['bucket']['transperency']

        if self.current_color is not None:
            x -= 75
            y -= 115
            
            color = (self.current_color.red(), self.current_color.green(), self.current_color.blue(), transperency)
            point = (x / self.show_img_width * self.image.image.width,
                     y / self.show_img_height * self.image.image.height)

            ImageDraw.floodfill(self.image.image, point, color, thresh=limit)
            self.update()

    def pipette(self, x, y):
        x -= 75
        y -= 115

        x, y = (x / self.show_img_width * self.image.image.width,
                y / self.show_img_height * self.image.image.height)
        
        button, pallete = self.prev_button_color

        color = QColor(*(self.image.image.getpixel((int(x), int(y)))[:-1]), 255)

        button.setIcon(self.get_icon_with_colour(color))

        self.palletes[pallete][button.num] = color
        self.current_color = color
                        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    program = Painter()
    program.show()
    sys.exit(app.exec())