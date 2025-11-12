from uti_api import ImageUti, WAYS_TO_CONVERT, convert_password
from PIL import Image, ImageDraw
from PyQt6 import uic
from PyQt6.QtWidgets import (QMainWindow, QApplication, QFileDialog, QMessageBox, QInputDialog, QColorDialog,
                             QPushButton, QSlider, QLabel, QCheckBox, QSpinBox)
from PyQt6.QtGui import QIcon, QPainter, QPixmap, QImage, QColor, QShortcut, QKeySequence
from PyQt6.QtCore import QSize, Qt
import sys
import pathlib
from math import sqrt
import csv


THEMES = ('По умолчанию', 'Светлая', 'Тёмная')
BLACK_THEME = '''
        QMainWindow {
            background-color: #171717;
        }
        QWidget {
            background-color: #171717;
        }
        QComboBox {
            color: #787777;
            background-color: #262626;
            selection-background-color: #262626;
        }
        QComboBox QAbstractItemView {
            color: #787777;
            background-color: #262626;
            border: 2px solid #262626;
        }
        QSpinBox {
            color: #787777;
            background-color: #262626;
        }
        QCheckBox {
            color: #787777;
        }
        QLabel {
            color: #787777;
        }
        QPushButton {
            background-color: #262626;
        }
        QMenu {
            background-color: #121212;
            color: #787777;
        }
        QMenu::item::selected {
            background-color: #303030;
        }
        QMenuBar {
            background-color: #121212;
            color: #787777;
        }
        QMenuBar::item {
            background-color: #121212;
        }
        QMenuBar::item::selected {
            background-color: #303030;
        }'''

WHITE_THEME = '''
        QMainWindow {
            background-color: #ebebeb;
        }
        QWidget {
            background-color: #ebebeb;
        }
        QComboBox {
            color: #000;
            background-color: #b0b0b0;
            selection-background-color: #b0b0b0;
        }
        QComboBox QAbstractItemView {
            color: #000;
            background-color: #b0b0b0;
            border: 2px solid #b0b0b0;
        }
        QSpinBox {
            color: #000;
            background-color: #b0b0b0;
        }
        QCheckBox {
            color: #000;
        }
        QLabel {
            color: #000;
        }
        QPushButton {
            background-color: #b0b0b0;
        }
        QMenu {
            background-color: #dbd9d9;
            color: #000;
        }
        QMenu::item::selected {
            background-color: #a6a6a6;
        }
        QMenuBar {
            background-color: #f2f2f2;
            color: #000;
        }
        QMenuBar::item {
            background-color: #dbd9d9;
        }
        QMenuBar::item::selected {
            background-color: #a6a6a6;
        }'''


class SaveDataDial(QMainWindow):
    def __init__(self, parent, data):
        super().__init__(parent=parent)
        self.data = data
        self.initUI()

    def initUI(self):
        self.setFixedSize(230, 110)
        self.setWindowTitle('Настройки сохранения')

        self.label1 = QLabel(self)
        self.label1.setText('Палитры')
        self.label1.move(10, 10)

        self.label2 = QLabel(self)
        self.label2.setText('Настройки инструментов')
        self.label2.move(10, 40)
        self.label2.setFixedWidth(150)

        self.check1 = QCheckBox(self)
        self.check1.setChecked(self.data.get('palletes', False))
        self.check1.move(70, 10)

        self.check2 = QCheckBox(self)
        self.check2.setChecked(self.data.get('params', False))
        self.check2.move(160, 40)

        self.fin_button = QPushButton(self)
        self.fin_button.setText('Подтвердить')
        self.fin_button.move(10, 70)
        self.fin_button.clicked.connect(self.fin)

        self.close_button = QPushButton(self)
        self.close_button.setText('Отмена')
        self.close_button.move(120, 70)
        self.close_button.clicked.connect(self.close)

    def fin(self):
        self.data['palletes'] = self.check1.isChecked()
        self.data['params'] = self.check2.isChecked()
        self.close()


