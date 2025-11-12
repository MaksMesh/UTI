from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt6 import uic
import pathlib
import sys
import socket
import zipfile
import os
import shutil


HOST = '26.201.31.50'
PORT = 65432
TEMP = pathlib.Path.home() / 'AppData' / 'Local' / 'Temp' / 'UTI'
FILES_TEMP = pathlib.Path.home() / 'AppData' / 'Local' / 'Temp' / 'UTI' / 'files.zip'


class Updater(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(r'.\UI\updater.ui', self)
        self.atts = 5
        self.initUI()
        self.load_data()

    def initUI(self):
        self.setWindowTitle('Обновление')
        self.setFixedSize(279, 130)

        self.check_upd_button.clicked.connect(self.check_update)
        self.help_button.clicked.connect(self.help)

    def check_update(self):
        key = self.key_text.text()
        username = self.user_text.text()

        if not key:
            QMessageBox.critical(self, 'Ошибка', 'Введите ключ!')
        else:
            if not username:
                QMessageBox.critical(self, 'Ошибка', 'Введите username!')
            else:
                try:
                    version = self.get_version(key, username)

                    if version:
                        path_m = pathlib.Path.home() / 'AppData' / 'Local' / 'MaksMesh'
                        path_m.mkdir(exist_ok=True)
                        path_u = path_m / 'UTI'
                        path_u.mkdir(exist_ok=True)
                        path_p = path_u / 'Updater'
                        path_p.mkdir(exist_ok=True)
                        fin = path_p / 'data.txt'

                        with open(fin, 'w') as file:
                            file.write(key + '\n' + username)

                        try:
                            with open(r'C:\Program Files\UTI\VERSION') as file:
                                data = file.read().strip()
                        except FileNotFoundError:
                            data = ''

                        if data and bytes(data, 'UTF-8') == version:
                            QMessageBox.information(self, 'Информация', 'У вас установлена последняя версия.')
                        else:
                            self.get_files(key, username)
                            temp_f = TEMP / 'First'
                            shutil.rmtree(temp_f)
                            os.mkdir(temp_f)
                            file = zipfile.ZipFile(FILES_TEMP)
                            file.extractall(temp_f)
                            file.close()
                            os.system('Powershell -Command "& { Start-Process \"' + str(temp_f / 'execute.exe') + '\" -Verb RunAs }')
                            QMessageBox.information(self, 'Информация', f'Успешно установлена версия {version.decode()}!')
                    else:
                        self.atts -= 1

                        if not self.atts:
                            self.close()
                        else:
                            QMessageBox.critical(self, 'Ошибка', f'Неверный ключ или username! Осталось попыток: {self.atts}.')
                except ConnectionError:
                    QMessageBox.critical(self, 'Ошибка', 'Нет подключения к серверу.')

    def get_version(self, key, username):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'uv ' + bytes(key, 'UTF-8') + b' ' + bytes(username, 'UTF-8'))
            data = s.recv(1024)

            if data == b'NONE':
                return False
            else:
                return data
            
    def get_files(self, key, username):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'ud ' + bytes(key, 'UTF-8') + b' ' + bytes(username, 'UTF-8'))
            data = s.recv(4)
            
            if data == b'FILE':
                data = s.recv(1024)

                with open(FILES_TEMP, 'wb') as file:
                    while data:
                        file.write(data)
                        data = s.recv(1024)
            
    def load_data(self):
        fin = pathlib.Path.home() / 'AppData' / 'Local' / 'MaksMesh' / 'UTI' / 'Updater' / 'data.txt'

        if fin.exists():
            with open(fin) as file:
                data = file.readlines()

            if data:
                if len(data) == 1:
                    self.key_text.setText(data[0].strip('\n'))
                else:
                    self.key_text.setText(data[0].strip('\n'))
                    self.user_text.setText(data[1].strip('\n'))

    def help(self):
        QMessageBox.information(self, 'Информация', '<html><head/><body><p>1. Установите программу Radmin Vpn.</p><p>2. Подключитесь к частной сети &quot;UTI Images&quot;</p><p>с паролем &quot;uti_images&quot; в установленной</p><p>программе.</p><p>3. Введите ключ активации, полученный из</p><p>телеграм бота @uti_images_bot.</p><p>4. <span style=" font-weight:600;">Убедитесь в стабильности интернет</span></p><p><span style=" font-weight:600;">соединения.</span></p><p>5. Нажмите &quot;Далее&quot;.</p></body></html>')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    program = Updater()
    program.show()
    sys.exit(app.exec())