import threading
import queue
import time
from functools import wraps


class DatabaseQueue:
    """Очередь запросов к базе данных для предотвращения блокировок"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_queue()
        return cls._instance

    def _init_queue(self):
        """Инициализирует очередь"""
        self.request_queue = queue.Queue()
        self.result_dict = {}
        self.request_id = 0
        self.lock = threading.Lock()

        # Запускаем обработчик очереди в отдельном потоке
        self.worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self.worker_thread.start()

    def _process_queue(self):
        """Обрабатывает очередь запросов"""
        while True:
            try:
                request_id, func, args, kwargs = self.request_queue.get()

                try:
                    # Выполняем функцию
                    result = func(*args, **kwargs)
                    self.result_dict[request_id] = (result, None)
                except Exception as e:
                    # Сохраняем ошибку
                    self.result_dict[request_id] = (None, e)

                self.request_queue.task_done()

            except Exception as e:
                print(f"Queue processor error: {e}")
                time.sleep(0.1)

    def enqueue(self, func, *args, **kwargs):
        """Добавляет запрос в очередь и возвращает результат"""
        with self.lock:
            request_id = self.request_id
            self.request_id += 1

        # Добавляем запрос в очередь
        self.request_queue.put((request_id, func, args, kwargs))

        # Ждем результат
        while request_id not in self.result_dict:
            time.sleep(0.01)

        result, error = self.result_dict.pop(request_id)

        if error:
            raise error
        return result

    def close(self):
        """Закрывает очередь"""
        self.request_queue.join()


# Синглтон экземпляр
db_queue = DatabaseQueue()


# Декоратор для автоматической постановки в очередь
def queued_db_call(func):
    """Декоратор для автоматической постановки вызовов БД в очередь"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return db_queue.enqueue(func, *args, **kwargs)

    return wrapper