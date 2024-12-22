# --- app.py ---
from django.utils.timezone import now
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

from init_db import init_db

app = Flask(__name__)
app.secret_key = 'super_secret_key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cars')
def available_cars():
    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cars WHERE is_available = 1")
    cars = cursor.fetchall()
    conn.close()
    return render_template('cars.html', cars=cars)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('rental.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, password))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('rental.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            return redirect(url_for('available_cars'))
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('rental.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE email = ?', (email,))
        admin = cursor.fetchone()
        conn.close()
        if admin and admin[3] == password:
            session['admin_id'] = admin[0]
            return redirect(url_for('admin_dashboard'))
        else:
            error = 'Неверный email или пароль'
    return render_template('admin_login.html', error=error)

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cars")
    cars = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', cars=cars)

@app.route('/admin/add_car', methods=['GET', 'POST'])
def add_car():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        model = request.form['model']
        brand = request.form['brand']
        year = request.form['year']
        price = request.form['price']
        image_url = request.form['image_url']
        conn = sqlite3.connect('rental.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO cars (model, brand, year, is_available, image_url, rental_price_per_day) 
                          VALUES (?, ?, ?, 1, ?, ?)''', (model, brand, year, image_url, price))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    return render_template('add_car.html')

@app.route('/admin/delete_car/<int:car_id>', methods=['GET'])
def delete_car(car_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cars WHERE id = ?', (car_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_car/<int:car_id>', methods=['GET', 'POST'])
def edit_car(car_id):
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        model = request.form['model']
        brand = request.form['brand']
        year = request.form['year']
        price = request.form['price']
        image_url = request.form['image_url']
        cursor.execute('''UPDATE cars SET model = ?, brand = ?, year = ?, image_url = ?, rental_price_per_day = ? 
                          WHERE id = ?''', (model, brand, year, image_url, price, car_id))
        conn.commit()
        conn.close()
        return redirect(url_for('admin_dashboard'))
    cursor.execute('SELECT * FROM cars WHERE id = ?', (car_id,))
    car = cursor.fetchone()
    conn.close()
    return render_template('edit_car.html', car=car)


@app.route('/rent_car/<int:car_id>', methods=['GET', 'POST'])
def rent_car(car_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        days = int(request.form['days'])
        user_id = session['user_id']

        conn = sqlite3.connect('rental.db')
        cursor = conn.cursor()

        cursor.execute('SELECT rental_price_per_day FROM cars WHERE id = ?', (car_id,))
        price_per_day = cursor.fetchone()[0]

        total_price = price_per_day * days

        cursor.execute(
            'INSERT INTO bookings (user_id, car_id, start_date, end_date) VALUES (?, ?, date(), date("now", ? || " days"))',
            (user_id, car_id, days)
        )

        cursor.execute('UPDATE cars SET is_available = 0 WHERE id = ?', (car_id,))

        conn.commit()
        conn.close()

        return redirect(url_for('available_cars'))

    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM cars WHERE id = ?', (car_id,))
    car = cursor.fetchone()
    conn.close()

    return render_template('rent_car.html', car=car)


@app.route('/profile')
def user_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT cars.model, cars.brand, cars.image_url, bookings.start_date, bookings.end_date, cars.rental_price_per_day 
                      FROM bookings 
                      JOIN cars ON bookings.car_id = cars.id 
                      WHERE bookings.user_id = ?''', (user_id,))
    bookings = cursor.fetchall()
    conn.close()

    user_info = {"username": "Пользователь", "email": "user@example.com"}  # Заглушка, добавить получение из БД

    return render_template('profile.html', bookings=bookings, user_info=user_info)

@app.route('/test_bookings')
def test_bookings():
    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM bookings')
    data = cursor.fetchall()
    conn.close()
    return f"{data}"


@app.route('/clear_bookings')
def clear_bookings():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM bookings WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('user_profile'))


if __name__ == '__main__':
    init_db()  # Убедимся, что база создается при запуске
    app.run(debug=True)
