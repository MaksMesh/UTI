from uti_api import ImageUti, WAYS_TO_CONVERT, convert_password
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QInputDialog
from PyQt6.QtGui import QPixmap, QPainter
import pathlib
import sys
import os


WIDTH_OF_WINDOW = 500
MIN_WINDOW_WIDTH = 235
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


class ImageView(QMainWindow):
    def __init__(self, args):
        super().__init__()
        self.default_status()
        self.setWindowTitle('Просмотр')
        self.theme = 0
        self.path_to_img = None
        self.initUI()
        self.load_params()
        
        if len(args) > 1:
            self.load_image(args[1])
            
    def default_status(self):
        self.image = None
        self.pixmap = None
        self.setMinimumSize(MIN_WINDOW_WIDTH, 0)

    def load_image(self, img):
        try:
            self.image, self.way = ImageUti.import_image_with_way(img)

            if self.image == 'PASSWORD':
                password, ok_pressed = QInputDialog.getText(self, 'Пароль', 'Изображение запаролено. Введите пароль:')

                if ok_pressed:
                    self.image = ImageUti.import_image_with_password(img, convert_password(password))

                    if self.image == 'Incorrect password':
                        QMessageBox.critical(self, 'Ошибка', 'Неверный пароль.')
                        self.image = None
                    else:
                        self.password = password
                else:
                    self.image = None

            if self.image is not None:
                self.path_to_img = img
                self.pixmap = QPixmap.fromImage(self.image.get_qimage())
                self.width_of_img = self.pixmap.width()
                self.height_of_img = self.pixmap.height()

                rect = self.geometry()
                rect.setWidth(WIDTH_OF_WINDOW)
                rect.setHeight(round(WIDTH_OF_WINDOW / self.width_of_img * self.height_of_img))

                self.setGeometry(rect)

                self.setMinimumSize(MIN_WINDOW_WIDTH, round(MIN_WINDOW_WIDTH / self.width_of_img * self.height_of_img))

                self.update()
        except Exception:
            QMessageBox.critical(self, 'Ошибка', 'Не удалось открыть изображение')

    def paintEvent(self, event):
        if self.pixmap is not None:
            painter = QPainter()

            painter.begin(self)
            pix = self.pixmap.scaledToWidth(self.width() - 20)
            p_h = pix.height()
            w_h = self.height()
            p_w = pix.width()
            w_w = self.width()

            if p_h > w_h - 45:
                pix = self.pixmap.scaledToHeight(w_h - 45)
                p_h = pix.height()
                p_w = pix.width()
                center_w = (w_w - p_w) // 2 - 10
                painter.drawPixmap(10 + center_w, 35, p_w, p_h, pix)
            else:
                center_h = (w_h - p_h - 45) // 2
                painter.drawPixmap(10, 35 + center_h, p_w, p_h, pix)

            painter.end()

    def initUI(self):
        self.setGeometry(100, 100, 200, 100)

        menu = self.menuBar()

        file = menu.addMenu('Файл')
        change = menu.addMenu('Правка')
        settings = menu.addMenu('Настройки')

        open_file = file.addAction('Открыть')
        open_file.triggered.connect(self.open_file)
        save_file = file.addAction('Сохранить как')
        save_file.triggered.connect(self.save_image)
        exitt = file.addAction('Выход')
        exitt.triggered.connect(self.close)

        redact_image = change.addAction('Редактировать изображение')
        redact_image.triggered.connect(self.redact_image)

        change_theme = settings.addAction('Сменить тему')
        change_theme.triggered.connect(self.change_theme)

    def open_file(self):
        name, _ = QFileDialog.getOpenFileName(self, 'Открыть файл', filter='Изображение (*.uti)')

        if name:           
            self.load_image(name)
            
    def save_image(self):
        if self.image is not None and self.pixmap is not None:
            name, ok_pressed = QFileDialog.getSaveFileName(self, 'Сохранить файл', filter='Изображение (*.uti)')

            if ok_pressed:
                try:
                    convert_way = WAYS_TO_CONVERT[self.way][0]

                    if convert_way.__name__ == 'PASSWORD_ENCODE':
                        self.image.export(name, convert_way, convert_password(self.password))
                    else:
                        self.image.export(name, convert_way)
                    QMessageBox.information(self, 'Информация', 'Успешно!')
                except Exception:
                    QMessageBox.critical(self, 'Ошибка', 'Не удалось сохранить изображение')
        else:
            QMessageBox.critical(self, 'Ошибка', 'Изображение не открыто!')

    def redact_image(self):
        if self.path_to_img is None:
            QMessageBox.critical(self, 'Ошибка', 'Изображение не открыто!')
        else:
            path_to_painter = pathlib.Path(r'C:\Program Files\UTI') / 'painter.exe'
            if path_to_painter.exists():
                os.startfile(path_to_painter, arguments='"' + self.path_to_img + '"')
            else:
                QMessageBox.critical(self, 'Ошибка', 'Не удаётся найти графический редактор.')

    def change_theme(self):
        theme, ok_pressed = QInputDialog.getItem(self, 'Выбрать тему', 'Выберите тему:', THEMES, self.theme, False)

        if ok_pressed:
            self.theme = THEMES.index(theme)
            self.change_theme_now()

    def change_theme_now(self):
        if self.theme == 0:
            self.setStyleSheet('')
        elif self.theme == 1:
            self.setStyleSheet(WHITE_THEME)
        elif self.theme == 2:
            self.setStyleSheet(BLACK_THEME)

    def closeEvent(self, event):
        path_m = pathlib.Path.home() / 'AppData' / 'Local' / 'MaksMesh'
        path_m.mkdir(exist_ok=True)
        path_u = path_m / 'UTI'
        path_u.mkdir(exist_ok=True)
        path_p = path_u / 'Viewer'
        path_p.mkdir(exist_ok=True)

        with open(path_p / 'theme.txt', 'w') as file:
            file.write(THEMES[self.theme])

    def load_params(self):
        try:
            with open(pathlib.Path.home() / 'AppData' / 'Local' / 'MaksMesh' / 'UTI' / 'Viewer' / 'theme.txt') as file:
                self.theme = THEMES.index(file.readline())
                self.change_theme_now()
        except FileNotFoundError:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    program = ImageView(app.arguments())
    program.show()
    sys.exit(app.exec())