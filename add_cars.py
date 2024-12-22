import sqlite3

def add_cars():
    cars = [
        ('Model S', 'Tesla', 2022, 1, '/static/images/тесла_моделС_2022.png', 120),
        ('M5', 'BMW', 2020, 1, '/static/images/м5_2020.jpg', 100),
        ('Camry', 'Toyota', 2021, 1, '/static/images/камри2021.jpg', 70),
        ('M3', 'BMW', 2019, 1, '/static/images/м3_2019.jpg', 80),
        ('Dodge', 'Challenger', 2019, 1, '/static/images/dodge_2019.jpg', 150)
    ]

    conn = sqlite3.connect('rental.db')
    cursor = conn.cursor()

    for car in cars:
        cursor.execute('''INSERT INTO cars (model, brand, year, is_available, image_url, rental_price_per_day)
                          VALUES (?, ?, ?, ?, ?, ?)''', car)
    conn.commit()
    conn.close()
    print("Автомобили успешно добавлены в базу данных")

if __name__ == '__main__':
    add_cars()
