# applications/assigned_tasks_db.py
import sqlite3
import threading
from datetime import datetime


class AssignedTasksDB:
    """База данных для назначенных задач"""

    def __init__(self, db_name='assigned_tasks.db'):
        self.db_name = db_name
        self._init_database()

    def _init_database(self):
        """Инициализация базы данных"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Таблица назначенных задач
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assigned_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                task_id INTEGER NOT NULL,
                accepted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'in_progress',
                UNIQUE(user_id, task_id)
            )
        ''')

        # Индекс для быстрого поиска по user_id
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_user_id 
            ON assigned_tasks(user_id)
        ''')

        # Индекс для быстрого поиска по task_id
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_task_id 
            ON assigned_tasks(task_id)
        ''')

        conn.commit()
        conn.close()
        print(f"База данных {self.db_name} инициализирована")

    def _get_connection(self):
        """Получение соединения с БД"""
        return sqlite3.connect(self.db_name)

    def assign_task(self, user_id: str, task_id: int) -> bool:
        """Назначение задачи пользователю"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Проверяем, не назначена ли уже задача
            cursor.execute('SELECT 1 FROM assigned_tasks WHERE task_id = ?', (task_id,))
            if cursor.fetchone():
                print(f"Задача {task_id} уже назначена")
                conn.close()
                return False

            # Добавляем запись
            cursor.execute('''
                INSERT INTO assigned_tasks (user_id, task_id, status)
                VALUES (?, ?, 'in_progress')
            ''', (user_id, task_id))

            conn.commit()
            conn.close()
            print(f"Задача {task_id} назначена пользователю {user_id}")
            return True

        except Exception as e:
            print(f"Ошибка при назначении задачи: {e}")
            return False

    def get_user_tasks(self, user_id: str) -> list:
        """Получение задач пользователя"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM assigned_tasks 
                WHERE user_id = ? AND status != 'completed'
                ORDER BY accepted_date DESC
            ''', (user_id,))

            tasks = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return tasks

        except Exception as e:
            print(f"Ошибка при получении задач пользователя: {e}")
            return []

    def complete_task(self, user_id: str, task_id: int) -> bool:
        """Завершение задачи"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Проверяем, принадлежит ли задача пользователю
            cursor.execute('''
                SELECT 1 FROM assigned_tasks 
                WHERE task_id = ? AND user_id = ? AND status = 'in_progress'
            ''', (task_id, user_id))

            if not cursor.fetchone():
                conn.close()
                return False

            # Обновляем статус
            cursor.execute('''
                UPDATE assigned_tasks 
                SET status = 'completed'
                WHERE task_id = ? AND user_id = ?
            ''', (task_id, user_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Ошибка при завершении задачи: {e}")
            return False

    def is_task_assigned(self, task_id: int) -> bool:
        """Проверка, назначена ли задача"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('SELECT 1 FROM assigned_tasks WHERE task_id = ?', (task_id,))
            result = cursor.fetchone() is not None
            conn.close()
            return result

        except Exception as e:
            print(f"Ошибка при проверке задачи: {e}")
            return False

    def get_all_assigned_tasks(self) -> list:
        """Получение всех назначенных задач"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM assigned_tasks ORDER BY accepted_date DESC')
            tasks = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return tasks

        except Exception as e:
            print(f"Ошибка при получении всех назначенных задач: {e}")
            return []