class InstrumentParams(QMainWindow):
    def __init__(self, parent, name, instrument, maximum_size):
        super().__init__(parent=parent)

        attributes_order = ['limit', 'size', 'transperency', 'fill']
        self.localization = {'limit': 'Порог', 'size': 'Размер', 'transperency': 'Непрозрачность', 'fill': 'Заливка',
                        'brush': 'Кисть', 'eraser': 'Ластик', 'bucket': 'Заливка', 'circle': 'Круг',
                        'rectangle': 'Прямоугольник', 'triangle': 'Треугольник', 'line': 'Линия'}
        self.maximum_size = maximum_size
        self.instrument = instrument
        self.new_params = {}
        
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
                slider.move(190, curr_height + 2)
                slider.setOrientation(Qt.Orientation.Horizontal)

                if self.instrument[i] is not None:
                    slider.setValue(self.instrument[i])

                spin_box = QSpinBox(self)
                spin_box.move(120, curr_height)
                spin_box.setFixedWidth(65)
                spin_box.setMinimum(slider.minimum())
                spin_box.setMaximum(slider.maximum())
                spin_box.setValue(slider.value())

                self.size_sl = slider
                self.size_sp = spin_box

                slider.valueChanged.connect(self.size_value_changed)
                spin_box.valueChanged.connect(self.size_value_changed)

                curr_height += 30
            elif i == 'transperency':
                label = QLabel(self)
                label.move(10, curr_height)
                label.setText(self.localization[i])

                slider = QSlider(self)
                slider.setMaximum(255)
                slider.setMinimum(0)
                slider.move(190, curr_height + 2)
                slider.setValue(self.instrument[i])
                slider.setOrientation(Qt.Orientation.Horizontal)
                slider.valueChanged.connect(self.transperency_value_changed)

                spin_box = QSpinBox(self)
                spin_box.move(120, curr_height)
                spin_box.setFixedWidth(65)
                spin_box.setMinimum(slider.minimum())
                spin_box.setMaximum(slider.maximum())
                spin_box.setValue(slider.value())
                spin_box.valueChanged.connect(self.transperency_value_changed)

                self.transperency_sl = slider
                self.transperency_sp = spin_box

                curr_height += 30
            elif i == 'limit':
                label = QLabel(self)
                label.move(10, curr_height)
                label.setText(self.localization[i])

                slider = QSlider(self)
                slider.setMaximum(300)
                slider.setMinimum(0)
                slider.move(190, curr_height + 2)
                slider.setValue(self.instrument[i])
                slider.setOrientation(Qt.Orientation.Horizontal)
                slider.valueChanged.connect(self.limit_value_changed)

                spin_box = QSpinBox(self)
                spin_box.move(120, curr_height)
                spin_box.setFixedWidth(65)
                spin_box.setMinimum(slider.minimum())
                spin_box.setMaximum(slider.maximum())
                spin_box.setValue(slider.value())
                spin_box.valueChanged.connect(self.limit_value_changed)

                self.limit_sl = slider
                self.limit_sp = spin_box

                curr_height += 30
            elif i == 'fill':
                label1 = QLabel(self)
                label1.move(10, curr_height)
                label1.setText(self.localization[i])

                label2 = QLabel(self)
                label2.move(30, curr_height + 20)
                label2.setText('Цвет заливки:')

                checkbox = QCheckBox(self)
                checkbox.move(70, curr_height + 1)

                color_button = QPushButton(self)
                color_button.move(115, curr_height + 20)
                color_button.setFixedSize(30, 30)
                color_button.setIconSize(QSize(20, 20))
                color_button.clicked.connect(self.fill_color_choose)

                if self.instrument[i] is not None:
                    checkbox.setChecked(True)
                    color = QColor(*self.instrument[i])
                    color_button.setIcon(self.get_icon_with_colour(color))
                    self.new_params['fill'] = [True, color]
                else:
                    color_button.setDisabled(True)
                    self.new_params['fill'] = [False, QColor()]

                checkbox.stateChanged.connect(self.use_fill_changed)

                self.fill_color_button = color_button

                curr_height += 50

        curr_height += 20

        fin_button = QPushButton(self)
        fin_button.move(40, curr_height)
        fin_button.setText('Подтвердить')
        fin_button.clicked.connect(self.fin)

        exit_button = QPushButton(self)
        exit_button.move(150, curr_height)
        exit_button.setText('Отмена')
        exit_button.clicked.connect(self.close)

        curr_height += 40

        self.setFixedSize(290, curr_height)

    def get_icon_with_colour(self, color):
        image = QImage(35, 35, QImage.Format.Format_RGBA64)
        image.fill(color)
        pixmap = QPixmap.fromImage(image)
        
        return QIcon(pixmap)

    def limit_value_changed(self, value):
        self.limit_sl.setValue(value)
        self.limit_sp.setValue(value)
        self.new_params['limit'] = value

    def transperency_value_changed(self, value):
        self.transperency_sl.setValue(value)
        self.transperency_sp.setValue(value)
        self.new_params['transperency'] = value

    def size_value_changed(self, value):
        self.size_sl.setValue(value)
        self.size_sp.setValue(value)
        self.new_params['size'] = value

    def use_fill_changed(self, value):
        self.new_params['fill'][0] = False if value == 0 else True

        if self.new_params['fill'][0]:
            self.fill_color_button.setDisabled(False)
        else:
            self.fill_color_button.setDisabled(True)

    def fill_color_choose(self):
        if self.instrument['fill'] is None:
            color = QColorDialog.getColor(parent=self, title='Выбор цвета')
        else:
            curr_color = self.new_params.get('fill', [0, QColor(*self.instrument['fill'])])[1]

            color = QColorDialog.getColor(curr_color, self, 'Выбор цвета')

        if color.isValid():
            self.new_params['fill'][1] = color
            self.fill_color_button.setIcon(self.get_icon_with_colour(color))

    def fin(self):
        fin = self.new_params.copy()

        if 'fill' in fin:
            if fin['fill'][0]:
                color = fin['fill'][1]

                if color.isValid():
                    fin['fill'] = (color.red(), color.green(), color.blue())
                else:
                    fin['fill'] = None
            else:
                fin['fill'] = None

        for i in fin:
            self.instrument[i] = fin[i]

        self.close()


