# applications/user_manager.py
import json
import os
import sqlite3
from typing import Dict, Optional


class UserManager:
    """Менеджер пользователей для получения текущего user_id"""

    def __init__(self):
        self.auth_file = 'auth_token.json'
        self.users_db_path = 'users.db'
        self.current_user = None

    def get_current_user_from_token(self) -> Optional[Dict]:
        """Получение текущего пользователя из токена"""
        try:
            print("🔍 Поиск текущего пользователя...")

            # 1. Читаем токен из файла
            if not os.path.exists(self.auth_file):
                print("❌ Файл auth_token.json не найден")
                return None

            with open(self.auth_file, 'r', encoding='utf-8') as f:
                auth_data = json.load(f)

            token = auth_data.get('token')
            if not token:
                print("❌ Токен не найден в файле")
                return None

            print(f"✅ Токен из файла: {token[:30]}...")
            print(f"   Длина токена: {len(token)} символов")

            # 2. Проверяем БД users.db
            if not os.path.exists(self.users_db_path):
                print(f"❌ БД {self.users_db_path} не найдена")
                return None

            conn = sqlite3.connect(self.users_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 3. Ищем пользователя по auth_token
            print(f"🔍 Поиск пользователя с токеном в столбце auth_token...")

            cursor.execute("SELECT * FROM users WHERE auth_token = ?", (token,))
            user = cursor.fetchone()

            if user:
                user_data = dict(user)
                print(f"✅ ПОЛЬЗОВАТЕЛЬ НАЙДЕН!")
                print(f"   UID: {user_data.get('uid')}")
                print(f"   Email: {user_data.get('email')}")
                print(f"   Имя: {user_data.get('first_name', '')} {user_data.get('last_name', '')}")

                conn.close()

                return {
                    'uid': user_data.get('uid'),
                    'email': user_data.get('email'),
                    'first_name': user_data.get('first_name', ''),
                    'last_name': user_data.get('last_name', ''),
                    'department': user_data.get('department', ''),
                    'token': token
                }
            else:
                print(f"❌ Пользователь не найден по токену")

                # Выводим отладочную информацию
                print(f"\n🔍 Отладка:")

                # Проверяем все токены в БД
                cursor.execute("SELECT uid, email, auth_token FROM users WHERE auth_token IS NOT NULL")
                users_with_tokens = cursor.fetchall()

                print(f"Пользователи с токенами в БД:")
                for u in users_with_tokens:
                    uid, email, user_token = u
                    if user_token:
                        token_preview = user_token[:30] + '...' if len(user_token) > 30 else user_token
                        print(f"  - {uid}: {email} - токен: {token_preview}")

                        # Сравниваем токены
                        if user_token == token:
                            print(f"    ✅ СОВПАДАЕТ с файлом!")
                        else:
                            print(f"    ❌ НЕ СОВПАДАЕТ")

                conn.close()
                return None

        except Exception as e:
            print(f"❌ Ошибка при получении пользователя: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_user_by_uid(self, uid: str) -> Optional[Dict]:
        """Получение пользователя по UID"""
        try:
            if not os.path.exists(self.users_db_path):
                return None

            conn = sqlite3.connect(self.users_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE uid = ?", (uid,))
            user = cursor.fetchone()
            conn.close()

            if user:
                return dict(user)
            return None
        except Exception as e:
            print(f"Ошибка при поиске пользователя по UID: {e}")
            return None

    def get_test_user(self) -> Dict:
        """Получение тестового пользователя"""
        return {
            'uid': 'test_user_123',
            'email': 'test@example.com',
            'first_name': 'Тестовый',
            'last_name': 'Пользователь',
            'department': ''
        }
