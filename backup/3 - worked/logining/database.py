import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
import threading
import time

from .db_queue import queued_db_call


class Database:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        """Инициализирует соединение с базой данных"""
        # Создаем отдельное соединение для каждого потока
        self.local = threading.local()
        self._get_connection()
        self.create_tables()

    def _get_connection(self):
        """Получает соединение для текущего потока"""
        if not hasattr(self.local, 'conn'):
            self.local.conn = sqlite3.connect('users.db', timeout=30.0, check_same_thread=False)
            self.local.cursor = self.local.conn.cursor()
        return self.local.conn, self.local.cursor

    def create_tables(self):
        """Создает таблицы если их нет"""
        conn, cursor = self._get_connection()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uid TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                middle_name TEXT,
                birth_date TEXT,
                department TEXT,
                locked INTEGER DEFAULT 0,
                auth_token TEXT,
                token_expiry TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

    @queued_db_call
    def create_user(self, email, password, first_name="", last_name="", middle_name=""):
        """Создает нового пользователя"""
        conn, cursor = self._get_connection()

        # Генерируем UID
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        uid = f"77021{count + 1:05d}"

        # Хешируем пароль
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        try:
            cursor.execute('''
                INSERT INTO users (uid, email, password_hash, first_name, last_name, middle_name)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (uid, email, password_hash, first_name, last_name, middle_name))
            conn.commit()
            return uid
        except sqlite3.IntegrityError:
            return None

    @queued_db_call
    def authenticate_user(self, email, password):
        """Аутентификация пользователя по email и паролю"""
        conn, cursor = self._get_connection()

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute('SELECT * FROM users WHERE email = ? AND password_hash = ?',
                       (email, password_hash))
        user = cursor.fetchone()

        if user:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, user))
        return None

    @queued_db_call
    def get_user_by_uid(self, uid):
        """Получает пользователя по UID"""
        conn, cursor = self._get_connection()

        cursor.execute('SELECT * FROM users WHERE uid = ?', (uid,))
        user = cursor.fetchone()
        if user:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, user))
        return None

    @queued_db_call
    def get_user_by_email(self, email):
        """Получает пользователя по email"""
        conn, cursor = self._get_connection()

        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        if user:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, user))
        return None

    @queued_db_call
    def update_user_profile(self, uid, first_name, last_name, middle_name, birth_date, department):
        """Обновляет профиль пользователя"""
        conn, cursor = self._get_connection()

        cursor.execute('''
            UPDATE users 
            SET first_name = ?, last_name = ?, middle_name = ?, 
                birth_date = ?, department = ?
            WHERE uid = ? AND locked = 0
        ''', (first_name, last_name, middle_name, birth_date, department, uid))
        conn.commit()
        return cursor.rowcount > 0

    @queued_db_call
    def update_password(self, uid, old_password, new_password):
        """Обновляет пароль пользователя"""
        conn, cursor = self._get_connection()

        old_hash = hashlib.sha256(old_password.encode()).hexdigest()
        new_hash = hashlib.sha256(new_password.encode()).hexdigest()

        cursor.execute('''
            UPDATE users 
            SET password_hash = ?
            WHERE uid = ? AND password_hash = ? AND locked = 0
        ''', (new_hash, uid, old_hash))
        conn.commit()
        return cursor.rowcount > 0

    @queued_db_call
    def create_auth_token(self, uid):
        """Создает токен авторизации на 30 дней"""
        conn, cursor = self._get_connection()

        token = secrets.token_hex(32)
        expiry = (datetime.now() + timedelta(days=30)).isoformat()

        try:
            cursor.execute('''
                UPDATE users 
                SET auth_token = ?, token_expiry = ?
                WHERE uid = ?
            ''', (token, expiry, uid))
            conn.commit()
            return token
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                time.sleep(0.1)
                try:
                    conn.rollback()
                    cursor.execute('''
                        UPDATE users 
                        SET auth_token = ?, token_expiry = ?
                        WHERE uid = ?
                    ''', (token, expiry, uid))
                    conn.commit()
                    return token
                except:
                    print("Warning: Could not save token to database")
                    return token
            else:
                raise

    @queued_db_call
    def validate_token(self, token):
        """Проверяет токен и возвращает пользователя если он валиден"""
        conn, cursor = self._get_connection()

        cursor.execute('''
            SELECT * FROM users 
            WHERE auth_token = ? AND token_expiry > ?
        ''', (token, datetime.now().isoformat()))

        user = cursor.fetchone()
        if user:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, user))
        return None

    @queued_db_call
    def logout_user(self, uid):
        """Удаляет токен пользователя"""
        conn, cursor = self._get_connection()

        try:
            cursor.execute('''
                UPDATE users 
                SET auth_token = NULL, token_expiry = NULL
                WHERE uid = ?
            ''', (uid,))
            conn.commit()
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"Database locked during logout for UID: {uid}")
                conn.rollback()
            else:
                raise

    @queued_db_call
    def get_user_locked_status(self, uid):
        """Проверяет заблокирован ли пользователь"""
        conn, cursor = self._get_connection()

        cursor.execute('SELECT locked FROM users WHERE uid = ?', (uid,))
        result = cursor.fetchone()
        return result[0] if result else 0

    @queued_db_call
    def search_users(self, search_term, exclude_uid=None):
        """Ищет пользователей по UID или email"""
        conn, cursor = self._get_connection()

        # Ищем по UID
        cursor.execute('''
            SELECT uid, email, first_name, last_name 
            FROM users 
            WHERE uid LIKE ? AND uid != ?
            LIMIT 10
        ''', (f'%{search_term}%', exclude_uid or ''))
        users_by_uid = cursor.fetchall()

        # Ищем по email
        cursor.execute('''
            SELECT uid, email, first_name, last_name 
            FROM users 
            WHERE email LIKE ? AND uid != ?
            LIMIT 10
        ''', (f'%{search_term}%', exclude_uid or ''))
        users_by_email = cursor.fetchall()

        # Объединяем результаты
        user_dict = {}
        for user in users_by_uid + users_by_email:
            uid, email, first_name, last_name = user
            if uid not in user_dict:
                # Формируем имя
                if first_name and last_name:
                    name = f"{first_name} {last_name}"
                elif first_name:
                    name = first_name
                elif last_name:
                    name = last_name
                else:
                    name = email

                user_dict[uid] = {
                    'uid': uid,
                    'email': email,
                    'name': name
                }

        return list(user_dict.values())

    @queued_db_call
    def get_all_users_except(self, exclude_uid):
        """Получает всех пользователей кроме указанного"""
        conn, cursor = self._get_connection()

        cursor.execute('''
            SELECT uid, email, first_name, last_name 
            FROM users 
            WHERE uid != ?
            ORDER BY first_name, last_name
        ''', (exclude_uid,))

        users = []
        for user in cursor.fetchall():
            uid, email, first_name, last_name = user

            if first_name and last_name:
                name = f"{first_name} {last_name}"
            elif first_name:
                name = first_name
            elif last_name:
                name = last_name
            else:
                name = email

            users.append({
                'uid': uid,
                'email': email,
                'name': name
            })

        return users

    def close(self):
        """Закрывает соединения с базой данных"""
        if hasattr(self.local, 'conn'):
            self.local.conn.close()