# --- init_db.py ---
import sqlite3

def init_db():
    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS admins (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS cars (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        model TEXT NOT NULL,
                        brand TEXT NOT NULL,
                        year INTEGER NOT NULL,
                        is_available BOOLEAN DEFAULT 1,
                        image_url TEXT,
                        rental_price_per_day REAL)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        car_id INTEGER,
                        start_date TEXT,
                        end_date TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id),
                        FOREIGN KEY(car_id) REFERENCES cars(id))''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("База данных успешно инициализирована!")
