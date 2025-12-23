# send/database.py
import sqlite3
from datetime import datetime


class RequestDatabase:
    """Класс для работы с базой данных заявок"""

    def __init__(self, db_path='applications.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Инициализация базы данных"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                department TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                days INTEGER NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new'
            )
        ''')

        conn.commit()
        conn.close()

    def save_request(self, department, title, description, days):
        """Сохранение заявки в базу данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO applications 
                (department, title, description, days)
                VALUES (?, ?, ?, ?)
            ''', (department, title, description, days))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Ошибка при сохранении в БД: {e}")
            return False

    def get_all_requests(self):
        """Получение всех заявок (для будущего расширения)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM applications 
            ORDER BY created_date DESC
        ''')

        requests = cursor.fetchall()
        conn.close()
        return requests