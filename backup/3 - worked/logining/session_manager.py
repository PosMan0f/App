import threading


class SessionManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.current_user = None
        return cls._instance

    def set_current_user(self, user):
        """Устанавливает текущего пользователя"""
        with self._lock:
            self.current_user = user

    def get_current_user(self):
        """Получает текущего пользователя"""
        with self._lock:
            return self.current_user

    def clear_session(self):
        """Очищает сессию"""
        with self._lock:
            self.current_user = None


# Синглтон экземпляр
session_manager = SessionManager()