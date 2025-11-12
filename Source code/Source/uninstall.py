from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication
import sys
import pathlib
import shutil
import winreg


FIN = r'C:\Program Files\UTI'
TEMP = pathlib.Path.home() / 'AppData' / 'Local' / 'Temp' / 'UTI'
INKS = pathlib.Path.home() / 'AppData' /  'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Start Menu' / 'UTI'


class Deleter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        valid = QMessageBox.question(self, 'Удаление', 'Вы уверены, что хотите удалить "UTI"?')
        
        if valid == QMessageBox.StandardButton.Yes:
            self.uninstall()
        else:
            sys.exit(0)

    def uninstall(self):
        if TEMP.exists():
            shutil.rmtree(TEMP, True)
        if pathlib.Path(FIN).exists():
            shutil.rmtree(FIN, True)
        if INKS.exists():
            shutil.rmtree(INKS, True)

        key_1 = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, '.uti')
        key_3 = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 'UTIView.uti')
        key_5 = winreg.CreateKey(key_3, 'shell')
        key_6 = winreg.CreateKey(key_5, 'open')

        winreg.DeleteKey(key_6, 'command')
        winreg.DeleteKey(key_5, 'open')
        winreg.DeleteKey(key_3, 'shell')
        winreg.DeleteKey(key_3, 'DefaultIcon')
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, 'UTIView.uti')
        winreg.DeleteKey(key_1, 'OpenWithProgids')
        winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, '.uti')

        sys.exit(0)
                        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    program = Deleter()
    app.exec()