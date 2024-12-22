import sqlite3

import app


def create_admin():
    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO admins (username, email, password) VALUES (?, ?, ?)",
                   ('admin', 'admin@yan.com', '123'))
    conn.commit()
    conn.close()
    print("Администратор успешно создан")

if __name__ == '__main__':
    create_admin()
    app.run(debug=True)

