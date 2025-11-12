import sqlite3
import random


letters = 'QWERTYUIOPASDFGHJKLZXCVBNM1234567890'

con = sqlite3.connect('users.db3')
num = int(input('Введите, сколько надо сгенерировать ключей: '))

print('Считываем уже имеющиеся ключи...')
keys = [i[0] for i in con.cursor().execute('SELECT key FROM licence_keys').fetchall()]

print('Генерируем...')

new_keys = []

while len(new_keys) < num:
    key = random.choices(letters, k=25)
    key = '-'.join([''.join(key[i:i + 5]) for i in range(0, len(key), 5)])
    
    if key not in keys:
        new_keys.append(key)

print('Записываем ключи в БД...')

for i in new_keys:
    con.cursor().execute(f"INSERT INTO licence_keys VALUES('{i}',0,'None')")
    
con.commit()
con.close()

print('Готово!')