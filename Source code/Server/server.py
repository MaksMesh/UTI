import socket
import sqlite3


HOST = '26.201.31.50'
PORT = 65432
con = sqlite3.connect('users.db3')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()

        with conn:
            try:
                data = conn.recv(1024)
                data = data.decode()
                
                if data[0] == 'i':
                    if data[1] == 'd':
                        key = data[data.index(' '):].strip()
                        result = con.cursor().execute('SELECT activated FROM licence_keys WHERE key = ?', (key,)).fetchone()
                        
                        if result is not None:
                            if result[0] == 0:
                                conn.sendall(b'FILE')

                                with open('source.zip', 'rb') as file:
                                    while True:
                                        data = file.read(1024)

                                        if not data:
                                            break

                                        conn.sendall(data)

                                con.cursor().execute('UPDATE licence_keys SET activated = 1 WHERE key = ?', (key,))

                                con.commit()
                            else:
                                conn.sendall(b'NONE')
                        else:
                            conn.sendall(b'NONE')
                    elif data[1] == 'u':
                        data = data[data.index(' '):].strip()
                        ind = data.index(' ')
                        key, username = data[:ind].strip(), data[ind:].strip()
                        
                        result = con.cursor().execute('SELECT user FROM licence_keys WHERE key = ?', (key,)).fetchone()

                        if result is not None:
                            if result[0] == username:
                                conn.sendall(b'TRUE')
                            else:
                                conn.sendall(b'NONE')
                        else:
                            conn.sendall(b'NONE')
                elif data[0] == 'u':
                    if data[1] == 'd':
                        data = data[data.index(' '):].strip()
                        ind = data.index(' ')
                        key, username = data[:ind].strip(), data[ind:].strip()
                            
                        result = con.cursor().execute('SELECT user FROM licence_keys WHERE key = ?', (key,)).fetchone()

                        if result is not None:
                            if result[0] == username:
                                result = con.cursor().execute('SELECT activated FROM licence_keys WHERE key = ?', (key,)).fetchone()
                            
                                if result is not None:
                                    if result[0] == 1:
                                        conn.sendall(b'FILE')

                                        with open('source.zip', 'rb') as file:
                                            while True:
                                                data = file.read(1024)

                                                if not data:
                                                    break

                                                conn.sendall(data)
                                    else:
                                        conn.sendall(b'NONE')
                                else:
                                    conn.sendall(b'NONE')
                            else:
                                conn.sendall(b'NONE')
                        else:
                            conn.sendall(b'NONE')
                    elif data[1] == 'v':
                        data = data[data.index(' '):].strip()
                        ind = data.index(' ')
                        key, username = data[:ind].strip(), data[ind:].strip()
                            
                        result = con.cursor().execute('SELECT user FROM licence_keys WHERE key = ?', (key,)).fetchone()

                        if result is not None:
                            if result[0] == username and result[0] != 'None':
                                result = con.cursor().execute('SELECT activated FROM licence_keys WHERE key = ?', (key,)).fetchone()
                            
                                if result is not None:
                                    if result[0] == 1:
                                        with open('version.txt') as file:
                                            conn.sendall(bytes(file.readline(), 'UTF-8'))
                                    else:
                                        conn.sendall(b'NONE')
                                else:
                                    conn.sendall(b'NONE')
                            else:
                                conn.sendall(b'NONE')
                        else:
                            conn.sendall(b'NONE')
            except Exception:
                pass