class NewImageDial(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.curr_color = (255, 255, 255)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Создать')
        self.setFixedSize(200, 210)
        
        self.width_sp = QSpinBox(self)
        self.width_sp.move(80, 10)
        self.width_sp.setMinimum(1)
        self.width_sp.setMaximum(99999)
        self.width_sp.setValue(1754)

        self.width_l = QLabel(self)
        self.width_l.setText('Ширина:')
        self.width_l.move(10, 10)

        self.height_sp = QSpinBox(self)
        self.height_sp.move(80, 50)
        self.height_sp.setMinimum(1)
        self.height_sp.setMaximum(99999)
        self.height_sp.setValue(1240)

        self.height_l = QLabel(self)
        self.height_l.setText('Высота:')
        self.height_l.move(10, 50)

        self.fill_l1 = QLabel(self)
        self.fill_l1.move(10, 90)
        self.fill_l1.setText('Заливка')

        self.fill_l2 = QLabel(self)
        self.fill_l2.move(30, 120)
        self.fill_l2.setText('Цвет заливки:')

        self.fill_check = QCheckBox(self)
        self.fill_check.move(70, 91)
        self.fill_check.setChecked(True)
        self.fill_check.stateChanged.connect(self.use_fill_changed)

        self.fill_color = QPushButton(self)
        self.fill_color.move(115, 120)
        self.fill_color.setFixedSize(30, 30)
        self.fill_color.setIconSize(QSize(20, 20))
        self.fill_color.setIcon(self.get_icon_with_colour(QColor(*self.curr_color)))
        self.fill_color.clicked.connect(self.fill_color_choose)

        self.fin_button = QPushButton(self)
        self.fin_button.move(10, 170)
        self.fin_button.setText('ОК')
        self.fin_button.setFixedWidth(85)
        self.fin_button.clicked.connect(self.fin)

        self.exit_button = QPushButton(self)
        self.exit_button.move(105, 170)
        self.exit_button.setText('Отмена')
        self.exit_button.setFixedWidth(85)
        self.exit_button.clicked.connect(self.close)

    def get_icon_with_colour(self, color):
        image = QImage(35, 35, QImage.Format.Format_RGBA64)
        image.fill(color)
        pixmap = QPixmap.fromImage(image)
        
        return QIcon(pixmap)
    
    def fill_color_choose(self):
        if self.curr_color is None:
            color = QColorDialog.getColor(parent=self, title='Выбор цвета')
        else:
            color = QColorDialog.getColor(QColor(*self.curr_color), self, 'Выбор цвета')

        if color.isValid():
            self.curr_color = (color.red(), color.green(), color.blue())
            self.fill_color.setIcon(self.get_icon_with_colour(color))

    def use_fill_changed(self, value):
        if value:
            self.fill_color.setDisabled(False)
        else:
            self.fill_color.setDisabled(True)

    def fin(self):
        width = self.width_sp.value()
        height = self.height_sp.value()

        if self.fill_check.isChecked():
            image = Image.new('RGBA', (width, height), self.curr_color)
        else:
            image = Image.new('RGBA', (width, height))
        
        self.parent().load_image(image)
        self.close()


class Painter(QMainWindow):
    def __init__(self, args):
        super().__init__()
        uic.loadUi(r'.\UI\painter.ui', self)
        self.initUI()
        self.load_saved_data()

        if len(args) > 1:
            self.open_file(args[1])

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

        for button in self.buttonGroup_2.buttons():
            tool = button.objectName()[:-7]
            button.setIcon(QIcon(f'UI/icons/{tool}.png'))
            button.setIconSize(button.size())

        self.stack_size = 30
        self.image = None
        self.pixmap = None
        self.tool = None
        self.tools = [i.objectName()[:-7] for i in self.buttonGroup_2.buttons()]
        self.drawing = False
        self.show_img_width = None
        self.show_img_height = None
        self.pre_image = None
        self.prev_point = None
        self.maximum_size = None
        self.stack = [None] * self.stack_size
        self.curr_stack = -1
        self.changed = False
        self.save_data = {'palletes': True, 'params': True}
        self.theme = 0

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
        self.new_act.triggered.connect(self.new_file)
        self.save_uti_act.triggered.connect(self.export_uti)
        self.save_png_act.triggered.connect(self.export_png)
        self.exit_act.triggered.connect(self.almost_close)
        self.back_act.triggered.connect(self.undo)
        self.straight_act.triggered.connect(self.unundo)
        self.num_images_act.triggered.connect(self.change_stack_len)
        self.theme_act.triggered.connect(self.change_theme)
        self.saving_data_act.triggered.connect(self.change_saving_data)
        self.help_action.triggered.connect(self.help)

        QShortcut(QKeySequence('CTRL+Z'), self).activated.connect(self.undo)
        QShortcut(QKeySequence('CTRL+Y'), self).activated.connect(self.unundo)

    def make_params_of_tools(self):
        self.params = {'brush': {'size': None, 'transperency': 255}, 'eraser': {'size': None, 'transperency': 0},
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

            if self.theme == 0:
                bg = ''
            elif self.theme == 1:
                bg = 'background-color: #b0b0b0;'
            else:
                bg = 'background-color: #262626;'

            if color is not None:
                self.current_color = color

                for i in range(12):
                    self.buttonGroup.buttons()[i].setStyleSheet('' + bg)
                
                curr_b = self.buttonGroup.buttons()[self.buttonGroup.buttons().index(button)]
                curr_b.setStyleSheet('border: 2px solid #3498db;' + bg)
            
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
        tool = button.objectName()[:-7]

        if self.set_instrument_box.isChecked():
            if tool in self.params:
                if self.maximum_size is not None:
                    max_size = self.maximum_size
                else:
                    max_size = 500

                params_dialog = InstrumentParams(self, tool, self.params[tool], max_size)
                params_dialog.show()
            else:
                if tool == 'pipette':
                    tool = 'Пипетка'
                QMessageBox.information(self, 'Информация', f'Инструмент "{tool}" не имеет настроек.')
        else:
            if self.theme == 0:
                bg = ''
            elif self.theme == 1:
                bg = 'background-color: #b0b0b0;'
            else:
                bg = 'background-color: #262626;'

            for i in range(8):
                self.buttonGroup_2.buttons()[i].setStyleSheet('' + bg)

            self.buttonGroup_2.buttons()[self.tools.index(tool)].setStyleSheet('border: 2px solid #3498db;' + bg)
            self.tool = tool

    def get_icon_with_colour(self, color):
        image = QImage(35, 35, QImage.Format.Format_RGBA64)
        image.fill(color)
        pixmap = QPixmap.fromImage(image)
        
        return QIcon(pixmap)
    
    def open_file(self, name=None):
        if name is None:
            name, _ = QFileDialog.getOpenFileName(self, 'Открыть файл', filter='Изображение (*.uti);;Изображение (*.png)')

        if name:  
            try:
                image = Image.open(name)
                self.load_image(image)
            except Exception:         
                try:
                    image = ImageUti.import_image(name)

                    if image == 'PASSWORD':
                        password, ok_pressed = QInputDialog.getText(self, 'Пароль', 'Изображение запаролено. Введите пароль:')

                        if ok_pressed:
                            image = ImageUti.import_image_with_password(name, convert_password(password))

                            if image == 'Incorrect password':
                                QMessageBox.critical(self, 'Ошибка', 'Неверный пароль.')
                                image = None
                        else:
                            image = None

                    if image is not None:
                        self.image = image
                        self.pixmap = QPixmap.fromImage(self.image.get_qimage())
                        self.width_of_img = self.pixmap.width()
                        self.height_of_img = self.pixmap.height()

                        s = self.width_of_img * self.height_of_img

                        prefer_size = round(s * 30 / 8699840)
                        self.maximum_size = round(sqrt(s))

                        for i in self.params:
                            if 'size' in self.params[i]:
                                if self.params[i]['size'] is None:
                                    self.params[i]['size'] = prefer_size
                                elif self.params[i]['size'] > self.maximum_size:
                                    self.params[i]['size'] = self.maximum_size

                        self.stack = [None] * self.stack_size
                        self.curr_stack = -1
                        self.stack[-1] = ImageUti(self.image.image.copy())

                        self.update()
                except Exception:
                    QMessageBox.critical(self, 'Ошибка', 'Не удалось открыть изображение')

    def load_image(self, image):
        self.image = ImageUti(image)
        self.pixmap = QPixmap.fromImage(self.image.get_qimage())
        self.width_of_img = self.pixmap.width()
        self.height_of_img = self.pixmap.height()
        s = self.width_of_img * self.height_of_img

        prefer_size = round(s * 30 / 8699840)
        self.maximum_size = round(sqrt(s))

        for i in self.params:
            if 'size' in self.params[i]:
                if self.params[i]['size'] is None:
                    self.params[i]['size'] = prefer_size
                elif self.params[i]['size'] > self.maximum_size:
                    self.params[i]['size'] = self.maximum_size

        self.stack = [None] * self.stack_size
        self.curr_stack = -1
        self.stack[-1] = ImageUti(self.image.image.copy())

        self.update()

    def new_file(self):
        NewImageDial(self).show()

    def export_uti(self):
        if self.image is None:
            QMessageBox.critical(self, 'Ошибка', 'Изображение не открыто!')
        else:
            file, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', filter='Изображение (*.uti)')

            if file:
                way_titles = [i[1] for i in WAYS_TO_CONVERT]
                way, ok_pressed = QInputDialog.getItem(self, 'Способ', 'Выберите способ конвертации:', way_titles, 0, False)

                if ok_pressed:
                    if way == 'Password way':
                        password, ok_pressed = QInputDialog.getText(self, 'Пароль', 'Введите пароль:')

                        if ok_pressed and password:
                            try:
                                self.image.export(file, WAYS_TO_CONVERT[way_titles.index(way)][0], convert_password(password))
                            except Exception:
                                QMessageBox.critical(self, 'Ошибка', 'Не удалось экспортировать изображение')
                            else:
                                QMessageBox.information(self, 'Информация', 'Успешно!')
                    else:
                        try:
                            self.image.export(file, WAYS_TO_CONVERT[way_titles.index(way)][0])
                        except Exception:
                            QMessageBox.critical(self, 'Ошибка', 'Не удалось экспортировать изображение')
                        else:
                            QMessageBox.information(self, 'Информация', 'Успешно!')

    def export_png(self):
        if self.image is None:
            QMessageBox.critical(self, 'Ошибка', 'Изображение не открыто!')
        else:
            file, _ = QFileDialog.getSaveFileName(self, 'Сохранить файл', filter='Изображение (*.png)')

            if file:
                try:
                    self.image.image.save(file)
                except Exception:
                    QMessageBox.critical(self, 'Ошибка', 'Не удалось экспортировать изображение')
                else:
                    QMessageBox.information(self, 'Информация', 'Успешно!')

    def almost_close(self):
        valid = QMessageBox.question(self, 'Выход', 'Вы уверены?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if valid == QMessageBox.StandardButton.Yes:
            self.close()

    def undo(self):
        ind = self.curr_stack - 1

        if -self.stack_size < ind < 0:
            if self.stack[ind] is not None:
                self.curr_stack = ind
                self.image = ImageUti(self.stack[ind].image.copy())
                self.update()

    def unundo(self):
        ind = self.curr_stack + 1

        if -self.stack_size < ind < 0:
            if self.stack[ind] is not None:
                self.curr_stack = ind
                self.image = ImageUti(self.stack[ind].image.copy())
                self.update()

    def change_theme(self):
        theme, ok_pressed = QInputDialog.getItem(self, 'Выбрать тему', 'Выберите тему:', THEMES, self.theme, False)

        if ok_pressed:
            self.theme = THEMES.index(theme)
            self.change_theme_now()

    def change_stack_len(self):
        result, ok_pressed = QInputDialog.getInt(self, 'Длина стека', 'Введите новую длину стека:', self.stack_size, 1, 1000)

        if ok_pressed:
            self.stack_size = result
            self.stack = self.stack[-self.stack_size:]

    def change_saving_data(self):
        SaveDataDial(self, self.save_data).show()

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
        self.changed = False
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
                    self.preview_image(x, y)
            
        return super().mouseMoveEvent(mouse)

    def mouseReleaseEvent(self, mouse):
        if self.image is not None:
            if self.drawing:
                if self.pre_image is not None:
                    self.image = self.pre_image
                    self.pre_image = None
                    
                    if self.changed:
                        self.add_image_to_stack(self.image)
            self.drawing = False
            self.prev_point = None

            self.update()

        return super().mouseMoveEvent(mouse)

    def mouseMoveEvent(self, mouse):
        pos = mouse.pos()
        self.preview_image(pos.x(), pos.y())
        return super().mouseMoveEvent(mouse)
    
    def add_image_to_stack(self, image):
        if self.curr_stack != -1:
            self.stack = self.stack[:self.curr_stack + 1]
            self.stack.append(ImageUti(image.image.copy()))
            if len(self.stack) < self.stack_size:
                self.stack = [None] * (self.stack_size - len(self.stack)) + self.stack
            else:
                self.stack = self.stack[-self.stack_size:]
            self.curr_stack = -1
        else:
            self.stack.append(ImageUti(image.image.copy()))
            self.stack = self.stack[-self.stack_size:]
    
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

                            draw = ImageDraw.Draw(self.pre_image.image)
                            draw.line(self.prev_point + curr_point, color, size)
                            draw.circle(curr_point, size // 2, color)

                            self.prev_point = curr_point
                            self.changed = True
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

                        draw = ImageDraw.Draw(self.pre_image.image)
                        draw.line(self.prev_point + curr_point, (0, 0, 0, transperency), size)
                        draw.circle(curr_point, size // 2, (0, 0, 0, transperency))
                        self.prev_point = curr_point
                        self.changed = True
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
                            self.changed = True
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
                            self.changed = True
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
                            self.changed = True
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
                            self.changed = True
                            self.update()

    def bucket_fill(self, x, y):
        limit = self.params['bucket']['limit']
        transperency = self.params['bucket']['transperency']

        if self.current_color is not None:
            x -= 75
            y -= 115
            
            color = (self.current_color.red(), self.current_color.green(), self.current_color.blue(), transperency)
            point = (x / self.show_img_width * self.image.image.width,
                     y / self.show_img_height * self.image.image.height)

            ImageDraw.floodfill(self.image.image, point, color, thresh=limit)
            self.add_image_to_stack(self.image)

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

        for i in range(12):
            self.buttonGroup.buttons()[i].setStyleSheet('')

        self.buttonGroup.buttons()[self.buttonGroup.buttons().index(button)].setStyleSheet('border: 2px solid #3498db;')

    def load_saved_data(self):
        path_m = pathlib.Path.home() / 'AppData' / 'Local' / 'MaksMesh'
        path_m.mkdir(exist_ok=True)
        path_u = path_m / 'UTI'
        path_u.mkdir(exist_ok=True)
        path_p = path_u / 'Painter'
        path_p.mkdir(exist_ok=True)

        try:
            with open(path_p / 'data.txt') as file:
                data = file.read().split('\n')

                for i in data:
                    if not i:
                        continue

                    key, value = i.split(':')

                    if value == 'True':
                        value = True
                    else:
                        value = False

                    self.save_data[key] = value

        except Exception:
            pass
        
        if self.save_data['palletes']:
            try:
                with open(path_p / 'palletes.csv') as file:
                    data = list(csv.reader(file))
                    fin = []

                    for pallete in data:
                        now = []
                        for color in pallete:
                            if color == 'None':
                                now.append(None)
                            else:
                                r, g, b = int(color[:3]), int(color[3:6]), int(color[6:9])
                                now.append(QColor(r, g, b))
                        fin.append(now)

                    self.palletes = fin

                self.pallete_changed(0)
            except Exception:
                pass
        
        if self.save_data['params']:
            try:
                with open(path_p / 'params.csv') as file:
                    data = list(csv.reader(file))
                    params_order = data[0][1:]

                    for row in data[1:]:
                        tool = row[0]

                        for param, value in zip(params_order, row[1:]):
                            if value in ('None', 'NULL'):
                                continue
                            
                            if param in ('limit', 'size', 'transperency'):
                                value = int(value)
                            
                            if param == 'fill':
                                value = (int(value[:3]), int(value[3:6]), int(value[6:9]))

                            self.params[tool][param] = value
            except Exception:
                pass

        try:
            with open(path_p / 'theme.txt') as file:
                self.theme = THEMES.index(file.readline())
                self.change_theme_now()
        except Exception:
            pass

        try:
            with open(path_p / 'len_stack.txt') as file:
                data = int(file.readline())
                
                if data > 0:
                    self.stack_size = data
                    self.stack = self.stack[-self.stack_size:]
        except Exception:
            pass

    def closeEvent(self, event):
        path_m = pathlib.Path.home() / 'AppData' / 'Local' / 'MaksMesh'
        path_m.mkdir(exist_ok=True)
        path_u = path_m / 'UTI'
        path_u.mkdir(exist_ok=True)
        path_p = path_u / 'Painter'
        path_p.mkdir(exist_ok=True)

        data = []

        for key, value in self.save_data.items():
            if value:
                data.append(f'{key}:True')
            else:
                data.append(f'{key}:False')

        with open(path_p / 'data.txt', 'w') as file:
            file.write('\n'.join(data))

        data = []

        for pallete in self.palletes:
            now = []
            for color in pallete:
                if color is None:
                    now.append('None')
                else:
                    r, g, b = color.red(), color.green(), color.blue()
                    now.append(f'{r:0>3}{g:0>3}{b:0>3}')
            data.append(now)
                        
        with open(path_p / 'palletes.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

        params_order = ['limit', 'size', 'transperency', 'fill']
        data = [['tool'] + params_order]

        for tool in self.tools:
            if tool not in self.params:
                continue

            now = [tool]
            for param in params_order:
                item = self.params[tool].get(param, 'NULL')

                if type(item) is tuple:
                    item = f'{item[0]:0>3}{item[1]:0>3}{item[2]:0>3}'

                now.append(str(item))

            data.append(now)

        with open(path_p / 'params.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

        with open(path_p / 'len_stack.txt', 'w') as file:
            file.write(str(self.stack_size))

        with open(path_p / 'theme.txt', 'w', newline='') as file:
            file.write(THEMES[self.theme])

    def change_theme_now(self):
        self.current_color = None
        for i in range(12):
            self.buttonGroup.buttons()[i].setStyleSheet('')

        for i in range(8):
            self.buttonGroup_2.buttons()[i].setStyleSheet('')

        if self.theme == 0:
            self.setStyleSheet('')
        elif self.theme == 1:
            self.setStyleSheet(WHITE_THEME)
        elif self.theme == 2:
            self.setStyleSheet(BLACK_THEME)
    
    def help(self):
        text = 'Левая панель представляет собой выбор инструментов, для того, чтобы выбрать инструмент, нажмите на него без выбранной галочки "Настроить инструмент". Верхняя панель представляет собой выбор цветов, для того, чтобы выбрать цвет, нажмите на него без выбранной галочки "Настроить цвет", прдеварительно его настроив. Если цвет и инструмент выбран, то вы сможете рисовать!'
        QMessageBox.information(self, 'Помощь', text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    program = Painter(app.arguments())
    program.show()
    sys.exit(app.exec())