from uti_api import ImageUti, WAYS_TO_CONVERT, convert_password, PasswordError
from PIL import Image
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
import sys


class Convertor(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'UI\convertator.ui', self)

        self.shown = True
        self.hide_show_params()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Ковертатор')

        self.mode_type_combo.addItems(['PNG -> UTI', 'UTI -> PNG'])
        self.mode_type_combo.currentIndexChanged.connect(self.mode_changed)

        self.first_file_button.clicked.connect(self.find_source_file)
        self.final_file_button.clicked.connect(self.find_final_file)
        self.params_button.clicked.connect(self.hide_show_params)

        self.mode_of_convert.addItems([i[1] for i in WAYS_TO_CONVERT])
        self.mode_of_convert.currentIndexChanged.connect(self.show_password)

        self.theme.addItems(['По умолчанию'])

        self.convert_button.clicked.connect(self.convert)

    def find_source_file(self):
        filt = 'Изображение (*.uti)' if self.mode_type_combo.currentIndex() else ''
        file, _ = QFileDialog.getOpenFileName(self, 'Выберите файл', filter=filt)
        self.first_file.setText(file)

    def find_final_file(self):
        filt = 'Изображение (*.png)' if self.mode_type_combo.currentIndex() else 'Изображение (*.uti)'
        file, _ = QFileDialog.getSaveFileName(self, 'Выберите файл', filter=filt)
        self.final_file.setText(file)

    def hide_show_params(self):
        if self.shown:
            self.mode_of_convert_label.hide()
            self.mode_of_convert.hide()
            self.password.hide()
            self.password_label.hide()
            self.theme.hide()
            self.theme_label.hide()

            self.params_button.setText('Показать')
            self.shown = False
        else:
            self.mode_of_convert_label.show()
            self.mode_of_convert.show()
            self.password.show()
            self.password_label.show()
            self.theme.show()
            self.theme_label.show()

            self.params_button.setText('Спрятать')
            self.shown = True

    def mode_changed(self, ind):
        if ind == 0:
            self.mode_of_convert.setEnabled(True)
            self.show_password()
        elif ind == 1:
            self.mode_of_convert.setEnabled(False)
            self.password.setEnabled(True)
            
    def show_password(self):
        if self.mode_of_convert.currentIndex() == 1:
            self.password.setEnabled(True)
        else:
            self.password.setEnabled(False)

    def convert(self):
        if self.mode_type_combo.currentIndex() == 0:
            source = self.first_file.text()
            fin = self.final_file.text()

            mode = self.mode_of_convert.currentIndex()
            password = self.password.text()

            try:
                source_image = Image.open(source)
            except Exception:
                self.error('Не удалось считать исходное изображение.')
            else:
                image = ImageUti(source_image)
                way_to_encode = WAYS_TO_CONVERT[mode][0]

                try:
                    image.export(fin, way_to_encode, convert_password(password))
                except Exception:
                    self.error('Не удалось экспортировать изображение.')
                else:
                    QMessageBox.information(self, 'Информация', 'Успешно!')
        elif self.mode_type_combo.currentIndex() == 1:
            source = self.first_file.text()
            fin = self.final_file.text()

            password = self.password.text()

            if password:
                try:
                    image = ImageUti.import_image_with_password(source, convert_password(password))
                except PasswordError:
                    try:
                        image = ImageUti.import_image(source)
                        QMessageBox.warning(self, 'Предупреждение', ('Изображение не имело пароля, но '
                                                                    'всё равно экспортируется.'))
                    except Exception:
                        self.error('Не удалось считать исходное изображение.')
                        image = None
                except Exception:
                    self.error('Не удалось считать исходное изображение.')
                    image = None
            else:
                try:
                    image = ImageUti.import_image(source)

                    if image == 'PASSWORD':
                        self.error('Изображение запаролено.')
                        image = None
                except Exception:
                    self.error('Не удалось считать исходное изображение.')
                    image = None

            if image == 'Incorrect password':
                self.error('Неверный пароль.')
            elif image is not None:
                try:
                    image.image.save(fin)
                except Exception:
                    self.error('Не удалось экспортировать изображение.')
                else:
                    QMessageBox.information(self, 'Информация', 'Успешно!')

    def error(self, text):
        QMessageBox.critical(self, 'Ошибка', text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    program = Convertor()
    program.show()
    sys.exit(app.exec())