# applications/task_manager.py
import sqlite3
import time
from typing import List, Dict, Callable
from applications.assigned_tasks_db import AssignedTasksDB
from applications.user_manager import UserManager


class TaskManager:
    """Менеджер задач с поддержкой событий"""

    def __init__(self):
        self.user_manager = UserManager()
        self.current_user = None
        self.assigned_db = AssignedTasksDB()
        self._initialize_tables()

        # Система событий
        self.listeners = {
            'tasks_changed': [],
            'user_tasks_changed': [],
            'user_changed': []
        }

        self.load_current_user()

    def add_listener(self, event: str, callback: Callable):
        """Добавление слушателя события"""
        if event in self.listeners:
            self.listeners[event].append(callback)

    def remove_listener(self, event: str, callback: Callable):
        """Удаление слушателя события"""
        if event in self.listeners and callback in self.listeners[event]:
            self.listeners[event].remove(callback)

    def _notify_listeners(self, event: str):
        """Уведомление всех слушателей события"""
        if event in self.listeners:
            for callback in self.listeners[event]:
                try:
                    callback()
                except Exception as e:
                    print(f"Ошибка в слушателе: {e}")

    def load_current_user(self):
        """Загрузка текущего пользователя"""
        user = self.user_manager.get_current_user_from_token()

        if user:
            self.current_user = user
            print(f"✅ Пользователь: {user['uid']}")
        else:
            self.current_user = self.user_manager.get_test_user()
            print(f"⚠ Тестовый пользователь: {self.current_user['uid']}")

        self._notify_listeners('user_changed')

    def _initialize_tables(self):
        """Инициализация таблиц"""
        pass  # База уже инициализирована

    def _get_connection(self):
        """Получение соединения с БД"""
        return sqlite3.connect('applications.db')

    def get_all_tasks(self, force_refresh: bool = False, department: str | None = None) -> List[Dict]:
        """Получение всех задач, с фильтром по отделу если указан"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            user_department = None
            if self.current_user:
                user_department = (self.current_user.get('department') or '').strip()

            query = '''
                SELECT * FROM applications 
                WHERE status = 'new' OR status IS NULL OR status = ''
            '''
            params = []

            if user_department:
                query += ' AND department = ?'
                params.append(user_department)

            query += ' ORDER BY created_date DESC'

            cursor.execute(query, params)

            tasks = []
            for row in cursor.fetchall():
                task = dict(row)
                task_id = task['id']

                # Проверяем, назначена ли задача
                is_assigned = self.assigned_db.is_task_assigned(task_id)
                task['is_assigned'] = 1 if is_assigned else 0

                tasks.append(task)

            return tasks

        except Exception as e:
            print(f"Ошибка: {e}")
            return []
        finally:
            conn.close()

    def get_user_tasks(self, force_refresh: bool = False) -> List[Dict]:
        """Получение задач пользователя"""
        if not self.current_user:
            return []

        user_id = self.current_user['uid']

        try:
            # Получаем назначенные задачи
            assigned_tasks = self.assigned_db.get_user_tasks(user_id)

            if not assigned_tasks:
                return []

            # Получаем детали задач
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            task_ids = [task['task_id'] for task in assigned_tasks]
            placeholders = ','.join('?' for _ in task_ids)

            cursor.execute(f'''
                SELECT * FROM applications 
                WHERE id IN ({placeholders})
                ORDER BY created_date DESC
            ''', task_ids)

            tasks = []
            for db_task in cursor.fetchall():
                task = dict(db_task)
                task_id = task['id']

                # Находим информацию о назначении
                assigned_info = next(
                    (at for at in assigned_tasks if at['task_id'] == task_id),
                    None
                )

                if assigned_info:
                    task['accepted_date'] = assigned_info.get('accepted_date')
                    task['user_task_status'] = assigned_info.get('status', 'in_progress')
                    tasks.append(task)

            conn.close()
            return tasks

        except Exception as e:
            print(f"Ошибка: {e}")
            return []

    def assign_task(self, task_id: int) -> bool:
        """Назначение задачи пользователю"""
        if not self.current_user:
            return False

        user_id = self.current_user['uid']
        user_email = self.current_user.get('email', '')

        try:
            # Назначаем задачу
            assigned_success = self.assigned_db.assign_task(user_id, task_id)

            if not assigned_success:
                return False

            # Обновляем статус
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE applications 
                SET status = 'assigned', 
                    assigned_to = ?,
                    assigned_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_email, task_id))

            conn.commit()
            conn.close()

            # Уведомляем об изменении
            self._notify_listeners('tasks_changed')
            self._notify_listeners('user_tasks_changed')

            print(f"✅ Задача {task_id} назначена")
            return True

        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    def complete_task(self, task_id: int) -> bool:
        """Завершение задачи"""
        if not self.current_user:
            return False

        user_id = self.current_user['uid']

        try:
            # Завершаем задачу
            success = self.assigned_db.complete_task(user_id, task_id)

            if not success:
                return False

            # Обновляем статус
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE applications 
                SET status = 'completed',
                    completed_date = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (task_id,))

            conn.commit()
            conn.close()

            # Уведомляем об изменении
            self._notify_listeners('tasks_changed')
            self._notify_listeners('user_tasks_changed')

            print(f"✅ Задача {task_id} завершена")
            return True

        except Exception as e:
            print(f"Ошибка: {e}")
            return False

    def get_task_details(self, task_id: int) -> Dict:
        """Получение деталей задачи"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM applications WHERE id = ?', (task_id,))
            task = cursor.fetchone()

            if task:
                return dict(task)
            return {}
        except:
            return {}
        finally:
            conn.close()

    def refresh_all(self):
        """Принудительное обновление всех данных"""
        print("🔄 Принудительное обновление...")
        self._notify_listeners('tasks_changed')
        self._notify_listeners('user_tasks_changed')
