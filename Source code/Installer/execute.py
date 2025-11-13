import winreg
import os
import pathlib
import shutil


ICON = r"C:\Program Files\UTI\logo.ico"
FIN = r'C:\Program Files\UTI'
TEMP = pathlib.Path.home() / 'AppData' / 'Local' / 'Temp' / 'UTI' / 'First'
PROGRAM = r"C:\Program Files\UTI\viewer.exe"
INKS = pathlib.Path.home() / 'AppData' /  'Roaming' / 'Microsoft' / 'Windows' / 'Start Menu' / 'Start Menu' / 'UTI'

if not os.path.exists(FIN):
    os.makedirs(FIN)
else:
    shutil.rmtree(FIN, True)
    os.makedirs(FIN, exist_ok=True)

shutil.copytree(TEMP / 'Program', FIN, dirs_exist_ok=True)

if not os.path.exists(INKS):
    os.makedirs(INKS)
else:
    shutil.rmtree(INKS)
    os.makedirs(INKS)

shutil.copytree(TEMP / 'Inks', INKS, dirs_exist_ok=True)

key_1 = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, '.uti')
key_2 = winreg.CreateKey(key_1, 'OpenWithProgids')

winreg.SetValueEx(key_2, 'UTIView.uti', 0, winreg.REG_SZ, '')
winreg.SetValue(winreg.HKEY_CLASSES_ROOT, '.uti', winreg.REG_SZ, 'UTI.File')
winreg.SetValueEx(key_1, 'Content Type', 0, winreg.REG_SZ, 'image/uti')

key_2.Close()

key_3 = winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, 'UTIView.uti')
key_4 = winreg.CreateKey(key_3, 'DefaultIcon')

winreg.SetValue(key_3, 'DefaultIcon', winreg.REG_SZ, ICON)
key_4.Close()

key_5 = winreg.CreateKey(key_3, 'shell')
key_6 = winreg.CreateKey(key_5, 'open')

winreg.SetValueEx(key_6, 'Icon', 0, winreg.REG_SZ, '"' + PROGRAM + '"')

key_7 = winreg.CreateKey(key_6, 'command')

winreg.SetValue(key_6, 'command', winreg.REG_SZ, '"' + PROGRAM + '" "%1"')

key_7.Close()
key_6.Close()
key_5.Close()
key_3.Close()
key_1.Close()

shutil.rmtree(TEMP, True)