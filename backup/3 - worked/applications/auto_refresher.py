# applications/auto_refresher.py
import threading
import time
from kivy.clock import Clock


class AutoRefresher:
    """Автоматическое обновление данных"""

    def __init__(self, task_manager):
        self.task_manager = task_manager
        self.is_active = False
        self.refresh_thread = None
        self.stop_event = threading.Event()
        self.ui_callback = None

    def set_ui_callback(self, callback):
        """Установка колбэка для обновления UI"""
        self.ui_callback = callback

    def start(self):
        """Запуск автоматического обновления"""
        if self.is_active:
            return

        self.is_active = True
        self.stop_event.clear()

        # Запускаем фоновый поток
        self.refresh_thread = threading.Thread(target=self._refresh_loop, daemon=True)
        self.refresh_thread.start()

        print("✅ Автообновление запущено")

    def stop(self):
        """Остановка автоматического обновления"""
        if not self.is_active:
            return

        self.is_active = False
        self.stop_event.set()

        if self.refresh_thread:
            self.refresh_thread.join(timeout=2)

        print("⏹ Автообновление остановлено")

    def _refresh_loop(self):
        """Цикл обновления в фоновом потоке"""
        while not self.stop_event.is_set():
            try:
                # Ждем 10 секунд
                for _ in range(10):
                    if self.stop_event.is_set():
                        return
                    time.sleep(1)

                # Обновляем данные
                print("🔄 Автоматическое обновление...")
                self.task_manager.refresh_all()

                # Уведомляем UI
                if self.ui_callback:
                    Clock.schedule_once(lambda dt: self.ui_callback('both'), 0.1)

            except Exception as e:
                print(f"❌ Ошибка в цикле обновления: {e}")
                time.sleep(5)

    def manual_refresh(self):
        """Ручное обновление"""
        print("🔄 Ручное обновление...")
        self.task_manager.refresh_all()