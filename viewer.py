from uti_api import ImageUti, WAYS_TO_CONVERT, convert_password
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QInputDialog
from PyQt6.QtGui import QPixmap, QPainter
import sys


WIDTH_OF_WINDOW = 500
MIN_WINDOW_WIDTH = 235
THEMES = ('По умолчанию',)


class ImageView(QMainWindow):
    def __init__(self, args):
        super().__init__()
        self.default_status()
        self.setWindowTitle('Просмотр')
        self.initUI()
        
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
            pix = self.pixmap.scaledToWidth(self.width())
            p_h = pix.height()
            w_h = self.height()
            p_w = pix.width()
            w_w = self.width()

            if p_h > w_h:
                pix = self.pixmap.scaledToHeight(w_h)
                p_h = pix.height()
                p_w = pix.width()
                center_w = (w_w - p_w) // 2
                painter.drawPixmap(10 + center_w, 35, p_w - 20, p_h - 45, pix)
            else:
                center_h = (w_h - p_h) // 2
                painter.drawPixmap(10, 35 + center_h, p_w - 20, p_h - 45, pix)

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
        ...

    def change_theme(self):
        theme, ok_pressed = QInputDialog.getItem(self, 'Выбрать тему', 'Выберите тему:', THEMES, 0, False)

        if ok_pressed:
            theme = THEMES.index(theme)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    program = ImageView(app.arguments())
    program.show()
    sys.exit(app.exec())