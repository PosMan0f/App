import json
import os

TOKEN_FILE = 'auth_token.json'


class AuthManager:
    def __init__(self):
        from .database import Database
        self.db = Database()

    def login_user(self, email, password):
        """Аутентификация пользователя"""
        user = self.db.authenticate_user(email, password)
        if user:
            token = self.db.create_auth_token(user['uid'])
            self.save_token(token)
            return user
        return None

    def logout_user(self, uid):
        """Выход пользователя"""
        try:
            self.db.logout_user(uid)
        except Exception as e:
            print(f"Warning during logout: {e}")
        finally:
            # Всегда удаляем файл токена
            self.remove_token()

    def save_token(self, token):
        """Сохраняет токен в файл"""
        try:
            with open(TOKEN_FILE, 'w') as f:
                json.dump({'token': token}, f)
            return True
        except Exception as e:
            print(f"Error saving token: {e}")
            return False

    def remove_token(self):
        """Удаляет токен из файла"""
        try:
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
        except Exception as e:
            print(f"Error removing token file: {e}")

    def register_user(self, email, password, first_name="", last_name="", middle_name=""):
        """Регистрирует нового пользователя и сразу возвращает его данные с токеном"""
        try:
            uid = self.db.create_user(email, password, first_name, last_name, middle_name)
            if not uid:
                return None

            # Создаем токен и сохраняем его
            token = self.db.create_auth_token(uid)
            if token:
                self.save_token(token)

            # Возвращаем полные данные пользователя
            user = self.db.get_user_by_uid(uid)
            if user:
                user['token'] = token
            return user
        except Exception as e:
            print(f"Error during user registration: {e}")
            return None

    def check_auto_login(self):
        """Проверяем сохраненный токен для автоматического входа"""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, 'r') as f:
                    data = json.load(f)
                    token = data.get('token')
                    if token:
                        return self.db.validate_token(token)
            except Exception as e:
                print(f"Error loading token: {e}")
        return None
