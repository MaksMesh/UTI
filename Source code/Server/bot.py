import telebot
import sqlite3
import random


LICENCE_TEXT = 'Для использования бота, согласитесь с лицензионным соглашением по ссылке !ПОКА НЕТУ)!.'

with open('token.txt') as file:
    TOKEN = file.readline().strip()

bot = telebot.TeleBot(TOKEN)


def check_agreement(user):
    con = sqlite3.connect('users.db3')
    result = con.cursor().execute('SELECT agreement FROM users WHERE username = ?', (user,)).fetchone()
    con.close()

    if result:
        if result[0] == 1:
            return True

    return False


def update_agreement(user, name=None, last_name=None, premium=None):
    con = sqlite3.connect('users.db3')
    result = con.cursor().execute('SELECT * FROM users WHERE username = ?', (user,)).fetchone()

    if result:
        con.cursor().execute('UPDATE users SET agreement = 1 WHERE username = ?', (user,))
    else:
        val = f"'{user}','{name}','{last_name}',0,1,'{premium}'"
        con.cursor().execute(f'INSERT INTO users VALUES({val})')

    con.commit()
    con.close()


def get_keys(user):
    con = sqlite3.connect('users.db3')
    result = con.cursor().execute('SELECT key, activated FROM licence_keys WHERE user = ?', (user,)).fetchall()
    con.close()

    return [i[0] for i in result], [i[1] for i in result]


def add_key(user):
    con = sqlite3.connect('users.db3')
    avaible_keys = con.cursor().execute('SELECT key FROM licence_keys WHERE user = "None"').fetchall()

    if not avaible_keys:
        con.close()
        return None
    
    key = random.choice(avaible_keys)[0]
    con.cursor().execute('UPDATE users SET keys = keys + 1 WHERE username = ?', (user,))
    con.cursor().execute('UPDATE licence_keys SET user = ? WHERE key = ?', (user, key))

    con.commit()
    con.close()

    return key


def delete_key_f(key):
    con = sqlite3.connect('users.db3')
    user = con.cursor().execute('SELECT user FROM licence_keys WHERE key = ?', (key,)).fetchone()

    if not user:
        con.close()
        return False
    else:
        con.cursor().execute('UPDATE users SET keys = keys - 1 WHERE username = ?', (user[0],))
        con.cursor().execute('UPDATE licence_keys SET user = "None" WHERE key = ?', (key,))
        con.cursor().execute('UPDATE licence_keys SET activated = 0 WHERE key = ?', (key,))

        con.commit()
        con.close()

        return True
    

@bot.message_handler(['start'])
def welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(True)
    markup.add('Добавить ключ активации', 'Мои ключи активации', 'Удалить ключ активации')
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


@bot.message_handler(['del'])
def delete_key(message):
    try:
        key = message.text[message.text.index(' ') + 1:]
        result = delete_key_f(key)

        if not result:
            bot.send_message(message.chat.id, 'Нет такого ключа!')
        else:
            bot.send_message(message.chat.id, 'Успешно!')
    except Exception:
        pass

    markup = telebot.types.ReplyKeyboardMarkup(True)
    markup.add('Добавить ключ активации', 'Мои ключи активации', 'Удалить ключ активации')
    bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def main(message):
    if message.text == 'Добавить ключ активации':
        if check_agreement('@' + message.from_user.username):
            keys, _ = get_keys('@' + message.from_user.username)

            if len(keys) < 10:
                new_key = add_key('@' + message.from_user.username)

                if new_key is None:
                    bot.send_message(message.chat.id, 'В данный момент невозможно получить ключ.')
                else:
                    bot.send_message(message.chat.id, f'Ключ "{new_key}" успешно добавлен!')
            else:
                bot.send_message(message.chat.id, 'У вас максимальное количесвто ключей!')
        else:
            username, name, last_name = '@' + message.from_user.username, message.from_user.first_name, message.from_user.last_name
            premium = message.from_user.is_premium

            markup = telebot.types.ReplyKeyboardMarkup(True)
            markup.add('Согласен', 'Не согласен')
            bot.send_message(message.chat.id, LICENCE_TEXT, reply_markup=markup)
    elif message.text == 'Мои ключи активации':
        keys, active = get_keys('@' + message.from_user.username)

        if keys:
            fin = []
            for key, act in zip(keys, active):
                fin.append(key + ' - ' + ('Активирован' if act else 'Не активирован'))

            bot.send_message(message.chat.id, f'({len(keys)}/10):\n' + '\n'.join(fin))
        else:
            bot.send_message(message.chat.id, 'У вас нет ключей.')
    elif message.text == 'Согласен':
        username, name, last_name = '@' + message.from_user.username, message.from_user.first_name, message.from_user.last_name
        premium = message.from_user.is_premium

        update_agreement(username, name, last_name, premium)
        bot.send_message(message.chat.id, 'Успешно!')
        
        markup = telebot.types.ReplyKeyboardMarkup(True)
        markup.add('Добавить ключ активации', 'Мои ключи активации', 'Удалить ключ активации')

        bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)
    elif message.text == 'Удалить ключ активации':
        keys, _ = get_keys('@' + message.from_user.username)

        if keys:
            markup = telebot.types.ReplyKeyboardMarkup(True)
            markup.add(*['/del ' + i for i in keys], 'Назад')
            bot.send_message(message.chat.id, 'Выберите ключ для удаления.', reply_markup=markup)
        else:
            markup = telebot.types.ReplyKeyboardMarkup(True)
            markup.add('Добавить ключ активации', 'Мои ключи активации', 'Удалить ключ активации')
            bot.send_message(message.chat.id, 'У вас нет ключей!', reply_markup=markup)
    else:
        markup = telebot.types.ReplyKeyboardMarkup(True)
        markup.add('Добавить ключ активации', 'Мои ключи активации', 'Удалить ключ активации')
        bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=markup)


bot.infinity_polling()